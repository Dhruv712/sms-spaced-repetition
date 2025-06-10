from datetime import datetime, timedelta

def compute_next_review(last_review_date: datetime, was_correct: bool, confidence_score: float):
    if not was_correct:
        return last_review_date + timedelta(days=1)

    # Scale interval based on confidence
    if confidence_score > 0.9:
        return last_review_date + timedelta(days=7)
    elif confidence_score > 0.7:
        return last_review_date + timedelta(days=3)
    else:
        return last_review_date + timedelta(days=2)
