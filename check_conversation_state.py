#!/usr/bin/env python3
"""
Check the current conversation state
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

def check_conversation_state():
    """Check the current conversation state"""
    
    try:
        from database import SessionLocal
        from models import User, ConversationState
        from datetime import datetime, timezone
        
        db = SessionLocal()
        
        # Find user
        user = db.query(User).filter_by(phone_number="+18054901242").first()
        if not user:
            print("❌ User not found")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Get conversation state
        state = db.query(ConversationState).filter_by(user_id=user.id).first()
        
        if state:
            print(f"\n🗣️ Conversation State:")
            print(f"   - User ID: {state.user_id}")
            print(f"   - Flashcard ID: {state.current_flashcard_id}")
            print(f"   - State: {state.state}")
            print(f"   - Last message at: {state.last_message_at}")
            
            # Check if state is recent
            now = datetime.now(timezone.utc)
            time_diff = now - state.last_message_at.replace(tzinfo=timezone.utc)
            print(f"   - Time since last message: {time_diff}")
            
            if state.state == "waiting_for_answer" and state.current_flashcard_id:
                print(f"   ✅ State is valid for processing responses")
            else:
                print(f"   ❌ State is not valid for processing responses")
        else:
            print(f"\n❌ No conversation state found!")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_conversation_state()
