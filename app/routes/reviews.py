from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CardReview, Flashcard
from app.schemas.review import ReviewCreate, ReviewOut
from app.services.evaluator import evaluate_answer
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/", response_model=ReviewOut)
def submit_review(payload: ReviewCreate, db: Session = Depends(get_db)):
    flashcard = db.query(Flashcard).filter_by(id=payload.flashcard_id).first()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    eval_result = evaluate_answer(
        concept=flashcard.concept,
        correct_definition=flashcard.definition,
        user_response=payload.user_response
    )

    next_review = datetime.utcnow() + (
        timedelta(days=2) if eval_result["was_correct"] else timedelta(days=1)
    )

    review = CardReview(
        user_id=payload.user_id,
        flashcard_id=payload.flashcard_id,
        user_response=payload.user_response,
        was_correct=eval_result["was_correct"],
        confidence_score=eval_result["confidence_score"],
        llm_feedback=eval_result["llm_feedback"],
        next_review_date=next_review
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

@router.get("/{user_id}")
def get_reviews_for_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(CardReview).filter_by(user_id=user_id).order_by(CardReview.created_at.desc()).all()

from sqlalchemy import func, cast, Integer
from sqlalchemy.types import Boolean
@router.get("/stats/{user_id}")
def get_review_stats(user_id: int, db: Session = Depends(get_db)):
    stats = (
    db.query(
        func.count(CardReview.id).label("total"),
        func.sum(cast(CardReview.was_correct, Integer)).label("correct"),
        func.avg(CardReview.confidence_score).label("average_confidence"),
    )
    .filter(CardReview.user_id == user_id)
    .first()
    )

    return {
        "total": stats.total or 0,
        "correct": int(stats.correct or 0),
        "average_confidence": round(stats.average_confidence or 0, 2)
    }