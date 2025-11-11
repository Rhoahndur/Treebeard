"""
Unit tests for Savings Calculator Service (Stories 2.4 & 2.5).

Tests coverage:
- Annual savings calculation
- Total Cost of Ownership (TCO)
- Break-even analysis
- Variable rate uncertainty
- Multi-plan comparison
- Edge cases and validation

Author: Backend Dev #4
"""

import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import uuid4, UUID

from src.backend.services.savings_calculator import SavingsCalculatorService
from src.backend.schemas.savings_schemas import (
    ComparisonPlan,
    CostRange,
    MonthlyCost,
    PlanComparison,
    RankedPlan,
    SavingsAnalysis,
)
from src.backend.schemas.plan import (
    PlanCatalogResponse,
    SupplierResponse,
)
from src.backend.schemas.user import CurrentPlanResponse
from src.backend.schemas.usage_schemas import UsageProjection


# ===== FIXTURES =====

@pytest.fixture
def savings_service():
    """Create savings calculator service instance."""
    return SavingsCalculatorService()


@pytest.fixture
def mock_current_plan():
    """Mock current plan for testing."""
    return CurrentPlanResponse(
        id=uuid4(),
        user_id=uuid4(),
        supplier_name="Current Energy Co",
        plan_name="Current Plan",
        current_rate=Decimal("12.5"),  # 12.5 cents per kWh
        contract_start_date=date(2024, 1, 1),
        contract_end_date=date(2025, 12, 31),
        early_termination_fee=Decimal("200.00"),
        monthly_fee=Decimal("9.95"),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_supplier():
    """Mock supplier for testing."""
    return SupplierResponse(
        id=uuid4(),
        supplier_name="Green Energy Solutions",
        average_rating=Decimal("4.5"),
        review_count=1250,
        website="https://greenenergy.example.com",
        customer_service_phone="1-800-555-0123",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_recommended_plan_fixed(mock_supplier):
    """Mock recommended plan with fixed rate."""
    return PlanCatalogResponse(
        id=uuid4(),
        supplier_id=mock_supplier.id,
        plan_name="EcoSaver Fixed 12",
        plan_type="fixed",
        rate_structure={"type": "fixed", "rate_per_kwh": 10.5},  # 10.5 cents per kWh
        contract_length_months=12,
        early_termination_fee=Decimal("75.00"),
        renewable_percentage=Decimal("100.00"),
        monthly_fee=Decimal("4.95"),
        connection_fee=Decimal("25.00"),
        available_regions=["75001", "75002"],
        plan_description="100% renewable fixed rate plan",
        is_active=True,
        last_updated=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        supplier=mock_supplier,
    )


@pytest.fixture
def mock_recommended_plan_variable(mock_supplier):
    """Mock recommended plan with variable rate."""
    return PlanCatalogResponse(
        id=uuid4(),
        supplier_id=mock_supplier.id,
        plan_name="Flex Variable",
        plan_type="variable",
        rate_structure={"type": "variable", "base_rate": 11.0, "adjustment_formula": "market_rate"},
        contract_length_months=0,  # Month-to-month
        early_termination_fee=Decimal("0.00"),
        renewable_percentage=Decimal("50.00"),
        monthly_fee=Decimal("0.00"),
        connection_fee=Decimal("0.00"),
        available_regions=["75001"],
        is_active=True,
        last_updated=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        supplier=mock_supplier,
    )


@pytest.fixture
def mock_usage_projection():
    """Mock usage projection with seasonal pattern."""
    return UsageProjection(
        projected_monthly_kwh=[
            750.0,  # Jan
            720.0,  # Feb
            780.0,  # Mar
            850.0,  # Apr
            1100.0,  # May
            1400.0,  # Jun - Summer peak
            1600.0,  # Jul - Summer peak
            1500.0,  # Aug - Summer peak
            1000.0,  # Sep
            850.0,  # Oct
            800.0,  # Nov
            750.0,  # Dec
        ],
        projected_annual_kwh=12100.0,
        confidence_lower=[month * 0.9 for month in [750, 720, 780, 850, 1100, 1400, 1600, 1500, 1000, 850, 800, 750]],
        confidence_upper=[month * 1.1 for month in [750, 720, 780, 850, 1100, 1400, 1600, 1500, 1000, 850, 800, 750]],
        confidence_score=0.85,
        method="seasonal_average",
        assumptions=["Strong seasonal pattern with summer peak"],
    )


# ===== STORY 2.4: SAVINGS CALCULATOR TESTS =====

class TestAnnualSavingsCalculation:
    """Test suite for annual savings calculation (Story 2.4)."""

    def test_calculate_annual_savings_basic(
        self,
        savings_service,
        mock_current_plan,
        mock_recommended_plan_fixed,
        mock_usage_projection,
    ):
        """Test basic annual savings calculation."""
        user_id = uuid4()

        result = savings_service.calculate_annual_savings(
            current_plan=mock_current_plan,
            recommended_plan=mock_recommended_plan_fixed,
            usage_projection=mock_usage_projection,
            user_id=user_id,
        )

        # Verify structure
        assert isinstance(result, SavingsAnalysis)
        assert result.plan_id == mock_recommended_plan_fixed.id
        assert result.user_id == user_id

        # Verify savings calculation
        assert result.annual_savings > 0  # Should save money
        assert result.savings_percentage > 0
        assert result.projected_annual_cost < result.current_annual_cost

        # Verify monthly breakdown
        assert len(result.monthly_breakdown) == 12
        assert all(isinstance(month, MonthlyCost) for month in result.monthly_breakdown)

    def test_monthly_breakdown_accuracy(
        self,
        savings_service,
        mock_current_plan,
        mock_recommended_plan_fixed,
        mock_usage_projection,
    ):
        """Test accuracy of month-by-month cost breakdown."""
        result = savings_service.calculate_annual_savings(
            current_plan=mock_current_plan,
            recommended_plan=mock_recommended_plan_fixed,
            usage_projection=mock_usage_projection,
            user_id=uuid4(),
        )

        # Verify first month includes connection fee
        assert result.monthly_breakdown[0].other_fees == Decimal("25.00")

        # Verify subsequent months don't have connection fee
        assert all(month.other_fees == Decimal("0.00") for month in result.monthly_breakdown[1:])

        # Verify monthly fees are consistent
        monthly_fee = mock_recommended_plan_fixed.monthly_fee or Decimal("0.00")
        assert all(month.monthly_fee == monthly_fee for month in result.monthly_breakdown)

        # Verify total equals sum of components
        for month in result.monthly_breakdown:
            expected_total = month.energy_cost + month.monthly_fee + month.other_fees
            assert abs(month.total_cost - expected_total) < Decimal("0.01")

        # Verify annual total
        calculated_annual = sum(month.total_cost for month in result.monthly_breakdown)
        assert abs(result.projected_annual_cost - calculated_annual) < Decimal("0.01")

    def test_all_fees_included_in_tco(
        self,
        savings_service,
        mock_current_plan,
        mock_recommended_plan_fixed,
        mock_usage_projection,
    ):
        """Test that all fees are included in TCO calculation."""
        result = savings_service.calculate_annual_savings(
            current_plan=mock_current_plan,
            recommended_plan=mock_recommended_plan_fixed,
            usage_projection=mock_usage_projection,
            user_id=uuid4(),
        )

        # Verify fees breakdown
        assert result.total_upfront_fees == Decimal("25.00")  # Connection fee
        assert result.total_monthly_fees == Decimal("4.95") * Decimal("12")  # Monthly fee × 12

        # Verify TCO includes all costs
        assert result.total_cost_of_ownership > result.projected_annual_cost  # TCO > annual (due to connection fee)

    def test_variable_rate_uncertainty_range(
        self,
        savings_service,
        mock_current_plan,
        mock_recommended_plan_variable,
        mock_usage_projection,
    ):
        """Test uncertainty range for variable rate plans."""
        result = savings_service.calculate_annual_savings(
            current_plan=mock_current_plan,
            recommended_plan=mock_recommended_plan_variable,
            usage_projection=mock_usage_projection,
            user_id=uuid4(),
        )

        # Verify variable rate flag
        assert result.is_variable_rate is True

        # Verify uncertainty range exists
        assert result.uncertainty_range is not None
        assert isinstance(result.uncertainty_range, CostRange)

        # Verify range is reasonable
        assert result.uncertainty_range.low_estimate < result.uncertainty_range.expected_value
        assert result.uncertainty_range.expected_value < result.uncertainty_range.high_estimate
        assert result.uncertainty_range.confidence_level == Decimal("0.95")

        # Verify warning about variable rate
        assert any("variable" in warning.lower() for warning in result.warnings)


class TestBreakEvenAnalysis:
    """Test suite for break-even analysis (Story 2.4)."""

    def test_break_even_with_etf(
        self,
        savings_service,
        mock_current_plan,
        mock_recommended_plan_fixed,
        mock_usage_projection,
    ):
        """Test break-even calculation with early termination fee."""
        result = savings_service.calculate_annual_savings(
            current_plan=mock_current_plan,
            recommended_plan=mock_recommended_plan_fixed,
            usage_projection=mock_usage_projection,
            user_id=uuid4(),
        )

        # Verify switching cost captured
        assert result.switching_cost == Decimal("200.00")

        # Verify break-even is calculated
        assert result.break_even_months is not None
        assert result.break_even_months > 0

        # Verify cumulative savings accounts for switching cost
        expected_cumulative = result.annual_savings - result.switching_cost
        assert abs(result.cumulative_savings_12_months - expected_cumulative) < Decimal("0.01")

    def test_break_even_no_etf(
        self,
        savings_service,
        mock_current_plan,
        mock_recommended_plan_variable,
        mock_usage_projection,
    ):
        """Test break-even when no ETF exists."""
        result = savings_service.calculate_annual_savings(
            current_plan=mock_current_plan,
            recommended_plan=mock_recommended_plan_variable,
            usage_projection=mock_usage_projection,
            user_id=uuid4(),
        )

        # No switching cost
        assert result.switching_cost == Decimal("0.00")

        # Break-even should be 0 or None (immediate)
        assert result.break_even_months == 0 or result.break_even_months is None

    def test_high_etf_warning(
        self,
        savings_service,
        mock_current_plan,
        mock_recommended_plan_fixed,
        mock_usage_projection,
    ):
        """Test warning for high early termination fee."""
        result = savings_service.calculate_annual_savings(
            current_plan=mock_current_plan,
            recommended_plan=mock_recommended_plan_fixed,
            usage_projection=mock_usage_projection,
            user_id=uuid4(),
        )

        # Verify high ETF warning (current plan has $200 ETF)
        etf_warnings = [w for w in result.warnings if "termination fee" in w.lower()]
        assert len(etf_warnings) > 0


class TestCostCalculations:
    """Test suite for various cost calculation methods."""

    def test_fixed_rate_calculation(self, savings_service, mock_usage_projection):
        """Test energy cost calculation for fixed rate."""
        rate_structure = {"type": "fixed", "rate_per_kwh": 10.0}
        kwh = 1000.0

        cost = savings_service._calculate_energy_cost_for_month(
            kwh=kwh,
            rate_structure=rate_structure,
            plan_type="fixed",
        )

        expected = Decimal("1000") * Decimal("10.0") / Decimal("100")
        assert abs(cost - expected) < Decimal("0.01")

    def test_tiered_rate_calculation(self, savings_service):
        """Test energy cost calculation for tiered pricing."""
        rate_structure = {
            "type": "tiered",
            "tiers": [
                {"usage_max": 500, "rate_per_kwh": 8.0},  # First 500 kWh
                {"usage_max": 500, "rate_per_kwh": 10.0},  # Next 500 kWh
                {"usage_max": float("inf"), "rate_per_kwh": 12.0},  # Above 1000 kWh
            ],
        }
        kwh = 1200.0

        cost = savings_service._calculate_energy_cost_for_month(
            kwh=kwh,
            rate_structure=rate_structure,
            plan_type="tiered",
        )

        # Calculate expected: (500*8 + 500*10 + 200*12) / 100
        expected = (Decimal("500") * Decimal("8") + Decimal("500") * Decimal("10") + Decimal("200") * Decimal("12")) / Decimal("100")
        assert abs(cost - expected) < Decimal("0.01")

    def test_time_of_use_calculation(self, savings_service):
        """Test energy cost calculation for time-of-use pricing."""
        rate_structure = {
            "type": "time_of_use",
            "peak_rate": 15.0,
            "off_peak_rate": 7.0,
            "peak_hours": [14, 15, 16, 17, 18, 19],
        }
        kwh = 1000.0

        cost = savings_service._calculate_energy_cost_for_month(
            kwh=kwh,
            rate_structure=rate_structure,
            plan_type="time_of_use",
        )

        # Should use average rate (simplified)
        avg_rate = (Decimal("15.0") + Decimal("7.0")) / Decimal("2")
        expected = Decimal("1000") * avg_rate / Decimal("100")
        assert abs(cost - expected) < Decimal("0.01")


# ===== STORY 2.5: COMPARISON FEATURES TESTS =====

class TestPlanComparison:
    """Test suite for plan comparison features (Story 2.5)."""

    def test_generate_comparison_basic(
        self,
        savings_service,
        mock_current_plan,
        mock_recommended_plan_fixed,
        mock_recommended_plan_variable,
        mock_usage_projection,
    ):
        """Test basic comparison generation."""
        user_id = uuid4()

        # Create ranked plans
        ranked_plans = [
            RankedPlan(
                plan_id=mock_recommended_plan_fixed.id,
                rank=1,
                composite_score=Decimal("0.92"),
                cost_score=Decimal("0.95"),
                flexibility_score=Decimal("0.85"),
                renewable_score=Decimal("1.0"),
                rating_score=Decimal("0.90"),
                projected_annual_cost=Decimal("1200.00"),
            ),
            RankedPlan(
                plan_id=mock_recommended_plan_variable.id,
                rank=2,
                composite_score=Decimal("0.88"),
                cost_score=Decimal("0.90"),
                flexibility_score=Decimal("1.0"),
                renewable_score=Decimal("0.50"),
                rating_score=Decimal("0.90"),
                projected_annual_cost=Decimal("1250.00"),
            ),
        ]

        plan_catalog = {
            mock_recommended_plan_fixed.id: mock_recommended_plan_fixed,
            mock_recommended_plan_variable.id: mock_recommended_plan_variable,
        }

        result = savings_service.generate_comparison(
            plans=ranked_plans,
            current_plan=mock_current_plan,
            usage_projection=mock_usage_projection,
            plan_catalog=plan_catalog,
            user_id=user_id,
        )

        # Verify structure
        assert isinstance(result, PlanComparison)
        assert result.user_id == user_id
        assert len(result.plans) == 2
        assert result.current_plan.is_current_plan is True

    def test_best_by_category_identification(
        self,
        savings_service,
        mock_current_plan,
        mock_recommended_plan_fixed,
        mock_recommended_plan_variable,
        mock_usage_projection,
    ):
        """Test identification of best plans in each category."""
        user_id = uuid4()

        ranked_plans = [
            RankedPlan(
                plan_id=mock_recommended_plan_fixed.id,
                rank=1,
                composite_score=Decimal("0.92"),
                cost_score=Decimal("0.95"),
                flexibility_score=Decimal("0.85"),
                renewable_score=Decimal("1.0"),
                rating_score=Decimal("0.90"),
                projected_annual_cost=Decimal("1200.00"),
            ),
            RankedPlan(
                plan_id=mock_recommended_plan_variable.id,
                rank=2,
                composite_score=Decimal("0.88"),
                cost_score=Decimal("0.90"),
                flexibility_score=Decimal("1.0"),
                renewable_score=Decimal("0.50"),
                rating_score=Decimal("0.90"),
                projected_annual_cost=Decimal("1250.00"),
            ),
        ]

        plan_catalog = {
            mock_recommended_plan_fixed.id: mock_recommended_plan_fixed,
            mock_recommended_plan_variable.id: mock_recommended_plan_variable,
        }

        result = savings_service.generate_comparison(
            plans=ranked_plans,
            current_plan=mock_current_plan,
            usage_projection=mock_usage_projection,
            plan_catalog=plan_catalog,
            user_id=user_id,
        )

        # Verify best by category
        assert "lowest_cost" in result.best_by_category
        assert "highest_renewable" in result.best_by_category
        assert "most_flexible" in result.best_by_category

        # Fixed plan should be highest renewable (100%)
        assert result.best_by_category["highest_renewable"] == mock_recommended_plan_fixed.id

        # Variable plan should be most flexible (0 month contract)
        assert result.best_by_category["most_flexible"] == mock_recommended_plan_variable.id

    def test_trade_off_generation(
        self,
        savings_service,
        mock_current_plan,
        mock_recommended_plan_fixed,
        mock_recommended_plan_variable,
        mock_usage_projection,
    ):
        """Test trade-off analysis generation."""
        user_id = uuid4()

        ranked_plans = [
            RankedPlan(
                plan_id=mock_recommended_plan_fixed.id,
                rank=1,
                composite_score=Decimal("0.92"),
                cost_score=Decimal("0.95"),
                flexibility_score=Decimal("0.85"),
                renewable_score=Decimal("1.0"),
                rating_score=Decimal("0.90"),
                projected_annual_cost=Decimal("1200.00"),
            ),
            RankedPlan(
                plan_id=mock_recommended_plan_variable.id,
                rank=2,
                composite_score=Decimal("0.88"),
                cost_score=Decimal("0.90"),
                flexibility_score=Decimal("1.0"),
                renewable_score=Decimal("0.50"),
                rating_score=Decimal("0.90"),
                projected_annual_cost=Decimal("1250.00"),
            ),
        ]

        plan_catalog = {
            mock_recommended_plan_fixed.id: mock_recommended_plan_fixed,
            mock_recommended_plan_variable.id: mock_recommended_plan_variable,
        }

        result = savings_service.generate_comparison(
            plans=ranked_plans,
            current_plan=mock_current_plan,
            usage_projection=mock_usage_projection,
            plan_catalog=plan_catalog,
            user_id=user_id,
        )

        # Verify trade-offs exist
        assert len(result.trade_offs) > 0

        # Should have flexibility trade-off (fixed vs variable)
        flexibility_tradeoffs = [t for t in result.trade_offs if t.category == "flexibility"]
        assert len(flexibility_tradeoffs) > 0

    def test_multi_year_projections(
        self,
        savings_service,
        mock_current_plan,
        mock_recommended_plan_fixed,
        mock_usage_projection,
    ):
        """Test multi-year cost projections."""
        user_id = uuid4()

        ranked_plans = [
            RankedPlan(
                plan_id=mock_recommended_plan_fixed.id,
                rank=1,
                composite_score=Decimal("0.92"),
                cost_score=Decimal("0.95"),
                flexibility_score=Decimal("0.85"),
                renewable_score=Decimal("1.0"),
                rating_score=Decimal("0.90"),
                projected_annual_cost=Decimal("1200.00"),
            ),
        ]

        plan_catalog = {
            mock_recommended_plan_fixed.id: mock_recommended_plan_fixed,
        }

        result = savings_service.generate_comparison(
            plans=ranked_plans,
            current_plan=mock_current_plan,
            usage_projection=mock_usage_projection,
            plan_catalog=plan_catalog,
            user_id=user_id,
        )

        # Verify multi-year projections
        assert len(result.multi_year_projections) > 0

        plan_id_str = str(mock_recommended_plan_fixed.id)
        assert plan_id_str in result.multi_year_projections

        projections = result.multi_year_projections[plan_id_str]
        assert len(projections) == 3  # 1-3 years

        # Verify cumulative costs increase
        assert projections[0].cumulative_cost < projections[1].cumulative_cost
        assert projections[1].cumulative_cost < projections[2].cumulative_cost


# ===== EDGE CASES AND VALIDATION =====

class TestEdgeCases:
    """Test suite for edge cases and validation."""

    def test_negative_savings_scenario(
        self,
        savings_service,
        mock_current_plan,
        mock_usage_projection,
        mock_supplier,
    ):
        """Test when recommended plan is more expensive (negative savings)."""
        # Create expensive plan
        expensive_plan = PlanCatalogResponse(
            id=uuid4(),
            supplier_id=mock_supplier.id,
            plan_name="Premium Plan",
            plan_type="fixed",
            rate_structure={"type": "fixed", "rate_per_kwh": 18.0},  # More expensive than current
            contract_length_months=12,
            early_termination_fee=Decimal("0.00"),
            renewable_percentage=Decimal("100.00"),
            monthly_fee=Decimal("15.00"),  # High monthly fee
            connection_fee=Decimal("0.00"),
            available_regions=["75001"],
            is_active=True,
            last_updated=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            supplier=mock_supplier,
        )

        result = savings_service.calculate_annual_savings(
            current_plan=mock_current_plan,
            recommended_plan=expensive_plan,
            usage_projection=mock_usage_projection,
            user_id=uuid4(),
        )

        # Verify negative savings
        assert result.annual_savings < 0
        assert result.savings_percentage < 0

        # Verify warning about more expensive plan
        assert any("more expensive" in warning.lower() for warning in result.warnings)

    def test_low_confidence_projection(
        self,
        savings_service,
        mock_current_plan,
        mock_recommended_plan_fixed,
    ):
        """Test with low confidence usage projection."""
        low_confidence_projection = UsageProjection(
            projected_monthly_kwh=[800.0] * 12,
            projected_annual_kwh=9600.0,
            confidence_lower=[700.0] * 12,
            confidence_upper=[900.0] * 12,
            confidence_score=0.45,  # Low confidence
            method="insufficient_data",
            assumptions=["Limited historical data"],
        )

        result = savings_service.calculate_annual_savings(
            current_plan=mock_current_plan,
            recommended_plan=mock_recommended_plan_fixed,
            usage_projection=low_confidence_projection,
            user_id=uuid4(),
        )

        # Verify warning about low confidence
        confidence_warnings = [w for w in result.warnings if "confidence" in w.lower()]
        assert len(confidence_warnings) > 0

    def test_zero_contract_length(
        self,
        savings_service,
        mock_current_plan,
        mock_recommended_plan_variable,
        mock_usage_projection,
    ):
        """Test month-to-month plan (0 contract length)."""
        result = savings_service.calculate_annual_savings(
            current_plan=mock_current_plan,
            recommended_plan=mock_recommended_plan_variable,
            usage_projection=mock_usage_projection,
            user_id=uuid4(),
        )

        # Should default to 12 months for TCO
        assert result.contract_length_months >= 12

    def test_marginal_savings_warning(
        self,
        savings_service,
        mock_current_plan,
        mock_usage_projection,
        mock_supplier,
    ):
        """Test warning for marginal savings (<5%)."""
        # Create plan with similar cost to current
        similar_plan = PlanCatalogResponse(
            id=uuid4(),
            supplier_id=mock_supplier.id,
            plan_name="Similar Plan",
            plan_type="fixed",
            rate_structure={"type": "fixed", "rate_per_kwh": 12.3},  # Very close to current 12.5
            contract_length_months=12,
            early_termination_fee=Decimal("0.00"),
            renewable_percentage=Decimal("50.00"),
            monthly_fee=Decimal("9.95"),
            connection_fee=Decimal("0.00"),
            available_regions=["75001"],
            is_active=True,
            last_updated=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            supplier=mock_supplier,
        )

        result = savings_service.calculate_annual_savings(
            current_plan=mock_current_plan,
            recommended_plan=similar_plan,
            usage_projection=mock_usage_projection,
            user_id=uuid4(),
        )

        # Should have marginal savings warning if savings < 5%
        if result.savings_percentage < Decimal("5"):
            marginal_warnings = [w for w in result.warnings if "marginal" in w.lower()]
            assert len(marginal_warnings) > 0


# ===== INTEGRATION-STYLE TESTS =====

class TestEndToEndScenarios:
    """End-to-end scenario tests."""

    def test_complete_savings_analysis_workflow(
        self,
        savings_service,
        mock_current_plan,
        mock_recommended_plan_fixed,
        mock_usage_projection,
    ):
        """Test complete savings analysis workflow."""
        user_id = uuid4()

        result = savings_service.calculate_annual_savings(
            current_plan=mock_current_plan,
            recommended_plan=mock_recommended_plan_fixed,
            usage_projection=mock_usage_projection,
            user_id=user_id,
        )

        # Verify all key components
        assert result.plan_id is not None
        assert result.user_id == user_id
        assert result.projected_annual_cost > 0
        assert result.current_annual_cost > 0
        assert len(result.monthly_breakdown) == 12
        assert result.total_cost_of_ownership > 0
        assert result.contract_length_months > 0
        assert len(result.assumptions) > 0

        # Verify calculations are consistent
        calculated_annual = sum(m.total_cost for m in result.monthly_breakdown)
        assert abs(result.projected_annual_cost - calculated_annual) < Decimal("1.00")

    def test_complete_comparison_workflow(
        self,
        savings_service,
        mock_current_plan,
        mock_recommended_plan_fixed,
        mock_recommended_plan_variable,
        mock_usage_projection,
    ):
        """Test complete comparison workflow."""
        user_id = uuid4()

        ranked_plans = [
            RankedPlan(
                plan_id=mock_recommended_plan_fixed.id,
                rank=1,
                composite_score=Decimal("0.92"),
                cost_score=Decimal("0.95"),
                flexibility_score=Decimal("0.85"),
                renewable_score=Decimal("1.0"),
                rating_score=Decimal("0.90"),
                projected_annual_cost=Decimal("1200.00"),
            ),
            RankedPlan(
                plan_id=mock_recommended_plan_variable.id,
                rank=2,
                composite_score=Decimal("0.88"),
                cost_score=Decimal("0.90"),
                flexibility_score=Decimal("1.0"),
                renewable_score=Decimal("0.50"),
                rating_score=Decimal("0.90"),
                projected_annual_cost=Decimal("1250.00"),
            ),
        ]

        plan_catalog = {
            mock_recommended_plan_fixed.id: mock_recommended_plan_fixed,
            mock_recommended_plan_variable.id: mock_recommended_plan_variable,
        }

        result = savings_service.generate_comparison(
            plans=ranked_plans,
            current_plan=mock_current_plan,
            usage_projection=mock_usage_projection,
            plan_catalog=plan_catalog,
            user_id=user_id,
        )

        # Verify complete structure
        assert result.user_id == user_id
        assert len(result.plans) == 2
        assert result.current_plan.is_current_plan
        assert len(result.best_by_category) >= 3
        assert len(result.assumptions) > 0
        assert result.generated_at is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
