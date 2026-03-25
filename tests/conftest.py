"""
Shared test fixtures for TreeBeard backend tests.

Provides SQLite-backed database session, FastAPI test client, and async DB
session so that backend and integration tests can run without PostgreSQL.
"""

import os
import sys
from uuid import uuid4

# Environment overrides — MUST happen before any src.backend import so that
# Settings() reads these values instead of production defaults.
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("MONITORING_ENABLED", "false")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# SQLite DDL compatibility for PostgreSQL-only column types.
# Must be registered before any model import triggers metadata reflection.
if not hasattr(SQLiteTypeCompiler, "visit_ARRAY"):
    SQLiteTypeCompiler.visit_ARRAY = lambda self, type_, **kw: "JSON"
if not hasattr(SQLiteTypeCompiler, "visit_JSONB"):
    SQLiteTypeCompiler.visit_JSONB = lambda self, type_, **kw: "JSON"

import src.backend.models  # noqa: F401  — registers all tables with Base.metadata
from src.backend.api.main import app
from src.backend.config.database import get_db
from src.backend.models.base import Base
from src.backend.models.user import User

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Patch the database module so middleware / code that uses SessionLocal
# directly (not through the get_db FastAPI dependency) hits the test DB.
#
# Because "src/backend" is on sys.path, Python maintains TWO module objects
# for the same file — "src.backend.config.database" and "config.database".
# Middleware imports via the short path, so we must reconfigure both.
for _mod_key in ("src.backend.config.database", "config.database"):
    _mod = sys.modules.get(_mod_key)
    if _mod and hasattr(_mod, "SessionLocal"):
        _mod.SessionLocal.configure(bind=engine)
        _mod.engine = engine


@pytest.fixture()
def db():
    """Yield a clean database session; tables are created/dropped per test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    """FastAPI TestClient with get_db overridden to use the test session."""
    def _override():
        yield db

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def async_db(db):
    """Alias for the synchronous session, usable in @pytest.mark.asyncio tests.

    SQLite has no async driver, but the async service functions perform
    synchronous ORM operations internally, so a sync session works fine.
    """
    return db


@pytest.fixture()
def admin_user(db):
    """Create an admin user for testing."""
    user = User(
        id=uuid4(),
        email="admin@test.com",
        name="Admin User",
        hashed_password="hashed_password",
        zip_code="78701",
        property_type="residential",
        is_active=True,
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def regular_user(db):
    """Create a regular (non-admin) user for testing."""
    user = User(
        id=uuid4(),
        email="regular@test.com",
        name="Regular User",
        hashed_password="hashed_password",
        zip_code="78701",
        property_type="residential",
        is_active=True,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def auth_headers():
    """Factory fixture: call with a user to get JWT auth headers."""
    from src.backend.api.auth.jwt import create_access_token

    def _make(user):
        token = create_access_token(str(user.id), is_admin=user.is_admin)
        return {"Authorization": f"Bearer {token}"}

    return _make
