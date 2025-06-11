from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class FlashcardCreate(BaseModel):
    user_id: int
    concept: str
    definition: str
    tags: Optional[str] = None

class FlashcardOut(BaseModel):
    id: int
    user_id: int
    concept: str
    definition: str
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class FlashcardWithNextReviewOut(BaseModel):
    id: int
    concept: str
    definition: str
    tags: str
    next_review_date: Optional[datetime]