from app.database import SessionLocal
from app.models import User
from app.services.reminder import send_study_reminder

def enqueue_reminders():
    db = SessionLocal()
    users = db.query(User).filter(User.is_active == True).all()
    for user in users:
        send_study_reminder.delay(user.phone_number)
    db.close()

if __name__ == "__main__":
    enqueue_reminders()
