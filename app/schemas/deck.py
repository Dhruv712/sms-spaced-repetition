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
    image_url: Optional[str] = None
    created_at: datetime
    flashcards_count: Optional[int] = None
    sms_enabled: Optional[bool] = False  # False = muted by default

    class Config:
        from_attributes = True

class DeckWithFlashcards(DeckOut):
    flashcards: List[dict]

DeckWithFlashcards.model_rebuild() 