"""
Pydantic schemas for plan catalog and suppliers.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator


# Rate Structure Schemas

class FixedRateStructure(BaseModel):
    """Fixed rate structure - single rate for all usage."""

    type: str = Field(default="fixed", description="Rate type")
    rate_per_kwh: Decimal = Field(..., gt=0, description="Rate in cents per kWh")


class TieredRateStructure(BaseModel):
    """Tiered rate structure - different rates based on usage levels."""

    type: str = Field(default="tiered", description="Rate type")
    tiers: list[dict[str, Any]] = Field(
        ...,
        description="List of tiers with usage_max and rate_per_kwh"
    )


class TimeOfUseRateStructure(BaseModel):
    """Time-of-use rate structure - different rates for peak/off-peak."""

    type: str = Field(default="time_of_use", description="Rate type")
    peak_rate: Decimal = Field(..., gt=0, description="Peak rate in cents per kWh")
    off_peak_rate: Decimal = Field(..., gt=0, description="Off-peak rate in cents per kWh")
    peak_hours: list[int] = Field(..., description="List of peak hours (0-23)")


class VariableRateStructure(BaseModel):
    """Variable rate structure - base rate with adjustment factors."""

    type: str = Field(default="variable", description="Rate type")
    base_rate: Decimal = Field(..., gt=0, description="Base rate in cents per kWh")
    adjustment_formula: str = Field(..., description="Formula for rate adjustment")


# Generic rate structure (used in database as JSONB)
RateStructure = dict[str, Any]


# Supplier Schemas

class SupplierBase(BaseModel):
    """Base schema for Supplier."""

    supplier_name: str = Field(..., max_length=255, description="Supplier name")
    average_rating: Optional[Decimal] = Field(
        None,
        ge=0,
        le=5,
        description="Average rating (0.00-5.00)"
    )
    review_count: int = Field(default=0, ge=0, description="Number of reviews")
    website: Optional[HttpUrl] = Field(None, description="Supplier website URL")
    customer_service_phone: Optional[str] = Field(
        None,
        max_length=20,
        description="Customer service phone"
    )


class SupplierCreate(SupplierBase):
    """Schema for creating a supplier."""

    is_active: bool = Field(default=True, description="Whether supplier is active")


class SupplierUpdate(BaseModel):
    """Schema for updating supplier information."""

    supplier_name: Optional[str] = Field(None, max_length=255)
    average_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)
    website: Optional[HttpUrl] = None
    customer_service_phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    """Schema for supplier response."""

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# PlanCatalog Schemas

class PlanCatalogBase(BaseModel):
    """Base schema for PlanCatalog."""

    plan_name: str = Field(..., max_length=255, description="Plan name")
    plan_type: str = Field(..., description="Type: fixed, variable, indexed, tiered")
    rate_structure: RateStructure = Field(..., description="Rate structure (JSONB)")
    contract_length_months: int = Field(..., ge=0, description="Contract length (0=month-to-month)")
    early_termination_fee: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Early termination fee"
    )
    renewable_percentage: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
        description="Renewable energy percentage"
    )
    monthly_fee: Optional[Decimal] = Field(None, ge=0, description="Monthly base fee")
    connection_fee: Optional[Decimal] = Field(None, ge=0, description="Connection fee")
    available_regions: list[str] = Field(..., description="List of ZIP codes/regions")
    plan_description: Optional[str] = Field(None, description="Plan description")
    terms_url: Optional[HttpUrl] = Field(None, description="Terms and conditions URL")

    @field_validator("plan_type")
    @classmethod
    def validate_plan_type(cls, v: str) -> str:
        """Validate plan type."""
        valid_types = ["fixed", "variable", "indexed", "tiered", "time_of_use"]
        if v not in valid_types:
            raise ValueError(f"Plan type must be one of {valid_types}")
        return v

    @field_validator("rate_structure")
    @classmethod
    def validate_rate_structure(cls, v: RateStructure) -> RateStructure:
        """Validate rate structure has required fields."""
        if not isinstance(v, dict):
            raise ValueError("Rate structure must be a dictionary")
        if "type" not in v:
            raise ValueError("Rate structure must have a 'type' field")
        return v


class PlanCatalogCreate(PlanCatalogBase):
    """Schema for creating a plan."""

    supplier_id: UUID
    is_active: bool = Field(default=True, description="Whether plan is active")


class PlanCatalogUpdate(BaseModel):
    """Schema for updating plan information."""

    plan_name: Optional[str] = Field(None, max_length=255)
    plan_type: Optional[str] = None
    rate_structure: Optional[RateStructure] = None
    contract_length_months: Optional[int] = Field(None, ge=0)
    early_termination_fee: Optional[Decimal] = Field(None, ge=0)
    renewable_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    monthly_fee: Optional[Decimal] = Field(None, ge=0)
    connection_fee: Optional[Decimal] = Field(None, ge=0)
    available_regions: Optional[list[str]] = None
    is_active: Optional[bool] = None
    plan_description: Optional[str] = None
    terms_url: Optional[HttpUrl] = None


class PlanCatalogResponse(PlanCatalogBase):
    """Schema for plan catalog response with full details."""

    id: UUID
    supplier_id: UUID
    is_active: bool
    last_updated: datetime
    created_at: datetime
    updated_at: datetime

    # Include supplier information
    supplier: Optional[SupplierResponse] = None

    model_config = {"from_attributes": True}


class PlanCatalogSummary(BaseModel):
    """Simplified plan summary for list views."""

    id: UUID
    plan_name: str
    supplier_name: str
    plan_type: str
    contract_length_months: int
    renewable_percentage: Decimal
    is_active: bool

    model_config = {"from_attributes": True}


# Helper schemas for filtering

class PlanFilterParams(BaseModel):
    """Parameters for filtering plans."""

    zip_code: Optional[str] = Field(None, description="Filter by ZIP code availability")
    plan_type: Optional[str] = Field(None, description="Filter by plan type")
    max_contract_length: Optional[int] = Field(None, ge=0, description="Max contract length")
    min_renewable_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    is_active: bool = Field(default=True, description="Filter active plans only")
    supplier_id: Optional[UUID] = Field(None, description="Filter by supplier")
