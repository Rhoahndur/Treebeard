"""
Cache Middleware.

Implements HTTP caching for GET requests.
"""

import hashlib
import json
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from services.cache_service import get_cache_service

logger = logging.getLogger(__name__)


class CacheMiddleware(BaseHTTPMiddleware):
    """
    Cache middleware for GET requests.

    Caches responses for GET requests to improve performance.
    Adds X-Cache-Status header (HIT or MISS) to responses.
    """

    def __init__(
        self,
        app,
        default_ttl: int = 300,  # 5 minutes
        cacheable_paths: list = None,
    ):
        """
        Initialize cache middleware.

        Args:
            app: FastAPI application
            default_ttl: Default cache TTL in seconds
            cacheable_paths: List of path prefixes to cache
        """
        super().__init__(app)
        self.default_ttl = default_ttl
        self.cacheable_paths = cacheable_paths or [
            "/api/v1/plans",
            "/api/v1/recommendations",
        ]
        self.cache = get_cache_service()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Check cache and process request.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response: Response from cache or handler
        """
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)

        # Check if path is cacheable
        if not any(
            request.url.path.startswith(path) for path in self.cacheable_paths
        ):
            return await call_next(request)

        # Generate cache key
        cache_key = self._generate_cache_key(request)

        # Try to get from cache
        try:
            cached_response = await self.cache.get(cache_key)

            if cached_response:
                logger.debug(f"Cache HIT: {cache_key}")

                # Parse cached response
                cached_data = json.loads(cached_response)

                # Create response
                response = Response(
                    content=cached_data["content"],
                    status_code=cached_data["status_code"],
                    headers=cached_data.get("headers", {}),
                    media_type=cached_data.get("media_type", "application/json"),
                )

                # Add cache header
                response.headers["X-Cache-Status"] = "HIT"
                response.headers["X-Request-ID"] = getattr(
                    request.state, "request_id", "unknown"
                )

                return response

        except Exception as exc:
            logger.warning(f"Cache error: {exc}")
            # Continue without cache on error

        # Cache MISS - process request
        logger.debug(f"Cache MISS: {cache_key}")
        response = await call_next(request)

        # Cache successful responses
        if response.status_code == 200:
            try:
                # Get response body
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk

                # Cache response data
                cache_data = {
                    "content": response_body.decode(),
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "media_type": response.media_type,
                }

                # Determine TTL
                ttl = self._get_ttl_for_path(request.url.path)

                # Store in cache
                await self.cache.set(
                    cache_key,
                    json.dumps(cache_data),
                    ttl=ttl,
                )

                # Recreate response
                response = Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )

            except Exception as exc:
                logger.warning(f"Failed to cache response: {exc}")

        # Add cache header
        response.headers["X-Cache-Status"] = "MISS"

        return response

    def _generate_cache_key(self, request: Request) -> str:
        """
        Generate cache key for request.

        Args:
            request: Request object

        Returns:
            str: Cache key
        """
        # Include path, query params, and auth header
        key_parts = [
            request.url.path,
            str(sorted(request.query_params.items())),
        ]

        # Include user ID if authenticated
        auth_header = request.headers.get("Authorization", "")
        if auth_header:
            key_parts.append(auth_header)

        key_string = "|".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()

        return f"cache:response:{key_hash}"

    def _get_ttl_for_path(self, path: str) -> int:
        """
        Get TTL for specific path.

        Args:
            path: Request path

        Returns:
            int: TTL in seconds
        """
        # Custom TTLs for different endpoints
        if path.startswith("/api/v1/plans/catalog"):
            return 3600  # 1 hour for plan catalog
        elif path.startswith("/api/v1/recommendations"):
            return 86400  # 24 hours for recommendations
        else:
            return self.default_ttl  # Default 5 minutes
