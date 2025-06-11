from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, cast, Integer
from app.database import get_db
from app.models import CardReview, Flashcard, User
from app.schemas.review import ManualReviewSchema, ReviewOut
from app.services.evaluator import evaluate_answer
from app.services.scheduler import compute_next_review
from app.dependencies.auth import get_current_active_user
import datetime

router = APIRouter()


@router.post("/manual_review", response_model=ReviewOut)
def manual_review(
    data: ManualReviewSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    card = db.query(Flashcard).filter(
        Flashcard.id == data.flashcard_id,
        Flashcard.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    result = evaluate_answer(
        concept=card.concept,
        correct_definition=card.definition,
        user_response=data.answer
    )

    next_review = compute_next_review(
        last_review_date=datetime.datetime.now(datetime.UTC),
        was_correct=result["was_correct"],
        confidence_score=result["confidence_score"],
        start_hour=current_user.preferred_start_hour,
        end_hour=current_user.preferred_end_hour,
        timezone_str=current_user.timezone
    )

    review = CardReview(
        user_id=current_user.id,
        flashcard_id=card.id,
        user_response=data.answer,
        was_correct=result["was_correct"],
        confidence_score=result["confidence_score"],
        llm_feedback=result["llm_feedback"],
        next_review_date=next_review
    )

    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/", response_model=list[ReviewOut])
def get_reviews_for_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return (
        db.query(CardReview)
        .options(joinedload(CardReview.flashcard))
        .filter_by(user_id=current_user.id)
        .order_by(CardReview.created_at.desc())
        .all()
    )


@router.get("/stats")
def get_review_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    stats = (
        db.query(
            func.count(CardReview.id).label("total"),
            func.sum(cast(CardReview.was_correct, Integer)).label("correct"),
            func.avg(CardReview.confidence_score).label("average_confidence")
        )
        .filter(CardReview.user_id == current_user.id)
        .first()
    )

    return {
        "total": stats.total or 0,
        "correct": int(stats.correct or 0),
        "average_confidence": round(stats.average_confidence or 0, 2)
    }
