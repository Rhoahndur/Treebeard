"""
Authentication Endpoints.

User registration, login, and token management.
"""

import logging
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from config.database import get_db
from models.user import User
from api.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_jwt,
    get_password_hash,
    verify_password,
)
from api.auth_dependencies import CurrentUser, DBSession

router = APIRouter()
logger = logging.getLogger(__name__)


# Request/Response Schemas


class RegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password (min 8 chars)")
    name: str = Field(..., min_length=1, description="User name")
    zip_code: str = Field(..., min_length=5, max_length=10, description="ZIP code")


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class UserResponse(BaseModel):
    """User information response."""

    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User name")
    is_admin: bool = Field(..., description="Whether user is admin")
    created_at: datetime = Field(..., description="Account creation timestamp")


# Endpoints


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Register a new user account and receive authentication tokens.",
)
async def register(request: RegisterRequest, db: DBSession):
    """
    Register a new user.

    Args:
        request: Registration request
        db: Database session

    Returns:
        TokenResponse: Authentication tokens

    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    user = User(
        id=uuid4(),
        email=request.email,
        name=request.name,
        hashed_password=get_password_hash(request.password),
        zip_code=request.zip_code,
        is_active=True,
        is_admin=False,
        created_at=datetime.utcnow(),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"New user registered: {user.email}", extra={"user_id": str(user.id)})

    # Create tokens
    access_token = create_access_token(str(user.id), is_admin=user.is_admin)
    refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=60 * 24 * 60,  # 24 hours in seconds
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Login with email and password to receive authentication tokens.",
)
async def login(
    db: DBSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Login user.

    Args:
        form_data: OAuth2 password form (username=email, password)
        db: Database session

    Returns:
        TokenResponse: Authentication tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email (username field contains email)
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    logger.info(f"User logged in: {user.email}", extra={"user_id": str(user.id)})

    # Create tokens
    access_token = create_access_token(str(user.id), is_admin=user.is_admin)
    refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=60 * 24 * 60,  # 24 hours in seconds
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh Token",
    description="Get a new access token using a refresh token.",
)
async def refresh_token(refresh_token: str, db: DBSession):
    """
    Refresh access token.

    Args:
        refresh_token: JWT refresh token
        db: Database session

    Returns:
        TokenResponse: New authentication tokens

    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = decode_jwt(refresh_token)
        user_id = payload.get("sub")
        token_type = payload.get("type")

        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Create new tokens
        new_access_token = create_access_token(str(user.id), is_admin=user.is_admin)
        new_refresh_token = create_refresh_token(str(user.id))

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=60 * 24 * 60,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User",
    description="Get information about the currently authenticated user.",
)
async def get_current_user_info(current_user: CurrentUser):
    """
    Get current user information.

    Args:
        current_user: Authenticated user

    Returns:
        UserResponse: User information
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
    )
