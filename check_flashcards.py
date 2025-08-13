#!/usr/bin/env python3
"""
Check what flashcard IDs exist in the database
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

def check_flashcards():
    """Check what flashcards exist"""
    
    try:
        from database import SessionLocal
        from models import Flashcard, User
        
        db = SessionLocal()
        
        # Find user
        user = db.query(User).filter_by(phone_number="+18054901242").first()
        if not user:
            print("❌ User not found")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Get all flashcards for this user
        flashcards = db.query(Flashcard).filter_by(user_id=user.id).all()
        
        if flashcards:
            print(f"📚 Found {len(flashcards)} flashcards:")
            for card in flashcards:
                print(f"   - ID: {card.id}, Concept: {card.concept}")
        else:
            print("❌ No flashcards found for this user")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_flashcards()
