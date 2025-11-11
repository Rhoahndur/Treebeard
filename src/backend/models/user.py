"""
User-related models including profiles, preferences, and current plans.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    User profile table storing basic user information and consent.

    Design Decision: Store only essential user information here.
    ZIP code is critical for regional plan availability filtering.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User's email address (unique)"
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="User's full name"
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Hashed password for authentication"
    )

    zip_code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
        comment="ZIP code for regional plan availability"
    )

    property_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of property: residential, commercial, etc."
    )

    consent_given: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="GDPR/CCPA consent for data usage"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether the user account is active (soft delete support)"
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether the user has admin privileges"
    )

    # Relationships
    usage_history: Mapped[list["UsageHistory"]] = relationship(
        "UsageHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    preferences: Mapped[Optional["UserPreference"]] = relationship(
        "UserPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    current_plan: Mapped[Optional["CurrentPlan"]] = relationship(
        "CurrentPlan",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    feedback: Mapped[list["Feedback"]] = relationship(
        "Feedback",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_users_zip_code", "zip_code"),
        Index("idx_users_email", "email"),
        Index("idx_users_is_active", "is_active"),
        Index("idx_users_is_admin", "is_admin"),
        {"comment": "User profiles with basic information and consent tracking"}
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, zip_code={self.zip_code})>"


class UserPreference(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    User preferences for plan recommendation weighting.

    Design Decision: Store as integer weights (0-100) rather than percentages
    for easier calculation and validation. These weights are normalized during
    scoring to sum to 100%.

    Default weights from PRD: cost 40%, flexibility 30%, renewable 20%, rating 10%
    """

    __tablename__ = "user_preferences"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        comment="Reference to the user"
    )

    cost_priority: Mapped[int] = mapped_column(
        nullable=False,
        default=40,
        comment="Weight for cost consideration (0-100)"
    )

    flexibility_priority: Mapped[int] = mapped_column(
        nullable=False,
        default=30,
        comment="Weight for contract flexibility (0-100)"
    )

    renewable_priority: Mapped[int] = mapped_column(
        nullable=False,
        default=20,
        comment="Weight for renewable energy percentage (0-100)"
    )

    rating_priority: Mapped[int] = mapped_column(
        nullable=False,
        default=10,
        comment="Weight for supplier ratings (0-100)"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="preferences")

    __table_args__ = (
        Index("idx_user_preferences_user_id", "user_id"),
        {"comment": "User preferences for plan recommendation algorithm weighting"}
    )

    def __repr__(self) -> str:
        return (
            f"<UserPreference(user_id={self.user_id}, "
            f"cost={self.cost_priority}, flex={self.flexibility_priority}, "
            f"renewable={self.renewable_priority}, rating={self.rating_priority})>"
        )


class CurrentPlan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    User's current energy plan details.

    Design Decision: Store as separate table rather than embedding in User
    to maintain historical record and support plan changes tracking.
    ETF (Early Termination Fee) is critical for switch cost calculations.
    """

    __tablename__ = "current_plans"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        comment="Reference to the user"
    )

    supplier_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Name of current energy supplier"
    )

    plan_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Name of current plan (if available)"
    )

    current_rate: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        comment="Current rate in cents per kWh"
    )

    contract_start_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Date when current contract started"
    )

    contract_end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Date when current contract ends"
    )

    early_termination_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Early termination fee in dollars"
    )

    monthly_fee: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Monthly base fee in dollars (if applicable)"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="current_plan")

    __table_args__ = (
        Index("idx_current_plans_user_id", "user_id"),
        Index("idx_current_plans_contract_end_date", "contract_end_date"),
        {"comment": "User's current energy plan details for comparison"}
    )

    def __repr__(self) -> str:
        return (
            f"<CurrentPlan(user_id={self.user_id}, "
            f"supplier={self.supplier_name}, rate={self.current_rate})>"
        )
