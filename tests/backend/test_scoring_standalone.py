"""
Standalone Unit Tests for Scoring Service (Story 2.1)
Tests scoring functions without database dependencies.

Target: >80% code coverage for scoring_service.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Direct imports to avoid email_validator dependency issue
from backend.schemas.recommendation_schemas import UserPreferences, PlanScores
from backend.schemas.usage_analysis import UsageProjection
from backend.services.scoring_service import (
    calculate_cost_score,
    calculate_flexibility_score,
    calculate_renewable_score,
    calculate_rating_score,
    calculate_composite_score,
    score_plan
)

# For convenience
class scoring_service:
    calculate_cost_score = staticmethod(calculate_cost_score)
    calculate_flexibility_score = staticmethod(calculate_flexibility_score)
    calculate_renewable_score = staticmethod(calculate_renewable_score)
    calculate_rating_score = staticmethod(calculate_rating_score)
    calculate_composite_score = staticmethod(calculate_composite_score)
    score_plan = staticmethod(score_plan)


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
def sample_usage_projection():
    """Sample usage projection for testing."""
    return UsageProjection(
        projected_monthly_kwh=[850.0, 820.0, 780.0, 900.0, 950.0, 1400.0,
                               1600.0, 1500.0, 1000.0, 850.0, 800.0, 820.0],
        projected_annual_kwh=12270.0,
        confidence_score=0.85
    )


# ============================================================================
# COST SCORING TESTS
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
        assert 45 <= score <= 55

    def test_cost_score_relative_scoring(self, sample_usage_projection):
        """Test relative scoring with plan cost list."""
        all_costs = [Decimal('1000.00'), Decimal('1500.00'), Decimal('2000.00')]

        score_low = scoring_service.calculate_cost_score(
            projected_annual_cost=Decimal('1000.00'),
            projected_usage=sample_usage_projection,
            all_plan_costs=all_costs
        )

        score_high = scoring_service.calculate_cost_score(
            projected_annual_cost=Decimal('2000.00'),
            projected_usage=sample_usage_projection,
            all_plan_costs=all_costs
        )

        assert score_low == 100.0
        assert score_high == 0.0

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
        assert 30 <= score <= 70


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

        assert score_many_reviews > score_few_reviews


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
        assert score == 40.0

    def test_composite_score_invalid_score_raises(self, default_preferences):
        """Test that invalid score raises ValueError."""
        with pytest.raises(ValueError, match="must be between 0 and 100"):
            scoring_service.calculate_composite_score(
                cost_score=150.0,
                flexibility_score=50.0,
                renewable_score=50.0,
                rating_score=50.0,
                preferences=default_preferences
            )


class TestScorePlanIntegration:
    """Integration tests for score_plan function."""

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


class TestScoringDeterminism:
    """Test deterministic behavior."""

    def test_scoring_deterministic(self, default_preferences, sample_usage_projection):
        """Test that scoring is deterministic (same inputs -> same outputs)."""
        plan = {
            'contract_length_months': 12,
            'early_termination_fee': Decimal('150.00'),
            'renewable_percentage': Decimal('75.00')
        }
        supplier = {'average_rating': Decimal('4.0'), 'review_count': 100}
        cost = Decimal('1500.00')

        # Score the same plan multiple times
        results = []
        for _ in range(10):
            scores = scoring_service.score_plan(
                plan, supplier, cost, sample_usage_projection, default_preferences
            )
            results.append(scores.composite_score)

        # All results should be identical
        assert len(set(results)) == 1

    def test_cost_score_monotonic(self, sample_usage_projection):
        """Test that cost score decreases as cost increases (monotonic)."""
        costs = [Decimal(str(c)) for c in [1000, 1500, 2000, 2500, 3000]]
        scores = [
            scoring_service.calculate_cost_score(c, sample_usage_projection)
            for c in costs
        ]

        # Scores should be non-increasing
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--cov=src/backend/services/scoring_service", "--cov-report=term-missing"])
