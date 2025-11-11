"""
API Request/Response Schemas.
"""

from .common import ErrorResponse, MessageResponse, PaginationParams
from .recommendation_requests import (
    GenerateRecommendationRequest,
    GenerateRecommendationResponse,
)

__all__ = [
    "ErrorResponse",
    "MessageResponse",
    "PaginationParams",
    "GenerateRecommendationRequest",
    "GenerateRecommendationResponse",
]
