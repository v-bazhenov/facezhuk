from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ProfileShort(BaseModel):
    username: Optional[str]


class FriendshipRequest(BaseModel):
    profile_id: UUID
    target_profile_id: UUID
