"""
Pydantic schemas for feedback-related models.

Story 8.2: Feedback API Endpoints
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Base Schemas

class FeedbackBase(BaseModel):
    """Base schema for Feedback with common fields."""

    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Rating: 1 (thumbs down) to 5 (thumbs up)"
    )
    feedback_text: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional text feedback from user"
    )
    feedback_type: str = Field(
        default="helpful",
        description="Type: helpful, not_helpful, selected, did_not_select, other"
    )

    @field_validator("feedback_text")
    @classmethod
    def validate_feedback_text_length(cls, v: Optional[str]) -> Optional[str]:
        """Ensure feedback text is within character limit."""
        if v and len(v) > 500:
            raise ValueError("Feedback text must be 500 characters or less")
        return v

    @field_validator("feedback_type")
    @classmethod
    def validate_feedback_type(cls, v: str) -> str:
        """Ensure feedback type is valid."""
        valid_types = {"helpful", "not_helpful", "selected", "did_not_select", "other"}
        if v not in valid_types:
            raise ValueError(f"Feedback type must be one of: {', '.join(valid_types)}")
        return v


# Create Schemas

class PlanFeedbackCreate(FeedbackBase):
    """Schema for creating feedback on a specific plan."""

    plan_id: UUID = Field(..., description="ID of the plan being reviewed")
    recommendation_id: Optional[UUID] = Field(
        None,
        description="Optional recommendation session ID"
    )


class RecommendationFeedbackCreate(FeedbackBase):
    """Schema for creating feedback on overall recommendation."""

    recommendation_id: UUID = Field(
        ...,
        description="ID of the recommendation session"
    )
    plan_id: Optional[UUID] = Field(
        None,
        description="Optional specific plan ID within the recommendation"
    )


# Response Schemas

class FeedbackResponse(BaseModel):
    """Schema for feedback response."""

    id: UUID
    user_id: Optional[UUID]
    recommendation_id: Optional[UUID]
    plan_id: Optional[UUID]
    rating: int
    feedback_text: Optional[str]
    feedback_type: str
    sentiment_score: Optional[Decimal]
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackSubmissionResponse(BaseModel):
    """Schema for feedback submission confirmation."""

    success: bool
    message: str
    feedback_id: UUID


# Analytics Schemas

class FeedbackStats(BaseModel):
    """Schema for aggregated feedback statistics."""

    total_feedback_count: int = Field(
        ...,
        description="Total number of feedback submissions"
    )
    average_rating: float = Field(
        ...,
        description="Average rating across all feedback"
    )
    thumbs_up_count: int = Field(
        ...,
        description="Number of positive ratings (4-5)"
    )
    thumbs_down_count: int = Field(
        ...,
        description="Number of negative ratings (1-2)"
    )
    neutral_count: int = Field(
        ...,
        description="Number of neutral ratings (3)"
    )
    text_feedback_count: int = Field(
        ...,
        description="Number of feedback submissions with text"
    )
    sentiment_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="Sentiment distribution (positive, neutral, negative)"
    )


class PlanFeedbackAggregation(BaseModel):
    """Schema for plan-level feedback aggregation."""

    plan_id: UUID
    plan_name: str
    supplier_name: str
    total_feedback: int
    average_rating: float
    thumbs_up_count: int
    thumbs_down_count: int
    most_recent_feedback: Optional[datetime]


class FeedbackTimeSeriesPoint(BaseModel):
    """Schema for time-series feedback data point."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    count: int = Field(..., description="Number of feedback submissions")
    average_rating: float = Field(..., description="Average rating for the day")


class FeedbackAnalyticsResponse(BaseModel):
    """Schema for comprehensive feedback analytics."""

    stats: FeedbackStats
    time_series: List[FeedbackTimeSeriesPoint] = Field(
        ...,
        description="Daily feedback volume for last 30 days"
    )
    top_plans: List[PlanFeedbackAggregation] = Field(
        ...,
        description="Top 10 most-reviewed plans"
    )
    recent_text_feedback: List[FeedbackResponse] = Field(
        default_factory=list,
        description="Recent feedback with text comments"
    )


class FeedbackSearchParams(BaseModel):
    """Schema for feedback search/filter parameters."""

    plan_id: Optional[UUID] = None
    min_rating: Optional[int] = Field(None, ge=1, le=5)
    max_rating: Optional[int] = Field(None, ge=1, le=5)
    has_text: Optional[bool] = None
    sentiment: Optional[str] = Field(
        None,
        description="Filter by sentiment: positive, neutral, negative"
    )
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)

    @field_validator("sentiment")
    @classmethod
    def validate_sentiment(cls, v: Optional[str]) -> Optional[str]:
        """Ensure sentiment is valid."""
        if v and v not in {"positive", "neutral", "negative"}:
            raise ValueError("Sentiment must be one of: positive, neutral, negative")
        return v


class FeedbackSearchResponse(BaseModel):
    """Schema for feedback search results."""

    results: List[FeedbackResponse]
    total_count: int
    limit: int
    offset: int
