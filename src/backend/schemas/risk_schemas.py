"""
Risk Detection Schemas
Story 6.1-6.3: Risk Detection & Warning System - Epic 6

This module defines data models for risk detection, warnings, and
"stay with current plan" logic.

Author: Backend Dev #7
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# ENUMS
# ============================================================================


class RiskType(str, Enum):
    """Types of risks detected in plan recommendations."""

    HIGH_ETF = "high_etf"
    LOW_SAVINGS = "low_savings"
    DATA_QUALITY = "data_quality"
    VARIABLE_RATE_VOLATILITY = "variable_rate_volatility"
    CONTRACT_LENGTH_MISMATCH = "contract_length_mismatch"
    SUPPLIER_RELIABILITY = "supplier_reliability"
    BREAK_EVEN_TOO_LONG = "break_even_too_long"
    # Additional risk types
    NEGATIVE_SAVINGS = "negative_savings"
    HIGH_UPFRONT_COSTS = "high_upfront_costs"
    INSUFFICIENT_DATA = "insufficient_data"


class RiskSeverity(str, Enum):
    """Severity levels for risk warnings."""

    CRITICAL = "critical"  # Major issues, user should reconsider
    WARNING = "warning"  # Notable concerns, user should be aware
    INFO = "info"  # FYI items, no action needed


class RiskCategory(str, Enum):
    """Categories for grouping risk warnings."""

    COST = "cost"
    CONTRACT_TERMS = "contract_terms"
    DATA_QUALITY = "data_quality"
    SUPPLIER = "supplier"
    SAVINGS = "savings"
    FLEXIBILITY = "flexibility"


# ============================================================================
# RISK WARNING SCHEMAS
# ============================================================================


class RiskWarning(BaseModel):
    """
    Individual risk warning for a plan recommendation.

    Story 6.1: Core risk detection output.
    """

    risk_type: RiskType = Field(..., description="Type of risk detected")
    severity: RiskSeverity = Field(..., description="Severity level")
    category: RiskCategory = Field(..., description="Risk category for grouping")

    title: str = Field(..., max_length=100, description="Short risk title")
    message: str = Field(..., max_length=500, description="Detailed risk explanation")
    mitigation: Optional[str] = Field(
        None,
        max_length=300,
        description="Suggested mitigation or alternative action",
    )

    affected_plan_ids: List[UUID] = Field(
        ..., description="Plan IDs affected by this risk"
    )

    # Risk-specific data (optional structured data)
    risk_data: Optional[dict] = Field(
        None, description="Additional structured data about the risk"
    )

    detected_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this risk was detected",
    )

    model_config = {"from_attributes": True}

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: RiskSeverity) -> RiskSeverity:
        """Ensure severity is valid."""
        if not isinstance(v, RiskSeverity):
            raise ValueError(f"Invalid severity: {v}")
        return v


class RiskSummary(BaseModel):
    """
    Summary of all risks for a recommendation set.

    Story 6.1: Aggregate risk information.
    """

    total_risks: int = Field(default=0, ge=0, description="Total number of risks")
    critical_count: int = Field(default=0, ge=0, description="Number of critical risks")
    warning_count: int = Field(default=0, ge=0, description="Number of warnings")
    info_count: int = Field(default=0, ge=0, description="Number of info items")

    overall_risk_level: str = Field(
        default="low", description="Overall risk assessment: low, medium, high"
    )

    risks_by_plan: dict[str, int] = Field(
        default_factory=dict, description="Risk counts per plan_id"
    )

    model_config = {"from_attributes": True}

    @field_validator("overall_risk_level")
    @classmethod
    def validate_risk_level(cls, v: str) -> str:
        """Validate overall risk level."""
        valid_levels = ["low", "medium", "high"]
        if v not in valid_levels:
            raise ValueError(f"Risk level must be one of {valid_levels}")
        return v


# ============================================================================
# "STAY WITH CURRENT PLAN" SCHEMAS (Story 6.2)
# ============================================================================


class StayRecommendationTrigger(str, Enum):
    """Reasons for recommending staying with current plan."""

    LOW_NET_SAVINGS = "low_net_savings"  # Savings after ETF < threshold
    LONG_BREAK_EVEN = "long_break_even"  # Break-even > threshold
    CRITICAL_RISKS = "critical_risks"  # Multiple critical risks
    CURRENT_PLAN_OPTIMAL = "current_plan_optimal"  # Already in top tier
    CONTRACT_ENDING_SOON = "contract_ending_soon"  # Contract ends soon + high ETF


class StayRecommendation(BaseModel):
    """
    Analysis of whether user should stay with current plan.

    Story 6.2: "Stay with current plan" logic output.
    """

    should_stay: bool = Field(
        ..., description="Whether staying with current plan is recommended"
    )

    triggers: List[StayRecommendationTrigger] = Field(
        default_factory=list, description="Reasons for stay recommendation"
    )

    reasoning: str = Field(
        ..., max_length=500, description="Plain-language explanation"
    )

    # Supporting data
    net_annual_savings: Optional[Decimal] = Field(
        None, description="Net savings after all costs (can be negative)"
    )
    break_even_months: Optional[int] = Field(
        None, ge=0, description="Months to break even (if applicable)"
    )
    critical_risk_count: int = Field(
        default=0, ge=0, description="Number of critical risks detected"
    )

    # Current plan quality metrics
    current_plan_percentile: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Current plan ranking percentile (e.g., 90 = top 10%)",
    )
    days_until_contract_end: Optional[int] = Field(
        None, ge=0, description="Days until current contract ends"
    )

    confidence: float = Field(
        default=0.8,
        ge=0,
        le=1,
        description="Confidence in stay recommendation (0-1)",
    )

    model_config = {"from_attributes": True}


# ============================================================================
# ENHANCED RECOMMENDATION RESULT (Story 6.3)
# ============================================================================


class EnhancedRecommendationResult(BaseModel):
    """
    Enhanced recommendation result with risk warnings and stay logic.

    Story 6.3: Extends base recommendation with risk data.
    """

    recommendation_id: UUID = Field(..., description="Unique recommendation ID")
    user_id: UUID = Field(..., description="User ID")

    # Top plans (from Story 2.2)
    top_plans: List = Field(
        ..., min_length=0, max_length=3, description="Top recommended plans"
    )

    # Risk analysis (Story 6.1)
    risk_warnings: List[RiskWarning] = Field(
        default_factory=list, description="All detected risk warnings"
    )
    risk_summary: RiskSummary = Field(
        default_factory=RiskSummary, description="Aggregate risk summary"
    )
    overall_risk_level: str = Field(
        default="low", description="Overall risk level: low, medium, high"
    )

    # Stay recommendation (Story 6.2)
    should_stay: bool = Field(
        default=False, description="Whether to stay with current plan"
    )
    stay_recommendation: Optional[StayRecommendation] = Field(
        None, description="Stay recommendation details (if applicable)"
    )

    # Metadata
    generated_at: datetime = Field(
        default_factory=datetime.utcnow, description="When recommendation was generated"
    )
    total_plans_analyzed: int = Field(
        default=0, ge=0, description="Total plans considered"
    )

    # Warnings and assumptions
    warnings: List[str] = Field(
        default_factory=list, description="General warnings about the analysis"
    )
    assumptions: List[str] = Field(
        default_factory=list, description="Key assumptions made"
    )

    model_config = {"from_attributes": True}


# ============================================================================
# RISK DETECTION CONFIGURATION
# ============================================================================


class RiskDetectionConfig(BaseModel):
    """
    Configuration for risk detection thresholds.

    Allows tuning risk detection sensitivity.
    """

    # ETF thresholds
    high_etf_threshold: Decimal = Field(
        default=Decimal("150.00"), description="ETF above this triggers warning"
    )
    critical_etf_threshold: Decimal = Field(
        default=Decimal("300.00"), description="ETF above this is critical"
    )

    # Savings thresholds
    low_savings_percentage: Decimal = Field(
        default=Decimal("5.0"), description="Savings below this % triggers warning"
    )
    negative_savings_threshold: Decimal = Field(
        default=Decimal("0.0"), description="Negative savings triggers critical"
    )
    min_annual_savings: Decimal = Field(
        default=Decimal("100.00"),
        description="Minimum annual savings to consider meaningful",
    )

    # Data quality thresholds
    min_confidence_score: float = Field(
        default=0.7, description="Minimum confidence score for data quality"
    )
    min_data_completeness: float = Field(
        default=0.8, description="Minimum data completeness percentage"
    )

    # Contract thresholds
    max_acceptable_break_even: int = Field(
        default=18, description="Maximum acceptable break-even period (months)"
    )
    contract_ending_soon_days: int = Field(
        default=30, description="Days to contract end considered 'soon'"
    )

    # Supplier thresholds
    min_supplier_rating: Decimal = Field(
        default=Decimal("3.5"), description="Minimum acceptable supplier rating"
    )
    min_review_count: int = Field(
        default=10, description="Minimum reviews for reliable rating"
    )

    # Variable rate volatility
    max_variable_rate_volatility: float = Field(
        default=0.25, description="Maximum acceptable rate volatility (25%)"
    )

    # Stay recommendation thresholds
    stay_min_net_savings: Decimal = Field(
        default=Decimal("100.00"),
        description="Min annual savings after ETF to recommend switch",
    )
    stay_max_break_even: int = Field(
        default=24, description="Max break-even months to recommend switch"
    )
    stay_current_plan_percentile: float = Field(
        default=90.0, description="Percentile above which current plan is 'optimal'"
    )

    model_config = {"from_attributes": True}


# ============================================================================
# HELPER SCHEMAS
# ============================================================================


class PlanRiskAnalysis(BaseModel):
    """
    Risk analysis for a single plan.

    Helper schema for organizing risks by plan.
    """

    plan_id: UUID = Field(..., description="Plan ID")
    plan_name: str = Field(..., description="Plan name")

    risks: List[RiskWarning] = Field(
        default_factory=list, description="Risks for this plan"
    )
    risk_count: int = Field(default=0, ge=0, description="Total risk count")
    highest_severity: Optional[RiskSeverity] = Field(
        None, description="Highest severity risk for this plan"
    )

    is_recommended: bool = Field(
        default=False, description="Whether this plan is in recommendations"
    )

    model_config = {"from_attributes": True}


class RiskMetrics(BaseModel):
    """
    Metrics for risk detection performance.

    Used for monitoring and optimization.
    """

    detection_time_ms: float = Field(..., description="Time taken for risk detection")
    rules_evaluated: int = Field(..., description="Number of rules evaluated")
    risks_detected: int = Field(..., description="Total risks detected")

    plans_analyzed: int = Field(..., description="Number of plans analyzed")
    plans_flagged: int = Field(..., description="Plans with at least one risk")

    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When metrics were captured"
    )

    model_config = {"from_attributes": True}
