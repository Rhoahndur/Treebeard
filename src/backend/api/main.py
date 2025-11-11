"""
TreeBeard FastAPI Application.

Main application entry point with middleware, routes, and configuration.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..config.settings import settings
from .middleware.audit_middleware import AuditMiddleware
from .middleware.cache import CacheMiddleware
from .middleware.error_handler import ErrorHandlerMiddleware
from .middleware.logging import LoggingMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.request_id import RequestIDMiddleware
from .routes import (
    admin,
    auth,
    feedback,
    health,
    plans,
    recommendations,
    usage,
    users,
)

# Initialize monitoring
if settings.monitoring_enabled:
    try:
        from ..monitoring import init_apm, init_metrics, init_sentry

        # Initialize Sentry for error tracking
        if settings.sentry_dsn:
            init_sentry(dsn=settings.sentry_dsn, environment=settings.environment)
            logger = logging.getLogger(__name__)
            logger.info("Sentry error tracking initialized")

        # Initialize APM for distributed tracing
        init_apm(provider=settings.apm_provider)
        logger = logging.getLogger(__name__)
        logger.info(f"APM initialized with provider: {settings.apm_provider}")

        # Initialize metrics collection
        init_metrics(backend=settings.metrics_backend)
        logger = logging.getLogger(__name__)
        logger.info(f"Metrics initialized with backend: {settings.metrics_backend}")

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to initialize monitoring: {e}")

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan context manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting TreeBeard API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    yield

    # Shutdown
    logger.info("Shutting down TreeBeard API")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    AI Energy Plan Recommendation Agent API

    This API provides intelligent energy plan recommendations based on usage patterns,
    user preferences, and comprehensive cost analysis. The system analyzes historical
    usage data, compares available plans, and generates personalized explanations
    using AI to help customers make informed decisions about their energy plans.

    ## Features

    - **Usage Analysis**: Analyze 12 months of usage patterns
    - **Smart Recommendations**: Get top 3 personalized plan recommendations
    - **Savings Calculator**: Calculate projected annual savings
    - **AI Explanations**: Natural language explanations for each recommendation
    - **Plan Comparison**: Side-by-side comparison of plans
    - **User Management**: Manage user profiles and preferences

    ## Authentication

    Most endpoints require JWT authentication. Use the `/auth/login` endpoint
    to obtain a JWT token, then include it in the Authorization header:

    ```
    Authorization: Bearer <your-token>
    ```
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Cache-Status"],
)

# Add custom middleware (order matters - last added is executed first)
# 1. Request ID must be first to ensure all logs have request IDs
# 2. Logging comes next to log all requests
# 3. Audit middleware to log admin actions
# 4. Cache middleware before rate limit to cache responses
# 5. Rate limit to prevent abuse
# 6. Error handler last to catch all errors
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CacheMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

# Include routers
app.include_router(
    health.router,
    tags=["Health"]
)

app.include_router(
    auth.router,
    prefix=f"{settings.api_v1_prefix}/auth",
    tags=["Authentication"]
)

app.include_router(
    users.router,
    prefix=f"{settings.api_v1_prefix}/users",
    tags=["Users"]
)

app.include_router(
    recommendations.router,
    prefix=f"{settings.api_v1_prefix}/recommendations",
    tags=["Recommendations"]
)

app.include_router(
    plans.router,
    prefix=f"{settings.api_v1_prefix}/plans",
    tags=["Plans"]
)

app.include_router(
    usage.router,
    prefix=f"{settings.api_v1_prefix}/usage",
    tags=["Usage Data"]
)

app.include_router(
    feedback.router,
    prefix=settings.api_v1_prefix,
    tags=["Feedback"]
)

app.include_router(
    admin.router,
    prefix=f"{settings.api_v1_prefix}/admin",
    tags=["Admin"]
)


@app.get("/")
async def root():
    """
    Root endpoint.

    Returns basic API information.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/version")
async def version():
    """
    Get API version information.
    """
    return {
        "version": settings.app_version,
        "environment": settings.environment,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
