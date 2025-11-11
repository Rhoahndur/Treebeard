"""
Unit tests for Recommendation Engine (Stories 2.1, 2.2, 2.3)

Tests cover:
- Story 2.1: Scoring algorithm (cost, flexibility, renewable, rating, composite)
- Story 2.2: Plan matching, filtering, ranking, cost calculation
- Story 2.3: Contract timing optimization, switching analysis

Target: >80% code coverage
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from src.backend.schemas.recommendation_schemas import (
    UserPreferences,
    PlanScores,
    CostBreakdown,
    RankedPlan,
    SwitchingAnalysis
)
from src.backend.schemas.usage_analysis import UsageProjection
from src.backend.services import scoring_service
from src.backend.services.recommendation_engine import (
    calculate_plan_cost,
    _calculate_fixed_cost,
    _calculate_tiered_cost,
    _calculate_time_of_use_cost,
    _calculate_variable_cost,
    analyze_switching_timing
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def default_preferences():
    """Default user preferences from PRD."""
    return UserPreferences(
        cost_priority=40,
        flexibility_priority=30,
        renewable_priority=20,
        rating_priority=10
    )


@pytest.fixture
def balanced_preferences():
    """Balanced preferences (25% each)."""
    return UserPreferences(
        cost_priority=25,
        flexibility_priority=25,
        renewable_priority=25,
        rating_priority=25
    )


@pytest.fixture
def cost_focused_preferences():
    """Cost-focused preferences."""
    return UserPreferences(
        cost_priority=70,
        flexibility_priority=10,
        renewable_priority=10,
        rating_priority=10
    )


@pytest.fixture
def green_focused_preferences():
    """Green energy focused preferences."""
    return UserPreferences(
        cost_priority=10,
        flexibility_priority=10,
        renewable_priority=70,
        rating_priority=10
    )


@pytest.fixture
def sample_usage_projection():
    """Sample usage projection for testing."""
    return UsageProjection(
        projected_monthly_kwh=[850.0, 820.0, 780.0, 900.0, 950.0, 1400.0,
                               1600.0, 1500.0, 1000.0, 850.0, 800.0, 820.0],
        projected_annual_kwh=12270.0,
        confidence_score=0.85
    )


@pytest.fixture
def low_confidence_usage_projection():
    """Low confidence usage projection."""
    return UsageProjection(
        projected_monthly_kwh=[800.0] * 12,
        projected_annual_kwh=9600.0,
        confidence_score=0.5
    )


# ============================================================================
# STORY 2.1: SCORING ALGORITHM TESTS
# ============================================================================

class TestCostScoring:
    """Test cost scoring function."""

    def test_cost_score_minimum(self, sample_usage_projection):
        """Test that low cost gives high score."""
        score = scoring_service.calculate_cost_score(
            projected_annual_cost=Decimal('800.00'),
            projected_usage=sample_usage_projection
        )
        assert score == 100.0

    def test_cost_score_maximum(self, sample_usage_projection):
        """Test that high cost gives low score."""
        score = scoring_service.calculate_cost_score(
            projected_annual_cost=Decimal('3000.00'),
            projected_usage=sample_usage_projection
        )
        assert score == 0.0

    def test_cost_score_midpoint(self, sample_usage_projection):
        """Test midpoint cost gives midpoint score."""
        score = scoring_service.calculate_cost_score(
            projected_annual_cost=Decimal('1900.00'),  # Midpoint of 800-3000
            projected_usage=sample_usage_projection
        )
        assert 45 <= score <= 55  # Should be around 50

    def test_cost_score_relative_scoring(self, sample_usage_projection):
        """Test relative scoring with plan cost list."""
        all_costs = [Decimal('1000.00'), Decimal('1500.00'), Decimal('2000.00')]

        # Lowest cost should get highest score
        score_low = scoring_service.calculate_cost_score(
            projected_annual_cost=Decimal('1000.00'),
            projected_usage=sample_usage_projection,
            all_plan_costs=all_costs
        )

        # Highest cost should get lowest score
        score_high = scoring_service.calculate_cost_score(
            projected_annual_cost=Decimal('2000.00'),
            projected_usage=sample_usage_projection,
            all_plan_costs=all_costs
        )

        assert score_low == 100.0
        assert score_high == 0.0

    def test_cost_score_low_confidence_penalty(self, low_confidence_usage_projection):
        """Test that low confidence applies penalty."""
        score_high_conf = scoring_service.calculate_cost_score(
            projected_annual_cost=Decimal('1500.00'),
            projected_usage=UsageProjection(
                projected_monthly_kwh=[800.0] * 12,
                projected_annual_kwh=9600.0,
                confidence_score=0.95
            )
        )

        score_low_conf = scoring_service.calculate_cost_score(
            projected_annual_cost=Decimal('1500.00'),
            projected_usage=low_confidence_usage_projection
        )

        # Low confidence should have lower score
        assert score_low_conf < score_high_conf

    def test_cost_score_negative_cost(self, sample_usage_projection):
        """Test handling of invalid negative cost."""
        score = scoring_service.calculate_cost_score(
            projected_annual_cost=Decimal('-100.00'),
            projected_usage=sample_usage_projection
        )
        assert score == 0.0

    def test_cost_score_deterministic(self, sample_usage_projection):
        """Test that same inputs produce same output."""
        cost = Decimal('1500.00')
        score1 = scoring_service.calculate_cost_score(cost, sample_usage_projection)
        score2 = scoring_service.calculate_cost_score(cost, sample_usage_projection)
        assert score1 == score2


class TestFlexibilityScoring:
    """Test flexibility scoring function."""

    def test_flexibility_score_month_to_month(self):
        """Test that month-to-month with no ETF gives perfect score."""
        score = scoring_service.calculate_flexibility_score(
            contract_length_months=0,
            early_termination_fee=Decimal('0.00')
        )
        assert score == 100.0

    def test_flexibility_score_long_contract_high_etf(self):
        """Test that long contract with high ETF gives low score."""
        score = scoring_service.calculate_flexibility_score(
            contract_length_months=36,
            early_termination_fee=Decimal('500.00')
        )
        assert score == 0.0

    def test_flexibility_score_12_month_moderate_etf(self):
        """Test 12-month contract with moderate ETF."""
        score = scoring_service.calculate_flexibility_score(
            contract_length_months=12,
            early_termination_fee=Decimal('150.00')
        )
        # Should be somewhere in middle range
        assert 30 <= score <= 70

    def test_flexibility_score_weighted_components(self):
        """Test that contract length weighs more than ETF (60/40)."""
        # Same contract, different ETFs
        score_low_etf = scoring_service.calculate_flexibility_score(
            contract_length_months=12,
            early_termination_fee=Decimal('0.00')
        )

        score_high_etf = scoring_service.calculate_flexibility_score(
            contract_length_months=12,
            early_termination_fee=Decimal('500.00')
        )

        # Difference should be less than if equally weighted (40% of range vs 50%)
        difference = score_low_etf - score_high_etf
        assert difference < 50  # Should be ~40 (40% weight on ETF)

    def test_flexibility_score_negative_inputs(self):
        """Test handling of negative inputs."""
        score = scoring_service.calculate_flexibility_score(
            contract_length_months=-1,
            early_termination_fee=Decimal('-50.00')
        )
        # Should treat as 0
        assert score == 100.0


class TestRenewableScoring:
    """Test renewable energy scoring function."""

    def test_renewable_score_100_percent(self):
        """Test 100% renewable gives perfect score."""
        score = scoring_service.calculate_renewable_score(Decimal('100.00'))
        assert score == 100.0

    def test_renewable_score_0_percent(self):
        """Test 0% renewable gives zero score."""
        score = scoring_service.calculate_renewable_score(Decimal('0.00'))
        assert score == 0.0

    def test_renewable_score_50_percent(self):
        """Test 50% renewable gives 50 score."""
        score = scoring_service.calculate_renewable_score(Decimal('50.00'))
        assert score == 50.0

    def test_renewable_score_direct_mapping(self):
        """Test that renewable percentage maps directly to score."""
        for pct in [10, 25, 33, 67, 75, 90]:
            score = scoring_service.calculate_renewable_score(Decimal(str(pct)))
            assert score == float(pct)

    def test_renewable_score_bounds(self):
        """Test boundary handling."""
        score_over = scoring_service.calculate_renewable_score(Decimal('150.00'))
        assert score_over == 100.0

        score_under = scoring_service.calculate_renewable_score(Decimal('-10.00'))
        assert score_under == 0.0


class TestRatingScoring:
    """Test supplier rating scoring function."""

    def test_rating_score_5_stars(self):
        """Test perfect rating gives perfect score."""
        score = scoring_service.calculate_rating_score(
            supplier_rating=Decimal('5.00'),
            review_count=100
        )
        assert score == 100.0

    def test_rating_score_0_stars(self):
        """Test zero rating gives zero score."""
        score = scoring_service.calculate_rating_score(
            supplier_rating=Decimal('0.00'),
            review_count=100
        )
        assert score == 0.0

    def test_rating_score_none_rating(self):
        """Test missing rating gives neutral score."""
        score = scoring_service.calculate_rating_score(
            supplier_rating=None,
            review_count=0
        )
        assert score == 50.0

    def test_rating_score_confidence_by_reviews(self):
        """Test that review count affects confidence."""
        rating = Decimal('4.0')

        score_many_reviews = scoring_service.calculate_rating_score(
            supplier_rating=rating,
            review_count=1000
        )

        score_few_reviews = scoring_service.calculate_rating_score(
            supplier_rating=rating,
            review_count=5
        )

        # Many reviews should have higher score (more confidence)
        assert score_many_reviews > score_few_reviews

    def test_rating_score_3_stars_50_reviews(self):
        """Test typical 3-star rating with moderate reviews."""
        score = scoring_service.calculate_rating_score(
            supplier_rating=Decimal('3.0'),
            review_count=50
        )
        # 3.0/5.0 = 60% * 95% confidence = 57
        assert 55 <= score <= 60


class TestCompositeScoring:
    """Test composite scoring function."""

    def test_composite_score_perfect_plan(self, default_preferences):
        """Test plan with perfect scores."""
        score = scoring_service.calculate_composite_score(
            cost_score=100.0,
            flexibility_score=100.0,
            renewable_score=100.0,
            rating_score=100.0,
            preferences=default_preferences
        )
        assert score == 100.0

    def test_composite_score_worst_plan(self, default_preferences):
        """Test plan with worst scores."""
        score = scoring_service.calculate_composite_score(
            cost_score=0.0,
            flexibility_score=0.0,
            renewable_score=0.0,
            rating_score=0.0,
            preferences=default_preferences
        )
        assert score == 0.0

    def test_composite_score_weighted_correctly(self, default_preferences):
        """Test weighting: 40% cost, 30% flex, 20% renewable, 10% rating."""
        score = scoring_service.calculate_composite_score(
            cost_score=100.0,
            flexibility_score=0.0,
            renewable_score=0.0,
            rating_score=0.0,
            preferences=default_preferences
        )
        assert score == 40.0  # Only cost contributes (40%)

    def test_composite_score_balanced_preferences(self, balanced_preferences):
        """Test with balanced preferences (25% each)."""
        score = scoring_service.calculate_composite_score(
            cost_score=100.0,
            flexibility_score=50.0,
            renewable_score=0.0,
            rating_score=0.0,
            preferences=balanced_preferences
        )
        # 100*0.25 + 50*0.25 + 0*0.25 + 0*0.25 = 37.5
        assert 37.0 <= score <= 38.0

    def test_composite_score_green_focused(self, green_focused_preferences):
        """Test green-focused preferences heavily weight renewable."""
        score = scoring_service.calculate_composite_score(
            cost_score=50.0,
            flexibility_score=50.0,
            renewable_score=100.0,
            rating_score=50.0,
            preferences=green_focused_preferences
        )
        # 50*0.1 + 50*0.1 + 100*0.7 + 50*0.1 = 85
        assert 84.0 <= score <= 86.0

    def test_composite_score_invalid_score_raises(self, default_preferences):
        """Test that invalid score raises ValueError."""
        with pytest.raises(ValueError, match="must be between 0 and 100"):
            scoring_service.calculate_composite_score(
                cost_score=150.0,  # Invalid
                flexibility_score=50.0,
                renewable_score=50.0,
                rating_score=50.0,
                preferences=default_preferences
            )

    def test_composite_score_invalid_preferences_raises(self):
        """Test that invalid preferences raise ValueError."""
        invalid_prefs = UserPreferences(
            cost_priority=50,
            flexibility_priority=30,
            renewable_priority=10,
            rating_priority=5  # Sum = 95, not 100
        )

        with pytest.raises(ValueError, match="must sum to 100"):
            scoring_service.calculate_composite_score(
                cost_score=50.0,
                flexibility_score=50.0,
                renewable_score=50.0,
                rating_score=50.0,
                preferences=invalid_prefs
            )


# ============================================================================
# STORY 2.2: COST CALCULATION TESTS
# ============================================================================

class TestFixedRateCostCalculation:
    """Test fixed rate cost calculation."""

    def test_fixed_rate_simple(self):
        """Test simple fixed rate calculation."""
        rate_structure = {'type': 'fixed', 'rate_per_kwh': 12.5}
        cost = _calculate_fixed_cost(rate_structure, 10000.0)
        # 12.5 cents/kWh * 10,000 kWh = $1,250
        assert cost == Decimal('1250.00')

    def test_fixed_rate_zero_usage(self):
        """Test fixed rate with zero usage."""
        rate_structure = {'type': 'fixed', 'rate_per_kwh': 12.5}
        cost = _calculate_fixed_cost(rate_structure, 0.0)
        assert cost == Decimal('0.00')

    def test_fixed_rate_fractional_usage(self):
        """Test fixed rate with fractional kWh."""
        rate_structure = {'type': 'fixed', 'rate_per_kwh': 10.0}
        cost = _calculate_fixed_cost(rate_structure, 123.45)
        # 10 cents/kWh * 123.45 kWh = $12.345
        assert abs(cost - Decimal('12.35')) < Decimal('0.01')


class TestTieredRateCostCalculation:
    """Test tiered rate cost calculation."""

    def test_tiered_rate_single_tier(self):
        """Test usage within first tier."""
        rate_structure = {
            'type': 'tiered',
            'tiers': [
                {'max_kwh': 1000, 'rate_per_kwh': 10.0},
                {'max_kwh': float('inf'), 'rate_per_kwh': 15.0}
            ]
        }
        cost = _calculate_tiered_cost(rate_structure, 500.0)
        # 10 cents/kWh * 500 kWh = $50
        assert cost == Decimal('50.00')

    def test_tiered_rate_multiple_tiers(self):
        """Test usage spanning multiple tiers."""
        rate_structure = {
            'type': 'tiered',
            'tiers': [
                {'max_kwh': 1000, 'rate_per_kwh': 8.0},
                {'max_kwh': 2000, 'rate_per_kwh': 10.0},
                {'max_kwh': float('inf'), 'rate_per_kwh': 12.0}
            ]
        }
        cost = _calculate_tiered_cost(rate_structure, 2500.0)
        # Tier 1: 1000 kWh @ 8¢ = $80
        # Tier 2: 1000 kWh @ 10¢ = $100
        # Tier 3: 500 kWh @ 12¢ = $60
        # Total: $240
        assert cost == Decimal('240.00')

    def test_tiered_rate_exact_tier_boundary(self):
        """Test usage exactly at tier boundary."""
        rate_structure = {
            'type': 'tiered',
            'tiers': [
                {'max_kwh': 1000, 'rate_per_kwh': 10.0},
                {'max_kwh': float('inf'), 'rate_per_kwh': 15.0}
            ]
        }
        cost = _calculate_tiered_cost(rate_structure, 1000.0)
        # 10 cents/kWh * 1000 kWh = $100
        assert cost == Decimal('100.00')


class TestTimeOfUseCostCalculation:
    """Test time-of-use rate calculation."""

    def test_time_of_use_50_50_split(self):
        """Test with 50/50 peak/off-peak split."""
        rate_structure = {
            'type': 'time_of_use',
            'peak_rate': 15.0,
            'off_peak_rate': 8.0,
            'peak_pct': 0.5
        }
        monthly_kwh = [1000.0] * 12
        cost = _calculate_time_of_use_cost(rate_structure, monthly_kwh)
        # Each month: 500 @ 15¢ + 500 @ 8¢ = $75 + $40 = $115
        # Annual: $115 * 12 = $1,380
        assert cost == Decimal('1380.00')

    def test_time_of_use_seasonal_pattern(self):
        """Test with seasonal usage pattern."""
        rate_structure = {
            'type': 'time_of_use',
            'peak_rate': 20.0,
            'off_peak_rate': 10.0,
            'peak_pct': 0.6  # 60% during peak
        }
        monthly_kwh = [800.0, 800.0, 800.0, 1000.0, 1200.0, 1500.0,
                       1600.0, 1500.0, 1200.0, 1000.0, 800.0, 800.0]
        cost = _calculate_time_of_use_cost(rate_structure, monthly_kwh)
        # Should calculate correctly with varying monthly usage
        assert cost > Decimal('1500.00')


class TestVariableRateCostCalculation:
    """Test variable rate cost calculation."""

    def test_variable_rate_with_historical_avg(self):
        """Test variable rate using historical average."""
        rate_structure = {
            'type': 'variable',
            'base_rate': 10.0,
            'historical_avg_rate': 12.0
        }
        cost = _calculate_variable_cost(rate_structure, 10000.0, confidence_score=0.9)
        # Should use historical avg (12¢) with small uncertainty buffer
        # 12¢ * 10,000 * ~1.01 uncertainty = ~$1,212
        assert Decimal('1200.00') < cost < Decimal('1250.00')

    def test_variable_rate_low_confidence(self):
        """Test variable rate with low confidence adds larger buffer."""
        rate_structure = {
            'type': 'variable',
            'base_rate': 10.0,
            'historical_avg_rate': 10.0
        }

        cost_high_conf = _calculate_variable_cost(rate_structure, 10000.0, confidence_score=0.95)
        cost_low_conf = _calculate_variable_cost(rate_structure, 10000.0, confidence_score=0.5)

        # Low confidence should add larger buffer
        assert cost_low_conf > cost_high_conf


# ============================================================================
# STORY 2.3: SWITCHING ANALYSIS TESTS
# ============================================================================

class TestSwitchingAnalysis:
    """Test contract timing optimization and switching analysis."""

    def test_switching_no_etf_immediate_switch(self):
        """Test recommendation to switch immediately when no ETF."""
        from src.backend.models.user import CurrentPlan

        current_plan_id = uuid4()
        current_plan = CurrentPlan(
            id=current_plan_id,
            user_id=uuid4(),
            supplier_name="Old Energy",
            current_rate=Decimal('15.0'),
            contract_end_date=date.today() + timedelta(days=200),
            early_termination_fee=Decimal('0.00'),
            monthly_fee=Decimal('10.00')
        )

        # Create a better plan
        recommended_plan = RankedPlan(
            plan_id=uuid4(),
            rank=1,
            plan_name="Better Plan",
            supplier_name="New Energy",
            plan_type="fixed",
            contract_length_months=12,
            early_termination_fee=Decimal('150.00'),
            renewable_percentage=Decimal('100.00'),
            scores=PlanScores(90, 85, 100, 90, 91),
            projected_annual_cost=Decimal('1500.00'),
            projected_monthly_cost=Decimal('125.00'),
            cost_breakdown=CostBreakdown(
                base_cost=Decimal('1380.00'),
                monthly_fees=Decimal('120.00'),
                connection_fee=Decimal('0.00'),
                total_annual_cost=Decimal('1500.00'),
                rate_type='fixed',
                avg_rate_per_kwh=Decimal('11.50')
            ),
            rate_structure={'type': 'fixed', 'rate_per_kwh': 11.5}
        )

        analysis = analyze_switching_timing(current_plan, [recommended_plan])

        assert analysis.should_wait == False
        assert analysis.early_termination_fee == Decimal('0.00')
        assert "No early termination fee" in analysis.switching_recommendation

    def test_switching_high_etf_should_wait(self):
        """Test recommendation to wait when ETF is high relative to savings."""
        from src.backend.models.user import CurrentPlan

        current_plan = CurrentPlan(
            id=uuid4(),
            user_id=uuid4(),
            supplier_name="Old Energy",
            current_rate=Decimal('14.0'),
            contract_end_date=date.today() + timedelta(days=200),
            early_termination_fee=Decimal('500.00'),  # High ETF
            monthly_fee=Decimal('10.00')
        )

        # Only marginally better plan
        recommended_plan = RankedPlan(
            plan_id=uuid4(),
            rank=1,
            plan_name="Slightly Better Plan",
            supplier_name="New Energy",
            plan_type="fixed",
            contract_length_months=12,
            early_termination_fee=Decimal('150.00'),
            renewable_percentage=Decimal('50.00'),
            scores=PlanScores(55, 70, 50, 80, 60),
            projected_annual_cost=Decimal('1650.00'),
            projected_monthly_cost=Decimal('137.50'),
            cost_breakdown=CostBreakdown(
                base_cost=Decimal('1530.00'),
                monthly_fees=Decimal('120.00'),
                connection_fee=Decimal('0.00'),
                total_annual_cost=Decimal('1650.00'),
                rate_type='fixed',
                avg_rate_per_kwh=Decimal('12.75')
            ),
            rate_structure={'type': 'fixed', 'rate_per_kwh': 12.75}
        )

        analysis = analyze_switching_timing(current_plan, [recommended_plan])

        # Should recommend waiting due to high ETF
        assert analysis.should_wait == True
        assert analysis.early_termination_fee == Decimal('500.00')

    def test_switching_near_contract_end(self):
        """Test recommendation to wait when close to contract end."""
        from src.backend.models.user import CurrentPlan

        current_plan = CurrentPlan(
            id=uuid4(),
            user_id=uuid4(),
            supplier_name="Old Energy",
            current_rate=Decimal('15.0'),
            contract_end_date=date.today() + timedelta(days=20),  # 20 days left
            early_termination_fee=Decimal('150.00'),
            monthly_fee=Decimal('10.00')
        )

        recommended_plan = RankedPlan(
            plan_id=uuid4(),
            rank=1,
            plan_name="Better Plan",
            supplier_name="New Energy",
            plan_type="fixed",
            contract_length_months=12,
            early_termination_fee=Decimal('150.00'),
            renewable_percentage=Decimal('100.00'),
            scores=PlanScores(95, 85, 100, 90, 92),
            projected_annual_cost=Decimal('1400.00'),
            projected_monthly_cost=Decimal('116.67'),
            cost_breakdown=CostBreakdown(
                base_cost=Decimal('1280.00'),
                monthly_fees=Decimal('120.00'),
                connection_fee=Decimal('0.00'),
                total_annual_cost=Decimal('1400.00'),
                rate_type='fixed',
                avg_rate_per_kwh=Decimal('10.67')
            ),
            rate_structure={'type': 'fixed', 'rate_per_kwh': 10.67}
        )

        analysis = analyze_switching_timing(current_plan, [recommended_plan])

        # Should wait since contract ends in 20 days
        assert analysis.should_wait == True
        assert analysis.days_until_contract_end == 20

    def test_switching_substantial_savings(self):
        """Test recommendation to switch when savings are substantial."""
        from src.backend.models.user import CurrentPlan

        current_plan = CurrentPlan(
            id=uuid4(),
            user_id=uuid4(),
            supplier_name="Expensive Energy",
            current_rate=Decimal('20.0'),  # Very expensive
            contract_end_date=date.today() + timedelta(days=300),
            early_termination_fee=Decimal('200.00'),
            monthly_fee=Decimal('15.00')
        )

        # Much cheaper plan
        recommended_plan = RankedPlan(
            plan_id=uuid4(),
            rank=1,
            plan_name="Cheap Plan",
            supplier_name="Budget Energy",
            plan_type="fixed",
            contract_length_months=12,
            early_termination_fee=Decimal('150.00'),
            renewable_percentage=Decimal('50.00'),
            scores=PlanScores(100, 80, 50, 80, 85),
            projected_annual_cost=Decimal('1200.00'),  # Much cheaper
            projected_monthly_cost=Decimal('100.00'),
            cost_breakdown=CostBreakdown(
                base_cost=Decimal('1080.00'),
                monthly_fees=Decimal('120.00'),
                connection_fee=Decimal('0.00'),
                total_annual_cost=Decimal('1200.00'),
                rate_type='fixed',
                avg_rate_per_kwh=Decimal('9.00')
            ),
            rate_structure={'type': 'fixed', 'rate_per_kwh': 9.0}
        )

        analysis = analyze_switching_timing(current_plan, [recommended_plan])

        # Should recommend switching due to substantial savings
        # Current: 20¢ * 12k kWh = $2,400 + $180 fees = $2,580
        # New: $1,200
        # Savings: ~$1,380/year (more than 2x ETF of $200)
        assert analysis.monthly_savings > Decimal('100.00')

    def test_switching_no_savings(self):
        """Test recommendation to stay when new plan costs more."""
        from src.backend.models.user import CurrentPlan

        current_plan = CurrentPlan(
            id=uuid4(),
            user_id=uuid4(),
            supplier_name="Good Energy",
            current_rate=Decimal('10.0'),  # Already cheap
            contract_end_date=date.today() + timedelta(days=200),
            early_termination_fee=Decimal('200.00'),
            monthly_fee=Decimal('5.00')
        )

        # More expensive plan
        recommended_plan = RankedPlan(
            plan_id=uuid4(),
            rank=1,
            plan_name="Expensive Plan",
            supplier_name="Premium Energy",
            plan_type="fixed",
            contract_length_months=12,
            early_termination_fee=Decimal('150.00'),
            renewable_percentage=Decimal('100.00'),  # 100% renewable but expensive
            scores=PlanScores(40, 80, 100, 90, 65),
            projected_annual_cost=Decimal('2000.00'),
            projected_monthly_cost=Decimal('166.67'),
            cost_breakdown=CostBreakdown(
                base_cost=Decimal('1880.00'),
                monthly_fees=Decimal('120.00'),
                connection_fee=Decimal('0.00'),
                total_annual_cost=Decimal('2000.00'),
                rate_type='fixed',
                avg_rate_per_kwh=Decimal('15.67')
            ),
            rate_structure={'type': 'fixed', 'rate_per_kwh': 15.67}
        )

        analysis = analyze_switching_timing(current_plan, [recommended_plan])

        # Should stay with current plan
        assert analysis.should_wait == True
        assert analysis.monthly_savings < Decimal('0.00')  # Negative savings

    def test_switching_break_even_calculation(self):
        """Test break-even period calculation."""
        from src.backend.models.user import CurrentPlan

        current_plan = CurrentPlan(
            id=uuid4(),
            user_id=uuid4(),
            supplier_name="Old Energy",
            current_rate=Decimal('15.0'),
            contract_end_date=date.today() + timedelta(days=365),
            early_termination_fee=Decimal('300.00'),
            monthly_fee=Decimal('10.00')
        )

        # Plan that saves $30/month
        recommended_plan = RankedPlan(
            plan_id=uuid4(),
            rank=1,
            plan_name="Savings Plan",
            supplier_name="Better Energy",
            plan_type="fixed",
            contract_length_months=12,
            early_termination_fee=Decimal('150.00'),
            renewable_percentage=Decimal('75.00'),
            scores=PlanScores(80, 80, 75, 85, 80),
            projected_annual_cost=Decimal('1440.00'),  # $120/month
            projected_monthly_cost=Decimal('120.00'),
            cost_breakdown=CostBreakdown(
                base_cost=Decimal('1320.00'),
                monthly_fees=Decimal('120.00'),
                connection_fee=Decimal('0.00'),
                total_annual_cost=Decimal('1440.00'),
                rate_type='fixed',
                avg_rate_per_kwh=Decimal('11.00')
            ),
            rate_structure={'type': 'fixed', 'rate_per_kwh': 11.0}
        )

        analysis = analyze_switching_timing(current_plan, [recommended_plan])

        # Break-even: $300 ETF / $30 savings per month = 10 months
        # (simplified calculation, actual may vary)
        assert analysis.break_even_months is not None
        assert analysis.break_even_months < 18  # Within acceptable range


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestEndToEndScoring:
    """Integration tests for complete scoring workflow."""

    def test_score_plan_complete(self, default_preferences, sample_usage_projection):
        """Test complete plan scoring with all factors."""
        plan_dict = {
            'contract_length_months': 12,
            'early_termination_fee': Decimal('150.00'),
            'renewable_percentage': Decimal('80.00')
        }

        supplier_dict = {
            'average_rating': Decimal('4.2'),
            'review_count': 500
        }

        scores = scoring_service.score_plan(
            plan=plan_dict,
            supplier=supplier_dict,
            projected_annual_cost=Decimal('1500.00'),
            projected_usage=sample_usage_projection,
            preferences=default_preferences
        )

        # Verify all scores are in valid range
        assert 0 <= scores.cost_score <= 100
        assert 0 <= scores.flexibility_score <= 100
        assert 0 <= scores.renewable_score <= 100
        assert 0 <= scores.rating_score <= 100
        assert 0 <= scores.composite_score <= 100

        # Renewable score should be 80 (direct mapping)
        assert scores.renewable_score == 80.0

    def test_score_multiple_plans_ranking(self, default_preferences, sample_usage_projection):
        """Test scoring multiple plans and verifying ranking."""
        # Cheap plan (best cost score)
        plan1 = {
            'contract_length_months': 24,
            'early_termination_fee': Decimal('250.00'),
            'renewable_percentage': Decimal('10.00')
        }

        # Green plan (best renewable score)
        plan2 = {
            'contract_length_months': 12,
            'early_termination_fee': Decimal('150.00'),
            'renewable_percentage': Decimal('100.00')
        }

        # Flexible plan (best flexibility score)
        plan3 = {
            'contract_length_months': 0,
            'early_termination_fee': Decimal('0.00'),
            'renewable_percentage': Decimal('50.00')
        }

        supplier = {
            'average_rating': Decimal('4.0'),
            'review_count': 100
        }

        all_costs = [Decimal('1200.00'), Decimal('1600.00'), Decimal('1450.00')]

        scores1 = scoring_service.score_plan(plan1, supplier, all_costs[0], sample_usage_projection, default_preferences, all_costs)
        scores2 = scoring_service.score_plan(plan2, supplier, all_costs[1], sample_usage_projection, default_preferences, all_costs)
        scores3 = scoring_service.score_plan(plan3, supplier, all_costs[2], sample_usage_projection, default_preferences, all_costs)

        # With default preferences (40% cost), cheapest should rank highest
        # Unless other factors compensate significantly
        # This test verifies scoring is working, not predicting exact ranking
        assert scores1.cost_score > scores2.cost_score  # Plan1 is cheapest
        assert scores2.renewable_score > scores1.renewable_score  # Plan2 is greenest
        assert scores3.flexibility_score > scores1.flexibility_score  # Plan3 is most flexible


# ============================================================================
# PROPERTY-BASED TESTS (Determinism & Invariants)
# ============================================================================

class TestDeterminismAndInvariants:
    """Test deterministic behavior and mathematical invariants."""

    def test_scoring_deterministic(self, default_preferences, sample_usage_projection):
        """Test that scoring is deterministic (same inputs -> same outputs)."""
        plan = {'contract_length_months': 12, 'early_termination_fee': Decimal('150.00'), 'renewable_percentage': Decimal('75.00')}
        supplier = {'average_rating': Decimal('4.0'), 'review_count': 100}
        cost = Decimal('1500.00')

        # Score the same plan multiple times
        results = []
        for _ in range(10):
            scores = scoring_service.score_plan(plan, supplier, cost, sample_usage_projection, default_preferences)
            results.append(scores.composite_score)

        # All results should be identical
        assert len(set(results)) == 1

    def test_composite_score_bounded(self, default_preferences):
        """Test that composite score is always 0-100."""
        import random

        for _ in range(100):
            cost_score = random.uniform(0, 100)
            flex_score = random.uniform(0, 100)
            renewable_score = random.uniform(0, 100)
            rating_score = random.uniform(0, 100)

            composite = scoring_service.calculate_composite_score(
                cost_score, flex_score, renewable_score, rating_score, default_preferences
            )

            assert 0 <= composite <= 100

    def test_cost_score_monotonic(self, sample_usage_projection):
        """Test that cost score decreases as cost increases (monotonic)."""
        costs = [Decimal(str(c)) for c in [1000, 1500, 2000, 2500, 3000]]
        scores = [scoring_service.calculate_cost_score(c, sample_usage_projection) for c in costs]

        # Scores should be non-increasing
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
