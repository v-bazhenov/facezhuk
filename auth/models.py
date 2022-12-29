import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType

from database.core import Base


class Notification(Base):
    __tablename__ = 'notification'

    id = sa.Column(sa.Integer, primary_key=True)
    user_username = sa.Column(sa.String, sa.ForeignKey("users.username", ondelete="CASCADE"), nullable=False)
    data = sa.Column(JSON, nullable=False)
    read = sa.Column(sa.Boolean, server_default="false")
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())


notification = Notification.__table__


class Friendship(Base):
    __tablename__ = 'friendships'

    user_username = sa.Column(sa.String, sa.ForeignKey('users.username'), primary_key=True)
    friend_username = sa.Column(sa.String, sa.ForeignKey('users.username'), primary_key=True)


friendship = Friendship.__table__


class User(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(), unique=True, nullable=False)
    first_name = sa.Column(sa.String(), nullable=True)
    last_name = sa.Column(sa.String(), nullable=True)
    phone = sa.Column(sa.String(), nullable=True)
    email = sa.Column(EmailType, unique=True, nullable=False)
    registered_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    password = sa.Column(sa.String(), nullable=False)
    otp_secret = sa.Column(sa.String(), nullable=True)
    is_active = sa.Column(sa.Boolean, server_default="false")

    friends = relationship('User',
                           lazy='dynamic',
                           secondary=friendship,
                           primaryjoin=username == friendship.c.user_username,
                           secondaryjoin=username == friendship.c.friend_username)


user = User.__table__


friendship_request = sa.Table(
    "friendship_request", Base.metadata,
    sa.Column("from_user", sa.String),
    sa.Column("to_user", sa.String)
)
