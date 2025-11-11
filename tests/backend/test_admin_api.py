"""
Tests for admin API endpoints.

Tests RBAC enforcement, user management, plan management, and system stats.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from src.backend.models.audit_log import AuditLog
from src.backend.models.plan import PlanCatalog, Supplier
from src.backend.models.recommendation import Recommendation
from src.backend.models.user import User
from src.backend.schemas.admin_schemas import (
    PlanCatalogCreate,
    PlanCatalogUpdate,
    UserRoleUpdate,
)


class TestAdminRBAC:
    """Test Role-Based Access Control for admin endpoints."""

    def test_non_admin_cannot_access_admin_endpoints(self, client, regular_user, auth_headers_regular):
        """Non-admin users should receive 403 Forbidden."""
        response = client.get("/api/v1/admin/users", headers=auth_headers_regular)
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()

    def test_admin_can_access_admin_endpoints(self, client, admin_user, auth_headers_admin):
        """Admin users should have access to admin endpoints."""
        response = client.get("/api/v1/admin/users", headers=auth_headers_admin)
        assert response.status_code == 200

    def test_unauthenticated_cannot_access_admin_endpoints(self, client):
        """Unauthenticated users should receive 401 Unauthorized."""
        response = client.get("/api/v1/admin/users")
        assert response.status_code == 401


class TestUserManagement:
    """Test user management endpoints."""

    def test_list_users(self, client, admin_user, regular_user, auth_headers_admin):
        """Test listing all users with pagination."""
        response = client.get("/api/v1/admin/users", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()
        assert "users" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert "has_more" in data
        assert data["total"] >= 2  # At least admin and regular user

    def test_list_users_with_filters(self, client, admin_user, auth_headers_admin):
        """Test filtering users by active status and admin role."""
        # Filter by admin role
        response = client.get(
            "/api/v1/admin/users?is_admin=true",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert all(user["is_admin"] for user in data["users"])

    def test_list_users_pagination(self, client, admin_user, auth_headers_admin):
        """Test pagination parameters."""
        response = client.get(
            "/api/v1/admin/users?limit=10&offset=0",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 0

    def test_get_user_detail(self, client, admin_user, regular_user, auth_headers_admin):
        """Test getting detailed user information."""
        response = client.get(
            f"/api/v1/admin/users/{regular_user.id}",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == str(regular_user.id)
        assert data["email"] == regular_user.email
        assert data["name"] == regular_user.name
        assert "activity" in data
        assert "total_recommendations" in data["activity"]
        assert "total_feedback" in data["activity"]

    def test_get_user_detail_not_found(self, client, admin_user, auth_headers_admin):
        """Test getting details for non-existent user."""
        fake_user_id = uuid4()
        response = client.get(
            f"/api/v1/admin/users/{fake_user_id}",
            headers=auth_headers_admin
        )
        assert response.status_code == 404

    def test_update_user_role(self, client, db, admin_user, regular_user, auth_headers_admin):
        """Test promoting user to admin."""
        # Promote user to admin
        response = client.put(
            f"/api/v1/admin/users/{regular_user.id}/role",
            json={"is_admin": True},
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        assert data["is_admin"] is True

        # Verify audit log was created
        audit_logs = db.query(AuditLog).filter(
            AuditLog.action == "user_role_updated",
            AuditLog.resource_id == regular_user.id
        ).all()
        assert len(audit_logs) > 0

    def test_cannot_change_own_role(self, client, admin_user, auth_headers_admin):
        """Admin should not be able to change their own role."""
        response = client.put(
            f"/api/v1/admin/users/{admin_user.id}/role",
            json={"is_admin": False},
            headers=auth_headers_admin
        )
        assert response.status_code == 400
        assert "own" in response.json()["detail"].lower()

    def test_soft_delete_user(self, client, db, admin_user, regular_user, auth_headers_admin):
        """Test soft deleting a user."""
        response = client.delete(
            f"/api/v1/admin/users/{regular_user.id}",
            headers=auth_headers_admin
        )
        assert response.status_code == 204

        # Verify user is soft deleted
        db.refresh(regular_user)
        assert regular_user.is_active is False

        # Verify audit log was created
        audit_logs = db.query(AuditLog).filter(
            AuditLog.action == "user_deleted",
            AuditLog.resource_id == regular_user.id
        ).all()
        assert len(audit_logs) > 0

    def test_cannot_delete_own_account(self, client, admin_user, auth_headers_admin):
        """Admin should not be able to delete their own account."""
        response = client.delete(
            f"/api/v1/admin/users/{admin_user.id}",
            headers=auth_headers_admin
        )
        assert response.status_code == 400
        assert "own" in response.json()["detail"].lower()


class TestPlanManagement:
    """Test plan management endpoints."""

    def test_list_plans(self, client, admin_user, sample_supplier, sample_plan, auth_headers_admin):
        """Test listing all plans with pagination."""
        response = client.get("/api/v1/admin/plans", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()
        assert "plans" in data
        assert "total" in data
        assert data["total"] >= 1

    def test_list_plans_with_filters(self, client, admin_user, sample_supplier, sample_plan, auth_headers_admin):
        """Test filtering plans by supplier and active status."""
        # Filter by supplier
        response = client.get(
            f"/api/v1/admin/plans?supplier_id={sample_supplier.id}",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert all(plan["supplier_id"] == str(sample_supplier.id) for plan in data["plans"])

    def test_create_plan(self, client, db, admin_user, sample_supplier, auth_headers_admin):
        """Test creating a new plan."""
        plan_data = {
            "supplier_id": str(sample_supplier.id),
            "plan_name": "Test Plan",
            "plan_type": "fixed",
            "rate_structure": {"base_rate": 0.10},
            "contract_length_months": 12,
            "early_termination_fee": 100.00,
            "renewable_percentage": 50.00,
            "available_regions": ["78701", "78702"],
            "plan_description": "Test plan description",
        }

        response = client.post(
            "/api/v1/admin/plans",
            json=plan_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 201

        data = response.json()
        assert data["plan_name"] == "Test Plan"
        assert data["plan_type"] == "fixed"
        assert data["supplier_id"] == str(sample_supplier.id)

        # Verify audit log was created
        audit_logs = db.query(AuditLog).filter(
            AuditLog.action == "plan_created"
        ).all()
        assert len(audit_logs) > 0

    def test_create_plan_invalid_supplier(self, client, admin_user, auth_headers_admin):
        """Test creating plan with non-existent supplier."""
        plan_data = {
            "supplier_id": str(uuid4()),
            "plan_name": "Test Plan",
            "plan_type": "fixed",
            "rate_structure": {"base_rate": 0.10},
            "contract_length_months": 12,
            "available_regions": ["78701"],
        }

        response = client.post(
            "/api/v1/admin/plans",
            json=plan_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 400

    def test_update_plan(self, client, db, admin_user, sample_plan, auth_headers_admin):
        """Test updating a plan."""
        update_data = {
            "plan_name": "Updated Plan Name",
            "renewable_percentage": 75.00,
        }

        response = client.put(
            f"/api/v1/admin/plans/{sample_plan.id}",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        assert data["plan_name"] == "Updated Plan Name"
        assert float(data["renewable_percentage"]) == 75.00

        # Verify audit log was created
        audit_logs = db.query(AuditLog).filter(
            AuditLog.action == "plan_updated",
            AuditLog.resource_id == sample_plan.id
        ).all()
        assert len(audit_logs) > 0

    def test_update_plan_not_found(self, client, admin_user, auth_headers_admin):
        """Test updating non-existent plan."""
        fake_plan_id = uuid4()
        response = client.put(
            f"/api/v1/admin/plans/{fake_plan_id}",
            json={"plan_name": "Updated"},
            headers=auth_headers_admin
        )
        assert response.status_code == 404

    def test_soft_delete_plan(self, client, db, admin_user, sample_plan, auth_headers_admin):
        """Test soft deleting a plan."""
        response = client.delete(
            f"/api/v1/admin/plans/{sample_plan.id}",
            headers=auth_headers_admin
        )
        assert response.status_code == 204

        # Verify plan is soft deleted
        db.refresh(sample_plan)
        assert sample_plan.is_active is False

        # Verify audit log was created
        audit_logs = db.query(AuditLog).filter(
            AuditLog.action == "plan_deleted",
            AuditLog.resource_id == sample_plan.id
        ).all()
        assert len(audit_logs) > 0


class TestRecommendationManagement:
    """Test recommendation management endpoints."""

    def test_list_recommendations(self, client, admin_user, auth_headers_admin):
        """Test listing all recommendations."""
        response = client.get("/api/v1/admin/recommendations", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()
        assert "recommendations" in data
        assert "total" in data

    def test_list_recommendations_with_filters(self, client, admin_user, regular_user, auth_headers_admin):
        """Test filtering recommendations by user and date range."""
        # Filter by user
        response = client.get(
            f"/api/v1/admin/recommendations?user_id={regular_user.id}",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert all(rec["user_id"] == str(regular_user.id) for rec in data["recommendations"])


class TestSystemStatistics:
    """Test system statistics endpoint."""

    def test_get_system_stats(self, client, admin_user, regular_user, auth_headers_admin):
        """Test getting system-wide statistics."""
        response = client.get("/api/v1/admin/stats", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()
        assert "total_users" in data
        assert "active_users" in data
        assert "inactive_users" in data
        assert "admin_users" in data
        assert "total_recommendations" in data
        assert "total_feedback" in data
        assert "avg_recommendations_per_user" in data
        assert "total_plans" in data
        assert "total_suppliers" in data

        # Verify counts are reasonable
        assert data["total_users"] >= 2  # At least admin and regular user
        assert data["admin_users"] >= 1  # At least one admin


# Fixtures


@pytest.fixture
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


@pytest.fixture
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


@pytest.fixture
def auth_headers_regular(regular_user):
    """Generate JWT auth headers for regular user."""
    from src.backend.api.auth.jwt import create_access_token
    token = create_access_token(str(regular_user.id), is_admin=False)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_admin(admin_user):
    """Generate JWT auth headers for admin user."""
    from src.backend.api.auth.jwt import create_access_token
    token = create_access_token(str(admin_user.id), is_admin=True)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_supplier(db):
    """Create a sample supplier for testing."""
    supplier = Supplier(
        id=uuid4(),
        supplier_name="Test Supplier",
        average_rating=Decimal("4.5"),
        review_count=100,
        is_active=True,
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@pytest.fixture
def sample_plan(db, sample_supplier):
    """Create a sample plan for testing."""
    plan = PlanCatalog(
        id=uuid4(),
        supplier_id=sample_supplier.id,
        plan_name="Test Plan",
        plan_type="fixed",
        rate_structure={"base_rate": 0.10},
        contract_length_months=12,
        early_termination_fee=Decimal("100.00"),
        renewable_percentage=Decimal("50.00"),
        available_regions=["78701", "78702"],
        is_active=True,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan
