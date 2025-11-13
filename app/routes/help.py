from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.services.auth import get_current_active_user
from app.services.email_service import send_contact_email
from pydantic import BaseModel, EmailStr
from typing import Dict, Any

router = APIRouter(tags=["Help"])

class ContactForm(BaseModel):
    subject: str
    message: str

@router.post("/contact")
async def submit_contact_form(
    contact: ContactForm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Submit a contact form message
    """
    try:
        if not contact.subject or not contact.message:
            raise HTTPException(status_code=400, detail="Subject and message are required")
        
        # Send email
        result = send_contact_email(
            user_email=current_user.email,
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

