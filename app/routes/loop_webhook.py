from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Flashcard, ConversationState, CardReview
from app.services.session_manager import get_next_due_flashcard, set_conversation_state
from app.services.evaluator import evaluate_answer
from app.services.loop_message_service import LoopMessageService
import datetime
import json
from typing import Dict, Any

router = APIRouter()

def normalize_phone(number: str) -> str:
    """Normalize phone number format"""
    number = number.strip()
    if not number.startswith("+") and number.isdigit():
        number = "+" + number
    return number

@router.post("/webhook")
async def receive_loop_webhook(
    request: Request,
    db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Receive webhook callbacks from LoopMessage
    """
    try:
        # Parse the JSON body
        body = await request.json()
        print(f"📥 Received LoopMessage webhook: {json.dumps(body, indent=2)}")
        
        # Extract webhook data - LoopMessage uses "alert_type" not "type"
        webhook_type = body.get("alert_type")
        
        if webhook_type == "message_inbound":
            return await handle_inbound_message(body, db)
        elif webhook_type == "message_sent":
            return await handle_message_sent(body, db)
        elif webhook_type == "message_failed":
            return await handle_message_failed(body, db)
        else:
            print(f"⚠️ Unknown webhook type: {webhook_type}")
            return JSONResponse(content={"status": "ignored"}, status_code=200)
            
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

async def handle_inbound_message(message_data: Dict[str, Any], db: Session) -> JSONResponse:
    """
    Handle incoming messages from users
    """
    try:
        # Extract message details from LoopMessage webhook format
        phone = normalize_phone(message_data.get("recipient", ""))
        body = message_data.get("text", "").strip()
        passthrough = message_data.get("passthrough", "")
        
        print(f"📱 Inbound message from {phone}: {body}")
        print(f"📎 Passthrough data: {passthrough}")
        
        # Find user by phone number
        user = db.query(User).filter_by(phone_number=phone).first()
        if not user:
            print(f"❌ No user found for phone: {phone}")
            return JSONResponse(content={"status": "user_not_found"}, status_code=200)
        
        # Handle the message based on conversation state
        response = await process_user_message(user, body, passthrough, db)
        
        return JSONResponse(content={"status": "processed", "response": response}, status_code=200)
        
    except Exception as e:
        print(f"❌ Error handling inbound message: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

async def process_user_message(user: User, body: str, passthrough: str, db: Session) -> str:
    """
    Process user message and return appropriate response
    """
    try:
        service = LoopMessageService()
        
        print(f"🔍 Processing message: passthrough='{passthrough}', body='{body}'")
        
        # Check if this is a response to a flashcard
        if passthrough and passthrough.startswith("flashcard_id:"):
            flashcard_id = int(passthrough.split(":")[1])
            print(f"📎 Found flashcard_id in passthrough: {flashcard_id}")
            return await handle_flashcard_response(user, flashcard_id, body, service, db)
        
        # Check conversation state
        state = db.query(ConversationState).filter_by(user_id=user.id).first()
        print(f"🗣️ Conversation state: {state.state if state else 'None'}")
        
        if state and state.state == "waiting_for_answer":
            print(f"⏳ User is waiting for answer, flashcard_id: {state.current_flashcard_id}")
            return await handle_flashcard_response(user, state.current_flashcard_id, body, service, db)
        
        # Handle general commands
        if "yes" in body.lower():
            print(f"✅ User said 'yes', starting session")
            return await handle_start_session(user, service, db)
        
        # Default response
        print(f"❓ Unknown message, sending default response")
        return "I didn't understand that. Reply 'Yes' to start a review session."
        
    except Exception as e:
        print(f"❌ Error processing user message: {e}")
        return "Sorry, there was an error processing your message. Please try again."

async def handle_flashcard_response(
    user: User, 
    flashcard_id: int, 
    user_response: str, 
    service: LoopMessageService, 
    db: Session
) -> str:
    """
    Handle user's response to a flashcard question
    """
    try:
        print(f"🔍 Processing flashcard response: user_id={user.id}, flashcard_id={flashcard_id}")
        
        # Get the flashcard
        card = db.query(Flashcard).filter_by(id=flashcard_id).first()
        if not card:
            print(f"❌ Flashcard {flashcard_id} not found")
            return "Hmm, we lost track of your flashcard. Say 'Yes' to start again."
        
        print(f"✅ Found flashcard: {card.concept}")
        
        # Evaluate the answer
        print(f"🧠 Evaluating answer: '{user_response}'")
        result = evaluate_answer(
            concept=card.concept,
            correct_definition=card.definition,
            user_response=user_response
        )
        print(f"✅ LLM evaluation result: {result}")
        
        # Compute next review date
        from app.services.scheduler import compute_next_review
        next_review = compute_next_review(
            last_review_date=datetime.datetime.now(datetime.UTC),
            was_correct=result["was_correct"],
            confidence_score=result["confidence_score"],
            start_hour=user.preferred_start_hour,
            end_hour=user.preferred_end_hour,
            timezone_str=user.timezone
        )
        print(f"📅 Next review scheduled for: {next_review}")
        
        # Save the review
        review = CardReview(
            user_id=user.id,
            flashcard_id=card.id,
            user_response=user_response,
            was_correct=result["was_correct"],
            confidence_score=result["confidence_score"],
            llm_feedback=result["llm_feedback"],
            next_review_date=next_review
        )
        
        db.add(review)
        print(f"💾 Review saved to database")
        
        # Clear conversation state
        state = db.query(ConversationState).filter_by(user_id=user.id).first()
        if state:
            state.state = "idle"
            state.current_flashcard_id = None
            print(f"🔄 Conversation state cleared")
        
        db.commit()
        print(f"✅ Database committed")
        
        # Send feedback to user
        print(f"📤 Sending feedback to {user.phone_number}")
        feedback_result = service.send_feedback(user.phone_number, result["llm_feedback"])
        print(f"📤 Feedback send result: {feedback_result}")
        
        return f"Response processed. Feedback sent to {user.phone_number}"
        
    except Exception as e:
        print(f"❌ Error handling flashcard response: {e}")
        import traceback
        traceback.print_exc()
        return "Sorry, there was an error processing your answer."

async def handle_start_session(user: User, service: LoopMessageService, db: Session) -> str:
    """
    Handle user starting a study session
    """
    try:
        # Get next due flashcard
        card = get_next_due_flashcard(user.id, db)
        if not card:
            service.send_feedback(user.phone_number, "You're all caught up! No flashcards due right now.")
            return "No due flashcards. Reminder sent."
        
        # Set conversation state
        set_conversation_state(user.id, card.id, db)
        
        # Send the flashcard
        result = service.send_flashcard(user.phone_number, card)
        
        if result.get("success"):
            return f"Flashcard sent to {user.phone_number}"
        else:
            return f"Failed to send flashcard: {result.get('error')}"
            
    except Exception as e:
        print(f"❌ Error starting session: {e}")
        return "Sorry, there was an error starting your session."

async def handle_message_sent(message_data: Dict[str, Any], db: Session) -> JSONResponse:
    """Handle message sent confirmation"""
    print(f"✅ Message sent: {message_data.get('message_id')}")
    return JSONResponse(content={"status": "acknowledged"}, status_code=200)

async def handle_message_failed(message_data: Dict[str, Any], db: Session) -> JSONResponse:
    """Handle message failure"""
    print(f"❌ Message failed: {message_data.get('message_id')} - {message_data.get('error')}")
    return JSONResponse(content={"status": "acknowledged"}, status_code=200) 