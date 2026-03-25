"""
Tests for Feedback API endpoints.

Story 8.2: Feedback API Endpoints
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.backend.models.plan import PlanCatalog, Supplier
from src.backend.models.user import User


@pytest.fixture
def test_user(db: Session):
    """Create a non-admin test user for feedback tests."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        hashed_password="hashed_password",
        zip_code="10001",
        property_type="residential",
        is_active=True,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def test_plan(db: Session):
    """Create a test supplier + plan for feedback tests."""
    supplier = Supplier(
        id=uuid4(),
        supplier_name="Test Supplier",
        is_active=True,
    )
    db.add(supplier)
    db.flush()

    plan = PlanCatalog(
        id=uuid4(),
        supplier_id=supplier.id,
        plan_name="Test Plan",
        plan_type="fixed",
        rate_structure={"type": "fixed", "rate_per_kwh": 0.105},
        contract_length_months=12,
        early_termination_fee=100.0,
        renewable_percentage=50.0,
        available_regions=["10001"],
        is_active=True,
    )
    db.add(plan)
    db.commit()
    return plan


class TestSubmitPlanFeedback:
    """Tests for POST /api/v1/feedback/plan endpoint."""

    def test_submit_plan_feedback_authenticated(
        self, client: TestClient, test_user: User, test_plan: PlanCatalog, auth_headers
    ):
        """Test submitting plan feedback as authenticated user."""
        feedback_data = {
            "plan_id": str(test_plan.id),
            "rating": 5,
            "feedback_text": "Great plan!",
            "feedback_type": "helpful",
        }

        response = client.post(
            "/api/v1/feedback/plan",
            json=feedback_data,
            headers=auth_headers(test_user),
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "feedback_id" in data
        assert data["message"] == "Thank you for your feedback!"

    def test_submit_plan_feedback_anonymous(
        self, client: TestClient, test_plan: PlanCatalog
    ):
        """Test submitting plan feedback anonymously."""
        feedback_data = {
            "plan_id": str(test_plan.id),
            "rating": 4,
            "feedback_text": "Good plan",
            "feedback_type": "helpful",
        }

        response = client.post("/api/v1/feedback/plan", json=feedback_data)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    def test_submit_plan_feedback_validation_error(self, client: TestClient):
        """Test validation error on invalid rating."""
        feedback_data = {
            "plan_id": str(uuid4()),
            "rating": 10,  # Invalid rating
            "feedback_type": "helpful",
        }

        response = client.post("/api/v1/feedback/plan", json=feedback_data)

        assert response.status_code == 422

    def test_submit_plan_feedback_text_too_long(
        self, client: TestClient, test_plan: PlanCatalog
    ):
        """Test validation error on text exceeding character limit."""
        feedback_data = {
            "plan_id": str(test_plan.id),
            "rating": 5,
            "feedback_text": "x" * 501,  # Exceeds 500 char limit
            "feedback_type": "helpful",
        }

        response = client.post("/api/v1/feedback/plan", json=feedback_data)

        assert response.status_code == 422


class TestSubmitRecommendationFeedback:
    """Tests for POST /api/v1/feedback/recommendation endpoint."""

    def test_submit_recommendation_feedback(self, client: TestClient):
        """Test submitting recommendation feedback."""
        recommendation_id = uuid4()
        feedback_data = {
            "recommendation_id": str(recommendation_id),
            "rating": 5,
            "feedback_text": "Very helpful recommendations!",
            "feedback_type": "helpful",
        }

        response = client.post("/api/v1/feedback/recommendation", json=feedback_data)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True


class TestGetFeedbackStats:
    """Tests for GET /api/v1/feedback/stats endpoint."""

    def test_get_feedback_stats_unauthorized(
        self, client: TestClient, test_user: User, auth_headers
    ):
        """Test that non-admin cannot access stats."""
        response = client.get(
            "/api/v1/feedback/stats", headers=auth_headers(test_user)
        )

        assert response.status_code == 403

    def test_get_feedback_stats_authorized(
        self, client: TestClient, admin_user: User, auth_headers
    ):
        """Test that admin can access stats."""
        response = client.get(
            "/api/v1/feedback/stats", headers=auth_headers(admin_user)
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_feedback_count" in data
        assert "average_rating" in data
        assert "thumbs_up_count" in data
        assert "sentiment_breakdown" in data


class TestGetFeedbackAnalytics:
    """Tests for GET /api/v1/admin/feedback/analytics endpoint."""

    def test_get_analytics_admin_only(
        self, client: TestClient, admin_user: User, auth_headers
    ):
        """Test analytics endpoint is admin-only."""
        response = client.get(
            "/api/v1/admin/feedback/analytics", headers=auth_headers(admin_user)
        )

        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert "time_series" in data
        assert "top_plans" in data
        assert "recent_text_feedback" in data


class TestSearchFeedback:
    """Tests for GET /api/v1/admin/feedback/search endpoint."""

    def test_search_feedback_with_filters(
        self, client: TestClient, admin_user: User, test_plan: PlanCatalog, auth_headers
    ):
        """Test searching feedback with filters."""
        response = client.get(
            "/api/v1/admin/feedback/search",
            params={"plan_id": str(test_plan.id), "min_rating": 4, "limit": 10},
            headers=auth_headers(admin_user),
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total_count" in data
        assert isinstance(data["results"], list)


class TestExportFeedback:
    """Tests for GET /api/v1/admin/feedback/export endpoint."""

    def test_export_csv_admin_only(
        self, client: TestClient, admin_user: User, auth_headers
    ):
        """Test CSV export is admin-only."""
        response = client.get(
            "/api/v1/admin/feedback/export", headers=auth_headers(admin_user)
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers.get("content-disposition", "")


class TestRateLimiting:
    """Tests for rate limiting on feedback endpoints."""

    def test_rate_limit_enforcement(
        self, client: TestClient, test_user: User, test_plan: PlanCatalog, auth_headers
    ):
        """Test that rate limiting is enforced (10 per day)."""
        feedback_data = {
            "plan_id": str(test_plan.id),
            "rating": 5,
            "feedback_type": "helpful",
        }

        # Submit 11 feedback submissions
        for i in range(11):
            response = client.post(
                "/api/v1/feedback/plan",
                json=feedback_data,
                headers=auth_headers(test_user),
            )

            if i < 10:
                assert response.status_code == 201
            else:
                # 11th request should be rate limited
                assert response.status_code == 429
                assert "Rate limit exceeded" in response.json()["detail"]


