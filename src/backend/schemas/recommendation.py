"""
Pydantic schemas for recommendations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .usage_schemas import UsageProfile
from .plan import PlanCatalogResponse


# Score component schemas

class PlanScores(BaseModel):
    """Individual score components for a plan recommendation."""

    cost_score: Decimal = Field(..., ge=0, le=100, description="Cost score (0-100)")
    flexibility_score: Decimal = Field(..., ge=0, le=100, description="Flexibility score (0-100)")
    renewable_score: Decimal = Field(..., ge=0, le=100, description="Renewable score (0-100)")
    rating_score: Decimal = Field(..., ge=0, le=100, description="Rating score (0-100)")
    composite_score: Decimal = Field(..., ge=0, le=100, description="Weighted composite score (0-100)")


# Risk flags schema

class RiskFlags(BaseModel):
    """Risk warnings for a recommended plan."""

    high_etf: Optional[dict[str, Any]] = Field(
        None,
        description="High early termination fee warning"
    )
    low_savings: Optional[dict[str, Any]] = Field(
        None,
        description="Low savings warning"
    )
    data_quality: Optional[dict[str, Any]] = Field(
        None,
        description="Data quality issues warning"
    )
    variable_rate: Optional[dict[str, Any]] = Field(
        None,
        description="Variable rate volatility warning"
    )
    contract_mismatch: Optional[dict[str, Any]] = Field(
        None,
        description="Contract timing mismatch warning"
    )


# Recommendation request/response schemas

class RecommendationRequest(BaseModel):
    """Request to generate recommendations for a user."""

    user_id: UUID = Field(..., description="User ID to generate recommendations for")
    force_refresh: bool = Field(
        default=False,
        description="Force regeneration even if cached recommendations exist"
    )


class RecommendationPlanResponse(BaseModel):
    """Individual recommended plan with all details."""

    id: UUID = Field(..., description="Recommendation plan ID")
    rank: int = Field(..., ge=1, le=3, description="Rank (1=best, 2=second, 3=third)")

    # Plan details
    plan: PlanCatalogResponse = Field(..., description="Complete plan information")

    # Scores
    scores: PlanScores = Field(..., description="Score breakdown")

    # Projections
    projected_annual_cost: Decimal = Field(..., description="Projected annual cost in dollars")
    projected_annual_savings: Decimal = Field(..., description="Savings vs current plan in dollars")
    break_even_months: Optional[int] = Field(
        None,
        description="Months to break even if switching costs apply"
    )

    # Explanation
    explanation: str = Field(..., description="Plain-language explanation")

    # Warnings
    risk_flags: Optional[dict[str, Any]] = Field(None, description="Risk warnings")

    model_config = {"from_attributes": True}


class RecommendationResponse(BaseModel):
    """Complete recommendation response with top 3 plans."""

    id: UUID = Field(..., description="Recommendation session ID")
    user_id: UUID = Field(..., description="User ID")

    # Usage analysis
    usage_profile: dict[str, Any] = Field(
        ...,
        description="Analyzed usage patterns and projections"
    )

    # Recommended plans (top 3)
    recommended_plans: list[RecommendationPlanResponse] = Field(
        ...,
        min_length=0,
        max_length=3,
        description="Top 3 recommended plans (may be less if insufficient options)"
    )

    # Metadata
    generated_at: datetime = Field(..., description="When recommendations were generated")
    expires_at: datetime = Field(..., description="When recommendations expire")
    algorithm_version: str = Field(..., description="Algorithm version used")

    # Special cases
    stay_with_current: bool = Field(
        default=False,
        description="Whether staying with current plan is recommended"
    )
    stay_reason: Optional[str] = Field(
        None,
        description="Reason for recommending to stay with current plan"
    )

    model_config = {"from_attributes": True}


class RecommendationSummary(BaseModel):
    """Simplified recommendation summary for list views."""

    id: UUID
    user_id: UUID
    generated_at: datetime
    expires_at: datetime
    num_recommendations: int = Field(..., description="Number of plans recommended")
    top_plan_id: Optional[UUID] = Field(None, description="ID of top recommended plan")
    top_plan_name: Optional[str] = Field(None, description="Name of top plan")
    projected_savings: Optional[Decimal] = Field(None, description="Savings from top plan")

    model_config = {"from_attributes": True}
