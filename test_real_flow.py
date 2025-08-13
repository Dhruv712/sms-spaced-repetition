#!/usr/bin/env python3
"""
Test the real flow with proper conversation state setup
"""

import os
import sys
import requests
import json
import time
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

def setup_conversation_state():
    """Set up conversation state for testing"""
    
    print("🔧 Setting up conversation state...")
    
    try:
        from database import SessionLocal
        from models import User, Flashcard
        from services.session_manager import set_conversation_state
        
        db = SessionLocal()
        
        # Find user
        user = db.query(User).filter_by(phone_number="+18054901242").first()
        if not user:
            print("❌ User not found")
            return False
        
        # Find flashcard
        flashcard = db.query(Flashcard).filter_by(id=4).first()
        if not flashcard:
            print("❌ Flashcard not found")
            return False
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        print(f"✅ Found flashcard: {flashcard.concept} (ID: {flashcard.id})")
        
        # Set conversation state
        set_conversation_state(user.id, flashcard.id, db)
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up conversation state: {e}")
        import traceback
        traceback.print_exc()
        return False

def send_flashcard_with_state():
    """Send flashcard after setting up conversation state"""
    
    print("📤 Sending flashcard with conversation state...")
    
    # Check environment variables
    auth_key = os.getenv("LOOPMESSAGE_AUTH_KEY")
    secret_key = os.getenv("LOOPMESSAGE_SECRET_KEY")
    sender_name = os.getenv("LOOPMESSAGE_SENDER_NAME")
    
    if not all([auth_key, secret_key, sender_name]):
        print("❌ Missing required environment variables!")
        return None
    
    # API endpoint
    url = "https://server.loopmessage.com/api/v1/message/send/"
    
    # Headers
    headers = {
        "Authorization": auth_key,
        "Loop-Secret-Key": secret_key,
        "Content-Type": "application/json"
    }
    
    # Payload with passthrough data
    payload = {
        "recipient": "+18054901242",
        "text": "What is DNA?",
        "sender_name": sender_name,
        "passthrough": "flashcard_id:4"
    }
    
    print(f"📤 Sending flashcard with passthrough: {payload['passthrough']}")
    print(f"📱 Recipient: {payload['recipient']}")
    print(f"📝 Message: {payload['text']}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Flashcard sent successfully!")
                print(f"Message ID: {result.get('message_id')}")
                return result.get('message_id')
            else:
                print("❌ Failed to send flashcard")
                print(f"Error: {result.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def main():
    """Main function"""
    
    print("🧪 Testing real flow with conversation state...")
    print("=" * 50)
    
    # Step 1: Set up conversation state
    if not setup_conversation_state():
        print("❌ Failed to set up conversation state")
        return
    
    # Step 2: Send flashcard
    message_id = send_flashcard_with_state()
    
    if message_id:
        print(f"\n✅ Flashcard sent with ID: {message_id}")
        print("📱 Check your phone for the flashcard message")
        print("\n🎯 Now respond to the flashcard via text!")
        print("The conversation state is set up, so your response should be processed correctly.")
    else:
        print("❌ Failed to send flashcard")

if __name__ == "__main__":
    main()
