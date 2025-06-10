from twilio.rest import Client
from app.utils.config import settings

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def send_sms(to_number: str, message: str):
    return client.messages.create(
        to=to_number,
        from_=settings.TWILIO_PHONE_NUMBER,
        body=message
    )
