"""
Pydantic schemas for AI-generated plan explanations.

This module defines the schemas for the explanation generation service
used in Stories 2.6, 2.7, and 2.8.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PersonaType(str):
    """User persona types based on preferences."""

    BUDGET_CONSCIOUS = "budget_conscious"
    ECO_CONSCIOUS = "eco_conscious"
    FLEXIBILITY_FOCUSED = "flexibility_focused"
    BALANCED = "balanced"


class UserPreferences(BaseModel):
    """User preference priorities for plan selection."""

    cost_priority: int = Field(..., ge=0, le=100, description="Cost priority weight (0-100)")
    flexibility_priority: int = Field(..., ge=0, le=100, description="Flexibility priority weight (0-100)")
    renewable_priority: int = Field(..., ge=0, le=100, description="Renewable energy priority weight (0-100)")
    rating_priority: int = Field(..., ge=0, le=100, description="Supplier rating priority weight (0-100)")

    def get_dominant_preference(self) -> str:
        """Get the dominant preference type."""
        prefs = {
            "cost": self.cost_priority,
            "flexibility": self.flexibility_priority,
            "renewable": self.renewable_priority,
            "rating": self.rating_priority,
        }
        return max(prefs, key=prefs.get)

    def get_persona_type(self) -> str:
        """Determine user persona based on preferences."""
        if self.cost_priority > 50:
            return PersonaType.BUDGET_CONSCIOUS
        elif self.renewable_priority > 50:
            return PersonaType.ECO_CONSCIOUS
        elif self.flexibility_priority > 50:
            return PersonaType.FLEXIBILITY_FOCUSED
        else:
            return PersonaType.BALANCED


class CurrentPlan(BaseModel):
    """Current plan information for comparison."""

    plan_name: Optional[str] = Field(None, description="Current plan name")
    supplier_name: Optional[str] = Field(None, description="Current supplier")
    annual_cost: Optional[Decimal] = Field(None, description="Current annual cost")
    contract_end_date: Optional[datetime] = Field(None, description="Contract end date")
    early_termination_fee: Optional[Decimal] = Field(None, description="Early termination fee")


class RankedPlan(BaseModel):
    """Ranked plan with all necessary information for explanation generation."""

    plan_id: UUID = Field(..., description="Plan ID")
    rank: int = Field(..., ge=1, le=3, description="Rank (1-3)")
    plan_name: str = Field(..., description="Plan name")
    supplier_name: str = Field(..., description="Supplier name")
    plan_type: str = Field(..., description="Plan type (fixed, variable, etc.)")

    # Scores
    composite_score: Decimal = Field(..., description="Overall composite score (0-100)")
    cost_score: Decimal = Field(..., description="Cost score (0-100)")
    flexibility_score: Decimal = Field(..., description="Flexibility score (0-100)")
    renewable_score: Decimal = Field(..., description="Renewable score (0-100)")
    rating_score: Decimal = Field(..., description="Rating score (0-100)")

    # Financial details
    projected_annual_cost: Decimal = Field(..., description="Projected annual cost")
    projected_annual_savings: Optional[Decimal] = Field(None, description="Savings vs current plan")
    break_even_months: Optional[int] = Field(None, description="Months to break even")

    # Plan details
    contract_length_months: int = Field(..., description="Contract length (0=month-to-month)")
    early_termination_fee: Decimal = Field(..., description="Early termination fee")
    renewable_percentage: Decimal = Field(..., description="Renewable energy percentage")
    monthly_fee: Optional[Decimal] = Field(None, description="Monthly base fee")

    # Rate information
    rate_structure: dict[str, Any] = Field(..., description="Rate structure details")
    average_rate: Optional[Decimal] = Field(None, description="Average rate per kWh")

    # Risk flags
    risk_flags: Optional[dict[str, Any]] = Field(None, description="Risk warnings")


class PlanExplanation(BaseModel):
    """Complete explanation for a recommended plan."""

    plan_id: UUID = Field(..., description="Plan ID")
    explanation_text: str = Field(..., description="Main explanation (2-3 sentences)")
    key_differentiators: List[str] = Field(
        default_factory=list,
        description="Key features that make this plan stand out"
    )
    trade_offs: List[str] = Field(
        default_factory=list,
        description="Important trade-offs or compromises"
    )
    persona_type: str = Field(..., description="User persona type")
    readability_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Flesch-Kincaid readability score"
    )
    generated_via: str = Field(
        ...,
        description="Generation method: 'claude_api' or 'template'"
    )
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When explanation was generated"
    )

    model_config = {"from_attributes": True}


class ExplanationRequest(BaseModel):
    """Request to generate explanation for a plan."""

    plan: RankedPlan = Field(..., description="Plan to explain")
    user_profile: dict[str, Any] = Field(..., description="User's usage profile")
    preferences: UserPreferences = Field(..., description="User preferences")
    current_plan: Optional[CurrentPlan] = Field(None, description="Current plan for comparison")
    force_regenerate: bool = Field(
        default=False,
        description="Force regeneration even if cached"
    )


class ExplanationResponse(BaseModel):
    """Response containing generated explanation."""

    explanation: PlanExplanation = Field(..., description="Generated explanation")
    cache_hit: bool = Field(..., description="Whether result was from cache")
    generation_time_ms: float = Field(..., description="Time taken to generate (milliseconds)")


class BulkExplanationRequest(BaseModel):
    """Request to generate explanations for multiple plans."""

    plans: List[RankedPlan] = Field(..., max_length=3, description="Plans to explain (max 3)")
    user_profile: dict[str, Any] = Field(..., description="User's usage profile")
    preferences: UserPreferences = Field(..., description="User preferences")
    current_plan: Optional[CurrentPlan] = Field(None, description="Current plan for comparison")


class BulkExplanationResponse(BaseModel):
    """Response containing multiple explanations."""

    explanations: List[PlanExplanation] = Field(..., description="Generated explanations")
    total_generation_time_ms: float = Field(..., description="Total time taken (milliseconds)")
    cache_hits: int = Field(..., description="Number of cache hits")
    api_calls: int = Field(..., description="Number of API calls made")


class ExplanationMetrics(BaseModel):
    """Metrics for monitoring explanation generation."""

    total_generated: int = Field(default=0, description="Total explanations generated")
    cache_hits: int = Field(default=0, description="Number of cache hits")
    cache_misses: int = Field(default=0, description="Number of cache misses")
    api_calls: int = Field(default=0, description="Claude API calls made")
    fallback_used: int = Field(default=0, description="Fallback template usage count")
    avg_generation_time_ms: float = Field(default=0.0, description="Average generation time")
    avg_readability_score: float = Field(default=0.0, description="Average readability score")

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate as percentage."""
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total > 0 else 0.0

    @property
    def fallback_rate(self) -> float:
        """Calculate fallback usage rate as percentage."""
        total_api_attempts = self.api_calls + self.fallback_used
        return (self.fallback_used / total_api_attempts * 100) if total_api_attempts > 0 else 0.0


class CacheWarmingRequest(BaseModel):
    """Request to pre-generate explanations for popular combinations."""

    plan_ids: List[UUID] = Field(..., description="Plan IDs to warm cache for")
    personas: List[str] = Field(
        default=[
            PersonaType.BUDGET_CONSCIOUS,
            PersonaType.ECO_CONSCIOUS,
            PersonaType.FLEXIBILITY_FOCUSED,
            PersonaType.BALANCED,
        ],
        description="Personas to generate for"
    )
