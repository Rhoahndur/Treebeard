"""
Recommendation Engine Service - Stories 2.1, 2.2, 2.3
Core recommendation engine that matches and ranks energy plans.

This service implements:
- Story 2.1: Multi-factor scoring algorithm
- Story 2.2: Plan matching, filtering, and ranking
- Story 2.3: Contract timing optimization and switching analysis
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
import logging

from sqlalchemy.orm import Session
from sqlalchemy import and_, any_

from models.plan import PlanCatalog, Supplier
from models.user import User, UserPreference, CurrentPlan
from schemas.recommendation_schemas import (
    RankedPlan,
    RecommendationResult,
    EnhancedRecommendationResult,
    PlanScores,
    UserPreferences,
    CostBreakdown,
    RateType,
    TierRate,
    TimeOfUseRate,
    SwitchingAnalysis,
    PlanFilter
)
from schemas.usage_analysis import UsageProjection
from services.scoring_service import score_plan

logger = logging.getLogger(__name__)


# ============================================================================
# COST CALCULATION (Story 2.2)
# ============================================================================

def calculate_plan_cost(
    plan: PlanCatalog,
    projected_usage: UsageProjection,
    include_connection_fee: bool = True
) -> CostBreakdown:
    """
    Calculate total annual cost for a plan based on its rate structure.

    Handles all rate types:
    - Fixed: Single rate per kWh
    - Tiered: Different rates for different usage levels
    - Time-of-use: Peak and off-peak rates
    - Variable: Base rate with historical adjustment

    Args:
        plan: Plan catalog entry from database
        projected_usage: Usage projection from Story 1.4
        include_connection_fee: Whether to include one-time connection fee

    Returns:
        CostBreakdown with detailed cost components

    Performance: <5ms per plan
    """
    rate_structure = plan.rate_structure
    rate_type = rate_structure.get('type', 'fixed')
    projected_annual_kwh = projected_usage.projected_annual_kwh

    # Calculate base cost based on rate type
    if rate_type == 'fixed':
        base_cost = _calculate_fixed_cost(rate_structure, projected_annual_kwh)

    elif rate_type == 'tiered':
        base_cost = _calculate_tiered_cost(rate_structure, projected_annual_kwh)

    elif rate_type == 'time_of_use':
        base_cost = _calculate_time_of_use_cost(
            rate_structure,
            projected_usage.projected_monthly_kwh
        )

    elif rate_type == 'variable':
        base_cost = _calculate_variable_cost(
            rate_structure,
            projected_annual_kwh,
            projected_usage.confidence_score
        )

    else:
        logger.warning(f"Unknown rate type '{rate_type}' for plan {plan.id}, using fixed rate fallback")
        base_cost = _calculate_fixed_cost(rate_structure, projected_annual_kwh)

    # Add monthly fees (multiply by 12 for annual)
    monthly_fees = Decimal('0.00')
    if plan.monthly_fee:
        monthly_fees = plan.monthly_fee * 12

    # Add connection fee if applicable
    connection_fee = Decimal('0.00')
    if include_connection_fee and plan.connection_fee:
        connection_fee = plan.connection_fee

    # Calculate total
    total_annual_cost = base_cost + monthly_fees + connection_fee

    # Calculate average rate per kWh
    if projected_annual_kwh > 0:
        avg_rate_per_kwh = (base_cost / Decimal(str(projected_annual_kwh))) * 100  # Convert to cents
    else:
        avg_rate_per_kwh = Decimal('0.00')

    return CostBreakdown(
        base_cost=base_cost,
        monthly_fees=monthly_fees,
        connection_fee=connection_fee,
        total_annual_cost=total_annual_cost,
        rate_type=rate_type,
        avg_rate_per_kwh=avg_rate_per_kwh
    )


def _calculate_fixed_cost(rate_structure: Dict[str, Any], annual_kwh: float) -> Decimal:
    """Calculate cost for fixed-rate plan."""
    # Support both 'rate' and 'rate_per_kwh' keys for backwards compatibility
    rate_per_kwh = Decimal(str(rate_structure.get('rate', rate_structure.get('rate_per_kwh', 0))))
    # Convert from cents to dollars
    return (rate_per_kwh / 100) * Decimal(str(annual_kwh))


def _calculate_tiered_cost(rate_structure: Dict[str, Any], annual_kwh: float) -> Decimal:
    """Calculate cost for tiered-rate plan."""
    tiers = rate_structure.get('tiers', [])
    if not tiers:
        # Fallback if tiers not defined
        return _calculate_fixed_cost(rate_structure, annual_kwh)

    total_cost = Decimal('0.00')
    remaining_kwh = annual_kwh

    for tier in tiers:
        max_kwh = tier.get('max_kwh', float('inf'))
        rate_per_kwh = Decimal(str(tier.get('rate_per_kwh', 0)))

        # Calculate kWh in this tier
        kwh_in_tier = min(remaining_kwh, max_kwh)

        # Add cost for this tier (convert rate from cents to dollars)
        tier_cost = (rate_per_kwh / 100) * Decimal(str(kwh_in_tier))
        total_cost += tier_cost

        remaining_kwh -= kwh_in_tier

        if remaining_kwh <= 0:
            break

    return total_cost


def _calculate_time_of_use_cost(
    rate_structure: Dict[str, Any],
    monthly_kwh: List[float]
) -> Decimal:
    """Calculate cost for time-of-use plan."""
    peak_rate = Decimal(str(rate_structure.get('peak_rate', 0)))
    off_peak_rate = Decimal(str(rate_structure.get('off_peak_rate', 0)))
    peak_pct = rate_structure.get('peak_pct', 0.5)  # Default: 50% during peak

    total_cost = Decimal('0.00')

    for month_kwh in monthly_kwh:
        peak_kwh = month_kwh * peak_pct
        off_peak_kwh = month_kwh * (1 - peak_pct)

        # Convert rates from cents to dollars
        month_cost = (
            (peak_rate / 100) * Decimal(str(peak_kwh)) +
            (off_peak_rate / 100) * Decimal(str(off_peak_kwh))
        )
        total_cost += month_cost

    return total_cost


def _calculate_variable_cost(
    rate_structure: Dict[str, Any],
    annual_kwh: float,
    confidence_score: float
) -> Decimal:
    """
    Calculate cost for variable-rate plan.

    Uses historical average with uncertainty buffer.
    """
    base_rate = Decimal(str(rate_structure.get('base_rate', 0)))
    historical_avg_rate = Decimal(str(rate_structure.get('historical_avg_rate', base_rate)))

    # Use historical average if available, otherwise base rate
    rate_to_use = historical_avg_rate if historical_avg_rate > 0 else base_rate

    # Add uncertainty buffer for variable rates (5-15% based on confidence)
    uncertainty_factor = 1.0 + (0.15 * (1 - confidence_score))

    # Convert from cents to dollars and apply uncertainty
    base_cost = (rate_to_use / 100) * Decimal(str(annual_kwh))
    adjusted_cost = base_cost * Decimal(str(uncertainty_factor))

    return adjusted_cost


# ============================================================================
# PLAN FILTERING (Story 2.2)
# ============================================================================

def filter_eligible_plans(
    db: Session,
    plan_filter: PlanFilter
) -> List[PlanCatalog]:
    """
    Filter plans by region, availability, and optional criteria.

    Args:
        db: Database session
        plan_filter: Filter criteria

    Returns:
        List of eligible plans

    Performance: <100ms for 1000 plans
    """
    # Base query: active plans in user's region
    query = db.query(PlanCatalog).join(Supplier).filter(
        and_(
            PlanCatalog.is_active == True,
            Supplier.is_active == True,
            plan_filter.zip_code == any_(PlanCatalog.available_regions)
        )
    )

    # Apply optional filters
    if plan_filter.max_contract_length is not None:
        query = query.filter(PlanCatalog.contract_length_months <= plan_filter.max_contract_length)

    if plan_filter.min_renewable_percentage is not None:
        query = query.filter(PlanCatalog.renewable_percentage >= plan_filter.min_renewable_percentage)

    if plan_filter.plan_types:
        query = query.filter(PlanCatalog.plan_type.in_(plan_filter.plan_types))

    plans = query.all()

    logger.info(f"Filtered {len(plans)} eligible plans for ZIP {plan_filter.zip_code}")

    return plans


# ============================================================================
# RANKING ALGORITHM (Story 2.2)
# ============================================================================

def rank_plans(
    plans: List[PlanCatalog],
    projected_usage: UsageProjection,
    preferences: UserPreferences,
    db: Session,
    top_n: int = 3
) -> List[Tuple[PlanCatalog, PlanScores, CostBreakdown]]:
    """
    Score and rank all eligible plans.

    Args:
        plans: List of eligible plans
        projected_usage: Usage projection from Story 1.4
        preferences: User preference weights
        db: Database session (for supplier lookups)
        top_n: Number of top plans to return (default 3)

    Returns:
        List of (plan, scores, cost_breakdown) tuples, sorted by composite score

    Performance: <500ms for 1000 plans
    """
    if not plans:
        return []

    # Calculate costs for all plans first (for relative cost scoring)
    plan_costs = []
    plan_cost_breakdowns = {}

    for plan in plans:
        cost_breakdown = calculate_plan_cost(plan, projected_usage, include_connection_fee=True)
        plan_costs.append(cost_breakdown.total_annual_cost)
        plan_cost_breakdowns[plan.id] = cost_breakdown

    # Score each plan
    scored_plans = []

    for plan in plans:
        supplier = plan.supplier  # Use relationship

        # Convert to dict for scoring function
        plan_dict = {
            'contract_length_months': plan.contract_length_months,
            'early_termination_fee': plan.early_termination_fee,
            'renewable_percentage': plan.renewable_percentage
        }

        supplier_dict = {
            'average_rating': supplier.average_rating,
            'review_count': supplier.review_count
        }

        # Get cost for this plan
        cost_breakdown = plan_cost_breakdowns[plan.id]

        # Calculate scores
        scores = score_plan(
            plan=plan_dict,
            supplier=supplier_dict,
            projected_annual_cost=cost_breakdown.total_annual_cost,
            projected_usage=projected_usage,
            preferences=preferences,
            all_plan_costs=plan_costs
        )

        scored_plans.append((plan, scores, cost_breakdown))

    # Sort by composite score (descending)
    scored_plans.sort(key=lambda x: x[1].composite_score, reverse=True)

    # Apply tie-breaking: prefer renewable, then lower cost
    scored_plans.sort(key=lambda x: (
        -x[1].composite_score,  # Primary: highest composite score
        -float(x[0].renewable_percentage),  # Tie-break 1: highest renewable
        float(x[2].total_annual_cost)  # Tie-break 2: lowest cost
    ))

    # Return top N
    return scored_plans[:top_n]


# ============================================================================
# MAIN RECOMMENDATION FUNCTION (Story 2.2)
# ============================================================================

def get_recommendations(
    user_id: UUID,
    usage_profile: UsageProjection,
    preferences: UserPreferences,
    db: Session,
    zip_code: str,
    top_n: int = 3
) -> RecommendationResult:
    """
    Generate top 3 plan recommendations for a user.

    This is the main entry point for Story 2.2.

    Args:
        user_id: User ID
        usage_profile: Usage projection from Story 1.4
        preferences: User preference weights
        db: Database session
        zip_code: User's ZIP code
        top_n: Number of recommendations (default 3)

    Returns:
        RecommendationResult with ranked plans

    Performance: <500ms for 1000 plans
    """
    start_time = datetime.now()

    # Filter eligible plans
    plan_filter = PlanFilter(zip_code=zip_code, is_active=True)
    eligible_plans = filter_eligible_plans(db, plan_filter)

    total_plans_analyzed = len(eligible_plans)

    if not eligible_plans:
        logger.warning(f"No eligible plans found for user {user_id} in ZIP {zip_code}")
        return RecommendationResult(
            user_id=user_id,
            top_plans=[],
            generated_at=datetime.now(),
            usage_profile_summary=_create_usage_summary(usage_profile),
            total_plans_analyzed=0,
            total_plans_eligible=0
        )

    # Rank plans
    ranked = rank_plans(
        plans=eligible_plans,
        projected_usage=usage_profile,
        preferences=preferences,
        db=db,
        top_n=top_n
    )

    # Convert to RankedPlan objects
    top_plans = []
    for rank, (plan, scores, cost_breakdown) in enumerate(ranked, start=1):
        ranked_plan = RankedPlan(
            plan_id=plan.id,
            rank=rank,
            plan_name=plan.plan_name,
            supplier_name=plan.supplier.supplier_name,
            plan_type=plan.plan_type,
            contract_length_months=plan.contract_length_months,
            early_termination_fee=plan.early_termination_fee,
            renewable_percentage=plan.renewable_percentage,
            scores=scores,
            projected_annual_cost=cost_breakdown.total_annual_cost,
            projected_monthly_cost=cost_breakdown.total_annual_cost / 12,
            cost_breakdown=cost_breakdown,
            rate_structure=plan.rate_structure,
            monthly_fee=plan.monthly_fee,
            connection_fee=plan.connection_fee
        )
        top_plans.append(ranked_plan)

    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
    logger.info(f"Generated {len(top_plans)} recommendations for user {user_id} in {elapsed_ms:.1f}ms")

    return RecommendationResult(
        user_id=user_id,
        top_plans=top_plans,
        generated_at=datetime.now(),
        usage_profile_summary=_create_usage_summary(usage_profile),
        total_plans_analyzed=total_plans_analyzed,
        total_plans_eligible=len(eligible_plans)
    )


# ============================================================================
# CONTRACT TIMING OPTIMIZATION (Story 2.3)
# ============================================================================

def analyze_switching_timing(
    current_plan: CurrentPlan,
    recommended_plans: List[RankedPlan],
    today: date = None
) -> SwitchingAnalysis:
    """
    Analyze switching costs and optimal timing.

    Args:
        current_plan: User's current plan details
        recommended_plans: Top recommended plans
        today: Current date (default: today)

    Returns:
        SwitchingAnalysis with timing recommendations
    """
    if today is None:
        today = date.today()

    # Calculate days until contract end
    days_until_end = (current_plan.contract_end_date - today).days
    etf = current_plan.early_termination_fee

    # Calculate current plan annual cost (simplified - using rate * typical usage)
    # In production, would use actual usage history
    current_annual_cost = (current_plan.current_rate / 100) * Decimal('12000')  # Assume 12k kWh/year
    if current_plan.monthly_fee:
        current_annual_cost += current_plan.monthly_fee * 12

    # Find best recommended plan
    if not recommended_plans:
        # No better plans available
        return SwitchingAnalysis(
            current_contract_end_date=current_plan.contract_end_date,
            days_until_contract_end=days_until_end,
            early_termination_fee=etf,
            monthly_savings=Decimal('0.00'),
            break_even_months=None,
            should_wait=True,
            optimal_switch_date=current_plan.contract_end_date,
            switching_recommendation="No better plans available. Stay with current plan."
        )

    best_plan = recommended_plans[0]
    annual_savings = current_annual_cost - best_plan.projected_annual_cost
    monthly_savings = annual_savings / 12

    # Break-even analysis
    if annual_savings <= 0:
        # Not saving money - should stay
        return SwitchingAnalysis(
            current_contract_end_date=current_plan.contract_end_date,
            days_until_contract_end=days_until_end,
            early_termination_fee=etf,
            monthly_savings=monthly_savings,
            break_even_months=None,
            should_wait=True,
            optimal_switch_date=current_plan.contract_end_date,
            switching_recommendation=f"Recommended plan costs more (${abs(monthly_savings):.2f}/month). Stay with current plan."
        )

    # Calculate break-even period
    if monthly_savings > 0:
        break_even_months = int((etf / monthly_savings) + 1)
    else:
        break_even_months = None

    # Determine if should wait
    if days_until_end <= 30:
        # Close to contract end - wait
        should_wait = True
        optimal_date = current_plan.contract_end_date
        recommendation = f"Contract ends in {days_until_end} days. Wait until {optimal_date.strftime('%B %d, %Y')} to switch without ETF."

    elif etf == 0:
        # No ETF - switch immediately
        should_wait = False
        optimal_date = today
        recommendation = f"No early termination fee. Switch now to save ${monthly_savings:.2f}/month."

    elif break_even_months and break_even_months > 18:
        # Long break-even - wait
        should_wait = True
        optimal_date = current_plan.contract_end_date
        recommendation = f"ETF of ${etf:.2f} would take {break_even_months} months to recoup. Wait until {optimal_date.strftime('%B %d, %Y')} to avoid ETF."

    elif monthly_savings * 12 > etf * 2:
        # Substantial savings - worth switching now
        should_wait = False
        optimal_date = today
        recommendation = f"Save ${monthly_savings:.2f}/month (${annual_savings:.2f}/year). Worth paying ${etf:.2f} ETF. Break-even in {break_even_months} months."

    else:
        # Marginal savings - wait
        should_wait = True
        optimal_date = current_plan.contract_end_date
        recommendation = f"Savings of ${monthly_savings:.2f}/month are marginal. Wait until {optimal_date.strftime('%B %d, %Y')} to avoid ${etf:.2f} ETF."

    return SwitchingAnalysis(
        current_contract_end_date=current_plan.contract_end_date,
        days_until_contract_end=days_until_end,
        early_termination_fee=etf,
        monthly_savings=monthly_savings,
        break_even_months=break_even_months,
        should_wait=should_wait,
        optimal_switch_date=optimal_date,
        switching_recommendation=recommendation
    )


def get_enhanced_recommendations(
    user_id: UUID,
    usage_profile: UsageProjection,
    preferences: UserPreferences,
    db: Session,
    zip_code: str,
    current_plan: Optional[CurrentPlan] = None,
    top_n: int = 3
) -> EnhancedRecommendationResult:
    """
    Generate recommendations with switching analysis (Story 2.3).

    Args:
        user_id: User ID
        usage_profile: Usage projection from Story 1.4
        preferences: User preference weights
        db: Database session
        zip_code: User's ZIP code
        current_plan: User's current plan (optional, for switching analysis)
        top_n: Number of recommendations (default 3)

    Returns:
        EnhancedRecommendationResult with switching analysis
    """
    # Get base recommendations
    base_result = get_recommendations(
        user_id=user_id,
        usage_profile=usage_profile,
        preferences=preferences,
        db=db,
        zip_code=zip_code,
        top_n=top_n
    )

    # If no current plan info, return base result
    if current_plan is None:
        return EnhancedRecommendationResult(
            user_id=base_result.user_id,
            top_plans=base_result.top_plans,
            generated_at=base_result.generated_at,
            usage_profile_summary=base_result.usage_profile_summary,
            total_plans_analyzed=base_result.total_plans_analyzed,
            total_plans_eligible=base_result.total_plans_eligible,
            switching_analysis=None,
            stay_with_current=False,
            stay_reason=None
        )

    # Calculate current plan annual cost if provided
    current_annual_cost = None
    if current_plan and current_plan.current_rate:
        current_annual_cost = (
            Decimal(str(current_plan.current_rate)) *
            Decimal(str(usage_profile.projected_annual_kwh)) /
            Decimal("100")  # Convert cents to dollars
        )

    # Populate savings fields on each plan
    for plan in base_result.top_plans:
        if current_annual_cost:
            # Calculate annual savings
            plan.projected_annual_savings = current_annual_cost - plan.projected_annual_cost

            # Calculate break-even months if there's an ETF
            if plan.early_termination_fee > 0 and plan.projected_annual_savings > 0:
                monthly_savings = plan.projected_annual_savings / Decimal("12")
                plan.break_even_months = int(plan.early_termination_fee / monthly_savings)
            else:
                plan.break_even_months = None
        else:
            plan.projected_annual_savings = None
            plan.break_even_months = None

    # Perform switching analysis
    switching_analysis = analyze_switching_timing(
        current_plan=current_plan,
        recommended_plans=base_result.top_plans
    )

    # Determine if should stay with current plan
    stay_with_current = switching_analysis.should_wait and switching_analysis.monthly_savings <= 0

    stay_reason = None
    if stay_with_current:
        stay_reason = switching_analysis.switching_recommendation

    return EnhancedRecommendationResult(
        user_id=base_result.user_id,
        top_plans=base_result.top_plans,
        generated_at=base_result.generated_at,
        usage_profile_summary=base_result.usage_profile_summary,
        total_plans_analyzed=base_result.total_plans_analyzed,
        total_plans_eligible=base_result.total_plans_eligible,
        switching_analysis=switching_analysis,
        stay_with_current=stay_with_current,
        stay_reason=stay_reason
    )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _create_usage_summary(usage_profile: UsageProjection) -> Dict[str, Any]:
    """Create a summary of usage profile for storage."""
    return {
        'projected_annual_kwh': usage_profile.projected_annual_kwh,
        'confidence_score': usage_profile.confidence_score,
        'projected_monthly_kwh': usage_profile.projected_monthly_kwh
    }
