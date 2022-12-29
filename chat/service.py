import datetime as dt
import uuid

from fastapi import Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.motor import paginate
from starlette import status

from chat.models import ChatMessage
from database.core import mongo_db_messages_collection, mongo_db_chats_collection, async_mongo_db_messages_collection, \
    async_mongo_db_chats_collection


class ChatService:

    def generate_chat_id(self, from_username: str, friend_username: str) -> str:
        ids = sorted([from_username, friend_username])
        chat_id = str(uuid.uuid5(uuid.NAMESPACE_X500, '+'.join(ids)))
        return chat_id

    def save_chat_message(self, from_username, friend_username, new_message: ChatMessage = Body(...)):
        msg = {
            'chatId': self.generate_chat_id(from_username, friend_username),
            'createdAt': dt.datetime.now(),
            'isBackupCreated': False,
            'fromUsername': from_username,
            'toUsername': friend_username,
            'content': new_message.content
        }
        message = jsonable_encoder(msg)
        n_msg = mongo_db_messages_collection.insert_one(message)
        chat_collection = mongo_db_chats_collection.find_one({"chatId": message['chatId']})
        if not chat_collection:
            chat_data = {'chatId': message['chatId'],
                         'interlocutors': [from_username, friend_username]}
            mongo_db_chats_collection.insert_one(chat_data)
        created_msg = mongo_db_messages_collection.find_one({"_id": n_msg.inserted_id})
        created_msg['_id'] = str(created_msg['_id'])
        created_msg['createdAt'] = str(created_msg['createdAt'])
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_msg)

    async def get_chat_messages(self, chat_id: str):
        query_filter = {'chatId': chat_id}
        messages = await paginate(collection=async_mongo_db_messages_collection,
                                  query_filter=query_filter,
                                  sort=[("created_at", -1)])
        return messages

    async def get_chats(self, username: str):
        query_filter = {'interlocutors': username}
        chats = await paginate(collection=async_mongo_db_chats_collection,
                               query_filter=query_filter,
                               sort=[("created_at", -1)])
        return chats
