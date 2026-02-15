from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from app.core.security import verify_token
from app.core.logging import get_logger

logger = get_logger(__name__)

security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """Returns user id from JWT. Use for any authenticated user (ADMIN or CUSTOMER)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = verify_token(token)
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        return int(sub)
    except HTTPException:
        raise
    except (InvalidTokenError, ValueError, TypeError) as e:
        logger.error(f"Token validation error: {str(e)}")
        raise credentials_exception


def get_current_admin_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """ADMIN only. Returns admin user id."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required.",
    )
    try:
        token = credentials.credentials
        payload = verify_token(token)
        sub = payload.get("sub")
        role = payload.get("role")
        if sub is None:
            raise credentials_exception
        if role != "ADMIN":
            raise forbidden_exception
        return int(sub)
    except HTTPException:
        raise
    except (InvalidTokenError, ValueError, TypeError) as e:
        logger.error(f"Token validation error: {str(e)}")
        raise credentials_exception


def get_current_admin_id_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
) -> int | None:
    """Return user id from JWT if valid admin token present, else None."""
    if credentials is None:
        return None
    try:
        token = credentials.credentials
        payload = verify_token(token)
        sub = payload.get("sub")
        role = payload.get("role")
        if sub is not None and role == "ADMIN":
            return int(sub)
    except Exception:
        pass
    return None


def get_current_customer_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """CUSTOMER only. Returns customer user id."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Customer access required.",
    )
    try:
        token = credentials.credentials
        payload = verify_token(token)
        sub = payload.get("sub")
        role = payload.get("role")
        if sub is None:
            raise credentials_exception
        if role != "CUSTOMER":
            raise forbidden_exception
        return int(sub)
    except HTTPException:
        raise
    except (InvalidTokenError, ValueError, TypeError) as e:
        logger.error(f"Token validation error: {str(e)}")
        raise credentials_exception
