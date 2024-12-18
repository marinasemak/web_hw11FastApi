from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from config.db import get_db
from config.general import settings
from src.auth.models import User
from src.auth.repos import UserRepository
from src.auth.schema import TokenData

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
VERIFICATION_TOKEN_EXPIRE_HOURS = 24


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_verification_token(email: EmailStr) -> str:
    """
    Create encoded token for user verification from user email and secret key
    :param email: User email
    :type email: EmailStr
    :return: Encoded jwt token
    :rtype: str
    """
    expire = datetime.now(timezone.utc) + timedelta(
        hours=VERIFICATION_TOKEN_EXPIRE_HOURS
    )
    to_encode = {"exp": expire, "sub": email}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def decode_verification_token(token: str) -> str | None:
    """
    Decode verification token
    :param token: Token to verify
    :type token: str
    :return: User email or None
    :rtype: str | None
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=ALGORITHM)
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


def create_access_token(data: dict) -> str:
    """
    Create token to get access
    :param data: Username (email)
    :type data: dict
    :return: Encoded jwt token
    :rtype: str
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    """
    Create refresh token
    :param data: Username (email)
    :type data: dict
    :return: Encoded jwt token
    :rtype: str
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData | None:
    """
    Decode access token
    :param token: Token to decode
    :type token: str
    :return: User email from token if exists
    :rtype: TokenData | None
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """
    Find user with token in db
    :param token: User token
    :type token: str
    :param db: The database session
    :type db: Session
    :return: User from db
    :rtype: User
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token)
    if token_data is None:
        raise credentials_exception
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(token_data.username)
    if user is None:
        raise credentials_exception
    return user
