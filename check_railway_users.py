#!/usr/bin/env python3
"""
Check users in the Railway database
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_railway_users():
    """Check users in the Railway database"""
    
    try:
        # Set the Railway database URL
        os.environ['DATABASE_URL'] = "postgresql://postgres:HKxMQCyIZjoNLhYHNuBGEtnqYUCSFFhW@postgres.railway.internal:5432/railway"
        
        from database import SessionLocal
        from models import User, Flashcard
        
        db = SessionLocal()
        
        # Get all users
        users = db.query(User).all()
        
        print(f"🚂 Railway Database - Found {len(users)} total users:")
        
        for i, user in enumerate(users, 1):
            print(f"\n👤 User {i}:")
            print(f"   - ID: {user.id}")
            print(f"   - Email: {user.email}")
            print(f"   - Phone: {user.phone_number}")
            print(f"   - SMS Opt-in: {user.sms_opt_in}")
            print(f"   - Active: {user.is_active}")
            
            # Get flashcards for this user
            flashcards = db.query(Flashcard).filter_by(user_id=user.id).all()
            print(f"   - Flashcards: {len(flashcards)}")
            for card in flashcards:
                print(f"     * ID: {card.id}, Concept: {card.concept}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_railway_users()
