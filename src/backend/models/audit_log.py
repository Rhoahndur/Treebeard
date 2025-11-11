"""
Audit logging model for tracking admin actions and system events.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDPrimaryKeyMixin


class AuditLog(Base, UUIDPrimaryKeyMixin):
    """
    Audit log for tracking administrative actions and system events.

    Design Decision: Append-only table with no updates or deletes allowed.
    This ensures tamper-proof audit trail for compliance and security.

    Actions tracked:
    - user_role_updated: Admin changed user role
    - user_deleted: Admin soft deleted user account
    - user_restored: Admin restored deleted user account
    - plan_created: Admin added new plan to catalog
    - plan_updated: Admin modified plan details
    - plan_deleted: Admin soft deleted plan from catalog
    - plan_restored: Admin restored deleted plan
    - bulk_operation: Admin performed bulk actions
    - settings_updated: System settings changed
    """

    __tablename__ = "audit_logs"

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Timestamp when the action occurred"
    )

    admin_user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID of the admin user who performed the action"
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Action performed (e.g., 'user_role_updated', 'plan_created')"
    )

    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Type of resource affected (e.g., 'user', 'plan', 'settings')"
    )

    resource_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID of the resource affected (nullable for bulk operations)"
    )

    details: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Action-specific details in JSON format (e.g., old/new values)"
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="IP address of the admin who performed the action (IPv4 or IPv6)"
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User agent string from the HTTP request"
    )

    # Relationships
    admin_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[admin_user_id],
        backref="audit_logs_created"
    )

    __table_args__ = (
        # Composite indexes for efficient querying
        Index("idx_audit_logs_timestamp", "timestamp"),
        Index("idx_audit_logs_admin_user", "admin_user_id"),
        Index("idx_audit_logs_action", "action"),
        Index("idx_audit_logs_resource_type", "resource_type"),
        Index("idx_audit_logs_resource_id", "resource_id"),
        # Composite index for common query patterns
        Index("idx_audit_logs_admin_timestamp", "admin_user_id", "timestamp"),
        Index("idx_audit_logs_resource", "resource_type", "resource_id"),
        {"comment": "Audit log for tracking admin actions and system events (append-only)"}
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, action={self.action}, "
            f"resource_type={self.resource_type}, admin_user_id={self.admin_user_id})>"
        )
