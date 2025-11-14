from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.database import get_db
from app.models import Deck, User, Flashcard, UserDeckSmsSettings, CardReview
from app.schemas.deck import DeckCreate, DeckOut, DeckWithFlashcards
from app.services.auth import get_current_active_user
from app.services.premium_service import check_deck_limit
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import os
import uuid
from PIL import Image
import io

router = APIRouter()

def get_full_image_url(image_url: str | None) -> str | None:
    """Convert relative image URL to full URL if needed"""
    if not image_url:
        return None
    
    # If it's already a full URL, return as is
    if image_url.startswith('http'):
        return image_url
    
    # Get base URL from environment or use Railway backend URL as fallback
    base_url = os.getenv("BASE_URL", "https://sms-spaced-repetition-production.up.railway.app")
    
    # Convert relative URL to full URL
    # Ensure image_url starts with / for proper concatenation
    if not image_url.startswith('/'):
        image_url = '/' + image_url
    return f"{base_url}{image_url}"

def save_uploaded_image(file: UploadFile, deck_id: int) -> str:
    """Save uploaded image and return the file path"""
    # Create deck-specific directory
    deck_dir = f"uploads/decks/{deck_id}"
    os.makedirs(deck_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"preview_{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(deck_dir, filename)
    
    # Read and validate image
    try:
        contents = file.file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Resize image to reasonable dimensions (e.g., 300x200)
        image.thumbnail((300, 200), Image.Resampling.LANCZOS)
        
        # Save the resized image
        image.save(file_path, quality=85, optimize=True)
        
        # Get base URL from environment or use Railway backend URL as fallback
        base_url = os.getenv("BASE_URL", "https://sms-spaced-repetition-production.up.railway.app")
        
        # Return the relative path (will be converted to full URL by get_full_image_url)
        return f"/uploads/decks/{deck_id}/{filename}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

@router.post("/upload-image/{deck_id}")
async def upload_deck_image(
    deck_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a preview image for a deck"""
    # Verify deck exists and belongs to user
    deck = db.query(Deck).filter(Deck.id == deck_id, Deck.user_id == current_user.id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found or not authorized")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save the image
    image_url = save_uploaded_image(file, deck_id)
    
    # Update deck with new image URL
    deck.image_url = image_url
    db.commit()
    db.refresh(deck)
    
    return {"image_url": image_url}

@router.post("/", response_model=DeckOut, status_code=status.HTTP_201_CREATED)
def create_deck(
    deck: DeckCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check deck limit for free users
    limit_check = check_deck_limit(current_user, db)
    if not limit_check["can_create"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You've reached the free tier limit of {limit_check['limit']} decks. Upgrade to Premium to create unlimited decks."
        )
    
    db_deck = Deck(name=deck.name, user_id=current_user.id)
    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)
    return db_deck

@router.get("/", response_model=List[DeckOut])
def get_all_decks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    decks = db.query(Deck).filter(Deck.user_id == current_user.id).all()
    
    # Get SMS settings for all decks
    sms_settings = {
        setting.deck_id: setting.sms_enabled
        for setting in db.query(UserDeckSmsSettings).filter(
            UserDeckSmsSettings.user_id == current_user.id
        ).all()
    }
    
    result = []
    for deck in decks:
        deck_out = DeckOut(
            id=deck.id,
            name=deck.name,
            user_id=deck.user_id,
            image_url=get_full_image_url(deck.image_url),
            created_at=deck.created_at,
            flashcards_count=db.query(func.count(Flashcard.id)).filter(Flashcard.deck_id == deck.id).scalar()
        )
        # Set SMS enabled status (defaults to False if not set)
        deck_out.sms_enabled = sms_settings.get(deck.id, False)  # Default to False (muted)
        result.append(deck_out)
    
    return result

@router.get("/{deck_id}", response_model=DeckWithFlashcards)
def get_deck_by_id(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    deck = (
        db.query(Deck)
        .filter(Deck.id == deck_id, Deck.user_id == current_user.id)
        .first()
    )
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found or not authorized")
    
    # Manually load flashcards with their tags parsed correctly
    flashcards_data = []
    for card in deck.flashcards:
        if isinstance(card.tags, str):
            parsed_tags = [tag.strip() for tag in card.tags.split(',') if tag.strip()]
        else:
            parsed_tags = card.tags if card.tags is not None else []
        flashcards_data.append({
            "id": card.id,
            "user_id": card.user_id,
            "concept": card.concept,
            "definition": card.definition,
            "tags": parsed_tags,
            "created_at": card.created_at,
            "updated_at": card.updated_at,
            "deck_id": card.deck_id,
        })

    return DeckWithFlashcards(
        id=deck.id,
        name=deck.name,
        user_id=deck.user_id,
        image_url=get_full_image_url(deck.image_url),
        created_at=deck.created_at,
        flashcards_count=len(deck.flashcards),
        flashcards=flashcards_data
    )

@router.put("/{deck_id}", response_model=DeckOut)
def update_deck(
    deck_id: int,
    deck_update: DeckCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    deck = (
        db.query(Deck)
        .filter(Deck.id == deck_id, Deck.user_id == current_user.id)
        .first()
    )
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found or not authorized")
    
    deck.name = deck_update.name
    db.commit()
    db.refresh(deck)
    return DeckOut(
        id=deck.id,
        name=deck.name,
        user_id=deck.user_id,
        image_url=get_full_image_url(deck.image_url),
        created_at=deck.created_at,
        flashcards_count=db.query(func.count(Flashcard.id)).filter(Flashcard.deck_id == deck.id).scalar()
    )

@router.delete("/{deck_id}")
def delete_deck(
    deck_id: int,
    delete_cards: bool = False,  # Query parameter to delete cards
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    deck = (
        db.query(Deck)
        .filter(Deck.id == deck_id, Deck.user_id == current_user.id)
        .first()
    )
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found or not authorized")
    
    # Count flashcards in this deck
    flashcard_count = db.query(Flashcard).filter(Flashcard.deck_id == deck_id).count()
    
    if delete_cards:
        # Delete all flashcards in this deck
        db.query(Flashcard).filter(Flashcard.deck_id == deck_id).delete()
        message = f"Deck deleted successfully. {flashcard_count} flashcard(s) were also deleted."
    else:
        # Disassociate flashcards from this deck (set deck_id to null)
        db.query(Flashcard).filter(Flashcard.deck_id == deck_id).update({"deck_id": None})
        message = f"Deck deleted successfully. {flashcard_count} flashcard(s) were unassigned from this deck."

    db.delete(deck)
    db.commit()
    return {"message": message, "deleted_cards": delete_cards, "flashcard_count": flashcard_count}

class DeckSmsToggle(BaseModel):
    sms_enabled: bool

@router.put("/{deck_id}/sms", response_model=dict)
def toggle_deck_sms(
    deck_id: int,
    sms_toggle: DeckSmsToggle,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Toggle SMS enabled/disabled for a deck"""
    # Verify deck exists and belongs to user
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found or not authorized")
    
    # Get or create SMS setting for this user-deck combination
    sms_setting = db.query(UserDeckSmsSettings).filter(
        UserDeckSmsSettings.user_id == current_user.id,
        UserDeckSmsSettings.deck_id == deck_id
    ).first()
    
    if sms_setting:
        # Update existing setting
        sms_setting.sms_enabled = sms_toggle.sms_enabled
    else:
        # Create new setting
        sms_setting = UserDeckSmsSettings(
            user_id=current_user.id,
            deck_id=deck_id,
            sms_enabled=sms_toggle.sms_enabled
        )
        db.add(sms_setting)
    
    db.commit()
    db.refresh(sms_setting)
    
    return {
        "deck_id": deck_id,
        "sms_enabled": sms_setting.sms_enabled,
        "message": f"SMS {'enabled' if sms_setting.sms_enabled else 'disabled'} for deck '{deck.name}'"
    }

@router.get("/{deck_id}/mastery")
def get_deck_mastery(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get mastery data for a deck - performance over time"""
    # Verify deck exists and belongs to user
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found or not authorized")
    
    # Get all flashcards in this deck
    deck_flashcards = db.query(Flashcard).filter(Flashcard.deck_id == deck_id).all()
    flashcard_ids = [card.id for card in deck_flashcards]
    
    if not flashcard_ids:
        return {
            "deck_id": deck_id,
            "deck_name": deck.name,
            "data_points": [],
            "current_streak": current_user.current_streak_days or 0,
            "longest_streak": current_user.longest_streak_days or 0
        }
    
    # Get all reviews for cards in this deck, ordered by date
    reviews = db.query(CardReview).filter(
        and_(
            CardReview.user_id == current_user.id,
            CardReview.flashcard_id.in_(flashcard_ids)
        )
    ).order_by(CardReview.review_date.asc()).all()
    
    # Group reviews by date and calculate daily performance
    daily_performance = {}
    for review in reviews:
        review_date = review.review_date.date()
        if review_date not in daily_performance:
            daily_performance[review_date] = {
                "total": 0,
                "correct": 0,
                "unique_cards": set()
            }
        
        daily_performance[review_date]["total"] += 1
        daily_performance[review_date]["unique_cards"].add(review.flashcard_id)
        if review.was_correct:
            daily_performance[review_date]["correct"] += 1
    
    # Convert to list of data points for the graph
    data_points = []
    for date, stats in sorted(daily_performance.items()):
        accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        cards_reviewed = len(stats["unique_cards"])  # Unique cards reviewed on this day
        
        data_points.append({
            "date": date.isoformat(),
            "accuracy": round(accuracy, 1),
            "cards_reviewed": cards_reviewed,
            "total_reviews": stats["total"],
            "correct_reviews": stats["correct"]
        })
    
    return {
        "deck_id": deck_id,
        "deck_name": deck.name,
        "data_points": data_points,
        "current_streak": current_user.current_streak_days or 0,
        "longest_streak": current_user.longest_streak_days or 0
    }

@router.get("/mastery/all")
def get_all_decks_mastery(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get mastery data for all decks - overall average accuracy and cards reviewed per day"""
    # Get all flashcards for the user (from all decks and no deck)
    all_flashcards = db.query(Flashcard).filter(Flashcard.user_id == current_user.id).all()
    flashcard_ids = [card.id for card in all_flashcards]
    
    if not flashcard_ids:
        return {
            "data_points": [],
            "current_streak": current_user.current_streak_days or 0,
            "longest_streak": current_user.longest_streak_days or 0
        }
    
    # Get all reviews for all cards, ordered by date
    reviews = db.query(CardReview).filter(
        and_(
            CardReview.user_id == current_user.id,
            CardReview.flashcard_id.in_(flashcard_ids)
        )
    ).order_by(CardReview.review_date.asc()).all()
    
    # Group reviews by date and calculate overall daily performance
    daily_performance = {}
    for review in reviews:
        review_date = review.review_date.date()
        if review_date not in daily_performance:
            daily_performance[review_date] = {
                "total": 0,
                "correct": 0,
                "unique_cards": set()
            }
        
        daily_performance[review_date]["total"] += 1
        daily_performance[review_date]["unique_cards"].add(review.flashcard_id)
        if review.was_correct:
            daily_performance[review_date]["correct"] += 1
    
    # Convert to list of data points for the graph
    data_points = []
    for date, stats in sorted(daily_performance.items()):
        accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        cards_reviewed = len(stats["unique_cards"])  # Unique cards reviewed on this day
        
        data_points.append({
            "date": date.isoformat(),
            "accuracy": round(accuracy, 1),
            "cards_reviewed": cards_reviewed,
            "total_reviews": stats["total"],
            "correct_reviews": stats["correct"]
        })
    
    return {
        "data_points": data_points,
        "current_streak": current_user.current_streak_days or 0,
        "longest_streak": current_user.longest_streak_days or 0
    } 