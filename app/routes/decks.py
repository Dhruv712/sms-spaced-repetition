from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Deck, User, Flashcard
from app.schemas.deck import DeckCreate, DeckOut, DeckWithFlashcards
from app.services.auth import get_current_active_user
from typing import List

router = APIRouter()

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