from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.loop_message_service import send_due_flashcards_to_user, send_due_flashcards_to_all_users
from app.services.auth import get_current_active_user
from app.models import User
from typing import Dict, Any

router = APIRouter()

@router.post("/send-to-user/{user_id}")
def send_flashcards_to_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Send due flashcards to a specific user via LoopMessage
    """
    # Only allow admins or the user themselves
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = send_due_flashcards_to_user(user_id, db)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to send flashcards"))
    
    return result

@router.post("/send-to-all")
def send_flashcards_to_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Send due flashcards to all users who have opted into SMS
    """
    # Only allow admins
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = send_due_flashcards_to_all_users(db)
    return result

@router.post("/send-to-me")
def send_flashcards_to_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Send due flashcards to the current user
    """
    result = send_due_flashcards_to_user(current_user.id, db)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to send flashcards"))
    
    return result 