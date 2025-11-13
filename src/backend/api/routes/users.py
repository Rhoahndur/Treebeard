"""
User Management Endpoints.

User profile and preferences management.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from models.user import UserPreference
from api.auth_dependencies import CurrentAdminUser, CurrentUser, DBSession
from api.schemas.common import MessageResponse

router = APIRouter()
logger = logging.getLogger(__name__)


# Request/Response Schemas


class UserPreferencesRequest(BaseModel):
    """User preferences update request."""

    cost_priority: int = Field(..., ge=0, le=100, description="Cost priority (0-100)")
    flexibility_priority: int = Field(
        ..., ge=0, le=100, description="Flexibility priority (0-100)"
    )
    renewable_priority: int = Field(
        ..., ge=0, le=100, description="Renewable energy priority (0-100)"
    )
    rating_priority: int = Field(
        ..., ge=0, le=100, description="Supplier rating priority (0-100)"
    )


class UserPreferencesResponse(BaseModel):
    """User preferences response."""

    cost_priority: int
    flexibility_priority: int
    renewable_priority: int
    rating_priority: int
    updated_at: datetime


class UpdateUserRequest(BaseModel):
    """User profile update request."""

    name: Optional[str] = Field(None, min_length=1, description="User name")
    email: Optional[EmailStr] = Field(None, description="User email")
    zip_code: Optional[str] = Field(
        None, min_length=5, max_length=10, description="ZIP code"
    )


# Endpoints


@router.post(
    "/preferences",
    response_model=UserPreferencesResponse,
    summary="Save User Preferences",
    description="Save or update user's plan selection preferences.",
)
async def save_preferences(
    request: UserPreferencesRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Save user preferences.

    Args:
        request: Preferences request
        current_user: Authenticated user
        db: Database session

    Returns:
        UserPreferencesResponse: Updated preferences
    """
    # Validate priorities sum to 100
    total = (
        request.cost_priority
        + request.flexibility_priority
        + request.renewable_priority
        + request.rating_priority
    )

    if total != 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Priorities must sum to 100 (current sum: {total})",
        )

    # Get or create preferences
    preferences = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == current_user.id)
        .first()
    )

    if preferences:
        # Update existing
        preferences.cost_priority = request.cost_priority
        preferences.flexibility_priority = request.flexibility_priority
        preferences.renewable_priority = request.renewable_priority
        preferences.rating_priority = request.rating_priority
        preferences.updated_at = datetime.utcnow()
    else:
        # Create new
        preferences = UserPreference(
            user_id=current_user.id,
            cost_priority=request.cost_priority,
            flexibility_priority=request.flexibility_priority,
            renewable_priority=request.renewable_priority,
            rating_priority=request.rating_priority,
            updated_at=datetime.utcnow(),
        )
        db.add(preferences)

    db.commit()
    db.refresh(preferences)

    logger.info(
        f"Preferences saved for user {current_user.id}",
        extra={"user_id": str(current_user.id)},
    )

    return UserPreferencesResponse(
        cost_priority=preferences.cost_priority,
        flexibility_priority=preferences.flexibility_priority,
        renewable_priority=preferences.renewable_priority,
        rating_priority=preferences.rating_priority,
        updated_at=preferences.updated_at,
    )


@router.get(
    "/preferences",
    response_model=UserPreferencesResponse,
    summary="Get User Preferences",
    description="Get user's current plan selection preferences.",
)
async def get_preferences(current_user: CurrentUser, db: DBSession):
    """
    Get user preferences.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        UserPreferencesResponse: User preferences

    Raises:
        HTTPException: If preferences not found
    """
    preferences = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == current_user.id)
        .first()
    )

    if not preferences:
        # Return default preferences
        return UserPreferencesResponse(
            cost_priority=40,
            flexibility_priority=30,
            renewable_priority=20,
            rating_priority=10,
            updated_at=datetime.utcnow(),
        )

    return UserPreferencesResponse(
        cost_priority=preferences.cost_priority,
        flexibility_priority=preferences.flexibility_priority,
        renewable_priority=preferences.renewable_priority,
        rating_priority=preferences.rating_priority,
        updated_at=preferences.updated_at,
    )


@router.put(
    "/profile",
    response_model=MessageResponse,
    summary="Update User Profile",
    description="Update user profile information.",
)
async def update_profile(
    request: UpdateUserRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Update user profile.

    Args:
        request: Update request
        current_user: Authenticated user
        db: DBSession: Database session

    Returns:
        MessageResponse: Success message

    Raises:
        HTTPException: If email already exists
    """
    # Check if email is being changed to existing email
    if request.email and request.email != current_user.email:
        from models.user import User

        existing = db.query(User).filter(User.email == request.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )

    # Update user
    if request.name:
        current_user.name = request.name
    if request.email:
        current_user.email = request.email
    if request.zip_code:
        current_user.zip_code = request.zip_code

    db.commit()

    logger.info(
        f"Profile updated for user {current_user.id}",
        extra={"user_id": str(current_user.id)},
    )

    return MessageResponse(
        message="Profile updated successfully",
        success=True,
    )


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Delete User (Admin Only)",
    description="Delete a user account. Admin only.",
)
async def delete_user(
    user_id: str,
    current_admin: CurrentAdminUser,
    db: DBSession,
):
    """
    Delete a user (admin only).

    Args:
        user_id: User ID to delete
        current_admin: Authenticated admin user
        db: Database session

    Returns:
        MessageResponse: Success message

    Raises:
        HTTPException: If user not found
    """
    from uuid import UUID

    from models.user import User

    user = db.query(User).filter(User.id == UUID(user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Don't allow deleting yourself
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    db.delete(user)
    db.commit()

    logger.info(
        f"User {user_id} deleted by admin {current_admin.id}",
        extra={"deleted_user_id": user_id, "admin_id": str(current_admin.id)},
    )

    return MessageResponse(
        message="User deleted successfully",
        success=True,
    )
