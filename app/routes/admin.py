from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime, timedelta, timezone
from app.database import get_db, engine
from app.models import User, Flashcard, CardReview, Deck, ConversationState
from app.services.auth import get_current_active_user, require_admin_access
from app.services.scheduler_service import send_due_flashcards_to_all_users, send_due_flashcards_to_user, get_user_flashcard_stats, cleanup_old_conversation_states
from app.services.summary_service import send_daily_summary_to_user, get_daily_review_summary
from typing import Dict, Any, List

router = APIRouter(tags=["Admin"])

@router.post("/create-user-deck-sms-settings-table")
async def create_user_deck_sms_settings_table(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create user_deck_sms_settings table for deck muting feature
    (Admin access required)
    """
    await require_admin_access(request, db)
    try:
        sql_commands = [
            """
            CREATE TABLE IF NOT EXISTS user_deck_sms_settings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                deck_id INTEGER NOT NULL REFERENCES decks(id) ON DELETE CASCADE,
                sms_enabled BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_user_deck_sms UNIQUE (user_id, deck_id)
            );
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_user_deck_sms_user_id ON user_deck_sms_settings(user_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_user_deck_sms_deck_id ON user_deck_sms_settings(deck_id);
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
                    results.append(f"❌ SQL command {i} failed: {str(e)}")
                    # Continue with other commands even if one fails
        
        return {
            "success": True,
            "message": "user_deck_sms_settings table creation completed",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating table: {str(e)}")

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
    if not current_user.is_admin:
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
async def migrate_sm2_columns_public(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Add SM-2 columns to card_reviews table
    (Admin access required)
    """
    await require_admin_access(request, db)
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
    # Check if user is admin
    if not current_user.is_admin:
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
    if not current_user.is_admin and current_user.id != user_id:
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
    if not current_user.is_admin:
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
async def cron_send_flashcards(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Cron endpoint for sending due flashcards
    This can be called by Railway's cron service
    (Requires admin secret key in X-Admin-Secret header)
    """
    await require_admin_access(request, db)
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
async def cron_cleanup(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Railway cron endpoint for cleaning up old conversation states
    (Requires admin secret key in X-Admin-Secret header)
    """
    await require_admin_access(request, db)
    try:
        print("🧹 Starting cleanup of old conversation states...")
        result = cleanup_old_conversation_states()
        print(f"✅ Cleanup completed: {result}")
        return {"success": True, "message": "Cleanup completed", "result": result}
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return {"success": False, "error": str(e)}

@router.post("/cron/daily-summary")
async def cron_daily_summary(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Railway cron endpoint for sending daily summaries to all users
    This should be called hourly. It will only send summaries to users
    when it's 9 PM or 10 PM in their timezone.
    (Requires admin secret key in X-Admin-Secret header)
    """
    await require_admin_access(request, db)
    try:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        
        print("📊 Starting daily summary generation...")
        
        # Get all users with SMS opt-in
        users = db.query(User).filter_by(sms_opt_in=True).all()
        print(f"📱 Found {len(users)} users with SMS opt-in")
        
        # Get current UTC time
        now_utc = datetime.now(ZoneInfo("UTC"))
        
        results = []
        for user in users:
            try:
                # Check if it's an appropriate time in user's timezone (9 PM or 10 PM)
                try:
                    user_tz = ZoneInfo(user.timezone)
                    now_user_tz = now_utc.astimezone(user_tz)
                    current_hour = now_user_tz.hour
                    
                    if current_hour not in [21, 22]:  # 9 PM or 10 PM
                        print(f"⏭️ Skipping user {user.id}: current hour {current_hour} not summary time (9-10 PM)")
                        results.append({
                            "success": True,
                            "user_id": user.id,
                            "phone": user.phone_number,
                            "message": "skipped",
                            "reason": f"Not summary time (hour {current_hour} in {user.timezone})"
                        })
                        continue
                except Exception as e:
                    print(f"⚠️ Error checking timezone for user {user.id}: {e}, skipping")
                    results.append({
                        "success": False,
                        "user_id": user.id,
                        "phone": user.phone_number,
                        "error": f"Invalid timezone: {str(e)}"
                    })
                    continue
                
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
        # Get user to get their timezone
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get summary for yesterday in user's timezone
        summary = get_daily_review_summary(user_id, db, user_timezone=user.timezone)
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
    if not current_user.is_admin:
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

@router.post("/migrate-conversation-state-fields-public")
async def migrate_conversation_state_fields_public(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Add message_count and last_sent_flashcard_id to conversation_state table
    (Admin access required)
    """
    await require_admin_access(request, db)
    try:
        sql_commands = [
            "ALTER TABLE conversation_state ADD COLUMN IF NOT EXISTS message_count INTEGER DEFAULT 0",
            "ALTER TABLE conversation_state ADD COLUMN IF NOT EXISTS last_sent_flashcard_id INTEGER"
        ]
        
        # Add foreign key constraint separately (PostgreSQL doesn't support IF NOT EXISTS for constraints)
        constraint_sql = """
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint 
                    WHERE conname = 'fk_conversation_state_last_sent_flashcard'
                ) THEN
                    ALTER TABLE conversation_state 
                    ADD CONSTRAINT fk_conversation_state_last_sent_flashcard 
                    FOREIGN KEY (last_sent_flashcard_id) 
                    REFERENCES flashcards(id) ON DELETE SET NULL;
                END IF;
            END $$;
        """
        
        results = []
        with engine.connect() as conn:
            for i, sql in enumerate(sql_commands, 1):
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    results.append(f"✅ SQL command {i} executed successfully")
                except Exception as e:
                    results.append(f"⚠️ SQL command {i} result: {e}")
            
            # Add foreign key constraint separately (PostgreSQL doesn't support IF NOT EXISTS for constraints)
            try:
                conn.execute(text(constraint_sql))
                conn.commit()
                results.append("✅ Foreign key constraint added successfully")
            except Exception as e:
                results.append(f"⚠️ Foreign key constraint result: {e}")
        
        return {
            "success": True,
            "message": "Conversation state fields migration completed",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error migrating database: {str(e)}")

@router.post("/migrate-user-streak-fields-public")
async def migrate_user_streak_fields_public(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Add streak tracking fields to users table
    (Admin access required)
    """
    await require_admin_access(request, db)
    try:
        sql_commands = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS current_streak_days INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS longest_streak_days INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_study_date TIMESTAMP WITH TIME ZONE"
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
            "message": "User streak fields migration completed",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error migrating database: {str(e)}")

@router.delete("/delete-user-2-public")
async def delete_user_2_public(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Delete user ID 2 (waterfire712@gmail.com) - Admin access required
    """
    await require_admin_access(request, db)
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

@router.post("/migrate-preferred-text-times-public")
async def migrate_preferred_text_times_public(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Add preferred_text_times field to users table
    (Admin access required)
    """
    await require_admin_access(request, db)
    try:
        sql_commands = [
            """
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS preferred_text_times JSON;
            """,
            """
            -- Migrate existing users: convert start_hour to preferred_text_times array
            UPDATE users 
            SET preferred_text_times = json_build_array(preferred_start_hour)
            WHERE preferred_text_times IS NULL AND preferred_start_hour IS NOT NULL;
            """,
            """
            -- Set default for users with no preferred_start_hour
            UPDATE users 
            SET preferred_text_times = '[12]'::json
            WHERE preferred_text_times IS NULL;
            """
        ]
        
        results = []
        with engine.connect() as conn:
            for i, sql in enumerate(sql_commands, 1):
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    results.append(f"Command {i}: Success")
                except Exception as e:
                    results.append(f"Command {i}: Error - {str(e)}")
        
        return {
            "success": True,
            "message": "Migration completed",
            "results": results
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/migrate-subscription-fields-public")
async def migrate_subscription_fields_public(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Add Stripe subscription fields to users table
    (Admin access required)
    """
    await require_admin_access(request, db)
    try:
        sql_commands = [
            """
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS is_premium BOOLEAN DEFAULT FALSE;
            """,
            """
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255);
            """,
            """
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR(255);
            """,
            """
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS stripe_subscription_status VARCHAR(50);
            """,
            """
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS stripe_price_id VARCHAR(255);
            """,
            """
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS subscription_start_date TIMESTAMP WITH TIME ZONE;
            """,
            """
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS subscription_end_date TIMESTAMP WITH TIME ZONE;
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_users_stripe_customer_id ON users(stripe_customer_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_users_stripe_subscription_id ON users(stripe_subscription_id);
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
                    results.append(f"⚠️ SQL command {i} result: {str(e)}")
        
        return {
            "success": True,
            "message": "Subscription fields migration completed",
            "results": results
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/migrate-sms-review-field-public")
async def migrate_sms_review_field_public(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Add is_sms_review field to card_reviews table
    (Admin access required)
    """
    await require_admin_access(request, db)
    try:
        sql_command = """
            ALTER TABLE card_reviews 
            ADD COLUMN IF NOT EXISTS is_sms_review BOOLEAN DEFAULT FALSE;
        """
        
        with engine.connect() as conn:
            conn.execute(text(sql_command))
            conn.commit()
        
        return {
            "success": True,
            "message": "SMS review field migration completed"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/grandfather-users-premium-public")
async def grandfather_users_premium_public(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Grandfather existing users to premium (except dhruv.sumathi@gmail.com for testing)
    (Admin access required)
    """
    await require_admin_access(request, db)
    try:
        sql_command = """
            UPDATE users 
            SET is_premium = TRUE 
            WHERE email != 'dhruv.sumathi@gmail.com' AND is_premium = FALSE;
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(sql_command))
            conn.commit()
            rows_updated = result.rowcount
        
        return {
            "success": True,
            "message": f"Grandfathered {rows_updated} users to premium",
            "users_updated": rows_updated
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/reset-premium-status-public")
async def reset_premium_status_public(
    email: str,
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Reset premium status for a user (for testing)
    (Admin access required)
    """
    await require_admin_access(request, db)
    try:
        sql_command = """
            UPDATE users 
            SET is_premium = FALSE,
                stripe_subscription_id = NULL,
                stripe_subscription_status = NULL,
                stripe_price_id = NULL,
                subscription_start_date = NULL,
                subscription_end_date = NULL
            WHERE email = :email;
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(sql_command), {"email": email})
            conn.commit()
            rows_updated = result.rowcount
        
        if rows_updated == 0:
            return {
                "success": False,
                "message": f"No user found with email: {email}"
            }
        
        return {
            "success": True,
            "message": f"Reset premium status for {email}",
            "email": email
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/set-premium-status-public")
async def set_premium_status_public(
    request: Request,
    email: str,
    is_premium: bool = True,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Set premium status for a user (for testing/admin use)
    (Admin access required)
    """
    await require_admin_access(request, db)
    try:
        from datetime import datetime, timezone, timedelta
        
        if is_premium:
            # Set premium to TRUE and add some test subscription data
            sql_command = """
                UPDATE users 
                SET is_premium = TRUE,
                    stripe_subscription_status = 'active',
                    subscription_start_date = :start_date,
                    subscription_end_date = :end_date
                WHERE email = :email;
            """
            
            # Set dates: start now, end in 30 days
            start_date = datetime.now(timezone.utc)
            end_date = start_date + timedelta(days=30)
            
            params = {
                "email": email,
                "start_date": start_date,
                "end_date": end_date
            }
        else:
            # Remove premium status
            sql_command = """
                UPDATE users 
                SET is_premium = FALSE,
                    stripe_subscription_status = NULL,
                    subscription_start_date = NULL,
                    subscription_end_date = NULL
                WHERE email = :email;
            """
            
            params = {"email": email}
        
        with engine.connect() as conn:
            result = conn.execute(
                text(sql_command), 
                params
            )
            conn.commit()
            rows_updated = result.rowcount
        
        if rows_updated == 0:
            return {
                "success": False,
                "message": f"No user found with email: {email}"
            }
        
        action = "granted" if is_premium else "removed"
        return {
            "success": True,
            "message": f"Premium status {action} for {email}",
            "email": email,
            "is_premium": is_premium
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/migrate-admin-field-public")
async def migrate_admin_field_public(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Add is_admin field to users table and set dhruv.sumathi@gmail.com as admin
    (Requires X-Admin-Secret header - this endpoint works before is_admin column exists)
    """
    from app.utils.config import settings
    
    # For first-time setup, ONLY allow admin secret key (can't check is_admin yet!)
    admin_secret = request.headers.get("X-Admin-Secret")
    if not (admin_secret and settings.ADMIN_SECRET_KEY and admin_secret == settings.ADMIN_SECRET_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required. Provide X-Admin-Secret header."
        )
    
    try:
        sql_commands = [
            """
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;
            """,
            """
            -- Set dhruv.sumathi@gmail.com as admin
            UPDATE users 
            SET is_admin = TRUE 
            WHERE email = 'dhruv.sumathi@gmail.com';
            """
        ]
        
        results = []
        with engine.connect() as conn:
            for i, sql in enumerate(sql_commands, 1):
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    results.append(f"Command {i}: Success")
                except Exception as e:
                    results.append(f"Command {i}: Error - {str(e)}")
        
        return {
            "success": True,
            "message": "Admin field migration completed",
            "results": results
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/dashboard")
async def get_admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get admin dashboard statistics and user list
    (Admin access required)
    """
    # Check admin access
    await require_admin_access(request, db)
    
    # Verify user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        now = datetime.now(timezone.utc)
        last_7_days = now - timedelta(days=7)
        last_30_days = now - timedelta(days=30)
        
        # Overall statistics
        total_users = db.query(func.count(User.id)).scalar() or 0
        premium_users = db.query(func.count(User.id)).filter(User.is_premium == True).scalar() or 0
        sms_opt_in_users = db.query(func.count(User.id)).filter(User.sms_opt_in == True).scalar() or 0
        active_users = db.query(func.count(func.distinct(User.id))).join(
            CardReview, User.id == CardReview.user_id
        ).filter(CardReview.review_date >= last_30_days).scalar() or 0
        
        # Recent signups
        new_users_7d = db.query(func.count(User.id)).filter(
            User.created_at >= last_7_days
        ).scalar() or 0
        new_users_30d = db.query(func.count(User.id)).filter(
            User.created_at >= last_30_days
        ).scalar() or 0
        
        # Content statistics
        total_flashcards = db.query(func.count(Flashcard.id)).scalar() or 0
        total_reviews = db.query(func.count(CardReview.id)).scalar() or 0
        total_decks = db.query(func.count(Deck.id)).scalar() or 0
        
        # Recent activity
        reviews_last_7d = db.query(func.count(CardReview.id)).filter(
            CardReview.review_date >= last_7_days
        ).scalar() or 0
        reviews_last_30d = db.query(func.count(CardReview.id)).filter(
            CardReview.review_date >= last_30_days
        ).scalar() or 0
        
        # Users with SMS conversation state
        users_with_sms_conversation = db.query(func.count(func.distinct(ConversationState.user_id))).scalar() or 0
        
        # Get user list with details
        users = db.query(User).order_by(User.created_at.desc()).all()
        
        user_list = []
        for user in users:
            # Get user stats
            user_flashcards = db.query(func.count(Flashcard.id)).filter(
                Flashcard.user_id == user.id
            ).scalar() or 0
            
            user_reviews = db.query(func.count(CardReview.id)).filter(
                CardReview.user_id == user.id
            ).scalar() or 0
            
            user_decks = db.query(func.count(Deck.id)).filter(
                Deck.user_id == user.id
            ).scalar() or 0
            
            # Check if user has SMS conversation
            has_sms_conversation = db.query(ConversationState).filter(
                ConversationState.user_id == user.id
            ).first() is not None
            
            # Get last review date
            last_review = db.query(CardReview).filter(
                CardReview.user_id == user.id
            ).order_by(CardReview.review_date.desc()).first()
            
            last_review_date = last_review.review_date.isoformat() if last_review else None
            
            user_list.append({
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_premium": user.is_premium or False,
                "is_admin": user.is_admin or False,
                "sms_opt_in": user.sms_opt_in or False,
                "has_sms_conversation": has_sms_conversation,
                "phone_number": user.phone_number,
                "timezone": user.timezone,
                "current_streak_days": user.current_streak_days or 0,
                "longest_streak_days": user.longest_streak_days or 0,
                "flashcards_count": user_flashcards,
                "reviews_count": user_reviews,
                "decks_count": user_decks,
                "last_review_date": last_review_date,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "subscription_status": user.stripe_subscription_status,
                "subscription_end_date": user.subscription_end_date.isoformat() if user.subscription_end_date else None,
            })
        
        return {
            "success": True,
            "stats": {
                "total_users": total_users,
                "premium_users": premium_users,
                "sms_opt_in_users": sms_opt_in_users,
                "active_users": active_users,
                "users_with_sms_conversation": users_with_sms_conversation,
                "new_users_7d": new_users_7d,
                "new_users_30d": new_users_30d,
                "total_flashcards": total_flashcards,
                "total_reviews": total_reviews,
                "total_decks": total_decks,
                "reviews_last_7d": reviews_last_7d,
                "reviews_last_30d": reviews_last_30d,
            },
            "users": user_list
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching admin dashboard: {str(e)}"
        )
