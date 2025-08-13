#!/usr/bin/env python3
"""
Simple database test to check if conversation state queries work
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_database_connection():
    """Test basic database connectivity"""
    
    print("🔧 Testing database connection...")
    
    # Import database components
    try:
        from app.database import SessionLocal
        from app.models import User, ConversationState
        print("✅ Database imports successful")
    except Exception as e:
        print(f"❌ Database import error: {e}")
        return
    
    # Test database session
    db = SessionLocal()
    try:
        print("🔧 Database session created")
        
        # Test a simple query
        print("🔍 Testing simple user query...")
        user_count = db.query(User).count()
        print(f"✅ User count query successful: {user_count} users")
        
        # Test conversation state query
        print("🔍 Testing conversation state query...")
        state_count = db.query(ConversationState).count()
        print(f"✅ Conversation state count query successful: {state_count} states")
        
        # Test specific user lookup
        print("🔍 Testing specific user lookup...")
        user = db.query(User).filter_by(phone_number="+18054901242").first()
        if user:
            print(f"✅ Found user: {user.email} (ID: {user.id})")
            
            # Test conversation state lookup for this user
            print(f"🔍 Testing conversation state lookup for user {user.id}...")
            state = db.query(ConversationState).filter_by(user_id=user.id).first()
            if state:
                print(f"✅ Found conversation state:")
                print(f"   - User ID: {state.user_id}")
                print(f"   - Flashcard ID: {state.current_flashcard_id}")
                print(f"   - State: {state.state}")
            else:
                print(f"✅ No conversation state found (this is expected)")
        else:
            print("❌ User not found")
            
    except Exception as e:
        print(f"❌ Database query error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("🔧 Database session closed")

if __name__ == "__main__":
    test_database_connection() 