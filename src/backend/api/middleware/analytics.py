"""
Analytics Middleware for FastAPI

Automatically tracks all API requests with timing, status codes, and errors.
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

from ...services.analytics_service import get_analytics_service

logger = logging.getLogger(__name__)


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track API request analytics.

    Tracks:
    - Request endpoint and method
    - Response status code
    - Request duration
    - Errors
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.analytics = get_analytics_service()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and track analytics"""
        # Start timer
        start_time = time.time()

        # Get request info
        endpoint = request.url.path
        method = request.method
        user_id = None

        # Try to get user ID from request state (if authenticated)
        if hasattr(request.state, "user_id"):
            user_id = request.state.user_id

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Track successful request
            await self.analytics.track_api_request(
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                duration_ms=duration_ms,
                user_id=user_id
            )

            return response

        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Track error
            await self.analytics.track_error(
                endpoint=endpoint,
                error_type=type(e).__name__,
                status_code=500,
                error_message=str(e),
                user_id=user_id
            )

            # Re-raise exception
            raise


class PerformanceTimer:
    """
    Context manager for tracking performance of specific operations.

    Usage:
        async with PerformanceTimer("recommendation_generation", user_id):
            # Your code here
            pass
    """

    def __init__(self, operation_name: str, user_id=None):
        self.operation_name = operation_name
        self.user_id = user_id
        self.start_time = None
        self.analytics = get_analytics_service()

    async def __aenter__(self):
        self.start_time = time.time()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000

        if exc_type is None:
            # Success
            await self.analytics.track_event(
                event_type="operation_completed",
                properties={
                    "operation": self.operation_name,
                    "duration_ms": duration_ms,
                    "success": True
                },
                user_id=self.user_id
            )
        else:
            # Error
            await self.analytics.track_event(
                event_type="operation_failed",
                properties={
                    "operation": self.operation_name,
                    "duration_ms": duration_ms,
                    "success": False,
                    "error_type": exc_type.__name__,
                    "error_message": str(exc_val)
                },
                user_id=self.user_id
            )

        return False  # Don't suppress exceptions
