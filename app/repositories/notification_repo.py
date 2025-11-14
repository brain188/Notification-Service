# Async DB operations for notifications

from app.models.notifications import Notification
from app.schemas.notification import NotificationCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging

logger = logging.getLogger(__name__)

class NotificationRepo:
    @staticmethod
    async def create(db: AsyncSession, notification: NotificationCreate):
        db_notification = Notification(**notification.model_dump())
        db.add(db_notification)
        await db.commit()
        await db.refresh(db_notification)
        logger.info(f"Created notification ID: {db_notification.id}")
        return db_notification
    
    @staticmethod
    async def get_by_event_id(db: AsyncSession, event_id: str):
        result = await db.execute(select(Notification).where(Notification.event_type == event_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_status(db: AsyncSession, event_id: str, status: str ):
        result = await db.execute(select(Notification).where(Notification.event_type == event_id))
        notification = result.scalar_one_or_none()
        if notification:
            notification.status = status
            await db.commit()
            logger.info(f"Updated status for event_id: {event_id} to {status}")
               