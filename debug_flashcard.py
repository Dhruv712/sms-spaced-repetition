from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Flashcard, User
from app.services.evaluator import evaluate_answer

def debug_flashcard():
    """Debug the flashcard and LLM evaluation"""
    
    db = next(get_db())
    
    # Get flashcard ID 4 (the one that was sent)
    flashcard = db.query(Flashcard).filter_by(id=4).first()
    
    if flashcard:
        print(f"📋 Flashcard ID 4:")
        print(f"   Concept: {flashcard.concept}")
        print(f"   Definition: {flashcard.definition}")
        print(f"   User ID: {flashcard.user_id}")
        print(f"   Tags: {flashcard.tags}")
        
        # Test LLM evaluation
        print(f"\n🧪 Testing LLM evaluation...")
        test_responses = [
            "A programming language",
            "I don't know",
            "Python is a programming language"
        ]
        
        for response in test_responses:
            print(f"\n📝 Testing response: '{response}'")
            try:
                result = evaluate_answer(
                    concept=flashcard.concept,
                    correct_definition=flashcard.definition,
                    user_response=response
                )
                print(f"✅ LLM Result: {result}")
            except Exception as e:
                print(f"❌ LLM Error: {e}")
                import traceback
                traceback.print_exc()
    else:
        print("❌ Flashcard ID 4 not found")

if __name__ == "__main__":
    debug_flashcard() 