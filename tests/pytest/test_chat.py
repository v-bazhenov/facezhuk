import asyncio

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from chat.service import ChatService
from main import app
from tests.pytest.conftest import app_base_url, get_headers


@pytest.mark.asyncio
async def test_create_message():
        async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
            AsyncIOMotorClient.get_io_loop = asyncio.get_running_loop

            friend_username = 'test_user'
            from_username = 'test'
            msg = {
                'chatId': ChatService().generate_chat_id(from_username, friend_username),
                'isBackupCreated': False,
                'fromUsername': from_username,
                'toUsername': friend_username,
                'content': 'test'
            }
            resp = await conn.post(f"/chat/messages/{friend_username}/", headers=get_headers, json=msg)
            assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_chats():
        async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
            AsyncIOMotorClient.get_io_loop = asyncio.get_running_loop

            resp = await conn.get("/chats", headers=get_headers)
            assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_chat_messages():
        async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
            AsyncIOMotorClient.get_io_loop = asyncio.get_running_loop

            resp = await conn.get("/chats", headers=get_headers)
            chat_id = resp.json()['items'][0]['chatId']

            resp = await conn.get(f"/chat/{chat_id}/messages", headers=get_headers)
            assert resp.status_code == 200
