import asyncio
import json
import datetime
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Flashcard, ConversationState, CardReview
from app.services.session_manager import get_next_due_flashcard, set_conversation_state
from app.services.evaluator import evaluate_answer
from app.services.loop_message_service import LoopMessageService
from typing import Dict, Any
from app.services.scheduler import compute_next_review
from datetime import datetime
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
        
        # Check conversation state
        try:
            print(f"🗣️ Looking up conversation state for user {user.id}...")
            state = db.query(ConversationState).filter_by(user_id=user.id).first()
            print(f"🗣️ Conversation state lookup for user {user.id}: {state.state if state else 'None'}")
            if state:
                print(f"🗣️ State details: user_id={state.user_id}, flashcard_id={state.current_flashcard_id}, state={state.state}")
                print(f"🗣️ Current time: {datetime.datetime.now()}")
                print(f"🗣️ Last message at: {state.last_message_at}")
                print(f"🗣️ State is waiting_for_answer: {state.state == 'waiting_for_answer'}")
                print(f"🗣️ Has flashcard_id: {state.current_flashcard_id is not None}")
        except Exception as e:
            print(f"❌ Error looking up conversation state: {e}")
            import traceback
            traceback.print_exc()
            state = None
        
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
            if "yes" in body.lower():
                print(f"✅ User confirmed flashcard creation")
                return await handle_flashcard_confirmation(user, state, service, db)
            elif "no" in body.lower():
                print(f"❌ User rejected flashcard creation")
                # Clear the state and ask for new input
                state.state = "idle"
                state.context = None
                db.commit()
                if service:
                    service.send_feedback(user.phone_number, "Flashcard cancelled. Send 'NEW' followed by your flashcard request to try again.")
                return "Flashcard cancelled. Send 'NEW' followed by your flashcard request to try again."
            else:
                return "Please reply 'Yes' to save the flashcard or 'No' to try again."
        
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
        
        # If we have a conversation state but it's not waiting for answer, clear it
        if state and state.state != "waiting_for_answer":
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
            last_review_date=datetime.datetime.now(datetime.UTC),
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
            interval_days=new_interval_days
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
            
            # Send the next flashcard
            if service:
                next_result = service.send_flashcard(user.phone_number, next_card)
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
            print(f"📭 No more due flashcards")
            return f"Response processed. Feedback sent. You're all caught up!"
        
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
        
        # Send the flashcard
        if service:
            result = service.send_flashcard(user.phone_number, card)
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
- tags: tags requested by the user, comma-separated. If no tags requested, this is an empty string.
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

Input: "create a card for Ohm's law"
Output: {{
  "concept": "Ohm's law",
  "definition": "$$ V = IR $$",
  "tags": "",
  "source_url": ""
}}

Important:
- Use double quotes around all keys and string values.
- Escape all backslashes in LaTeX as \\\\ (double-escaped for JSON validity).
- Return only a raw JSON object with no explanation.
- Always include a source_url field, even if empty.

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
        state.last_message_at = datetime.utcnow()
        state.context = json.dumps(card_data)  # Store flashcard data as JSON
        
        db.add(state)
        db.commit()

        # Send the generated flashcard for confirmation
        concept = card_data["concept"]
        definition = card_data["definition"]
        tags = card_data.get("tags", "")
        
        confirmation_message = f"Generated flashcard:\n\nConcept: {concept}\nDefinition: {definition}"
        if tags:
            confirmation_message += f"\nTags: {tags}"
        confirmation_message += "\n\nReply 'Yes' to save or 'No' to try again."

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