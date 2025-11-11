"""
Plan catalog and supplier models.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import ARRAY, Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Supplier(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Energy suppliers/providers with ratings.

    Design Decision: Separate suppliers from plans to:
    - Avoid data duplication (one supplier, many plans)
    - Support supplier-level analytics
    - Enable easy supplier information updates
    """

    __tablename__ = "suppliers"

    supplier_name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Official name of the energy supplier"
    )

    average_rating: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
        comment="Average customer rating (0.00-5.00)"
    )

    review_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total number of customer reviews"
    )

    website: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Supplier's official website URL"
    )

    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="URL to supplier's logo image"
    )

    customer_service_phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Customer service phone number"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether supplier is currently active"
    )

    # Relationships
    plans: Mapped[list["PlanCatalog"]] = relationship(
        "PlanCatalog",
        back_populates="supplier",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_suppliers_name", "supplier_name"),
        Index("idx_suppliers_active", "is_active"),
        {"comment": "Energy suppliers with ratings and contact information"}
    )

    def __repr__(self) -> str:
        return (
            f"<Supplier(id={self.id}, name={self.supplier_name}, "
            f"rating={self.average_rating})>"
        )


class PlanCatalog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Available energy plans with all attributes needed for matching and recommendation.

    Design Decision: Use JSONB for rate_structure to support multiple rate types:
    - Fixed: single rate
    - Tiered: multiple rates based on usage levels
    - Time-of-Use (TOU): different rates for peak/off-peak
    - Variable: base rate with adjustment factors

    This provides flexibility without creating complex normalized schemas.
    The PRD mentions "different rate structures" - JSONB handles this elegantly.
    """

    __tablename__ = "plan_catalog"

    supplier_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("suppliers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the supplier"
    )

    plan_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Name of the energy plan"
    )

    plan_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Type: fixed, variable, indexed, tiered"
    )

    rate_structure: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Rate structure in JSON format (supports multiple rate types)"
    )

    contract_length_months: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="Contract length in months (0 for month-to-month)"
    )

    early_termination_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Early termination fee in dollars"
    )

    renewable_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
        index=True,
        comment="Percentage of renewable energy (0.00-100.00)"
    )

    monthly_fee: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Monthly base fee in dollars"
    )

    connection_fee: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="One-time connection/activation fee in dollars"
    )

    available_regions: Mapped[list[str]] = mapped_column(
        ARRAY(String(10)),
        nullable=False,
        comment="List of ZIP codes or regions where plan is available"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether plan is currently available"
    )

    plan_description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Marketing description of the plan"
    )

    terms_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="URL to full terms and conditions"
    )

    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
        comment="Last time plan details were updated"
    )

    # Relationships
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="plans")

    recommendation_plans: Mapped[list["RecommendationPlan"]] = relationship(
        "RecommendationPlan",
        back_populates="plan"
    )

    __table_args__ = (
        # Composite index for efficient filtering by supplier and active status
        Index("idx_plan_catalog_supplier_active", "supplier_id", "is_active"),
        # Support filtering by plan type and contract length
        Index("idx_plan_catalog_type_length", "plan_type", "contract_length_months"),
        # Support filtering by renewable percentage for green energy preferences
        Index("idx_plan_catalog_renewable", "renewable_percentage"),
        # GIN index for efficient array searches on available_regions
        Index("idx_plan_catalog_regions", "available_regions", postgresql_using="gin"),
        {"comment": "Energy plan catalog with all attributes for matching and recommendations"}
    )

    def __repr__(self) -> str:
        return (
            f"<PlanCatalog(id={self.id}, name={self.plan_name}, "
            f"type={self.plan_type}, renewable={self.renewable_percentage}%)>"
        )
