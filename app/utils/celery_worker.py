from celery import Celery
from app.utils.config import settings

# 🔥 This ensures the task is registered at runtime
import app.services.reminder

celery_app = Celery(
    "sms_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.timezone = "UTC"
celery_app.autodiscover_tasks(["app.services"])
