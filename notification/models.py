import datetime as dt
from typing import Optional

from pydantic import BaseModel


class NotificationData(BaseModel):
    event: str
    from_user: str


class Notification(BaseModel):
    id: Optional[int]
    created_at: Optional[dt.datetime]
    user_username: str
    data: NotificationData
    read: bool = False
