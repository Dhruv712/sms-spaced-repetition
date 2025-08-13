#!/usr/bin/env python3
"""
Local debug script to simulate webhook processing without passthrough
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from database import SessionLocal
from models import User, ConversationState
from services.loop_message_service import LoopMessageService

load_dotenv()

def simulate_webhook_without_passthrough():
    """Simulate webhook processing without passthrough data"""
    
    print("🔧 Starting webhook simulation without passthrough...")
    
    # Simulate the webhook data
    webhook_data = {
        "alert_type": "message_inbound",
        "text": "The molecule that encodes genetic information",
        "message_id": "test-no-passthrough-123",
        "sandbox": True
    }
    
    print(f"📥 Simulated webhook data: {webhook_data}")
    
    # Step 1: Extract phone number (simulating handle_inbound_message)
    recipient = "+18054901242"  # Hardcoded for testing
    print(f"📱 Extracted recipient: {recipient}")
    
    # Step 2: Find user
    db = SessionLocal()
    try:
        print(f"🔍 Looking up user by phone: {recipient}")
        user = db.query(User).filter_by(phone_number=recipient).first()
        
        if not user:
            print("❌ User not found!")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Step 3: Process message (simulating process_user_message)
        body = webhook_data["text"]
        passthrough = None  # No passthrough data
        
        print(f"🔍 Processing message: passthrough='{passthrough}', body='{body}'")
        
        # Step 4: Try to initialize LoopMessage service
        print(f"🔧 Initializing LoopMessage service...")
        try:
            service = LoopMessageService()
            print(f"✅ LoopMessage service initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize LoopMessage service: {e}")
            service = None
        
        # Step 5: Check for passthrough (should be None)
        if passthrough and passthrough.startswith("flashcard_id:"):
            print(f"📎 Found flashcard_id in passthrough: {passthrough}")
            # This shouldn't happen in our test
        else:
            print(f"📎 No flashcard_id in passthrough")
        
        # Step 6: Look up conversation state (THIS IS WHERE IT HANGS!)
        print(f"🗣️ Looking up conversation state for user {user.id}...")
        try:
            state = db.query(ConversationState).filter_by(user_id=user.id).first()
            print(f"🗣️ Conversation state lookup completed!")
            
            if state:
                print(f"🗣️ Found conversation state:")
                print(f"   - User ID: {state.user_id}")
                print(f"   - Flashcard ID: {state.current_flashcard_id}")
                print(f"   - State: {state.state}")
            else:
                print(f"🗣️ No conversation state found")
                
        except Exception as e:
            print(f"❌ Error looking up conversation state: {e}")
            import traceback
            traceback.print_exc()
        
        # Step 7: Continue with the rest of the logic
        if state and state.state == "waiting_for_answer":
            print(f"⏳ User is waiting for answer, flashcard_id: {state.current_flashcard_id}")
        else:
            print(f"❓ Unknown message, would send default response")
            
    except Exception as e:
        print(f"❌ Error in webhook simulation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("🔧 Database session closed")

if __name__ == "__main__":
    simulate_webhook_without_passthrough() 