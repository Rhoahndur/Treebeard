"""
Database connection and session management.
Story 7.2 - Epic 7: Performance Optimization

Optimized configuration for:
- Connection pooling (10-20 connections for production)
- Query performance monitoring
- Health checks and timeouts
- Prepared statement caching
"""

import logging
import time
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from .settings import settings

logger = logging.getLogger(__name__)

# Optimized database engine configuration
# Connection pool sized for 10,000+ concurrent users
# Target: Sub-100ms query performance (P95)
engine = create_engine(
    settings.database_url,
    # Connection Pool Configuration
    poolclass=QueuePool,
    pool_size=settings.database_pool_size,        # Base pool size (10-20)
    max_overflow=settings.database_max_overflow,  # Additional connections (10-20)
    pool_pre_ping=True,                           # Health check before using connection
    pool_recycle=3600,                            # Recycle connections after 1 hour
    pool_timeout=30,                              # Wait time for connection (seconds)

    # Query Performance
    echo=settings.database_echo,                  # Log queries (disable in production)
    echo_pool=False,                              # Don't log pool operations

    # Connection Configuration
    connect_args={
        "connect_timeout": 10,                    # Connection timeout
        "options": "-c statement_timeout=30000"   # 30s query timeout
        if "postgresql" in settings.database_url else {},
    },

    # Execution Options
    execution_options={
        "postgresql_readonly": False,
        "postgresql_deferrable": False,
    },
)


# Configure SQLite for foreign key support (if using SQLite for testing)
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key support for SQLite connections."""
    if "sqlite" in settings.database_url:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Yields a database session and ensures it's closed after use.

    Usage in FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# QUERY PERFORMANCE MONITORING
# ============================================================================

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Record query start time for performance monitoring."""
    conn.info.setdefault("query_start_time", []).append(time.time())


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries for optimization."""
    total_time = time.time() - conn.info["query_start_time"].pop(-1)

    # Log queries slower than 100ms (P95 target)
    if total_time > 0.1:
        logger.warning(
            f"Slow query detected ({total_time * 1000:.2f}ms): "
            f"{statement[:200]}{'...' if len(statement) > 200 else ''}"
        )


# ============================================================================
# DATABASE UTILITIES
# ============================================================================

def get_pool_status() -> dict:
    """
    Get current connection pool status.

    Returns:
        Dictionary with pool statistics
    """
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total_connections": pool.size() + pool.overflow(),
    }


@contextmanager
def get_db_session():
    """
    Context manager for database session.

    Usage:
        with get_db_session() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def health_check_db() -> bool:
    """
    Perform database health check.

    Returns:
        True if database is healthy, False otherwise
    """
    try:
        with get_db_session() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def analyze_query(db: Session, query_text: str) -> dict:
    """
    Analyze query performance using EXPLAIN ANALYZE.

    Args:
        db: Database session
        query_text: SQL query to analyze

    Returns:
        Dictionary with query analysis results
    """
    try:
        result = db.execute(text(f"EXPLAIN ANALYZE {query_text}"))
        analysis = [row[0] for row in result]
        return {
            "query": query_text,
            "analysis": analysis,
        }
    except Exception as e:
        logger.error(f"Query analysis failed: {e}")
        return {
            "query": query_text,
            "error": str(e),
        }
