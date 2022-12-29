import asyncio

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from main import app, startup

app_base_url = "http://127.0.0.1:8000/api"


@pytest.fixture(autouse=True, scope="session")
async def created_user():
    async with AsyncClient(app=app, base_url=app_base_url) as ac, LifespanManager(app):
        await startup()
        user_data = {
            "email": "fftestffcreateasf@example.com",
            "password": "password123",
            'username': 'ftffesfft12affsd',
            "first_name": "test",
            "last_name": "test",
            "phone": "+380989090000"
        }
        res = await ac.post("/register", json=user_data)
    assert res.status_code == 201
    return res.json()


async def headers():
    async with AsyncClient(app=app, base_url=app_base_url) as ac, LifespanManager(app):
        user_data = {
            "email": "fftestffcreateasf@example.com",
            "password": "password123"
        }
        res = await ac.post("/login", json=user_data)
    assert res.status_code == 200
    headers = {'Authorization': f"Bearer {res.json()['accessToken']}"}
    return headers


loop = asyncio.get_event_loop()
coroutine = headers()
get_headers = loop.run_until_complete(coroutine)
