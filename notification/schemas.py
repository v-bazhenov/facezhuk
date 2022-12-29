import datetime as dt
from typing import Optional

from common.schemas import BaseSchema


class NotificationReadData(BaseSchema):
    event: str
    from_user: str


class NotificationRead(BaseSchema):
    id: int
    created_at: Optional[dt.datetime]
    user_username: str
    data: NotificationReadData
    read: bool
