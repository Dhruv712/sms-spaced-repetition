from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Deck, User, Flashcard
from app.schemas.deck import DeckCreate, DeckOut, DeckWithFlashcards
from app.services.auth import get_current_active_user
from typing import List
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
        
        # Return the full URL path
        return f"{base_url}/uploads/decks/{deck_id}/{filename}"
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
    return [
        DeckOut(
            id=deck.id,
            name=deck.name,
            user_id=deck.user_id,
            image_url=get_full_image_url(deck.image_url),
            created_at=deck.created_at,
            flashcards_count=db.query(func.count(Flashcard.id)).filter(Flashcard.deck_id == deck.id).scalar()
        )
        for deck in decks
    ]

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

@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deck(
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
    
    # Option 1: Disassociate flashcards from this deck (set deck_id to null)
    # This is generally safer than deleting cards along with the deck
    db.query(Flashcard).filter(Flashcard.deck_id == deck_id).update({"deck_id": None})

    db.delete(deck)
    db.commit()
    return {"message": "Deck deleted successfully and flashcards disassociated"} 