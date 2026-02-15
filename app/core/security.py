from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
import jwt
from jwt.exceptions import ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

context = CryptContext(schemes=["sha512_crypt"])


def generate_random_password(length: int) -> str:
    return secrets.token_urlsafe(length)


def generate_random_otp(length: int) -> str:
    return str(secrets.randbelow(10 ** length))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return context.hash(password)


def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    secret_key = str(settings.secret_key)
    algorithm = str(settings.algorithm)
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def verify_token(token: str) -> dict:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = token.strip()
        secret_key = str(settings.secret_key)
        algorithm = str(settings.algorithm)
        if not secret_key:
            logger.error("Secret key is empty!")
            raise credentials_exception
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Token verification error: {type(e).__name__}: {str(e)}")
        raise credentials_exception
