"""
Pydantic schemas for user feedback.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Feedback schemas

class FeedbackBase(BaseModel):
    """Base schema for feedback."""

    rating: int = Field(..., ge=1, le=5, description="Rating: 1-5 stars")
    feedback_text: Optional[str] = Field(None, max_length=2000, description="Optional text feedback")
    feedback_type: str = Field(..., description="Type: helpful, not_helpful, selected, did_not_select, other")

    @field_validator("feedback_type")
    @classmethod
    def validate_feedback_type(cls, v: str) -> str:
        """Validate feedback type."""
        valid_types = ["helpful", "not_helpful", "selected", "did_not_select", "other"]
        if v not in valid_types:
            raise ValueError(f"Feedback type must be one of {valid_types}")
        return v


class FeedbackCreate(FeedbackBase):
    """Schema for creating feedback."""

    recommendation_id: UUID = Field(..., description="Recommendation session ID")
    recommended_plan_id: Optional[UUID] = Field(
        None,
        description="Specific recommended plan ID (if applicable)"
    )
    plan_id: Optional[UUID] = Field(
        None,
        description="Plan from catalog (for tracking)"
    )


class FeedbackResponse(FeedbackBase):
    """Schema for feedback response."""

    id: UUID
    user_id: UUID
    recommendation_id: UUID
    recommended_plan_id: Optional[UUID] = None
    plan_id: Optional[UUID] = None
    sentiment_score: Optional[Decimal] = Field(None, description="Automated sentiment score (-1.0 to 1.0)")
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackSummary(BaseModel):
    """Aggregated feedback summary for analytics."""

    total_feedback: int = Field(..., description="Total feedback count")
    avg_rating: Decimal = Field(..., description="Average rating")
    helpful_count: int = Field(..., description="Number of 'helpful' feedback")
    not_helpful_count: int = Field(..., description="Number of 'not helpful' feedback")
    selected_count: int = Field(..., description="Number of plans selected")
    avg_sentiment: Optional[Decimal] = Field(None, description="Average sentiment score")


class PlanFeedbackSummary(BaseModel):
    """Feedback summary for a specific plan."""

    plan_id: UUID
    plan_name: str
    total_recommendations: int = Field(..., description="Times this plan was recommended")
    total_feedback: int = Field(..., description="Total feedback received")
    avg_rating: Optional[Decimal] = Field(None, description="Average rating")
    selection_rate: Decimal = Field(..., description="Percentage of times selected when recommended")
    helpful_rate: Decimal = Field(..., description="Percentage of 'helpful' feedback")
