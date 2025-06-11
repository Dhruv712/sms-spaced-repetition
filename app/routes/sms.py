from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Flashcard, ConversationState, CardReview
from app.services.session_manager import get_next_due_flashcard, set_conversation_state
from app.services.evaluator import evaluate_answer
# from datetime import datetime, timedelta
import datetime

router = APIRouter()

def normalize_phone(number: str) -> str:
    number = number.strip()
    if not number.startswith("+") and number.isdigit():
        number = "+" + number
    return number

@router.post("/incoming", response_class=PlainTextResponse)
async def receive_sms(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    db: Session = Depends(get_db)
):
    phone = normalize_phone(From)
    body = Body.strip()

    user = db.query(User).filter_by(phone_number=phone).first()
    if not user:
        return _twiml_response("You're not registered. Visit our site to sign up.")

    state = db.query(ConversationState).filter_by(user_id=user.id).first()

    if state and state.state == "waiting_for_answer":
        card = db.query(Flashcard).filter_by(id=state.current_flashcard_id).first()
        if not card:
            return _twiml_response("Hmm, we lost track of your flashcard. Say 'Yes' to start again.")

        result = evaluate_answer(
            concept=card.concept,
            correct_definition=card.definition,
            user_response=body
        )

        from app.services.scheduler import compute_next_review
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
            user_response=body,
            was_correct=result["was_correct"],
            confidence_score=result["confidence_score"],
            llm_feedback=result["llm_feedback"],
            next_review_date=next_review
        )

        db.add(review)
        state.state = "idle"
        state.current_flashcard_id = None
        db.commit()

        return _twiml_response(result["llm_feedback"])

    elif "yes" in body.lower():
        card = get_next_due_flashcard(user.id, db)
        if not card:
            return _twiml_response("You're all caught up! No flashcards due right now.")

        set_conversation_state(user.id, card.id, db)
        return _twiml_response(f"{card.concept}?\n(Reply with your answer)")

    return _twiml_response("I didn't understand that. Reply 'Yes' to start a review session.")


def _twiml_response(message: str) -> PlainTextResponse:
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{message}</Message>
</Response>"""
    return PlainTextResponse(content=xml, media_type="application/xml")
