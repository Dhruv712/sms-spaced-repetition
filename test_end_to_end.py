import requests
import json
import time
from app.services.loop_message_service import LoopMessageService
from sqlalchemy.orm import Session
from app.database import get_db

def test_end_to_end_communication():
    """Test the complete end-to-end communication flow"""
    
    print("🚀 Testing End-to-End LoopMessage Communication")
    print("=" * 60)
    
    # Step 1: Send a flashcard to the user
    print("\n📤 Step 1: Sending flashcard to user...")
    try:
        db = next(get_db())
        service = LoopMessageService()
        
        # Send flashcard to user ID 1 (your test user)
        result = send_due_flashcards_to_user(1, db)
        
        if result.get("success"):
            if result.get("message") == "flashcard_sent":
                flashcard_id = result.get("flashcard_id")
                print(f"✅ Flashcard sent! ID: {flashcard_id}")
                print("📱 Check your phone for the flashcard question")
                
                # Step 2: Simulate user response
                print(f"\n📥 Step 2: Simulating user response...")
                simulate_user_response(flashcard_id)
                
            else:
                print(f"ℹ️ {result.get('message')}")
        else:
            print(f"❌ Failed to send flashcard: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error in end-to-end test: {e}")

def simulate_user_response(flashcard_id: int):
    """Simulate a user responding to a flashcard"""
    
    # Test different types of responses
    test_responses = [
        {
            "text": "A programming language",
            "description": "Good answer"
        },
        {
            "text": "I don't know",
            "description": "Incorrect answer"
        }
    ]
    
    for i, response in enumerate(test_responses, 1):
        print(f"\n🧪 Test Response {i}: '{response['text']}' ({response['description']})")
        
        # Create webhook payload simulating user response
        webhook_payload = {
            "type": "message_inbound",
            "message": {
                "from": "+18054901242",
                "text": response["text"],
                "passthrough": f"flashcard_id:{flashcard_id}",
                "message_id": f"test-response-{i}"
            }
        }
        
        # Send to Railway webhook
        railway_url = "https://sms-spaced-repetition-production.up.railway.app/loop-webhook/webhook"
        
        try:
            webhook_response = requests.post(
                railway_url,
                json=webhook_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"📊 Webhook Response: {webhook_response.status_code}")
            print(f"📄 Response: {webhook_response.text}")
            
            if webhook_response.status_code == 200:
                print("✅ Response processed successfully!")
                print("📱 Check your phone for LLM feedback")
            else:
                print("❌ Failed to process response")
                
        except Exception as e:
            print(f"❌ Error sending webhook: {e}")
        
        # Wait a bit between tests
        if i < len(test_responses):
            print("⏳ Waiting 3 seconds before next test...")
            time.sleep(3)

def send_due_flashcards_to_user(user_id: int, db: Session):
    """Send due flashcards to a specific user"""
    from app.models import User
    from app.services.session_manager import get_next_due_flashcard
    
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}
    
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

if __name__ == "__main__":
    test_end_to_end_communication() 