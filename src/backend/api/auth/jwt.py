"""
JWT Token Management.

Handles JWT token creation, validation, and decoding.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from config.settings import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_prefix}/auth/login",
    auto_error=False,  # Allow optional authentication
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def create_jwt(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time (defaults to settings)

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()

    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_expiration_minutes
        )

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    # Encode token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return encoded_jwt


def decode_jwt(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Dict[str, Any]: Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload

    except JWTError as exc:
        raise credentials_exception from exc


def create_access_token(user_id: str, is_admin: bool = False) -> str:
    """
    Create an access token for a user.

    Args:
        user_id: User ID to encode
        is_admin: Whether user is an admin

    Returns:
        str: Encoded JWT access token
    """
    data = {
        "sub": str(user_id),
        "type": "access",
        "is_admin": is_admin,
    }
    return create_jwt(data)


def create_refresh_token(user_id: str) -> str:
    """
    Create a refresh token for a user.

    Args:
        user_id: User ID to encode

    Returns:
        str: Encoded JWT refresh token
    """
    data = {
        "sub": str(user_id),
        "type": "refresh",
    }
    # Refresh tokens expire after 7 days
    return create_jwt(data, expires_delta=timedelta(days=7))
