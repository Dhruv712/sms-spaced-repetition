from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.flashcard import FlashcardCreate, FlashcardOut, FlashcardWithNextReviewOut
from app.models import Flashcard, CardReview
from app.database import get_db
from datetime import datetime, timedelta
from app.services.auth import get_current_active_user
from app.models import User
from sqlalchemy import func
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter()

class DeckAssignment(BaseModel):
    deck_id: Optional[int] = None

@router.post("/", response_model=FlashcardOut)
def create_flashcard(flashcard: FlashcardCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    new_card = Flashcard(
        user_id=current_user.id,
        concept=flashcard.concept,
        definition=flashcard.definition,
        tags=', '.join(flashcard.tags) if flashcard.tags else None,
        deck_id=flashcard.deck_id,
        source_url=flashcard.source_url
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card

@router.get("/due", response_model=list[FlashcardOut])
def get_due_flashcards(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user), deck_id: Optional[int] = None):
    now = datetime.utcnow()
    
    query = db.query(Flashcard).filter(Flashcard.user_id == current_user.id)
    if deck_id is not None:
        query = query.filter(Flashcard.deck_id == deck_id)

    subquery = db.query(CardReview.flashcard_id).filter(
        CardReview.user_id == current_user.id,
        CardReview.next_review_date > now
    ).subquery()
    
    due_cards = query.filter(
        ~Flashcard.id.in_(subquery)
    ).all()
    return due_cards

@router.get("/with-reviews", response_model=list[FlashcardWithNextReviewOut])
def get_flashcards_with_next_review(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user), deck_id: Optional[int] = None, tags: Optional[str] = None):
    query = db.query(Flashcard).filter(Flashcard.user_id == current_user.id)
    if deck_id is not None:
        query = query.filter(Flashcard.deck_id == deck_id)

    if tags is not None:
        query = query.filter(Flashcard.tags.ilike(f"%{tags}%"))

    cards = query.all()
    result = []
    for card in cards:
        latest_review = db.query(CardReview).filter(
            CardReview.user_id == current_user.id,
            CardReview.flashcard_id == card.id
        ).order_by(CardReview.created_at.desc()).first()
        # Ensure tags are a list of strings
        if isinstance(card.tags, str):
            parsed_tags = [tag.strip() for tag in card.tags.split(',') if tag.strip()]
        else:
            parsed_tags = card.tags if card.tags is not None else []

        result.append({
            "id": card.id,
            "concept": card.concept,
            "definition": card.definition,
            "tags": parsed_tags,
            "next_review_date": latest_review.next_review_date if latest_review else None,
            "deck_id": card.deck_id
        })
    return result

@router.get("/", response_model=list[FlashcardOut])
def get_all_flashcards(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user), deck_id: Optional[int] = None):
    query = db.query(Flashcard).filter(Flashcard.user_id == current_user.id)
    if deck_id is not None:
        query = query.filter(Flashcard.deck_id == deck_id)
    return query.all()

@router.get("/{card_id}", response_model=FlashcardOut)
def get_flashcard(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    card = db.query(Flashcard).filter_by(id=card_id, user_id=current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found or not authorized")
    return card

@router.get("/decks/{deck_id}/all-flashcards", response_model=List[FlashcardOut])
def get_all_flashcards_in_deck(deck_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    cards = db.query(Flashcard).filter(Flashcard.user_id == current_user.id, Flashcard.deck_id == deck_id).all()
    return cards

@router.put("/{card_id}", response_model=FlashcardOut)
def update_flashcard(
    card_id: int, 
    flashcard_update: FlashcardCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    card = db.query(Flashcard).filter_by(id=card_id, user_id=current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found or not authorized")
    
    card.concept = flashcard_update.concept
    card.definition = flashcard_update.definition
    # Convert tags array to comma-separated string for database storage
    card.tags = ', '.join(flashcard_update.tags) if flashcard_update.tags else None
    card.deck_id = flashcard_update.deck_id
    card.source_url = flashcard_update.source_url
    
    db.commit()
    db.refresh(card)
    return card

@router.delete("/{card_id}")
def delete_flashcard(card_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    card = db.query(Flashcard).filter_by(id=card_id, user_id=current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found or not authorized")
    db.delete(card)
    db.commit()
    return {"detail": "Flashcard deleted"}

@router.post("/{card_id}/mark-reviewed")
def mark_flashcard_reviewed(card_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    card = db.query(Flashcard).filter_by(id=card_id, user_id=current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found or not authorized")
    review = CardReview(
        user_id=current_user.id,
        flashcard_id=card_id,
        user_response="[manual override]",
        was_correct=True,
        confidence_score=1.0,
        llm_feedback="Marked as reviewed manually.",
        next_review_date=datetime.utcnow() + timedelta(days=7)
    )
    db.add(review)
    db.commit()
    return {"detail": "Card marked as reviewed."}

@router.patch("/{card_id}/assign-deck")
def assign_flashcard_to_deck(
    card_id: int,
    deck_assignment: DeckAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    card = db.query(Flashcard).filter_by(id=card_id, user_id=current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found or not authorized")
    
    if deck_assignment.deck_id is not None:
        # Verify the deck belongs to the user
        from app.models import Deck
        deck = db.query(Deck).filter_by(id=deck_assignment.deck_id, user_id=current_user.id).first()
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found or not authorized")
    
    card.deck_id = deck_assignment.deck_id
    db.commit()
    db.refresh(card)
    return {"detail": "Flashcard assigned to deck successfully"}

