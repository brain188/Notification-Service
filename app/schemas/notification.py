# For API input/output validation

from pydantic import BaseModel
from datetime import datetime

class NotificationBase(BaseModel):
    event_type: str
    channel: str
    recipient: str
    content: str

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    id: int
    status: str
    attempt: int
    created_at: datetime

class NotificationReport(NotificationBase):
    id: int
    status: str
    attempts: int
    created_at: datetime    

class Config:
    from_attributes = True # for ORM mode