from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ManualReviewSchema(BaseModel):
    flashcard_id: int
    answer: str

class ReviewOut(BaseModel):
    id: int
    user_id: int
    flashcard_id: int
    user_response: str
    was_correct: bool
    confidence_score: float
    llm_feedback: str
    next_review_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewWithFlashcard(ReviewOut):
    flashcard: dict  # This will be populated with the flashcard data

class ReviewCreate(BaseModel):
    pass