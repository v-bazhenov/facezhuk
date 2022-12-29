from fastapi import Depends, HTTPException
from fastapi_pagination import LimitOffsetPage
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette import status

from auth.models import User
from auth.security import get_user
from common.rate_limiter import RateLimitTo
from notification.manager import notifier
from notification.models import NotificationData, Notification
from notification.service import NotificationService
from profile.schemas import FullProfile, IncomingFriendRequest, OutgoingFriendRequest, BaseProfile, FullProfileOut
from profile.service import ProfilesService

profiles_router = InferringRouter()


@cbv(profiles_router)
class ProfilesApi:
    """Profiles API router.

    Attributes:
        _service (ProfilesService): Profiles Service for handling extra work.
        _service (NotificationService): NotificationService Service for handling extra work with notifications.
    """
    _service = ProfilesService()
    _notifications = NotificationService()

    @profiles_router.get(
        "/profiles",
        response_model=LimitOffsetPage[BaseProfile],
        dependencies=[Depends(RateLimitTo(times=10, seconds=1))])
    async def get_profiles_by_username_search(self, username_query: str):
        """Return a list of profile whose usernames match the query."""
        return await self._service.find_profiles_by_username_search(username_query)

    @profiles_router.get(
        "/profiles/{profile_username}",
        response_model=FullProfile,
        dependencies=[Depends(RateLimitTo(times=10, seconds=1))])
    async def get_profile_by_username(self, profile_username: str, user: User = Depends(get_user)):
        """Get profile's data by profile id."""
        profile = await self._service.find_profile_by_username(profile_username)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User with such username does not exist')
        return profile

    @profiles_router.post(
        "/profiles/outgoing_friend_requests/{target_profile_username}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(RateLimitTo(times=10, seconds=1))])
    async def create_friend_request(
            self,
            target_profile_username: str,
            user: User = Depends(get_user)):
        """Send a friend request from one profile to another."""
        if user.username == target_profile_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='You cannot send request to yourself')
        if not await self._service.find_profile_by_username(target_profile_username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='This user does not exist')
        if await self._service.check_friend_request_exists(user.username, target_profile_username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='There already exists a pending friend request')
        await self._service.create_friend_request(
            from_user=user.username,
            to_user=target_profile_username)
        await notifier.broadcast(target_profile_username, f'New Friendship Request from {user.username}')
        await self._notifications.create_notification(Notification(
                user_username=target_profile_username,
                data=NotificationData(
                    event="New Friendship Request",
                    from_user=user.username
                )
            )
        )

    @profiles_router.post(
        "/profiles/friends/{requester_profile_username}",
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(RateLimitTo(times=10, seconds=1))])
    async def accept_friend_request(
            self,
            requester_profile_username: str,
            user: User = Depends(get_user)):
        """Accept an incoming friend request."""
        is_added = await self._service.add_friend(
            requester_profile_username=requester_profile_username,
            accepter_profile_username=user.username)
        if not is_added:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='You are already friends')

    @profiles_router.delete(
        "/profiles/incoming_friend_requests/{requester_username}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(RateLimitTo(times=10, seconds=1))])
    async def reject_incoming_friend_request(self, requester_username: str, user: User = Depends(get_user)):
        """Reject an incoming friend request."""
        return await self._service.delete_friend_request(
            from_user=requester_username,
            to_user=user.username)

    @profiles_router.delete(
        "/profiles/outgoing_friend_requests/{target_profile_username}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(RateLimitTo(times=10, seconds=1))])
    async def cancel_outgoing_friend_request(self, target_profile_username: str, user: User = Depends(get_user)):
        """Cancel an outgoing friend request."""
        return await self._service.delete_friend_request(
            from_user=user.username,
            to_user=target_profile_username)

    @profiles_router.delete(
        "/profiles/friends/{friend_profile_username}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(RateLimitTo(times=10, seconds=1))])
    async def remove_friend(self, friend_profile_username: str, user: User = Depends(get_user)):
        """Remove a friend from logged user's friends list."""
        is_friends = await self._service.delete_friend(user.username, friend_profile_username)
        if not is_friends:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Cannot delete user from your friends list - you are not friends')

    @profiles_router.get(
        "/profiles/friends/",
        response_model=LimitOffsetPage[FullProfileOut],
        dependencies=[Depends(RateLimitTo(times=10, seconds=1))])
    async def get_friends(self, user: User = Depends(get_user)):
        """Get specified profile's friends."""
        return await self._service.get_friends(user.username)

    @profiles_router.get(
        "/profiles/outgoing_friend_requests/",
        response_model=LimitOffsetPage[OutgoingFriendRequest],
        dependencies=[Depends(RateLimitTo(times=10, seconds=1))])
    async def get_outgoing_friend_requests(self, user: User = Depends(get_user)):
        """Get outgoing friend requests."""
        return await self._service.find_outgoing_friend_requests(user.username)

    @profiles_router.get(
        "/profiles/incoming_friend_requests/",
        response_model=LimitOffsetPage[IncomingFriendRequest],
        dependencies=[Depends(RateLimitTo(times=10, seconds=1))])
    async def get_incoming_friend_requests(self, user: User = Depends(get_user)):
        """Get incoming friend requests."""
        return await self._service.find_incoming_friend_requests(user.username)
