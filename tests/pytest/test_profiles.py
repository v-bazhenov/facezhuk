import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from main import app
from tests.pytest.conftest import app_base_url, get_headers


@pytest.mark.asyncio
async def test_search_profiles():
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        resp = await conn.get("/profiles?username_query=test")
        assert resp.status_code == 200
        assert resp.json()['items'][0]['username'] == 'test_user'


@pytest.mark.asyncio
async def test_search_profile_not_exist():
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        resp = await conn.get("/profiles/xxx", headers=get_headers)
        assert resp.status_code == 404
        assert resp.json()['detail'] == 'User with such username does not exist'


@pytest.mark.asyncio
async def test_search_profiles_no_query():
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        resp = await conn.get("/profiles")
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_send_friendship_request():
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        resp = await conn.post("/profiles/outgoing_friend_requests/test_user_1", json=dict(), headers=get_headers)
        assert resp.status_code == 204
        resp = await conn.delete("/profiles/outgoing_friend_requests/test_user_1", headers=get_headers)
        assert resp.status_code == 204


@pytest.mark.asyncio
async def test_send_friendship_request_non_existent_user():
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        resp = await conn.post("/profiles/outgoing_friend_requests/gubka_bob", json=dict(), headers=get_headers)
        assert resp.status_code == 400
        assert resp.json()['detail'] == 'This user does not exist'


@pytest.mark.asyncio
async def test_send_friendship_request_exists():
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        await conn.delete("/profiles/outgoing_friend_requests/test_user", headers=get_headers)
        resp = await conn.post("/profiles/outgoing_friend_requests/test_user", json=None, headers=get_headers)
        assert resp.status_code == 204
        resp = await conn.post("/profiles/outgoing_friend_requests/test_user", json=None, headers=get_headers)
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_send_friendship_request_non_existent_user():
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        resp = await conn.post("/profiles/outgoing_friend_requests/ftffesfft12affsd", json=dict(), headers=get_headers)
        assert resp.status_code == 400
        assert resp.json()['detail'] == 'You cannot send request to yourself'


@pytest.mark.asyncio
async def test_incoming_friendship_requests():
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        user_data = {
            "email": "jack@example.com",
            "password": "stringst"
        }
        res = await conn.post("/login", json=user_data)
        jon_token = {'Authorization': f"Bearer {res.json()['accessToken']}"}
        res = await conn.post("/profiles/outgoing_friend_requests/ftffesfft12affsd", json=dict(), headers=jon_token)
        assert res.status_code == 204

        res = await conn.get("/profiles/incoming_friend_requests/", headers=get_headers)
        assert res.status_code == 200
        assert res.json()['total'] == 1

        res = await conn.delete("/profiles/incoming_friend_requests/jack", headers=get_headers)
        assert res.status_code == 204


@pytest.mark.asyncio
async def test_accept_friendship_request():
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        user_data = {
            "email": "jack@example.com",
            "password": "stringst"
        }
        res = await conn.post("/login", json=user_data)
        jon_token = {'Authorization': f"Bearer {res.json()['accessToken']}"}

        await conn.delete("/profiles/friends/jack", headers=get_headers)

        res = await conn.post("/profiles/outgoing_friend_requests/ftffesfft12affsd", json=dict(), headers=jon_token)
        assert res.status_code == 204

        res = await conn.post("/profiles/friends/jack", json=dict(), headers=get_headers)
        assert res.status_code == 201


@pytest.mark.asyncio
async def test_accept_friendship_request_already_friends():
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        res = await conn.post("/profiles/friends/jack", json=dict(), headers=get_headers)
        assert res.status_code == 400
        assert res.json()['detail'] == 'You are already friends'


@pytest.mark.asyncio
async def test_get_friends():
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        res = await conn.get("/profiles/friends/", headers=get_headers)
        assert res.status_code == 200
        assert res.json()['total'] == 1


@pytest.mark.asyncio
async def test_delete_friend():
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        user_data = {
            "email": "jack@example.com",
            "password": "stringst"
        }
        res = await conn.post("/login", json=user_data)
        jon_token = {'Authorization': f"Bearer {res.json()['accessToken']}"}

        await conn.delete("/profiles/friends/jack", headers=get_headers)
        await conn.delete("/profiles/outgoing_friend_requests/ftffesfft12affsd", headers=jon_token)

        res = await conn.post("/profiles/outgoing_friend_requests/ftffesfft12affsd", json=dict(), headers=jon_token)
        assert res.status_code == 204

        res = await conn.post("/profiles/friends/jack", headers=get_headers)
        assert res.status_code == 201
        res = await conn.get("/profiles/friends/", headers=get_headers)
        assert res.json()['total'] == 1

        res = await conn.delete("/profiles/friends/jack", headers=get_headers)
        assert res.status_code == 204
        res = await conn.get("/profiles/friends/", headers=get_headers)
        assert res.json()['total'] == 0
