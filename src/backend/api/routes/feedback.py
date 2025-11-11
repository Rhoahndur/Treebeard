"""
Feedback Endpoints.

API endpoints for collecting user feedback on recommendations and plans.

Story 8.2: Feedback API Endpoints
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ...schemas.feedback_schemas import (
    FeedbackAnalyticsResponse,
    FeedbackSearchParams,
    FeedbackSearchResponse,
    FeedbackStats,
    FeedbackSubmissionResponse,
    PlanFeedbackCreate,
    RecommendationFeedbackCreate,
)
from ...services.feedback_service import FeedbackService, create_feedback_service
from ..auth_dependencies import CurrentAdminUser, DBSession, OptionalUser

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/feedback/plan",
    response_model=FeedbackSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Plan Feedback",
    description="""
    Submit feedback on a specific energy plan.

    This endpoint:
    - Accepts feedback from authenticated or anonymous users
    - Applies rate limiting (10 submissions per user per day)
    - Performs basic sentiment analysis on text feedback
    - Returns submission confirmation

    No authentication required for anonymous feedback.
    """,
)
async def submit_plan_feedback(
    request: Request,
    feedback_data: PlanFeedbackCreate,
    db: DBSession,
    current_user: OptionalUser = None,
):
    """
    Submit feedback on a specific plan.

    Args:
        request: FastAPI request object
        feedback_data: Plan feedback data
        db: Database session
        current_user: Optional authenticated user

    Returns:
        FeedbackSubmissionResponse: Submission confirmation

    Raises:
        HTTPException: If rate limit exceeded or validation fails
    """
    try:
        # Get client IP for rate limiting
        client_ip = request.client.host if request.client else "unknown"

        # Create feedback service
        feedback_service = create_feedback_service(db)

        # Check rate limit
        user_id = current_user.id if current_user else None
        if not feedback_service.check_rate_limit(user_id, client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Maximum 10 feedback submissions per day.",
            )

        # Create feedback
        feedback = feedback_service.create_feedback(
            user_id=user_id,
            recommendation_id=feedback_data.recommendation_id,
            plan_id=feedback_data.plan_id,
            rating=feedback_data.rating,
            feedback_text=feedback_data.feedback_text,
            feedback_type=feedback_data.feedback_type,
        )

        logger.info(
            f"Plan feedback submitted: plan_id={feedback_data.plan_id}, "
            f"rating={feedback_data.rating}, user_id={user_id}"
        )

        return FeedbackSubmissionResponse(
            success=True,
            message="Thank you for your feedback!",
            feedback_id=feedback.id,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to submit plan feedback: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback. Please try again later.",
        )


@router.post(
    "/feedback/recommendation",
    response_model=FeedbackSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Recommendation Feedback",
    description="""
    Submit feedback on the overall recommendation experience.

    This endpoint:
    - Accepts feedback from authenticated or anonymous users
    - Applies rate limiting (10 submissions per user per day)
    - Performs basic sentiment analysis on text feedback
    - Returns submission confirmation

    No authentication required for anonymous feedback.
    """,
)
async def submit_recommendation_feedback(
    request: Request,
    feedback_data: RecommendationFeedbackCreate,
    db: DBSession,
    current_user: OptionalUser = None,
):
    """
    Submit feedback on overall recommendation.

    Args:
        request: FastAPI request object
        feedback_data: Recommendation feedback data
        db: Database session
        current_user: Optional authenticated user

    Returns:
        FeedbackSubmissionResponse: Submission confirmation

    Raises:
        HTTPException: If rate limit exceeded or validation fails
    """
    try:
        # Get client IP for rate limiting
        client_ip = request.client.host if request.client else "unknown"

        # Create feedback service
        feedback_service = create_feedback_service(db)

        # Check rate limit
        user_id = current_user.id if current_user else None
        if not feedback_service.check_rate_limit(user_id, client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Maximum 10 feedback submissions per day.",
            )

        # Create feedback
        feedback = feedback_service.create_feedback(
            user_id=user_id,
            recommendation_id=feedback_data.recommendation_id,
            plan_id=feedback_data.plan_id,
            rating=feedback_data.rating,
            feedback_text=feedback_data.feedback_text,
            feedback_type=feedback_data.feedback_type,
        )

        logger.info(
            f"Recommendation feedback submitted: "
            f"recommendation_id={feedback_data.recommendation_id}, "
            f"rating={feedback_data.rating}, user_id={user_id}"
        )

        return FeedbackSubmissionResponse(
            success=True,
            message="Thank you for your feedback!",
            feedback_id=feedback.id,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            f"Failed to submit recommendation feedback: {exc}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback. Please try again later.",
        )


@router.get(
    "/feedback/stats",
    response_model=FeedbackStats,
    summary="Get Feedback Statistics (Admin Only)",
    description="""
    Get aggregated feedback statistics.

    Admin-only endpoint that returns:
    - Total feedback count
    - Average rating
    - Rating distribution (thumbs up/down/neutral)
    - Sentiment breakdown
    - Text feedback count

    Requires admin authentication.
    """,
)
async def get_feedback_stats(
    db: DBSession,
    current_admin: CurrentAdminUser,
):
    """
    Get aggregated feedback statistics (admin only).

    Args:
        db: Database session
        current_admin: Current admin user

    Returns:
        FeedbackStats: Aggregated statistics

    Raises:
        HTTPException: If unauthorized or error occurs
    """
    try:
        feedback_service = create_feedback_service(db)
        stats = feedback_service.get_feedback_stats()

        logger.info(
            f"Feedback stats requested by admin: {current_admin.id}",
            extra={"admin_id": str(current_admin.id)},
        )

        return stats

    except Exception as exc:
        logger.error(f"Failed to get feedback stats: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve feedback statistics.",
        )


@router.get(
    "/admin/feedback/analytics",
    response_model=FeedbackAnalyticsResponse,
    summary="Get Comprehensive Feedback Analytics (Admin Only)",
    description="""
    Get comprehensive feedback analytics including:
    - Overall statistics
    - Time-series data (last 30 days)
    - Top plans by feedback volume
    - Recent text feedback

    Requires admin authentication.
    """,
)
async def get_feedback_analytics(
    db: DBSession,
    current_admin: CurrentAdminUser,
):
    """
    Get comprehensive feedback analytics (admin only).

    Args:
        db: Database session
        current_admin: Current admin user

    Returns:
        FeedbackAnalyticsResponse: Complete analytics data

    Raises:
        HTTPException: If unauthorized or error occurs
    """
    try:
        feedback_service = create_feedback_service(db)
        analytics = feedback_service.get_analytics()

        logger.info(
            f"Feedback analytics requested by admin: {current_admin.id}",
            extra={"admin_id": str(current_admin.id)},
        )

        return analytics

    except Exception as exc:
        logger.error(f"Failed to get feedback analytics: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve feedback analytics.",
        )


@router.get(
    "/admin/feedback/search",
    response_model=FeedbackSearchResponse,
    summary="Search Feedback (Admin Only)",
    description="""
    Search and filter feedback submissions.

    Supports filtering by:
    - Plan ID
    - Rating range
    - Text presence
    - Sentiment
    - Date range
    - Pagination

    Requires admin authentication.
    """,
)
async def search_feedback(
    db: DBSession,
    current_admin: CurrentAdminUser,
    plan_id: Optional[UUID] = None,
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None,
    has_text: Optional[bool] = None,
    sentiment: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """
    Search feedback with filters (admin only).

    Args:
        db: Database session
        current_admin: Current admin user
        plan_id: Filter by plan ID
        min_rating: Minimum rating
        max_rating: Maximum rating
        has_text: Filter by text presence
        sentiment: Filter by sentiment (positive/neutral/negative)
        limit: Results per page
        offset: Pagination offset

    Returns:
        FeedbackSearchResponse: Filtered feedback results

    Raises:
        HTTPException: If unauthorized or validation fails
    """
    try:
        # Create search params
        search_params = FeedbackSearchParams(
            plan_id=plan_id,
            min_rating=min_rating,
            max_rating=max_rating,
            has_text=has_text,
            sentiment=sentiment,
            limit=limit,
            offset=offset,
        )

        feedback_service = create_feedback_service(db)
        results = feedback_service.search_feedback(search_params)

        logger.info(
            f"Feedback search performed by admin: {current_admin.id}",
            extra={
                "admin_id": str(current_admin.id),
                "filters": search_params.model_dump(exclude_none=True),
            },
        )

        return results

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to search feedback: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search feedback.",
        )


@router.get(
    "/admin/feedback/export",
    summary="Export Feedback to CSV (Admin Only)",
    description="""
    Export all feedback data to CSV format.

    Includes:
    - Feedback ID
    - User ID (anonymized if null)
    - Plan details
    - Rating and text
    - Sentiment score
    - Timestamp

    Requires admin authentication.
    """,
)
async def export_feedback_csv(
    db: DBSession,
    current_admin: CurrentAdminUser,
):
    """
    Export feedback to CSV (admin only).

    Args:
        db: Database session
        current_admin: Current admin user

    Returns:
        StreamingResponse: CSV file download

    Raises:
        HTTPException: If unauthorized or error occurs
    """
    try:
        import csv
        import io

        from fastapi.responses import StreamingResponse

        from ...models.feedback import Feedback
        from ...models.plan import Plan

        # Query all feedback with plan details
        feedbacks = (
            db.query(Feedback, Plan)
            .outerjoin(Plan, Feedback.plan_id == Plan.id)
            .order_by(Feedback.created_at.desc())
            .all()
        )

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "Feedback ID",
            "User ID",
            "Recommendation ID",
            "Plan ID",
            "Plan Name",
            "Supplier Name",
            "Rating",
            "Feedback Type",
            "Feedback Text",
            "Sentiment Score",
            "Created At",
        ])

        # Write rows
        for feedback, plan in feedbacks:
            writer.writerow([
                str(feedback.id),
                str(feedback.user_id) if feedback.user_id else "Anonymous",
                str(feedback.recommendation_id) if feedback.recommendation_id else "",
                str(feedback.plan_id) if feedback.plan_id else "",
                plan.plan_name if plan else "",
                plan.supplier_name if plan else "",
                feedback.rating,
                feedback.feedback_type,
                feedback.feedback_text or "",
                str(feedback.sentiment_score) if feedback.sentiment_score else "",
                feedback.created_at.isoformat(),
            ])

        # Prepare response
        output.seek(0)

        logger.info(
            f"Feedback CSV export by admin: {current_admin.id}",
            extra={"admin_id": str(current_admin.id), "row_count": len(feedbacks)},
        )

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=feedback_export_{current_admin.id}.csv"
            },
        )

    except Exception as exc:
        logger.error(f"Failed to export feedback CSV: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export feedback data.",
        )
