import datetime as dt
import secrets
from typing import Optional, Dict

import bcrypt
import jwt
import pyotp
from asyncpg import UniqueViolationError
from fastapi import HTTPException
from jwt import ExpiredSignatureError
from sqlalchemy import insert, select, update
from starlette import status

from auth.exceptions import LoginFailed, \
    EmailAlreadyTaken, UsernameAlreadyTaken, UserDoesNotExist, ExpiredJwtRefreshToken
from auth.mail import send_email
from auth.models import user
from auth.schemas import Profile, JwtTokenPayload, JwtData, JwtTokenData, \
    JwtRefreshTokenData, JwtUser
from auth.security import decode_jwt_refresh_token
from auth.social.facebook import FacebookAdapter
from auth.social.google import GoogleAdapter
from config import cfg
from database.core import db


class AuthService:
    _google_adapter = GoogleAdapter()
    _facebook_adapter = FacebookAdapter()

    async def find_profile_by_username(self, username: str):
        return await db.fetch_one(select([user])
                                  .where(user.c.username == username))

    async def find_profile_by_email(self, email: str):
        return await db.fetch_one(select([user])
                                  .where(user.c.email == email.lower()))

    async def update_profile_data(self, username: str, values: Dict) \
            -> Optional[Profile]:
        return await db.fetch_one(update(user)
                                  .where(user.c.username == username)
                                  .values(**values)
                                  .returning(user))

    async def register(self, profile: Profile, enable_2fa: bool) -> Profile:
        profile.password = bcrypt.hashpw(profile.password.encode(), bcrypt.gensalt()).decode()
        profile.email = profile.email.lower()
        if enable_2fa:
            profile.otp_secret = pyotp.random_base32()
        try:
            result = await db.fetch_one(insert(user).values(
                profile.dict(exclude_none=True)).returning(user))
            await self.send_activation_email(profile)
            return result
        except UniqueViolationError as e:
            if e.constraint_name == "user_email_key":
                raise EmailAlreadyTaken()
            if e.constraint_name == "user_username_key":
                raise UsernameAlreadyTaken()
            raise e

    async def login(self, email: str, password: str, one_time_pass: str = None) -> [bool, JwtData]:
        profile = await self.find_profile_by_email(email=email)
        if not profile or not await self._check_password(password, profile.password):
            raise HTTPException(detail='Wrong email or password', status_code=status.HTTP_400_BAD_REQUEST)
        if not profile.is_active:
            raise HTTPException(detail='User is not active', status_code=status.HTTP_400_BAD_REQUEST)
        if profile.otp_secret and not one_time_pass:
            raise HTTPException(detail='One-time password is not provided', status_code=status.HTTP_400_BAD_REQUEST)
        elif profile.otp_secret and one_time_pass:
            totp = pyotp.TOTP(profile.otp_secret)
            if not totp.verify(one_time_pass):
                raise HTTPException(detail='Wrong one-time password', status_code=status.HTTP_400_BAD_REQUEST)
        jwt_user_data = JwtUser(email=profile.email, username=profile.username)
        jwt_data = await self._generate_jwt_access_token(jwt_user_data)
        jwt_refresh_data = await self._generate_jwt_refresh_token(jwt_user_data)
        return JwtData(access_token=jwt_data.access_token, refresh_token=jwt_refresh_data.refresh_token)

    async def social_login(self, code: str, social_provider: str) -> JwtData:
        match social_provider:
            case "google":
                access_token = self._google_adapter.get_access_token_data(code=code)
                profile_info = self._google_adapter.get_profile_data(access_token)
            case "facebook":
                access_token = self._facebook_adapter.get_access_token_data(code=code)
                profile_info = self._facebook_adapter.get_profile_data(access_token)
            case _:
                raise HTTPException(detail='Wrong social provider', status_code=status.HTTP_400_BAD_REQUEST)

        email = profile_info.get('email')
        username = email.split('@')[0]
        profile = await self.find_profile_by_email(email=email)
        if not profile:
            profile = Profile(
                username=username, email=email, password=await self.create_temp_password(email), is_active=True
            )
            await db.fetch_one(insert(user).values(
                profile.dict(exclude_none=True)).returning(user))
        jwt_user_data = JwtUser(email=profile.email, username=profile.username)
        jwt_data = await self._generate_jwt_access_token(jwt_user_data)
        jwt_refresh_data = await self._generate_jwt_refresh_token(jwt_user_data)
        return JwtData(access_token=jwt_data.access_token,
                       refresh_token=jwt_refresh_data.refresh_token)

    async def two_factor_auth(self, action, profile):
        match action:
            case 'connect':
                if profile.otp_secret is not None:
                    raise HTTPException(
                        detail='Two factor auth is already connected',
                        status_code=status.HTTP_400_BAD_REQUEST)
                otp_secret = pyotp.random_base32()
                return await db.fetch_one(
                    update(user)
                    .where(user.c.username == profile.username)
                    .values({'otp_secret': otp_secret})
                    .returning(user))
            case 'disconnect':
                if profile.otp_secret is None:
                    raise HTTPException(
                        detail='Two factor auth is not connected',
                        status_code=status.HTTP_400_BAD_REQUEST)
                return await db.fetch_one(
                    update(user)
                    .where(user.c.username == profile.username)
                    .values({'otp_secret': None}).returning(user))
            case _:
                raise HTTPException(
                    detail='Wrong query param',
                    status_code=status.HTTP_400_BAD_REQUEST)

    async def change_password(self, username: str, current_password: str, new_password: str):
        current_user = await self.find_profile_by_username(username)
        if not await self._check_password(current_password, current_user.password):
            raise LoginFailed()
        new_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        return await self.update_profile_data(username=username, values=dict(password=new_password))

    async def change_profile_data(self, username: str, data):
        return await self.update_profile_data(username=username, values=data.dict(exclude_unset=True))

    async def _check_password(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode(), password_hash.encode())

    async def _generate_jwt_access_token(self, user: JwtUser) -> JwtTokenData:
        iat = dt.datetime.now(dt.timezone.utc)
        exp = iat + dt.timedelta(seconds=cfg.jwt_expiration_seconds)
        payload = JwtTokenPayload(iat=iat, exp=exp, user=user)
        enc_jwt = jwt.encode(
            payload=payload.dict(),
            key=cfg.jwt_secret,
            algorithm=cfg.jwt_algorithm)
        return JwtTokenData(access_token=enc_jwt)

    async def _generate_jwt_refresh_token(self, user: JwtUser) -> JwtRefreshTokenData:
        iat = dt.datetime.now(dt.timezone.utc)
        exp = iat + dt.timedelta(seconds=cfg.jwt_refresh_expiration_seconds)
        payload = JwtTokenPayload(user=user, iat=iat, exp=exp)
        enc_jwt_refresh = jwt.encode(
            payload=payload.dict(),
            key=cfg.jwt_secret,
            algorithm=cfg.jwt_algorithm)
        return JwtRefreshTokenData(refresh_token=enc_jwt_refresh)

    async def refresh_jwt_access_token(self, encoded_refresh_token: str) -> JwtData:
        try:
            old_refresh_token = decode_jwt_refresh_token(encoded_refresh_token)
        except jwt.ExpiredSignatureError:
            raise ExpiredJwtRefreshToken()
        email, username = (old_refresh_token["user"]["email"], old_refresh_token["user"]["username"])
        jwt_user_data = JwtUser(email=email, username=username)
        new_jwt_data = await self._generate_jwt_access_token(jwt_user_data)
        new_jwt_refresh_data = await self._generate_jwt_refresh_token(jwt_user_data)
        return JwtData(access_token=new_jwt_data.access_token,
                       refresh_token=new_jwt_refresh_data.refresh_token)

    async def forgot_password(self, email):
        user = await self.find_profile_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='This user does not exist')

        exp = (dt.datetime.utcnow() + dt.timedelta(minutes=cfg.reset_password_token_duration)).timestamp()
        token = jwt.encode({"email": email, "exp": exp}, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)
        print('forgot_password', token)

        # Sending email
        subject = "Facezhuk Reset Password"
        recipient = [email]
        context = {'username': user.username, 'token': token}
        template_name = 'forgot_password.html'
        await send_email(recipient, template_name, context, subject)

    async def reset_password(self, reset_password):
        try:
            user_email = jwt.decode(
                jwt=reset_password.token,
                key=cfg.jwt_secret,
                algorithms=cfg.jwt_algorithm)['email']
        except ExpiredSignatureError:
            raise HTTPException(detail='Token has already expired', status_code=status.HTTP_400_BAD_REQUEST)
        user = await self.find_profile_by_email(user_email)
        new_password = bcrypt.hashpw(reset_password.new_password.encode(), bcrypt.gensalt()).decode()
        return await self.update_profile_data(username=user.username, values=dict(password=new_password))

    async def create_temp_password(self, email):
        temp_password = secrets.token_urlsafe(6)
        hashed = bcrypt.hashpw(temp_password.encode(), bcrypt.gensalt()).decode()
        subject = "Facezhuk Temp Password"
        recipient = [email]
        context = {'email': email, 'temp_password': temp_password}
        template_name = 'temp_password.html'
        await send_email(recipient, template_name, context, subject)
        print('temp password', temp_password)
        return hashed

    async def send_activation_email(self, profile):
        exp = (dt.datetime.utcnow() + dt.timedelta(minutes=cfg.activation_token_duration)).timestamp()
        token = jwt.encode({"email": profile.email, "exp": exp}, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)

        # Sending email
        subject = "Facezhuk Activation"
        recipient = [profile.email]
        context = {'first_name': profile.first_name, 'last_name': profile.last_name, 'token': token}
        template_name = 'activation.html'
        print('activation email', token)
        await send_email(recipient, template_name, context, subject)

    async def activate_user(self, activation):
        try:
            user_email = jwt.decode(
                jwt=activation.token,
                key=cfg.jwt_secret,
                algorithms=cfg.jwt_algorithm)['email']
        except ExpiredSignatureError:
            raise HTTPException(detail='Token has already expired', status_code=status.HTTP_400_BAD_REQUEST)
        user = await self.find_profile_by_email(user_email)
        return await self.update_profile_data(username=user.username, values=dict(is_active=True))
