from sqlalchemy.orm import Session
from app.models import ConversationState, Flashcard, CardReview, UserDeckSmsSettings
from datetime import datetime, timezone
from sqlalchemy import and_, or_

def get_next_due_flashcard(user_id: int, db: Session) -> Flashcard | None:
    now = datetime.now(timezone.utc)
    
    # Get deck IDs that are enabled for SMS for this user
    enabled_deck_ids_result = db.query(UserDeckSmsSettings.deck_id).filter(
        UserDeckSmsSettings.user_id == user_id,
        UserDeckSmsSettings.sms_enabled == True
    ).all()
    enabled_deck_ids = [row[0] for row in enabled_deck_ids_result] if enabled_deck_ids_result else []
    
    subquery = db.query(CardReview.flashcard_id).filter(
        CardReview.user_id == user_id,
        CardReview.next_review_date > now
    ).subquery()

    # Filter: only include cards that are:
    # 1. Not in a deck (deck_id is None) - always include these
    # 2. In a deck that is enabled for SMS (deck_id in enabled_deck_ids)
    query = db.query(Flashcard).filter(
        Flashcard.user_id == user_id,
        ~Flashcard.id.in_(subquery)
    )
    
    # Apply deck filtering: include cards without decks OR cards from enabled decks
    if enabled_deck_ids:
        query = query.filter(
            or_(
                Flashcard.deck_id.is_(None),  # Cards without a deck are always included
                Flashcard.deck_id.in_(enabled_deck_ids)  # Cards from enabled decks
            )
        )
    else:
        # If no decks are enabled, only include cards without decks
        query = query.filter(Flashcard.deck_id.is_(None))
    
    return query.first()

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
