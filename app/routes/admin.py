from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db, engine
from app.models import User
from app.services.auth import get_current_active_user
from app.services.scheduler_service import send_due_flashcards_to_all_users, send_due_flashcards_to_user, get_user_flashcard_stats, cleanup_old_conversation_states
from app.services.summary_service import send_daily_summary_to_user, get_daily_review_summary
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
    """Railway cron endpoint for cleaning up old conversation states"""
    try:
        print("🧹 Starting cleanup of old conversation states...")
        result = cleanup_old_conversation_states()
        print(f"✅ Cleanup completed: {result}")
        return {"success": True, "message": "Cleanup completed", "result": result}
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return {"success": False, "error": str(e)}

@router.post("/cron/daily-summary")
async def cron_daily_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Railway cron endpoint for sending daily summaries to all users"""
    try:
        print("📊 Starting daily summary generation...")
        
        # Get all users with SMS opt-in
        users = db.query(User).filter_by(sms_opt_in=True).all()
        print(f"📱 Found {len(users)} users with SMS opt-in")
        
        results = []
        for user in users:
            try:
                result = send_daily_summary_to_user(user, db)
                results.append(result)
                print(f"📤 Summary sent to {user.phone_number}: {result.get('success', False)}")
            except Exception as e:
                print(f"❌ Error sending summary to {user.phone_number}: {e}")
                results.append({
                    "success": False,
                    "user_id": user.id,
                    "phone": user.phone_number,
                    "error": str(e)
                })
        
        successful = sum(1 for r in results if r.get("success", False))
        print(f"✅ Daily summary completed: {successful}/{len(users)} successful")
        
        return {
            "success": True, 
            "message": f"Daily summary sent to {successful}/{len(users)} users",
            "results": results
        }
        
    except Exception as e:
        print(f"❌ Error during daily summary: {e}")
        return {"success": False, "error": str(e)}

@router.get("/daily-summary/{user_id}")
async def get_user_daily_summary(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get daily summary for a specific user (requires auth)"""
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        summary = get_daily_review_summary(user_id, db)
        return {"success": True, "summary": summary}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

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

@router.post("/fix-foreign-key-cascades")
async def fix_foreign_key_cascades() -> Dict[str, Any]:
    """
    Fix foreign key constraints to use ON DELETE CASCADE
    (Temporary public endpoint for one-time fix)
    """
    try:
        sql_commands = [
            # Drop existing foreign key constraints
            "ALTER TABLE decks DROP CONSTRAINT IF EXISTS decks_user_id_fkey",
            "ALTER TABLE flashcards DROP CONSTRAINT IF EXISTS flashcards_user_id_fkey", 
            "ALTER TABLE flashcards DROP CONSTRAINT IF EXISTS flashcards_deck_id_fkey",
            "ALTER TABLE card_reviews DROP CONSTRAINT IF EXISTS card_reviews_user_id_fkey",
            "ALTER TABLE card_reviews DROP CONSTRAINT IF EXISTS card_reviews_flashcard_id_fkey",
            "ALTER TABLE study_sessions DROP CONSTRAINT IF EXISTS study_sessions_user_id_fkey",
            "ALTER TABLE conversation_state DROP CONSTRAINT IF EXISTS conversation_state_user_id_fkey",
            
            # Recreate with ON DELETE CASCADE
            "ALTER TABLE decks ADD CONSTRAINT decks_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE",
            "ALTER TABLE flashcards ADD CONSTRAINT flashcards_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE",
            "ALTER TABLE flashcards ADD CONSTRAINT flashcards_deck_id_fkey FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE", 
            "ALTER TABLE card_reviews ADD CONSTRAINT card_reviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE",
            "ALTER TABLE card_reviews ADD CONSTRAINT card_reviews_flashcard_id_fkey FOREIGN KEY (flashcard_id) REFERENCES flashcards(id) ON DELETE CASCADE",
            "ALTER TABLE study_sessions ADD CONSTRAINT study_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE",
            "ALTER TABLE conversation_state ADD CONSTRAINT conversation_state_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"
        ]
        
        with engine.connect() as connection:
            for sql in sql_commands:
                print(f"Executing: {sql}")
                connection.execute(text(sql))
            connection.commit()
        
        return {
            "success": True,
            "message": "Foreign key constraints updated with ON DELETE CASCADE",
            "commands_executed": len(sql_commands)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating foreign key constraints: {str(e)}")

@router.post("/migrate-google-oauth")
async def migrate_google_oauth() -> Dict[str, Any]:
    """
    Add Google OAuth columns to users table
    (Temporary public endpoint for one-time fix)
    """
    try:
        # SQL to add the Google OAuth columns
        sql_commands = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(255)",
            "ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL",
            "ALTER TABLE users ALTER COLUMN phone_number DROP NOT NULL",
            "CREATE INDEX IF NOT EXISTS ix_users_google_id ON users (google_id)"
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
            "message": "Google OAuth columns migration completed",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error migrating database: {str(e)}")

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
