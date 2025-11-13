"""
Plan Catalog Endpoints.

Browse and search available energy plans.
"""

import logging
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from models.plan import PlanCatalog
from api.auth_dependencies import DBSession, OptionalUser
from api.schemas.common import PaginatedResponse

router = APIRouter()
logger = logging.getLogger(__name__)


# Response Schemas


class PlanResponse(BaseModel):
    """Energy plan response."""

    id: str
    plan_name: str
    supplier_name: str
    plan_type: str
    contract_length_months: int
    early_termination_fee: Decimal
    renewable_percentage: Decimal
    monthly_fee: Optional[Decimal]
    is_active: bool
    rate_structure: dict


# Endpoints


@router.get(
    "/catalog",
    response_model=PaginatedResponse,
    summary="Get Plan Catalog",
    description="Get paginated list of available energy plans with optional filtering.",
)
async def get_plan_catalog(
    db: DBSession,
    user: OptionalUser,
    zip_code: Optional[str] = Query(None, description="Filter by ZIP code"),
    plan_type: Optional[str] = Query(None, description="Filter by plan type"),
    min_renewable: Optional[int] = Query(
        None, ge=0, le=100, description="Minimum renewable percentage"
    ),
    max_contract_length: Optional[int] = Query(
        None, ge=0, description="Maximum contract length (months)"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Get plan catalog with filters.

    Args:
        db: Database session
        user: Optional authenticated user
        zip_code: Filter by ZIP code
        plan_type: Filter by plan type
        min_renewable: Minimum renewable percentage
        max_contract_length: Maximum contract length
        page: Page number
        page_size: Items per page

    Returns:
        PaginatedResponse: Paginated plan list
    """
    # Build query
    query = db.query(PlanCatalog).filter(PlanCatalog.is_active == True)

    # Apply filters
    if zip_code:
        # Note: This requires a JSON query for available_regions array
        # Simplified for now - in production, use proper PostgreSQL JSON queries
        pass

    if plan_type:
        query = query.filter(PlanCatalog.plan_type == plan_type)

    if min_renewable is not None:
        query = query.filter(
            PlanCatalog.renewable_percentage >= Decimal(str(min_renewable))
        )

    if max_contract_length is not None:
        query = query.filter(
            PlanCatalog.contract_length_months <= max_contract_length
        )

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    plans = query.offset(offset).limit(page_size).all()

    # Convert to response
    items = [
        {
            "id": str(plan.id),
            "plan_name": plan.plan_name,
            "supplier_name": plan.supplier.supplier_name if plan.supplier else "Unknown",
            "plan_type": plan.plan_type,
            "contract_length_months": plan.contract_length_months,
            "early_termination_fee": plan.early_termination_fee,
            "renewable_percentage": plan.renewable_percentage,
            "monthly_fee": plan.monthly_fee,
            "is_active": plan.is_active,
            "rate_structure": plan.rate_structure or {},
        }
        for plan in plans
    ]

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )


@router.get(
    "/{plan_id}",
    response_model=PlanResponse,
    summary="Get Plan Details",
    description="Get detailed information about a specific plan.",
)
async def get_plan_details(plan_id: UUID, db: DBSession):
    """
    Get plan details.

    Args:
        plan_id: Plan ID
        db: Database session

    Returns:
        PlanResponse: Plan details

    Raises:
        HTTPException: If plan not found
    """
    plan = db.query(PlanCatalog).filter(PlanCatalog.id == plan_id).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )

    return PlanResponse(
        id=str(plan.id),
        plan_name=plan.plan_name,
        supplier_name=plan.supplier.supplier_name if plan.supplier else "Unknown",
        plan_type=plan.plan_type,
        contract_length_months=plan.contract_length_months,
        early_termination_fee=plan.early_termination_fee,
        renewable_percentage=plan.renewable_percentage,
        monthly_fee=plan.monthly_fee,
        is_active=plan.is_active,
        rate_structure=plan.rate_structure or {},
    )
