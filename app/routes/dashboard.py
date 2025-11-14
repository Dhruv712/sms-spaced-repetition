"""
Dashboard routes for analytics and statistics
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, cast, Integer
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from app.database import get_db
from app.models import User, CardReview, Flashcard, Deck
from app.services.auth import get_current_active_user

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard statistics including:
    - Activity heatmap data (reviews per day for the past year)
    - Accuracy over time (overall and per-deck)
    - Current streak
    - Weakest areas (tags/decks with lowest accuracy)
    """
    today = datetime.now(timezone.utc).date()
    one_year_ago = today - timedelta(days=365)
    
    # Activity heatmap data - reviews per day for past year
    activity_data = db.query(
        func.date(CardReview.review_date).label('date'),
        func.count(CardReview.id).label('count')
    ).filter(
        CardReview.user_id == current_user.id,
        func.date(CardReview.review_date) >= one_year_ago
    ).group_by(
        func.date(CardReview.review_date)
    ).all()
    
    # Convert to dict for easier frontend consumption
    activity_map = {str(row.date): row.count for row in activity_data}
    
    # Generate all dates in range for heatmap
    all_dates = {}
    current_date = one_year_ago
    while current_date <= today:
        date_str = current_date.isoformat()
        all_dates[date_str] = activity_map.get(date_str, 0)
        current_date += timedelta(days=1)
    
    # Accuracy over time - overall
    accuracy_data = db.query(
        func.date(CardReview.review_date).label('date'),
        func.avg(
            case(
                (CardReview.was_correct == True, 100),
                else_=0
            )
        ).label('accuracy'),
        func.count(CardReview.id).label('cards_reviewed')
    ).filter(
        CardReview.user_id == current_user.id,
        func.date(CardReview.review_date) >= one_year_ago
    ).group_by(
        func.date(CardReview.review_date)
    ).order_by(
        func.date(CardReview.review_date)
    ).all()
    
    accuracy_points = [
        {
            'date': row.date.isoformat(),
            'accuracy': float(row.accuracy) if row.accuracy else 0,
            'cards_reviewed': row.cards_reviewed
        }
        for row in accuracy_data
    ]
    
    # Accuracy per deck
    deck_accuracy = db.query(
        Deck.id,
        Deck.name,
        func.date(CardReview.review_date).label('date'),
        func.avg(
            case(
                (CardReview.was_correct == True, 100),
                else_=0
            )
        ).label('accuracy'),
        func.count(CardReview.id).label('cards_reviewed')
    ).join(
        Flashcard, Flashcard.deck_id == Deck.id
    ).join(
        CardReview, CardReview.flashcard_id == Flashcard.id
    ).filter(
        CardReview.user_id == current_user.id,
        func.date(CardReview.review_date) >= one_year_ago
    ).group_by(
        Deck.id,
        Deck.name,
        func.date(CardReview.review_date)
    ).order_by(
        func.date(CardReview.review_date)
    ).all()
    
    # Group by deck
    deck_accuracy_map: Dict[int, List[Dict[str, Any]]] = {}
    for row in deck_accuracy:
        if row.id not in deck_accuracy_map:
            deck_accuracy_map[row.id] = {
                'deck_id': row.id,
                'deck_name': row.name,
                'data_points': []
            }
        deck_accuracy_map[row.id]['data_points'].append({
            'date': row.date.isoformat(),
            'accuracy': float(row.accuracy) if row.accuracy else 0,
            'cards_reviewed': row.cards_reviewed
        })
    
    # Current streak
    streak_days = current_user.current_streak_days or 0
    longest_streak = current_user.longest_streak_days or 0
    
    # Weakest areas - tags with lowest accuracy
    tag_accuracy = db.query(
        Flashcard.tags,
        func.avg(
            case(
                (CardReview.was_correct == True, 100),
                else_=0
            )
        ).label('accuracy'),
        func.count(CardReview.id).label('review_count')
    ).join(
        CardReview, CardReview.flashcard_id == Flashcard.id
    ).filter(
        CardReview.user_id == current_user.id,
        Flashcard.tags.isnot(None),
        Flashcard.tags != ''
    ).group_by(
        Flashcard.tags
    ).having(
        func.count(CardReview.id) >= 5  # Only show tags with at least 5 reviews
    ).order_by(
        func.avg(
            func.case(
                (CardReview.was_correct == True, 100),
                else_=0
            )
        ).asc()
    ).limit(10).all()
    
    weakest_tags = [
        {
            'tag': row.tags,
            'accuracy': float(row.accuracy) if row.accuracy else 0,
            'review_count': row.review_count
        }
        for row in tag_accuracy
    ]
    
    # Weakest decks
    deck_weakest = db.query(
        Deck.id,
        Deck.name,
        func.avg(
            case(
                (CardReview.was_correct == True, 100),
                else_=0
            )
        ).label('accuracy'),
        func.count(CardReview.id).label('review_count')
    ).join(
        Flashcard, Flashcard.deck_id == Deck.id
    ).join(
        CardReview, CardReview.flashcard_id == Flashcard.id
    ).filter(
        CardReview.user_id == current_user.id,
        Deck.user_id == current_user.id
    ).group_by(
        Deck.id,
        Deck.name
    ).having(
        func.count(CardReview.id) >= 5
    ).order_by(
        func.avg(
            func.case(
                (CardReview.was_correct == True, 100),
                else_=0
            )
        ).asc()
    ).limit(10).all()
    
    weakest_decks = [
        {
            'deck_id': row.id,
            'deck_name': row.name,
            'accuracy': float(row.accuracy) if row.accuracy else 0,
            'review_count': row.review_count
        }
        for row in deck_weakest
    ]
    
    return {
        'activity_heatmap': all_dates,
        'accuracy_over_time': accuracy_points,
        'deck_accuracy': list(deck_accuracy_map.values()),
        'streak': {
            'current': streak_days,
            'longest': longest_streak
        },
        'weakest_areas': {
            'tags': weakest_tags,
            'decks': weakest_decks
        }
    }

