from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.services.auth import get_current_active_user, get_current_user_optional
from app.services.email_service import send_contact_email
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional

router = APIRouter(tags=["Help"])

class ContactForm(BaseModel):
    subject: str
    message: str
    email: Optional[str] = None  # Optional email for non-logged-in users

@router.post("/contact")
async def submit_contact_form(
    contact: ContactForm,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Submit a contact form message
    Can be used by logged-in users (uses their account email) or non-logged-in users (requires email field)
    """
    try:
        if not contact.subject or not contact.message:
            raise HTTPException(status_code=400, detail="Subject and message are required")
        
        # Determine email to use
        user_email = None
        if current_user:
            user_email = current_user.email
        elif contact.email:
            user_email = contact.email
        else:
            raise HTTPException(status_code=400, detail="Email is required for non-logged-in users")
        
        # Send email
        result = send_contact_email(
            user_email=user_email,
            subject=contact.subject,
            message=contact.message
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": "Your message has been sent successfully. We'll get back to you soon!"
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Failed to send message")
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting contact form: {str(e)}")

