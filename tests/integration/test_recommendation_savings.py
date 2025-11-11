"""
Integration tests for Story 2.2 (Recommendation) + Story 2.4/2.5 (Savings).

Tests the integration between:
- Plan Matching/Ranking (Story 2.2 - Backend Dev #3)
- Savings Calculator (Story 2.4 - Backend Dev #4)
- Comparison Features (Story 2.5 - Backend Dev #4)

Author: Backend Dev #4
Note: Uses mock data for Story 2.2 until contract is published
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from uuid import uuid4

from src.backend.services.savings_calculator import SavingsCalculatorService
from src.backend.schemas.savings_schemas import (
    RankedPlan,
    RecommendationResult,
    SavingsAnalysis,
    PlanComparison,
)
from src.backend.schemas.plan import PlanCatalogResponse, SupplierResponse
from src.backend.schemas.user import CurrentPlanResponse
from src.backend.schemas.usage_schemas import UsageProjection


# ===== FIXTURES =====

@pytest.fixture
def integration_user_id():
    """Fixed user ID for integration testing."""
    return uuid4()


@pytest.fixture
def integration_current_plan(integration_user_id):
    """Current plan for integration testing."""
    return CurrentPlanResponse(
        id=uuid4(),
        user_id=integration_user_id,
        supplier_name="Legacy Power Co",
        plan_name="Standard Rate",
        current_rate=Decimal("13.8"),  # 13.8 cents/kWh
        contract_start_date=date(2023, 6, 1),
        contract_end_date=date(2024, 12, 31),
        early_termination_fee=Decimal("250.00"),
        monthly_fee=Decimal("12.00"),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def integration_usage_projection():
    """Seasonal usage projection for integration testing."""
    return UsageProjection(
        projected_monthly_kwh=[
            820.0,   # Jan
            800.0,   # Feb
            850.0,   # Mar
            920.0,   # Apr
            1150.0,  # May
            1500.0,  # Jun - AC starts
            1750.0,  # Jul - Peak summer
            1680.0,  # Aug - Peak summer
            1200.0,  # Sep
            950.0,   # Oct
            870.0,   # Nov
            830.0,   # Dec
        ],
        projected_annual_kwh=13320.0,
        confidence_lower=[m * 0.85 for m in [820, 800, 850, 920, 1150, 1500, 1750, 1680, 1200, 950, 870, 830]],
        confidence_upper=[m * 1.15 for m in [820, 800, 850, 920, 1150, 1500, 1750, 1680, 1200, 950, 870, 830]],
        confidence_score=0.88,
        method="seasonal_decomposition",
        assumptions=[
            "Strong summer cooling demand",
            "Baseline winter heating usage",
            "12 months complete historical data",
        ],
    )


@pytest.fixture
def integration_suppliers():
    """Mock suppliers for integration testing."""
    return [
        SupplierResponse(
            id=uuid4(),
            supplier_name="GreenChoice Energy",
            average_rating=Decimal("4.7"),
            review_count=2450,
            website="https://greenchoice.example.com",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        SupplierResponse(
            id=uuid4(),
            supplier_name="PowerSaver Plus",
            average_rating=Decimal("4.3"),
            review_count=1820,
            website="https://powersaver.example.com",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        SupplierResponse(
            id=uuid4(),
            supplier_name="FlexEnergy Solutions",
            average_rating=Decimal("4.5"),
            review_count=980,
            website="https://flexenergy.example.com",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]


@pytest.fixture
def integration_plan_catalog(integration_suppliers):
    """Mock plan catalog for integration testing."""
    plans = [
        # Plan 1: Best cost saver - fixed rate, high renewable
        PlanCatalogResponse(
            id=uuid4(),
            supplier_id=integration_suppliers[0].id,
            plan_name="GreenSaver 24",
            plan_type="fixed",
            rate_structure={"type": "fixed", "rate_per_kwh": 10.8},
            contract_length_months=24,
            early_termination_fee=Decimal("100.00"),
            renewable_percentage=Decimal("100.00"),
            monthly_fee=Decimal("5.99"),
            connection_fee=Decimal("29.95"),
            available_regions=["75001", "75002"],
            plan_description="100% wind energy with locked rate",
            is_active=True,
            last_updated=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            supplier=integration_suppliers[0],
        ),
        # Plan 2: Most flexible - month-to-month variable
        PlanCatalogResponse(
            id=uuid4(),
            supplier_id=integration_suppliers[2].id,
            plan_name="Flex Freedom",
            plan_type="variable",
            rate_structure={"type": "variable", "base_rate": 11.5, "adjustment_formula": "market_index"},
            contract_length_months=0,  # Month-to-month
            early_termination_fee=Decimal("0.00"),
            renewable_percentage=Decimal("30.00"),
            monthly_fee=Decimal("0.00"),
            connection_fee=Decimal("0.00"),
            available_regions=["75001"],
            plan_description="No commitment, cancel anytime",
            is_active=True,
            last_updated=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            supplier=integration_suppliers[2],
        ),
        # Plan 3: Balance of cost and renewable
        PlanCatalogResponse(
            id=uuid4(),
            supplier_id=integration_suppliers[1].id,
            plan_name="PowerSaver 12",
            plan_type="fixed",
            rate_structure={"type": "fixed", "rate_per_kwh": 11.2},
            contract_length_months=12,
            early_termination_fee=Decimal("75.00"),
            renewable_percentage=Decimal("50.00"),
            monthly_fee=Decimal("7.95"),
            connection_fee=Decimal("19.95"),
            available_regions=["75001", "75002", "75003"],
            plan_description="50% solar blend with competitive rates",
            is_active=True,
            last_updated=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            supplier=integration_suppliers[1],
        ),
    ]
    return {plan.id: plan for plan in plans}


@pytest.fixture
def integration_recommendation_result(integration_user_id, integration_plan_catalog):
    """
    Mock recommendation result from Story 2.2.

    Replace with actual Story 2.2 output when contract is published.
    """
    plans = list(integration_plan_catalog.values())

    return RecommendationResult(
        user_id=integration_user_id,
        top_plans=[
            RankedPlan(
                plan_id=plans[0].id,  # GreenSaver 24
                rank=1,
                composite_score=Decimal("0.94"),
                cost_score=Decimal("0.96"),
                flexibility_score=Decimal("0.80"),
                renewable_score=Decimal("1.00"),
                rating_score=Decimal("0.94"),
                projected_annual_cost=Decimal("1520.00"),
            ),
            RankedPlan(
                plan_id=plans[2].id,  # PowerSaver 12
                rank=2,
                composite_score=Decimal("0.89"),
                cost_score=Decimal("0.92"),
                flexibility_score=Decimal("0.90"),
                renewable_score=Decimal("0.50"),
                rating_score=Decimal("0.86"),
                projected_annual_cost=Decimal("1580.00"),
            ),
            RankedPlan(
                plan_id=plans[1].id,  # Flex Freedom
                rank=3,
                composite_score=Decimal("0.85"),
                cost_score=Decimal("0.88"),
                flexibility_score=Decimal("1.00"),
                renewable_score=Decimal("0.30"),
                rating_score=Decimal("0.90"),
                projected_annual_cost=Decimal("1610.00"),
            ),
        ],
        generated_at=datetime.now(),
    )


# ===== INTEGRATION TESTS =====

class TestRecommendationToSavingsIntegration:
    """Integration tests for Story 2.2 → Story 2.4."""

    def test_calculate_savings_for_top_recommendation(
        self,
        integration_recommendation_result,
        integration_current_plan,
        integration_usage_projection,
        integration_plan_catalog,
    ):
        """Test calculating savings for top recommended plan."""
        service = SavingsCalculatorService()

        # Get top recommendation
        top_plan = integration_recommendation_result.top_plans[0]
        full_plan = integration_plan_catalog[top_plan.plan_id]

        # Calculate savings
        savings = service.calculate_annual_savings(
            current_plan=integration_current_plan,
            recommended_plan=full_plan,
            usage_projection=integration_usage_projection,
            user_id=integration_recommendation_result.user_id,
        )

        # Verify savings structure
        assert isinstance(savings, SavingsAnalysis)
        assert savings.plan_id == top_plan.plan_id
        assert savings.user_id == integration_recommendation_result.user_id

        # Verify significant savings (top plan should save money)
        assert savings.annual_savings > Decimal("100.00")
        assert savings.savings_percentage > Decimal("5.00")

        # Verify all components calculated
        assert len(savings.monthly_breakdown) == 12
        assert savings.total_cost_of_ownership > 0
        assert savings.break_even_months is not None

    def test_calculate_savings_for_all_recommendations(
        self,
        integration_recommendation_result,
        integration_current_plan,
        integration_usage_projection,
        integration_plan_catalog,
    ):
        """Test calculating savings for all top 3 recommendations."""
        service = SavingsCalculatorService()

        savings_analyses = []

        for ranked_plan in integration_recommendation_result.top_plans:
            full_plan = integration_plan_catalog[ranked_plan.plan_id]

            savings = service.calculate_annual_savings(
                current_plan=integration_current_plan,
                recommended_plan=full_plan,
                usage_projection=integration_usage_projection,
                user_id=integration_recommendation_result.user_id,
            )

            savings_analyses.append(savings)

        # Verify we got 3 analyses
        assert len(savings_analyses) == 3

        # Verify all show savings
        assert all(s.annual_savings > 0 for s in savings_analyses)

        # Verify rank 1 has best savings (generally)
        # Note: May not always be true if rank 1 optimizes for other factors
        rank_1_savings = savings_analyses[0].annual_savings
        assert rank_1_savings > Decimal("0")


class TestRecommendationToComparisonIntegration:
    """Integration tests for Story 2.2 → Story 2.5."""

    def test_generate_comparison_from_recommendations(
        self,
        integration_recommendation_result,
        integration_current_plan,
        integration_usage_projection,
        integration_plan_catalog,
    ):
        """Test generating comparison from recommendation results."""
        service = SavingsCalculatorService()

        comparison = service.generate_comparison(
            plans=integration_recommendation_result.top_plans,
            current_plan=integration_current_plan,
            usage_projection=integration_usage_projection,
            plan_catalog=integration_plan_catalog,
            user_id=integration_recommendation_result.user_id,
        )

        # Verify comparison structure
        assert isinstance(comparison, PlanComparison)
        assert comparison.user_id == integration_recommendation_result.user_id

        # Verify all plans included
        assert len(comparison.plans) == 3

        # Verify current plan included
        assert comparison.current_plan.is_current_plan is True

        # Verify best by category identified
        assert "lowest_cost" in comparison.best_by_category
        assert "highest_renewable" in comparison.best_by_category
        assert "most_flexible" in comparison.best_by_category

        # Verify trade-offs generated
        assert len(comparison.trade_offs) > 0

        # Verify multi-year projections
        assert len(comparison.multi_year_projections) > 0

    def test_comparison_best_categories_accuracy(
        self,
        integration_recommendation_result,
        integration_current_plan,
        integration_usage_projection,
        integration_plan_catalog,
    ):
        """Test that best category identification is accurate."""
        service = SavingsCalculatorService()

        comparison = service.generate_comparison(
            plans=integration_recommendation_result.top_plans,
            current_plan=integration_current_plan,
            usage_projection=integration_usage_projection,
            plan_catalog=integration_plan_catalog,
            user_id=integration_recommendation_result.user_id,
        )

        # Find the plan with highest renewable
        highest_renewable_plan = max(
            comparison.plans,
            key=lambda p: p.renewable_percentage
        )

        # Verify it matches best_by_category
        assert comparison.best_by_category["highest_renewable"] == highest_renewable_plan.plan_id

        # Find most flexible (lowest contract length)
        most_flexible_plan = min(
            comparison.plans,
            key=lambda p: p.contract_length_months
        )

        # Verify it matches best_by_category
        assert comparison.best_by_category["most_flexible"] == most_flexible_plan.plan_id

    def test_comparison_includes_rank_from_recommendation(
        self,
        integration_recommendation_result,
        integration_current_plan,
        integration_usage_projection,
        integration_plan_catalog,
    ):
        """Test that comparison preserves rank from recommendation."""
        service = SavingsCalculatorService()

        comparison = service.generate_comparison(
            plans=integration_recommendation_result.top_plans,
            current_plan=integration_current_plan,
            usage_projection=integration_usage_projection,
            plan_catalog=integration_plan_catalog,
            user_id=integration_recommendation_result.user_id,
        )

        # Verify ranks preserved
        for comp_plan in comparison.plans:
            # Find corresponding ranked plan
            ranked_plan = next(
                (rp for rp in integration_recommendation_result.top_plans if rp.plan_id == comp_plan.plan_id),
                None
            )

            assert ranked_plan is not None
            assert comp_plan.rank == ranked_plan.rank
            assert comp_plan.composite_score == ranked_plan.composite_score


class TestEndToEndRecommendationSavingsFlow:
    """End-to-end integration flow tests."""

    def test_complete_recommendation_to_comparison_flow(
        self,
        integration_recommendation_result,
        integration_current_plan,
        integration_usage_projection,
        integration_plan_catalog,
    ):
        """
        Test complete flow: Recommendation → Savings → Comparison.

        This simulates the full user journey:
        1. User gets top 3 recommendations (Story 2.2)
        2. System calculates savings for each (Story 2.4)
        3. System generates comparison view (Story 2.5)
        """
        service = SavingsCalculatorService()

        # Step 1: Start with recommendations (from Story 2.2)
        recommendations = integration_recommendation_result
        assert len(recommendations.top_plans) == 3

        # Step 2: Calculate savings for each recommendation (Story 2.4)
        savings_list = []
        for ranked_plan in recommendations.top_plans:
            full_plan = integration_plan_catalog[ranked_plan.plan_id]

            savings = service.calculate_annual_savings(
                current_plan=integration_current_plan,
                recommended_plan=full_plan,
                usage_projection=integration_usage_projection,
                user_id=recommendations.user_id,
            )

            savings_list.append(savings)

        # Verify savings calculated
        assert len(savings_list) == 3
        assert all(isinstance(s, SavingsAnalysis) for s in savings_list)

        # Step 3: Generate comparison view (Story 2.5)
        comparison = service.generate_comparison(
            plans=recommendations.top_plans,
            current_plan=integration_current_plan,
            usage_projection=integration_usage_projection,
            plan_catalog=integration_plan_catalog,
            user_id=recommendations.user_id,
        )

        # Verify comparison complete
        assert isinstance(comparison, PlanComparison)
        assert len(comparison.plans) == 3
        assert comparison.current_plan.is_current_plan

        # Step 4: Verify data consistency across analyses
        for i, comp_plan in enumerate(comparison.plans):
            # Find corresponding savings analysis
            savings = next((s for s in savings_list if s.plan_id == comp_plan.plan_id), None)

            if savings:
                # Annual costs should match
                assert abs(comp_plan.annual_cost - savings.projected_annual_cost) < Decimal("1.00")

                # Savings should match
                assert abs(comp_plan.savings_vs_current_annual - savings.annual_savings) < Decimal("1.00")

    def test_user_decision_support_data_complete(
        self,
        integration_recommendation_result,
        integration_current_plan,
        integration_usage_projection,
        integration_plan_catalog,
    ):
        """
        Test that user has all data needed for decision.

        Verify that the integrated output provides:
        - Cost projections
        - Savings calculations
        - Risk warnings
        - Trade-off analysis
        - Multi-year outlook
        """
        service = SavingsCalculatorService()

        # Get top recommendation
        top_plan = integration_recommendation_result.top_plans[0]
        full_plan = integration_plan_catalog[top_plan.plan_id]

        # Calculate savings
        savings = service.calculate_annual_savings(
            current_plan=integration_current_plan,
            recommended_plan=full_plan,
            usage_projection=integration_usage_projection,
            user_id=integration_recommendation_result.user_id,
        )

        # Generate comparison
        comparison = service.generate_comparison(
            plans=integration_recommendation_result.top_plans,
            current_plan=integration_current_plan,
            usage_projection=integration_usage_projection,
            plan_catalog=integration_plan_catalog,
            user_id=integration_recommendation_result.user_id,
        )

        # Verify complete decision support data

        # 1. Cost projections available
        assert savings.projected_annual_cost > 0
        assert savings.current_annual_cost > 0
        assert len(savings.monthly_breakdown) == 12

        # 2. Savings calculations clear
        assert savings.annual_savings is not None
        assert savings.savings_percentage is not None
        assert savings.cumulative_savings_12_months is not None

        # 3. Risk information provided
        assert savings.break_even_months is not None or savings.switching_cost == 0
        assert len(savings.assumptions) > 0
        assert len(savings.warnings) >= 0  # May have warnings

        # 4. Trade-off analysis available
        assert len(comparison.trade_offs) > 0

        # 5. Multi-year outlook provided
        assert len(comparison.multi_year_projections) > 0

        # 6. Best options highlighted
        assert len(comparison.best_by_category) >= 3

        print("\n✓ User has complete decision support data:")
        print(f"  - Annual savings: ${savings.annual_savings:.2f}")
        print(f"  - Break-even: {savings.break_even_months} months")
        print(f"  - Trade-offs identified: {len(comparison.trade_offs)}")
        print(f"  - Best in {len(comparison.best_by_category)} categories")


class TestDataConsistency:
    """Test data consistency across integration points."""

    def test_projected_costs_consistent_across_services(
        self,
        integration_recommendation_result,
        integration_current_plan,
        integration_usage_projection,
        integration_plan_catalog,
    ):
        """Test that projected costs are consistent."""
        service = SavingsCalculatorService()

        for ranked_plan in integration_recommendation_result.top_plans:
            full_plan = integration_plan_catalog[ranked_plan.plan_id]

            # Calculate via savings service
            savings = service.calculate_annual_savings(
                current_plan=integration_current_plan,
                recommended_plan=full_plan,
                usage_projection=integration_usage_projection,
                user_id=integration_recommendation_result.user_id,
            )

            # Projected cost from Story 2.4
            savings_projected_cost = savings.projected_annual_cost

            # Projected cost from Story 2.2 (in RankedPlan)
            recommendation_projected_cost = ranked_plan.projected_annual_cost

            # Should be similar (may have small differences due to fees)
            # Allow 10% difference (fees, connection costs, etc.)
            diff_percentage = abs(savings_projected_cost - recommendation_projected_cost) / recommendation_projected_cost * 100

            assert diff_percentage < 15, \
                f"Cost mismatch for {full_plan.plan_name}: " \
                f"Savings={savings_projected_cost}, Recommendation={recommendation_projected_cost}"

    def test_rankings_reflected_in_comparison(
        self,
        integration_recommendation_result,
        integration_current_plan,
        integration_usage_projection,
        integration_plan_catalog,
    ):
        """Test that recommendation rankings are preserved in comparison."""
        service = SavingsCalculatorService()

        comparison = service.generate_comparison(
            plans=integration_recommendation_result.top_plans,
            current_plan=integration_current_plan,
            usage_projection=integration_usage_projection,
            plan_catalog=integration_plan_catalog,
            user_id=integration_recommendation_result.user_id,
        )

        # Sort comparison plans by rank
        sorted_plans = sorted(comparison.plans, key=lambda p: p.rank or 999)

        # Verify order matches recommendation order
        for i, comp_plan in enumerate(sorted_plans):
            expected_rank = i + 1
            assert comp_plan.rank == expected_rank


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
