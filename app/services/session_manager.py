from sqlalchemy.orm import Session
from app.models import ConversationState, Flashcard, CardReview
from datetime import datetime, timezone
from sqlalchemy import and_

def get_next_due_flashcard(user_id: int, db: Session) -> Flashcard | None:
    now = datetime.now(timezone.utc)
    
    subquery = db.query(CardReview.flashcard_id).filter(
        CardReview.user_id == user_id,
        CardReview.next_review_date > now
    ).subquery()

    return db.query(Flashcard).filter(
        Flashcard.user_id == user_id,
        ~Flashcard.id.in_(subquery)
    ).first()

def set_conversation_state(user_id: int, flashcard_id: int, db: Session):
    print(f"🔧 set_conversation_state called: user_id={user_id}, flashcard_id={flashcard_id}")
    
    try:
        state = db.query(ConversationState).filter_by(user_id=user_id).first()

        if not state:
            print(f"📝 Creating new conversation state for user {user_id}")
            state = ConversationState(user_id=user_id)
        else:
            print(f"📝 Updating existing conversation state for user {user_id}")

        state.current_flashcard_id = flashcard_id
        state.state = "waiting_for_answer"
        state.last_message_at = datetime.now(timezone.utc)

        print(f"💾 Saving conversation state: user_id={user_id}, flashcard_id={flashcard_id}, state=waiting_for_answer")

        db.add(state)
        db.commit()
        
        print(f"✅ Conversation state saved successfully")
        
        # Verify the state was saved
        verification_state = db.query(ConversationState).filter_by(user_id=user_id).first()
        if verification_state:
            print(f"✅ Verification: State found - user_id={verification_state.user_id}, flashcard_id={verification_state.current_flashcard_id}, state={verification_state.state}")
        else:
            print(f"❌ Verification: No state found after saving!")
            
    except Exception as e:
        print(f"❌ Error in set_conversation_state: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
