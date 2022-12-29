from typing import Optional, Dict

import jwt
from fastapi import HTTPException
from starlette import status
from starlette.requests import Request

from auth.models import User
from config import cfg


def get_user(request: Request) -> User:
    """
    Protect route from anonymous access, requiring and returning current
    authenticated user.

    :param request: web request
    :return: current user, otherwise raise an HTTPException (status=401)
    """

    return _check_and_extract_user(request)



def get_optional_user(request: Request) -> Optional[User]:
    """
    Return authenticated user or None if session is anonymous.

    :param request: web request
    :return: current user or None for anonymous sessions
    """
    try:
        return _check_and_extract_user(request)
    except HTTPException:
        if request.headers.get("Authorization"):
            raise


def extract_user_from_token(access_token: str, verify_exp: bool = True) -> User:
    """
    Extract User object from jwt token, with optional expiration check.

    :param access_token: encoded access token string
    :param verify_exp: whether to perform verification or not
    :return: User object stored inside the jwt
    """

    return User(**jwt.decode(
        access_token,
        key=cfg.jwt_secret,
        algorithms=[cfg.jwt_algorithm],
        options={"verify_exp": verify_exp})["user"])


def decode_jwt_refresh_token(
        encoded_refresh_token: str,
        verify_exp: bool = True) -> Dict:
    """
    Decode an encoded refresh token, with optional expiration check.

    :param encoded_refresh_token: encoded refresh token string
    :param verify_exp: whether to perform verification or not
    :return: decoded jwt refresh token as dictionary
    """

    return jwt.decode(
        encoded_refresh_token,
        key=cfg.jwt_secret,
        algorithms=[cfg.jwt_algorithm],
        options={"verify_exp": verify_exp})


def _check_and_extract_user(request: Request) -> User:
    authorization_header = request.headers.get("Authorization")
    if not authorization_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        access_token = authorization_header.replace("Bearer ", "")
        user = extract_user_from_token(access_token, )
        return user
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
