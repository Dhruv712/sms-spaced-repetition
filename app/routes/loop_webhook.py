import asyncio
import json
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Flashcard, ConversationState, CardReview
from app.services.session_manager import get_next_due_flashcard, set_conversation_state
from app.services.evaluator import evaluate_answer
from app.services.loop_message_service import LoopMessageService
from typing import Dict, Any
from app.services.scheduler import compute_next_review, compute_sm2_next_review
from datetime import datetime, timezone
import logging

router = APIRouter(tags=["loop-webhook"])

def normalize_phone(number: str) -> str:
    """Normalize phone number format"""
    number = number.strip()
    if not number.startswith("+") and number.isdigit():
        number = "+" + number
    return number

async def initialize_loop_service_with_timeout():
    """Initialize LoopMessageService with a timeout"""
    try:
        # Use asyncio.wait_for to add a timeout
        loop = asyncio.get_event_loop()
        service = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: LoopMessageService()),
            timeout=5.0  # 5 second timeout
        )
        return service
    except asyncio.TimeoutError:
        print("⏰ LoopMessageService initialization timed out after 5 seconds")
        return None
    except Exception as e:
        print(f"❌ Failed to initialize LoopMessageService: {e}")
        return None

async def send_welcome_message(user: User, first_message: str, db: Session) -> str:
    """
    Send welcome message to first-time users and create initial conversation state
    """
    try:
        # Create welcome message
        welcome_text = f"""🎉 Welcome to Cue, {user.name or 'there'}!

I'm your AI-powered spaced repetition assistant. Here's how to get started:

📝 **Create New Flashcards:**
Text "NEW" followed by your instructions. For example:
"NEW card for the year of the declaration of independence"

🏷️ **Add Tags:**
Include tags in brackets: "NEW card about photosynthesis [biology, science]"

📚 **Review Flashcards:**
I'll send you flashcards to review based on spaced repetition. Just reply with your answer!

💡 **Pro Tips:**
• Be specific in your NEW requests
• Use tags to organize your cards
• I'll remember your progress and schedule reviews optimally

Ready to start learning? Send "NEW" with your first flashcard!"""

        # Initialize LoopMessage service
        service = await initialize_loop_service_with_timeout()
        if service:
            # Send the welcome message
            service._send_message(
                recipient=user.phone_number,
                text=welcome_text
            )
            print(f"✅ Welcome message sent to {user.email}")
        else:
            print(f"⚠️ Could not send welcome message - service unavailable")
        
        # Create initial conversation state
        conversation_state = ConversationState(
            user_id=user.id,
            state="idle",
            last_message_at=datetime.now(timezone.utc)
        )
        db.add(conversation_state)
        db.commit()
        print(f"✅ Created initial conversation state for user {user.id}")
        
        return "Welcome message sent successfully"
        
    except Exception as e:
        print(f"❌ Error sending welcome message: {e}")
        import traceback
        traceback.print_exc()
        return "Welcome message failed"

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
            print(f"📤 Processing message_sent webhook - this should NOT trigger response processing")
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
        print(f"🔍 Starting handle_inbound_message with data: {message_data}")
        
        # Extract message details from LoopMessage webhook format
        phone = normalize_phone(message_data.get("recipient", ""))
        body = message_data.get("text", "").strip()
        
        # Try different possible locations for passthrough data
        passthrough = message_data.get("passthrough", "")
        if not passthrough:
            # Check if passthrough is nested in a message object
            message_obj = message_data.get("message", {})
            if isinstance(message_obj, dict):
                passthrough = message_obj.get("passthrough", "")
        
        print(f"📱 Inbound message from {phone}: {body}")
        print(f"📎 Passthrough data: {passthrough}")
        print(f"🔍 Full webhook payload for debugging: {json.dumps(message_data, indent=2)}")
        
        # Find user by phone number
        user = db.query(User).filter_by(phone_number=phone).first()
        if not user:
            print(f"❌ No user found for phone: {phone}")
            return JSONResponse(content={"status": "user_not_found"}, status_code=200)
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Check if this is a first-time user (no conversation state)
        existing_conversation = db.query(ConversationState).filter_by(user_id=user.id).first()
        if not existing_conversation:
            print(f"🎉 First-time user detected! Sending welcome message.")
            # Send welcome message and create initial conversation state
            welcome_response = await send_welcome_message(user, body, db)
            return JSONResponse(content={"status": "processed", "response": welcome_response}, status_code=200)
        
        # Handle the message based on conversation state
        response = await process_user_message(user, body, passthrough, db)
        
        print(f"📤 Returning response: {response}")
        return JSONResponse(content={"status": "processed", "response": response}, status_code=200)
        
    except Exception as e:
        print(f"❌ Error handling inbound message: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

async def process_user_message(user: User, body: str, passthrough: str, db: Session) -> str:
    """
    Process user message and return appropriate response
    """
    try:
        print(f"🔍 Processing message: passthrough='{passthrough}', body='{body}'")
        
        # Initialize LoopMessage service with timeout
        print(f"🔧 Initializing LoopMessage service with timeout...")
        service = await initialize_loop_service_with_timeout()
        if service:
            print(f"✅ LoopMessage service initialized successfully")
        else:
            print(f"⚠️ LoopMessage service initialization failed or timed out")
        
        # Check conversation state first (needed for skip command check)
        try:
            print(f"🗣️ Looking up conversation state for user {user.id}...")
            state = db.query(ConversationState).filter_by(user_id=user.id).first()
            print(f"🗣️ Conversation state lookup for user {user.id}: {state.state if state else 'None'}")
            if state:
                print(f"🗣️ State details: user_id={state.user_id}, flashcard_id={state.current_flashcard_id}, state={state.state}")
                print(f"🗣️ Current time: {datetime.now()}")
                print(f"🗣️ Last message at: {state.last_message_at}")
                print(f"🗣️ State is waiting_for_answer: {state.state == 'waiting_for_answer'}")
                print(f"🗣️ State is waiting_for_flashcard_confirmation: {state.state == 'waiting_for_flashcard_confirmation'}")
                print(f"🗣️ Has flashcard_id: {state.current_flashcard_id is not None}")
                print(f"🗣️ Context: {state.context}")
        except Exception as e:
            print(f"❌ Error looking up conversation state: {e}")
            import traceback
            traceback.print_exc()
            state = None
        
        # Handle skip command FIRST (before processing as answer)
        if body and body.strip() and body.strip().lower() == "skip":
            print(f"⏭️ User wants to skip current flashcard")
            if state and state.state == "waiting_for_answer" and state.current_flashcard_id:
                # Mark the card as skipped (don't create a review, just move to next)
                state.state = "idle"
                state.current_flashcard_id = None
                db.commit()
                
                # Get next due flashcard
                next_card = get_next_due_flashcard(user.id, db)
                if next_card:
                    set_conversation_state(user.id, next_card.id, db)
                    if service:
                        state_after = db.query(ConversationState).filter_by(user_id=user.id).first()
                        message_count = state_after.message_count if state_after else 0
                        result = service.send_flashcard(user.phone_number, next_card, message_count)
                        if result.get("success"):
                            return "Card skipped. Next flashcard sent."
                    return "Card skipped. Next flashcard sent."
                else:
                    # Send completion message with stats
                    completion_message = generate_session_completion_message(user.id, db)
                    if service:
                        service.send_feedback(user.phone_number, completion_message)
                    return "Card skipped. Completion message sent."
            else:
                if service:
                    service.send_feedback(user.phone_number, "No card to skip. Send 'Yes' to start a session.")
                return "No card to skip."
        
        # Check if this is a response to a flashcard
        if passthrough and passthrough.startswith("flashcard_id:"):
            flashcard_id = int(passthrough.split(":")[1])
            print(f"📎 Found flashcard_id in passthrough: {flashcard_id}")
            # Only process if there's actual user input
            if body and body.strip():
                return await handle_flashcard_response(user, flashcard_id, body, service, db)
            else:
                print(f"⚠️ Empty body received with passthrough, ignoring")
                return "No user input received"
        
        # Fallback: If no passthrough but conversation state exists, use that
        print(f"🔍 Checking conversation state fallback...")
        print(f"   - State exists: {state is not None}")
        if state:
            print(f"   - State is waiting_for_answer: {state.state == 'waiting_for_answer'}")
            print(f"   - Has flashcard_id: {state.current_flashcard_id is not None}")
            print(f"   - Flashcard_id: {state.current_flashcard_id}")
        
        if state and state.state == "waiting_for_answer" and state.current_flashcard_id:
            print(f"⏳ User is waiting for answer, flashcard_id: {state.current_flashcard_id}")
            print(f"📎 Using conversation state as fallback (no passthrough data)")
            # Only process if there's actual user input
            if body and body.strip():
                print(f"📝 Processing response with conversation state fallback")
                return await handle_flashcard_response(user, state.current_flashcard_id, body, service, db)
            else:
                print(f"⚠️ Empty body received with conversation state, ignoring")
                return "No user input received"
        else:
            print(f"❌ Conversation state fallback conditions not met")
            print(f"   - State exists: {state is not None}")
            if state:
                print(f"   - State: {state.state}")
                print(f"   - Flashcard ID: {state.current_flashcard_id}")
        
        # Handle flashcard confirmation FIRST (before general commands)
        if state and state.state == "waiting_for_flashcard_confirmation":
            print(f"🎯 Found flashcard confirmation state for user {user.id}")
            if "save" in body.lower():
                print(f"✅ User confirmed flashcard creation")
                return await handle_flashcard_confirmation(user, state, service, db)
            elif "no" in body.lower() or "cancel" in body.lower():
                print(f"❌ User rejected flashcard creation")
                # Clear the state and ask for new input
                state.state = "idle"
                state.context = None
                db.commit()
                if service:
                    service.send_feedback(user.phone_number, "Flashcard cancelled. Send 'NEW' followed by your flashcard request to try again.")
                return "Flashcard cancelled. Send 'NEW' followed by your flashcard request to try again."
            else:
                return "Please reply 'SAVE' to save the flashcard or 'NO' to try again."
        else:
            print(f"❌ No flashcard confirmation state found. State: {state.state if state else 'None'}")
        
        # Handle general commands
        if "yes" in body.lower():
            print(f"✅ User said 'yes', starting session")
            return await handle_start_session(user, service, db)
        
        # Handle NEW flashcard creation
        if body.strip().upper().startswith("NEW"):
            print(f"🎯 User wants to create a new flashcard")
            natural_text = body.strip()[3:].strip()  # Remove "NEW" prefix
            if natural_text:
                return await handle_natural_flashcard_creation(user, natural_text, service, db)
            else:
                return "Please provide a description after 'NEW'. Example: 'NEW Create a flashcard about photosynthesis'"
        
        # If we have a conversation state but it's not waiting for answer or flashcard confirmation, clear it
        if state and state.state not in ["waiting_for_answer", "waiting_for_flashcard_confirmation"]:
            print(f"🔄 Clearing stale conversation state: {state.state}")
            state.state = "idle"
            state.current_flashcard_id = None
            db.commit()
        
        # Default response
        print(f"❓ Unknown message, sending default response")
        return "I didn't understand that. Reply 'Yes' to start a review session, or 'NEW' followed by a description to create a flashcard."
        
    except Exception as e:
        print(f"❌ Error processing user message: {e}")
        import traceback
        traceback.print_exc()
        return "Sorry, there was an error processing your message. Please try again."

def generate_session_completion_message(user_id: int, db: Session) -> str:
    """
    Generate completion message with session stats and next review time
    """
    from app.models import CardReview, Flashcard
    from datetime import datetime, timezone, timedelta
    
    today = datetime.now(timezone.utc).date()
    start_of_day = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
    end_of_day = datetime.combine(today, datetime.max.time(), tzinfo=timezone.utc)
    
    # Get all SMS reviews from today
    today_reviews = db.query(CardReview).filter(
        CardReview.user_id == user_id,
        CardReview.is_sms_review == True,
        CardReview.review_date >= start_of_day,
        CardReview.review_date <= end_of_day
    ).all()
    
    if not today_reviews:
        # No reviews today, just send basic message
        next_review_time = get_next_review_time()
        return f"That's it for now! Next review: {next_review_time}"
    
    # Calculate stats
    total_reviews = len(today_reviews)
    correct_reviews = sum(1 for r in today_reviews if r.was_correct)
    percent_correct = (correct_reviews / total_reviews * 100) if total_reviews > 0 else 0
    
    # Find issue areas (tags/decks with lowest accuracy)
    tag_stats = {}
    deck_stats = {}
    
    for review in today_reviews:
        flashcard = db.query(Flashcard).filter_by(id=review.flashcard_id).first()
        if not flashcard:
            continue
        
        # Track by tag
        if flashcard.tags:
            tag = flashcard.tags
            if tag not in tag_stats:
                tag_stats[tag] = {'total': 0, 'correct': 0}
            tag_stats[tag]['total'] += 1
            if review.was_correct:
                tag_stats[tag]['correct'] += 1
        
        # Track by deck
        if flashcard.deck_id:
            deck_id = flashcard.deck_id
            if deck_id not in deck_stats:
                deck_stats[deck_id] = {'total': 0, 'correct': 0}
            deck_stats[deck_id]['total'] += 1
            if review.was_correct:
                deck_stats[deck_id]['correct'] += 1
    
    # Find weakest areas (lowest accuracy, minimum 2 reviews)
    issue_areas = []
    
    for tag, stats in tag_stats.items():
        if stats['total'] >= 2:
            accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            if accuracy < 70:  # Less than 70% correct
                issue_areas.append(f"{tag} ({int(accuracy)}%)")
    
    for deck_id, stats in deck_stats.items():
        if stats['total'] >= 2:
            from app.models import Deck
            deck = db.query(Deck).filter_by(id=deck_id).first()
            if deck:
                accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
                if accuracy < 70:  # Less than 70% correct
                    issue_areas.append(f"{deck.name} ({int(accuracy)}%)")
    
    # Limit to top 3 issue areas
    issue_areas = issue_areas[:3]
    
    # Get next review time (12 PM or 9 PM UTC)
    next_review_time = get_next_review_time()
    
    # Build message
    message = f"That's it for now! 📊\n\n"
    message += f"Today: {correct_reviews}/{total_reviews} correct ({int(percent_correct)}%)\n"
    
    if issue_areas:
        message += f"\nFocus areas: {', '.join(issue_areas)}\n"
    
    message += f"\nNext review: {next_review_time}"
    
    return message


def get_next_review_time() -> str:
    """
    Get the next review time (12 PM or 9 PM UTC, whichever comes next)
    """
    from datetime import datetime, timezone, time
    
    now = datetime.now(timezone.utc)
    today = now.date()
    
    # 12 PM UTC
    noon_utc = datetime.combine(today, time(12, 0), tzinfo=timezone.utc)
    # 9 PM UTC
    evening_utc = datetime.combine(today, time(21, 0), tzinfo=timezone.utc)
    
    if now < noon_utc:
        return "12 PM UTC today"
    elif now < evening_utc:
        return "9 PM UTC today"
    else:
        # Next is tomorrow at 12 PM
        return "12 PM UTC tomorrow"


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
        
        # Get the previous review for this flashcard to get SM-2 data
        previous_review = db.query(CardReview).filter_by(
            user_id=user.id, 
            flashcard_id=card.id
        ).order_by(CardReview.review_date.desc()).first()
        
        # Get SM-2 data from previous review, or use defaults
        repetition_count = previous_review.repetition_count if previous_review else 0
        ease_factor = previous_review.ease_factor if previous_review else 2.5
        interval_days = previous_review.interval_days if previous_review else 0
        
        # Compute next review date using SM-2 algorithm
        next_review = compute_next_review(
            last_review_date=datetime.now(timezone.utc),
            was_correct=result["was_correct"],
            confidence_score=result["confidence_score"],
            start_hour=user.preferred_start_hour,
            end_hour=user.preferred_end_hour,
            timezone_str=user.timezone,
            repetition_count=repetition_count,
            ease_factor=ease_factor,
            interval_days=interval_days
        )
        
        # Compute new SM-2 values
        new_repetition_count, new_ease_factor, new_interval_days = compute_sm2_next_review(
            repetition_count, ease_factor, interval_days, 
            result["was_correct"], result["confidence_score"]
        )
        
        print(f"📅 Next review scheduled for: {next_review}")
        print(f"🔄 SM-2: rep={new_repetition_count}, ease={new_ease_factor:.2f}, interval={new_interval_days} days")
        
        # Check SMS review limit for free users
        from app.services.premium_service import check_sms_limit
        sms_limit_check = check_sms_limit(user, db)
        if not sms_limit_check["within_limit"]:
            return f"❌ You've reached your monthly limit of {sms_limit_check['limit']} SMS reviews. Upgrade to Premium for unlimited reviews! Visit trycue.xyz to upgrade."
        
        # Save the review with SM-2 data
        review = CardReview(
            user_id=user.id,
            flashcard_id=card.id,
            user_response=user_response,
            was_correct=result["was_correct"],
            confidence_score=result["confidence_score"],
            llm_feedback=result["llm_feedback"],
            next_review_date=next_review,
            repetition_count=new_repetition_count,
            ease_factor=new_ease_factor,
            interval_days=new_interval_days,
            is_sms_review=True  # This review came via SMS
        )
        
        db.add(review)
        print(f"💾 Review saved to database")
        
        # Update user streak tracking
        from app.services.summary_service import calculate_streak_days
        today = datetime.now(timezone.utc).date()
        user_today = user.last_study_date.date() if user.last_study_date else None
        
        if user_today != today:
            # New day - update streak
            streak_days = calculate_streak_days(user.id, db)
            user.current_streak_days = streak_days
            if streak_days > (user.longest_streak_days or 0):
                user.longest_streak_days = streak_days
            user.last_study_date = datetime.now(timezone.utc)
        
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
        if service:
            feedback_result = service.send_feedback(user.phone_number, result["llm_feedback"])
            print(f"📤 Feedback send result: {feedback_result}")
        else:
            print(f"📤 LoopMessage service not initialized, skipping feedback.")
        
        # Check if there are more due flashcards and send the next one
        print(f"🔍 Checking for more due flashcards...")
        next_card = get_next_due_flashcard(user.id, db)
        if next_card:
            print(f"📚 Found next due flashcard: {next_card.concept} (ID: {next_card.id})")
            
            # Set conversation state for the next card
            set_conversation_state(user.id, next_card.id, db)
            
            # Get message count for skip reminder
            state_after = db.query(ConversationState).filter_by(user_id=user.id).first()
            message_count = state_after.message_count if state_after else 0
            
            # Send the next flashcard
            if service:
                next_result = service.send_flashcard(user.phone_number, next_card, message_count)
                if next_result.get("success"):
                    print(f"📤 Next flashcard sent successfully: {next_card.concept}")
                    return f"Response processed. Feedback sent. Next flashcard sent: {next_card.concept}"
                else:
                    print(f"❌ Failed to send next flashcard: {next_result.get('error')}")
                    return f"Response processed. Feedback sent. Error sending next flashcard."
            else:
                print(f"📤 LoopMessage service not initialized, skipping next flashcard.")
                return f"Response processed. Feedback sent. Error sending next flashcard."
        else:
            print(f"📭 No more due flashcards - sending completion message with stats")
            # Send completion message with stats
            completion_message = generate_session_completion_message(user.id, db)
            if service:
                service.send_feedback(user.phone_number, completion_message)
            return f"Response processed. Feedback sent. Completion message sent."
        
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
            if service:
                service.send_feedback(user.phone_number, "You're all caught up! No flashcards due right now.")
            else:
                print(f"📤 LoopMessage service not initialized, skipping reminder.")
            return "No due flashcards. Reminder sent."
        
        # Set conversation state
        set_conversation_state(user.id, card.id, db)
        
        # Get message count for skip reminder
        state_after = db.query(ConversationState).filter_by(user_id=user.id).first()
        message_count = state_after.message_count if state_after else 0
        
        # Send the flashcard
        if service:
            result = service.send_flashcard(user.phone_number, card, message_count)
            if result.get("success"):
                return f"Flashcard sent to {user.phone_number}"
            else:
                return f"Failed to send flashcard: {result.get('error')}"
        else:
            print(f"📤 LoopMessage service not initialized, skipping sending flashcard.")
            return "Sorry, there was an error starting your session."
            
    except Exception as e:
        print(f"❌ Error starting session: {e}")
        return "Sorry, there was an error starting your session."

async def handle_message_sent(message_data: Dict[str, Any], db: Session) -> JSONResponse:
    """Handle message sent confirmation"""
    print(f"✅ Message sent: {message_data.get('message_id')}")
    print(f"📤 message_sent webhook - this should ONLY acknowledge, not process responses")
    print(f"📤 message_sent data: {json.dumps(message_data, indent=2)}")
    return JSONResponse(content={"status": "acknowledged"}, status_code=200)

async def handle_message_failed(message_data: Dict[str, Any], db: Session) -> JSONResponse:
    """Handle message failure"""
    print(f"❌ Message failed: {message_data.get('message_id')} - {message_data.get('error')}")
    return JSONResponse(content={"status": "acknowledged"}, status_code=200) 

async def handle_natural_flashcard_creation(user: User, natural_text: str, service: LoopMessageService, db: Session) -> str:
    """
    Handle creation of flashcard from natural language via SMS
    """
    try:
        from openai import OpenAI
        import os
        import json
        import re
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        print(f"🎯 Creating flashcard from natural language: '{natural_text}'")
        
        # Use the same prompt as the web interface
        prompt = f"""
You are an assistant that extracts flashcards from natural language.

Each flashcard has three fields:
- concept: what the user is trying to remember
- definition: the answer, explanation, or formula (use LaTeX if the definition is a formula)
- tags: tags requested by the user, comma-separated. The user may include tags in brackets, like [tag1, tag2, ...]. Convert all tags to lowercase (e.g., "ML" becomes "ml"). If no tags requested, this is an empty string.
- source_url: the URL of the source you used to verify the information. If no source was used, this should be an empty string.

Return ONLY a JSON object with these fields. No text before or after it.

Examples:

Input: "make a card about how Pretoria is Elon Musk's birthplace, with biography and Elon tags"
Output: {{
  "concept": "Elon Musk's birthplace",
  "definition": "Pretoria",
  "tags": "biography, Elon",
  "source_url": "https://example.com/elon-musk-biography"
}}

Input: "create a card for the capital of Japan"
Output: {{
  "concept": "Capital of Japan",
  "definition": "Tokyo",
  "tags": "",
  "source_url": "https://example.com/japan-capital"
}}

Input: "create a card for Ohm's law [circuits, EE]"
Output: {{
  "concept": "Ohm's law",
  "definition": "$$ V = IR $$",
  "tags": "circuits, ee",
  "source_url": ""
}}

Important:
- Use double quotes around all keys and string values.
- Escape all backslashes in LaTeX as \\\\ (double-escaped for JSON validity).
- Return only a raw JSON object with no explanation.
- Always include a source_url field, even if empty.

Lastly, if the user has provided their own definition, remain as close to theirs as possible, prioritizing concision and making sure to not be verbose.

Now convert this into a flashcard:
"{natural_text}"
"""

        # Generate flashcard using GPT
        completion = client.chat.completions.create(
            model="gpt-4o-search-preview",
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = completion.choices[0].message.content.strip()
        print(f"🤖 GPT response: {response_text}")

        # Parse JSON response
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        try:
            card_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            # Fallback: escape single backslashes and try again
            safe_text = re.sub(r'(?<!\\)\\(?![\\ntr"])', r'\\\\', response_text)
            try:
                card_data = json.loads(safe_text)
            except json.JSONDecodeError as e2:
                return "Sorry, I couldn't generate a flashcard from that. Please try again with different wording."

        # Normalize tags to lowercase
        if "tags" in card_data and card_data["tags"]:
            # Split by comma, strip whitespace, convert to lowercase, then rejoin
            tags_list = [tag.strip().lower() for tag in card_data["tags"].split(",") if tag.strip()]
            card_data["tags"] = ", ".join(tags_list)
        
        # Validate required fields
        if "concept" not in card_data or "definition" not in card_data:
            return "Sorry, I couldn't generate a proper flashcard. Please try again."

        # Set conversation state to waiting for confirmation
        state = db.query(ConversationState).filter_by(user_id=user.id).first()
        if not state:
            state = ConversationState(user_id=user.id)
        
        # Store the generated flashcard data in context
        state.state = "waiting_for_flashcard_confirmation"
        state.current_flashcard_id = None
        state.last_message_at = datetime.now(timezone.utc)
        state.context = json.dumps(card_data)  # Store flashcard data as JSON
        
        print(f"💾 Saving conversation state: user_id={user.id}, state=waiting_for_flashcard_confirmation, context={state.context}")
        
        db.add(state)
        db.commit()
        
        # Verify the state was saved
        verification_state = db.query(ConversationState).filter_by(user_id=user.id).first()
        if verification_state:
            print(f"✅ Verification: State saved successfully - user_id={verification_state.user_id}, state={verification_state.state}, context={verification_state.context}")
        else:
            print(f"❌ Verification: No state found after saving!")

        # Send the generated flashcard for confirmation
        concept = card_data["concept"]
        definition = card_data["definition"]
        tags = card_data.get("tags", "")
        
        confirmation_message = f"Generated flashcard:\n\nConcept: {concept}\nDefinition: {definition}"
        if tags:
            confirmation_message += f"\nTags: {tags}"
        confirmation_message += "\n\nReply 'SAVE' to save or 'NO' to try again."

        if service:
            service.send_feedback(user.phone_number, confirmation_message)
        
        return f"Flashcard generated and sent for confirmation to {user.phone_number}"
        
    except Exception as e:
        print(f"❌ Error creating natural flashcard: {e}")
        import traceback
        traceback.print_exc()
        return "Sorry, there was an error creating your flashcard. Please try again."

async def handle_flashcard_confirmation(user: User, state: ConversationState, service: LoopMessageService, db: Session) -> str:
    """
    Handle user confirmation of flashcard creation
    """
    try:
        print(f"💾 Saving confirmed flashcard for user {user.id}")
        
        # Get the flashcard data from context
        if not state.context:
            return "Error: No flashcard data found. Please try creating the flashcard again."
        
        card_data = json.loads(state.context)
        
        # Create the flashcard
        from app.models import Flashcard
        
        # Sanitize source_url
        source_url = card_data.get("source_url", "").lstrip('@').strip()
        
        new_flashcard = Flashcard(
            user_id=user.id,
            concept=card_data["concept"],
            definition=card_data["definition"],
            tags=card_data.get("tags", ""),
            source_url=source_url
        )
        
        db.add(new_flashcard)
        db.commit()
        db.refresh(new_flashcard)
        
        print(f"✅ Flashcard saved: ID {new_flashcard.id}, Concept: {new_flashcard.concept}")
        
        # Clear the conversation state
        state.state = "idle"
        state.context = None
        state.current_flashcard_id = None
        db.commit()
        
        # Send confirmation to user
        confirmation_message = f"✅ Flashcard saved successfully!\n\nConcept: {new_flashcard.concept}\nDefinition: {new_flashcard.definition}"
        if new_flashcard.tags:
            confirmation_message += f"\nTags: {new_flashcard.tags}"
        
        if service:
            service.send_feedback(user.phone_number, confirmation_message)
        
        return f"Flashcard saved successfully! ID: {new_flashcard.id}"
        
    except Exception as e:
        print(f"❌ Error saving flashcard: {e}")
        import traceback
        traceback.print_exc()
        return "Sorry, there was an error saving your flashcard. Please try again." 