"""
Automated scheduling service for sending due flashcards
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Flashcard, CardReview
from app.services.loop_message_service import LoopMessageService
from app.services.session_manager import get_next_due_flashcard, set_conversation_state
from app.services.reminder import send_study_reminder
from app.utils.celery_app import celery_app

logger = logging.getLogger(__name__)

@celery_app.task
def scheduled_flashcard_task():
    """
    Celery task for sending due flashcards to all users
    This will be called by the scheduler
    """
    logger.info("🕐 Celery task: Starting scheduled flashcard sending...")
    try:
        result = send_due_flashcards_to_all_users()
        logger.info(f"✅ Celery task completed: {result}")
        return result
    except Exception as e:
        logger.error(f"❌ Celery task failed: {e}")
        raise

@celery_app.task
def cleanup_conversation_states_task():
    """
    Celery task for cleaning up old conversation states
    """
    logger.info("🧹 Celery task: Cleaning up old conversation states...")
    try:
        cleanup_old_conversation_states()
        logger.info("✅ Celery task: Cleanup completed")
    except Exception as e:
        logger.error(f"❌ Celery task: Cleanup failed: {e}")
        raise

def send_due_flashcards_to_all_users():
    """
    Send due flashcards to all users who have opted into SMS
    This function checks if the current hour (in user's timezone) matches their preferred_text_times
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo
    
    logger.info("🕐 Starting scheduled flashcard sending...")
    
    db = SessionLocal()
    try:
        # Get all active users who have opted into SMS
        users = db.query(User).filter_by(
            is_active=True, 
            sms_opt_in=True
        ).all()
        
        logger.info(f"📱 Found {len(users)} users with SMS opt-in")
        
        # Get current UTC time
        now_utc = datetime.now(ZoneInfo("UTC"))
        
        results = []
        for user in users:
            try:
                # Get user's preferred text times
                preferred_times = user.preferred_text_times
                if preferred_times is None:
                    # Fallback to old system: use start_hour if available
                    if user.preferred_start_hour is not None:
                        preferred_times = [user.preferred_start_hour]
                    else:
                        preferred_times = [12]  # Default to noon
                
                # Convert current UTC time to user's timezone
                try:
                    user_tz = ZoneInfo(user.timezone)
                    now_user_tz = now_utc.astimezone(user_tz)
                    current_hour = now_user_tz.hour
                except Exception as e:
                    logger.warning(f"⚠️ Invalid timezone for user {user.id}: {user.timezone}, using UTC")
                    current_hour = now_utc.hour
                
                # Check if current hour matches any of user's preferred times
                if current_hour not in preferred_times:
                    logger.info(f"⏭️ Skipping user {user.id}: current hour {current_hour} not in preferred times {preferred_times}")
                    results.append({
                        "user_id": user.id,
                        "phone_number": user.phone_number,
                        "result": {"success": True, "message": "skipped", "reason": f"Hour {current_hour} not in preferred times"}
                    })
                    continue
                
                # Send flashcards to this user
                result = send_due_flashcards_to_user(user.id, db)
                results.append({
                    "user_id": user.id,
                    "phone_number": user.phone_number,
                    "result": result
                })
                logger.info(f"📤 User {user.id}: {result.get('message', 'Unknown result')}")
            except Exception as e:
                logger.error(f"❌ Error sending flashcards to user {user.id}: {e}")
                results.append({
                    "user_id": user.id,
                    "phone_number": user.phone_number,
                    "result": {"success": False, "error": str(e)}
                })
        
        logger.info(f"✅ Completed sending flashcards to {len(users)} users")
        return {
            "total_users": len(users),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Error in send_due_flashcards_to_all_users: {e}")
        raise
    finally:
        db.close()

def send_due_flashcards_to_user(user_id: int, db: Session = None):
    """
    Send due flashcards to a specific user
    
    Args:
        user_id: User ID to send flashcards to
        db: Database session (optional, will create one if not provided)
        
    Returns:
        Dict containing results
    """
    should_close_db = False
    if db is None:
        db = SessionLocal()
        should_close_db = True
    
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return {"success": False, "error": "User not found"}
        
        if not user.sms_opt_in:
            return {"success": False, "error": "User has not opted into SMS"}
        
        logger.info(f"🔍 Checking due flashcards for user {user_id} ({user.phone_number})")
        
        # Get next due flashcard
        due_card = get_next_due_flashcard(user_id, db)
        
        if not due_card:
            logger.info(f"📭 No due flashcards for user {user_id}")
            return {
                "success": True,
                "message": "no_due_flashcards",
                "flashcard_id": None
            }
        
        logger.info(f"📚 Found due flashcard: {due_card.concept} (ID: {due_card.id})")
        
        # Set conversation state to waiting for answer
        set_conversation_state(user_id, due_card.id, db)
        logger.info(f"🗣️ Set conversation state for user {user_id}, flashcard {due_card.id}")
        
        # Get message count and session progress for skip reminder and progress indicator
        from app.models import ConversationState
        state_after = db.query(ConversationState).filter_by(user_id=user_id).first()
        message_count = state_after.message_count if state_after else 0
        current_card = getattr(state_after, 'session_current_card', None) if state_after else None
        total_cards = getattr(state_after, 'session_total_cards', None) if state_after else None
        
        # Send the flashcard
        try:
            service = LoopMessageService()
            result = service.send_flashcard(user.phone_number, due_card, message_count, current_card, total_cards)
            
            if result.get("success"):
                logger.info(f"✅ Flashcard sent successfully to {user.phone_number}")
                return {
                    "success": True,
                    "message": "flashcard_sent",
                    "flashcard_id": due_card.id,
                    "concept": due_card.concept,
                    "phone_number": user.phone_number
                }
            else:
                logger.error(f"❌ Failed to send flashcard: {result.get('error')}")
                return {
                    "success": False,
                    "error": f"Failed to send flashcard: {result.get('error')}"
                }
                
        except Exception as e:
            logger.error(f"❌ Error sending flashcard: {e}")
            return {"success": False, "error": str(e)}
            
    except Exception as e:
        logger.error(f"❌ Error in send_due_flashcards_to_user: {e}")
        return {"success": False, "error": str(e)}
    finally:
        if should_close_db:
            db.close()

def get_user_flashcard_stats(user_id: int, db: Session = None):
    """
    Get statistics about a user's flashcards
    
    Args:
        user_id: User ID
        db: Database session (optional)
        
    Returns:
        Dict with flashcard statistics
    """
    should_close_db = False
    if db is None:
        db = SessionLocal()
        should_close_db = True
    
    try:
        # Total flashcards
        total_flashcards = db.query(Flashcard).filter_by(user_id=user_id).count()
        
        # Due flashcards
        due_flashcards = db.query(Flashcard).filter(
            Flashcard.user_id == user_id,
            ~Flashcard.id.in_(
                db.query(CardReview.flashcard_id).filter(
                    CardReview.user_id == user_id,
                    CardReview.next_review_date > datetime.utcnow()
                ).subquery()
            )
        ).count()
        
        # Recently reviewed (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_reviews = db.query(CardReview).filter(
            CardReview.user_id == user_id,
            CardReview.review_date >= week_ago
        ).count()
        
        return {
            "total_flashcards": total_flashcards,
            "due_flashcards": due_flashcards,
            "recent_reviews": recent_reviews
        }
        
    finally:
        if should_close_db:
            db.close()

def cleanup_old_conversation_states():
    """
    Clean up old conversation states that are no longer needed
    """
    from app.models import ConversationState
    
    db = SessionLocal()
    try:
        # Find conversation states older than 1 hour
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        old_states = db.query(ConversationState).filter(
            ConversationState.last_message_at < hour_ago,
            ConversationState.state == "waiting_for_answer"
        ).all()
        
        for state in old_states:
            state.state = "idle"
            state.current_flashcard_id = None
            logger.info(f"🔄 Cleaned up old conversation state for user {state.user_id}")
        
        db.commit()
        logger.info(f"✅ Cleaned up {len(old_states)} old conversation states")
        
    except Exception as e:
        logger.error(f"❌ Error cleaning up conversation states: {e}")
        db.rollback()
    finally:
        db.close()
