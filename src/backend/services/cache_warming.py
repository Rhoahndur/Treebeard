"""
Cache Warming Service.
Story 7.1 - Epic 7: Performance Optimization

Pre-caches frequently accessed data to maximize cache hit rate:
- Popular energy plans on startup
- Common user profiles
- Background refresh of stale cache
- Pre-warming before traffic spikes

Target: >80% cache hit rate through strategic warming
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from services.cache_optimization import OptimizedCacheService, get_optimized_cache
from config.database import SessionLocal

logger = logging.getLogger(__name__)


class CacheWarmingService:
    """
    Service for pre-warming cache with frequently accessed data.

    Strategies:
    1. Startup warming: Pre-cache popular plans and common data
    2. Scheduled warming: Refresh cache periodically
    3. Predictive warming: Pre-cache based on access patterns
    4. Event-based warming: Warm cache before expected traffic spikes
    """

    def __init__(self, cache_service: Optional[OptimizedCacheService] = None):
        """
        Initialize cache warming service.

        Args:
            cache_service: Cache service instance (uses global if not provided)
        """
        self.cache = cache_service or get_optimized_cache()
        self.warming_stats = {
            "last_full_warm": None,
            "last_plan_warm": None,
            "last_profile_warm": None,
            "total_items_warmed": 0,
            "errors": 0,
        }

    async def warm_startup_cache(self):
        """
        Warm cache on application startup.

        Pre-caches:
        - Top 100 most popular plans
        - Most accessed user profiles
        - Common recommendation patterns
        """
        logger.info("Starting cache warming on startup...")
        start_time = datetime.utcnow()

        try:
            # Warm popular plans
            plan_count = await self.warm_popular_plans(limit=100)
            logger.info(f"Warmed {plan_count} popular plans")

            # Warm active user profiles
            profile_count = await self.warm_active_user_profiles(days=7, limit=50)
            logger.info(f"Warmed {profile_count} active user profiles")

            # Warm common recommendations
            rec_count = await self.warm_recent_recommendations(days=1, limit=50)
            logger.info(f"Warmed {rec_count} recent recommendations")

            # Update stats
            duration = (datetime.utcnow() - start_time).total_seconds()
            total_warmed = plan_count + profile_count + rec_count
            self.warming_stats["last_full_warm"] = datetime.utcnow()
            self.warming_stats["total_items_warmed"] += total_warmed

            logger.info(
                f"Cache warming completed in {duration:.2f}s. "
                f"Warmed {total_warmed} items total."
            )

        except Exception as e:
            logger.error(f"Error during cache warming: {e}")
            self.warming_stats["errors"] += 1

    async def warm_popular_plans(self, limit: int = 100) -> int:
        """
        Pre-cache most popular energy plans.

        Identifies popular plans by:
        - View count
        - Recommendation frequency
        - Recent activity

        Args:
            limit: Number of plans to warm

        Returns:
            Number of plans warmed
        """
        logger.info(f"Warming {limit} popular plans...")
        warmed_count = 0

        try:
            db = SessionLocal()

            # In a real implementation, this would query the actual database
            # For now, we'll create a placeholder implementation
            # that would work with the actual schema

            # Example query logic:
            # popular_plans = db.query(PlanCatalog)\
            #     .filter(PlanCatalog.is_active == True)\
            #     .order_by(desc(PlanCatalog.view_count))\
            #     .limit(limit)\
            #     .all()

            # For demonstration, we'll simulate the warming
            popular_plan_ids = self._get_popular_plan_ids(db, limit)

            for plan_id in popular_plan_ids:
                try:
                    # Pre-cache the plan data
                    plan_data = self._get_plan_data(db, plan_id)
                    if plan_data:
                        cache_key = f"plan_catalog:v1:{plan_id}"
                        self.cache.set(
                            cache_key,
                            plan_data,
                            ttl=3600,  # 1 hour
                        )
                        warmed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to warm plan {plan_id}: {e}")
                    continue

            db.close()
            self.warming_stats["last_plan_warm"] = datetime.utcnow()

        except Exception as e:
            logger.error(f"Error warming popular plans: {e}")
            self.warming_stats["errors"] += 1

        return warmed_count

    async def warm_active_user_profiles(self, days: int = 7, limit: int = 50) -> int:
        """
        Pre-cache profiles for recently active users.

        Args:
            days: Consider users active in last N days
            limit: Maximum number of profiles to warm

        Returns:
            Number of profiles warmed
        """
        logger.info(f"Warming profiles for {limit} active users...")
        warmed_count = 0

        try:
            db = SessionLocal()

            # Get recently active users
            active_user_ids = self._get_active_user_ids(db, days, limit)

            for user_id in active_user_ids:
                try:
                    # Pre-cache user profile
                    profile_data = self._get_user_profile_data(db, user_id)
                    if profile_data:
                        cache_key = f"user_profile:v1:{user_id}"
                        self.cache.set(
                            cache_key,
                            profile_data,
                            ttl=86400,  # 24 hours
                        )
                        warmed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to warm profile for user {user_id}: {e}")
                    continue

            db.close()
            self.warming_stats["last_profile_warm"] = datetime.utcnow()

        except Exception as e:
            logger.error(f"Error warming user profiles: {e}")
            self.warming_stats["errors"] += 1

        return warmed_count

    async def warm_recent_recommendations(self, days: int = 1, limit: int = 50) -> int:
        """
        Pre-cache recent recommendations that might be re-accessed.

        Args:
            days: Cache recommendations from last N days
            limit: Maximum number of recommendations to warm

        Returns:
            Number of recommendations warmed
        """
        logger.info(f"Warming {limit} recent recommendations...")
        warmed_count = 0

        try:
            db = SessionLocal()

            # Get recent recommendation IDs
            recent_rec_ids = self._get_recent_recommendation_ids(db, days, limit)

            for rec_id in recent_rec_ids:
                try:
                    # Pre-cache recommendation
                    rec_data = self._get_recommendation_data(db, rec_id)
                    if rec_data:
                        cache_key = f"recommendations:v1:{rec_data['user_id']}"
                        self.cache.set(
                            cache_key,
                            rec_data,
                            ttl=86400,  # 24 hours
                        )
                        warmed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to warm recommendation {rec_id}: {e}")
                    continue

            db.close()

        except Exception as e:
            logger.error(f"Error warming recommendations: {e}")
            self.warming_stats["errors"] += 1

        return warmed_count

    async def refresh_expiring_cache(self, threshold_seconds: int = 300):
        """
        Background job to refresh cache entries that are about to expire.

        Args:
            threshold_seconds: Refresh cache if TTL < this value (default 5 min)
        """
        logger.info("Refreshing expiring cache entries...")
        refreshed_count = 0

        try:
            # This would scan for keys with low TTL and refresh them
            # Implementation depends on tracking which keys need refresh
            # For now, we'll log the capability

            logger.info(f"Cache refresh completed. Refreshed {refreshed_count} entries.")

        except Exception as e:
            logger.error(f"Error refreshing cache: {e}")
            self.warming_stats["errors"] += 1

    async def schedule_periodic_warming(self, interval_minutes: int = 60):
        """
        Schedule periodic cache warming.

        Args:
            interval_minutes: Interval between warming cycles
        """
        logger.info(f"Starting periodic cache warming (every {interval_minutes} minutes)")

        while True:
            try:
                await asyncio.sleep(interval_minutes * 60)
                await self.warm_popular_plans(limit=50)
                logger.info("Periodic cache warming completed")
            except Exception as e:
                logger.error(f"Error in periodic warming: {e}")
                self.warming_stats["errors"] += 1

    def get_warming_stats(self) -> Dict[str, Any]:
        """
        Get cache warming statistics.

        Returns:
            Dictionary with warming statistics
        """
        return {
            "last_full_warm": self.warming_stats["last_full_warm"].isoformat()
            if self.warming_stats["last_full_warm"]
            else None,
            "last_plan_warm": self.warming_stats["last_plan_warm"].isoformat()
            if self.warming_stats["last_plan_warm"]
            else None,
            "last_profile_warm": self.warming_stats["last_profile_warm"].isoformat()
            if self.warming_stats["last_profile_warm"]
            else None,
            "total_items_warmed": self.warming_stats["total_items_warmed"],
            "errors": self.warming_stats["errors"],
        }

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    def _get_popular_plan_ids(self, db: Session, limit: int) -> List[str]:
        """
        Get IDs of most popular plans.

        Args:
            db: Database session
            limit: Number of IDs to return

        Returns:
            List of plan IDs
        """
        # Placeholder implementation
        # In production, this would query actual database tables
        # Example:
        # return [str(row.id) for row in db.query(PlanCatalog.id)
        #         .filter(PlanCatalog.is_active == True)
        #         .order_by(desc(PlanCatalog.view_count))
        #         .limit(limit).all()]

        # For demonstration, return placeholder IDs
        return [f"plan_{i}" for i in range(min(limit, 10))]

    def _get_plan_data(self, db: Session, plan_id: str) -> Optional[str]:
        """
        Get plan data for caching.

        Args:
            db: Database session
            plan_id: Plan identifier

        Returns:
            Serialized plan data
        """
        # Placeholder - would fetch actual plan from database
        # and serialize to JSON
        import json

        return json.dumps({
            "id": plan_id,
            "name": f"Sample Plan {plan_id}",
            "cached_at": datetime.utcnow().isoformat(),
        })

    def _get_active_user_ids(
        self, db: Session, days: int, limit: int
    ) -> List[str]:
        """
        Get IDs of recently active users.

        Args:
            db: Database session
            days: Activity within last N days
            limit: Number of IDs to return

        Returns:
            List of user IDs
        """
        # Placeholder implementation
        # In production:
        # cutoff_date = datetime.utcnow() - timedelta(days=days)
        # return [str(row.user_id) for row in db.query(User.id)
        #         .filter(User.last_login > cutoff_date)
        #         .order_by(desc(User.last_login))
        #         .limit(limit).all()]

        return [f"user_{i}" for i in range(min(limit, 10))]

    def _get_user_profile_data(self, db: Session, user_id: str) -> Optional[str]:
        """
        Get user profile data for caching.

        Args:
            db: Database session
            user_id: User identifier

        Returns:
            Serialized profile data
        """
        # Placeholder
        import json

        return json.dumps({
            "user_id": user_id,
            "profile": "active",
            "cached_at": datetime.utcnow().isoformat(),
        })

    def _get_recent_recommendation_ids(
        self, db: Session, days: int, limit: int
    ) -> List[str]:
        """
        Get IDs of recent recommendations.

        Args:
            db: Database session
            days: Recommendations from last N days
            limit: Number of IDs to return

        Returns:
            List of recommendation IDs
        """
        # Placeholder implementation
        return [f"rec_{i}" for i in range(min(limit, 10))]

    def _get_recommendation_data(self, db: Session, rec_id: str) -> Optional[Dict]:
        """
        Get recommendation data for caching.

        Args:
            db: Database session
            rec_id: Recommendation identifier

        Returns:
            Recommendation data dictionary
        """
        # Placeholder
        return {
            "id": rec_id,
            "user_id": f"user_for_{rec_id}",
            "plans": [],
            "cached_at": datetime.utcnow().isoformat(),
        }


# Singleton instance
_cache_warming_instance: Optional[CacheWarmingService] = None


def get_cache_warming_service() -> CacheWarmingService:
    """
    Get the global cache warming service instance.

    Returns:
        CacheWarmingService instance
    """
    global _cache_warming_instance
    if _cache_warming_instance is None:
        _cache_warming_instance = CacheWarmingService()
    return _cache_warming_instance
