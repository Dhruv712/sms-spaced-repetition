#!/usr/bin/env python3
"""
Script to manually run the scheduled flashcard sending
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

def run_scheduled_flashcards():
    """Run the scheduled flashcard sending"""
    
    print("🕐 Running scheduled flashcard sending...")
    
    try:
        from services.scheduler_service import send_due_flashcards_to_all_users, get_user_flashcard_stats
        
        # Get stats for your user (ID 1)
        print("\n📊 Your flashcard stats:")
        stats = get_user_flashcard_stats(1)
        print(f"   - Total flashcards: {stats['total_flashcards']}")
        print(f"   - Due flashcards: {stats['due_flashcards']}")
        print(f"   - Recent reviews (7 days): {stats['recent_reviews']}")
        
        # Send due flashcards
        print("\n📤 Sending due flashcards...")
        result = send_due_flashcards_to_all_users()
        
        print(f"\n✅ Scheduled sending completed!")
        print(f"📱 Processed {result['total_users']} users")
        
        for user_result in result['results']:
            user_id = user_result['user_id']
            phone = user_result['phone_number']
            result_data = user_result['result']
            
            if result_data.get('success'):
                message = result_data.get('message', 'Unknown')
                if message == 'flashcard_sent':
                    flashcard_id = result_data.get('flashcard_id')
                    concept = result_data.get('concept')
                    print(f"   ✅ User {user_id} ({phone}): Sent flashcard {flashcard_id} - '{concept}'")
                elif message == 'no_due_flashcards':
                    print(f"   📭 User {user_id} ({phone}): No due flashcards")
                else:
                    print(f"   ℹ️ User {user_id} ({phone}): {message}")
            else:
                error = result_data.get('error', 'Unknown error')
                print(f"   ❌ User {user_id} ({phone}): {error}")
        
    except Exception as e:
        print(f"❌ Error running scheduled flashcards: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_scheduled_flashcards()
