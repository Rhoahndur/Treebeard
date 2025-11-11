"""
API dependencies for dependency injection.
"""

from .admin import AdminUser, require_admin

__all__ = [
    "require_admin",
    "AdminUser",
]
