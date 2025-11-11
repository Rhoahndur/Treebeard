"""
SQLAlchemy models for TreeBeard Energy Plan Recommendation System.

This module provides all database models for the application, including:
- User management (users, preferences, current plans)
- Usage tracking (usage_history)
- Plan catalog (plan_catalog, suppliers)
- Recommendations (recommendations, recommendation_plans)
- Feedback (feedback)
- Audit logging (audit_logs)
"""

from .base import Base
from .user import User, UserPreference, CurrentPlan
from .usage import UsageHistory
from .plan import PlanCatalog, Supplier
from .recommendation import Recommendation, RecommendationPlan
from .feedback import Feedback
from .audit_log import AuditLog

__all__ = [
    "Base",
    "User",
    "UserPreference",
    "CurrentPlan",
    "UsageHistory",
    "PlanCatalog",
    "Supplier",
    "Recommendation",
    "RecommendationPlan",
    "Feedback",
    "AuditLog",
]
