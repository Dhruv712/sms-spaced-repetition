from sqlalchemy import Column, Integer, ForeignKey, Boolean, Float, DateTime
from sqlalchemy.orm import relationship
import datetime

class CardReview(Base):
    __tablename__ = "card_reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    flashcard_id = Column(Integer, ForeignKey("flashcards.id"))
    rating = Column(Integer)  # Rating from 1-5
    was_correct = Column(Boolean)
    confidence_score = Column(Float)
    next_review_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC))

    user = relationship("User", back_populates="reviews")
    flashcard = relationship("Flashcard", back_populates="reviews") 