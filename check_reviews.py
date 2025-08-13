#!/usr/bin/env python3
"""
Check the review status of flashcards
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

def check_reviews():
    """Check review status of flashcards"""
    
    try:
        from database import SessionLocal
        from models import User, Flashcard, CardReview
        from datetime import datetime
        
        db = SessionLocal()
        
        # Find user
        user = db.query(User).filter_by(phone_number="+18054901242").first()
        if not user:
            print("❌ User not found")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Get all flashcards for this user
        flashcards = db.query(Flashcard).filter_by(user_id=user.id).all()
        
        print(f"\n📚 Flashcards for user {user.id}:")
        for card in flashcards:
            print(f"   - ID: {card.id}, Concept: {card.concept}")
            
            # Get the latest review for this card
            latest_review = db.query(CardReview).filter_by(
                user_id=user.id, 
                flashcard_id=card.id
            ).order_by(CardReview.review_date.desc()).first()
            
            if latest_review:
                print(f"     📅 Last reviewed: {latest_review.review_date}")
                print(f"     📅 Next review: {latest_review.next_review_date}")
                print(f"     ✅ Correct: {latest_review.was_correct}")
                print(f"     🔢 Repetition count: {latest_review.repetition_count}")
                print(f"     📊 Ease factor: {latest_review.ease_factor}")
                print(f"     ⏰ Interval: {latest_review.interval_days} days")
                
                # Check if due
                from datetime import timezone
                now = datetime.now(timezone.utc)
                if latest_review.next_review_date <= now:
                    print(f"     🚨 DUE FOR REVIEW!")
                else:
                    print(f"     ✅ Not due yet")
            else:
                print(f"     📝 Never reviewed")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_reviews()
