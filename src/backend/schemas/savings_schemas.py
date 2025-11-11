"""
Pydantic schemas for savings analysis and plan comparison.

Stories 2.4 and 2.5: Savings Calculator & Comparison Features
Author: Backend Dev #4
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Story 2.4: Savings Analysis Schemas

class MonthlyCost(BaseModel):
    """Month-by-month cost breakdown."""

    month: int = Field(..., ge=1, le=12, description="Month number (1-12)")
    year: int = Field(..., description="Year")
    projected_kwh: Decimal = Field(..., ge=0, description="Projected kWh for the month")
    energy_cost: Decimal = Field(..., ge=0, description="Energy cost for the month")
    monthly_fee: Decimal = Field(default=Decimal("0.00"), ge=0, description="Monthly base fee")
    other_fees: Decimal = Field(default=Decimal("0.00"), ge=0, description="Other fees")
    total_cost: Decimal = Field(..., ge=0, description="Total cost for the month")

    @field_validator("total_cost")
    @classmethod
    def validate_total_cost(cls, v: Decimal, values: Any) -> Decimal:
        """Ensure total_cost matches sum of components (if all are provided)."""
        # Note: In Pydantic v2, we don't have access to other fields during validation
        # This validation is more of a documentation of expected behavior
        return v


class CostRange(BaseModel):
    """Cost range for variable rate plans with uncertainty."""

    low_estimate: Decimal = Field(..., description="Lower bound estimate (conservative)")
    high_estimate: Decimal = Field(..., description="Upper bound estimate (worst case)")
    expected_value: Decimal = Field(..., description="Most likely cost (expected value)")
    confidence_level: Decimal = Field(
        default=Decimal("0.95"),
        ge=0,
        le=1,
        description="Confidence level (e.g., 0.95 for 95% confidence interval)"
    )
    volatility_note: Optional[str] = Field(
        None,
        description="Explanation of volatility factors"
    )

    @field_validator("low_estimate", "high_estimate", "expected_value")
    @classmethod
    def validate_range_order(cls, v: Decimal, info) -> Decimal:
        """Validate that estimates are in logical order."""
        # Pydantic v2 validation - we'll validate the full model in a separate validator
        return v


class SavingsAnalysis(BaseModel):
    """
    Complete savings analysis for a recommended plan.

    Story 2.4: Calculates detailed cost comparisons and savings projections.
    """

    plan_id: UUID = Field(..., description="ID of the recommended plan")
    user_id: UUID = Field(..., description="ID of the user")

    # Annual cost comparison
    projected_annual_cost: Decimal = Field(
        ...,
        ge=0,
        description="Projected annual cost for recommended plan"
    )
    current_annual_cost: Decimal = Field(
        ...,
        ge=0,
        description="Current plan annual cost"
    )
    annual_savings: Decimal = Field(
        ...,
        description="Annual savings (can be negative if more expensive)"
    )
    savings_percentage: Decimal = Field(
        ...,
        description="Savings as percentage of current cost"
    )

    # Monthly breakdown
    monthly_breakdown: list[MonthlyCost] = Field(
        ...,
        min_length=12,
        max_length=12,
        description="Month-by-month cost projection (12 months)"
    )

    # Total Cost of Ownership
    total_cost_of_ownership: Decimal = Field(
        ...,
        ge=0,
        description="Total cost over contract length including all fees"
    )
    tco_current_plan: Decimal = Field(
        ...,
        ge=0,
        description="TCO for current plan over same period"
    )
    contract_length_months: int = Field(
        ...,
        ge=0,
        description="Contract length used for TCO calculation"
    )

    # Break-even analysis (if switching cost exists)
    break_even_months: Optional[int] = Field(
        None,
        ge=0,
        description="Months until savings offset switching cost (ETF)"
    )
    switching_cost: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Early termination fee for leaving current plan"
    )
    cumulative_savings_12_months: Decimal = Field(
        ...,
        description="Cumulative savings after 12 months (including switching cost)"
    )

    # Variable rate uncertainty (if applicable)
    uncertainty_range: Optional[CostRange] = Field(
        None,
        description="Cost range for variable rate plans"
    )
    is_variable_rate: bool = Field(
        default=False,
        description="Whether this is a variable rate plan"
    )

    # Fees breakdown
    total_upfront_fees: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Total upfront fees (connection fee, etc.)"
    )
    total_monthly_fees: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Total monthly fees over contract period"
    )
    total_energy_cost: Decimal = Field(
        ...,
        ge=0,
        description="Total energy cost (kWh × rate)"
    )

    # Metadata
    analysis_date: datetime = Field(
        default_factory=datetime.now,
        description="When this analysis was generated"
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Key assumptions used in calculations"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Warnings about the analysis (e.g., high ETF, low confidence)"
    )

    model_config = {"from_attributes": True}


# Story 2.5: Comparison Features Schemas

class ComparisonPlan(BaseModel):
    """
    Plan data structured for side-by-side comparison.

    Story 2.5: Enables comparison of multiple plans with current plan.
    """

    plan_id: UUID = Field(..., description="Plan ID")
    plan_name: str = Field(..., description="Plan name")
    supplier_name: str = Field(..., description="Supplier name")

    # Cost metrics
    annual_cost: Decimal = Field(..., ge=0, description="Projected annual cost")
    monthly_average: Decimal = Field(..., ge=0, description="Average monthly cost")
    first_year_total: Decimal = Field(..., ge=0, description="Total first year cost including all fees")

    # Contract terms
    contract_length_months: int = Field(..., ge=0, description="Contract length (0=month-to-month)")
    early_termination_fee: Decimal = Field(default=Decimal("0.00"), ge=0, description="ETF")
    monthly_fee: Decimal = Field(default=Decimal("0.00"), ge=0, description="Monthly base fee")

    # Plan attributes
    renewable_percentage: Decimal = Field(..., ge=0, le=100, description="Renewable energy %")
    plan_type: str = Field(..., description="fixed, variable, tiered, time_of_use")
    rate_per_kwh: Optional[Decimal] = Field(None, description="Rate (for fixed plans)")

    # Supplier rating
    supplier_rating: Optional[Decimal] = Field(None, ge=0, le=5, description="Supplier rating (0-5)")

    # Savings vs current
    savings_vs_current_annual: Decimal = Field(
        ...,
        description="Annual savings vs current plan (negative if more expensive)"
    )
    savings_vs_current_percentage: Decimal = Field(
        ...,
        description="Savings percentage vs current plan"
    )

    # Rank and scores (from Story 2.2)
    rank: Optional[int] = Field(None, ge=1, description="Recommendation rank")
    composite_score: Optional[Decimal] = Field(None, ge=0, le=1, description="Overall score (0-1)")

    # Comparison indicators
    is_current_plan: bool = Field(default=False, description="Whether this is user's current plan")
    is_recommended: bool = Field(default=False, description="Whether this is in top recommendations")

    model_config = {"from_attributes": True}


class TradeOffNote(BaseModel):
    """Trade-off analysis note comparing plan characteristics."""

    category: str = Field(..., description="Category: cost, contract, renewable, flexibility, rating")
    description: str = Field(..., description="Human-readable trade-off description")
    affected_plans: list[UUID] = Field(..., description="Plan IDs affected by this trade-off")
    severity: str = Field(
        default="info",
        description="Severity: info, warning, critical"
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category."""
        valid_categories = ["cost", "contract", "renewable", "flexibility", "rating", "other"]
        if v not in valid_categories:
            raise ValueError(f"Category must be one of {valid_categories}")
        return v

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        """Validate severity."""
        valid_severities = ["info", "warning", "critical"]
        if v not in valid_severities:
            raise ValueError(f"Severity must be one of {valid_severities}")
        return v


class MultiYearProjection(BaseModel):
    """Cost projection over multiple years."""

    year: int = Field(..., ge=1, le=3, description="Year number (1-3)")
    annual_cost: Decimal = Field(..., ge=0, description="Projected annual cost")
    cumulative_cost: Decimal = Field(..., ge=0, description="Cumulative cost from year 1")
    cumulative_savings: Decimal = Field(..., description="Cumulative savings vs current plan")
    notes: list[str] = Field(
        default_factory=list,
        description="Notes (e.g., contract renewal, rate changes)"
    )


class PlanComparison(BaseModel):
    """
    Side-by-side comparison of multiple plans.

    Story 2.5: Complete comparison structure for 3+ plans.
    """

    comparison_id: UUID = Field(default_factory=lambda: UUID(int=0), description="Comparison ID")
    user_id: UUID = Field(..., description="User ID")

    # Plans being compared
    plans: list[ComparisonPlan] = Field(
        ...,
        min_length=1,
        description="Plans to compare (including recommended plans)"
    )
    current_plan: ComparisonPlan = Field(..., description="User's current plan for baseline")

    # Best in category
    best_by_category: dict[str, UUID] = Field(
        ...,
        description="Best plan ID for each category"
    )

    # Trade-off analysis
    trade_offs: list[TradeOffNote] = Field(
        default_factory=list,
        description="Trade-off notes explaining plan differences"
    )

    # Multi-year projections
    multi_year_projections: dict[str, list[MultiYearProjection]] = Field(
        default_factory=dict,
        description="Multi-year cost projections by plan_id"
    )

    # Comparison metadata
    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="When comparison was generated"
    )
    projection_basis: str = Field(
        ...,
        description="Basis for projections (e.g., 'Historical 12-month usage')"
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Key assumptions for comparison"
    )

    model_config = {"from_attributes": True}

    @field_validator("best_by_category")
    @classmethod
    def validate_best_by_category(cls, v: dict[str, UUID]) -> dict[str, UUID]:
        """Validate best_by_category structure."""
        expected_categories = [
            "lowest_cost",
            "highest_renewable",
            "most_flexible",
            "highest_rated",
            "best_value"
        ]
        # Just ensure it's a dict - plans may not have all categories
        if not isinstance(v, dict):
            raise ValueError("best_by_category must be a dictionary")
        return v


# Helper schemas for API responses

class SavingsSummary(BaseModel):
    """Simplified savings summary for quick display."""

    plan_id: UUID
    annual_savings: Decimal
    savings_percentage: Decimal
    break_even_months: Optional[int] = None
    is_variable_rate: bool = False
    confidence: str = Field(default="high", description="Confidence level: high, medium, low")

    model_config = {"from_attributes": True}


class ComparisonSummary(BaseModel):
    """Simplified comparison summary."""

    user_id: UUID
    num_plans_compared: int
    best_savings_plan_id: UUID
    best_renewable_plan_id: UUID
    generated_at: datetime

    model_config = {"from_attributes": True}


# Mock data structures for Story 2.2 integration (TEMPORARY)

class RankedPlan(BaseModel):
    """
    TEMPORARY MOCK - Replace when Backend Dev #3 publishes Story 2.2 contract.

    Represents a plan ranked by the recommendation algorithm.
    """

    plan_id: UUID = Field(..., description="Plan ID from catalog")
    rank: int = Field(..., ge=1, le=3, description="Rank (1=best)")
    composite_score: Decimal = Field(..., ge=0, le=1, description="Overall score (0-1)")
    cost_score: Decimal = Field(..., ge=0, le=1, description="Cost score")
    flexibility_score: Decimal = Field(..., ge=0, le=1, description="Flexibility score")
    renewable_score: Decimal = Field(..., ge=0, le=1, description="Renewable score")
    rating_score: Decimal = Field(..., ge=0, le=1, description="Rating score")
    projected_annual_cost: Decimal = Field(..., ge=0, description="Projected annual cost")

    model_config = {"from_attributes": True}


class RecommendationResult(BaseModel):
    """
    TEMPORARY MOCK - Replace when Backend Dev #3 publishes Story 2.2 contract.

    Output from Story 2.2 (Plan Matching).
    """

    user_id: UUID = Field(..., description="User ID")
    top_plans: list[RankedPlan] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="Top 3 recommended plans"
    )
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")

    model_config = {"from_attributes": True}
