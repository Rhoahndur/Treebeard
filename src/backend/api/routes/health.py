"""
Health Check Endpoints.

Provides health check and metrics endpoints for monitoring.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from config.database import get_db
from config.settings import settings
from services.cache_service import get_cache_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.

    Returns the health status of the API and its dependencies.

    Returns:
        dict: Health status information
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "checks": {},
    }

    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "type": "postgresql",
        }
    except Exception as exc:
        logger.error(f"Database health check failed: {exc}")
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(exc),
        }

    # Check Redis cache
    try:
        cache = get_cache_service()
        await cache.set("health_check", "ok", ttl=10)
        value = await cache.get("health_check")

        if value == "ok":
            health_status["checks"]["cache"] = {
                "status": "healthy",
                "type": "redis",
            }
        else:
            health_status["checks"]["cache"] = {
                "status": "degraded",
                "message": "Cache read/write mismatch",
            }
    except Exception as exc:
        logger.warning(f"Cache health check failed: {exc}")
        health_status["checks"]["cache"] = {
            "status": "unhealthy",
            "error": str(exc),
            "message": "Cache unavailable - API will function with degraded performance",
        }

    return health_status


@router.get("/health/live")
async def liveness_probe():
    """
    Kubernetes liveness probe.

    Returns a simple status to indicate the service is running.

    Returns:
        dict: Liveness status
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_probe(db: Session = Depends(get_db)):
    """
    Kubernetes readiness probe.

    Checks if the service is ready to accept traffic.

    Returns:
        dict: Readiness status
    """
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as exc:
        logger.error(f"Readiness check failed: {exc}")
        return {"status": "not ready", "error": str(exc)}


@router.get("/metrics")
async def metrics():
    """
    Metrics endpoint.

    Returns basic metrics for monitoring.

    Returns:
        dict: Application metrics
    """
    # TODO: Implement proper metrics collection
    # For now, return basic information
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "metrics": {
            "note": "Detailed metrics coming soon",
        },
    }
