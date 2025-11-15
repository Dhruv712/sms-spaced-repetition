from sqlalchemy.orm import Session
from app.models import User, CardReview, Flashcard
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
from sqlalchemy import func, and_
from openai import OpenAI
from app.utils.config import settings

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
            "study_analysis": None,
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
    
    # Generate GPT analysis of areas to study hardest
    study_analysis = generate_study_analysis(reviews, db)
    
    # Calculate streak (consecutive days with reviews)
    streak_days = calculate_streak_days(user_id, db)
    
    # Count next due cards
    next_due_cards = count_next_due_cards(user_id, db)
    
    # Generate personalized message
    message = generate_summary_message(total_reviews, percent_correct, streak_days, [])
    
    return {
        "date": date.strftime("%Y-%m-%d"),
        "total_reviews": total_reviews,
        "correct_reviews": correct_reviews,
        "percent_correct": round(percent_correct, 1),
        "study_analysis": study_analysis,
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

def generate_study_analysis(reviews: List[CardReview], db: Session) -> str | None:
    """
    Generate a 1-2 sentence GPT analysis of areas the user needs to study hardest
    """
    if not reviews or not settings.OPENAI_API_KEY:
        return None
    
    try:
        # Get flashcards that were answered incorrectly or with low confidence
        problem_flashcards = []
        for review in reviews:
            if not review.was_correct or (review.confidence_score and review.confidence_score < 0.7):
                flashcard = db.query(Flashcard).filter_by(id=review.flashcard_id).first()
                if flashcard:
                    problem_flashcards.append({
                        "concept": flashcard.concept,
                        "tags": flashcard.tags if flashcard.tags else "",
                        "was_correct": review.was_correct,
                        "confidence": review.confidence_score
                    })
        
        if not problem_flashcards:
            return None
        
        # Group by tags/decks to identify patterns
        tag_issues = {}
        for card in problem_flashcards[:10]:  # Limit to top 10 for context
            tags = card["tags"].split(",") if card["tags"] else []
            for tag in tags:
                tag = tag.strip()
                if tag:
                    if tag not in tag_issues:
                        tag_issues[tag] = 0
                    tag_issues[tag] += 1
        
        # Prepare context for GPT
        problem_concepts = [card["concept"] for card in problem_flashcards[:5]]
        top_tags = sorted(tag_issues.items(), key=lambda x: x[1], reverse=True)[:3]
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Build a more specific context with actual concepts that were wrong
        concepts_list = ', '.join([f'"{c}"' for c in problem_concepts[:5]])
        tags_list = ', '.join([tag for tag, _ in top_tags]) if top_tags else 'None'
        
        prompt = f"""Based on the user's actual flashcard review performance, generate a brief, concise analysis (1 sentence max, ideally 10-15 words).

ACTUAL concepts they got wrong: {concepts_list}
Tags (if any): {tags_list}

CRITICAL RULES:
1. Be extremely concise - maximum 1 sentence, ideally 10-15 words
2. Only mention concepts/topics that actually appear in the list above - DO NOT make up or infer additional details
3. Do NOT add explanations about "interactions" or "relationships" unless explicitly stated in the concepts
4. Focus on the specific topics/concepts listed, not general patterns
5. If tags are provided, you can mention the tag category, but keep it brief

Examples of good responses:
- "Review reinforcement learning concepts, especially policy and value functions."
- "Focus on neuroscience topics you missed today."
- "Review the specific concepts you got wrong today."

Response (just the analysis, no quotes, no formatting, maximum 1 sentence):"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower temperature for more grounded responses
            max_tokens=50  # Reduced token limit to force conciseness
        )
        
        analysis = response.choices[0].message.content.strip()
        # Remove quotes if present
        if analysis.startswith('"') and analysis.endswith('"'):
            analysis = analysis[1:-1]
        if analysis.startswith("'") and analysis.endswith("'"):
            analysis = analysis[1:-1]
        
        return analysis if analysis else None
        
    except Exception as e:
        print(f"Error generating study analysis: {e}")
        return None

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
    
    return f"{performance}\n\n📊 Today's Stats:\n• {total_reviews} cards reviewed\n• {percent_correct}% correct\n\n{streak_msg}"

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
    
    if summary.get("study_analysis"):
        message += f"\n\n📝 {summary['study_analysis']}"
    
    return message
