"""
Audit middleware for automatically logging admin API calls.
"""

import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ...config.database import get_db
from ...services.audit_service import log_admin_action_sync

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically log all admin API calls to the audit log.

    This middleware:
    1. Intercepts all requests to admin endpoints (/api/v1/admin/*)
    2. Extracts user information from the request state (set by auth middleware)
    3. Logs the action after the request completes successfully
    4. Captures IP address and User-Agent for security tracking
    """

    def __init__(self, app: ASGIApp):
        """
        Initialize the audit middleware.

        Args:
            app: ASGI application
        """
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and log admin actions.

        Args:
            request: Incoming request
            call_next: Next middleware or endpoint

        Returns:
            Response: Response from the endpoint
        """
        # Only audit admin endpoints
        if not request.url.path.startswith("/api/v1/admin/"):
            return await call_next(request)

        # Skip audit log viewing endpoints to avoid recursive logging
        if "/api/v1/admin/audit-logs" in request.url.path:
            return await call_next(request)

        # Extract request details
        method = request.method
        path = request.url.path
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Process the request
        response = await call_next(request)

        # Only log successful requests (2xx status codes)
        if 200 <= response.status_code < 300:
            # Try to get the current user from request state (set by auth middleware)
            current_user = getattr(request.state, "user", None)

            if current_user and current_user.is_admin:
                # Determine action and resource based on path and method
                action, resource_type = _determine_action_and_resource(method, path)

                # Log the action (use synchronous version to avoid blocking)
                try:
                    # Get a database session
                    db_gen = get_db()
                    db = next(db_gen)

                    log_admin_action_sync(
                        db=db,
                        admin_user_id=current_user.id,
                        action=action,
                        resource_type=resource_type,
                        resource_id=None,  # Could extract from path if needed
                        details={"method": method, "path": path, "status_code": response.status_code},
                        ip_address=ip_address,
                        user_agent=user_agent,
                    )

                    # Close the session
                    try:
                        next(db_gen)
                    except StopIteration:
                        pass

                except Exception as e:
                    logger.error(f"Failed to log admin action: {e}", exc_info=True)

        return response


def _determine_action_and_resource(method: str, path: str) -> tuple[str, str]:
    """
    Determine the action and resource type from the request method and path.

    Args:
        method: HTTP method
        path: Request path

    Returns:
        tuple[str, str]: (action, resource_type)
    """
    # Parse the path to determine resource type
    path_parts = path.split("/")

    # Default values
    resource_type = "unknown"
    action = f"{method.lower()}_unknown"

    # Extract resource type from path
    # Path format: /api/v1/admin/{resource_type}/...
    if len(path_parts) >= 5:
        resource_type = path_parts[4]

    # Determine action based on method and resource
    if method == "GET":
        if path.endswith("/stats"):
            action = "view_stats"
        else:
            action = f"view_{resource_type}"
    elif method == "POST":
        action = f"{resource_type}_created"
    elif method == "PUT" or method == "PATCH":
        if "role" in path:
            action = "user_role_updated"
        else:
            action = f"{resource_type}_updated"
    elif method == "DELETE":
        action = f"{resource_type}_deleted"

    return action, resource_type
