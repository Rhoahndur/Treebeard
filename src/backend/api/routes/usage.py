"""
Usage Data Endpoints.

Upload and manage usage data.
"""

import logging
from datetime import date
from decimal import Decimal
from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from models.usage import UsageHistory
from api.auth_dependencies import CurrentUser, DBSession
from api.schemas.common import MessageResponse

router = APIRouter()
logger = logging.getLogger(__name__)


# Request/Response Schemas


class UsageDataPoint(BaseModel):
    """Single usage data point."""

    month: date = Field(..., description="Month (first day of month)")
    kwh: Decimal = Field(..., ge=0, description="kWh consumed")


class UploadUsageRequest(BaseModel):
    """Upload usage data request."""

    usage_data: List[UsageDataPoint] = Field(
        ..., min_items=1, max_items=24, description="Usage data (1-24 months)"
    )


# Endpoints


@router.post(
    "/upload",
    response_model=MessageResponse,
    summary="Upload Usage Data",
    description="Upload monthly usage data for the authenticated user.",
)
async def upload_usage(
    request: UploadUsageRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Upload usage data.

    Args:
        request: Usage data upload request
        current_user: Authenticated user
        db: Database session

    Returns:
        MessageResponse: Success message
    """
    try:
        # Delete existing usage data for these months
        months = [point.month for point in request.usage_data]
        db.query(UsageHistory).filter(
            UsageHistory.user_id == current_user.id,
            UsageHistory.usage_date.in_(months),
        ).delete(synchronize_session=False)

        # Insert new usage data
        for point in request.usage_data:
            usage = UsageHistory(
                user_id=current_user.id,
                usage_date=point.month,
                kwh_consumed=point.kwh,
                data_source="manual_upload",
            )
            db.add(usage)

        db.commit()

        logger.info(
            f"Uploaded {len(request.usage_data)} months of usage data for user {current_user.id}",
            extra={"user_id": str(current_user.id), "months": len(request.usage_data)},
        )

        return MessageResponse(
            message=f"Successfully uploaded {len(request.usage_data)} months of usage data",
            success=True,
            data={"months_uploaded": len(request.usage_data)},
        )

    except Exception as exc:
        logger.error(
            f"Failed to upload usage data: {exc}",
            exc_info=True,
            extra={"user_id": str(current_user.id)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload usage data: {str(exc)}",
        )


@router.get(
    "/history",
    response_model=List[UsageDataPoint],
    summary="Get Usage History",
    description="Get usage history for the authenticated user.",
)
async def get_usage_history(current_user: CurrentUser, db: DBSession):
    """
    Get usage history.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List[UsageDataPoint]: Usage history
    """
    usage_records = (
        db.query(UsageHistory)
        .filter(UsageHistory.user_id == current_user.id)
        .order_by(UsageHistory.usage_date.desc())
        .limit(24)  # Last 24 months
        .all()
    )

    return [
        UsageDataPoint(month=record.usage_date, kwh=record.kwh_consumed)
        for record in usage_records
    ]
