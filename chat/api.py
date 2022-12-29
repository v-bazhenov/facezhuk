from fastapi import Depends
from fastapi_pagination import LimitOffsetPage
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from auth.models import User
from auth.security import get_user
from chat.schemas import ChatMessage, Chat
from chat.service import ChatService
from notification.manager import notifier

chat_router = InferringRouter()


@cbv(chat_router)
class ChatApi:
    """Chat API router.

    Attributes:
        _service (ChatService): ChatService Service for handling extra work.
    """
    _service = ChatService()

    @chat_router.get(
        "/chat/{chat_id}/messages",
        response_model=LimitOffsetPage[ChatMessage])
    async def get_messages(self, chat_id: str, user: User = Depends(get_user)):
        """Get messages belonging to a specific chat."""
        return await self._service.get_chat_messages(chat_id)

    @chat_router.get(
        "/chats",
        response_model=LimitOffsetPage[Chat])
    async def get_chats(self, user: User = Depends(get_user)):
        """Get all user's chats."""
        return await self._service.get_chats(user.username)

    @chat_router.post(
        "/chat/messages/{friend_username}/")
    async def create_message(
            self,
            friend_username: str,
            message_in: ChatMessage,
            user: User = Depends(get_user)):
        """Send new message to interlocutor."""
        self._service.save_chat_message(user.username, friend_username, new_message=message_in)
        await notifier.broadcast(friend_username, f'New Message Received from {user.username}')
