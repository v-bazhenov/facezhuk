from typing import List, Optional

from fastapi import Query, Depends
from fastapi_pagination import LimitOffsetPage
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from auth.models import User
from auth.security import get_user
from common.rate_limiter import RateLimitTo
from notification.schemas import NotificationRead
from notification.service import NotificationService

notification_router = InferringRouter()


@cbv(notification_router)
class NotificationApi:
    """Notification API router.

    Attributes:
        _service (NotificationService): NotificationService Service for handling extra work with notifications.
    """
    _service = NotificationService()

    @notification_router.get(
        "/notifications",
        response_model=LimitOffsetPage[NotificationRead],
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def get_notifications(
            self,
            is_read: Optional[bool] = Query(None),
            user: User = Depends(get_user)):
        """Get notifications for a specific profile."""
        return await self._service.get_notifications(user.username, is_read)

    @notification_router.patch(
        "/notifications",
        response_model=List[NotificationRead],
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def patch_notifications(
            self,
            notification_ids: List[int],
            is_read: Optional[bool] = Query(None),
            user: User = Depends(get_user)):
        """Mark specified notifications as read."""
        return await self._service.mark_notifications_as(notification_ids, is_read)
