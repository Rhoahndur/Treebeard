"""
Recommendation Endpoints.

Main recommendation generation and retrieval endpoints.

Story 6.3: Enhanced to include risk detection and stay recommendations.
"""

import logging
from datetime import datetime, timedelta
from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...config.database import get_db
from ...models.plan import Supplier
from ...models.recommendation import Recommendation
from ...models.user import User
from ...schemas.usage_analysis import MonthlyUsage
from ...services.explanation_service import create_explanation_service
from ...services.recommendation_engine import get_enhanced_recommendations
from ...services.risk_detection import (
    CurrentPlan as RiskCurrentPlan,
    create_risk_detection_service,
)
from ...services.savings_calculator import SavingsCalculatorService
from ...services.usage_analysis import UsageAnalysisService
from ..auth.rbac import Permission, require_permission
from ..auth_dependencies import CurrentActiveUser, CurrentUser, DBSession, OptionalUser
from ..schemas.common import MessageResponse
from ..schemas.recommendation_requests import (
    GenerateRecommendationRequest,
    GenerateRecommendationResponse,
    PlanRecommendationResponse,
    PlanScoresResponse,
    RiskWarningResponse,
    SavingsResponse,
    StayRecommendationResponse,
    UsageProfileSummary,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/generate",
    response_model=GenerateRecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Plan Recommendations",
    description="""
    Generate personalized energy plan recommendations based on usage data,
    preferences, and optional current plan information.

    This endpoint:
    1. Analyzes usage patterns (Story 1.4)
    2. Scores and ranks available plans (Story 2.2)
    3. Calculates savings (Story 2.4)
    4. Generates AI explanations (Story 2.7)

    Returns the top 3 recommended plans with detailed analysis.
    """,
)
async def generate_recommendations(
    request: GenerateRecommendationRequest,
    db: DBSession,
    current_user: OptionalUser = None,
):
    """
    Generate plan recommendations for a user.

    Args:
        request: Recommendation request with usage data and preferences
        current_user: Optional authenticated user (creates guest if not authenticated)
        db: Database session

    Returns:
        GenerateRecommendationResponse: Top 3 recommendations with explanations

    Raises:
        HTTPException: If generation fails
    """
    try:
        # Create or get user ID - use guest user if not authenticated
        if current_user:
            user_id = current_user.id
        else:
            # Create a guest user ID for anonymous recommendations
            user_id = uuid4()
        logger.info(
            f"Generating recommendations for user {user_id}",
            extra={"user_id": str(user_id)},
        )

        # Step 1: Analyze usage patterns (Story 1.4)
        usage_service = UsageAnalysisService()

        # Convert request usage data to MonthlyUsage objects
        usage_data = [
            MonthlyUsage(month=item.month, kwh=float(item.kwh))
            for item in request.usage_data
        ]

        usage_profile = usage_service.analyze_usage_patterns(
            usage_data=usage_data,
            user_id=str(user_id),
        )

        logger.info(
            f"Usage analysis complete: {usage_profile.profile_type.value}",
            extra={"profile_type": usage_profile.profile_type.value},
        )

        # Step 2: Get recommendations (Story 2.2)
        from ...schemas.explanation_schemas import UserPreferences

        preferences = UserPreferences(
            cost_priority=request.preferences.cost_priority,
            flexibility_priority=request.preferences.flexibility_priority,
            renewable_priority=request.preferences.renewable_priority,
            rating_priority=request.preferences.rating_priority,
        )

        # Get current plan if provided
        current_plan = None
        if request.current_plan:
            from ...models.user import CurrentPlan

            current_plan = CurrentPlan(
                plan_name=request.current_plan.plan_name,
                supplier_name=request.current_plan.supplier_name,
                current_rate=request.current_plan.current_rate,
                contract_end_date=request.current_plan.contract_end_date,
                early_termination_fee=request.current_plan.early_termination_fee,
                contract_start_date=request.current_plan.contract_start_date,
            )
            # Add annual_cost dynamically
            if request.current_plan.annual_cost is not None:
                current_plan.annual_cost = request.current_plan.annual_cost

        recommendation_result = get_enhanced_recommendations(
            user_id=user_id,
            usage_profile=usage_profile.projection,
            preferences=preferences,
            db=db,
            zip_code=request.user_data.zip_code,
            current_plan=current_plan,
            top_n=3,
        )

        logger.info(
            f"Found {len(recommendation_result.top_plans)} recommendations",
            extra={"plans_analyzed": recommendation_result.total_plans_analyzed},
        )

        # Step 3: Calculate savings for each plan (Story 2.4)
        savings_service = SavingsCalculatorService()
        plan_responses = []

        # Step 4: Generate explanations (Story 2.7)
        from ...config.settings import settings

        explanation_service = create_explanation_service(
            api_key=settings.openai_api_key,
            redis_client=None,  # Will use default from cache service
        )

        # Step 3.5: Calculate savings for all plans (needed for risk detection)
        from ...schemas.savings_schemas import SavingsAnalysis
        from decimal import Decimal

        savings_analyses = []
        for ranked_plan in recommendation_result.top_plans:
            # Calculate savings if current plan exists
            savings_data = None
            annual_savings = Decimal("0")
            savings_pct = Decimal("0")
            break_even = None

            if request.current_plan:
                # Calculate current plan annual cost
                current_annual_cost = (
                    Decimal(str(request.current_plan.current_rate))
                    * Decimal(str(usage_profile.projection.projected_annual_kwh))
                    / Decimal("100")  # Convert cents to dollars
                )

                # Use projected costs from ranked plan
                annual_savings = current_annual_cost - ranked_plan.projected_annual_cost

                if current_annual_cost > 0:
                    savings_pct = (annual_savings / current_annual_cost) * Decimal("100")

                    if ranked_plan.early_termination_fee > 0 and current_plan:
                        monthly_savings = annual_savings / Decimal("12")
                        if monthly_savings > 0:
                            break_even = int(
                                ranked_plan.early_termination_fee / monthly_savings
                            )

                    savings_data = SavingsResponse(
                        annual_savings=float(annual_savings),
                        savings_percentage=float(savings_pct),
                        monthly_savings=float(annual_savings / Decimal("12")),
                        break_even_months=break_even,
                    )

                # Create SavingsAnalysis for risk detection
                # Generate monthly breakdown (required by schema)
                from ...schemas.savings_schemas import MonthlyCost
                from datetime import datetime

                monthly_breakdown = []
                current_date = datetime.now()
                monthly_cost = ranked_plan.projected_monthly_cost
                monthly_kwh = Decimal(str(usage_profile.projection.projected_annual_kwh)) / Decimal("12")
                for month_num in range(1, 13):
                    monthly_breakdown.append(
                        MonthlyCost(
                            month=month_num,
                            year=current_date.year,
                            projected_kwh=monthly_kwh,
                            energy_cost=monthly_cost,
                            monthly_fee=ranked_plan.monthly_fee
                            if ranked_plan.monthly_fee
                            else Decimal("0"),
                            other_fees=Decimal("0"),
                            total_cost=monthly_cost
                            + (
                                ranked_plan.monthly_fee
                                if ranked_plan.monthly_fee
                                else Decimal("0")
                            ),
                        )
                    )

                savings_analysis = SavingsAnalysis(
                    plan_id=ranked_plan.plan_id,
                    user_id=user_id,
                    projected_annual_cost=ranked_plan.projected_annual_cost,
                    current_annual_cost=current_annual_cost,
                    annual_savings=annual_savings,
                    savings_percentage=savings_pct,
                    monthly_breakdown=monthly_breakdown,
                    total_cost_of_ownership=ranked_plan.projected_annual_cost,
                    tco_current_plan=current_annual_cost,
                    contract_length_months=ranked_plan.contract_length_months,
                    break_even_months=break_even,
                    switching_cost=ranked_plan.early_termination_fee
                    if current_plan
                    else Decimal("0"),
                    cumulative_savings_12_months=annual_savings
                    - (ranked_plan.early_termination_fee if current_plan else Decimal("0")),
                    total_energy_cost=ranked_plan.projected_annual_cost,
                )
                savings_analyses.append(savings_analysis)
            else:
                savings_data = None

        # Step 4: Detect risks (Story 6.1) if requested
        all_risk_warnings = []
        risk_summary = None
        should_stay = False
        stay_recommendation = None

        if request.include_risks and request.current_plan:
            logger.info("Running risk detection")
            risk_service = create_risk_detection_service()

            # Convert current_plan to RiskCurrentPlan
            risk_current_plan = RiskCurrentPlan(
                plan_name=request.current_plan.plan_name or "Current Plan",
                supplier_name=request.current_plan.supplier_name or "Current Supplier",
                current_rate=Decimal(str(request.current_plan.current_rate or 0)),
                contract_end_date=request.current_plan.contract_end_date,
                early_termination_fee=Decimal(
                    str(request.current_plan.early_termination_fee or 0)
                ),
                annual_cost=current_annual_cost if request.current_plan else None,
                contract_start_date=request.current_plan.contract_start_date,
            )

            # Detect risks for all plans
            all_risk_warnings = risk_service.detect_risks(
                plans=recommendation_result.top_plans,
                current_plan=risk_current_plan,
                savings_analyses=savings_analyses if savings_analyses else None,
                usage_profile=usage_profile,
                preferences=preferences,
            )

            # Calculate risk summary
            risk_summary = risk_service.calculate_risk_summary(
                risks=all_risk_warnings, plans=recommendation_result.top_plans
            )

            # Check if user should stay (Story 6.2)
            if recommendation_result.top_plans and savings_analyses:
                top_plan = recommendation_result.top_plans[0]
                top_savings = savings_analyses[0]

                should_stay, stay_rec = risk_service.should_recommend_staying(
                    current_plan=risk_current_plan,
                    top_plan=top_plan,
                    savings=top_savings,
                    risks=all_risk_warnings,
                    all_plans_count=recommendation_result.total_plans_analyzed,
                )

                stay_recommendation = stay_rec

            logger.info(
                f"Risk detection complete: {len(all_risk_warnings)} risks, "
                f"should_stay={should_stay}"
            )

        # Step 5: Query supplier websites and logos for all plans (to avoid N+1 queries)
        supplier_names = [plan.supplier_name for plan in recommendation_result.top_plans]
        suppliers = db.query(Supplier).filter(Supplier.supplier_name.in_(supplier_names)).all()
        supplier_websites = {s.supplier_name: s.website for s in suppliers}
        supplier_logo_urls = {s.supplier_name: s.logo_url for s in suppliers}

        # Step 6: Build plan responses with risk warnings
        plan_responses = []
        for i, ranked_plan in enumerate(recommendation_result.top_plans):
            savings_data = None
            if i < len(savings_analyses):
                sa = savings_analyses[i]
                savings_data = SavingsResponse(
                    annual_savings=float(sa.annual_savings),
                    savings_percentage=float(sa.savings_percentage),
                    monthly_savings=float(sa.annual_savings / Decimal("12")),
                    break_even_months=sa.break_even_months,
                )

            # Generate explanation
            explanation = await explanation_service.generate_explanation(
                plan=ranked_plan,
                user_profile=usage_profile.to_dict(),
                preferences=preferences,
                current_plan=current_plan,
            )

            # Get risk warnings for this plan
            plan_risk_warnings = [
                RiskWarningResponse(
                    risk_type=r.risk_type.value,
                    severity=r.severity.value,
                    category=r.category.value,
                    title=r.title,
                    message=r.message,
                    mitigation=r.mitigation,
                )
                for r in all_risk_warnings
                if ranked_plan.plan_id in r.affected_plan_ids
            ]

            # Determine highest severity
            highest_severity = None
            if plan_risk_warnings:
                severity_order = {"critical": 0, "warning": 1, "info": 2}
                plan_risk_warnings_sorted = sorted(
                    plan_risk_warnings, key=lambda r: severity_order.get(r.severity, 3)
                )
                highest_severity = plan_risk_warnings_sorted[0].severity

            # Build response
            plan_response = PlanRecommendationResponse(
                rank=ranked_plan.rank,
                plan_id=ranked_plan.plan_id,
                plan_name=ranked_plan.plan_name,
                supplier_name=ranked_plan.supplier_name,
                supplier_website=supplier_websites.get(ranked_plan.supplier_name),
                supplier_logo_url=supplier_logo_urls.get(ranked_plan.supplier_name),
                plan_type=ranked_plan.plan_type,
                scores=PlanScoresResponse(
                    cost_score=ranked_plan.scores.cost_score,
                    flexibility_score=ranked_plan.scores.flexibility_score,
                    renewable_score=ranked_plan.scores.renewable_score,
                    rating_score=ranked_plan.scores.rating_score,
                    composite_score=ranked_plan.scores.composite_score,
                ),
                projected_annual_cost=ranked_plan.projected_annual_cost,
                projected_monthly_cost=ranked_plan.projected_monthly_cost,
                average_rate_per_kwh=ranked_plan.cost_breakdown.avg_rate_per_kwh,
                savings=savings_data,
                contract_length_months=ranked_plan.contract_length_months,
                early_termination_fee=ranked_plan.early_termination_fee,
                renewable_percentage=ranked_plan.renewable_percentage,
                monthly_fee=ranked_plan.monthly_fee,
                explanation=explanation.explanation_text,
                key_differentiators=explanation.key_differentiators,
                trade_offs=explanation.trade_offs,
                risk_warnings=plan_risk_warnings,
                risk_count=len(plan_risk_warnings),
                highest_risk_severity=highest_severity,
            )
            plan_responses.append(plan_response)

        # Create recommendation record in database (only for authenticated users)
        recommendation_id = uuid4()
        generated_at = datetime.utcnow()

        # Only save to database if user is authenticated (not a guest)
        if current_user:
            db_recommendation = Recommendation(
                id=recommendation_id,
                user_id=user_id,
                usage_profile=usage_profile.to_dict(),
                generated_at=generated_at,
                expires_at=generated_at + timedelta(hours=24),  # Recommendations expire after 24 hours
            )
            db.add(db_recommendation)
            db.commit()

        # Build stay recommendation response
        stay_rec_response = None
        if stay_recommendation:
            stay_rec_response = StayRecommendationResponse(
                should_stay=stay_recommendation.should_stay,
                reasoning=stay_recommendation.reasoning,
                triggers=[t.value for t in stay_recommendation.triggers],
                net_annual_savings=stay_recommendation.net_annual_savings,
                break_even_months=stay_recommendation.break_even_months,
                confidence=Decimal(str(stay_recommendation.confidence)),
            )

        # Build response with risk data
        response = GenerateRecommendationResponse(
            recommendation_id=recommendation_id,
            user_profile=UsageProfileSummary(
                profile_type=usage_profile.profile_type.value,
                projected_annual_kwh=usage_profile.projection.projected_annual_kwh,
                mean_monthly_kwh=usage_profile.statistics.mean_kwh,
                has_seasonal_pattern=usage_profile.seasonal_analysis.has_seasonal_pattern,
                confidence_score=usage_profile.overall_confidence,
            ),
            top_plans=plan_responses,
            generated_at=datetime.utcnow(),
            total_plans_analyzed=recommendation_result.total_plans_analyzed,
            warnings=usage_profile.warnings,
            # Risk analysis (Story 6.1)
            overall_risk_level=risk_summary.overall_risk_level if risk_summary else "low",
            total_risks_detected=len(all_risk_warnings),
            critical_risk_count=risk_summary.critical_count if risk_summary else 0,
            # Stay recommendation (Story 6.2)
            should_stay=should_stay,
            stay_recommendation=stay_rec_response,
        )

        logger.info(
            f"Successfully generated recommendations",
            extra={
                "recommendation_id": str(recommendation_id),
                "num_plans": len(plan_responses),
            },
        )

        return response

    except Exception as exc:
        logger.error(
            f"Failed to generate recommendations: {exc}",
            exc_info=True,
            extra={"user_id": str(user_id) if 'user_id' in locals() else 'unknown'},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(exc)}",
        )


@router.get(
    "/{user_id}",
    response_model=List[GenerateRecommendationResponse],
    summary="Get User Recommendations",
    description="Retrieve saved recommendations for a user.",
)
async def get_user_recommendations(
    user_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Get saved recommendations for a user.

    Args:
        user_id: User ID to get recommendations for
        current_user: Authenticated user
        db: Database session

    Returns:
        List[GenerateRecommendationResponse]: User's recommendations

    Raises:
        HTTPException: If not authorized or user not found
    """
    # Check authorization - users can only view their own recommendations
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these recommendations",
        )

    # Get recommendations from database
    recommendations = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == user_id)
        .order_by(Recommendation.generated_at.desc())
        .limit(10)
        .all()
    )

    # Convert to response format
    # TODO: Implement full conversion from DB model to response
    return []


@router.delete(
    "/{recommendation_id}",
    response_model=MessageResponse,
    summary="Delete Recommendation",
    description="Delete a saved recommendation.",
)
async def delete_recommendation(
    recommendation_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Delete a recommendation.

    Args:
        recommendation_id: Recommendation ID to delete
        current_user: Authenticated user
        db: Database session

    Returns:
        MessageResponse: Success message

    Raises:
        HTTPException: If not authorized or not found
    """
    # Get recommendation
    recommendation = (
        db.query(Recommendation)
        .filter(Recommendation.id == recommendation_id)
        .first()
    )

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    # Check authorization
    if recommendation.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this recommendation",
        )

    # Delete
    db.delete(recommendation)
    db.commit()

    return MessageResponse(
        message="Recommendation deleted successfully",
        success=True,
    )
