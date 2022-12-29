from typing import Optional

from pydantic import EmailStr

from common.schemas import BaseSchema


class BaseProfile(BaseSchema):
    username: str
    first_name: Optional[str]
    last_name: Optional[str]


class FullProfile(BaseProfile):
    email: EmailStr
    phone: Optional[str]


class IncomingFriendRequest(BaseSchema):
    from_user: str


class OutgoingFriendRequest(BaseSchema):
    to_user: str
