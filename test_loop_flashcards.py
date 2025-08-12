import sys
import os
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.loop_message_service import send_due_flashcards_to_user, LoopMessageService

def test_loop_message_service():
    """Test the LoopMessage service directly"""
    try:
        service = LoopMessageService()
        print("✅ LoopMessage service initialized successfully")
        
        # Test phone number (replace with your actual number)
        test_phone = input("Enter your phone number for testing: ").strip()
        if not test_phone:
            print("❌ Phone number required")
            return
        
        # Test sending a simple message
        result = service.send_reminder(test_phone)
        if result.get("success"):
            print("✅ Test reminder sent successfully!")
        else:
            print(f"❌ Failed to send test reminder: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error testing LoopMessage service: {e}")

def test_send_flashcards_to_user():
    """Test sending flashcards to a specific user"""
    try:
        # Get database session
        db = next(get_db())
        
        # Get user ID from input
        user_id = input("Enter user ID to test with: ").strip()
        if not user_id:
            print("❌ User ID required")
            return
        
        user_id = int(user_id)
        
        # Test sending flashcards
        result = send_due_flashcards_to_user(user_id, db)
        
        print(f"\n📊 Test Results:")
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        
        if result.get('success'):
            if result.get('message') == 'flashcard_sent':
                print(f"Flashcard ID: {result.get('flashcard_id')}")
            print("✅ Test completed successfully!")
        else:
            print(f"❌ Test failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error testing flashcard sending: {e}")

def main():
    """Main test function"""
    print("🧪 Testing LoopMessage Flashcard Integration")
    print("=" * 50)
    
    print("\n1. Test LoopMessage service initialization and basic message sending")
    test_loop_message_service()
    
    print("\n" + "=" * 50)
    print("\n2. Test sending flashcards to a specific user")
    test_send_flashcards_to_user()
    
    print("\n" + "=" * 50)
    print("\n🎉 Testing complete!")

if __name__ == "__main__":
    main() 