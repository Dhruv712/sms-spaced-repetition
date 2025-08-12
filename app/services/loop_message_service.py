import os
import requests
import json
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import User, Flashcard, CardReview
from app.services.session_manager import get_next_due_flashcard
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LoopMessageService:
    """Service for sending messages via LoopMessage API"""
    
    def __init__(self):
        self.base_url = "https://server.loopmessage.com/api/v1/message/send/"
        self.auth_key = os.getenv("LOOPMESSAGE_AUTH_KEY")
        self.secret_key = os.getenv("LOOPMESSAGE_SECRET_KEY")
        self.sender_name = os.getenv("LOOPMESSAGE_SENDER_NAME")
        
        if not all([self.auth_key, self.secret_key, self.sender_name]):
            raise ValueError("Missing required LoopMessage environment variables")
    
    def send_flashcard(self, phone_number: str, flashcard: Flashcard) -> Dict[str, Any]:
        """
        Send a flashcard question via LoopMessage
        
        Args:
            phone_number: Recipient's phone number
            flashcard: Flashcard object to send
            
        Returns:
            Dict containing API response
        """
        message_text = f"{flashcard.concept}?\n\n(Reply with your answer)"
        
        return self._send_message(
            recipient=phone_number,
            text=message_text,
            passthrough=f"flashcard_id:{flashcard.id}"
        )
    
    def send_reminder(self, phone_number: str) -> Dict[str, Any]:
        """
        Send a study reminder via LoopMessage
        
        Args:
            phone_number: Recipient's phone number
            
        Returns:
            Dict containing API response
        """
        message_text = "Hey! You've got flashcards to review. Reply 'Yes' to begin."
        
        return self._send_message(
            recipient=phone_number,
            text=message_text,
            passthrough="reminder"
        )
    
    def send_feedback(self, phone_number: str, feedback: str) -> Dict[str, Any]:
        """
        Send feedback after grading a flashcard response
        
        Args:
            phone_number: Recipient's phone number
            feedback: Feedback message to send
            
        Returns:
            Dict containing API response
        """
        return self._send_message(
            recipient=phone_number,
            text=feedback
        )
    
    def _send_message(
        self, 
        recipient: str, 
        text: str, 
        passthrough: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message via LoopMessage API
        
        Args:
            recipient: Phone number or email
            text: Message text
            passthrough: Optional metadata string
            
        Returns:
            Dict containing API response
        """
        headers = {
            "Authorization": self.auth_key,
            "Loop-Secret-Key": self.secret_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "recipient": recipient,
            "text": text,
            "sender_name": self.sender_name
        }
        
        if passthrough:
            payload["passthrough"] = passthrough
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ Message sent successfully to {recipient}")
                    print(f"Message ID: {result.get('message_id')}")
                else:
                    print(f"❌ Message failed to send to {recipient}")
                    print(f"Error: {result.get('message')}")
                
                return result
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return {"success": False, "error": str(e)}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            return {"success": False, "error": "Invalid JSON response"}

def send_due_flashcards_to_user(user_id: int, db: Session) -> Dict[str, Any]:
    """
    Send due flashcards to a specific user
    
    Args:
        user_id: User ID to send flashcards to
        db: Database session
        
    Returns:
        Dict containing results
    """
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}
    
    if not user.sms_opt_in:
        return {"success": False, "error": "User has not opted into SMS"}
    
    try:
        service = LoopMessageService()
        
        # Get next due flashcard
        due_card = get_next_due_flashcard(user_id, db)
        
        if not due_card:
            # No due cards, send reminder
            result = service.send_reminder(user.phone_number)
            return {
                "success": result.get("success", False),
                "message": "reminder_sent",
                "details": result
            }
        else:
            # Send the due flashcard
            result = service.send_flashcard(user.phone_number, due_card)
            return {
                "success": result.get("success", False),
                "message": "flashcard_sent",
                "flashcard_id": due_card.id,
                "details": result
            }
            
    except Exception as e:
        print(f"❌ Error sending flashcards to user {user_id}: {e}")
        return {"success": False, "error": str(e)}

def send_due_flashcards_to_all_users(db: Session) -> Dict[str, Any]:
    """
    Send due flashcards to all users who have opted into SMS
    
    Args:
        db: Database session
        
    Returns:
        Dict containing results for all users
    """
    users = db.query(User).filter_by(sms_opt_in=True, is_active=True).all()
    results = []
    
    for user in users:
        result = send_due_flashcards_to_user(user.id, db)
        results.append({
            "user_id": user.id,
            "phone_number": user.phone_number,
            "result": result
        })
    
    return {
        "total_users": len(users),
        "results": results
    } 