from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReviewCreate(BaseModel):
    user_id: int
    flashcard_id: int
    user_response: str

class ReviewOut(BaseModel):
    id: int
    was_correct: bool
    confidence_score: float
    llm_feedback: str
    next_review_date: datetime

    class Config:
        orm_mode = True
