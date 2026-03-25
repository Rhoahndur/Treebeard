"""
Pydantic schemas for API request/response validation and serialization.

These schemas define the contract between backend and other services,
ensuring type safety and validation at API boundaries.
"""

from .feedback import (
    FeedbackCreate,
    FeedbackResponse,
)
from .plan import (
    PlanCatalogCreate,
    PlanCatalogResponse,
    PlanCatalogSummary,
    PlanCatalogUpdate,
    RateStructure,
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)
from .recommendation import (
    PlanScores,
    RecommendationPlanResponse,
    RecommendationRequest,
    RecommendationResponse,
)

# Story 1.4 - Usage Pattern Analysis Schemas
from .usage_analysis import (
    DataQualityMetrics,
    MonthlyUsage,
    OutlierDetection,
    PeakOffPeakAnalysis,
    SeasonalAnalysis,
    SeasonalPattern,
    SeasonType,
    UsageProfile,
    UsageProjection,
    UsageStatistics,
    UserProfileType,
)
from .usage_schemas import (
    MonthlyUsageBreakdown,
    UsageHistoryBulkCreate,
    UsageHistoryCreate,
    UsageHistoryResponse,
    UsageSummary,
)
from .user import (
    CurrentPlanCreate,
    CurrentPlanResponse,
    CurrentPlanUpdate,
    UserCreate,
    UserPreferenceCreate,
    UserPreferenceResponse,
    UserPreferenceUpdate,
    UserResponse,
    UserUpdate,
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
