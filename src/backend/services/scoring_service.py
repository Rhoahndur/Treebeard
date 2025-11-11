"""
Scoring Service - Story 2.1
Multi-factor scoring system for ranking energy plans.

This service implements the four scoring factors:
1. Cost Score: Lower projected annual cost = higher score
2. Flexibility Score: Shorter contract + lower ETF = higher score
3. Renewable Score: Higher renewable % = higher score
4. Rating Score: Better supplier rating = higher score

All scores are normalized to 0-100 range, where higher is better.
"""

from decimal import Decimal
from typing import Dict, Any, Optional
import math

from ..schemas.recommendation_schemas import PlanScores, UserPreferences
from ..schemas.usage_analysis import UsageProjection


# ============================================================================
# SCORING CONSTANTS
# ============================================================================

# Cost scoring thresholds (in dollars per year)
COST_MIN_THRESHOLD = 800.0  # Below this = score 100
COST_MAX_THRESHOLD = 3000.0  # Above this = score 0

# Flexibility scoring weights
CONTRACT_LENGTH_WEIGHT = 0.6  # 60% weight for contract length
ETF_WEIGHT = 0.4  # 40% weight for early termination fee

# Contract length thresholds (in months)
CONTRACT_MIN_MONTHS = 0  # Month-to-month (best flexibility) = 100
CONTRACT_MAX_MONTHS = 36  # 3-year contract (worst flexibility) = 0

# ETF thresholds (in dollars)
ETF_MIN = 0.0  # No ETF (best) = 100
ETF_MAX = 500.0  # High ETF (worst) = 0

# Renewable percentage is already 0-100, so no transformation needed

# Rating thresholds
RATING_MIN = 0.0  # Worst rating = 0
RATING_MAX = 5.0  # Best rating = 100


# ============================================================================
# COST SCORING (Story 2.1)
# ============================================================================

def calculate_cost_score(
    projected_annual_cost: Decimal,
    projected_usage: UsageProjection,
    all_plan_costs: Optional[list[Decimal]] = None
) -> float:
    """
    Calculate cost score for a plan (0-100, higher is better).

    Scoring approach:
    - Uses inverse linear scaling: lower cost = higher score
    - If all_plan_costs provided, uses min/max from that set for normalization
    - Otherwise, uses predefined thresholds

    Args:
        projected_annual_cost: Total annual cost for this plan (including all fees)
        projected_usage: Usage projection from Story 1.4 (for confidence weighting)
        all_plan_costs: Optional list of all plan costs for relative scoring

    Returns:
        Score from 0 to 100 (higher = lower cost = better)

    Deterministic: Same inputs always produce same output.
    """
    cost = float(projected_annual_cost)

    # Handle edge cases
    if cost < 0:
        return 0.0  # Invalid cost

    # Determine min/max for normalization
    if all_plan_costs and len(all_plan_costs) > 1:
        # Use relative scoring based on actual plan costs
        min_cost = float(min(all_plan_costs))
        max_cost = float(max(all_plan_costs))

        # Add small buffer to avoid division by zero
        if max_cost == min_cost:
            return 100.0  # All plans cost the same
    else:
        # Use predefined thresholds
        min_cost = COST_MIN_THRESHOLD
        max_cost = COST_MAX_THRESHOLD

    # Linear inverse scaling: lower cost = higher score
    if cost <= min_cost:
        score = 100.0
    elif cost >= max_cost:
        score = 0.0
    else:
        # Inverse linear interpolation
        score = 100.0 * (1 - (cost - min_cost) / (max_cost - min_cost))

    # Apply confidence factor from usage projection
    # Lower confidence = slight penalty to account for uncertainty
    confidence_factor = projected_usage.confidence_score
    if confidence_factor < 0.8:
        # Apply up to 5% penalty for low confidence
        penalty = (0.8 - confidence_factor) * 0.05
        score = score * (1 - penalty)

    return max(0.0, min(100.0, score))


# ============================================================================
# FLEXIBILITY SCORING (Story 2.1)
# ============================================================================

def calculate_flexibility_score(
    contract_length_months: int,
    early_termination_fee: Decimal
) -> float:
    """
    Calculate flexibility score for a plan (0-100, higher is better).

    Scoring approach:
    - Combines contract length and ETF with weighted average
    - Shorter contract = higher score (more flexibility)
    - Lower ETF = higher score (easier to exit)

    Args:
        contract_length_months: Contract length in months (0 = month-to-month)
        early_termination_fee: Early termination fee in dollars

    Returns:
        Score from 0 to 100 (higher = more flexible)

    Deterministic: Same inputs always produce same output.
    """
    # Handle edge cases
    if contract_length_months < 0:
        contract_length_months = 0

    etf = float(early_termination_fee)
    if etf < 0:
        etf = 0

    # Score contract length (inverse linear scaling)
    if contract_length_months <= CONTRACT_MIN_MONTHS:
        contract_score = 100.0
    elif contract_length_months >= CONTRACT_MAX_MONTHS:
        contract_score = 0.0
    else:
        # Linear interpolation
        range_size = CONTRACT_MAX_MONTHS - CONTRACT_MIN_MONTHS
        contract_score = 100.0 * (1 - (contract_length_months - CONTRACT_MIN_MONTHS) / range_size)

    # Score ETF (inverse linear scaling)
    if etf <= ETF_MIN:
        etf_score = 100.0
    elif etf >= ETF_MAX:
        etf_score = 0.0
    else:
        # Linear interpolation
        etf_score = 100.0 * (1 - (etf - ETF_MIN) / (ETF_MAX - ETF_MIN))

    # Weighted combination
    flexibility_score = (
        CONTRACT_LENGTH_WEIGHT * contract_score +
        ETF_WEIGHT * etf_score
    )

    return max(0.0, min(100.0, flexibility_score))


# ============================================================================
# RENEWABLE SCORING (Story 2.1)
# ============================================================================

def calculate_renewable_score(renewable_percentage: Decimal) -> float:
    """
    Calculate renewable energy score for a plan (0-100, higher is better).

    Scoring approach:
    - Direct mapping: renewable_percentage is already 0-100
    - Higher percentage = higher score

    Args:
        renewable_percentage: Percentage of renewable energy (0.00-100.00)

    Returns:
        Score from 0 to 100 (higher = more renewable)

    Deterministic: Same inputs always produce same output.
    """
    score = float(renewable_percentage)

    # Handle edge cases
    if score < 0:
        score = 0.0
    elif score > 100:
        score = 100.0

    # Renewable percentage is already in the right scale
    return score


# ============================================================================
# RATING SCORING (Story 2.1)
# ============================================================================

def calculate_rating_score(
    supplier_rating: Optional[Decimal],
    review_count: int = 0
) -> float:
    """
    Calculate supplier rating score (0-100, higher is better).

    Scoring approach:
    - Converts 0-5 star rating to 0-100 scale
    - Applies confidence factor based on number of reviews
    - Fewer reviews = lower confidence = slight penalty

    Args:
        supplier_rating: Supplier rating (0.00-5.00), None if no rating
        review_count: Number of reviews (for confidence weighting)

    Returns:
        Score from 0 to 100 (higher = better rating)

    Deterministic: Same inputs always produce same output.
    """
    # Handle missing rating
    if supplier_rating is None:
        # No rating available - use neutral score with penalty
        return 50.0

    rating = float(supplier_rating)

    # Handle edge cases
    if rating < RATING_MIN:
        rating = RATING_MIN
    elif rating > RATING_MAX:
        rating = RATING_MAX

    # Convert 0-5 scale to 0-100 scale
    base_score = (rating / RATING_MAX) * 100.0

    # Apply confidence factor based on review count
    # More reviews = more confidence = less penalty
    if review_count < 10:
        # Very few reviews - apply penalty
        confidence_factor = 0.85
    elif review_count < 50:
        # Some reviews - small penalty
        confidence_factor = 0.95
    else:
        # Many reviews - full confidence
        confidence_factor = 1.0

    score = base_score * confidence_factor

    return max(0.0, min(100.0, score))


# ============================================================================
# COMPOSITE SCORING (Story 2.1)
# ============================================================================

def calculate_composite_score(
    cost_score: float,
    flexibility_score: float,
    renewable_score: float,
    rating_score: float,
    preferences: UserPreferences
) -> float:
    """
    Calculate composite score using user preference weights.

    Formula from PRD:
    composite_score = (
        cost_score * cost_priority +
        flexibility_score * flexibility_priority +
        renewable_score * renewable_priority +
        rating_score * rating_priority
    ) / 100

    The division by 100 normalizes since priorities sum to 100.

    Args:
        cost_score: Cost score (0-100)
        flexibility_score: Flexibility score (0-100)
        renewable_score: Renewable score (0-100)
        rating_score: Rating score (0-100)
        preferences: User preference weights (must sum to 100)

    Returns:
        Composite score from 0 to 100

    Raises:
        ValueError: If any score is out of range or preferences invalid

    Deterministic: Same inputs always produce same output.
    """
    # Validate input scores
    for score_name, score_value in [
        ('cost_score', cost_score),
        ('flexibility_score', flexibility_score),
        ('renewable_score', renewable_score),
        ('rating_score', rating_score)
    ]:
        if not 0 <= score_value <= 100:
            raise ValueError(f"{score_name} must be between 0 and 100, got {score_value}")

    # Validate preferences sum to 100
    total_priority = (
        preferences.cost_priority +
        preferences.flexibility_priority +
        preferences.renewable_priority +
        preferences.rating_priority
    )
    if total_priority != 100:
        raise ValueError(f"Preference weights must sum to 100, got {total_priority}")

    # Calculate weighted composite score
    composite = (
        cost_score * preferences.cost_priority +
        flexibility_score * preferences.flexibility_priority +
        renewable_score * preferences.renewable_priority +
        rating_score * preferences.rating_priority
    ) / 100.0

    return max(0.0, min(100.0, composite))


# ============================================================================
# COMPLETE SCORING FUNCTION (Story 2.1)
# ============================================================================

def score_plan(
    plan: Dict[str, Any],
    supplier: Dict[str, Any],
    projected_annual_cost: Decimal,
    projected_usage: UsageProjection,
    preferences: UserPreferences,
    all_plan_costs: Optional[list[Decimal]] = None
) -> PlanScores:
    """
    Calculate all scores for a plan.

    This is the main scoring function that combines all four factors.

    Args:
        plan: Plan details (from database)
        supplier: Supplier details (from database)
        projected_annual_cost: Total annual cost for this plan
        projected_usage: Usage projection from Story 1.4
        preferences: User preference weights
        all_plan_costs: Optional list of all plan costs for relative scoring

    Returns:
        PlanScores object with all individual and composite scores

    Deterministic: Same inputs always produce same output.
    """
    # Calculate individual scores
    cost_score = calculate_cost_score(
        projected_annual_cost=projected_annual_cost,
        projected_usage=projected_usage,
        all_plan_costs=all_plan_costs
    )

    flexibility_score = calculate_flexibility_score(
        contract_length_months=plan['contract_length_months'],
        early_termination_fee=plan['early_termination_fee']
    )

    renewable_score = calculate_renewable_score(
        renewable_percentage=plan['renewable_percentage']
    )

    rating_score = calculate_rating_score(
        supplier_rating=supplier.get('average_rating'),
        review_count=supplier.get('review_count', 0)
    )

    # Calculate composite score
    composite = calculate_composite_score(
        cost_score=cost_score,
        flexibility_score=flexibility_score,
        renewable_score=renewable_score,
        rating_score=rating_score,
        preferences=preferences
    )

    return PlanScores(
        cost_score=cost_score,
        flexibility_score=flexibility_score,
        renewable_score=renewable_score,
        rating_score=rating_score,
        composite_score=composite
    )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def normalize_scores(scores: list[float], target_min: float = 0.0, target_max: float = 100.0) -> list[float]:
    """
    Normalize a list of scores to a target range.

    Useful for re-normalizing scores when comparing a subset of plans.

    Args:
        scores: List of scores to normalize
        target_min: Target minimum value
        target_max: Target maximum value

    Returns:
        Normalized scores
    """
    if not scores:
        return []

    current_min = min(scores)
    current_max = max(scores)

    # If all scores are the same, return them as-is
    if current_max == current_min:
        return scores

    # Linear scaling
    normalized = []
    for score in scores:
        normalized_score = target_min + (score - current_min) * (target_max - target_min) / (current_max - current_min)
        normalized.append(normalized_score)

    return normalized
