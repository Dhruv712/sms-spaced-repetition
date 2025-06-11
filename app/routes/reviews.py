from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, cast, Integer
from app.database import get_db
from app.models import CardReview, Flashcard, User
from app.schemas.review import ReviewCreate, ReviewOut, ManualReviewSchema
from app.services.evaluator import evaluate_answer
from app.services.scheduler import compute_next_review
import datetime

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

    next_review = datetime.datetime.now(datetime.UTC) + (
        datetime.timedelta(days=2) if eval_result["was_correct"] else datetime.timedelta(days=1)
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
    return (
        db.query(CardReview)
        .options(joinedload(CardReview.flashcard))  # Eager load flashcard
        .filter_by(user_id=user_id)
        .order_by(CardReview.created_at.desc())
        .all()
    )


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


@router.post("/manual_review")
def manual_review(data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data["user_id"]).first()
    card = db.query(Flashcard).filter(Flashcard.id == data["flashcard_id"]).first()

    if not user or not card:
        raise HTTPException(status_code=404, detail="User or flashcard not found")

    result = evaluate_answer(
        concept=card.concept,
        correct_definition=card.definition,
        user_response=data["answer"]
    )

    next_review = compute_next_review(
        last_review_date=datetime.datetime.now(datetime.UTC),
        was_correct=result["was_correct"],
        confidence_score=result["confidence_score"],
        start_hour=user.preferred_start_hour,
        end_hour=user.preferred_end_hour,
        timezone_str=user.timezone
    )

    review = CardReview(
        user_id=user.id,
        flashcard_id=card.id,
        user_response=data["answer"],
        was_correct=result["was_correct"],
        confidence_score=result["confidence_score"],
        llm_feedback=result["llm_feedback"],
        next_review_date=next_review
    )

    db.add(review)
    db.commit()
    return {"llm_feedback": result["llm_feedback"]}
