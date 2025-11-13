"""
Feedback Service.

Business logic for feedback processing, sentiment analysis, and statistics.

Story 8.2: Feedback API Endpoints
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from models.feedback import Feedback
from models.plan import PlanCatalog
from models.recommendation import RecommendationPlan
from schemas.feedback_schemas import (
    FeedbackAnalyticsResponse,
    FeedbackResponse,
    FeedbackSearchParams,
    FeedbackSearchResponse,
    FeedbackStats,
    FeedbackTimeSeriesPoint,
    PlanFeedbackAggregation,
)

logger = logging.getLogger(__name__)


class FeedbackService:
    """
    Service for feedback management and analytics.

    Handles:
    - Feedback creation and validation
    - Sentiment analysis (basic keyword detection)
    - Statistics aggregation
    - Time-series analysis
    - Plan-level feedback aggregation
    """

    # Sentiment keywords for basic sentiment analysis
    POSITIVE_KEYWORDS = {
        "great", "excellent", "love", "perfect", "amazing", "wonderful",
        "best", "fantastic", "helpful", "satisfied", "recommend", "good",
        "happy", "pleased", "awesome", "brilliant", "super"
    }

    NEGATIVE_KEYWORDS = {
        "bad", "terrible", "worst", "hate", "awful", "horrible", "poor",
        "disappointed", "frustrating", "confusing", "unclear", "expensive",
        "complicated", "difficult", "unhappy", "dissatisfied", "useless"
    }

    def __init__(self, db: Session):
        """
        Initialize feedback service.

        Args:
            db: Database session
        """
        self.db = db

    def create_feedback(
        self,
        user_id: Optional[UUID],
        recommendation_id: Optional[UUID],
        plan_id: Optional[UUID],
        rating: int,
        feedback_text: Optional[str],
        feedback_type: str,
    ) -> Feedback:
        """
        Create a new feedback record.

        Args:
            user_id: User ID (None for anonymous feedback)
            recommendation_id: Recommendation session ID
            plan_id: Plan ID
            rating: Rating 1-5
            feedback_text: Optional text feedback
            feedback_type: Type of feedback

        Returns:
            Feedback: Created feedback record

        Raises:
            ValueError: If validation fails
        """
        # Calculate sentiment score if text provided
        sentiment_score = None
        if feedback_text:
            sentiment_score = self._analyze_sentiment(feedback_text)

        # Get recommended_plan_id if available
        recommended_plan_id = None
        if recommendation_id and plan_id:
            recommended_plan = (
                self.db.query(RecommendationPlan)
                .filter(
                    and_(
                        RecommendationPlan.recommendation_id == recommendation_id,
                        RecommendationPlan.plan_id == plan_id,
                    )
                )
                .first()
            )
            if recommended_plan:
                recommended_plan_id = recommended_plan.id

        # Create feedback record
        feedback = Feedback(
            user_id=user_id,
            recommendation_id=recommendation_id,
            recommended_plan_id=recommended_plan_id,
            plan_id=plan_id,
            rating=rating,
            feedback_text=feedback_text,
            feedback_type=feedback_type,
            sentiment_score=sentiment_score,
        )

        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)

        logger.info(
            f"Created feedback: rating={rating}, type={feedback_type}, "
            f"sentiment={sentiment_score}"
        )

        return feedback

    def _analyze_sentiment(self, text: str) -> Decimal:
        """
        Analyze sentiment of feedback text using keyword detection.

        Args:
            text: Feedback text

        Returns:
            Decimal: Sentiment score from -1.0 (negative) to 1.0 (positive)
        """
        if not text:
            return Decimal("0.0")

        # Convert to lowercase for matching
        text_lower = text.lower()
        words = set(text_lower.split())

        # Count positive and negative keywords
        positive_count = sum(1 for word in words if word in self.POSITIVE_KEYWORDS)
        negative_count = sum(1 for word in words if word in self.NEGATIVE_KEYWORDS)

        # Calculate score
        total_keywords = positive_count + negative_count

        if total_keywords == 0:
            return Decimal("0.0")

        # Normalize to -1.0 to 1.0 range
        score = (positive_count - negative_count) / total_keywords
        return Decimal(str(round(score, 2)))

    def get_feedback_stats(self) -> FeedbackStats:
        """
        Get aggregated feedback statistics.

        Returns:
            FeedbackStats: Aggregated statistics
        """
        # Total count
        total_count = self.db.query(func.count(Feedback.id)).scalar() or 0

        if total_count == 0:
            return FeedbackStats(
                total_feedback_count=0,
                average_rating=0.0,
                thumbs_up_count=0,
                thumbs_down_count=0,
                neutral_count=0,
                text_feedback_count=0,
                sentiment_breakdown={"positive": 0, "neutral": 0, "negative": 0},
            )

        # Average rating
        avg_rating = self.db.query(func.avg(Feedback.rating)).scalar() or 0.0

        # Rating distribution
        thumbs_up = (
            self.db.query(func.count(Feedback.id))
            .filter(Feedback.rating >= 4)
            .scalar()
            or 0
        )

        thumbs_down = (
            self.db.query(func.count(Feedback.id))
            .filter(Feedback.rating <= 2)
            .scalar()
            or 0
        )

        neutral = (
            self.db.query(func.count(Feedback.id))
            .filter(Feedback.rating == 3)
            .scalar()
            or 0
        )

        # Text feedback count
        text_count = (
            self.db.query(func.count(Feedback.id))
            .filter(Feedback.feedback_text.isnot(None))
            .scalar()
            or 0
        )

        # Sentiment breakdown (based on sentiment_score)
        positive_sentiment = (
            self.db.query(func.count(Feedback.id))
            .filter(Feedback.sentiment_score > 0.3)
            .scalar()
            or 0
        )

        negative_sentiment = (
            self.db.query(func.count(Feedback.id))
            .filter(Feedback.sentiment_score < -0.3)
            .scalar()
            or 0
        )

        neutral_sentiment = total_count - positive_sentiment - negative_sentiment

        return FeedbackStats(
            total_feedback_count=total_count,
            average_rating=float(avg_rating),
            thumbs_up_count=thumbs_up,
            thumbs_down_count=thumbs_down,
            neutral_count=neutral,
            text_feedback_count=text_count,
            sentiment_breakdown={
                "positive": positive_sentiment,
                "neutral": neutral_sentiment,
                "negative": negative_sentiment,
            },
        )

    def get_time_series_data(self, days: int = 30) -> List[FeedbackTimeSeriesPoint]:
        """
        Get daily feedback volume for the last N days.

        Args:
            days: Number of days to include (default 30)

        Returns:
            List[FeedbackTimeSeriesPoint]: Daily feedback counts and ratings
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # Query feedback grouped by date
        results = (
            self.db.query(
                func.date(Feedback.created_at).label("date"),
                func.count(Feedback.id).label("count"),
                func.avg(Feedback.rating).label("avg_rating"),
            )
            .filter(Feedback.created_at >= start_date)
            .group_by(func.date(Feedback.created_at))
            .order_by(func.date(Feedback.created_at))
            .all()
        )

        # Fill in missing dates with zero counts
        date_map = {
            row.date.strftime("%Y-%m-%d"): FeedbackTimeSeriesPoint(
                date=row.date.strftime("%Y-%m-%d"),
                count=row.count,
                average_rating=float(row.avg_rating or 0.0),
            )
            for row in results
        }

        # Generate all dates in range
        time_series = []
        current_date = start_date.date()
        end_date = datetime.utcnow().date()

        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            if date_str in date_map:
                time_series.append(date_map[date_str])
            else:
                time_series.append(
                    FeedbackTimeSeriesPoint(
                        date=date_str, count=0, average_rating=0.0
                    )
                )
            current_date += timedelta(days=1)

        return time_series

    def get_plan_feedback_aggregation(
        self, limit: int = 10
    ) -> List[PlanFeedbackAggregation]:
        """
        Get plan-level feedback aggregation.

        Args:
            limit: Maximum number of plans to return

        Returns:
            List[PlanFeedbackAggregation]: Top plans by feedback volume
        """
        results = (
            self.db.query(
                Feedback.plan_id,
                PlanCatalog.plan_name,
                PlanCatalog.supplier_name,
                func.count(Feedback.id).label("total_feedback"),
                func.avg(Feedback.rating).label("avg_rating"),
                func.sum(func.case((Feedback.rating >= 4, 1), else_=0)).label(
                    "thumbs_up"
                ),
                func.sum(func.case((Feedback.rating <= 2, 1), else_=0)).label(
                    "thumbs_down"
                ),
                func.max(Feedback.created_at).label("most_recent"),
            )
            .join(PlanCatalog, Feedback.plan_id == PlanCatalog.id)
            .filter(Feedback.plan_id.isnot(None))
            .group_by(Feedback.plan_id, PlanCatalog.plan_name, PlanCatalog.supplier_name)
            .order_by(func.count(Feedback.id).desc())
            .limit(limit)
            .all()
        )

        return [
            PlanFeedbackAggregation(
                plan_id=row.plan_id,
                plan_name=row.plan_name,
                supplier_name=row.supplier_name,
                total_feedback=row.total_feedback,
                average_rating=float(row.avg_rating or 0.0),
                thumbs_up_count=int(row.thumbs_up or 0),
                thumbs_down_count=int(row.thumbs_down or 0),
                most_recent_feedback=row.most_recent,
            )
            for row in results
        ]

    def get_analytics(self) -> FeedbackAnalyticsResponse:
        """
        Get comprehensive feedback analytics.

        Returns:
            FeedbackAnalyticsResponse: Complete analytics data
        """
        stats = self.get_feedback_stats()
        time_series = self.get_time_series_data(days=30)
        top_plans = self.get_plan_feedback_aggregation(limit=10)

        # Get recent text feedback
        recent_feedback = (
            self.db.query(Feedback)
            .filter(Feedback.feedback_text.isnot(None))
            .order_by(Feedback.created_at.desc())
            .limit(20)
            .all()
        )

        recent_text_feedback = [
            FeedbackResponse.model_validate(fb) for fb in recent_feedback
        ]

        return FeedbackAnalyticsResponse(
            stats=stats,
            time_series=time_series,
            top_plans=top_plans,
            recent_text_feedback=recent_text_feedback,
        )

    def search_feedback(
        self, params: FeedbackSearchParams
    ) -> FeedbackSearchResponse:
        """
        Search feedback with filters.

        Args:
            params: Search parameters

        Returns:
            FeedbackSearchResponse: Filtered feedback results
        """
        query = self.db.query(Feedback)

        # Apply filters
        if params.plan_id:
            query = query.filter(Feedback.plan_id == params.plan_id)

        if params.min_rating:
            query = query.filter(Feedback.rating >= params.min_rating)

        if params.max_rating:
            query = query.filter(Feedback.rating <= params.max_rating)

        if params.has_text is not None:
            if params.has_text:
                query = query.filter(Feedback.feedback_text.isnot(None))
            else:
                query = query.filter(Feedback.feedback_text.is_(None))

        if params.sentiment:
            if params.sentiment == "positive":
                query = query.filter(Feedback.sentiment_score > 0.3)
            elif params.sentiment == "negative":
                query = query.filter(Feedback.sentiment_score < -0.3)
            elif params.sentiment == "neutral":
                query = query.filter(
                    and_(
                        Feedback.sentiment_score >= -0.3,
                        Feedback.sentiment_score <= 0.3,
                    )
                )

        if params.start_date:
            query = query.filter(Feedback.created_at >= params.start_date)

        if params.end_date:
            query = query.filter(Feedback.created_at <= params.end_date)

        # Get total count
        total_count = query.count()

        # Apply pagination
        results = (
            query.order_by(Feedback.created_at.desc())
            .offset(params.offset)
            .limit(params.limit)
            .all()
        )

        feedback_responses = [FeedbackResponse.model_validate(fb) for fb in results]

        return FeedbackSearchResponse(
            results=feedback_responses,
            total_count=total_count,
            limit=params.limit,
            offset=params.offset,
        )

    def check_rate_limit(self, user_id: Optional[UUID], ip_address: str) -> bool:
        """
        Check if user/IP has exceeded rate limit.

        Args:
            user_id: User ID (None for anonymous)
            ip_address: Client IP address

        Returns:
            bool: True if within rate limit, False if exceeded
        """
        # 10 submissions per user/IP per day
        rate_limit = 10
        start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        if user_id:
            count = (
                self.db.query(func.count(Feedback.id))
                .filter(
                    and_(
                        Feedback.user_id == user_id,
                        Feedback.created_at >= start_of_day,
                    )
                )
                .scalar()
                or 0
            )
        else:
            # For anonymous users, we can't track by IP in the feedback table
            # This would need to be handled by the rate limiting middleware
            # For now, return True (allow)
            return True

        return count < rate_limit


def create_feedback_service(db: Session) -> FeedbackService:
    """
    Factory function to create feedback service.

    Args:
        db: Database session

    Returns:
        FeedbackService: Configured feedback service
    """
    return FeedbackService(db=db)
