from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import *

class CardReview(Base):
    __tablename__ = "card_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    flashcard_id = Column(Integer, ForeignKey("flashcards.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_response = Column(Text)
    was_correct = Column(Boolean)
    confidence_score = Column(Float)  # 0-1 from LLM evaluation
    llm_feedback = Column(Text)
    review_date = Column(DateTime(timezone=True), server_default=func.now())
    next_review_date = Column(DateTime(timezone=True), nullable=False)
    
    # SM-2 Algorithm fields
    repetition_count = Column(Integer, default=0)  # Number of successful repetitions
    ease_factor = Column(Float, default=2.5)  # Ease factor (starts at 2.5)
    interval_days = Column(Integer, default=0)  # Current interval in days
    
    # Review source tracking
    is_sms_review = Column(Boolean, default=False)  # True if review was done via SMS
        
    # Relationships
    user = relationship("User", back_populates="reviews")
    flashcard = relationship("Flashcard", back_populates="reviews")

class StudySession(Base):
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_type = Column(String(20))  # 'batch' or 'distributed'
    cards_reviewed = Column(Integer, default=0)
    cards_correct = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    status = Column(String(20), default="active")  # 'active', 'completed', 'cancelled'
    
    # Relationships
    user = relationship("User", back_populates="sessions")

class ConversationState(Base):
    __tablename__ = "conversation_state"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    current_flashcard_id = Column(
    Integer,
    ForeignKey("flashcards.id", ondelete="SET NULL"),
    nullable=True
)
    session_id = Column(Integer, ForeignKey("study_sessions.id"))
    state = Column(String(50))  # 'idle', 'waiting_for_batch_confirm', 'waiting_for_answer', 'session_complete'
    last_message_at = Column(DateTime(timezone=True), server_default=func.now())
    context = Column(Text)  # JSON string for additional state data
    message_count = Column(Integer, default=0)  # Track number of messages sent for skip reminders
    last_sent_flashcard_id = Column(Integer, ForeignKey("flashcards.id", ondelete="SET NULL"), nullable=True)  # Track last sent card to prevent duplicates
    # TODO: Uncomment these after running /admin/migrate-session-progress-fields
    # session_total_cards = Column(Integer, nullable=True)  # Total number of due cards in current session
    # session_current_card = Column(Integer, nullable=True)  # Current card number in session (1-indexed)
    
    # Relationships
    user = relationship("User", back_populates="conversation_state")