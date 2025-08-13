from celery import Celery
from celery.schedules import crontab
from app.utils.config import settings

# Use Railway Redis URL if available, otherwise fallback to local
redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')

celery_app = Celery(
    "sms_spaced_repetition", 
    broker=redis_url, 
    backend=redis_url
)

celery_app.autodiscover_tasks(["app.services"])

# Configure Celery to run tasks synchronously in development
if getattr(settings, 'ENVIRONMENT', 'development') == 'development':
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )

# Configure Celery Beat schedule for automated tasks
celery_app.conf.beat_schedule = {
    'send-due-flashcards': {
        'task': 'app.services.scheduler_service.scheduled_flashcard_task',
        'schedule': crontab(minute=0, hour='9,12,15,18,21'),  # Send at 9am, 12pm, 3pm, 6pm, 9pm
    },
    'cleanup-conversation-states': {
        'task': 'app.services.scheduler_service.cleanup_conversation_states_task',
        'schedule': crontab(minute=0, hour='*/2'),  # Clean up every 2 hours
    },
}
