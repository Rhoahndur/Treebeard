"""
Admin-specific dependencies for RBAC.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status

from ...models.user import User
from ..auth_dependencies import get_current_user


async def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Require that the current user is an admin.

    This dependency checks that:
    1. User is authenticated (via get_current_user)
    2. User account is active
    3. User has admin privileges

    Args:
        current_user: Current authenticated user

    Returns:
        User: Admin user

    Raises:
        HTTPException: If user is not an admin (403 Forbidden)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required.",
        )

    return current_user


# Type alias for dependency injection
AdminUser = Annotated[User, Depends(require_admin)]
