"""
Service for sending streak engagement reminders
"""
from sqlalchemy.orm import Session
from app.models import User, CardReview
from app.models import UserDeckSmsSettings
from app.services.session_manager import get_next_due_flashcard
from app.services.loop_message_service import LoopMessageService
from app.services.summary_service import calculate_streak_days, calculate_potential_streak
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import and_


def check_streak_at_risk(user: User, db: Session) -> Dict[str, Any]:
    """
    Check if user is at risk of losing their streak
    
    Returns:
        Dict with:
        - at_risk: bool
        - current_streak: int
        - has_reviewed_today: bool
        - has_due_cards: bool
        - has_sms_enabled_cards: bool
        - message: Optional[str] - reminder message if at risk
    """
    today = datetime.now(timezone.utc).date()
    start_of_today = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
    end_of_today = datetime.combine(today, datetime.max.time(), tzinfo=timezone.utc)
    
    # Check if user has reviewed today
    reviews_today = db.query(CardReview).filter(
        and_(
            CardReview.user_id == user.id,
            CardReview.review_date >= start_of_today,
            CardReview.review_date <= end_of_today
        )
    ).count()
    
    has_reviewed_today = reviews_today > 0
    
    # Calculate current streak
    current_streak = calculate_streak_days(user.id, db)
    
    # If no active streak, not at risk
    if current_streak == 0 and not has_reviewed_today:
        # Check potential streak
        potential_streak, _ = calculate_potential_streak(user.id, db)
        if potential_streak == 0:
            return {
                "at_risk": False,
                "current_streak": 0,
                "has_reviewed_today": has_reviewed_today,
                "has_due_cards": False,
                "has_sms_enabled_cards": False,
                "message": None
            }
    
    # If user already reviewed today, not at risk
    if has_reviewed_today:
        return {
            "at_risk": False,
            "current_streak": current_streak,
            "has_reviewed_today": True,
            "has_due_cards": False,
            "has_sms_enabled_cards": False,
            "message": None
        }
    
    # User hasn't reviewed today and has a streak - check for due cards
    due_card = get_next_due_flashcard(user.id, db)
    has_due_cards = due_card is not None
    
    # Check if there are SMS-enabled cards due
    has_sms_enabled_cards = False
    if has_due_cards:
        # Check if the due card is from an SMS-enabled deck
        if due_card.deck_id:
            sms_setting = db.query(UserDeckSmsSettings).filter_by(
                user_id=user.id,
                deck_id=due_card.deck_id,
                sms_enabled=True
            ).first()
            has_sms_enabled_cards = sms_setting is not None
        else:
            # Cards without decks are always SMS-enabled (if user has SMS opt-in)
            has_sms_enabled_cards = user.sms_opt_in
    
    # User is at risk if they have a streak and haven't reviewed today
    at_risk = (current_streak > 0 or (not has_reviewed_today and calculate_potential_streak(user.id, db)[0] > 0))
    
    message = None
    if at_risk:
        if has_sms_enabled_cards:
            # Cards available via SMS
            message = f"Don't forget to review today to keep your {current_streak}-day streak! 📚"
        else:
            # No SMS-enabled cards due - direct to web
            message = f"Keep your {current_streak}-day streak going! Log onto the web app and go to 'Review Due Cards' to continue your streak."
    
    return {
        "at_risk": at_risk,
        "current_streak": current_streak,
        "has_reviewed_today": has_reviewed_today,
        "has_due_cards": has_due_cards,
        "has_sms_enabled_cards": has_sms_enabled_cards,
        "message": message
    }


def send_streak_reminder_if_needed(user: User, db: Session) -> Dict[str, Any]:
    """
    Check if user needs a streak reminder and send it if appropriate
    
    Returns:
        Dict with success status and details
    """
    if not user.sms_opt_in or not user.phone_number:
        return {
            "success": False,
            "skipped": True,
            "reason": "User not opted into SMS or no phone number"
        }
    
    # Check if at risk
    risk_check = check_streak_at_risk(user, db)
    
    if not risk_check["at_risk"] or not risk_check["message"]:
        return {
            "success": True,
            "skipped": True,
            "reason": "User not at risk or already reviewed today"
        }
    
    # Send reminder
    try:
        service = LoopMessageService()
        result = service._send_message(
            recipient=user.phone_number,
            text=risk_check["message"]
        )
        
        return {
            "success": result.get("success", False),
            "skipped": False,
            "message_sent": risk_check["message"],
            "current_streak": risk_check["current_streak"],
            "details": result
        }
    except Exception as e:
        return {
            "success": False,
            "skipped": False,
            "error": str(e)
        }


def check_and_send_streak_reminders_for_all_users(db: Session) -> Dict[str, Any]:
    """
    Check all users and send streak reminders if needed
    Should be called once per day (e.g., at 6 PM user's local time)
    
    Returns:
        Dict with summary of reminders sent
    """
    from zoneinfo import ZoneInfo
    
    users = db.query(User).filter(
        User.sms_opt_in == True,
        User.phone_number.isnot(None)
    ).all()
    
    results = {
        "total_users_checked": len(users),
        "reminders_sent": 0,
        "skipped": 0,
        "errors": 0,
        "details": []
    }
    
    for user in users:
        try:
            # Check user's local time - only send if it's late afternoon/evening (6-8 PM)
            try:
                user_tz = ZoneInfo(user.timezone or "UTC")
                now_user_tz = datetime.now(timezone.utc).astimezone(user_tz)
                current_hour = now_user_tz.hour
                
                # Only send reminders between 6 PM and 8 PM user's local time
                if current_hour < 18 or current_hour >= 20:
                    results["skipped"] += 1
                    results["details"].append({
                        "user_id": user.id,
                        "email": user.email,
                        "status": "skipped",
                        "reason": f"Not reminder time (current hour: {current_hour})"
                    })
                    continue
            except Exception:
                # If timezone is invalid, skip this user
                results["skipped"] += 1
                continue
            
            result = send_streak_reminder_if_needed(user, db)
            
            if result.get("skipped"):
                results["skipped"] += 1
            elif result.get("success"):
                results["reminders_sent"] += 1
            else:
                results["errors"] += 1
            
            results["details"].append({
                "user_id": user.id,
                "email": user.email,
                "status": "sent" if result.get("success") else ("skipped" if result.get("skipped") else "error"),
                "current_streak": result.get("current_streak"),
                "message": result.get("message_sent") or result.get("reason") or result.get("error")
            })
        except Exception as e:
            results["errors"] += 1
            results["details"].append({
                "user_id": user.id,
                "email": user.email,
                "status": "error",
                "error": str(e)
            })
    
    return results

