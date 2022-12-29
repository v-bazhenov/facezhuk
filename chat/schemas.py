from typing import Optional

from common.schemas import BaseSchema


class ChatMessage(BaseSchema):
    from_username: Optional[str]
    to_username: Optional[str]
    content: str


class Chat(BaseSchema):
    chat_id: str
    interlocutors: list = []
