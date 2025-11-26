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
    
    # Get all flashcards for the user
    all_flashcards = db.query(Flashcard).filter(Flashcard.user_id == current_user.id).all()
    flashcard_ids = [card.id for card in all_flashcards]
    
    # Always calculate streak first, even if no flashcards
    from app.services.summary_service import calculate_streak_days, calculate_potential_streak
    potential_streak, has_reviewed_today = calculate_potential_streak(current_user.id, db)
    streak_days = calculate_streak_days(current_user.id, db)
    longest_streak = current_user.longest_streak_days or 0
    
    # Update user's current streak if it changed (only if they've reviewed today)
    if has_reviewed_today and streak_days != (current_user.current_streak_days or 0):
        current_user.current_streak_days = streak_days
        if streak_days > longest_streak:
            current_user.longest_streak_days = streak_days
            longest_streak = streak_days
        db.commit()
    
    if not flashcard_ids:
        return {
            'activity_heatmap': {},
            'accuracy_over_time': [],
            'deck_accuracy': [],
            'streak': {
                'current': streak_days,
                'potential': potential_streak,
                'has_reviewed_today': has_reviewed_today,
                'longest': longest_streak
            },
            'weakest_areas': {
                'tags': [],
                'decks': []
            }
        }
    
    # Get all reviews for the user's flashcards, ordered by date
    reviews = db.query(CardReview).filter(
        and_(
            CardReview.user_id == current_user.id,
            CardReview.flashcard_id.in_(flashcard_ids),
            CardReview.review_date >= datetime.combine(one_year_ago, datetime.min.time()).replace(tzinfo=timezone.utc)
        )
    ).order_by(CardReview.review_date.asc()).all()
    
    # Group reviews by date and calculate daily performance (same pattern as mastery graphs)
    daily_performance = {}
    for review in reviews:
        review_date = review.review_date.date()
        if review_date not in daily_performance:
            daily_performance[review_date] = {
                "total": 0,
                "correct": 0,
                "unique_cards": set()
            }
        
        daily_performance[review_date]["total"] += 1
        daily_performance[review_date]["unique_cards"].add(review.flashcard_id)
        if review.was_correct:
            daily_performance[review_date]["correct"] += 1
    
    # Activity heatmap - generate all dates in range
    all_dates = {}
    current_date = one_year_ago
    while current_date <= today:
        date_str = current_date.isoformat()
        if current_date in daily_performance:
            all_dates[date_str] = len(daily_performance[current_date]["unique_cards"])
        else:
            all_dates[date_str] = 0
        current_date += timedelta(days=1)
    
    # Accuracy over time - overall
    accuracy_points = []
    for date, stats in sorted(daily_performance.items()):
        accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        cards_reviewed = len(stats["unique_cards"])
        
        accuracy_points.append({
            'date': date.isoformat(),
            'accuracy': round(accuracy, 1),
            'cards_reviewed': cards_reviewed
        })
    
    # Accuracy per deck - group by deck
    deck_reviews: Dict[int, Dict[datetime.date, Dict[str, Any]]] = {}
    for review in reviews:
        flashcard = next((f for f in all_flashcards if f.id == review.flashcard_id), None)
        if not flashcard or not flashcard.deck_id:
            continue
        
        deck_id = flashcard.deck_id
        review_date = review.review_date.date()
        
        if deck_id not in deck_reviews:
            deck_reviews[deck_id] = {}
        
        if review_date not in deck_reviews[deck_id]:
            deck_reviews[deck_id][review_date] = {
                "total": 0,
                "correct": 0,
                "unique_cards": set()
            }
        
        deck_reviews[deck_id][review_date]["total"] += 1
        deck_reviews[deck_id][review_date]["unique_cards"].add(review.flashcard_id)
        if review.was_correct:
            deck_reviews[deck_id][review_date]["correct"] += 1
    
    # Convert deck reviews to data points
    deck_accuracy_map: Dict[int, Dict[str, Any]] = {}
    for deck_id, daily_stats in deck_reviews.items():
        deck = db.query(Deck).filter(Deck.id == deck_id).first()
        if not deck:
            continue
        
        data_points = []
        for date, stats in sorted(daily_stats.items()):
            accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            cards_reviewed = len(stats["unique_cards"])
            
            data_points.append({
                'date': date.isoformat(),
                'accuracy': round(accuracy, 1),
                'cards_reviewed': cards_reviewed
            })
        
        deck_accuracy_map[deck_id] = {
            'deck_id': deck_id,
            'deck_name': deck.name,
            'data_points': data_points
        }
    
    # Streak already calculated above, just use those values
    
    # Weakest areas - calculate from reviews we already fetched
    # Group by tags
    tag_stats: Dict[str, Dict[str, int]] = {}
    for review in reviews:
        flashcard = next((f for f in all_flashcards if f.id == review.flashcard_id), None)
        if not flashcard or not flashcard.tags:
            continue
        
        tag = flashcard.tags
        if tag not in tag_stats:
            tag_stats[tag] = {'total': 0, 'correct': 0}
        
        tag_stats[tag]['total'] += 1
        if review.was_correct:
            tag_stats[tag]['correct'] += 1
    
    # Calculate accuracy for each tag and filter by minimum reviews
    weakest_tags = []
    for tag, stats in tag_stats.items():
        if stats['total'] >= 5:  # Only show tags with at least 5 reviews
            accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            weakest_tags.append({
                'tag': tag,
                'accuracy': round(accuracy, 1),
                'review_count': stats['total']
            })
    
    # Sort by accuracy (lowest first) and limit to 10
    weakest_tags.sort(key=lambda x: x['accuracy'])
    weakest_tags = weakest_tags[:10]
    
    # Weakest decks - calculate from deck_reviews we already have
    weakest_decks = []
    for deck_id, daily_stats in deck_reviews.items():
        deck = db.query(Deck).filter(Deck.id == deck_id).first()
        if not deck:
            continue
        
        total_reviews = 0
        correct_reviews = 0
        for date_stats in daily_stats.values():
            total_reviews += date_stats['total']
            correct_reviews += date_stats['correct']
        
        if total_reviews >= 5:  # Only show decks with at least 5 reviews
            accuracy = (correct_reviews / total_reviews * 100) if total_reviews > 0 else 0
            weakest_decks.append({
                'deck_id': deck_id,
                'deck_name': deck.name,
                'accuracy': round(accuracy, 1),
                'review_count': total_reviews
            })
    
    # Sort by accuracy (lowest first) and limit to 10
    weakest_decks.sort(key=lambda x: x['accuracy'])
    weakest_decks = weakest_decks[:10]
    
    # Calculate comparison data (this week vs last week, this month vs last month)
    today = datetime.now(timezone.utc).date()
    
    # This week (Monday to Sunday)
    days_since_monday = today.weekday()
    this_week_start = today - timedelta(days=days_since_monday)
    this_week_end = today
    last_week_start = this_week_start - timedelta(days=7)
    last_week_end = this_week_start - timedelta(days=1)
    
    # This month
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    def count_reviews_in_range(start_date, end_date):
        """Count unique cards reviewed in date range"""
        count = 0
        current = start_date
        while current <= end_date:
            date_str = current.isoformat()
            if date_str in all_dates:
                count += all_dates[date_str]
            current += timedelta(days=1)
        return count
    
    this_week_count = count_reviews_in_range(this_week_start, this_week_end)
    last_week_count = count_reviews_in_range(last_week_start, last_week_end)
    this_month_count = count_reviews_in_range(this_month_start, today)
    last_month_count = count_reviews_in_range(last_month_start, last_month_end)
    
    # Calculate streak history (last 30 days)
    streak_history = []
    for days_back in range(30):
        check_date = today - timedelta(days=days_back)
        start_of_day = datetime.combine(check_date, datetime.min.time(), tzinfo=timezone.utc)
        end_of_day = datetime.combine(check_date, datetime.max.time(), tzinfo=timezone.utc)
        
        reviews = db.query(CardReview).filter(
            and_(
                CardReview.user_id == current_user.id,
                CardReview.flashcard_id.in_(flashcard_ids),
                CardReview.review_date >= start_of_day,
                CardReview.review_date <= end_of_day
            )
        ).count()
        
        streak_history.append({
            'date': check_date.isoformat(),
            'reviewed': reviews > 0
        })
    
    streak_history.reverse()  # Oldest to newest
    
    return {
        'activity_heatmap': all_dates,
        'accuracy_over_time': accuracy_points,
        'deck_accuracy': list(deck_accuracy_map.values()),
        'streak': {
            'current': streak_days,
            'potential': potential_streak,
            'has_reviewed_today': has_reviewed_today,
            'longest': longest_streak,
            'history': streak_history
        },
        'weakest_areas': {
            'tags': weakest_tags,
            'decks': weakest_decks
        },
        'comparisons': {
            'this_week': this_week_count,
            'last_week': last_week_count,
            'this_month': this_month_count,
            'last_month': last_month_count
        }
    }

@router.get("/difficult-cards")
def get_difficult_cards(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get top 5 most difficult cards based on user's accuracy
    Returns cards with lowest accuracy (at least 3 reviews to avoid noise)
    """
    # Get all flashcards for the user
    all_flashcards = db.query(Flashcard).filter(Flashcard.user_id == current_user.id).all()
    flashcard_ids = [card.id for card in all_flashcards]
    
    if not flashcard_ids:
        return {"difficult_cards": []}
    
    # Get all reviews for user's flashcards
    reviews = db.query(CardReview).filter(
        CardReview.user_id == current_user.id,
        CardReview.flashcard_id.in_(flashcard_ids)
    ).all()
    
    # Calculate accuracy per flashcard
    card_stats: Dict[int, Dict[str, Any]] = {}
    
    for review in reviews:
        flashcard_id = review.flashcard_id
        if flashcard_id not in card_stats:
            card_stats[flashcard_id] = {
                'total_reviews': 0,
                'correct_reviews': 0
            }
        
        card_stats[flashcard_id]['total_reviews'] += 1
        if review.was_correct:
            card_stats[flashcard_id]['correct_reviews'] += 1
    
    # Calculate accuracy and filter cards with at least 3 reviews
    difficult_cards = []
    for flashcard_id, stats in card_stats.items():
        if stats['total_reviews'] >= 3:  # Minimum 3 reviews to avoid noise
            accuracy = (stats['correct_reviews'] / stats['total_reviews'] * 100) if stats['total_reviews'] > 0 else 0
            
            # Find the flashcard
            flashcard = next((f for f in all_flashcards if f.id == flashcard_id), None)
            if flashcard:
                difficult_cards.append({
                    'flashcard_id': flashcard_id,
                    'concept': flashcard.concept,
                    'definition': flashcard.definition,
                    'accuracy': round(accuracy, 1),
                    'total_reviews': stats['total_reviews'],
                    'correct_reviews': stats['correct_reviews'],
                    'deck_id': flashcard.deck_id,
                    'deck_name': flashcard.deck.name if flashcard.deck else None
                })
    
    # Sort by accuracy (lowest first) and take top 5
    difficult_cards.sort(key=lambda x: x['accuracy'])
    difficult_cards = difficult_cards[:5]
    
    return {"difficult_cards": difficult_cards}

@router.get("/confusion-breakdown")
def get_confusion_breakdown(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get confusion breakdown - most common incorrect answers per flashcard
    Returns cards with their most frequently typed wrong answers
    """
    # Get all flashcards for the user
    all_flashcards = db.query(Flashcard).filter(Flashcard.user_id == current_user.id).all()
    flashcard_ids = [card.id for card in all_flashcards]
    
    if not flashcard_ids:
        return {"confusion_breakdown": []}
    
    # Get all incorrect reviews
    incorrect_reviews = db.query(CardReview).filter(
        CardReview.user_id == current_user.id,
        CardReview.flashcard_id.in_(flashcard_ids),
        CardReview.was_correct == False,
        CardReview.user_response.isnot(None)
    ).all()
    
    # Group incorrect answers by flashcard
    confusion_map: Dict[int, Dict[str, int]] = {}
    
    for review in incorrect_reviews:
        flashcard_id = review.flashcard_id
        # Normalize the response (lowercase, strip whitespace)
        normalized_response = review.user_response.strip().lower() if review.user_response else ""
        
        if not normalized_response:
            continue
        
        if flashcard_id not in confusion_map:
            confusion_map[flashcard_id] = {}
        
        if normalized_response not in confusion_map[flashcard_id]:
            confusion_map[flashcard_id][normalized_response] = 0
        
        confusion_map[flashcard_id][normalized_response] += 1
    
    # Build result with top incorrect answers per card
    confusion_breakdown = []
    for flashcard_id, wrong_answers in confusion_map.items():
        # Find the flashcard
        flashcard = next((f for f in all_flashcards if f.id == flashcard_id), None)
        if not flashcard:
            continue
        
        # Sort wrong answers by frequency and take top 5
        sorted_answers = sorted(
            wrong_answers.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        if sorted_answers:
            confusion_breakdown.append({
                'flashcard_id': flashcard_id,
                'concept': flashcard.concept,
                'definition': flashcard.definition,
                'deck_id': flashcard.deck_id,
                'deck_name': flashcard.deck.name if flashcard.deck else None,
                'incorrect_answers': [
                    {
                        'answer': answer,
                        'count': count
                    }
                    for answer, count in sorted_answers
                ],
                'total_incorrect': sum(wrong_answers.values())
            })
    
    # Sort by total incorrect count (most confused cards first)
    confusion_breakdown.sort(key=lambda x: x['total_incorrect'], reverse=True)
    confusion_breakdown = confusion_breakdown[:10]  # Top 10 most confused cards
    
    return {"confusion_breakdown": confusion_breakdown}

