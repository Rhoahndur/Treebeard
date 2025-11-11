"""
Logging Middleware.

Structured JSON logging for all API requests.
"""

import json
import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for structured logging of all requests.

    Logs request details, response status, and timing information
    in JSON format for easy parsing and analysis.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request and response details.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response: Response from handler
        """
        # Start timer
        start_time = time.time()

        # Get request ID (set by RequestIDMiddleware)
        request_id = getattr(request.state, "request_id", "unknown")

        # Extract request details
        request_details = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }

        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={"request": request_details},
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            response_details = {
                **request_details,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            }

            log_level = logging.INFO
            if response.status_code >= 500:
                log_level = logging.ERROR
            elif response.status_code >= 400:
                log_level = logging.WARNING

            logger.log(
                log_level,
                f"Request completed: {request.method} {request.url.path} "
                f"[{response.status_code}] ({duration_ms:.2f}ms)",
                extra={"response": response_details},
            )

            return response

        except Exception as exc:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            error_details = {
                **request_details,
                "error": str(exc),
                "error_type": type(exc).__name__,
                "duration_ms": round(duration_ms, 2),
            }

            logger.error(
                f"Request failed: {request.method} {request.url.path} - {exc}",
                extra={"error": error_details},
                exc_info=True,
            )

            raise
