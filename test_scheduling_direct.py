#!/usr/bin/env python3
"""
Test the scheduling system directly without Celery
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_scheduling_direct():
    """Test the scheduling system directly"""
    
    try:
        # Set the Railway database URL
        os.environ['DATABASE_URL'] = "postgresql://postgres:HKxMQCyIZjoNLhYHNuBGEtnqYUCSFFhW@postgres.railway.internal:5432/railway"
        
        from app.services.scheduler_service import send_due_flashcards_to_all_users
        
        print("🚀 Testing scheduling system directly...")
        
        # Call the function directly
        result = send_due_flashcards_to_all_users()
        
        print(f"✅ Scheduling result: {result}")
        
        # Check if any flashcards were sent
        if result.get('total_users', 0) > 0:
            print(f"📱 Processed {result['total_users']} users")
            for user_result in result.get('results', []):
                print(f"   User {user_result['user_id']}: {user_result['result']}")
        else:
            print("📭 No users found or no flashcards sent")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scheduling_direct()
