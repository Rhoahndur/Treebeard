"""
Usage history model for tracking energy consumption patterns.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDPrimaryKeyMixin


class UsageHistory(Base, UUIDPrimaryKeyMixin):
    """
    Energy usage history tracking.

    Design Decision: Store at daily granularity to support:
    - Seasonal pattern analysis (required by PRD)
    - Peak/off-peak usage detection
    - Flexible aggregation to monthly for basic analysis

    The PRD specifies "12 months minimum, daily preferred" - we support both.
    Data source field allows tracking whether data came from upload, API, or manual entry.
    """

    __tablename__ = "usage_history"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the user"
    )

    usage_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Date of energy usage"
    )

    kwh_consumed: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
        comment="Energy consumed in kilowatt-hours"
    )

    data_source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="upload",
        comment="Source of data: upload, api, manual"
    )

    data_quality: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Data quality flag: complete, estimated, partial"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Timestamp when the record was created"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="usage_history")

    __table_args__ = (
        # Composite index for efficient date range queries per user
        Index("idx_usage_history_user_date", "user_id", "usage_date"),
        # Prevent duplicate entries for same user/date combination
        Index("idx_usage_history_unique_user_date", "user_id", "usage_date", unique=True),
        # Support date range queries for seasonal analysis
        Index("idx_usage_history_date", "usage_date"),
        {"comment": "Daily energy usage history for pattern analysis and projections"}
    )

    def __repr__(self) -> str:
        return (
            f"<UsageHistory(user_id={self.user_id}, "
            f"date={self.usage_date}, kwh={self.kwh_consumed})>"
        )
