from fastapi_pagination.ext.databases import paginate
from fastapi_pagination.ext.sqlalchemy import paginate as paginate_sqlalchemy
from sqlalchemy import select, desc, insert, delete, and_

from auth.models import user, friendship_request, User
from database.core import db, session


class ProfilesService:

    async def find_profiles_by_username_search(self, username: str):
        return await paginate(db, select([
            user.c.id, user.c.username, user.c.first_name, user.c.last_name, user.c.phone])
        .where(user.c.username.ilike(f"%{username}%"))
        .order_by(
            desc(user.c.username.ilike(f"{username}%"))))

    async def find_profile_by_username(self, profile_username: str):
        return await db.fetch_one(select([user]).where(user.c.username == profile_username))

    async def create_friend_request(self, from_user: str, to_user: str):
        request = {
            'from_user': from_user,
            'to_user': to_user
        }
        return await db.fetch_one(insert(friendship_request).values(request).returning(friendship_request))

    async def check_friend_request_exists(self, requester_profile_username: str, target_profile_username: str):
        return await db.fetch_one(select([friendship_request])
                                      .where(
            (and_(friendship_request.c.from_user == requester_profile_username,
             friendship_request.c.to_user == target_profile_username) |
            (and_(friendship_request.c.from_user == target_profile_username,
            friendship_request.c.to_user == requester_profile_username))))
        )

    async def add_friend(self, requester_profile_username: str, accepter_profile_username: str):
        accepter = session.query(User).filter(User.username == accepter_profile_username).first()
        requester = session.query(User).filter(User.username == requester_profile_username).first()
        if requester in accepter.friends:
            return False
        accepter.friends.append(requester)
        requester.friends.append(accepter)
        session.commit()
        await self.delete_friend_request(requester_profile_username, accepter_profile_username)
        return True

    async def delete_friend_request(self, from_user: str, to_user: str):
        return await db.fetch_one(delete(friendship_request).where(
            friendship_request.c.from_user == from_user,
            friendship_request.c.to_user == to_user))

    async def delete_friend(self, username: str, friend_profile_username: str):
        current_user = session.query(User).filter(User.username == username).first()
        friend = session.query(User).filter(User.username == friend_profile_username).first()
        if friend not in current_user.friends:
            return False
        current_user.friends.remove(friend)
        friend.friends.remove(current_user)
        session.commit()
        return True

    async def get_friends(self, profile_username: str):
        current_user = session.query(User).filter(User.username == profile_username).first()
        return paginate_sqlalchemy(current_user.friends)

    async def find_outgoing_friend_requests(self, username: str):
        return await paginate(db, select([friendship_request]).where(friendship_request.c.from_user == username))

    async def find_incoming_friend_requests(self, username: str):
        return await paginate(db, select([friendship_request]).where(friendship_request.c.to_user == username))
