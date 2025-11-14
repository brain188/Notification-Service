# Asynchronous notification sending with retries.

from app.workers.celery_app import celery_app
from app.services.email import send_email
from app.services.sms import send_sms
from app.services.push import send_push
from app.db.session import SessionLocal
from app.repositories.notification_repo import NotificationRepo
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
async def send_notification(self, notification_data: dict):
    channel = notification_data["channel"]
    recipient = notification_data["recipient"]
    content = notification_data["content"]
    event_type = notification_data["event_type"]
    
    success = False
    async with SessionLocal() as db:
        try:
            if channel == "email":
                success = await send_email(recipient, content)
            elif channel == "sms":
                success = await send_sms(recipient, content)
            elif channel == "push":
                success = await send_push(recipient, content)
            else:
                raise ValueError("Invalid channel")
            
            status = "sent" if success else "failed"
            await NotificationRepo.update_status(db, event_type, status)
            logger.info(f"Notification {event_type} {status}")
        except Exception as exc:
            logger.error(f"Task failed: {str(exc)}")
            # Update attempts
            report = await NotificationRepo.get_by_event_id(db, event_type)
            if report:
                report.attempts += 1
                await db.commit()
            raise self.retry(exc=exc)  # Retry with backoff