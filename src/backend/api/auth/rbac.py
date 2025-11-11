"""
Role-Based Access Control (RBAC).

Implements permission checking and role-based authorization.
"""

from enum import Enum
from typing import List

from fastapi import HTTPException, status

from ...models.user import User


class Permission(str, Enum):
    """
    User permissions.
    """

    # User permissions
    READ_USER = "read:user"
    UPDATE_USER = "update:user"
    DELETE_USER = "delete:user"

    # Plan permissions
    READ_PLAN = "read:plan"
    CREATE_PLAN = "create:plan"
    UPDATE_PLAN = "update:plan"
    DELETE_PLAN = "delete:plan"

    # Recommendation permissions
    READ_RECOMMENDATION = "read:recommendation"
    CREATE_RECOMMENDATION = "create:recommendation"

    # Admin permissions
    ADMIN_ACCESS = "admin:access"
    ADMIN_USERS = "admin:users"
    ADMIN_PLANS = "admin:plans"
    ADMIN_CACHE = "admin:cache"
    ADMIN_METRICS = "admin:metrics"


# Role to permissions mapping
ROLE_PERMISSIONS = {
    "user": [
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.READ_PLAN,
        Permission.READ_RECOMMENDATION,
        Permission.CREATE_RECOMMENDATION,
    ],
    "admin": [
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.DELETE_USER,
        Permission.READ_PLAN,
        Permission.CREATE_PLAN,
        Permission.UPDATE_PLAN,
        Permission.DELETE_PLAN,
        Permission.READ_RECOMMENDATION,
        Permission.CREATE_RECOMMENDATION,
        Permission.ADMIN_ACCESS,
        Permission.ADMIN_USERS,
        Permission.ADMIN_PLANS,
        Permission.ADMIN_CACHE,
        Permission.ADMIN_METRICS,
    ],
}


def get_user_permissions(user: User) -> List[Permission]:
    """
    Get all permissions for a user based on their role.

    Args:
        user: User object

    Returns:
        List[Permission]: List of permissions
    """
    if user.is_admin:
        return ROLE_PERMISSIONS["admin"]
    return ROLE_PERMISSIONS["user"]


def check_permission(user: User, permission: Permission) -> bool:
    """
    Check if user has a specific permission.

    Args:
        user: User object
        permission: Permission to check

    Returns:
        bool: True if user has permission, False otherwise
    """
    user_permissions = get_user_permissions(user)
    return permission in user_permissions


def require_permission(user: User, permission: Permission) -> None:
    """
    Require a specific permission, raise exception if not authorized.

    Args:
        user: User object
        permission: Permission to require

    Raises:
        HTTPException: If user doesn't have permission
    """
    if not check_permission(user, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {permission.value}",
        )


def require_permissions(user: User, permissions: List[Permission]) -> None:
    """
    Require multiple permissions, raise exception if any are missing.

    Args:
        user: User object
        permissions: List of permissions to require

    Raises:
        HTTPException: If user doesn't have all permissions
    """
    user_permissions = get_user_permissions(user)
    missing = [p for p in permissions if p not in user_permissions]

    if missing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing permissions: {', '.join(p.value for p in missing)}",
        )
