import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from main import app
from tests.pytest.conftest import app_base_url, get_headers


@pytest.mark.asyncio
async def test_get_notifications():
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        resp = await conn.get("/notifications", headers=get_headers)
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_notifications_unauthorized():
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        resp = await conn.get("/notifications")
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_mark_notification_as_read():

    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        resp = await conn.patch("/notifications", headers=get_headers, json=[1], params={'is_read': True})
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_mark_notification_as_read_unauthorized():
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        resp = await conn.patch("/notifications", json=[1], params={'is_read': True})
        assert resp.status_code == 401
