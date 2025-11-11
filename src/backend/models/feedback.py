"""
User feedback model for recommendation quality tracking.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDPrimaryKeyMixin


class Feedback(Base, UUIDPrimaryKeyMixin):
    """
    User feedback on recommendations for continuous improvement.

    Design Decision: Link feedback to both user and specific recommended plan
    to enable:
    - Plan-specific feedback analysis
    - User feedback history tracking
    - Recommendation quality scoring
    - Algorithm improvement through feedback loop

    Sentiment score enables automated sentiment analysis integration.
    """

    __tablename__ = "feedback"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the user providing feedback"
    )

    recommendation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("recommendations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the recommendation session"
    )

    recommended_plan_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("recommendation_plans.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Reference to the specific recommended plan (if applicable)"
    )

    plan_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("plan_catalog.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Reference to the plan from catalog (for joins)"
    )

    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Numeric rating: 1-5 stars or thumbs up/down (1=down, 5=up)"
    )

    feedback_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Optional text feedback from user"
    )

    feedback_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type: helpful, not_helpful, selected, did_not_select, other"
    )

    sentiment_score: Mapped[Optional[Decimal]] = mapped_column(
        nullable=True,
        comment="Automated sentiment analysis score (-1.0 to 1.0)"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Timestamp when feedback was provided"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="feedback")

    recommendation: Mapped["Recommendation"] = relationship("Recommendation")

    recommended_plan: Mapped[Optional["RecommendationPlan"]] = relationship(
        "RecommendationPlan",
        back_populates="feedback"
    )

    __table_args__ = (
        # Composite index for user feedback history
        Index("idx_feedback_user_created", "user_id", "created_at"),
        # Composite index for recommendation feedback analysis
        Index("idx_feedback_recommendation", "recommendation_id", "created_at"),
        # Support plan-specific feedback aggregation
        Index("idx_feedback_plan", "plan_id"),
        # Support rating-based queries
        Index("idx_feedback_rating", "rating"),
        {"comment": "User feedback on recommendations for quality tracking and improvement"}
    )

    def __repr__(self) -> str:
        return (
            f"<Feedback(id={self.id}, user_id={self.user_id}, "
            f"rating={self.rating}, type={self.feedback_type})>"
        )
