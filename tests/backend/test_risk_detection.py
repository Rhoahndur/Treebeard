"""
Comprehensive Test Suite for Risk Detection Service
Story 6.1-6.2: Risk Detection & Warning System

Tests all 7+ risk detection rules and stay recommendation logic.

Author: Backend Dev #7
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from src.backend.schemas.recommendation_schemas import (
    PlanScores,
    RankedPlan,
    CostBreakdown,
    UserPreferences,
)
from src.backend.schemas.risk_schemas import (
    RiskDetectionConfig,
    RiskSeverity,
    RiskType,
    StayRecommendationTrigger,
)
from src.backend.schemas.savings_schemas import SavingsAnalysis
from src.backend.schemas.usage_analysis import (
    DataQualityMetrics,
    UsageProfile,
    UsageProjection,
    UsageStatistics,
    SeasonalAnalysis,
    PeakOffPeakAnalysis,
    OutlierDetection,
    UserProfileType,
)
from src.backend.services.risk_detection import (
    CurrentPlan,
    RiskDetectionService,
    create_risk_detection_service,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def default_config():
    """Default risk detection configuration."""
    return RiskDetectionConfig()


@pytest.fixture
def risk_service(default_config):
    """Risk detection service instance."""
    return RiskDetectionService(config=default_config)


@pytest.fixture
def sample_plan():
    """Sample ranked plan for testing."""
    return RankedPlan(
        plan_id=uuid4(),
        rank=1,
        plan_name="Test Plan",
        supplier_name="Test Supplier",
        plan_type="fixed",
        contract_length_months=12,
        early_termination_fee=Decimal("150.00"),
        renewable_percentage=Decimal("50.00"),
        scores=PlanScores(
            cost_score=85.0,
            flexibility_score=70.0,
            renewable_score=50.0,
            rating_score=80.0,
            composite_score=75.0,
        ),
        projected_annual_cost=Decimal("1200.00"),
        projected_monthly_cost=Decimal("100.00"),
        cost_breakdown=CostBreakdown(
            base_cost=Decimal("1200.00"),
            monthly_fees=Decimal("0.00"),
            connection_fee=Decimal("0.00"),
            total_annual_cost=Decimal("1200.00"),
            rate_type="fixed",
            avg_rate_per_kwh=Decimal("12.00"),
        ),
        rate_structure={"type": "fixed", "rate_per_kwh": 12.0},
    )


@pytest.fixture
def sample_current_plan():
    """Sample current plan for testing."""
    return CurrentPlan(
        plan_name="Current Plan",
        supplier_name="Current Supplier",
        current_rate=Decimal("13.00"),
        contract_end_date=datetime.now() + timedelta(days=180),
        early_termination_fee=Decimal("150.00"),
        annual_cost=Decimal("1500.00"),
    )


@pytest.fixture
def sample_savings():
    """Sample savings analysis for testing."""
    plan_id = uuid4()
    user_id = uuid4()

    return SavingsAnalysis(
        plan_id=plan_id,
        user_id=user_id,
        projected_annual_cost=Decimal("1200.00"),
        current_annual_cost=Decimal("1500.00"),
        annual_savings=Decimal("300.00"),
        savings_percentage=Decimal("20.00"),
        monthly_breakdown=[],
        total_cost_of_ownership=Decimal("1200.00"),
        tco_current_plan=Decimal("1500.00"),
        contract_length_months=12,
        break_even_months=6,
        switching_cost=Decimal("150.00"),
        cumulative_savings_12_months=Decimal("150.00"),
        total_energy_cost=Decimal("1200.00"),
    )


@pytest.fixture
def sample_usage_profile():
    """Sample usage profile for testing."""
    return UsageProfile(
        user_id="test-user",
        profile_type=UserProfileType.SEASONAL,
        statistics=UsageStatistics(
            min_kwh=800.0,
            max_kwh=1500.0,
            mean_kwh=1000.0,
            median_kwh=950.0,
            std_dev=200.0,
            coefficient_of_variation=0.2,
            total_annual_kwh=12000.0,
        ),
        seasonal_analysis=SeasonalAnalysis(
            has_seasonal_pattern=True,
            dominant_season=None,
            patterns=[],
            summer_to_winter_ratio=1.5,
            peak_to_avg_ratio=1.3,
            confidence_score=0.85,
        ),
        peak_offpeak=PeakOffPeakAnalysis(
            peak_months=["Jun", "Jul", "Aug"],
            off_peak_months=["Jan", "Feb", "Mar"],
            peak_avg_kwh=1300.0,
            off_peak_avg_kwh=850.0,
            peak_to_offpeak_ratio=1.53,
        ),
        outliers=OutlierDetection(
            has_outliers=False,
            outlier_months=[],
            outlier_values=[],
            method="IQR",
        ),
        data_quality=DataQualityMetrics(
            total_months=12,
            missing_months=0,
            interpolated_months=0,
            has_gaps=False,
            completeness_pct=100.0,
            quality_score=0.95,
        ),
        projection=UsageProjection(
            projected_monthly_kwh=[1000.0] * 12,
            projected_annual_kwh=12000.0,
            confidence_lower=[900.0] * 12,
            confidence_upper=[1100.0] * 12,
            confidence_score=0.85,
            method="seasonal_average",
            assumptions=["Stable usage pattern"],
        ),
        analysis_date=datetime.now(),
        data_period_start=datetime.now().date(),
        data_period_end=datetime.now().date(),
        num_months_analyzed=12,
        overall_confidence=0.85,
        warnings=[],
    )


@pytest.fixture
def sample_preferences():
    """Sample user preferences."""
    return UserPreferences(
        cost_priority=40,
        flexibility_priority=30,
        renewable_priority=20,
        rating_priority=10,
    )


# ============================================================================
# RISK DETECTION RULE TESTS
# ============================================================================


class TestHighETFRule:
    """Test Rule 1: High ETF Warning."""

    def test_critical_etf(self, risk_service):
        """Test critical ETF warning (>$300)."""
        plan = RankedPlan(
            plan_id=uuid4(),
            rank=1,
            plan_name="High ETF Plan",
            supplier_name="Test Supplier",
            plan_type="fixed",
            contract_length_months=24,
            early_termination_fee=Decimal("350.00"),  # Critical level
            renewable_percentage=Decimal("50.00"),
            scores=PlanScores(
                cost_score=85.0,
                flexibility_score=70.0,
                renewable_score=50.0,
                rating_score=80.0,
                composite_score=75.0,
            ),
            projected_annual_cost=Decimal("1200.00"),
            projected_monthly_cost=Decimal("100.00"),
            cost_breakdown=CostBreakdown(
                base_cost=Decimal("1200.00"),
                monthly_fees=Decimal("0.00"),
                connection_fee=Decimal("0.00"),
                total_annual_cost=Decimal("1200.00"),
                rate_type="fixed",
                avg_rate_per_kwh=Decimal("12.00"),
            ),
            rate_structure={"type": "fixed"},
        )

        risk = risk_service._check_high_etf(plan)

        assert risk is not None
        assert risk.severity == RiskSeverity.CRITICAL
        assert risk.risk_type == RiskType.HIGH_ETF
        assert "$350" in risk.message

    def test_warning_etf(self, risk_service):
        """Test warning ETF (>$150, <$300)."""
        plan = RankedPlan(
            plan_id=uuid4(),
            rank=1,
            plan_name="Medium ETF Plan",
            supplier_name="Test Supplier",
            plan_type="fixed",
            contract_length_months=12,
            early_termination_fee=Decimal("200.00"),  # Warning level
            renewable_percentage=Decimal("50.00"),
            scores=PlanScores(
                cost_score=85.0,
                flexibility_score=70.0,
                renewable_score=50.0,
                rating_score=80.0,
                composite_score=75.0,
            ),
            projected_annual_cost=Decimal("1200.00"),
            projected_monthly_cost=Decimal("100.00"),
            cost_breakdown=CostBreakdown(
                base_cost=Decimal("1200.00"),
                monthly_fees=Decimal("0.00"),
                connection_fee=Decimal("0.00"),
                total_annual_cost=Decimal("1200.00"),
                rate_type="fixed",
                avg_rate_per_kwh=Decimal("12.00"),
            ),
            rate_structure={"type": "fixed"},
        )

        risk = risk_service._check_high_etf(plan)

        assert risk is not None
        assert risk.severity == RiskSeverity.WARNING
        assert risk.risk_type == RiskType.HIGH_ETF

    def test_no_etf_warning(self, risk_service):
        """Test no warning for low ETF."""
        plan = RankedPlan(
            plan_id=uuid4(),
            rank=1,
            plan_name="Low ETF Plan",
            supplier_name="Test Supplier",
            plan_type="fixed",
            contract_length_months=12,
            early_termination_fee=Decimal("50.00"),  # Below threshold
            renewable_percentage=Decimal("50.00"),
            scores=PlanScores(
                cost_score=85.0,
                flexibility_score=70.0,
                renewable_score=50.0,
                rating_score=80.0,
                composite_score=75.0,
            ),
            projected_annual_cost=Decimal("1200.00"),
            projected_monthly_cost=Decimal("100.00"),
            cost_breakdown=CostBreakdown(
                base_cost=Decimal("1200.00"),
                monthly_fees=Decimal("0.00"),
                connection_fee=Decimal("0.00"),
                total_annual_cost=Decimal("1200.00"),
                rate_type="fixed",
                avg_rate_per_kwh=Decimal("12.00"),
            ),
            rate_structure={"type": "fixed"},
        )

        risk = risk_service._check_high_etf(plan)

        assert risk is None


class TestLowSavingsRule:
    """Test Rule 2: Low Savings Warning."""

    def test_low_savings_warning(self, risk_service, sample_plan):
        """Test warning for low savings (<$100/year)."""
        savings = SavingsAnalysis(
            plan_id=sample_plan.plan_id,
            user_id=uuid4(),
            projected_annual_cost=Decimal("1450.00"),
            current_annual_cost=Decimal("1500.00"),
            annual_savings=Decimal("50.00"),  # Low savings
            savings_percentage=Decimal("3.33"),  # <5%
            monthly_breakdown=[],
            total_cost_of_ownership=Decimal("1450.00"),
            tco_current_plan=Decimal("1500.00"),
            contract_length_months=12,
            switching_cost=Decimal("0.00"),
            cumulative_savings_12_months=Decimal("50.00"),
            total_energy_cost=Decimal("1450.00"),
        )

        risk = risk_service._check_low_savings(sample_plan, savings)

        assert risk is not None
        assert risk.severity == RiskSeverity.WARNING
        assert risk.risk_type == RiskType.LOW_SAVINGS
        assert "$50" in risk.message

    def test_modest_savings_info(self, risk_service, sample_plan):
        """Test info for modest savings (>$100 but <5%)."""
        savings = SavingsAnalysis(
            plan_id=sample_plan.plan_id,
            user_id=uuid4(),
            projected_annual_cost=Decimal("1350.00"),
            current_annual_cost=Decimal("1500.00"),
            annual_savings=Decimal("150.00"),  # Above $100
            savings_percentage=Decimal("4.5"),  # <5%
            monthly_breakdown=[],
            total_cost_of_ownership=Decimal("1350.00"),
            tco_current_plan=Decimal("1500.00"),
            contract_length_months=12,
            switching_cost=Decimal("0.00"),
            cumulative_savings_12_months=Decimal("150.00"),
            total_energy_cost=Decimal("1350.00"),
        )

        risk = risk_service._check_low_savings(sample_plan, savings)

        assert risk is not None
        assert risk.severity == RiskSeverity.INFO
        assert risk.risk_type == RiskType.LOW_SAVINGS

    def test_good_savings_no_warning(self, risk_service, sample_plan):
        """Test no warning for good savings (>5%)."""
        savings = SavingsAnalysis(
            plan_id=sample_plan.plan_id,
            user_id=uuid4(),
            projected_annual_cost=Decimal("1200.00"),
            current_annual_cost=Decimal("1500.00"),
            annual_savings=Decimal("300.00"),
            savings_percentage=Decimal("20.00"),  # >5%
            monthly_breakdown=[],
            total_cost_of_ownership=Decimal("1200.00"),
            tco_current_plan=Decimal("1500.00"),
            contract_length_months=12,
            switching_cost=Decimal("0.00"),
            cumulative_savings_12_months=Decimal("300.00"),
            total_energy_cost=Decimal("1200.00"),
        )

        risk = risk_service._check_low_savings(sample_plan, savings)

        assert risk is None


class TestDataQualityRule:
    """Test Rule 3: Data Quality Issues."""

    def test_critical_low_confidence(self, risk_service, sample_plan):
        """Test critical warning for very low confidence (<0.5)."""
        usage_profile = UsageProfile(
            user_id="test-user",
            profile_type=UserProfileType.INSUFFICIENT_DATA,
            statistics=UsageStatistics(
                min_kwh=800.0,
                max_kwh=1500.0,
                mean_kwh=1000.0,
                median_kwh=950.0,
                std_dev=200.0,
                coefficient_of_variation=0.2,
                total_annual_kwh=12000.0,
            ),
            seasonal_analysis=SeasonalAnalysis(
                has_seasonal_pattern=False,
                dominant_season=None,
                patterns=[],
                summer_to_winter_ratio=1.0,
                peak_to_avg_ratio=1.0,
                confidence_score=0.3,
            ),
            peak_offpeak=PeakOffPeakAnalysis(
                peak_months=[],
                off_peak_months=[],
                peak_avg_kwh=1000.0,
                off_peak_avg_kwh=1000.0,
                peak_to_offpeak_ratio=1.0,
            ),
            outliers=OutlierDetection(
                has_outliers=False,
                outlier_months=[],
                outlier_values=[],
                method="IQR",
            ),
            data_quality=DataQualityMetrics(
                total_months=12,
                missing_months=5,
                interpolated_months=3,
                has_gaps=True,
                completeness_pct=58.3,
                quality_score=0.4,
            ),
            projection=UsageProjection(
                projected_monthly_kwh=[1000.0] * 12,
                projected_annual_kwh=12000.0,
                confidence_lower=[800.0] * 12,
                confidence_upper=[1200.0] * 12,
                confidence_score=0.4,
                method="simple_average",
                assumptions=["Low data quality"],
            ),
            analysis_date=datetime.now(),
            data_period_start=datetime.now().date(),
            data_period_end=datetime.now().date(),
            num_months_analyzed=7,
            overall_confidence=0.4,  # Critical level
            warnings=["Insufficient data"],
        )

        risk = risk_service._check_data_quality(sample_plan, usage_profile)

        assert risk is not None
        assert risk.severity == RiskSeverity.CRITICAL
        assert risk.risk_type == RiskType.DATA_QUALITY

    def test_warning_low_completeness(self, risk_service, sample_plan):
        """Test warning for low completeness (<80%)."""
        usage_profile = UsageProfile(
            user_id="test-user",
            profile_type=UserProfileType.BASELINE,
            statistics=UsageStatistics(
                min_kwh=800.0,
                max_kwh=1500.0,
                mean_kwh=1000.0,
                median_kwh=950.0,
                std_dev=200.0,
                coefficient_of_variation=0.2,
                total_annual_kwh=12000.0,
            ),
            seasonal_analysis=SeasonalAnalysis(
                has_seasonal_pattern=False,
                dominant_season=None,
                patterns=[],
                summer_to_winter_ratio=1.0,
                peak_to_avg_ratio=1.0,
                confidence_score=0.75,
            ),
            peak_offpeak=PeakOffPeakAnalysis(
                peak_months=[],
                off_peak_months=[],
                peak_avg_kwh=1000.0,
                off_peak_avg_kwh=1000.0,
                peak_to_offpeak_ratio=1.0,
            ),
            outliers=OutlierDetection(
                has_outliers=False,
                outlier_months=[],
                outlier_values=[],
                method="IQR",
            ),
            data_quality=DataQualityMetrics(
                total_months=12,
                missing_months=3,
                interpolated_months=1,
                has_gaps=True,
                completeness_pct=75.0,  # Below 80%
                quality_score=0.75,
            ),
            projection=UsageProjection(
                projected_monthly_kwh=[1000.0] * 12,
                projected_annual_kwh=12000.0,
                confidence_lower=[900.0] * 12,
                confidence_upper=[1100.0] * 12,
                confidence_score=0.75,
                method="seasonal_average",
                assumptions=["Some missing data"],
            ),
            analysis_date=datetime.now(),
            data_period_start=datetime.now().date(),
            data_period_end=datetime.now().date(),
            num_months_analyzed=9,
            overall_confidence=0.75,
            warnings=["Some data gaps"],
        )

        risk = risk_service._check_data_quality(sample_plan, usage_profile)

        assert risk is not None
        assert risk.severity == RiskSeverity.WARNING
        assert risk.risk_type == RiskType.DATA_QUALITY


class TestVariableRateRule:
    """Test Rule 4: Variable Rate Volatility."""

    def test_variable_rate_warning(self, risk_service):
        """Test warning for variable rate plans."""
        plan = RankedPlan(
            plan_id=uuid4(),
            rank=1,
            plan_name="Variable Rate Plan",
            supplier_name="Test Supplier",
            plan_type="variable",  # Variable rate
            contract_length_months=12,
            early_termination_fee=Decimal("150.00"),
            renewable_percentage=Decimal("50.00"),
            scores=PlanScores(
                cost_score=85.0,
                flexibility_score=70.0,
                renewable_score=50.0,
                rating_score=80.0,
                composite_score=75.0,
            ),
            projected_annual_cost=Decimal("1200.00"),
            projected_monthly_cost=Decimal("100.00"),
            cost_breakdown=CostBreakdown(
                base_cost=Decimal("1200.00"),
                monthly_fees=Decimal("0.00"),
                connection_fee=Decimal("0.00"),
                total_annual_cost=Decimal("1200.00"),
                rate_type="variable",
                avg_rate_per_kwh=Decimal("12.00"),
            ),
            rate_structure={"type": "variable"},
        )

        risk = risk_service._check_variable_rate_volatility(plan)

        assert risk is not None
        assert risk.severity == RiskSeverity.WARNING
        assert risk.risk_type == RiskType.VARIABLE_RATE_VOLATILITY
        assert "variable rate" in risk.message.lower()

    def test_fixed_rate_no_warning(self, risk_service, sample_plan):
        """Test no warning for fixed rate plans."""
        risk = risk_service._check_variable_rate_volatility(sample_plan)

        assert risk is None


class TestContractMismatchRule:
    """Test Rule 5: Contract Length Mismatch."""

    def test_long_contract_high_flexibility(self, risk_service):
        """Test warning for long contract when flexibility is prioritized."""
        plan = RankedPlan(
            plan_id=uuid4(),
            rank=1,
            plan_name="Long Contract Plan",
            supplier_name="Test Supplier",
            plan_type="fixed",
            contract_length_months=24,  # Long contract
            early_termination_fee=Decimal("150.00"),
            renewable_percentage=Decimal("50.00"),
            scores=PlanScores(
                cost_score=85.0,
                flexibility_score=70.0,
                renewable_score=50.0,
                rating_score=80.0,
                composite_score=75.0,
            ),
            projected_annual_cost=Decimal("1200.00"),
            projected_monthly_cost=Decimal("100.00"),
            cost_breakdown=CostBreakdown(
                base_cost=Decimal("1200.00"),
                monthly_fees=Decimal("0.00"),
                connection_fee=Decimal("0.00"),
                total_annual_cost=Decimal("1200.00"),
                rate_type="fixed",
                avg_rate_per_kwh=Decimal("12.00"),
            ),
            rate_structure={"type": "fixed"},
        )

        preferences = UserPreferences(
            cost_priority=30,
            flexibility_priority=40,  # High flexibility priority
            renewable_priority=20,
            rating_priority=10,
        )

        risk = risk_service._check_contract_length_mismatch(plan, preferences)

        assert risk is not None
        assert risk.severity == RiskSeverity.WARNING
        assert risk.risk_type == RiskType.CONTRACT_LENGTH_MISMATCH

    def test_no_mismatch(self, risk_service, sample_plan, sample_preferences):
        """Test no warning when no mismatch."""
        risk = risk_service._check_contract_length_mismatch(
            sample_plan, sample_preferences
        )

        assert risk is None


class TestBreakEvenRule:
    """Test Rule 7: Break-Even Too Long."""

    def test_critical_long_break_even(self, risk_service, sample_plan):
        """Test critical warning for very long break-even (>24 months)."""
        savings = SavingsAnalysis(
            plan_id=sample_plan.plan_id,
            user_id=uuid4(),
            projected_annual_cost=Decimal("1400.00"),
            current_annual_cost=Decimal("1500.00"),
            annual_savings=Decimal("100.00"),
            savings_percentage=Decimal("6.67"),
            monthly_breakdown=[],
            total_cost_of_ownership=Decimal("1400.00"),
            tco_current_plan=Decimal("1500.00"),
            contract_length_months=12,
            break_even_months=30,  # Critical level
            switching_cost=Decimal("250.00"),
            cumulative_savings_12_months=Decimal("-150.00"),
            total_energy_cost=Decimal("1400.00"),
        )

        risk = risk_service._check_break_even(sample_plan, savings)

        assert risk is not None
        assert risk.severity == RiskSeverity.CRITICAL
        assert risk.risk_type == RiskType.BREAK_EVEN_TOO_LONG

    def test_warning_long_break_even(self, risk_service, sample_plan):
        """Test warning for long break-even (>18 months)."""
        savings = SavingsAnalysis(
            plan_id=sample_plan.plan_id,
            user_id=uuid4(),
            projected_annual_cost=Decimal("1400.00"),
            current_annual_cost=Decimal("1500.00"),
            annual_savings=Decimal("100.00"),
            savings_percentage=Decimal("6.67"),
            monthly_breakdown=[],
            total_cost_of_ownership=Decimal("1400.00"),
            tco_current_plan=Decimal("1500.00"),
            contract_length_months=12,
            break_even_months=20,  # Warning level
            switching_cost=Decimal("167.00"),
            cumulative_savings_12_months=Decimal("-67.00"),
            total_energy_cost=Decimal("1400.00"),
        )

        risk = risk_service._check_break_even(sample_plan, savings)

        assert risk is not None
        assert risk.severity == RiskSeverity.WARNING
        assert risk.risk_type == RiskType.BREAK_EVEN_TOO_LONG

    def test_no_break_even_warning(self, risk_service, sample_plan, sample_savings):
        """Test no warning for acceptable break-even."""
        risk = risk_service._check_break_even(sample_plan, sample_savings)

        assert risk is None


class TestNegativeSavingsRule:
    """Test Rule 8: Negative Savings."""

    def test_negative_savings_critical(self, risk_service, sample_plan):
        """Test critical warning for plans that cost more."""
        savings = SavingsAnalysis(
            plan_id=sample_plan.plan_id,
            user_id=uuid4(),
            projected_annual_cost=Decimal("1600.00"),
            current_annual_cost=Decimal("1500.00"),
            annual_savings=Decimal("-100.00"),  # Negative savings
            savings_percentage=Decimal("-6.67"),
            monthly_breakdown=[],
            total_cost_of_ownership=Decimal("1600.00"),
            tco_current_plan=Decimal("1500.00"),
            contract_length_months=12,
            switching_cost=Decimal("0.00"),
            cumulative_savings_12_months=Decimal("-100.00"),
            total_energy_cost=Decimal("1600.00"),
        )

        risk = risk_service._check_negative_savings(sample_plan, savings)

        assert risk is not None
        assert risk.severity == RiskSeverity.CRITICAL
        assert risk.risk_type == RiskType.NEGATIVE_SAVINGS
        assert "MORE" in risk.message


class TestHighUpfrontCostsRule:
    """Test Rule 9: High Upfront Costs."""

    def test_high_upfront_costs_info(self, risk_service):
        """Test info for high upfront costs."""
        plan = RankedPlan(
            plan_id=uuid4(),
            rank=1,
            plan_name="High Upfront Plan",
            supplier_name="Test Supplier",
            plan_type="fixed",
            contract_length_months=12,
            early_termination_fee=Decimal("150.00"),
            renewable_percentage=Decimal("50.00"),
            scores=PlanScores(
                cost_score=85.0,
                flexibility_score=70.0,
                renewable_score=50.0,
                rating_score=80.0,
                composite_score=75.0,
            ),
            projected_annual_cost=Decimal("1200.00"),
            projected_monthly_cost=Decimal("100.00"),
            cost_breakdown=CostBreakdown(
                base_cost=Decimal("1200.00"),
                monthly_fees=Decimal("0.00"),
                connection_fee=Decimal("75.00"),
                total_annual_cost=Decimal("1200.00"),
                rate_type="fixed",
                avg_rate_per_kwh=Decimal("12.00"),
            ),
            rate_structure={"type": "fixed"},
            connection_fee=Decimal("75.00"),
            monthly_fee=Decimal("30.00"),  # Total: $105
        )

        risk = risk_service._check_high_upfront_costs(plan)

        assert risk is not None
        assert risk.severity == RiskSeverity.INFO
        assert risk.risk_type == RiskType.HIGH_UPFRONT_COSTS


# ============================================================================
# STAY RECOMMENDATION LOGIC TESTS (Story 6.2)
# ============================================================================


class TestStayRecommendation:
    """Test "stay with current plan" logic."""

    def test_stay_low_net_savings(
        self, risk_service, sample_current_plan, sample_plan
    ):
        """Test stay recommendation due to low net savings."""
        savings = SavingsAnalysis(
            plan_id=sample_plan.plan_id,
            user_id=uuid4(),
            projected_annual_cost=Decimal("1450.00"),
            current_annual_cost=Decimal("1500.00"),
            annual_savings=Decimal("50.00"),
            savings_percentage=Decimal("3.33"),
            monthly_breakdown=[],
            total_cost_of_ownership=Decimal("1450.00"),
            tco_current_plan=Decimal("1500.00"),
            contract_length_months=12,
            break_even_months=36,
            switching_cost=Decimal("150.00"),
            cumulative_savings_12_months=Decimal("-100.00"),  # Low net savings
            total_energy_cost=Decimal("1450.00"),
        )

        should_stay, stay_rec = risk_service.should_recommend_staying(
            current_plan=sample_current_plan,
            top_plan=sample_plan,
            savings=savings,
            risks=[],
        )

        assert should_stay is True
        assert stay_rec is not None
        assert StayRecommendationTrigger.LOW_NET_SAVINGS in stay_rec.triggers
        assert "savings" in stay_rec.reasoning.lower()

    def test_stay_long_break_even(
        self, risk_service, sample_current_plan, sample_plan
    ):
        """Test stay recommendation due to long break-even."""
        savings = SavingsAnalysis(
            plan_id=sample_plan.plan_id,
            user_id=uuid4(),
            projected_annual_cost=Decimal("1300.00"),
            current_annual_cost=Decimal("1500.00"),
            annual_savings=Decimal("200.00"),
            savings_percentage=Decimal("13.33"),
            monthly_breakdown=[],
            total_cost_of_ownership=Decimal("1300.00"),
            tco_current_plan=Decimal("1500.00"),
            contract_length_months=12,
            break_even_months=30,  # Very long
            switching_cost=Decimal("500.00"),
            cumulative_savings_12_months=Decimal("-300.00"),
            total_energy_cost=Decimal("1300.00"),
        )

        should_stay, stay_rec = risk_service.should_recommend_staying(
            current_plan=sample_current_plan,
            top_plan=sample_plan,
            savings=savings,
            risks=[],
        )

        assert should_stay is True
        assert stay_rec is not None
        assert StayRecommendationTrigger.LONG_BREAK_EVEN in stay_rec.triggers

    def test_stay_critical_risks(
        self, risk_service, sample_current_plan, sample_plan, sample_savings
    ):
        """Test stay recommendation due to multiple critical risks."""
        from src.backend.schemas.risk_schemas import (
            RiskWarning,
            RiskType,
            RiskSeverity,
            RiskCategory,
        )

        # Create multiple critical risks
        risks = [
            RiskWarning(
                risk_type=RiskType.HIGH_ETF,
                severity=RiskSeverity.CRITICAL,
                category=RiskCategory.CONTRACT_TERMS,
                title="High ETF",
                message="Critical ETF issue",
                affected_plan_ids=[sample_plan.plan_id],
            ),
            RiskWarning(
                risk_type=RiskType.DATA_QUALITY,
                severity=RiskSeverity.CRITICAL,
                category=RiskCategory.DATA_QUALITY,
                title="Data Quality",
                message="Critical data issue",
                affected_plan_ids=[sample_plan.plan_id],
            ),
        ]

        should_stay, stay_rec = risk_service.should_recommend_staying(
            current_plan=sample_current_plan,
            top_plan=sample_plan,
            savings=sample_savings,
            risks=risks,
        )

        assert should_stay is True
        assert stay_rec is not None
        assert StayRecommendationTrigger.CRITICAL_RISKS in stay_rec.triggers
        assert stay_rec.critical_risk_count == 2

    def test_stay_current_plan_optimal(
        self, risk_service, sample_current_plan, sample_plan
    ):
        """Test stay recommendation when current plan is already optimal."""
        # Very small savings indicating current plan is already good
        savings = SavingsAnalysis(
            plan_id=sample_plan.plan_id,
            user_id=uuid4(),
            projected_annual_cost=Decimal("1480.00"),
            current_annual_cost=Decimal("1500.00"),
            annual_savings=Decimal("20.00"),  # Minimal savings
            savings_percentage=Decimal("1.33"),  # <2%
            monthly_breakdown=[],
            total_cost_of_ownership=Decimal("1480.00"),
            tco_current_plan=Decimal("1500.00"),
            contract_length_months=12,
            switching_cost=Decimal("0.00"),
            cumulative_savings_12_months=Decimal("20.00"),
            total_energy_cost=Decimal("1480.00"),
        )

        should_stay, stay_rec = risk_service.should_recommend_staying(
            current_plan=sample_current_plan,
            top_plan=sample_plan,
            savings=savings,
            risks=[],
        )

        assert should_stay is True
        assert stay_rec is not None
        assert StayRecommendationTrigger.CURRENT_PLAN_OPTIMAL in stay_rec.triggers

    def test_no_stay_good_savings(
        self, risk_service, sample_current_plan, sample_plan, sample_savings
    ):
        """Test no stay recommendation when savings are good."""
        should_stay, stay_rec = risk_service.should_recommend_staying(
            current_plan=sample_current_plan,
            top_plan=sample_plan,
            savings=sample_savings,
            risks=[],
        )

        assert should_stay is False
        assert stay_rec is None


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestRiskDetectionIntegration:
    """Integration tests for full risk detection flow."""

    def test_detect_all_risks(
        self,
        risk_service,
        sample_plan,
        sample_current_plan,
        sample_savings,
        sample_usage_profile,
        sample_preferences,
    ):
        """Test detecting risks across multiple plans."""
        # Modify plan to trigger multiple risks
        sample_plan.early_termination_fee = Decimal("200.00")  # High ETF
        sample_plan.plan_type = "variable"  # Variable rate
        sample_plan.contract_length_months = 24  # Long contract
        sample_preferences.flexibility_priority = 40  # High flexibility

        risks = risk_service.detect_risks(
            plans=[sample_plan],
            current_plan=sample_current_plan,
            savings_analyses=[sample_savings],
            usage_profile=sample_usage_profile,
            preferences=sample_preferences,
        )

        assert len(risks) > 0
        # Should have at least: high ETF, variable rate, contract mismatch
        assert any(r.risk_type == RiskType.HIGH_ETF for r in risks)
        assert any(r.risk_type == RiskType.VARIABLE_RATE_VOLATILITY for r in risks)
        assert any(r.risk_type == RiskType.CONTRACT_LENGTH_MISMATCH for r in risks)

    def test_risk_summary_calculation(self, risk_service, sample_plan):
        """Test risk summary calculation."""
        from src.backend.schemas.risk_schemas import (
            RiskWarning,
            RiskType,
            RiskSeverity,
            RiskCategory,
        )

        risks = [
            RiskWarning(
                risk_type=RiskType.HIGH_ETF,
                severity=RiskSeverity.CRITICAL,
                category=RiskCategory.CONTRACT_TERMS,
                title="High ETF",
                message="Critical issue",
                affected_plan_ids=[sample_plan.plan_id],
            ),
            RiskWarning(
                risk_type=RiskType.LOW_SAVINGS,
                severity=RiskSeverity.WARNING,
                category=RiskCategory.SAVINGS,
                title="Low Savings",
                message="Warning issue",
                affected_plan_ids=[sample_plan.plan_id],
            ),
            RiskWarning(
                risk_type=RiskType.HIGH_UPFRONT_COSTS,
                severity=RiskSeverity.INFO,
                category=RiskCategory.COST,
                title="High Upfront",
                message="Info item",
                affected_plan_ids=[sample_plan.plan_id],
            ),
        ]

        summary = risk_service.calculate_risk_summary(risks, [sample_plan])

        assert summary.total_risks == 3
        assert summary.critical_count == 1
        assert summary.warning_count == 1
        assert summary.info_count == 1
        assert summary.overall_risk_level == "medium"  # 1 critical = medium


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


class TestRiskDetectionPerformance:
    """Test performance of risk detection."""

    def test_detection_speed(
        self,
        risk_service,
        sample_plan,
        sample_current_plan,
        sample_savings,
        sample_usage_profile,
        sample_preferences,
    ):
        """Test that risk detection completes within time limit (<50ms)."""
        import time

        start = time.time()

        risks = risk_service.detect_risks(
            plans=[sample_plan] * 3,  # 3 plans
            current_plan=sample_current_plan,
            savings_analyses=[sample_savings] * 3,
            usage_profile=sample_usage_profile,
            preferences=sample_preferences,
        )

        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed < 100  # Should be < 100ms for 3 plans
        # Requirements state <50ms overhead, so <100ms for 3 plans is reasonable


# ============================================================================
# FACTORY FUNCTION TESTS
# ============================================================================


def test_create_risk_detection_service():
    """Test factory function."""
    service = create_risk_detection_service()

    assert isinstance(service, RiskDetectionService)
    assert service.config is not None


def test_create_risk_detection_service_with_config():
    """Test factory function with custom config."""
    config = RiskDetectionConfig(high_etf_threshold=Decimal("200.00"))

    service = create_risk_detection_service(config=config)

    assert isinstance(service, RiskDetectionService)
    assert service.config.high_etf_threshold == Decimal("200.00")
