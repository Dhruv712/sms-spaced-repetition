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

logger = logging.getLogger(__name__)

def send_due_flashcards_to_all_users():
    """
    Send due flashcards to all users who have opted into SMS
    This is the main function that should be called by a scheduler
    """
    logger.info("🕐 Starting scheduled flashcard sending...")
    
    db = SessionLocal()
    try:
        # Get all active users who have opted into SMS
        users = db.query(User).filter_by(
            is_active=True, 
            sms_opt_in=True
        ).all()
        
        logger.info(f"📱 Found {len(users)} users with SMS opt-in")
        
        results = []
        for user in users:
            try:
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
        
        # Send the flashcard
        try:
            service = LoopMessageService()
            result = service.send_flashcard(user.phone_number, due_card)
            
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
