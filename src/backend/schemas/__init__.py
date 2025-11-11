"""
Pydantic schemas for API request/response validation and serialization.

These schemas define the contract between backend and other services,
ensuring type safety and validation at API boundaries.
"""

from .user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPreferenceCreate,
    UserPreferenceUpdate,
    UserPreferenceResponse,
    CurrentPlanCreate,
    CurrentPlanUpdate,
    CurrentPlanResponse,
)
from .usage_schemas import (
    UsageHistoryCreate,
    UsageHistoryBulkCreate,
    UsageHistoryResponse,
    UsageSummary,
    MonthlyUsageBreakdown,
)
# Story 1.4 - Usage Pattern Analysis Schemas
from .usage_analysis import (
    MonthlyUsage,
    UsageProfile,
    UserProfileType,
    SeasonalAnalysis,
    SeasonalPattern,
    SeasonType,
    PeakOffPeakAnalysis,
    OutlierDetection,
    DataQualityMetrics,
    UsageProjection,
    UsageStatistics,
)
from .plan import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    PlanCatalogCreate,
    PlanCatalogUpdate,
    PlanCatalogResponse,
    PlanCatalogSummary,
    RateStructure,
)
from .recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendationPlanResponse,
    PlanScores,
)
from .feedback import (
    FeedbackCreate,
    FeedbackResponse,
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserPreferenceCreate",
    "UserPreferenceUpdate",
    "UserPreferenceResponse",
    "CurrentPlanCreate",
    "CurrentPlanUpdate",
    "CurrentPlanResponse",
    # Usage schemas
    "UsageHistoryCreate",
    "UsageHistoryBulkCreate",
    "UsageHistoryResponse",
    "UsageSummary",
    "MonthlyUsageBreakdown",
    # Story 1.4 - Usage Pattern Analysis
    "MonthlyUsage",
    "UsageProfile",
    "UserProfileType",
    "SeasonalAnalysis",
    "SeasonalPattern",
    "SeasonType",
    "PeakOffPeakAnalysis",
    "OutlierDetection",
    "DataQualityMetrics",
    "UsageProjection",
    "UsageStatistics",
    # Plan schemas
    "SupplierCreate",
    "SupplierUpdate",
    "SupplierResponse",
    "PlanCatalogCreate",
    "PlanCatalogUpdate",
    "PlanCatalogResponse",
    "PlanCatalogSummary",
    "RateStructure",
    # Recommendation schemas
    "RecommendationRequest",
    "RecommendationResponse",
    "RecommendationPlanResponse",
    "PlanScores",
    # Feedback schemas
    "FeedbackCreate",
    "FeedbackResponse",
]
