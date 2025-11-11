"""
Pydantic schemas for usage history and analysis.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# UsageHistory Schemas

class UsageHistoryBase(BaseModel):
    """Base schema for usage history."""

    usage_date: date = Field(..., description="Date of energy usage")
    kwh_consumed: Decimal = Field(..., gt=0, description="Energy consumed in kWh")
    data_source: str = Field(
        default="upload",
        description="Source: upload, api, manual"
    )
    data_quality: Optional[str] = Field(
        None,
        description="Quality flag: complete, estimated, partial"
    )


class UsageHistoryCreate(UsageHistoryBase):
    """Schema for creating a single usage record."""
    pass


class UsageHistoryBulkCreate(BaseModel):
    """Schema for bulk creating usage records."""

    user_id: UUID
    usage_records: list[UsageHistoryCreate] = Field(
        ...,
        min_length=1,
        description="List of usage records to create"
    )

    @field_validator("usage_records")
    @classmethod
    def validate_usage_records(cls, v: list[UsageHistoryCreate]) -> list[UsageHistoryCreate]:
        """Validate that usage records are not empty."""
        if not v:
            raise ValueError("At least one usage record is required")
        return v


class UsageHistoryResponse(UsageHistoryBase):
    """Schema for usage history response."""

    id: UUID
    user_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# Usage Analysis Schemas (for Backend Dev #2)

class SeasonalPattern(BaseModel):
    """Seasonal usage pattern analysis."""

    season: str = Field(..., description="Season: winter, spring, summer, fall")
    avg_daily_kwh: Decimal = Field(..., description="Average daily kWh for season")
    total_kwh: Decimal = Field(..., description="Total kWh for season")
    percentage_of_annual: Decimal = Field(..., description="Percentage of annual usage")


class UsageStatistics(BaseModel):
    """Basic usage statistics."""

    total_kwh: Decimal = Field(..., description="Total kWh consumed")
    avg_daily_kwh: Decimal = Field(..., description="Average daily kWh")
    avg_monthly_kwh: Decimal = Field(..., description="Average monthly kWh")
    min_daily_kwh: Decimal = Field(..., description="Minimum daily kWh")
    max_daily_kwh: Decimal = Field(..., description="Maximum daily kWh")
    std_dev_kwh: Decimal = Field(..., description="Standard deviation of daily kWh")


class PeakUsageAnalysis(BaseModel):
    """Peak vs off-peak usage analysis (if time-of-use data available)."""

    peak_percentage: Optional[Decimal] = Field(None, description="Percentage of usage during peak hours")
    off_peak_percentage: Optional[Decimal] = Field(None, description="Percentage of usage during off-peak hours")
    peak_avg_kwh: Optional[Decimal] = Field(None, description="Average daily peak kWh")
    off_peak_avg_kwh: Optional[Decimal] = Field(None, description="Average daily off-peak kWh")


class DataQualityMetrics(BaseModel):
    """Data quality assessment for usage history."""

    total_days_expected: int = Field(..., description="Expected number of days")
    total_days_available: int = Field(..., description="Actual number of days with data")
    completeness_percentage: Decimal = Field(..., description="Data completeness percentage")
    missing_days: int = Field(..., description="Number of missing days")
    has_gaps: bool = Field(..., description="Whether there are gaps in data")
    quality_flag: str = Field(..., description="Overall quality: excellent, good, fair, poor")
    quality_issues: list[str] = Field(default_factory=list, description="List of quality issues")


class UsageProfile(BaseModel):
    """
    Complete usage profile for recommendation algorithm.

    This is the key contract for Backend Dev #2 (Usage Analysis Engine).
    It contains all analyzed usage patterns and projections.
    """

    user_id: UUID
    profile_type: str = Field(
        ...,
        description="User type: baseline, high_user, variable_user, seasonal_user"
    )
    analysis_period_start: date = Field(..., description="Start date of analysis period")
    analysis_period_end: date = Field(..., description="End date of analysis period")

    # Statistics
    statistics: UsageStatistics

    # Seasonal patterns
    seasonal_patterns: list[SeasonalPattern] = Field(
        default_factory=list,
        description="Seasonal usage patterns"
    )

    # Peak/off-peak (if available)
    peak_analysis: Optional[PeakUsageAnalysis] = None

    # Projections
    projected_annual_kwh: Decimal = Field(..., description="Projected 12-month consumption")
    projected_monthly_kwh: list[Decimal] = Field(
        ...,
        min_length=12,
        max_length=12,
        description="Projected kWh for next 12 months"
    )

    # Data quality
    data_quality: DataQualityMetrics

    # Additional metadata
    confidence_score: Decimal = Field(
        ...,
        ge=0,
        le=1,
        description="Confidence in projections (0.0-1.0)"
    )
    notes: list[str] = Field(default_factory=list, description="Analysis notes")

    model_config = {"from_attributes": True}


class UsageSummary(BaseModel):
    """
    Simplified usage summary for API responses.
    """

    user_id: UUID
    total_records: int
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    total_kwh: Decimal
    avg_monthly_kwh: Decimal
    data_completeness: Decimal = Field(..., description="Percentage (0-100)")

    model_config = {"from_attributes": True}


# Month-by-month breakdown for visualizations

class MonthlyUsage(BaseModel):
    """Monthly usage breakdown."""

    year: int
    month: int
    total_kwh: Decimal
    avg_daily_kwh: Decimal
    days_in_month: int
    days_with_data: int


class MonthlyUsageBreakdown(BaseModel):
    """Complete monthly breakdown for a user."""

    user_id: UUID
    monthly_data: list[MonthlyUsage] = Field(..., description="Month-by-month usage")
    total_kwh: Decimal
    avg_monthly_kwh: Decimal

    model_config = {"from_attributes": True}
