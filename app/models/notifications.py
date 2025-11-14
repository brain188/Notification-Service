from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.base import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable = False) # e.g., 'user_signup', 'password_reset'
    channel = Column(String, nullable = False) # e.g., 'email', 'sms', 'push'
    recipient = Column(String, nullable = False) # e.g., email address or phone number
    content = Column(Text, nullable = False)
    status = Column(String, default='pending')  # e.g., 'pending', 'sent', 'failed' 
    attempt = Column(Integer, default=0)  # Number of send attempts
    created_at = Column(DateTime, server_default=func.now())