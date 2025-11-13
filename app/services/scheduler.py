from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo  # For Python 3.9+
from typing import Tuple
# If you're using <3.9, use: from pytz import timezone

def compute_sm2_next_review(
    repetition_count: int,
    ease_factor: float,
    interval_days: int,
    was_correct: bool,
    confidence_score: float
) -> Tuple[int, float, int]:
    """
    Compute next review using SuperMemo 2 algorithm
    
    Args:
        repetition_count: Current number of successful repetitions
        ease_factor: Current ease factor (starts at 2.5)
        interval_days: Current interval in days
        was_correct: Whether the answer was correct
        confidence_score: LLM confidence score (0-1)
    
    Returns:
        Tuple of (new_repetition_count, new_ease_factor, new_interval_days)
    """
    
    # Convert confidence score to SM-2 quality (0-5 scale)
    # 0-0.3: 0 (complete blackout)
    # 0.3-0.5: 1 (incorrect response)
    # 0.5-0.7: 2 (hard response)
    # 0.7-0.8: 3 (correct response)
    # 0.8-0.9: 4 (easy response)
    # 0.9-1.0: 5 (perfect response)
    
    if confidence_score < 0.3:
        quality = 0
    elif confidence_score < 0.5:
        quality = 1
    elif confidence_score < 0.7:
        quality = 2
    elif confidence_score < 0.8:
        quality = 3
    elif confidence_score < 0.9:
        quality = 4
    else:
        quality = 5
    
    # If answer was incorrect, quality is 0
    if not was_correct:
        quality = 0
    
    # SM-2 Algorithm
    if quality < 3:
        # Incorrect response - reset repetition count
        new_repetition_count = 0
        new_interval_days = 1
    else:
        # Correct response
        new_repetition_count = repetition_count + 1
        
        if new_repetition_count == 1:
            new_interval_days = 1
        elif new_repetition_count == 2:
            new_interval_days = 6
        else:
            new_interval_days = int(interval_days * ease_factor)
    
    # Update ease factor
    new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    
    # Ensure ease factor doesn't go below 1.3
    new_ease_factor = max(1.3, new_ease_factor)
    
    return new_repetition_count, new_ease_factor, new_interval_days

def compute_next_review(
    last_review_date: datetime,
    was_correct: bool,
    confidence_score: float,
    start_hour: int,
    end_hour: int,
    timezone_str: str,
    repetition_count: int = 0,
    ease_factor: float = 2.5,
    interval_days: int = 0
) -> datetime:
    """
    Compute next review date using SM-2 algorithm with timezone adjustments
    """
    
    # Step 1: Compute SM-2 interval
    new_repetition_count, new_ease_factor, new_interval_days = compute_sm2_next_review(
        repetition_count, ease_factor, interval_days, was_correct, confidence_score
    )
    
    # Step 2: Adjust interval based on confidence score gradient
    # Higher confidence = longer interval, lower confidence = shorter interval
    # This provides more granular control than just was_correct boolean
    if was_correct and confidence_score >= 0.9:
        # Perfect answer - extend interval by 20%
        new_interval_days = int(new_interval_days * 1.2)
    elif was_correct and confidence_score >= 0.8:
        # Very good answer - extend interval by 10%
        new_interval_days = int(new_interval_days * 1.1)
    elif was_correct and confidence_score < 0.7:
        # Correct but low confidence - reduce interval by 10%
        new_interval_days = max(1, int(new_interval_days * 0.9))
    elif not was_correct:
        # Incorrect - already handled in SM-2, but ensure minimum interval
        new_interval_days = max(1, new_interval_days)
    
    # Step 3: Compute naive next review time
    interval = timedelta(days=new_interval_days)
    naive_next_review = last_review_date + interval

    # Step 4: Convert to user's timezone
    user_tz = ZoneInfo(timezone_str)
    local_next_review = naive_next_review.astimezone(user_tz)

    # Step 5: Adjust time to be within preferred review window
    if not (start_hour <= local_next_review.hour < end_hour):
        # Set to *next day's* preferred start time
        next_day = local_next_review.date() + timedelta(days=1)
        local_next_review = datetime.combine(next_day, time(hour=start_hour), tzinfo=user_tz)

    # Step 6: Convert back to UTC
    return local_next_review.astimezone(ZoneInfo("UTC"))
