from celery import Celery

celery_app = Celery("sms_spaced_repetition", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

celery_app.autodiscover_tasks(["app.services"])
