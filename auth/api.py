from asyncpg import UniqueViolationError
from fastapi import status, Cookie, HTTPException, Depends, Query
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette.responses import Response, JSONResponse

from auth.exceptions import LoginFailed, ExpiredJwtRefreshToken, InvalidUsername
from auth.models import User
from auth.schemas import ProfileCreate, RegisterResponse, LoginIn, LoginResponse, SocialAuthIn, ChangePasswordIn, \
    Profile, ChangeProfile, ForgotPassword, ResetPassword, TwoFactorConnectionResponse, ActivateUser
from auth.security import get_user
from auth.service import AuthService
from common.exceptions import HTTPExceptionJSON
from common.rate_limiter import RateLimitTo
from config import cfg

auth_router = InferringRouter()


@cbv(auth_router)
class AuthApi:
    """Authentication API router.

    Attributes:
        _service (AuthService): Authentication Service for handling extra work.
    """
    _service = AuthService()

    @auth_router.post(
        "/register",
        response_model=RegisterResponse,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(RateLimitTo(times=10, minutes=1))])
    async def register(self, profile_in: ProfileCreate):
        """Register a new user.
        User will receive an activation email.
        """
        try:
            profile = await self._service.register(Profile(**profile_in.dict()), profile_in.enable_2fa)
            return profile
        except InvalidUsername as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e))
        except UniqueViolationError as e:
            raise HTTPExceptionJSON(status_code=status.HTTP_409_CONFLICT,
                                    detail=str(e))

    @auth_router.post(
        "/login",
        response_model=LoginResponse)
    async def login(self, log_in: LoginIn, response: Response):
        """Perform a login attempt; if successful, refresh token cookie is set
        and access token is returned to the client."""
        jwt_data = await self._service.login(log_in.email, log_in.password, log_in.one_time_pass)
        response.set_cookie(key="refresh_token",
                            value=jwt_data.refresh_token,
                            httponly=True,
                            secure=cfg.debug,
                            expires=cfg.jwt_refresh_expiration_seconds)
        return {
            "access_token": jwt_data.access_token,
            "refresh_token": jwt_data.refresh_token
        }

    @auth_router.post(
        "/social-login",
        response_model=LoginResponse)
    async def social_login(self, social_auth_in: SocialAuthIn, response: Response):
        """Perform a social login attempt;
        if user's email is present in the system - login will be performed and access token will be returned.
        Otherwise, the new account will be created;
        Temporary password email will be sent to user.
        """
        try:
            jwt_data = await self._service.social_login(
                social_auth_in.code,
                social_auth_in.social_provider
            )
        except LoginFailed:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        response.set_cookie(key="refresh_token",
                            value=jwt_data.refresh_token,
                            httponly=True,
                            secure=cfg.debug,
                            expires=cfg.jwt_refresh_expiration_seconds)
        return {
            "access_token": jwt_data.access_token,
            "refresh_token": jwt_data.refresh_token
        }

    @auth_router.post(
        "/refresh",
        response_model=LoginResponse)
    async def refresh(self, response: Response, refresh_token: str = Cookie(None)):
        """If refresh token hasn't expired, perform jwt token refresh, returning
        a new access token as well as setting a new refresh token cookie."""
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        try:
            jwt_data = await self._service.refresh_jwt_access_token(refresh_token)
        except ExpiredJwtRefreshToken:
            response = JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content='Token has expired')
            response.delete_cookie("refresh_token")
            return response
        response.set_cookie(key="refresh_token",
                            value=jwt_data.refresh_token,
                            httponly=True,
                            secure=cfg.debug,
                            expires=cfg.jwt_refresh_expiration_seconds)
        return {
            "access_token": jwt_data.access_token,
            "refresh_token": jwt_data.refresh_token
        }

    @auth_router.post(
        "/change-password",
        status_code=status.HTTP_200_OK,
        response_model=ChangeProfile)
    async def change_password(self, change_password_in: ChangePasswordIn, user: User = Depends(get_user)):
        """Changing password. User should input his current password and new password
        """
        try:
            data = await self._service.change_password(
                user.username,
                change_password_in.current_password,
                change_password_in.new_password
            )
        except LoginFailed:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return data

    @auth_router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
    async def forgot_password(self, forgot_password: ForgotPassword):
        """User can use a `forgot password` option. He would need to input his email address,
        and he will receive a link to reset his password.
        """
        await self._service.forgot_password(forgot_password.email)

    @auth_router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
    async def reset_password(self, reset_password: ResetPassword):
        """It is used to reset user's password. Token and new password should be entered.
        """
        await self._service.reset_password(reset_password)

    @auth_router.post("/activate", status_code=status.HTTP_204_NO_CONTENT)
    async def activate_user(self, activation: ActivateUser):
        """User activation
        """
        await self._service.activate_user(activation)

    @auth_router.post(
        "/account/two-factor-auth",
        response_model=TwoFactorConnectionResponse,
        status_code=status.HTTP_200_OK)
    async def two_factor_auth(self, action: str = Query(...), user: User = Depends(get_user)):
        """User can connect/disconnect Two-Factor Authentication
        """
        profile = await self._service.find_profile_by_username(username=user.username)
        return await self._service.two_factor_auth(action, profile)

    @auth_router.patch(
        "/account/change",
        response_model=ChangeProfile,
        status_code=status.HTTP_200_OK)
    async def change_profile_data(self, data: ChangeProfile, user: User = Depends(get_user)):
        """User can update his profile information.
        """
        if not data.dict(exclude_none=True):
            raise HTTPException(detail='Request cannot be empty', status_code=status.HTTP_400_BAD_REQUEST)
        data = await self._service.change_profile_data(user.username, data)
        return data
