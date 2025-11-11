#!/usr/bin/env python3
"""
Cache Warming Script.
Story 7.1 - Epic 7: Performance Optimization

Standalone script to warm cache on-demand or via cron.

Usage:
    python scripts/warm_cache.py --mode full
    python scripts/warm_cache.py --mode plans --limit 100
    python scripts/warm_cache.py --mode profiles --days 7
    python scripts/warm_cache.py --mode recommendations --days 1
"""

import sys
import asyncio
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from backend.services.cache_warming import get_cache_warming_service
from backend.services.cache_optimization import get_optimized_cache


async def warm_full_cache(service, args):
    """Warm entire cache (startup mode)."""
    print("Warming full cache...")
    await service.warm_startup_cache()
    print("Full cache warming complete!")


async def warm_plans(service, args):
    """Warm popular plans only."""
    limit = args.limit or 100
    print(f"Warming {limit} popular plans...")
    count = await service.warm_popular_plans(limit=limit)
    print(f"Warmed {count} plans successfully!")


async def warm_profiles(service, args):
    """Warm user profiles."""
    days = args.days or 7
    limit = args.limit or 50
    print(f"Warming profiles for active users (last {days} days)...")
    count = await service.warm_active_user_profiles(days=days, limit=limit)
    print(f"Warmed {count} profiles successfully!")


async def warm_recommendations(service, args):
    """Warm recent recommendations."""
    days = args.days or 1
    limit = args.limit or 50
    print(f"Warming recent recommendations (last {days} days)...")
    count = await service.warm_recent_recommendations(days=days, limit=limit)
    print(f"Warmed {count} recommendations successfully!")


async def show_stats(service, args):
    """Show cache and warming statistics."""
    print("\n" + "=" * 60)
    print("CACHE STATISTICS")
    print("=" * 60)

    # Cache stats
    cache = get_optimized_cache()
    stats = cache.get_stats()

    print("\nGeneral Stats:")
    print(f"  Enabled: {stats['enabled']}")
    print(f"  Total Requests: {stats['total_requests']}")
    print(f"  Cache Hits: {stats['cache_hits']}")
    print(f"  Cache Misses: {stats['cache_misses']}")
    print(f"  Hit Rate: {stats['hit_rate']:.2f}%")
    print(f"  Miss Rate: {stats['miss_rate']:.2f}%")
    print(f"  Errors: {stats['errors']}")

    if 'used_memory_human' in stats:
        print(f"\nRedis Stats:")
        print(f"  Memory Used: {stats['used_memory_human']}")
        print(f"  Connected Clients: {stats['connected_clients']}")

    # Warming stats
    warming_stats = service.get_warming_stats()
    print("\nWarming Stats:")
    print(f"  Last Full Warm: {warming_stats['last_full_warm'] or 'Never'}")
    print(f"  Last Plan Warm: {warming_stats['last_plan_warm'] or 'Never'}")
    print(f"  Last Profile Warm: {warming_stats['last_profile_warm'] or 'Never'}")
    print(f"  Total Items Warmed: {warming_stats['total_items_warmed']}")
    print(f"  Errors: {warming_stats['errors']}")

    # Key pattern stats
    print("\nKey Pattern Stats:")
    key_stats = cache.get_key_stats()
    if key_stats:
        for kstat in key_stats:
            print(f"  {kstat['pattern']}:")
            print(f"    Hits: {kstat['hits']}")
            print(f"    Misses: {kstat['misses']}")
            print(f"    Hit Rate: {kstat['hit_rate']:.2f}%")
    else:
        print("  No key pattern data available")

    print("\n" + "=" * 60)


async def health_check(service, args):
    """Perform health check on cache."""
    print("Performing cache health check...")
    cache = get_optimized_cache()
    health = cache.health_check()

    print("\nCache Health:")
    print(f"  Status: {health['status']}")
    print(f"  Healthy: {health['healthy']}")
    if 'latency_ms' in health:
        print(f"  Latency: {health['latency_ms']:.2f}ms")
    if 'hit_rate' in health:
        print(f"  Hit Rate: {health['hit_rate']:.2f}%")
    if 'message' in health:
        print(f"  Message: {health['message']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Cache warming script for TreeBeard application"
    )

    parser.add_argument(
        "--mode",
        choices=["full", "plans", "profiles", "recommendations", "stats", "health"],
        default="full",
        help="Warming mode (default: full)",
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of items to warm",
    )

    parser.add_argument(
        "--days",
        type=int,
        help="Number of days for filtering (profiles/recommendations)",
    )

    args = parser.parse_args()

    # Initialize service
    service = get_cache_warming_service()

    # Mode handlers
    mode_handlers = {
        "full": warm_full_cache,
        "plans": warm_plans,
        "profiles": warm_profiles,
        "recommendations": warm_recommendations,
        "stats": show_stats,
        "health": health_check,
    }

    # Run selected mode
    handler = mode_handlers[args.mode]
    try:
        asyncio.run(handler(service, args))
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
