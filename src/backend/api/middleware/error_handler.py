"""
Error Handler Middleware.

Global error handling and standardized error responses.
"""

import logging
from typing import Callable

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for global error handling.

    Catches unhandled exceptions and returns standardized error responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """
        Handle errors and return standardized responses.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            JSONResponse: Response (success or error)
        """
        try:
            return await call_next(request)

        except RequestValidationError as exc:
            # Pydantic validation error (422)
            request_id = getattr(request.state, "request_id", "unknown")

            error_details = {
                "request_id": request_id,
                "error": "Validation Error",
                "message": "Invalid request data",
                "details": exc.errors(),
            }

            logger.warning(
                f"Validation error: {request.url.path}",
                extra={"error": error_details},
            )

            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=error_details,
            )

        except ValidationError as exc:
            # Pydantic validation error (internal)
            request_id = getattr(request.state, "request_id", "unknown")

            error_details = {
                "request_id": request_id,
                "error": "Validation Error",
                "message": "Data validation failed",
                "details": exc.errors(),
            }

            logger.warning(
                f"Internal validation error: {request.url.path}",
                extra={"error": error_details},
            )

            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=error_details,
            )

        except SQLAlchemyError as exc:
            # Database error (500)
            request_id = getattr(request.state, "request_id", "unknown")

            error_details = {
                "request_id": request_id,
                "error": "Database Error",
                "message": "A database error occurred",
            }

            logger.error(
                f"Database error: {request.url.path} - {exc}",
                extra={"error": error_details},
                exc_info=True,
            )

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_details,
            )

        except ValueError as exc:
            # Invalid value (400)
            request_id = getattr(request.state, "request_id", "unknown")

            error_details = {
                "request_id": request_id,
                "error": "Bad Request",
                "message": str(exc),
            }

            logger.warning(
                f"Value error: {request.url.path} - {exc}",
                extra={"error": error_details},
            )

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=error_details,
            )

        except Exception as exc:
            # Unhandled exception (500)
            request_id = getattr(request.state, "request_id", "unknown")

            error_details = {
                "request_id": request_id,
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "type": type(exc).__name__,
            }

            logger.error(
                f"Unhandled exception: {request.url.path} - {exc}",
                extra={"error": error_details},
                exc_info=True,
            )

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_details,
            )
