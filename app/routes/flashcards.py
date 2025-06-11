from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.flashcard import FlashcardCreate, FlashcardOut
from app.models import Flashcard, CardReview
from app.database import get_db
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=FlashcardOut)
def create_flashcard(flashcard: FlashcardCreate, db: Session = Depends(get_db)):
    new_card = Flashcard(**flashcard.dict())
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card

@router.get("/due/{user_id}", response_model=list[FlashcardOut])
def get_due_flashcards(user_id: int, db: Session = Depends(get_db)):
    now = datetime.utcnow()

    # Very basic rule: due if no reviews or next_review_date <= now
    subquery = db.query(CardReview.flashcard_id).filter(
        CardReview.user_id == user_id,
        CardReview.next_review_date > now
    ).subquery()

    due_cards = db.query(Flashcard).filter(
        Flashcard.user_id == user_id,
        ~Flashcard.id.in_(subquery)
    ).all()

    return due_cards

from sqlalchemy import func
from app.schemas.flashcard import FlashcardWithNextReviewOut

@router.get("/with-reviews/{user_id}", response_model=list[FlashcardWithNextReviewOut])
def get_flashcards_with_next_review(user_id: int, db: Session = Depends(get_db)):
    cards = db.query(Flashcard).filter(Flashcard.user_id == user_id).all()

    result = []
    for card in cards:
        latest_review = db.query(CardReview).filter(
            CardReview.user_id == user_id,
            CardReview.flashcard_id == card.id
        ).order_by(CardReview.created_at.desc()).first()

        result.append({
            "id": card.id,
            "concept": card.concept,
            "definition": card.definition,
            "tags": card.tags,
            "next_review_date": latest_review.next_review_date if latest_review else None
        })

    return result


from fastapi import HTTPException

@router.delete("/{card_id}")
def delete_flashcard(card_id: int, db: Session = Depends(get_db)):
    card = db.query(Flashcard).filter_by(id=card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    db.delete(card)
    db.commit()
    return {"detail": "Flashcard deleted"}

from app.models import CardReview
from datetime import datetime, timedelta

@router.post("/{card_id}/mark-reviewed")
def mark_flashcard_reviewed(card_id: int, db: Session = Depends(get_db)):
    card = db.query(Flashcard).filter_by(id=card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    # Just pick the user_id from the card, or override if needed
    user_id = card.user_id

    review = CardReview(
        user_id=user_id,
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

