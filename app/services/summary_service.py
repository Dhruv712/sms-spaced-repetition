from sqlalchemy.orm import Session
from app.models import User, CardReview, Flashcard
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
from sqlalchemy import func, and_

def get_daily_review_summary(user_id: int, db: Session, date: datetime = None) -> Dict[str, Any]:
    """
    Generate a daily summary of flashcard reviews for a user
    
    Args:
        user_id: User ID to get summary for
        db: Database session
        date: Date to get summary for (defaults to today)
    
    Returns:
        Dictionary with summary statistics
    """
    if date is None:
        date = datetime.now(timezone.utc).date()
    
    # Get start and end of the specified date
    start_of_day = datetime.combine(date, datetime.min.time(), tzinfo=timezone.utc)
    end_of_day = datetime.combine(date, datetime.max.time(), tzinfo=timezone.utc)
    
    # Get all reviews for the user on this date
    reviews = db.query(CardReview).filter(
        and_(
            CardReview.user_id == user_id,
            CardReview.review_date >= start_of_day,
            CardReview.review_date <= end_of_day
        )
    ).all()
    
    if not reviews:
        return {
            "date": date.strftime("%Y-%m-%d"),
            "total_reviews": 0,
            "correct_reviews": 0,
            "percent_correct": 0.0,
            "problem_areas": [],
            "streak_days": 0,
            "next_due_cards": 0,
            "message": "No reviews today. Time to start studying!"
        }
    
    # Calculate basic stats - count unique flashcards reviewed
    unique_flashcards_reviewed = set(review.flashcard_id for review in reviews)
    total_reviews = len(unique_flashcards_reviewed)
    
    # For correctness, count the most recent review for each flashcard
    correct_reviews = 0
    for flashcard_id in unique_flashcards_reviewed:
        # Get the most recent review for this flashcard today
        latest_review = max([r for r in reviews if r.flashcard_id == flashcard_id], 
                           key=lambda r: r.review_date)
        if latest_review.was_correct:
            correct_reviews += 1
    
    percent_correct = (correct_reviews / total_reviews) * 100 if total_reviews > 0 else 0
    
    # Get problem areas (cards with low confidence scores)
    problem_areas = []
    
    for flashcard_id in unique_flashcards_reviewed:
        # Get the most recent review for this flashcard today
        latest_review = max([r for r in reviews if r.flashcard_id == flashcard_id], 
                           key=lambda r: r.review_date)
        
        if latest_review.confidence_score < 0.7:
            flashcard = db.query(Flashcard).filter_by(id=flashcard_id).first()
            if flashcard:
                problem_areas.append({
                    "concept": flashcard.concept,
                    "confidence_score": latest_review.confidence_score,
                    "user_response": latest_review.user_response
                })
    
    # Sort by confidence score (lowest first) and take top 5
    problem_areas.sort(key=lambda x: x["confidence_score"])
    problem_areas = problem_areas[:5]
    
    # Calculate streak (consecutive days with reviews)
    streak_days = calculate_streak_days(user_id, db)
    
    # Count next due cards
    next_due_cards = count_next_due_cards(user_id, db)
    
    # Generate personalized message
    message = generate_summary_message(total_reviews, percent_correct, streak_days, problem_areas)
    
    return {
        "date": date.strftime("%Y-%m-%d"),
        "total_reviews": total_reviews,
        "correct_reviews": correct_reviews,
        "percent_correct": round(percent_correct, 1),
        "problem_areas": problem_areas,
        "streak_days": streak_days,
        "next_due_cards": next_due_cards,
        "message": message
    }

def calculate_streak_days(user_id: int, db: Session) -> int:
    """Calculate consecutive days with reviews or no cards due"""
    today = datetime.now(timezone.utc).date()
    streak = 0
    
    for days_back in range(30):  # Check last 30 days
        check_date = today - timedelta(days=days_back)
        start_of_day = datetime.combine(check_date, datetime.min.time(), tzinfo=timezone.utc)
        end_of_day = datetime.combine(check_date, datetime.max.time(), tzinfo=timezone.utc)
        
        # Check if user reviewed cards on this day
        reviews = db.query(CardReview).filter(
            and_(
                CardReview.user_id == user_id,
                CardReview.review_date >= start_of_day,
                CardReview.review_date <= end_of_day
            )
        ).count()
        
        if reviews > 0:
            # User reviewed cards - streak continues
            streak += 1
        else:
            # No reviews on this day - check if there were cards due
            cards_due_that_day = count_cards_due_on_date(user_id, db, check_date)
            
            if cards_due_that_day == 0:
                # No cards due - streak continues (user couldn't review)
                streak += 1
            else:
                # Cards were due but user didn't review - streak breaks
                break
    
    return streak

def count_cards_due_on_date(user_id: int, db: Session, date: datetime.date) -> int:
    """Count how many cards were due on a specific date"""
    # This is a simplified version - in reality, we'd need to check the scheduling logic
    # For now, let's check if there are any flashcards that could have been due
    
    # Get all user's flashcards
    total_flashcards = db.query(Flashcard).filter(Flashcard.user_id == user_id).count()
    
    if total_flashcards == 0:
        return 0
    
    # Check if there are any reviews before this date
    start_of_day = datetime.combine(date, datetime.min.time(), tzinfo=timezone.utc)
    
    reviews_before_date = db.query(CardReview).filter(
        and_(
            CardReview.user_id == user_id,
            CardReview.review_date < start_of_day
        )
    ).count()
    
    # If user has flashcards but no reviews before this date, 
    # then all cards would have been due on this date
    if reviews_before_date == 0:
        return total_flashcards
    
    # For now, return a reasonable estimate
    # In a full implementation, we'd calculate based on the actual scheduling algorithm
    return min(total_flashcards, 5)  # Assume max 5 cards due per day

def count_next_due_cards(user_id: int, db: Session) -> int:
    """Count cards due for review"""
    now = datetime.now(timezone.utc)
    
    # Get unique flashcards that are due (next_review_date <= now)
    # Use the same logic as get_next_due_flashcard but count all due cards
    subquery = db.query(CardReview.flashcard_id).filter(
        and_(
            CardReview.user_id == user_id,
            CardReview.next_review_date > now
        )
    ).subquery()

    # Count flashcards that are NOT in the subquery (i.e., are due)
    due_cards = db.query(Flashcard).filter(
        and_(
            Flashcard.user_id == user_id,
            ~Flashcard.id.in_(subquery)
        )
    ).count()
    
    return due_cards

def generate_summary_message(total_reviews: int, percent_correct: float, streak_days: int, problem_areas: List[Dict]) -> str:
    """Generate a personalized summary message"""
    
    if total_reviews == 0:
        return "No reviews today. Time to start studying!"
    
    # Base message
    if percent_correct >= 90:
        performance = "Excellent work today! 🎉"
    elif percent_correct >= 80:
        performance = "Great job! Keep it up! 👍"
    elif percent_correct >= 70:
        performance = "Good progress! You're improving! 📈"
    else:
        performance = "Keep practicing! You'll get better! 💪"
    
    # Streak message
    if streak_days >= 7:
        streak_msg = f"🔥 Amazing {streak_days}-day streak!"
    elif streak_days >= 3:
        streak_msg = f"🔥 {streak_days}-day streak! Keep it going!"
    elif streak_days > 1:
        streak_msg = f"🔥 {streak_days}-day streak!"
    else:
        streak_msg = "Start building your streak tomorrow!"
    
    # Problem areas message
    if problem_areas:
        problem_msg = f"\n\nAreas to focus on: {', '.join([area['concept'] for area in problem_areas[:3]])}"
    else:
        problem_msg = "\n\nNo problem areas today - you're crushing it!"
    
    return f"{performance}\n\n📊 Today's Stats:\n• {total_reviews} cards reviewed\n• {percent_correct}% correct\n\n{streak_msg}{problem_msg}"

def send_daily_summary_to_user(user: User, db: Session) -> Dict[str, Any]:
    """Send daily summary to a specific user"""
    try:
        from app.services.loop_message_service import LoopMessageService
        
        # Get summary
        summary = get_daily_review_summary(user.id, db)
        
        # Format message for SMS
        message = format_summary_for_sms(summary)
        
        # Send via LoopMessage
        service = LoopMessageService()
        if service:
            result = service.send_feedback(user.phone_number, message)
            return {
                "success": True,
                "user_id": user.id,
                "phone": user.phone_number,
                "summary": summary,
                "message_sent": result.get("success", False)
            }
        else:
            return {
                "success": False,
                "user_id": user.id,
                "phone": user.phone_number,
                "error": "LoopMessage service not available"
            }
            
    except Exception as e:
        return {
            "success": False,
            "user_id": user.id,
            "phone": user.phone_number,
            "error": str(e)
        }

def format_summary_for_sms(summary: Dict[str, Any]) -> str:
    """Format summary data for SMS message"""
    
    if summary["total_reviews"] == 0:
        return "📚 Daily Summary\n\nNo reviews today.\n\nTime to start studying! Send 'Yes' to begin a review session."
    
    message = f"📚 Daily Summary - {summary['date']}\n\n"
    message += f"📊 {summary['total_reviews']} cards reviewed\n"
    message += f"✅ {summary['correct_reviews']} correct ({summary['percent_correct']}%)\n"
    message += f"🔥 {summary['streak_days']}-day streak\n"
    message += f"📅 {summary['next_due_cards']} cards due tomorrow\n\n"
    
    message += summary["message"]
    
    if summary["problem_areas"]:
        message += "\n\nFocus on: " + ", ".join([area["concept"] for area in summary["problem_areas"][:3]])
    
    return message
