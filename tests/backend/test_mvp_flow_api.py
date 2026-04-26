"""Focused tests for MVP recommendation/result flow behavior."""

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from src.backend.models.plan import PlanCatalog, Supplier
from src.backend.models.recommendation import Recommendation


def test_get_recommendation_by_id_returns_persisted_payload(client, db, regular_user):
    recommendation_id = uuid4()
    generated_at = datetime.utcnow()
    payload = {
        "recommendation_id": str(recommendation_id),
        "user_profile": {
            "profile_type": "baseline",
            "projected_annual_kwh": 12000,
            "mean_monthly_kwh": 1000,
            "has_seasonal_pattern": False,
            "confidence_score": 0.9,
        },
        "top_plans": [],
        "generated_at": generated_at.isoformat(),
        "total_plans_analyzed": 0,
        "warnings": [],
        "overall_risk_level": "low",
        "total_risks_detected": 0,
        "critical_risk_count": 0,
        "should_stay": False,
        "stay_recommendation": None,
    }

    db.add(
        Recommendation(
            id=recommendation_id,
            user_id=regular_user.id,
            usage_profile={"profile_type": "baseline"},
            result_payload=payload,
            generated_at=generated_at,
            expires_at=generated_at + timedelta(hours=24),
        )
    )
    db.commit()

    response = client.get(f"/api/v1/recommendations/{recommendation_id}")

    assert response.status_code == 200
    assert response.json()["recommendation_id"] == str(recommendation_id)
    assert response.json()["user_profile"]["profile_type"] == "baseline"


def test_plan_catalog_filters_by_zip_code(client, db):
    supplier = Supplier(
        id=uuid4(),
        supplier_name="ZIP Filter Energy",
        average_rating=Decimal("4.5"),
        review_count=20,
        is_active=True,
    )
    db.add(supplier)
    db.flush()

    matching_plan = PlanCatalog(
        id=uuid4(),
        supplier_id=supplier.id,
        plan_name="Austin Match",
        plan_type="fixed",
        rate_structure={"type": "fixed", "rate": 11.5},
        contract_length_months=12,
        early_termination_fee=Decimal("100.00"),
        renewable_percentage=Decimal("50.00"),
        available_regions=["78701", "78702"],
        is_active=True,
    )
    non_matching_plan = PlanCatalog(
        id=uuid4(),
        supplier_id=supplier.id,
        plan_name="Dallas Only",
        plan_type="fixed",
        rate_structure={"type": "fixed", "rate": 12.5},
        contract_length_months=12,
        early_termination_fee=Decimal("100.00"),
        renewable_percentage=Decimal("50.00"),
        available_regions=["75201"],
        is_active=True,
    )
    db.add_all([matching_plan, non_matching_plan])
    db.commit()

    response = client.get("/api/v1/plans/catalog?zip_code=78701")

    assert response.status_code == 200
    plan_names = {item["plan_name"] for item in response.json()["items"]}
    assert "Austin Match" in plan_names
    assert "Dallas Only" not in plan_names
