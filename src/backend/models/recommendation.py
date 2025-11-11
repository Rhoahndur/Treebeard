"""
Recommendation and recommendation_plans models.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDPrimaryKeyMixin


class Recommendation(Base, UUIDPrimaryKeyMixin):
    """
    Recommendation session storing the analysis context.

    Design Decision: Store usage_profile as JSONB to capture the analyzed patterns
    without duplicating the entire usage_history. This includes:
    - Seasonal patterns detected
    - User profile classification (baseline, high-user, variable)
    - Projected 12-month consumption
    - Peak/off-peak ratios

    Expires_at enables cache invalidation and re-analysis triggers.
    """

    __tablename__ = "recommendations"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the user"
    )

    usage_profile: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Analyzed usage patterns and projections used for recommendations"
    )

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Timestamp when recommendations were generated"
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Timestamp when recommendations should be refreshed"
    )

    algorithm_version: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="1.0.0",
        comment="Version of recommendation algorithm used"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="recommendations")

    recommendation_plans: Mapped[list["RecommendationPlan"]] = relationship(
        "RecommendationPlan",
        back_populates="recommendation",
        cascade="all, delete-orphan",
        order_by="RecommendationPlan.rank"
    )

    __table_args__ = (
        Index("idx_recommendations_user_generated", "user_id", "generated_at"),
        Index("idx_recommendations_expires", "expires_at"),
        {"comment": "Recommendation sessions with usage profile context"}
    )

    def __repr__(self) -> str:
        return (
            f"<Recommendation(id={self.id}, user_id={self.user_id}, "
            f"generated_at={self.generated_at})>"
        )


class RecommendationPlan(Base, UUIDPrimaryKeyMixin):
    """
    Individual plan recommendations with scoring and explanations.

    Design Decision: Store the top 3 plans per recommendation as separate rows.
    This allows:
    - Easy querying of plan details via JOIN
    - Historical tracking of what was recommended
    - Feedback linking to specific recommended plans

    Risk flags stored as JSONB to support multiple warning types:
    - high_etf: Early termination fee warning
    - low_savings: Marginal benefit warning
    - data_quality: Insufficient data warning
    - variable_rate: Rate volatility warning
    """

    __tablename__ = "recommendation_plans"

    recommendation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("recommendations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the recommendation session"
    )

    plan_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("plan_catalog.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the recommended plan"
    )

    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Rank of this plan (1=best, 2=second, 3=third)"
    )

    composite_score: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        comment="Final weighted score (0.0000-100.0000)"
    )

    cost_score: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        comment="Cost component score (0.0000-100.0000)"
    )

    flexibility_score: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        comment="Flexibility component score (0.0000-100.0000)"
    )

    renewable_score: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        comment="Renewable energy component score (0.0000-100.0000)"
    )

    rating_score: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        comment="Supplier rating component score (0.0000-100.0000)"
    )

    projected_annual_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Projected annual cost in dollars"
    )

    projected_annual_savings: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Projected annual savings vs current plan in dollars"
    )

    break_even_months: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Months to break even if switching costs apply"
    )

    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Plain-language explanation of why this plan was recommended"
    )

    risk_flags: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Risk warnings and alerts for this plan"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when this recommendation was created"
    )

    # Relationships
    recommendation: Mapped["Recommendation"] = relationship(
        "Recommendation",
        back_populates="recommendation_plans"
    )

    plan: Mapped["PlanCatalog"] = relationship("PlanCatalog", back_populates="recommendation_plans")

    feedback: Mapped[list["Feedback"]] = relationship(
        "Feedback",
        back_populates="recommended_plan"
    )

    __table_args__ = (
        # Composite index for efficient recommendation retrieval
        Index("idx_recommendation_plans_rec_rank", "recommendation_id", "rank"),
        # Support feedback queries
        Index("idx_recommendation_plans_plan", "plan_id"),
        # Ensure rank is unique within a recommendation
        Index(
            "idx_recommendation_plans_unique_rec_rank",
            "recommendation_id", "rank",
            unique=True
        ),
        {"comment": "Top 3 recommended plans per recommendation with scoring and explanations"}
    )

    def __repr__(self) -> str:
        return (
            f"<RecommendationPlan(id={self.id}, rank={self.rank}, "
            f"plan_id={self.plan_id}, score={self.composite_score})>"
        )
