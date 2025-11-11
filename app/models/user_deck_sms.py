from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class UserDeckSmsSettings(Base):
    """
    Tracks which decks are enabled for SMS per user.
    If a deck is not in this table for a user, it's considered muted (SMS disabled).
    """
    __tablename__ = "user_deck_sms_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    deck_id = Column(Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    sms_enabled = Column(Boolean, default=True, nullable=False)  # True = SMS enabled, False = muted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Ensure one record per user-deck combination
    __table_args__ = (
        UniqueConstraint('user_id', 'deck_id', name='uq_user_deck_sms'),
    )
    
    # Relationships
    user = relationship("User", back_populates="deck_sms_settings")
    deck = relationship("Deck", back_populates="user_sms_settings")

