#!/usr/bin/env python3
"""
Test script to verify conversation state can be saved and retrieved
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from database import SessionLocal
from models import ConversationState, User
from services.session_manager import set_conversation_state

load_dotenv()

def test_conversation_state():
    """Test saving and retrieving conversation state"""
    
    db = SessionLocal()
    
    try:
        # Find user
        user = db.query(User).filter_by(phone_number="+18054901242").first()
        if not user:
            print("❌ User not found")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Set conversation state
        print(f"🔧 Setting conversation state...")
        set_conversation_state(user.id, 4, db)
        print(f"✅ Conversation state set")
        
        # Immediately try to retrieve it
        print(f"🔍 Retrieving conversation state...")
        state = db.query(ConversationState).filter_by(user_id=user.id).first()
        
        if state:
            print(f"✅ Found conversation state:")
            print(f"   - User ID: {state.user_id}")
            print(f"   - Flashcard ID: {state.current_flashcard_id}")
            print(f"   - State: {state.state}")
        else:
            print(f"❌ No conversation state found!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_conversation_state() 