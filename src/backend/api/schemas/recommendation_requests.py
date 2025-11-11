"""
Recommendation API Request/Response Schemas.

Enhanced in Story 6.3 to include risk warnings and stay recommendations.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Request Schemas


class UserDataRequest(BaseModel):
    """
    User data for recommendation generation.
    """

    zip_code: str = Field(..., min_length=5, max_length=10, description="ZIP code")
    property_type: str = Field(
        "residential",
        pattern="^(residential|commercial)$",
        description="Property type",
    )


class MonthlyUsageData(BaseModel):
    """
    Monthly usage data point.
    """

    month: date = Field(..., description="Month (first day of month)")
    kwh: Decimal = Field(..., ge=0, description="kWh consumed")


class UserPreferencesRequest(BaseModel):
    """
    User preferences for plan selection.
    """

    cost_priority: int = Field(40, ge=0, le=100, description="Cost priority (0-100)")
    flexibility_priority: int = Field(
        30, ge=0, le=100, description="Flexibility priority (0-100)"
    )
    renewable_priority: int = Field(
        20, ge=0, le=100, description="Renewable energy priority (0-100)"
    )
    rating_priority: int = Field(
        10, ge=0, le=100, description="Supplier rating priority (0-100)"
    )


class CurrentPlanRequest(BaseModel):
    """
    Current plan information.
    """

    plan_name: Optional[str] = Field(None, description="Current plan name")
    supplier_name: Optional[str] = Field(None, description="Current supplier name")
    current_rate: Optional[Decimal] = Field(
        None, ge=0, description="Current rate (cents per kWh)"
    )
    contract_end_date: Optional[date] = Field(None, description="Contract end date")
    early_termination_fee: Optional[Decimal] = Field(
        None, ge=0, description="Early termination fee"
    )
    annual_cost: Optional[Decimal] = Field(
        None, ge=0, description="Annual cost of current plan"
    )
    contract_start_date: Optional[date] = Field(None, description="Contract start date")


class GenerateRecommendationRequest(BaseModel):
    """
    Request to generate plan recommendations.

    Story 6.3: Enhanced with risk detection option.
    """

    user_data: UserDataRequest = Field(..., description="User location and property data")
    usage_data: List[MonthlyUsageData] = Field(
        ..., min_items=3, max_items=24, description="12 months of usage data (3-24 months)"
    )
    preferences: UserPreferencesRequest = Field(..., description="User preferences")
    current_plan: Optional[CurrentPlanRequest] = Field(None, description="Current plan")
    include_risks: bool = Field(True, description="Include risk analysis (Story 6.1)")

    class Config:
        json_schema_extra = {
            "example": {
                "user_data": {"zip_code": "78701", "property_type": "residential"},
                "usage_data": [
                    {"month": "2024-01-01", "kwh": 850},
                    {"month": "2024-02-01", "kwh": 820},
                    {"month": "2024-03-01", "kwh": 780},
                    {"month": "2024-04-01", "kwh": 900},
                    {"month": "2024-05-01", "kwh": 950},
                    {"month": "2024-06-01", "kwh": 1400},
                    {"month": "2024-07-01", "kwh": 1600},
                    {"month": "2024-08-01", "kwh": 1500},
                    {"month": "2024-09-01", "kwh": 1000},
                    {"month": "2024-10-01", "kwh": 850},
                    {"month": "2024-11-01", "kwh": 800},
                    {"month": "2024-12-01", "kwh": 820},
                ],
                "preferences": {
                    "cost_priority": 50,
                    "flexibility_priority": 20,
                    "renewable_priority": 20,
                    "rating_priority": 10,
                },
                "current_plan": {
                    "plan_name": "Standard Plan",
                    "supplier_name": "CurrentCo",
                    "current_rate": 12.5,
                    "contract_end_date": "2025-06-30",
                    "early_termination_fee": 150,
                },
            }
        }


# Response Schemas


class UsageProfileSummary(BaseModel):
    """
    Summary of user's usage profile.
    """

    profile_type: str = Field(..., description="Profile type classification")
    projected_annual_kwh: Decimal = Field(..., description="Projected annual usage")
    mean_monthly_kwh: Decimal = Field(..., description="Mean monthly usage")
    has_seasonal_pattern: bool = Field(
        ..., description="Whether user has seasonal usage pattern"
    )
    confidence_score: Decimal = Field(..., description="Analysis confidence (0-1)")


class PlanScoresResponse(BaseModel):
    """
    Plan scores breakdown.
    """

    cost_score: Decimal = Field(..., description="Cost score (0-100)")
    flexibility_score: Decimal = Field(..., description="Flexibility score (0-100)")
    renewable_score: Decimal = Field(..., description="Renewable energy score (0-100)")
    rating_score: Decimal = Field(..., description="Supplier rating score (0-100)")
    composite_score: Decimal = Field(..., description="Composite score (0-100)")


class SavingsResponse(BaseModel):
    """
    Savings information.
    """

    annual_savings: Decimal = Field(..., description="Annual savings vs current plan")
    savings_percentage: Decimal = Field(..., description="Savings percentage")
    monthly_savings: Decimal = Field(..., description="Average monthly savings")
    break_even_months: Optional[int] = Field(
        None, description="Months to break even (if ETF exists)"
    )


class RiskWarningResponse(BaseModel):
    """
    Risk warning for a plan.

    Story 6.1: Risk detection output.
    """

    risk_type: str = Field(..., description="Type of risk")
    severity: str = Field(..., description="Severity: critical, warning, info")
    category: str = Field(..., description="Risk category")
    title: str = Field(..., description="Risk title")
    message: str = Field(..., description="Risk explanation")
    mitigation: Optional[str] = Field(None, description="Suggested mitigation")


class PlanRecommendationResponse(BaseModel):
    """
    Single plan recommendation.

    Story 6.3: Enhanced with risk warnings.
    """

    rank: int = Field(..., ge=1, le=3, description="Recommendation rank (1-3)")
    plan_id: UUID = Field(..., description="Plan ID")
    plan_name: str = Field(..., description="Plan name")
    supplier_name: str = Field(..., description="Supplier name")
    supplier_website: Optional[str] = Field(None, description="Supplier website URL")
    supplier_logo_url: Optional[str] = Field(None, description="Supplier logo URL")
    plan_type: str = Field(..., description="Plan type")

    # Scores
    scores: PlanScoresResponse = Field(..., description="Scoring breakdown")

    # Costs
    projected_annual_cost: Decimal = Field(..., description="Projected annual cost")
    projected_monthly_cost: Decimal = Field(..., description="Projected monthly cost")
    average_rate_per_kwh: Decimal = Field(..., description="Average rate (cents per kWh)")

    # Savings (if current plan provided)
    savings: Optional[SavingsResponse] = Field(None, description="Savings vs current plan")

    # Plan details
    contract_length_months: int = Field(..., description="Contract length (0 = month-to-month)")
    early_termination_fee: Decimal = Field(..., description="Early termination fee")
    renewable_percentage: Decimal = Field(..., description="Renewable energy percentage")
    monthly_fee: Optional[Decimal] = Field(None, description="Monthly base fee")

    # AI Explanation
    explanation: str = Field(..., description="AI-generated explanation")
    key_differentiators: List[str] = Field(..., description="Key differentiating factors")
    trade_offs: List[str] = Field(..., description="Important trade-offs")

    # Risk warnings (Story 6.1)
    risk_warnings: List[RiskWarningResponse] = Field(
        default_factory=list, description="Risk warnings for this plan"
    )
    risk_count: int = Field(default=0, description="Total risk count")
    highest_risk_severity: Optional[str] = Field(None, description="Highest risk severity")


class StayRecommendationResponse(BaseModel):
    """
    Recommendation to stay with current plan.

    Story 6.2: Stay logic output.
    """

    should_stay: bool = Field(..., description="Whether to stay with current plan")
    reasoning: str = Field(..., description="Explanation for stay recommendation")
    triggers: List[str] = Field(..., description="Reasons for staying")
    net_annual_savings: Optional[Decimal] = Field(None, description="Net savings after costs")
    break_even_months: Optional[int] = Field(None, description="Break-even period")
    confidence: Decimal = Field(..., description="Confidence in recommendation (0-1)")


class GenerateRecommendationResponse(BaseModel):
    """
    Response with top plan recommendations.

    Story 6.3: Enhanced with risk warnings and stay recommendation.
    """

    recommendation_id: UUID = Field(..., description="Unique recommendation ID")
    user_profile: UsageProfileSummary = Field(..., description="User usage profile summary")
    top_plans: List[PlanRecommendationResponse] = Field(
        ..., description="Top 3 recommended plans"
    )
    generated_at: datetime = Field(..., description="Generation timestamp")
    total_plans_analyzed: int = Field(..., description="Number of plans analyzed")
    warnings: List[str] = Field(default_factory=list, description="Any warnings or notes")

    # Risk analysis (Story 6.1)
    overall_risk_level: str = Field(
        default="low", description="Overall risk level: low, medium, high"
    )
    total_risks_detected: int = Field(default=0, description="Total risks across all plans")
    critical_risk_count: int = Field(default=0, description="Number of critical risks")

    # Stay recommendation (Story 6.2)
    should_stay: bool = Field(
        default=False, description="Whether staying with current plan is recommended"
    )
    stay_recommendation: Optional[StayRecommendationResponse] = Field(
        None, description="Stay recommendation details"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "recommendation_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_profile": {
                    "profile_type": "seasonal",
                    "projected_annual_kwh": 12270,
                    "mean_monthly_kwh": 1022.5,
                    "has_seasonal_pattern": True,
                    "confidence_score": 0.85,
                },
                "top_plans": [
                    {
                        "rank": 1,
                        "plan_id": "223e4567-e89b-12d3-a456-426614174001",
                        "plan_name": "Solar Saver 12",
                        "supplier_name": "GreenEnergy Co",
                        "plan_type": "fixed",
                        "scores": {
                            "cost_score": 92.5,
                            "flexibility_score": 80.0,
                            "renewable_score": 100.0,
                            "rating_score": 95.0,
                            "composite_score": 91.2,
                        },
                        "projected_annual_cost": 1500.00,
                        "projected_monthly_cost": 125.00,
                        "average_rate_per_kwh": 11.8,
                        "savings": {
                            "annual_savings": 300.00,
                            "savings_percentage": 16.7,
                            "monthly_savings": 25.00,
                            "break_even_months": 6,
                        },
                        "contract_length_months": 12,
                        "early_termination_fee": 150.00,
                        "renewable_percentage": 100.0,
                        "monthly_fee": 0.0,
                        "explanation": "This plan will save you $300 per year...",
                        "key_differentiators": [
                            "100% renewable energy",
                            "Lowest total cost",
                        ],
                        "trade_offs": ["12-month contract commitment"],
                    }
                ],
                "generated_at": "2025-11-10T14:30:00Z",
                "total_plans_analyzed": 156,
                "warnings": [],
            }
        }
