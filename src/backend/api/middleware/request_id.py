"""
Request ID Middleware.

Adds unique request ID to all requests for tracing and correlation.
"""

import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID to all requests.

    The request ID can be:
    - Provided by the client in X-Request-ID header
    - Generated automatically if not provided

    The request ID is:
    - Stored in request.state.request_id
    - Returned in X-Request-ID response header
    - Used for logging correlation
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add request ID to request and response.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response: Response with X-Request-ID header
        """
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store in request state for access in route handlers
        request.state.request_id = request_id

        # Call next middleware/handler
        response = await call_next(request)

        # Add to response headers
        response.headers["X-Request-ID"] = request_id

        return response
