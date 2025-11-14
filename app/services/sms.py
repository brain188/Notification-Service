# Integrates with Twilio for sending SMS

from twilio.rest import Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def send_sms(recipient: str, content: str):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        message = client.messages.create(
            body = content,
            from_ = settings.TWILIO_PHONE_NUMBER,
            to = recipient

        )
        logger.info(f"SMS sent to {recipient}, SID: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"SMS send failed: {str(e)}")
        return False