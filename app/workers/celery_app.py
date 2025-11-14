# Sets up the app with broker and backend.

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "notification_workers",
    broker=settings.RABBITMQ_BROKER_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"]
)

# Configure retries with exponential backoff
celery_app.conf.task_default_retry_delay = 10
celery_app.conf.task_max_retries = 3
celery_app.conf.task_retry_backoff = True