from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db, engine
from app.models import User
from app.services.auth import get_current_active_user
from app.services.scheduler_service import send_due_flashcards_to_all_users, get_user_flashcard_stats
from typing import Dict, Any

router = APIRouter(tags=["Admin"])

@router.post("/migrate-sm2-columns")
async def migrate_sm2_columns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Add SM-2 columns to card_reviews table
    (Admin only)
    """
    # Check if user is admin
    if current_user.email != "dhruv.sumathi@gmail.com":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # SQL to add the SM-2 columns
        sql_commands = [
            """
            ALTER TABLE card_reviews 
            ADD COLUMN IF NOT EXISTS repetition_count INTEGER DEFAULT 0;
            """,
            """
            ALTER TABLE card_reviews 
            ADD COLUMN IF NOT EXISTS ease_factor FLOAT DEFAULT 2.5;
            """,
            """
            ALTER TABLE card_reviews 
            ADD COLUMN IF NOT EXISTS interval_days INTEGER DEFAULT 0;
            """
        ]
        
        results = []
        with engine.connect() as conn:
            for i, sql in enumerate(sql_commands, 1):
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    results.append(f"✅ SQL command {i} executed successfully")
                except Exception as e:
                    results.append(f"⚠️ SQL command {i} result: {e}")
        
        return {
            "success": True,
            "message": "SM-2 columns migration completed",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error migrating database: {str(e)}")

@router.post("/migrate-sm2-columns-public")
async def migrate_sm2_columns_public() -> Dict[str, Any]:
    """
    Add SM-2 columns to card_reviews table
    (Temporary public endpoint for one-time fix)
    """
    try:
        # SQL to add the SM-2 columns
        sql_commands = [
            "ALTER TABLE card_reviews ADD COLUMN IF NOT EXISTS repetition_count INTEGER DEFAULT 0",
            "ALTER TABLE card_reviews ADD COLUMN IF NOT EXISTS ease_factor FLOAT DEFAULT 2.5",
            "ALTER TABLE card_reviews ADD COLUMN IF NOT EXISTS interval_days INTEGER DEFAULT 0"
        ]
        
        results = []
        with engine.connect() as conn:
            for i, sql in enumerate(sql_commands, 1):
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    results.append(f"✅ SQL command {i} executed successfully")
                except Exception as e:
                    results.append(f"⚠️ SQL command {i} result: {e}")
        
        return {
            "success": True,
            "message": "SM-2 columns migration completed",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error migrating database: {str(e)}")

@router.post("/send-due-flashcards")
async def trigger_scheduled_flashcards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Manually trigger sending due flashcards to all users
    (Admin only)
    """
    # Check if user is admin (you can add admin field to User model later)
    if current_user.email != "dhruv.sumathi@gmail.com":  # Temporary admin check
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = send_due_flashcards_to_all_users()
        return {
            "success": True,
            "message": "Scheduled flashcard sending completed",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending flashcards: {str(e)}")

@router.post("/trigger-scheduled-flashcards")
async def trigger_scheduled_flashcards_manual() -> Dict[str, Any]:
    """
    Manually trigger the scheduled flashcard sending
    (Temporary public endpoint for testing)
    """
    try:
        from app.services.scheduler_service import scheduled_flashcard_task
        
        # Run the task synchronously for immediate feedback
        result = scheduled_flashcard_task.delay()
        
        return {
            "success": True,
            "message": "Scheduled flashcard task triggered",
            "task_id": result.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering task: {str(e)}")

@router.post("/trigger-scheduled-flashcards-direct")
async def trigger_scheduled_flashcards_direct() -> Dict[str, Any]:
    """
    Manually trigger the scheduled flashcard sending directly
    (Temporary public endpoint for testing)
    """
    try:
        from app.services.scheduler_service import send_due_flashcards_to_all_users
        
        # Call the function directly (synchronously)
        result = send_due_flashcards_to_all_users()
        
        return {
            "success": True,
            "message": "Scheduled flashcard sending completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering scheduling: {str(e)}")

@router.get("/user-stats/{user_id}")
async def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get flashcard statistics for a user
    """
    # Check if user is admin or requesting their own stats
    if current_user.email != "dhruv.sumathi@gmail.com" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        stats = get_user_flashcard_stats(user_id, db)
        return {
            "success": True,
            "user_id": user_id,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user stats: {str(e)}")

@router.post("/send-to-user/{user_id}")
async def send_flashcards_to_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Manually send due flashcards to a specific user
    """
    # Check if user is admin
    if current_user.email != "dhruv.sumathi@gmail.com":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.services.scheduler_service import send_due_flashcards_to_user
        result = send_due_flashcards_to_user(user_id, db)
        return {
            "success": True,
            "user_id": user_id,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending flashcards: {str(e)}")

@router.post("/cron/send-flashcards")
async def cron_send_flashcards() -> Dict[str, Any]:
    """
    Cron endpoint for sending due flashcards
    This can be called by Railway's cron service
    """
    try:
        from app.services.scheduler_service import send_due_flashcards_to_all_users
        
        # Call the function directly
        result = send_due_flashcards_to_all_users()
        
        return {
            "success": True,
            "message": "Cron flashcard sending completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in cron task: {str(e)}")

@router.post("/cron/cleanup")
async def cron_cleanup() -> Dict[str, Any]:
    """
    Cron endpoint for cleaning up old conversation states
    """
    try:
        from app.services.scheduler_service import cleanup_old_conversation_states
        
        # Call the function directly
        cleanup_old_conversation_states()
        
        return {
            "success": True,
            "message": "Cron cleanup completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in cron cleanup: {str(e)}")

@router.delete("/delete-user/{user_id}")
async def delete_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Delete a user and all their associated data
    (Admin only)
    """
    # Check if user is admin
    if current_user.email != "dhruv.sumathi@gmail.com":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models import User, Flashcard, CardReview, ConversationState
        
        # Find the user to delete
        user_to_delete = db.query(User).filter_by(id=user_id).first()
        if not user_to_delete:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Count associated data
        flashcard_count = db.query(Flashcard).filter_by(user_id=user_id).count()
        review_count = db.query(CardReview).filter_by(user_id=user_id).count()
        conversation_count = db.query(ConversationState).filter_by(user_id=user_id).count()
        
        # Delete associated data first (foreign key constraints)
        db.query(ConversationState).filter_by(user_id=user_id).delete()
        db.query(CardReview).filter_by(user_id=user_id).delete()
        db.query(Flashcard).filter_by(user_id=user_id).delete()
        
        # Delete the user
        db.delete(user_to_delete)
        db.commit()
        
        return {
            "success": True,
            "message": f"User {user_to_delete.email} deleted successfully",
            "deleted_data": {
                "user_id": user_id,
                "email": user_to_delete.email,
                "flashcards_deleted": flashcard_count,
                "reviews_deleted": review_count,
                "conversations_deleted": conversation_count
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

@router.delete("/delete-user-2-public")
async def delete_user_2_public(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Delete user ID 2 (waterfire712@gmail.com) - public endpoint for one-time use
    """
    try:
        from app.models import User, Flashcard, CardReview, ConversationState
        
        # Find the user to delete
        user_to_delete = db.query(User).filter_by(id=2).first()
        if not user_to_delete:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Count associated data
        flashcard_count = db.query(Flashcard).filter_by(user_id=2).count()
        review_count = db.query(CardReview).filter_by(user_id=2).count()
        conversation_count = db.query(ConversationState).filter_by(user_id=2).count()
        
        # Delete associated data first (foreign key constraints)
        db.query(ConversationState).filter_by(user_id=2).delete()
        db.query(CardReview).filter_by(user_id=2).delete()
        db.query(Flashcard).filter_by(user_id=2).delete()
        
        # Delete the user
        db.delete(user_to_delete)
        db.commit()
        
        return {
            "success": True,
            "message": f"User {user_to_delete.email} deleted successfully",
            "deleted_data": {
                "user_id": 2,
                "email": user_to_delete.email,
                "flashcards_deleted": flashcard_count,
                "reviews_deleted": review_count,
                "conversations_deleted": conversation_count
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")
