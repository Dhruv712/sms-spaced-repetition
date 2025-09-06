#!/usr/bin/env python3
"""
Delete a user and all their associated data
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def delete_user():
    """Delete user with email waterfire712@gmail.com"""
    
    try:
        # Set the Railway database URL
        os.environ['DATABASE_URL'] = "postgresql://postgres:HKxMQCyIZjoNLhYHNuBGEtnqYUCSFFhW@postgres.railway.internal:5432/railway"
        
        from database import SessionLocal
        from models import User, Flashcard, CardReview, ConversationState
        
        db = SessionLocal()
        
        # Find the user
        user = db.query(User).filter_by(email="waterfire712@gmail.com").first()
        
        if not user:
            print("❌ User not found")
            return
        
        print(f"👤 Found user: {user.email} (ID: {user.id})")
        print(f"📱 Phone: {user.phone_number}")
        
        # Count associated data
        flashcard_count = db.query(Flashcard).filter_by(user_id=user.id).count()
        review_count = db.query(CardReview).filter_by(user_id=user.id).count()
        conversation_count = db.query(ConversationState).filter_by(user_id=user.id).count()
        
        print(f"📊 Associated data:")
        print(f"   - Flashcards: {flashcard_count}")
        print(f"   - Reviews: {review_count}")
        print(f"   - Conversation states: {conversation_count}")
        
        # Confirm deletion
        confirm = input(f"\n⚠️ Are you sure you want to delete user {user.email} and all their data? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("❌ Deletion cancelled")
            return
        
        # Delete associated data first (foreign key constraints)
        print("🗑️ Deleting conversation states...")
        db.query(ConversationState).filter_by(user_id=user.id).delete()
        
        print("🗑️ Deleting card reviews...")
        db.query(CardReview).filter_by(user_id=user.id).delete()
        
        print("🗑️ Deleting flashcards...")
        db.query(Flashcard).filter_by(user_id=user.id).delete()
        
        print("🗑️ Deleting user...")
        db.delete(user)
        
        # Commit the changes
        db.commit()
        
        print("✅ User and all associated data deleted successfully!")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    delete_user()
