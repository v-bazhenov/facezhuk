import datetime as dt
from typing import Optional
from uuid import UUID

from bson import ObjectId
from pydantic import BaseModel
from sqlalchemy import Column, String, Table, DateTime

from database.core import Base

chat_message = Table(
    "chat_message", Base.metadata,
    Column("mongo_id", String),
    Column("from_username", String),
    Column("to_username", String),
    Column("chat_id", String),
    Column("created_at", DateTime(timezone=True)),
    Column("content", String),
)


class ChatMessage(BaseModel):
    created_at: Optional[dt.datetime]
    from_profile_id: UUID
    to_profile_id: UUID
    chat_id: UUID
    content: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        orm_mode = True
