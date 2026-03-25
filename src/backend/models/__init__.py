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

from .audit_log import AuditLog
from .base import Base
from .feedback import Feedback
from .plan import PlanCatalog, Supplier
from .recommendation import Recommendation, RecommendationPlan
from .usage import UsageHistory
from .user import CurrentPlan, User, UserPreference

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
