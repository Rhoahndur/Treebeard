"""
Admin API endpoints for system management.

All endpoints in this module require admin privileges (RBAC enforced).
"""

import logging
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.database import get_db
from ...schemas.admin_schemas import (
    PaginationParams,
    PlanCatalogCreate,
    PlanCatalogResponse,
    PlanCatalogUpdate,
    PlanListResponse,
    RecommendationListResponse,
    SystemStats,
    UserDetailResponse,
    UserListResponse,
    UserRoleUpdate,
)
from ...schemas.audit_schemas import (
    AuditLogFilter,
    AuditLogListResponse,
    AuditLogStats,
)
from ...services.admin_service import (
    create_plan,
    get_plans,
    get_recommendations,
    get_system_stats,
    get_user_detail,
    get_users,
    soft_delete_plan,
    soft_delete_user,
    update_plan,
    update_user_role,
)
from ...services.audit_service import get_audit_logs, get_audit_stats, log_admin_action
from ..dependencies.admin import AdminUser

router = APIRouter()
logger = logging.getLogger(__name__)


# User Management Endpoints


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="List All Users",
    description="Get paginated list of all users with optional filtering by active status and admin role.",
)
async def list_users(
    admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(50, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_admin: Optional[bool] = Query(None, description="Filter by admin role"),
) -> UserListResponse:
    """
    List all users with pagination and filtering.

    Requires admin privileges.

    Args:
        admin: Current admin user
        db: Database session
        limit: Number of results per page (default 50, max 100)
        offset: Number of results to skip (default 0)
        is_active: Filter by active status (optional)
        is_admin: Filter by admin role (optional)

    Returns:
        UserListResponse: Paginated list of users
    """
    pagination = PaginationParams(limit=limit, offset=offset)
    return await get_users(db, pagination, is_active, is_admin)


@router.get(
    "/users/{user_id}",
    response_model=UserDetailResponse,
    summary="Get User Details",
    description="Get detailed information about a specific user including activity summary.",
)
async def get_user(
    user_id: UUID,
    admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserDetailResponse:
    """
    Get detailed information about a user.

    Requires admin privileges.

    Args:
        user_id: User ID
        admin: Current admin user
        db: Database session

    Returns:
        UserDetailResponse: User details with activity summary

    Raises:
        HTTPException: If user not found
    """
    user_detail = await get_user_detail(db, user_id)

    if not user_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    return user_detail


@router.put(
    "/users/{user_id}/role",
    response_model=UserDetailResponse,
    summary="Update User Role",
    description="Update a user's admin role (promote to admin or demote to regular user).",
)
async def update_role(
    user_id: UUID,
    role_update: UserRoleUpdate,
    admin: AdminUser,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserDetailResponse:
    """
    Update a user's admin role.

    Requires admin privileges.

    Args:
        user_id: User ID
        role_update: Role update data
        admin: Current admin user
        request: HTTP request (for audit logging)
        db: Database session

    Returns:
        UserDetailResponse: Updated user details

    Raises:
        HTTPException: If user not found or trying to change own role
    """
    # Prevent admin from changing their own role
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own admin role",
        )

    # Get current role before update
    user_detail = await get_user_detail(db, user_id)
    if not user_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    old_role = user_detail.is_admin

    # Update role
    updated_user = await update_user_role(db, user_id, role_update.is_admin)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # Log the action
    await log_admin_action(
        db=db,
        admin_user_id=admin.id,
        action="user_role_updated",
        resource_type="user",
        resource_id=user_id,
        details={
            "old_role": "admin" if old_role else "user",
            "new_role": "admin" if role_update.is_admin else "user",
            "user_email": user_detail.email,
        },
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    # Return updated user details
    return await get_user_detail(db, user_id)


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft Delete User",
    description="Soft delete a user account (sets is_active to False).",
)
async def delete_user(
    user_id: UUID,
    admin: AdminUser,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Soft delete a user account.

    Requires admin privileges.

    Args:
        user_id: User ID
        admin: Current admin user
        request: HTTP request (for audit logging)
        db: Database session

    Raises:
        HTTPException: If user not found or trying to delete own account
    """
    # Prevent admin from deleting their own account
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    # Get user details before deletion
    user_detail = await get_user_detail(db, user_id)
    if not user_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # Soft delete
    deleted_user = await soft_delete_user(db, user_id)

    if not deleted_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # Log the action
    await log_admin_action(
        db=db,
        admin_user_id=admin.id,
        action="user_deleted",
        resource_type="user",
        resource_id=user_id,
        details={
            "user_email": user_detail.email,
            "user_name": user_detail.name,
        },
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


# Plan Management Endpoints


@router.get(
    "/plans",
    response_model=PlanListResponse,
    summary="List All Plans",
    description="Get paginated list of all plans with optional filtering by supplier and active status.",
)
async def list_plans(
    admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(50, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    supplier_id: Optional[UUID] = Query(None, description="Filter by supplier ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
) -> PlanListResponse:
    """
    List all plans with pagination and filtering.

    Requires admin privileges.

    Args:
        admin: Current admin user
        db: Database session
        limit: Number of results per page (default 50, max 100)
        offset: Number of results to skip (default 0)
        supplier_id: Filter by supplier ID (optional)
        is_active: Filter by active status (optional)

    Returns:
        PlanListResponse: Paginated list of plans
    """
    pagination = PaginationParams(limit=limit, offset=offset)
    return await get_plans(db, pagination, supplier_id, is_active)


@router.post(
    "/plans",
    response_model=PlanCatalogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Plan",
    description="Add a new plan to the catalog.",
)
async def create_new_plan(
    plan_data: PlanCatalogCreate,
    admin: AdminUser,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlanCatalogResponse:
    """
    Create a new plan in the catalog.

    Requires admin privileges.

    Args:
        plan_data: Plan creation data
        admin: Current admin user
        request: HTTP request (for audit logging)
        db: Database session

    Returns:
        PlanCatalogResponse: Created plan

    Raises:
        HTTPException: If supplier not found or validation fails
    """
    try:
        plan = await create_plan(db, plan_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Log the action
    await log_admin_action(
        db=db,
        admin_user_id=admin.id,
        action="plan_created",
        resource_type="plan",
        resource_id=plan.id,
        details={
            "plan_name": plan.plan_name,
            "supplier_id": str(plan.supplier_id),
            "plan_type": plan.plan_type,
        },
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    # Load supplier relationship
    await db.refresh(plan, ["supplier"])

    return PlanCatalogResponse(
        id=plan.id,
        supplier_id=plan.supplier_id,
        supplier_name=plan.supplier.supplier_name,
        plan_name=plan.plan_name,
        plan_type=plan.plan_type,
        rate_structure=plan.rate_structure,
        contract_length_months=plan.contract_length_months,
        early_termination_fee=plan.early_termination_fee,
        renewable_percentage=plan.renewable_percentage,
        monthly_fee=plan.monthly_fee,
        connection_fee=plan.connection_fee,
        available_regions=plan.available_regions,
        is_active=plan.is_active,
        plan_description=plan.plan_description,
        terms_url=plan.terms_url,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        last_updated=plan.last_updated,
    )


@router.put(
    "/plans/{plan_id}",
    response_model=PlanCatalogResponse,
    summary="Update Plan",
    description="Update an existing plan's details.",
)
async def update_existing_plan(
    plan_id: UUID,
    plan_data: PlanCatalogUpdate,
    admin: AdminUser,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlanCatalogResponse:
    """
    Update an existing plan.

    Requires admin privileges.

    Args:
        plan_id: Plan ID
        plan_data: Plan update data
        admin: Current admin user
        request: HTTP request (for audit logging)
        db: Database session

    Returns:
        PlanCatalogResponse: Updated plan

    Raises:
        HTTPException: If plan not found
    """
    updated_plan = await update_plan(db, plan_id, plan_data)

    if not updated_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found",
        )

    # Log the action
    await log_admin_action(
        db=db,
        admin_user_id=admin.id,
        action="plan_updated",
        resource_type="plan",
        resource_id=plan_id,
        details={
            "plan_name": updated_plan.plan_name,
            "updated_fields": list(plan_data.model_dump(exclude_unset=True).keys()),
        },
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    # Load supplier relationship
    await db.refresh(updated_plan, ["supplier"])

    return PlanCatalogResponse(
        id=updated_plan.id,
        supplier_id=updated_plan.supplier_id,
        supplier_name=updated_plan.supplier.supplier_name,
        plan_name=updated_plan.plan_name,
        plan_type=updated_plan.plan_type,
        rate_structure=updated_plan.rate_structure,
        contract_length_months=updated_plan.contract_length_months,
        early_termination_fee=updated_plan.early_termination_fee,
        renewable_percentage=updated_plan.renewable_percentage,
        monthly_fee=updated_plan.monthly_fee,
        connection_fee=updated_plan.connection_fee,
        available_regions=updated_plan.available_regions,
        is_active=updated_plan.is_active,
        plan_description=updated_plan.plan_description,
        terms_url=updated_plan.terms_url,
        created_at=updated_plan.created_at,
        updated_at=updated_plan.updated_at,
        last_updated=updated_plan.last_updated,
    )


@router.delete(
    "/plans/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft Delete Plan",
    description="Soft delete a plan from the catalog (sets is_active to False).",
)
async def delete_plan(
    plan_id: UUID,
    admin: AdminUser,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Soft delete a plan.

    Requires admin privileges.

    Args:
        plan_id: Plan ID
        admin: Current admin user
        request: HTTP request (for audit logging)
        db: Database session

    Raises:
        HTTPException: If plan not found
    """
    deleted_plan = await soft_delete_plan(db, plan_id)

    if not deleted_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found",
        )

    # Log the action
    await log_admin_action(
        db=db,
        admin_user_id=admin.id,
        action="plan_deleted",
        resource_type="plan",
        resource_id=plan_id,
        details={
            "plan_name": deleted_plan.plan_name,
            "supplier_id": str(deleted_plan.supplier_id),
        },
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


# Recommendation Management Endpoints


@router.get(
    "/recommendations",
    response_model=RecommendationListResponse,
    summary="List All Recommendations",
    description="Get paginated list of all recommendations with optional filtering.",
)
async def list_recommendations(
    admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(50, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
) -> RecommendationListResponse:
    """
    List all recommendations with pagination and filtering.

    Requires admin privileges.

    Args:
        admin: Current admin user
        db: Database session
        limit: Number of results per page (default 50, max 100)
        offset: Number of results to skip (default 0)
        user_id: Filter by user ID (optional)
        start_date: Filter by start date (optional)
        end_date: Filter by end date (optional)

    Returns:
        RecommendationListResponse: Paginated list of recommendations
    """
    pagination = PaginationParams(limit=limit, offset=offset)
    return await get_recommendations(db, pagination, user_id, start_date, end_date)


# System Statistics Endpoint


@router.get(
    "/stats",
    response_model=SystemStats,
    summary="Get System Statistics",
    description="Get system-wide statistics dashboard data.",
)
async def get_stats(
    admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SystemStats:
    """
    Get system-wide statistics.

    Requires admin privileges.

    Args:
        admin: Current admin user
        db: Database session

    Returns:
        SystemStats: System statistics
    """
    return await get_system_stats(db)


# Audit Log Endpoints


@router.get(
    "/audit-logs",
    response_model=AuditLogListResponse,
    summary="Get Audit Logs",
    description="Get paginated list of audit logs with filtering options.",
)
async def list_audit_logs(
    admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(100, ge=1, le=500, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    admin_user_id: Optional[UUID] = Query(None, description="Filter by admin user ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[UUID] = Query(None, description="Filter by resource ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
) -> AuditLogListResponse:
    """
    Get audit logs with filtering and pagination.

    Requires admin privileges.

    Args:
        admin: Current admin user
        db: Database session
        limit: Number of results per page (default 100, max 500)
        offset: Number of results to skip (default 0)
        admin_user_id: Filter by admin user ID (optional)
        action: Filter by action type (optional)
        resource_type: Filter by resource type (optional)
        resource_id: Filter by resource ID (optional)
        start_date: Filter by start date (optional)
        end_date: Filter by end date (optional)

    Returns:
        AuditLogListResponse: Paginated list of audit logs
    """
    filters = AuditLogFilter(
        admin_user_id=admin_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )

    return await get_audit_logs(db, filters)


@router.get(
    "/audit-logs/stats",
    response_model=AuditLogStats,
    summary="Get Audit Log Statistics",
    description="Get audit log statistics including action counts and recent activity.",
)
async def get_audit_log_stats(
    admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuditLogStats:
    """
    Get audit log statistics.

    Requires admin privileges.

    Args:
        admin: Current admin user
        db: Database session

    Returns:
        AuditLogStats: Audit log statistics
    """
    return await get_audit_stats(db)
