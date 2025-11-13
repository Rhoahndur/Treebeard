"""
Audit logging service for tracking admin actions and system events.
"""

import logging
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from models.audit_log import AuditLog
from models.user import User
from schemas.audit_schemas import (
    AuditLogCreate,
    AuditLogFilter,
    AuditLogListResponse,
    AuditLogResponse,
    AuditLogStats,
)

logger = logging.getLogger(__name__)


async def log_admin_action(
    db: AsyncSession,
    admin_user_id: UUID,
    action: str,
    resource_type: str,
    resource_id: Optional[UUID] = None,
    details: Optional[dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditLog:
    """
    Log an admin action to the audit log.

    Args:
        db: Database session
        admin_user_id: ID of the admin user performing the action
        action: Action type (e.g., 'user_role_updated', 'plan_created')
        resource_type: Type of resource affected (e.g., 'user', 'plan')
        resource_id: ID of the resource affected (optional for bulk operations)
        details: Additional action-specific details (will be sanitized)
        ip_address: IP address of the admin
        user_agent: User agent string from the request

    Returns:
        AuditLog: The created audit log entry

    Note:
        This function automatically sanitizes sensitive data from the details field.
    """
    # Sanitize details to remove sensitive information
    sanitized_details = _sanitize_details(details) if details else None

    # Create audit log entry
    audit_log = AuditLog(
        id=uuid4(),
        timestamp=datetime.utcnow(),
        admin_user_id=admin_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=sanitized_details,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.add(audit_log)
    await db.commit()
    await db.refresh(audit_log)

    logger.info(
        f"Audit log created: {action} on {resource_type}",
        extra={
            "audit_log_id": str(audit_log.id),
            "admin_user_id": str(admin_user_id),
            "action": action,
            "resource_type": resource_type,
            "resource_id": str(resource_id) if resource_id else None,
        },
    )

    return audit_log


def log_admin_action_sync(
    db: Session,
    admin_user_id: UUID,
    action: str,
    resource_type: str,
    resource_id: Optional[UUID] = None,
    details: Optional[dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditLog:
    """
    Synchronous version of log_admin_action.

    Args:
        db: Database session (synchronous)
        admin_user_id: ID of the admin user performing the action
        action: Action type
        resource_type: Type of resource affected
        resource_id: ID of the resource affected (optional)
        details: Additional action-specific details
        ip_address: IP address of the admin
        user_agent: User agent string

    Returns:
        AuditLog: The created audit log entry
    """
    sanitized_details = _sanitize_details(details) if details else None

    audit_log = AuditLog(
        id=uuid4(),
        timestamp=datetime.utcnow(),
        admin_user_id=admin_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=sanitized_details,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


async def get_audit_logs(
    db: AsyncSession,
    filters: AuditLogFilter,
) -> AuditLogListResponse:
    """
    Get audit logs with filtering and pagination.

    Args:
        db: Database session
        filters: Filter criteria

    Returns:
        AuditLogListResponse: Paginated list of audit logs
    """
    # Build query
    query = select(AuditLog).options(selectinload(AuditLog.admin_user))

    # Apply filters
    if filters.admin_user_id:
        query = query.where(AuditLog.admin_user_id == filters.admin_user_id)

    if filters.action:
        query = query.where(AuditLog.action == filters.action)

    if filters.resource_type:
        query = query.where(AuditLog.resource_type == filters.resource_type)

    if filters.resource_id:
        query = query.where(AuditLog.resource_id == filters.resource_id)

    if filters.start_date:
        query = query.where(AuditLog.timestamp >= filters.start_date)

    if filters.end_date:
        query = query.where(AuditLog.timestamp <= filters.end_date)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Order by timestamp (newest first) and apply pagination
    query = query.order_by(AuditLog.timestamp.desc())
    query = query.offset(filters.offset).limit(filters.limit)

    # Execute query
    result = await db.execute(query)
    audit_logs = result.scalars().all()

    # Convert to response schemas
    log_responses = [
        AuditLogResponse(
            id=log.id,
            timestamp=log.timestamp,
            admin_user_id=log.admin_user_id,
            admin_email=log.admin_user.email if log.admin_user else None,
            admin_name=log.admin_user.name if log.admin_user else None,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            details=log.details,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
        )
        for log in audit_logs
    ]

    return AuditLogListResponse(
        logs=log_responses,
        total=total,
        limit=filters.limit,
        offset=filters.offset,
        has_more=(filters.offset + filters.limit) < total,
    )


async def get_audit_log_by_id(
    db: AsyncSession,
    audit_log_id: UUID,
) -> Optional[AuditLog]:
    """
    Get a single audit log entry by ID.

    Args:
        db: Database session
        audit_log_id: Audit log entry ID

    Returns:
        Optional[AuditLog]: The audit log entry, or None if not found
    """
    query = select(AuditLog).options(selectinload(AuditLog.admin_user)).where(AuditLog.id == audit_log_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_audit_stats(db: AsyncSession) -> AuditLogStats:
    """
    Get audit log statistics.

    Args:
        db: Database session

    Returns:
        AuditLogStats: Audit log statistics
    """
    # Total logs
    total_query = select(func.count()).select_from(AuditLog)
    total_result = await db.execute(total_query)
    total_logs = total_result.scalar() or 0

    # Total unique admins
    admins_query = select(func.count(func.distinct(AuditLog.admin_user_id))).select_from(AuditLog)
    admins_result = await db.execute(admins_query)
    total_admins = admins_result.scalar() or 0

    # Actions by type
    actions_query = select(AuditLog.action, func.count(AuditLog.id)).group_by(AuditLog.action)
    actions_result = await db.execute(actions_query)
    actions_by_type = {row[0]: row[1] for row in actions_result.all()}

    # Recent activity (last 10 logs)
    recent_query = (
        select(AuditLog)
        .options(selectinload(AuditLog.admin_user))
        .order_by(AuditLog.timestamp.desc())
        .limit(10)
    )
    recent_result = await db.execute(recent_query)
    recent_logs = recent_result.scalars().all()

    recent_activity = [
        AuditLogResponse(
            id=log.id,
            timestamp=log.timestamp,
            admin_user_id=log.admin_user_id,
            admin_email=log.admin_user.email if log.admin_user else None,
            admin_name=log.admin_user.name if log.admin_user else None,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            details=log.details,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
        )
        for log in recent_logs
    ]

    return AuditLogStats(
        total_logs=total_logs,
        total_admins=total_admins,
        actions_by_type=actions_by_type,
        recent_activity=recent_activity,
    )


def _sanitize_details(details: dict[str, Any]) -> dict[str, Any]:
    """
    Sanitize sensitive data from audit log details.

    Removes:
    - Passwords (plain or hashed)
    - API keys and tokens
    - Credit card numbers
    - SSN and other PII

    Args:
        details: Raw details dictionary

    Returns:
        dict: Sanitized details dictionary
    """
    # List of sensitive keys to remove
    sensitive_keys = {
        "password",
        "hashed_password",
        "new_password",
        "old_password",
        "token",
        "api_key",
        "secret",
        "access_token",
        "refresh_token",
        "credit_card",
        "ssn",
        "social_security",
    }

    # Create a copy to avoid mutating the original
    sanitized = details.copy()

    # Remove sensitive keys (case-insensitive)
    for key in list(sanitized.keys()):
        if key.lower() in sensitive_keys or any(s in key.lower() for s in sensitive_keys):
            sanitized[key] = "[REDACTED]"

    return sanitized
