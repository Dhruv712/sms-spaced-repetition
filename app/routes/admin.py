from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.services.auth import get_current_active_user
from app.services.scheduler_service import send_due_flashcards_to_all_users, get_user_flashcard_stats
from typing import Dict, Any

router = APIRouter(tags=["Admin"])

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
