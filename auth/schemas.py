import datetime as dt
from typing import Optional

from pydantic import Field, EmailStr

from common.schemas import BaseSchema


class ProfileCreate(BaseSchema):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str]
    password: str = Field(min_length=8, max_length=64)
    enable_2fa: Optional[bool]


class RegisterResponse(BaseSchema):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    otp_secret: Optional[str]


class TwoFactorConnectionResponse(BaseSchema):
    otp_secret: Optional[str]


class LoginIn(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    one_time_pass: Optional[str]


class LoginResponse(BaseSchema):
    access_token: Optional[str]
    refresh_token: Optional[str]


class SocialAuthIn(BaseSchema):
    code: str
    social_provider: str


class ChangePasswordIn(BaseSchema):
    current_password: str = Field(min_length=8, max_length=32)
    new_password: str = Field(min_length=8, max_length=32)


class ChangeProfile(BaseSchema):
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]


class Profile(BaseSchema):
    username: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    registered_at: Optional[dt.datetime]
    last_login_at: Optional[dt.datetime]
    otp_secret: Optional[str]
    password: str
    is_active: Optional[bool]


class JwtUser(BaseSchema):
    email: EmailStr
    username: str


class JwtTokenPayload(BaseSchema):
    iat: dt.datetime
    exp: dt.datetime
    user: JwtUser


class JwtRefreshTokenPayload(JwtTokenPayload):
    pass


class JwtTokenData(BaseSchema):
    access_token: str


class JwtRefreshTokenData(BaseSchema):
    refresh_token: str


class JwtData(JwtTokenData, JwtRefreshTokenData):
    pass


class ForgotPassword(BaseSchema):
    email: EmailStr


class ResetPassword(BaseSchema):
    token: str
    new_password: str


class ActivateUser(BaseSchema):
    token: str
