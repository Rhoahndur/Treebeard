"""
Pydantic schemas for user-related models.
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

# User Schemas


class UserBase(BaseModel):
    """Base schema for User with common fields."""

    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    zip_code: str = Field(..., pattern=r"^\d{5}(-\d{4})?$", description="ZIP code (5 or 9 digits)")
    property_type: str = Field(..., description="Property type: residential, commercial, etc.")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    consent_given: bool = Field(default=True, description="GDPR/CCPA consent")


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    name: str | None = Field(None, min_length=1, max_length=255)
    zip_code: str | None = Field(None, pattern=r"^\d{5}(-\d{4})?$")
    property_type: str | None = None
    consent_given: bool | None = None


class UserResponse(UserBase):
    """Schema for user response with full information."""

    id: UUID
    consent_given: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# UserPreference Schemas


class UserPreferenceBase(BaseModel):
    """Base schema for UserPreference with validation."""

    cost_priority: int = Field(default=40, ge=0, le=100, description="Weight for cost consideration (0-100)")
    flexibility_priority: int = Field(default=30, ge=0, le=100, description="Weight for contract flexibility (0-100)")
    renewable_priority: int = Field(default=20, ge=0, le=100, description="Weight for renewable energy (0-100)")
    rating_priority: int = Field(default=10, ge=0, le=100, description="Weight for supplier ratings (0-100)")

    @field_validator("cost_priority", "flexibility_priority", "renewable_priority", "rating_priority")
    @classmethod
    def validate_priority_range(cls, v: int) -> int:
        """Ensure priority is within valid range."""
        if not 0 <= v <= 100:
            raise ValueError("Priority must be between 0 and 100")
        return v


class UserPreferenceCreate(UserPreferenceBase):
    """Schema for creating user preferences."""

    pass


class UserPreferenceUpdate(BaseModel):
    """Schema for updating user preferences."""

    cost_priority: int | None = Field(None, ge=0, le=100)
    flexibility_priority: int | None = Field(None, ge=0, le=100)
    renewable_priority: int | None = Field(None, ge=0, le=100)
    rating_priority: int | None = Field(None, ge=0, le=100)


class UserPreferenceResponse(UserPreferenceBase):
    """Schema for user preference response."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# CurrentPlan Schemas


class CurrentPlanBase(BaseModel):
    """Base schema for CurrentPlan."""

    supplier_name: str = Field(..., max_length=255, description="Current supplier name")
    plan_name: str | None = Field(None, max_length=255, description="Current plan name")
    current_rate: Decimal = Field(..., gt=0, description="Current rate in cents per kWh")
    contract_start_date: date | None = Field(None, description="Contract start date")
    contract_end_date: date = Field(..., description="Contract end date")
    early_termination_fee: Decimal = Field(
        default=Decimal("0.00"), ge=0, description="Early termination fee in dollars"
    )
    monthly_fee: Decimal | None = Field(None, ge=0, description="Monthly base fee")


class CurrentPlanCreate(CurrentPlanBase):
    """Schema for creating current plan information."""

    pass


class CurrentPlanUpdate(BaseModel):
    """Schema for updating current plan information."""

    supplier_name: str | None = Field(None, max_length=255)
    plan_name: str | None = Field(None, max_length=255)
    current_rate: Decimal | None = Field(None, gt=0)
    contract_start_date: date | None = None
    contract_end_date: date | None = None
    early_termination_fee: Decimal | None = Field(None, ge=0)
    monthly_fee: Decimal | None = Field(None, ge=0)


class CurrentPlanResponse(CurrentPlanBase):
    """Schema for current plan response."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Combined User Profile Schema (for convenience)


class UserProfileResponse(BaseModel):
    """Complete user profile including preferences and current plan."""

    user: UserResponse
    preferences: UserPreferenceResponse | None = None
    current_plan: CurrentPlanResponse | None = None

    model_config = {"from_attributes": True}
