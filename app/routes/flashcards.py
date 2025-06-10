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

from fastapi import HTTPException

@router.delete("/{card_id}")
def delete_flashcard(card_id: int, db: Session = Depends(get_db)):
    card = db.query(Flashcard).filter_by(id=card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    db.delete(card)
    db.commit()
    return {"detail": "Flashcard deleted"}

