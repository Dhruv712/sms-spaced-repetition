from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Flashcard
from app.services.session_manager import set_conversation_state
from app.services.loop_message_service import LoopMessageService
from app.services.auth import get_current_active_user
from app.services.loop_message_service import send_due_flashcards_to_user, send_due_flashcards_to_all_users
from typing import Dict, Any

router = APIRouter(tags=["Loop_Test"])

@router.post("/send-test-flashcard")
async def send_test_flashcard(db: Session = Depends(get_db)):
    """Send a test flashcard (for testing purposes only)"""
    
    try:
        # Find user
        user = db.query(User).filter_by(phone_number="+18054901242").first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Find the DNA flashcard (ID 4)
        flashcard = db.query(Flashcard).filter_by(user_id=user.id, id=4).first()
        if not flashcard:
            # Fallback to any flashcard
            flashcard = db.query(Flashcard).filter_by(user_id=user.id).first()
            if not flashcard:
                raise HTTPException(status_code=404, detail="No flashcards found")
        
        # Set conversation state
        set_conversation_state(user.id, flashcard.id, db)
        
        # Send the flashcard
        service = LoopMessageService()
        result = service.send_flashcard(user.phone_number, flashcard)
        
        if result.get("success"):
            return {
                "success": True,
                "message": f"Test flashcard sent to {user.phone_number}",
                "flashcard_id": flashcard.id,
                "concept": flashcard.concept
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to send flashcard: {result.get('error')}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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