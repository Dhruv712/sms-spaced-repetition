"""
Premium service for checking limits and premium status
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timezone, timedelta
from app.models import User, CardReview, Deck, Flashcard


def get_sms_reviews_this_month(user_id: int, db: Session) -> int:
    """
    Get the number of SMS reviews the user has done this month
    """
    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    count = db.query(CardReview).filter(
        and_(
            CardReview.user_id == user_id,
            CardReview.is_sms_review == True,
            CardReview.created_at >= start_of_month
        )
    ).count()
    
    return count


def get_deck_count(user_id: int, db: Session) -> int:
    """
    Get the number of decks the user has
    """
    return db.query(Deck).filter(Deck.user_id == user_id).count()


def get_flashcard_count_in_deck(deck_id: int, db: Session) -> int:
    """
    Get the number of flashcards in a deck
    """
    return db.query(Flashcard).filter(Flashcard.deck_id == deck_id).count()


def check_sms_limit(user: User, db: Session) -> dict:
    """
    Check if user has reached SMS review limit
    Returns: {
        "within_limit": bool,
        "count": int,
        "limit": int,
        "remaining": int
    }
    """
    if user.is_premium:
        return {
            "within_limit": True,
            "count": 0,
            "limit": float('inf'),
            "remaining": float('inf')
        }
    
    count = get_sms_reviews_this_month(user.id, db)
    limit = 50
    remaining = max(0, limit - count)
    
    return {
        "within_limit": count < limit,
        "count": count,
        "limit": limit,
        "remaining": remaining
    }


def check_deck_limit(user: User, db: Session) -> dict:
    """
    Check if user can create more decks
    Returns: {
        "can_create": bool,
        "count": int,
        "limit": int,
        "remaining": int
    }
    """
    if user.is_premium:
        return {
            "can_create": True,
            "count": 0,
            "limit": float('inf'),
            "remaining": float('inf')
        }
    
    count = get_deck_count(user.id, db)
    limit = 3
    remaining = max(0, limit - count)
    
    return {
        "can_create": count < limit,
        "count": count,
        "limit": limit,
        "remaining": remaining
    }


def check_flashcard_limit_in_deck(deck_id: int, user: User, db: Session) -> dict:
    """
    Check if user can add more flashcards to a deck
    Returns: {
        "can_add": bool,
        "count": int,
        "limit": int,
        "remaining": int
    }
    """
    if user.is_premium:
        return {
            "can_add": True,
            "count": 0,
            "limit": float('inf'),
            "remaining": float('inf')
        }
    
    count = get_flashcard_count_in_deck(deck_id, db)
    limit = 20
    remaining = max(0, limit - count)
    
    return {
        "can_add": count < limit,
        "count": count,
        "limit": limit,
        "remaining": remaining
    }


def check_premium_status(user: User) -> bool:
    """
    Check if user has premium status
    """
    return user.is_premium or False

