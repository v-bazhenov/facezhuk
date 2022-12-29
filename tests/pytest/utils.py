import random
import string
from datetime import timedelta, datetime
from typing import Dict, Tuple

import jwt
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from config import cfg
from main import app
from tests.pytest.conftest import app_base_url


def get_random_username_and_email():
    letters = string.ascii_lowercase
    username = ''.join(random.choice(letters) for i in range(8))
    email = f'{username}@example.com'
    return username, email


async def register_user(username: str, email: str, password: str, first_name: str, last_name: str, phone: str):
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        return await conn.post("/register", json=dict(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone))


async def register_random_user() -> Tuple[Dict, str, str, str, str]:
    username, email = get_random_username_and_email()
    password, first_name, last_name, phone = \
        "testpassword", "test_first", "test_last", "+380989009900"
    return (await register_user(username, email, password, first_name, last_name, phone)).json(), \
        password, email, first_name, last_name


async def do_login(email: str, password: str):
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        return await conn.post("/login", json=dict(
            email=email,
            password=password))


async def activate_user(token: str):
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        return await conn.post("/activate", json=dict(token=token))


async def generate_token(email):
    exp = (datetime.utcnow() + timedelta(minutes=cfg.activation_token_duration)).timestamp()
    token = jwt.encode({"email": email, "exp": exp}, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)
    return token


async def change_password(current_password: str, new_password: str, access_token: str):
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        return await conn.post("/change-password", json=dict(current_password=current_password,
                                                             new_password=new_password),
                                                    headers={'Authorization': f'Bearer {access_token}'})


async def change_profile_data(first_name: str, last_name: str, access_token: str):
    async with AsyncClient(app=app, base_url=app_base_url) as conn, LifespanManager(app):
        return await conn.patch("/account/change", json=dict(first_name=first_name,
                                                             last_name=last_name),
                                                    headers={'Authorization': f'Bearer {access_token}'})
