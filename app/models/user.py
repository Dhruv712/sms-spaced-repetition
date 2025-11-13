from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Make optional for Google users
    google_id = Column(String(255), unique=True, index=True, nullable=True)  # Google OAuth ID
    phone_number = Column(String(20), unique=True, index=True, nullable=True)  # Make optional for Google users
    name = Column(String(100))
    study_mode = Column(String(20), default="batch")  # 'batch' or 'distributed'
    preferred_start_hour = Column(Integer, default=9)  # 24-hour format
    preferred_end_hour = Column(Integer, default=21)
    timezone = Column(String(50), default="UTC")
    is_active = Column(Boolean, default=True)
    sms_opt_in = Column(Boolean, default=False)  # SMS opt-in preference
    current_streak_days = Column(Integer, default=0)  # Current consecutive days with reviews
    longest_streak_days = Column(Integer, default=0)  # Longest streak achieved
    last_study_date = Column(DateTime(timezone=True), nullable=True)  # Last date user studied
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    flashcards = relationship("Flashcard", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("CardReview", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("StudySession", back_populates="user", cascade="all, delete-orphan")
    conversation_state = relationship("ConversationState", back_populates="user", uselist=False, cascade="all, delete-orphan")
    decks = relationship("Deck", back_populates="user", cascade="all, delete-orphan")
    deck_sms_settings = relationship("UserDeckSmsSettings", back_populates="user", cascade="all, delete-orphan")