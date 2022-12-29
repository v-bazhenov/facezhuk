from typing import Optional, List

from fastapi_pagination.ext.databases import paginate
from sqlalchemy import insert, select, desc, literal, update

from auth.models import notification
from database.core import db
from notification.models import Notification


class NotificationService:

    async def create_notification(self, new_notification: Notification) -> Notification:
        return await db.fetch_one(
            insert(notification)
            .values(new_notification.dict(exclude_unset=True))
            .returning(notification))

    async def get_notifications(self, user_username: str, is_read: bool = None):
        return await paginate(db, select([notification]).where(notification.c.user_username == user_username)
                              .where(notification.c.read == is_read)
                              .order_by(desc(notification.c.created_at)))

    async def mark_notifications_as(
            self,
            notification_ids: List[int],
            is_read: Optional[bool] = None) -> List[Notification]:
        return await db.fetch_all(
            update(notification)
            .where(notification.c.id.in_([literal(e) for e in notification_ids]))
            .values(**(dict(read=is_read) if is_read is not None else {}))
            .returning(notification))
