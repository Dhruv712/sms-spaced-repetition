from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.flashcard import FlashcardCreate, FlashcardOut, FlashcardWithNextReviewOut
from app.models import Flashcard, CardReview
from app.database import get_db
from datetime import datetime, timedelta
from app.services.auth import get_current_active_user
from app.models import User
from sqlalchemy import func

router = APIRouter()

@router.post("/", response_model=FlashcardOut)
def create_flashcard(flashcard: FlashcardCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    new_card = Flashcard(
        user_id=current_user.id,
        concept=flashcard.concept,
        definition=flashcard.definition,
        tags=flashcard.tags,
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card

@router.get("/due", response_model=list[FlashcardOut])
def get_due_flashcards(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    now = datetime.utcnow()
    subquery = db.query(CardReview.flashcard_id).filter(
        CardReview.user_id == current_user.id,
        CardReview.next_review_date > now
    ).subquery()
    due_cards = db.query(Flashcard).filter(
        Flashcard.user_id == current_user.id,
        ~Flashcard.id.in_(subquery)
    ).all()
    return due_cards

@router.get("/with-reviews", response_model=list[FlashcardWithNextReviewOut])
def get_flashcards_with_next_review(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    cards = db.query(Flashcard).filter(Flashcard.user_id == current_user.id).all()
    result = []
    for card in cards:
        latest_review = db.query(CardReview).filter(
            CardReview.user_id == current_user.id,
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

@router.get("/", response_model=list[FlashcardOut])
def get_all_flashcards(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return db.query(Flashcard).filter(Flashcard.user_id == current_user.id).all()

