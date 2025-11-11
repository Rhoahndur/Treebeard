"""
Recommendation Engine Schemas
Story 2.1-2.3 - Epic 2: Recommendation Core

This module defines the data models for the recommendation engine,
including scoring, ranking, and switching optimization.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID


# ============================================================================
# SCORING SCHEMAS (Story 2.1)
# ============================================================================

@dataclass
class PlanScores:
    """
    Individual factor scores and composite score for a plan.
    All scores are 0-100, where higher is better.
    """
    cost_score: float  # 0-100: Lower cost = higher score
    flexibility_score: float  # 0-100: Shorter contract + lower ETF = higher score
    renewable_score: float  # 0-100: Higher renewable % = higher score
    rating_score: float  # 0-100: Better supplier rating = higher score
    composite_score: float  # Weighted average of above factors

    def __post_init__(self):
        """Validate scores are in valid range."""
        for score_name in ['cost_score', 'flexibility_score', 'renewable_score', 'rating_score', 'composite_score']:
            score = getattr(self, score_name)
            if not 0 <= score <= 100:
                raise ValueError(f"{score_name} must be between 0 and 100, got {score}")


@dataclass
class UserPreferences:
    """
    User's preference weights for recommendation scoring.
    All priorities must sum to 100.
    """
    cost_priority: int = 40  # Default: 40%
    flexibility_priority: int = 30  # Default: 30%
    renewable_priority: int = 20  # Default: 20%
    rating_priority: int = 10  # Default: 10%

    def __post_init__(self):
        """Validate priorities sum to 100."""
        total = self.cost_priority + self.flexibility_priority + self.renewable_priority + self.rating_priority
        if total != 100:
            raise ValueError(f"Priorities must sum to 100, got {total}")


# ============================================================================
# COST CALCULATION SCHEMAS (Story 2.2)
# ============================================================================

class RateType(str, Enum):
    """Energy plan rate structure types."""
    FIXED = "fixed"
    TIERED = "tiered"
    TIME_OF_USE = "time_of_use"
    VARIABLE = "variable"


@dataclass
class CostBreakdown:
    """
    Detailed cost breakdown for a plan.
    """
    base_cost: Decimal  # Cost based on usage and rate
    monthly_fees: Decimal  # Total annual monthly fees (monthly_fee * 12)
    connection_fee: Decimal  # One-time connection fee
    total_annual_cost: Decimal  # Sum of all costs
    rate_type: str  # Type of rate structure
    avg_rate_per_kwh: Decimal  # Effective average rate


@dataclass
class TierRate:
    """Rate tier for tiered rate structures."""
    max_kwh: float  # Maximum kWh for this tier (inclusive)
    rate_per_kwh: Decimal  # Rate in cents per kWh


@dataclass
class TimeOfUseRate:
    """Time-of-use rate structure."""
    peak_rate: Decimal  # Rate during peak hours (cents per kWh)
    off_peak_rate: Decimal  # Rate during off-peak hours (cents per kWh)
    peak_hours: List[int]  # Hours considered peak (0-23)
    peak_pct: float = 0.5  # Percentage of usage during peak (default 50%)


# ============================================================================
# RANKING & RECOMMENDATION SCHEMAS (Story 2.2)
# ============================================================================

@dataclass
class RankedPlan:
    """
    A plan with its ranking and scoring details.
    This is the core output of the recommendation engine.
    """
    plan_id: UUID
    rank: int  # 1, 2, or 3

    # Plan details
    plan_name: str
    supplier_name: str
    plan_type: str
    contract_length_months: int
    early_termination_fee: Decimal
    renewable_percentage: Decimal

    # Scores
    scores: PlanScores

    # Cost analysis
    projected_annual_cost: Decimal
    projected_monthly_cost: Decimal
    cost_breakdown: CostBreakdown

    # Additional details
    rate_structure: Dict[str, Any]  # Original rate structure from DB
    monthly_fee: Optional[Decimal] = None
    connection_fee: Optional[Decimal] = None


@dataclass
class RecommendationResult:
    """
    Complete recommendation result for a user.
    This is the main output contract for Story 2.2.
    """
    user_id: UUID
    top_plans: List[RankedPlan]  # Top 3 plans (or fewer if <3 available)

    # Metadata
    generated_at: datetime
    usage_profile_summary: Dict[str, Any]  # Summary from Story 1.4 UsageProfile

    # Total plans analyzed
    total_plans_analyzed: int
    total_plans_eligible: int


# ============================================================================
# CONTRACT TIMING OPTIMIZATION SCHEMAS (Story 2.3)
# ============================================================================

@dataclass
class SwitchingAnalysis:
    """
    Analysis of switching costs and timing.
    Story 2.3 enhancement to RecommendationResult.
    """
    current_contract_end_date: date
    days_until_contract_end: int
    early_termination_fee: Decimal

    # Break-even analysis
    monthly_savings: Decimal  # Per-month savings vs current plan
    break_even_months: Optional[int]  # Months to recoup ETF (None if negative savings)

    # Recommendation
    should_wait: bool  # True if staying with current plan is better
    optimal_switch_date: date  # Best date to switch
    switching_recommendation: str  # Plain-language recommendation


@dataclass
class EnhancedRecommendationResult(RecommendationResult):
    """
    Enhanced recommendation result with switching analysis (Story 2.3).
    Extends the base RecommendationResult from Story 2.2.
    """
    switching_analysis: Optional[SwitchingAnalysis] = None
    stay_with_current: bool = False  # True if current plan is better than all recommendations
    stay_reason: Optional[str] = None  # Explanation why staying is recommended


# ============================================================================
# FILTERING SCHEMAS (Story 2.2)
# ============================================================================

@dataclass
class PlanFilter:
    """
    Criteria for filtering eligible plans.
    """
    zip_code: str  # Required: user's location
    is_active: bool = True  # Only active plans
    max_contract_length: Optional[int] = None  # Max contract length in months
    min_renewable_percentage: Optional[Decimal] = None  # Minimum renewable %
    plan_types: Optional[List[str]] = None  # Filter by plan types


# ============================================================================
# USAGE PROJECTION (from Story 1.4)
# ============================================================================

@dataclass
class UsageProjection:
    """
    12-month forward usage projection.
    Re-exported from Story 1.4 for convenience.
    """
    projected_monthly_kwh: List[float]  # 12 months
    projected_annual_kwh: float
    confidence_score: float  # 0.0 to 1.0


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_user_preferences(preferences: UserPreferences) -> bool:
    """
    Validate user preferences sum to 100 and are non-negative.

    Args:
        preferences: User preference weights

    Returns:
        True if valid

    Raises:
        ValueError: If preferences are invalid
    """
    total = (
        preferences.cost_priority +
        preferences.flexibility_priority +
        preferences.renewable_priority +
        preferences.rating_priority
    )

    if total != 100:
        raise ValueError(f"Preference weights must sum to 100, got {total}")

    for attr in ['cost_priority', 'flexibility_priority', 'renewable_priority', 'rating_priority']:
        value = getattr(preferences, attr)
        if value < 0 or value > 100:
            raise ValueError(f"{attr} must be between 0 and 100, got {value}")

    return True


def create_default_preferences() -> UserPreferences:
    """
    Create default user preferences based on PRD specifications.

    Returns:
        Default UserPreferences (cost=40, flexibility=30, renewable=20, rating=10)
    """
    return UserPreferences(
        cost_priority=40,
        flexibility_priority=30,
        renewable_priority=20,
        rating_priority=10
    )
