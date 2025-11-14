# Integrates with Firebase for push notifications

import firebase_admin
from firebase_admin import credentials, messaging
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase
cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

async def send_push(device_id: str, content: str):
    message = messaging.Message(
        notification=messaging.Notification(
            title="Notification",
            body=content
        ),
        token=device_id
    )
    try:
        response = messaging.send(message)
        logger.info(f"Push sent to {device_id}, response: {response}")
        return True
    except Exception as e:
        logger.error(f"Push send failed: {str(e)}")
        return False