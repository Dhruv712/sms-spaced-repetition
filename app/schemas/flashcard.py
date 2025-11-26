from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

class FlashcardCreate(BaseModel):
    concept: str
    definition: str
    tags: Optional[List[str]] = None
    deck_id: Optional[int] = None
    source_url: Optional[str] = None

class FlashcardOut(BaseModel):
    id: int
    user_id: int
    concept: str
    definition: str
    tags: List[str]
    source_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deck_id: Optional[int] = None
    deck_name: Optional[str] = None

    @validator('tags', pre=True, always=True)
    def parse_tags(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            if not v.strip():
                return []
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        if isinstance(v, list):
            return v
        return []

    class Config:
        orm_mode = True

class FlashcardWithNextReviewOut(BaseModel):
    id: int
    concept: str
    definition: str
    tags: List[str]
    source_url: Optional[str] = None
    next_review_date: Optional[datetime]
    deck_id: Optional[int] = None

    @validator('tags', pre=True, always=True)
    def parse_tags_for_review(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            if not v.strip():
                return []
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        if isinstance(v, list):
            return v
        return []