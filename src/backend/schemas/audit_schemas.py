"""
Pydantic schemas for audit logging.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class AuditLogBase(BaseModel):
    """Base audit log schema."""

    action: str = Field(..., description="Action performed (e.g., 'user_role_updated')")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: UUID | None = Field(None, description="ID of the resource affected")
    details: dict[str, Any] | None = Field(None, description="Action-specific details")


class AuditLogCreate(AuditLogBase):
    """Schema for creating an audit log entry."""

    admin_user_id: UUID = Field(..., description="ID of the admin who performed the action")
    ip_address: str | None = Field(None, description="IP address of the admin")
    user_agent: str | None = Field(None, description="User agent string")


class AuditLogResponse(AuditLogBase):
    """Schema for audit log responses."""

    id: UUID = Field(..., description="Audit log entry ID")
    timestamp: datetime = Field(..., description="Timestamp when the action occurred")
    admin_user_id: UUID | None = Field(None, description="ID of the admin who performed the action")
    admin_email: str | None = Field(None, description="Email of the admin who performed the action")
    admin_name: str | None = Field(None, description="Name of the admin who performed the action")
    ip_address: str | None = Field(None, description="IP address of the admin")
    user_agent: str | None = Field(None, description="User agent string")

    class Config:
        from_attributes = True


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs."""

    admin_user_id: UUID | None = Field(None, description="Filter by admin user ID")
    action: str | None = Field(None, description="Filter by action type")
    resource_type: str | None = Field(None, description="Filter by resource type")
    resource_id: UUID | None = Field(None, description="Filter by resource ID")
    start_date: datetime | None = Field(None, description="Filter by start date")
    end_date: datetime | None = Field(None, description="Filter by end date")
    limit: int = Field(100, ge=1, le=500, description="Maximum number of results (default 100, max 500)")
    offset: int = Field(0, ge=0, description="Number of results to skip (default 0)")

    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v: int) -> int:
        """Ensure limit is within acceptable range."""
        if v > 500:
            return 500
        return v


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list responses."""

    logs: list[AuditLogResponse] = Field(..., description="List of audit log entries")
    total: int = Field(..., description="Total number of audit log entries matching the filter")
    limit: int = Field(..., description="Number of results per page")
    offset: int = Field(..., description="Number of results skipped")
    has_more: bool = Field(..., description="Whether there are more results available")


class AuditLogStats(BaseModel):
    """Schema for audit log statistics."""

    total_logs: int = Field(..., description="Total number of audit log entries")
    total_admins: int = Field(..., description="Total number of unique admins who performed actions")
    actions_by_type: dict[str, int] = Field(..., description="Count of actions by type")
    recent_activity: list[AuditLogResponse] = Field(..., description="Recent audit log entries")
