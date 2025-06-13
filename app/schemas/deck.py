from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.flashcard import FlashcardOut

class DeckCreate(BaseModel):
    name: str

class DeckOut(BaseModel):
    id: int
    name: str
    user_id: int
    created_at: datetime
    flashcards_count: Optional[int] = None

    class Config:
        from_attributes = True

class DeckWithFlashcards(DeckOut):
    flashcards: List[FlashcardOut] = []

DeckWithFlashcards.model_rebuild() 