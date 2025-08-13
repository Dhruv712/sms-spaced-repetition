#!/usr/bin/env python3
"""
Test script to verify conversation state flow and passthrough functionality
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from database import SessionLocal
from models import User, Flashcard, ConversationState
from services.session_manager import set_conversation_state, get_next_due_flashcard
from services.loop_message_service import send_due_flashcards_to_user

load_dotenv()

def test_conversation_flow():
    """Test the complete conversation flow"""
    
    print("🧪 Testing conversation flow...")
    
    db = SessionLocal()
    
    try:
        # Find user
        user = db.query(User).filter_by(phone_number="+18054901242").first()
        if not user:
            print("❌ User not found")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Check current conversation state
        print(f"🔍 Checking current conversation state...")
        current_state = db.query(ConversationState).filter_by(user_id=user.id).first()
        if current_state:
            print(f"Current state: user_id={current_state.user_id}, flashcard_id={current_state.current_flashcard_id}, state={current_state.state}")
        else:
            print("No current conversation state")
        
        # Get next due flashcard
        print(f"🔍 Getting next due flashcard...")
        due_card = get_next_due_flashcard(user.id, db)
        if due_card:
            print(f"✅ Found due flashcard: {due_card.concept} (ID: {due_card.id})")
        else:
            print("❌ No due flashcards found")
            return
        
        # Test setting conversation state
        print(f"🔧 Testing set_conversation_state...")
        set_conversation_state(user.id, due_card.id, db)
        
        # Verify state was set
        print(f"🔍 Verifying conversation state...")
        state = db.query(ConversationState).filter_by(user_id=user.id).first()
        if state:
            print(f"✅ State verified: user_id={state.user_id}, flashcard_id={state.current_flashcard_id}, state={state.state}")
        else:
            print("❌ State not found after setting!")
        
        # Test sending flashcard
        print(f"📤 Testing send_due_flashcards_to_user...")
        result = send_due_flashcards_to_user(user.id, db)
        print(f"Send result: {result}")
        
        # Check state after sending
        print(f"🔍 Checking state after sending...")
        state_after = db.query(ConversationState).filter_by(user_id=user.id).first()
        if state_after:
            print(f"✅ State after sending: user_id={state_after.user_id}, flashcard_id={state_after.current_flashcard_id}, state={state_after.state}")
        else:
            print("❌ No state found after sending!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_conversation_flow()
