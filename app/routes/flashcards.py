from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.flashcard import FlashcardCreate, FlashcardOut, FlashcardWithNextReviewOut
from app.models import Flashcard, CardReview
from app.database import get_db
from datetime import datetime, timedelta
from app.services.auth import get_current_active_user
from app.models import User
from sqlalchemy import func
from typing import Optional, List
from pydantic import BaseModel
from openai import OpenAI
import os
import json
import re

router = APIRouter()

class DeckAssignment(BaseModel):
    deck_id: Optional[int] = None

@router.post("/", response_model=FlashcardOut)
def create_flashcard(flashcard: FlashcardCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    # Check flashcard limit in deck for free users
    if flashcard.deck_id:
        from app.services.premium_service import check_flashcard_limit_in_deck
        limit_check = check_flashcard_limit_in_deck(flashcard.deck_id, current_user, db)
        if not limit_check["can_add"]:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You've reached the free tier limit of {limit_check['limit']} flashcards per deck. Upgrade to Premium to add unlimited flashcards."
            )
    
    new_card = Flashcard(
        user_id=current_user.id,
        concept=flashcard.concept,
        definition=flashcard.definition,
        tags=', '.join([tag.strip().lower() for tag in flashcard.tags if tag.strip()]) if flashcard.tags else None,
        deck_id=flashcard.deck_id,
        source_url=flashcard.source_url
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card

@router.get("/due", response_model=list[FlashcardOut])
def get_due_flashcards(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user), deck_id: Optional[int] = None):
    from sqlalchemy.orm import joinedload
    from app.models import Deck
    
    now = datetime.utcnow()
    
    query = db.query(Flashcard).options(joinedload(Flashcard.deck)).filter(Flashcard.user_id == current_user.id)
    if deck_id is not None:
        query = query.filter(Flashcard.deck_id == deck_id)

    subquery = db.query(CardReview.flashcard_id).filter(
        CardReview.user_id == current_user.id,
        CardReview.next_review_date > now
    ).subquery()
    
    due_cards = query.filter(
        ~Flashcard.id.in_(subquery)
    ).all()
    
    # Convert to dict format with deck_name
    result = []
    for card in due_cards:
        card_dict = {
            "id": card.id,
            "user_id": card.user_id,
            "concept": card.concept,
            "definition": card.definition,
            "tags": card.tags,
            "source_url": card.source_url,
            "created_at": card.created_at,
            "updated_at": card.updated_at,
            "deck_id": card.deck_id,
            "deck_name": card.deck.name if card.deck else None
        }
        result.append(card_dict)
    
    return result

@router.get("/with-reviews", response_model=list[FlashcardWithNextReviewOut])
def get_flashcards_with_next_review(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user), deck_id: Optional[int] = None, tags: Optional[str] = None):
    query = db.query(Flashcard).filter(Flashcard.user_id == current_user.id)
    if deck_id is not None:
        query = query.filter(Flashcard.deck_id == deck_id)

    if tags is not None:
        query = query.filter(Flashcard.tags.ilike(f"%{tags}%"))

    cards = query.all()
    result = []
    for card in cards:
        latest_review = db.query(CardReview).filter(
            CardReview.user_id == current_user.id,
            CardReview.flashcard_id == card.id
        ).order_by(CardReview.created_at.desc()).first()
        # Ensure tags are a list of strings
        if isinstance(card.tags, str):
            parsed_tags = [tag.strip() for tag in card.tags.split(',') if tag.strip()]
        else:
            parsed_tags = card.tags if card.tags is not None else []

        result.append({
            "id": card.id,
            "concept": card.concept,
            "definition": card.definition,
            "tags": parsed_tags,
            "next_review_date": latest_review.next_review_date if latest_review else None,
            "deck_id": card.deck_id
        })
    return result

@router.get("/", response_model=list[FlashcardOut])
def get_all_flashcards(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user), deck_id: Optional[int] = None):
    query = db.query(Flashcard).filter(Flashcard.user_id == current_user.id)
    if deck_id is not None:
        query = query.filter(Flashcard.deck_id == deck_id)
    return query.all()

@router.get("/{card_id}", response_model=FlashcardOut)
def get_flashcard(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    card = db.query(Flashcard).filter_by(id=card_id, user_id=current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found or not authorized")
    return card

@router.get("/decks/{deck_id}/all-flashcards", response_model=List[FlashcardOut])
def get_all_flashcards_in_deck(deck_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    cards = db.query(Flashcard).filter(Flashcard.user_id == current_user.id, Flashcard.deck_id == deck_id).all()
    return cards

@router.put("/{card_id}", response_model=FlashcardOut)
def update_flashcard(
    card_id: int, 
    flashcard_update: FlashcardCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    card = db.query(Flashcard).filter_by(id=card_id, user_id=current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found or not authorized")
    
    card.concept = flashcard_update.concept
    card.definition = flashcard_update.definition
    # Convert tags array to comma-separated string for database storage (normalize to lowercase)
    if flashcard_update.tags:
        normalized_tags = [tag.strip().lower() for tag in flashcard_update.tags if tag.strip()]
        card.tags = ', '.join(normalized_tags)
    else:
        card.tags = None
    card.deck_id = flashcard_update.deck_id
    card.source_url = flashcard_update.source_url
    
    db.commit()
    db.refresh(card)
    return card

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

@router.patch("/{card_id}/assign-deck")
def assign_flashcard_to_deck(
    card_id: int,
    deck_assignment: DeckAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    card = db.query(Flashcard).filter_by(id=card_id, user_id=current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found or not authorized")
    
    if deck_assignment.deck_id is not None:
        # Verify the deck belongs to the user
        from app.models import Deck
        deck = db.query(Deck).filter_by(id=deck_assignment.deck_id, user_id=current_user.id).first()
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found or not authorized")
    
    card.deck_id = deck_assignment.deck_id
    db.commit()
    db.refresh(card)
    return {"detail": "Flashcard assigned to deck successfully"}

@router.delete("/tags/{tag}")
def delete_tag(
    tag: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a tag from all flashcards belonging to the current user.
    This removes the tag from the tags field but does not delete the flashcards themselves.
    """
    # Get all flashcards for this user that have this tag
    flashcards = db.query(Flashcard).filter(
        Flashcard.user_id == current_user.id,
        Flashcard.tags.ilike(f"%{tag}%")
    ).all()
    
    if not flashcards:
        raise HTTPException(status_code=404, detail=f"Tag '{tag}' not found in any of your flashcards")
    
    # Remove the tag from each flashcard
    updated_count = 0
    for card in flashcards:
        if card.tags:
            # Parse tags, remove the target tag, and reconstruct
            tag_list = [t.strip() for t in card.tags.split(',') if t.strip()]
            # Remove the tag (case-insensitive)
            tag_list = [t for t in tag_list if t.lower() != tag.lower()]
            
            if tag_list:
                card.tags = ', '.join(tag_list)
            else:
                card.tags = None
            updated_count += 1
    
    db.commit()
    
    return {
        "detail": f"Tag '{tag}' removed from {updated_count} flashcard(s)",
        "flashcards_updated": updated_count
    }

class BatchFlashcardCreate(BaseModel):
    raw_text: str
    deck_ids: List[int] = []

@router.post("/batch-create")
def batch_create_flashcards(
    data: BatchFlashcardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create multiple flashcards from pasted text using GPT to parse and structure them.
    Supports various formats: lists, notes, etc.
    """
    if not data.raw_text or not data.raw_text.strip():
        raise HTTPException(status_code=400, detail="raw_text is required and cannot be empty")
    
    # Check deck limits for free users if deck_ids provided
    if data.deck_ids:
        from app.services.premium_service import check_flashcard_limit_in_deck
        for deck_id in data.deck_ids:
            limit_check = check_flashcard_limit_in_deck(deck_id, current_user, db)
            if not limit_check["can_add"]:
                raise HTTPException(
                    status_code=403,
                    detail=f"You've reached the free tier limit of {limit_check['limit']} flashcards in one of the selected decks. Upgrade to Premium for unlimited flashcards."
                )
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""You are an assistant that extracts multiple flashcards from text input. The user may paste:
- A list of terms and definitions
- Notes with concepts and explanations
- Any structured or unstructured text containing information to memorize

For each flashcard, extract:
- concept: what the user is trying to remember (the question/front)
- definition: the answer, explanation, or formula (the back)
- tags: relevant tags if contextually obvious, otherwise empty string
- source_url: empty string (user will add if needed)

Return ONLY a JSON array of flashcard objects. Each object must have: concept, definition, tags, source_url.

Examples:

Input:
"Tokyo - Capital of Japan
Paris - Capital of France
London - Capital of UK"

Output:
[
  {{"concept": "Capital of Japan", "definition": "Tokyo", "tags": "", "source_url": ""}},
  {{"concept": "Capital of France", "definition": "Paris", "tags": "", "source_url": ""}},
  {{"concept": "Capital of UK", "definition": "London", "tags": "", "source_url": ""}}
]

Input:
"Japanese words:
こんにちは - Hello
ありがとう - Thank you
さようなら - Goodbye"

Output:
[
  {{"concept": "こんにちは", "definition": "Hello", "tags": "japanese", "source_url": ""}},
  {{"concept": "ありがとう", "definition": "Thank you", "tags": "japanese", "source_url": ""}},
  {{"concept": "さようなら", "definition": "Goodbye", "tags": "japanese", "source_url": ""}}
]

Important:
- Return ONLY a JSON array, no text before or after
- Use double quotes for all keys and string values
- Escape backslashes in LaTeX as \\\\
- Always include all four fields: concept, definition, tags, source_url
- If input is ambiguous, make reasonable assumptions about concept/definition split
- Extract as many flashcards as possible from the input

Now parse this text into flashcards:
{data.raw_text}
"""
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        response_text = completion.choices[0].message.content.strip()
        
        # Strip markdown code block if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        try:
            cards_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            # Fallback: escape single backslashes and try again
            safe_text = re.sub(r'(?<!\\)\\(?![\\ntr"])', r'\\\\', response_text)
            try:
                cards_data = json.loads(safe_text)
            except json.JSONDecodeError as e2:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to parse GPT response as JSON. Please try again with clearer formatting."
                )
        
        if not isinstance(cards_data, list):
            raise HTTPException(status_code=500, detail="GPT returned invalid format: expected array of flashcards")
        
        if len(cards_data) == 0:
            raise HTTPException(status_code=400, detail="No flashcards could be extracted from the input text")
        
        # Validate and create flashcards
        created_cards = []
        errors = []
        
        for idx, card_data in enumerate(cards_data):
            if not isinstance(card_data, dict):
                errors.append(f"Card {idx + 1}: Invalid format")
                continue
            
            if "concept" not in card_data or "definition" not in card_data:
                errors.append(f"Card {idx + 1}: Missing concept or definition")
                continue
            
            concept = str(card_data["concept"]).strip()
            definition = str(card_data["definition"]).strip()
            
            if not concept or not definition:
                errors.append(f"Card {idx + 1}: Empty concept or definition")
                continue
            
            # Normalize tags
            tags_str = ""
            if "tags" in card_data and card_data["tags"]:
                tags_list = [tag.strip().lower() for tag in str(card_data["tags"]).split(',') if tag.strip()]
                tags_str = ', '.join(tags_list)
            
            # Create flashcard for each selected deck (or no deck if none selected)
            deck_ids_to_use = data.deck_ids if data.deck_ids else [None]
            
            for deck_id in deck_ids_to_use:
                # Check limit again before creating (in case we're creating multiple)
                if deck_id:
                    from app.services.premium_service import check_flashcard_limit_in_deck
                    limit_check = check_flashcard_limit_in_deck(deck_id, current_user, db)
                    if not limit_check["can_add"]:
                        errors.append(f"Card {idx + 1}: Deck limit reached")
                        continue
                
                new_card = Flashcard(
                    user_id=current_user.id,
                    concept=concept,
                    definition=definition,
                    tags=tags_str if tags_str else None,
                    deck_id=deck_id,
                    source_url=str(card_data.get("source_url", "")).strip() or None
                )
                db.add(new_card)
                created_cards.append(new_card)
        
        db.commit()
        
        # Refresh all created cards
        for card in created_cards:
            db.refresh(card)
        
        return {
            "success": True,
            "created_count": len(created_cards),
            "total_parsed": len(cards_data),
            "errors": errors if errors else None,
            "flashcards": [{"id": card.id, "concept": card.concept, "definition": card.definition} for card in created_cards]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create flashcards: {str(e)}")

