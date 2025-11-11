"""
Pydantic schemas for admin operations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# User Management Schemas


class UserListItem(BaseModel):
    """Schema for user list item."""

    id: UUID = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    name: str = Field(..., description="User name")
    zip_code: str = Field(..., description="User ZIP code")
    property_type: str = Field(..., description="Property type")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_admin: bool = Field(..., description="Whether the user has admin privileges")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for paginated user list response."""

    users: list[UserListItem] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users matching the filter")
    limit: int = Field(..., description="Number of results per page")
    offset: int = Field(..., description="Number of results skipped")
    has_more: bool = Field(..., description="Whether there are more results available")


class UserActivitySummary(BaseModel):
    """Schema for user activity summary."""

    total_recommendations: int = Field(..., description="Total number of recommendations generated")
    total_feedback: int = Field(..., description="Total number of feedback submissions")
    last_recommendation: Optional[datetime] = Field(None, description="Last recommendation timestamp")
    last_feedback: Optional[datetime] = Field(None, description="Last feedback timestamp")
    usage_data_points: int = Field(..., description="Number of usage data points")


class UserDetailResponse(BaseModel):
    """Schema for detailed user information."""

    id: UUID = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    name: str = Field(..., description="User name")
    zip_code: str = Field(..., description="User ZIP code")
    property_type: str = Field(..., description="Property type")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_admin: bool = Field(..., description="Whether the user has admin privileges")
    consent_given: bool = Field(..., description="Whether consent was given")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    activity: UserActivitySummary = Field(..., description="User activity summary")

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    """Schema for updating user role."""

    is_admin: bool = Field(..., description="Whether the user should have admin privileges")


# Plan Management Schemas


class PlanCatalogCreate(BaseModel):
    """Schema for creating a new plan."""

    supplier_id: UUID = Field(..., description="Supplier ID")
    plan_name: str = Field(..., min_length=1, max_length=255, description="Plan name")
    plan_type: str = Field(..., description="Plan type (fixed, variable, indexed, tiered)")
    rate_structure: dict[str, Any] = Field(..., description="Rate structure in JSON format")
    contract_length_months: int = Field(..., ge=0, description="Contract length in months (0 for month-to-month)")
    early_termination_fee: Decimal = Field(Decimal("0.00"), ge=0, description="Early termination fee in dollars")
    renewable_percentage: Decimal = Field(Decimal("0.00"), ge=0, le=100, description="Renewable energy percentage")
    monthly_fee: Optional[Decimal] = Field(None, ge=0, description="Monthly base fee in dollars")
    connection_fee: Optional[Decimal] = Field(None, ge=0, description="One-time connection fee in dollars")
    available_regions: list[str] = Field(..., min_length=1, description="List of ZIP codes where plan is available")
    plan_description: Optional[str] = Field(None, description="Marketing description of the plan")
    terms_url: Optional[str] = Field(None, description="URL to full terms and conditions")

    @field_validator('plan_type')
    @classmethod
    def validate_plan_type(cls, v: str) -> str:
        """Validate plan type."""
        allowed_types = ['fixed', 'variable', 'indexed', 'tiered']
        if v.lower() not in allowed_types:
            raise ValueError(f"Plan type must be one of: {', '.join(allowed_types)}")
        return v.lower()


class PlanCatalogUpdate(BaseModel):
    """Schema for updating an existing plan."""

    plan_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Plan name")
    plan_type: Optional[str] = Field(None, description="Plan type")
    rate_structure: Optional[dict[str, Any]] = Field(None, description="Rate structure in JSON format")
    contract_length_months: Optional[int] = Field(None, ge=0, description="Contract length in months")
    early_termination_fee: Optional[Decimal] = Field(None, ge=0, description="Early termination fee in dollars")
    renewable_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Renewable energy percentage")
    monthly_fee: Optional[Decimal] = Field(None, ge=0, description="Monthly base fee in dollars")
    connection_fee: Optional[Decimal] = Field(None, ge=0, description="Connection fee in dollars")
    available_regions: Optional[list[str]] = Field(None, min_length=1, description="Available regions")
    is_active: Optional[bool] = Field(None, description="Whether the plan is active")
    plan_description: Optional[str] = Field(None, description="Plan description")
    terms_url: Optional[str] = Field(None, description="Terms URL")

    @field_validator('plan_type')
    @classmethod
    def validate_plan_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate plan type."""
        if v is None:
            return v
        allowed_types = ['fixed', 'variable', 'indexed', 'tiered']
        if v.lower() not in allowed_types:
            raise ValueError(f"Plan type must be one of: {', '.join(allowed_types)}")
        return v.lower()


class PlanCatalogResponse(BaseModel):
    """Schema for plan catalog response."""

    id: UUID = Field(..., description="Plan ID")
    supplier_id: UUID = Field(..., description="Supplier ID")
    supplier_name: str = Field(..., description="Supplier name")
    plan_name: str = Field(..., description="Plan name")
    plan_type: str = Field(..., description="Plan type")
    rate_structure: dict[str, Any] = Field(..., description="Rate structure")
    contract_length_months: int = Field(..., description="Contract length in months")
    early_termination_fee: Decimal = Field(..., description="Early termination fee")
    renewable_percentage: Decimal = Field(..., description="Renewable energy percentage")
    monthly_fee: Optional[Decimal] = Field(None, description="Monthly base fee")
    connection_fee: Optional[Decimal] = Field(None, description="Connection fee")
    available_regions: list[str] = Field(..., description="Available regions")
    is_active: bool = Field(..., description="Whether the plan is active")
    plan_description: Optional[str] = Field(None, description="Plan description")
    terms_url: Optional[str] = Field(None, description="Terms URL")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_updated: datetime = Field(..., description="Last plan details update")

    class Config:
        from_attributes = True


class PlanListResponse(BaseModel):
    """Schema for paginated plan list response."""

    plans: list[PlanCatalogResponse] = Field(..., description="List of plans")
    total: int = Field(..., description="Total number of plans matching the filter")
    limit: int = Field(..., description="Number of results per page")
    offset: int = Field(..., description="Number of results skipped")
    has_more: bool = Field(..., description="Whether there are more results available")


# Recommendation Management Schemas


class RecommendationListItem(BaseModel):
    """Schema for recommendation list item."""

    id: UUID = Field(..., description="Recommendation ID")
    user_id: UUID = Field(..., description="User ID")
    user_email: str = Field(..., description="User email")
    user_name: str = Field(..., description="User name")
    generated_at: datetime = Field(..., description="Generation timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    algorithm_version: str = Field(..., description="Algorithm version")
    plan_count: int = Field(..., description="Number of plans recommended")

    class Config:
        from_attributes = True


class RecommendationListResponse(BaseModel):
    """Schema for paginated recommendation list response."""

    recommendations: list[RecommendationListItem] = Field(..., description="List of recommendations")
    total: int = Field(..., description="Total number of recommendations matching the filter")
    limit: int = Field(..., description="Number of results per page")
    offset: int = Field(..., description="Number of results skipped")
    has_more: bool = Field(..., description="Whether there are more results available")


# System Statistics Schemas


class SystemStats(BaseModel):
    """Schema for system-wide statistics."""

    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    inactive_users: int = Field(..., description="Number of inactive users")
    admin_users: int = Field(..., description="Number of admin users")
    total_recommendations: int = Field(..., description="Total number of recommendations generated")
    total_feedback: int = Field(..., description="Total number of feedback submissions")
    avg_recommendations_per_user: float = Field(..., description="Average recommendations per user")
    total_plans: int = Field(..., description="Total number of plans in catalog")
    active_plans: int = Field(..., description="Number of active plans")
    inactive_plans: int = Field(..., description="Number of inactive plans")
    total_suppliers: int = Field(..., description="Total number of suppliers")
    cache_hit_rate: Optional[float] = Field(None, description="Cache hit rate (0-100)")
    api_response_time_p50: Optional[float] = Field(None, description="API response time P50 (ms)")
    api_response_time_p95: Optional[float] = Field(None, description="API response time P95 (ms)")
    api_response_time_p99: Optional[float] = Field(None, description="API response time P99 (ms)")


# Pagination Schemas


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""

    limit: int = Field(50, ge=1, le=100, description="Number of results per page (default 50, max 100)")
    offset: int = Field(0, ge=0, description="Number of results to skip (default 0)")

    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v: int) -> int:
        """Ensure limit is within acceptable range."""
        if v > 100:
            return 100
        return v
