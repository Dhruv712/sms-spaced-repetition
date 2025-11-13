from sqlalchemy.orm import Session
from app.models import ConversationState, Flashcard, CardReview, UserDeckSmsSettings
from datetime import datetime, timezone
from sqlalchemy import and_, or_

def get_next_due_flashcard(user_id: int, db: Session) -> Flashcard | None:
    """
    Get next due flashcard with priority scoring:
    1. Deck-first approach: Complete all cards from one deck before moving to another
    2. Overdue cards get higher priority
    3. Never-reviewed cards get priority
    4. Avoid sending the same card that was just sent without response
    """
    now = datetime.now(timezone.utc)
    
    # Get deck IDs that are enabled for SMS for this user
    enabled_deck_ids_result = db.query(UserDeckSmsSettings.deck_id).filter(
        UserDeckSmsSettings.user_id == user_id,
        UserDeckSmsSettings.sms_enabled == True
    ).all()
    enabled_deck_ids = [row[0] for row in enabled_deck_ids_result] if enabled_deck_ids_result else []
    
    # Get cards that are due (next_review_date <= now or no review exists)
    subquery = db.query(CardReview.flashcard_id).filter(
        CardReview.user_id == user_id,
        CardReview.next_review_date > now
    ).subquery()

    # Base query: cards that are due
    base_query = db.query(Flashcard).filter(
        Flashcard.user_id == user_id,
        ~Flashcard.id.in_(subquery)
    )
    
    # Apply deck filtering: include cards without decks OR cards from enabled decks
    if enabled_deck_ids:
        base_query = base_query.filter(
            or_(
                Flashcard.deck_id.is_(None),  # Cards without a deck are always included
                Flashcard.deck_id.in_(enabled_deck_ids)  # Cards from enabled decks
            )
        )
    else:
        # If no decks are enabled, only include cards without decks
        base_query = base_query.filter(Flashcard.deck_id.is_(None))
    
    # Get conversation state to avoid resending the same card
    state = db.query(ConversationState).filter_by(user_id=user_id).first()
    last_sent_id = state.last_sent_flashcard_id if state else None
    
    # Exclude the last sent card if it hasn't been answered yet
    if last_sent_id and state and state.state == "waiting_for_answer":
        base_query = base_query.filter(Flashcard.id != last_sent_id)
    
    # Get all due cards
    all_due_cards = base_query.all()
    
    if not all_due_cards:
        return None
    
    # Priority scoring: Group by deck and prioritize deck-first
    # Strategy: Find the deck with the most due cards, complete all cards from that deck first
    
    # Group cards by deck_id (None for cards without decks)
    deck_groups = {}
    for card in all_due_cards:
        deck_id = card.deck_id if card.deck_id else -1  # Use -1 for cards without decks
        if deck_id not in deck_groups:
            deck_groups[deck_id] = []
        deck_groups[deck_id].append(card)
    
    # Find the deck with the most due cards (deck-first approach)
    if deck_groups:
        # Sort decks by number of due cards (descending), then pick the first
        sorted_decks = sorted(deck_groups.items(), key=lambda x: len(x[1]), reverse=True)
        selected_deck_id, cards_in_deck = sorted_decks[0]
        
        # Now prioritize within this deck:
        # 1. Never-reviewed cards first
        # 2. Then overdue cards (cards past their next_review_date)
        # 3. Then by how overdue they are
        
        never_reviewed = []
        overdue_cards = []
        due_cards = []
        
        for card in cards_in_deck:
            # Check if card has been reviewed
            latest_review = db.query(CardReview).filter_by(
                user_id=user_id,
                flashcard_id=card.id
            ).order_by(CardReview.review_date.desc()).first()
            
            if not latest_review:
                # Never reviewed - highest priority
                never_reviewed.append(card)
            else:
                # Check if overdue
                if latest_review.next_review_date < now:
                    # Calculate how overdue (in hours)
                    overdue_hours = (now - latest_review.next_review_date).total_seconds() / 3600
                    overdue_cards.append((overdue_hours, card))
                else:
                    # Due but not overdue
                    due_cards.append(card)
        
        # Sort overdue cards by how overdue they are (most overdue first)
        overdue_cards.sort(key=lambda x: x[0], reverse=True)
        
        # Priority order: never reviewed > most overdue > due
        if never_reviewed:
            return never_reviewed[0]
        elif overdue_cards:
            return overdue_cards[0][1]
        elif due_cards:
            return due_cards[0]
        else:
            # Fallback to first card in deck
            return cards_in_deck[0]
    
    # Fallback: return first due card
    return all_due_cards[0]

def set_conversation_state(user_id: int, flashcard_id: int, db: Session, increment_message_count: bool = True):
    print(f"🔧 set_conversation_state called: user_id={user_id}, flashcard_id={flashcard_id}")
    
    try:
        state = db.query(ConversationState).filter_by(user_id=user_id).first()

        if not state:
            print(f"📝 Creating new conversation state for user {user_id}")
            state = ConversationState(user_id=user_id, message_count=0)
        else:
            print(f"📝 Updating existing conversation state for user {user_id}")

        state.current_flashcard_id = flashcard_id
        state.last_sent_flashcard_id = flashcard_id
        state.state = "waiting_for_answer"
        state.last_message_at = datetime.now(timezone.utc)
        
        if increment_message_count:
            state.message_count = (state.message_count or 0) + 1

        print(f"💾 Saving conversation state: user_id={user_id}, flashcard_id={flashcard_id}, state=waiting_for_answer, message_count={state.message_count}")

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
