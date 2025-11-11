"""
Rate Limiting Middleware.

Implements rate limiting to prevent API abuse.
"""

import logging
import time
from typing import Callable, Dict, Optional

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from ...services.cache_service import get_cache_service

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.

    Limits requests per user and per IP address to prevent abuse.

    Default limits:
    - 100 requests per minute per authenticated user
    - 1000 requests per hour per IP address
    - Custom limits for expensive endpoints
    """

    def __init__(
        self,
        app,
        requests_per_minute_per_user: int = 100,
        requests_per_hour_per_ip: int = 1000,
        custom_limits: Optional[Dict[str, int]] = None,
    ):
        """
        Initialize rate limiter.

        Args:
            app: FastAPI application
            requests_per_minute_per_user: Max requests per minute per user
            requests_per_hour_per_ip: Max requests per hour per IP
            custom_limits: Custom limits for specific endpoints
        """
        super().__init__(app)
        self.requests_per_minute_per_user = requests_per_minute_per_user
        self.requests_per_hour_per_ip = requests_per_hour_per_ip
        self.custom_limits = custom_limits or {
            "/api/v1/recommendations/generate": 10,  # 10 per minute
        }
        self.cache = get_cache_service()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Check rate limits and process request.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response: Response from handler

        Raises:
            HTTPException: If rate limit exceeded (429)
        """
        # Skip rate limiting for health check and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get identifiers
        ip_address = request.client.host if request.client else "unknown"
        user_id = None

        # Try to get user ID from JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from ..auth.jwt import decode_jwt

                token = auth_header.split(" ")[1]
                payload = decode_jwt(token)
                user_id = payload.get("sub")
            except Exception:
                pass  # Failed to decode, continue with IP-only rate limiting

        # Check rate limits
        if user_id:
            # Check user rate limit (per minute)
            await self._check_user_rate_limit(user_id, request.url.path)

        # Check IP rate limit (per hour)
        await self._check_ip_rate_limit(ip_address)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit-User"] = str(
            self.requests_per_minute_per_user
        )
        response.headers["X-RateLimit-Limit-IP"] = str(
            self.requests_per_hour_per_ip
        )

        return response

    async def _check_user_rate_limit(self, user_id: str, path: str) -> None:
        """
        Check rate limit for authenticated user.

        Args:
            user_id: User ID
            path: Request path

        Raises:
            HTTPException: If rate limit exceeded
        """
        # Check if path has custom limit
        limit = self.requests_per_minute_per_user
        window = 60  # 1 minute

        for custom_path, custom_limit in self.custom_limits.items():
            if path.startswith(custom_path):
                limit = custom_limit
                break

        # Get current count
        key = f"rate_limit:user:{user_id}:{int(time.time() // window)}"
        count = await self.cache.get(key)

        if count is None:
            count = 0

        count = int(count) if count else 0

        if count >= limit:
            logger.warning(
                f"Rate limit exceeded for user {user_id}: {count}/{limit}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {limit} requests per minute.",
                headers={
                    "Retry-After": str(window),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + window),
                },
            )

        # Increment counter
        await self.cache.set(key, count + 1, ttl=window)

    async def _check_ip_rate_limit(self, ip_address: str) -> None:
        """
        Check rate limit for IP address.

        Args:
            ip_address: Client IP address

        Raises:
            HTTPException: If rate limit exceeded
        """
        limit = self.requests_per_hour_per_ip
        window = 3600  # 1 hour

        # Get current count
        key = f"rate_limit:ip:{ip_address}:{int(time.time() // window)}"
        count = await self.cache.get(key)

        if count is None:
            count = 0

        count = int(count) if count else 0

        if count >= limit:
            logger.warning(
                f"Rate limit exceeded for IP {ip_address}: {count}/{limit}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {limit} requests per hour.",
                headers={
                    "Retry-After": str(window),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + window),
                },
            )

        # Increment counter
        await self.cache.set(key, count + 1, ttl=window)
