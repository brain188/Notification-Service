# Integrates with SendGrid for sending emails

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def send_email(recipient: str, content: str):
    message = Mail(
        from_email = settings.DEFAULT_FROM_EMAIL,
        to_emails = recipient,
        subject = 'Notification',
        html_content = content
    )
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"Email sent to {recipient}, status:{response.status_code} ")
        return True
    except Exception as e:
        logger.error(f"Email send failed: {str(e)}")
        return False