#Endpoints to trigger events, get reports, and handle webhooks.

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.schemas.notification import NotificationCreate, NotificationReport
from app.workers.tasks import send_notification
from app.repositories.notification_repo import NotificationRepo
from app.db.session import AsyncSession, get_db
from slowapi import Limiter
from slowapi.util import get_remote_address
from jose import JWTError, jwt
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])

limiter = Limiter(key_func=get_remote_address)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # Placeholder; implement auth properly

# Dependency for JWT auth
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

class WebhookPayload(BaseModel):
    event_id: str
    status: str  

@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("10/minute")  # Rate limit to prevent abuse
async def trigger_notification(notification: NotificationCreate, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    logger.info(f"Triggering notification for event: {notification.event_type}")
    try:
        # Enqueue task via Celery
        send_notification.delay(notification.dict())
        # Log to DB
        await NotificationRepo.create(db, notification)
        return {"message": "Notification queued"}
    except Exception as e:
        logger.error(f"Error triggering notification: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal error")

@router.get("/reports/{event_id}", response_model=NotificationReport)
async def get_report(event_id: str, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    logger.info(f"Fetching report for event_id: {event_id}")
    report = await NotificationRepo.get_by_event_id(db, event_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.post("/webhook")
async def handle_webhook(payload: WebhookPayload, db: AsyncSession = Depends(get_db)):
    logger.info(f"Webhook received for event_id: {payload.event_id}, status: {payload.status}")
    await NotificationRepo.update_status(db, payload.event_id, payload.status)
    return {"message": "Status updated"}