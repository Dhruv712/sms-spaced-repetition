from app.utils.celery_app import celery_app
from app.utils.config import settings
from twilio.rest import Client

@celery_app.task
def send_study_reminder(phone_number: str):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    message = client.messages.create(
        body="You're all caught up! I'll send you flashcards automatically when they're due.",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )

    print(f"✅ Reminder sent to {phone_number}. SID: {message.sid}")
