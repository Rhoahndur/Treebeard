"""
Admin service for managing users, plans, and system operations.
"""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.feedback import Feedback
from ..models.plan import PlanCatalog, Supplier
from ..models.recommendation import Recommendation, RecommendationPlan
from ..models.user import User
from ..schemas.admin_schemas import (
    PaginationParams,
    PlanCatalogCreate,
    PlanCatalogResponse,
    PlanCatalogUpdate,
    PlanListResponse,
    RecommendationListItem,
    RecommendationListResponse,
    SystemStats,
    UserActivitySummary,
    UserDetailResponse,
    UserListItem,
    UserListResponse,
)

logger = logging.getLogger(__name__)


# User Management


async def get_users(
    db: AsyncSession,
    pagination: PaginationParams,
    is_active: Optional[bool] = None,
    is_admin: Optional[bool] = None,
) -> UserListResponse:
    """
    Get paginated list of users with optional filtering.

    Args:
        db: Database session
        pagination: Pagination parameters
        is_active: Filter by active status (optional)
        is_admin: Filter by admin status (optional)

    Returns:
        UserListResponse: Paginated list of users
    """
    # Build query
    query = select(User)

    # Apply filters
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    if is_admin is not None:
        query = query.where(User.is_admin == is_admin)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Order by created_at (newest first) and apply pagination
    query = query.order_by(User.created_at.desc())
    query = query.offset(pagination.offset).limit(pagination.limit)

    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()

    # Convert to response schemas
    user_items = [
        UserListItem(
            id=user.id,
            email=user.email,
            name=user.name,
            zip_code=user.zip_code,
            property_type=user.property_type,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            last_login=None,  # TODO: Add last_login tracking if needed
        )
        for user in users
    ]

    return UserListResponse(
        users=user_items,
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
        has_more=(pagination.offset + pagination.limit) < total,
    )


async def get_user_detail(
    db: AsyncSession,
    user_id: UUID,
) -> Optional[UserDetailResponse]:
    """
    Get detailed information about a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Optional[UserDetailResponse]: User details, or None if not found
    """
    # Get user
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return None

    # Get activity summary
    # Count recommendations
    rec_count_query = select(func.count()).select_from(Recommendation).where(Recommendation.user_id == user_id)
    rec_count_result = await db.execute(rec_count_query)
    total_recommendations = rec_count_result.scalar() or 0

    # Count feedback
    feedback_count_query = select(func.count()).select_from(Feedback).where(Feedback.user_id == user_id)
    feedback_count_result = await db.execute(feedback_count_query)
    total_feedback = feedback_count_result.scalar() or 0

    # Get last recommendation
    last_rec_query = (
        select(Recommendation.generated_at)
        .where(Recommendation.user_id == user_id)
        .order_by(Recommendation.generated_at.desc())
        .limit(1)
    )
    last_rec_result = await db.execute(last_rec_query)
    last_recommendation = last_rec_result.scalar_one_or_none()

    # Get last feedback
    last_feedback_query = (
        select(Feedback.created_at)
        .where(Feedback.user_id == user_id)
        .order_by(Feedback.created_at.desc())
        .limit(1)
    )
    last_feedback_result = await db.execute(last_feedback_query)
    last_feedback = last_feedback_result.scalar_one_or_none()

    # Count usage data points
    from ..models.usage import UsageHistory
    usage_count_query = select(func.count()).select_from(UsageHistory).where(UsageHistory.user_id == user_id)
    usage_count_result = await db.execute(usage_count_query)
    usage_data_points = usage_count_result.scalar() or 0

    activity = UserActivitySummary(
        total_recommendations=total_recommendations,
        total_feedback=total_feedback,
        last_recommendation=last_recommendation,
        last_feedback=last_feedback,
        usage_data_points=usage_data_points,
    )

    return UserDetailResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        zip_code=user.zip_code,
        property_type=user.property_type,
        is_active=user.is_active,
        is_admin=user.is_admin,
        consent_given=user.consent_given,
        created_at=user.created_at,
        updated_at=user.updated_at,
        activity=activity,
    )


async def update_user_role(
    db: AsyncSession,
    user_id: UUID,
    is_admin: bool,
) -> Optional[User]:
    """
    Update a user's admin role.

    Args:
        db: Database session
        user_id: User ID
        is_admin: New admin status

    Returns:
        Optional[User]: Updated user, or None if not found
    """
    # Get user
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return None

    # Update role
    old_role = user.is_admin
    user.is_admin = is_admin
    user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    logger.info(
        f"User role updated: {user.email} (admin: {old_role} -> {is_admin})",
        extra={"user_id": str(user_id), "old_role": old_role, "new_role": is_admin},
    )

    return user


async def soft_delete_user(
    db: AsyncSession,
    user_id: UUID,
) -> Optional[User]:
    """
    Soft delete a user account.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Optional[User]: Deleted user, or None if not found
    """
    # Get user
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return None

    # Soft delete
    user.is_active = False
    user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    logger.info(
        f"User soft deleted: {user.email}",
        extra={"user_id": str(user_id)},
    )

    return user


# Plan Management


async def get_plans(
    db: AsyncSession,
    pagination: PaginationParams,
    supplier_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
) -> PlanListResponse:
    """
    Get paginated list of plans with optional filtering.

    Args:
        db: Database session
        pagination: Pagination parameters
        supplier_id: Filter by supplier ID (optional)
        is_active: Filter by active status (optional)

    Returns:
        PlanListResponse: Paginated list of plans
    """
    # Build query
    query = select(PlanCatalog).options(selectinload(PlanCatalog.supplier))

    # Apply filters
    if supplier_id is not None:
        query = query.where(PlanCatalog.supplier_id == supplier_id)

    if is_active is not None:
        query = query.where(PlanCatalog.is_active == is_active)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Order by created_at (newest first) and apply pagination
    query = query.order_by(PlanCatalog.created_at.desc())
    query = query.offset(pagination.offset).limit(pagination.limit)

    # Execute query
    result = await db.execute(query)
    plans = result.scalars().all()

    # Convert to response schemas
    plan_responses = [
        PlanCatalogResponse(
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
        for plan in plans
    ]

    return PlanListResponse(
        plans=plan_responses,
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
        has_more=(pagination.offset + pagination.limit) < total,
    )


async def create_plan(
    db: AsyncSession,
    plan_data: PlanCatalogCreate,
) -> PlanCatalog:
    """
    Create a new plan in the catalog.

    Args:
        db: Database session
        plan_data: Plan creation data

    Returns:
        PlanCatalog: Created plan
    """
    # Verify supplier exists
    supplier_query = select(Supplier).where(Supplier.id == plan_data.supplier_id)
    supplier_result = await db.execute(supplier_query)
    supplier = supplier_result.scalar_one_or_none()

    if not supplier:
        raise ValueError(f"Supplier with ID {plan_data.supplier_id} not found")

    # Create plan
    plan = PlanCatalog(
        id=uuid4(),
        supplier_id=plan_data.supplier_id,
        plan_name=plan_data.plan_name,
        plan_type=plan_data.plan_type,
        rate_structure=plan_data.rate_structure,
        contract_length_months=plan_data.contract_length_months,
        early_termination_fee=plan_data.early_termination_fee,
        renewable_percentage=plan_data.renewable_percentage,
        monthly_fee=plan_data.monthly_fee,
        connection_fee=plan_data.connection_fee,
        available_regions=plan_data.available_regions,
        is_active=True,
        plan_description=plan_data.plan_description,
        terms_url=plan_data.terms_url,
        last_updated=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(plan)
    await db.commit()
    await db.refresh(plan)

    logger.info(
        f"Plan created: {plan.plan_name}",
        extra={"plan_id": str(plan.id), "supplier_id": str(plan.supplier_id)},
    )

    return plan


async def update_plan(
    db: AsyncSession,
    plan_id: UUID,
    plan_data: PlanCatalogUpdate,
) -> Optional[PlanCatalog]:
    """
    Update an existing plan.

    Args:
        db: Database session
        plan_id: Plan ID
        plan_data: Plan update data

    Returns:
        Optional[PlanCatalog]: Updated plan, or None if not found
    """
    # Get plan
    query = select(PlanCatalog).where(PlanCatalog.id == plan_id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()

    if not plan:
        return None

    # Update fields
    update_data = plan_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)

    plan.last_updated = datetime.utcnow()
    plan.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(plan)

    logger.info(
        f"Plan updated: {plan.plan_name}",
        extra={"plan_id": str(plan_id)},
    )

    return plan


async def soft_delete_plan(
    db: AsyncSession,
    plan_id: UUID,
) -> Optional[PlanCatalog]:
    """
    Soft delete a plan.

    Args:
        db: Database session
        plan_id: Plan ID

    Returns:
        Optional[PlanCatalog]: Deleted plan, or None if not found
    """
    # Get plan
    query = select(PlanCatalog).where(PlanCatalog.id == plan_id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()

    if not plan:
        return None

    # Soft delete
    plan.is_active = False
    plan.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(plan)

    logger.info(
        f"Plan soft deleted: {plan.plan_name}",
        extra={"plan_id": str(plan_id)},
    )

    return plan


# Recommendation Management


async def get_recommendations(
    db: AsyncSession,
    pagination: PaginationParams,
    user_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> RecommendationListResponse:
    """
    Get paginated list of recommendations with optional filtering.

    Args:
        db: Database session
        pagination: Pagination parameters
        user_id: Filter by user ID (optional)
        start_date: Filter by start date (optional)
        end_date: Filter by end date (optional)

    Returns:
        RecommendationListResponse: Paginated list of recommendations
    """
    # Build query with user join
    query = select(Recommendation).options(selectinload(Recommendation.user))

    # Apply filters
    if user_id is not None:
        query = query.where(Recommendation.user_id == user_id)

    if start_date is not None:
        query = query.where(Recommendation.generated_at >= start_date)

    if end_date is not None:
        query = query.where(Recommendation.generated_at <= end_date)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Order by generated_at (newest first) and apply pagination
    query = query.order_by(Recommendation.generated_at.desc())
    query = query.offset(pagination.offset).limit(pagination.limit)

    # Execute query
    result = await db.execute(query)
    recommendations = result.scalars().all()

    # Get plan counts for each recommendation
    rec_items = []
    for rec in recommendations:
        plan_count_query = (
            select(func.count()).select_from(RecommendationPlan).where(RecommendationPlan.recommendation_id == rec.id)
        )
        plan_count_result = await db.execute(plan_count_query)
        plan_count = plan_count_result.scalar() or 0

        rec_items.append(
            RecommendationListItem(
                id=rec.id,
                user_id=rec.user_id,
                user_email=rec.user.email,
                user_name=rec.user.name,
                generated_at=rec.generated_at,
                expires_at=rec.expires_at,
                algorithm_version=rec.algorithm_version,
                plan_count=plan_count,
            )
        )

    return RecommendationListResponse(
        recommendations=rec_items,
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
        has_more=(pagination.offset + pagination.limit) < total,
    )


# System Statistics


async def get_system_stats(db: AsyncSession) -> SystemStats:
    """
    Get system-wide statistics.

    Args:
        db: Database session

    Returns:
        SystemStats: System statistics
    """
    # User statistics
    total_users_query = select(func.count()).select_from(User)
    total_users_result = await db.execute(total_users_query)
    total_users = total_users_result.scalar() or 0

    active_users_query = select(func.count()).select_from(User).where(User.is_active == True)
    active_users_result = await db.execute(active_users_query)
    active_users = active_users_result.scalar() or 0

    inactive_users = total_users - active_users

    admin_users_query = select(func.count()).select_from(User).where(User.is_admin == True)
    admin_users_result = await db.execute(admin_users_query)
    admin_users = admin_users_result.scalar() or 0

    # Recommendation statistics
    total_recommendations_query = select(func.count()).select_from(Recommendation)
    total_recommendations_result = await db.execute(total_recommendations_query)
    total_recommendations = total_recommendations_result.scalar() or 0

    avg_recommendations_per_user = (
        total_recommendations / total_users if total_users > 0 else 0.0
    )

    # Feedback statistics
    total_feedback_query = select(func.count()).select_from(Feedback)
    total_feedback_result = await db.execute(total_feedback_query)
    total_feedback = total_feedback_result.scalar() or 0

    # Plan statistics
    total_plans_query = select(func.count()).select_from(PlanCatalog)
    total_plans_result = await db.execute(total_plans_query)
    total_plans = total_plans_result.scalar() or 0

    active_plans_query = select(func.count()).select_from(PlanCatalog).where(PlanCatalog.is_active == True)
    active_plans_result = await db.execute(active_plans_query)
    active_plans = active_plans_result.scalar() or 0

    inactive_plans = total_plans - active_plans

    # Supplier statistics
    total_suppliers_query = select(func.count()).select_from(Supplier)
    total_suppliers_result = await db.execute(total_suppliers_query)
    total_suppliers = total_suppliers_result.scalar() or 0

    return SystemStats(
        total_users=total_users,
        active_users=active_users,
        inactive_users=inactive_users,
        admin_users=admin_users,
        total_recommendations=total_recommendations,
        total_feedback=total_feedback,
        avg_recommendations_per_user=avg_recommendations_per_user,
        total_plans=total_plans,
        active_plans=active_plans,
        inactive_plans=inactive_plans,
        total_suppliers=total_suppliers,
        cache_hit_rate=None,  # TODO: Implement cache metrics collection
        api_response_time_p50=None,  # TODO: Implement API metrics collection
        api_response_time_p95=None,
        api_response_time_p99=None,
    )
