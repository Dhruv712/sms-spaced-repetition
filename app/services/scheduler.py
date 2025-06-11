from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo  # For Python 3.9+
# If you're using <3.9, use: from pytz import timezone

def compute_next_review(
    last_review_date: datetime,
    was_correct: bool,
    confidence_score: float,
    start_hour: int,
    end_hour: int,
    timezone_str: str
) -> datetime:
    # Step 1: Determine the base interval
    if not was_correct:
        interval = timedelta(days=1)
    elif confidence_score > 0.9:
        interval = timedelta(days=7)
    elif confidence_score > 0.7:
        interval = timedelta(days=3)
    else:
        interval = timedelta(days=2)

    # Step 2: Compute naive next review time
    naive_next_review = last_review_date + interval

    # Step 3: Convert to user's timezone
    user_tz = ZoneInfo(timezone_str)
    local_next_review = naive_next_review.astimezone(user_tz)

    # Step 4: Adjust time to be within preferred review window
    if not (start_hour <= local_next_review.hour < end_hour):
        # Set to *next day’s* preferred start time
        next_day = local_next_review.date() + timedelta(days=1)
        local_next_review = datetime.combine(next_day, time(hour=start_hour), tzinfo=user_tz)

    # Step 5: Convert back to UTC
    return local_next_review.astimezone(ZoneInfo("UTC"))
