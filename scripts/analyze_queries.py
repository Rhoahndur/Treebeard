#!/usr/bin/env python3
"""
Query Analysis Script.
Story 7.2 - Epic 7: Performance Optimization

Analyzes slow queries and provides optimization recommendations.

Usage:
    python scripts/analyze_queries.py --mode all
    python scripts/analyze_queries.py --mode slow --threshold 100
    python scripts/analyze_queries.py --mode pool
    python scripts/analyze_queries.py --mode indexes
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from backend.config.database import (
    engine,
    get_pool_status,
    health_check_db,
    get_db_session,
)
from sqlalchemy import text, inspect


def analyze_slow_queries(threshold_ms: int = 100):
    """
    Analyze slow queries from PostgreSQL logs.

    Args:
        threshold_ms: Query time threshold in milliseconds
    """
    print(f"\n{'=' * 70}")
    print(f"SLOW QUERY ANALYSIS (threshold: {threshold_ms}ms)")
    print(f"{'=' * 70}\n")

    try:
        with get_db_session() as db:
            # Enable query statistics if not already enabled
            query = text("""
                SELECT
                    queryid,
                    query,
                    calls,
                    total_time,
                    mean_time,
                    max_time,
                    stddev_time
                FROM pg_stat_statements
                WHERE mean_time > :threshold
                ORDER BY mean_time DESC
                LIMIT 20
            """)

            try:
                result = db.execute(query, {"threshold": threshold_ms})
                rows = result.fetchall()

                if rows:
                    print(f"Found {len(rows)} slow queries:\n")
                    for i, row in enumerate(rows, 1):
                        print(f"{i}. Mean Time: {row.mean_time:.2f}ms")
                        print(f"   Max Time: {row.max_time:.2f}ms")
                        print(f"   Calls: {row.calls}")
                        print(f"   Query: {row.query[:100]}...")
                        print()
                else:
                    print("No slow queries found.")
            except Exception as e:
                print(f"Note: pg_stat_statements extension not available: {e}")
                print("To enable: CREATE EXTENSION pg_stat_statements;")

    except Exception as e:
        print(f"Error analyzing slow queries: {e}")


def analyze_pool_status():
    """Analyze database connection pool status."""
    print(f"\n{'=' * 70}")
    print("CONNECTION POOL STATUS")
    print(f"{'=' * 70}\n")

    try:
        status = get_pool_status()

        print(f"Pool Configuration:")
        print(f"  Pool Size: {status['pool_size']}")
        print(f"  Total Connections: {status['total_connections']}")
        print()

        print(f"Current Usage:")
        print(f"  Checked Out: {status['checked_out']}")
        print(f"  Checked In: {status['checked_in']}")
        print(f"  Overflow: {status['overflow']}")
        print()

        # Calculate utilization
        utilization = (status['checked_out'] / status['total_connections'] * 100
                      if status['total_connections'] > 0 else 0)

        print(f"Utilization: {utilization:.1f}%")

        if utilization > 80:
            print("  ⚠️  WARNING: High pool utilization. Consider increasing pool size.")
        elif utilization < 20:
            print("  ℹ️  INFO: Low pool utilization. Pool is adequately sized.")
        else:
            print("  ✓ GOOD: Pool utilization is healthy.")

    except Exception as e:
        print(f"Error analyzing pool: {e}")


def analyze_indexes():
    """Analyze database indexes."""
    print(f"\n{'=' * 70}")
    print("INDEX ANALYSIS")
    print(f"{'=' * 70}\n")

    try:
        with get_db_session() as db:
            # Get index usage statistics
            query = text("""
                SELECT
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch,
                    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
                FROM pg_stat_user_indexes
                ORDER BY idx_scan ASC, pg_relation_size(indexrelid) DESC
                LIMIT 20
            """)

            result = db.execute(query)
            rows = result.fetchall()

            if rows:
                print("Index Usage Statistics (least used first):\n")

                unused_count = 0
                for i, row in enumerate(rows, 1):
                    if row.idx_scan == 0:
                        unused_count += 1
                        print(f"⚠️  {i}. {row.tablename}.{row.indexname}")
                        print(f"    Scans: {row.idx_scan}")
                        print(f"    Size: {row.index_size}")
                        print(f"    Status: UNUSED - Consider dropping")
                    else:
                        print(f"✓ {i}. {row.tablename}.{row.indexname}")
                        print(f"    Scans: {row.idx_scan}")
                        print(f"    Tuples Read: {row.idx_tup_read}")
                        print(f"    Size: {row.index_size}")
                    print()

                if unused_count > 0:
                    print(f"\n⚠️  Found {unused_count} unused indexes.")
                    print("Consider dropping unused indexes to improve write performance.")
            else:
                print("No index statistics available.")

            # Missing indexes analysis
            print(f"\n{'=' * 70}")
            print("MISSING INDEXES (Tables with Sequential Scans)")
            print(f"{'=' * 70}\n")

            query = text("""
                SELECT
                    schemaname,
                    tablename,
                    seq_scan,
                    seq_tup_read,
                    idx_scan,
                    seq_tup_read / seq_scan AS avg_seq_read
                FROM pg_stat_user_tables
                WHERE seq_scan > 0
                ORDER BY seq_tup_read DESC
                LIMIT 10
            """)

            result = db.execute(query)
            rows = result.fetchall()

            if rows:
                print("Tables with high sequential scan rates:\n")
                for i, row in enumerate(rows, 1):
                    ratio = (row.seq_scan / (row.seq_scan + row.idx_scan) * 100
                            if (row.seq_scan + row.idx_scan) > 0 else 0)

                    print(f"{i}. {row.tablename}")
                    print(f"   Sequential Scans: {row.seq_scan}")
                    print(f"   Index Scans: {row.idx_scan}")
                    print(f"   Seq Scan Ratio: {ratio:.1f}%")
                    print(f"   Avg Rows per Seq Scan: {row.avg_seq_read:.0f}")

                    if ratio > 50:
                        print(f"   ⚠️  Consider adding indexes to improve performance")
                    print()

    except Exception as e:
        print(f"Error analyzing indexes: {e}")


def analyze_table_sizes():
    """Analyze table and index sizes."""
    print(f"\n{'=' * 70}")
    print("TABLE SIZE ANALYSIS")
    print(f"{'=' * 70}\n")

    try:
        with get_db_session() as db:
            query = text("""
                SELECT
                    tablename,
                    pg_size_pretty(pg_total_relation_size(tablename::regclass)) AS total_size,
                    pg_size_pretty(pg_relation_size(tablename::regclass)) AS table_size,
                    pg_size_pretty(pg_total_relation_size(tablename::regclass) -
                                   pg_relation_size(tablename::regclass)) AS index_size
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(tablename::regclass) DESC
            """)

            result = db.execute(query)
            rows = result.fetchall()

            if rows:
                print("Table sizes:\n")
                for i, row in enumerate(rows, 1):
                    print(f"{i}. {row.tablename}")
                    print(f"   Total Size: {row.total_size}")
                    print(f"   Table Size: {row.table_size}")
                    print(f"   Index Size: {row.index_size}")
                    print()

    except Exception as e:
        print(f"Error analyzing table sizes: {e}")


def analyze_cache_hit_rate():
    """Analyze database cache hit rate."""
    print(f"\n{'=' * 70}")
    print("DATABASE CACHE HIT RATE")
    print(f"{'=' * 70}\n")

    try:
        with get_db_session() as db:
            query = text("""
                SELECT
                    sum(heap_blks_read) as heap_read,
                    sum(heap_blks_hit) as heap_hit,
                    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) AS ratio
                FROM pg_statio_user_tables;
            """)

            result = db.execute(query)
            row = result.fetchone()

            if row and row.ratio is not None:
                hit_rate = row.ratio * 100
                print(f"Cache Hit Rate: {hit_rate:.2f}%")
                print(f"Heap Blocks Read: {row.heap_read}")
                print(f"Heap Blocks Hit: {row.heap_hit}")
                print()

                if hit_rate > 99:
                    print("✓ EXCELLENT: Cache hit rate is optimal.")
                elif hit_rate > 95:
                    print("✓ GOOD: Cache hit rate is healthy.")
                elif hit_rate > 90:
                    print("⚠️  WARNING: Cache hit rate could be improved.")
                    print("Consider increasing shared_buffers in PostgreSQL config.")
                else:
                    print("⚠️  CRITICAL: Low cache hit rate.")
                    print("Increase shared_buffers and effective_cache_size.")

    except Exception as e:
        print(f"Error analyzing cache hit rate: {e}")


def health_check():
    """Perform database health check."""
    print(f"\n{'=' * 70}")
    print("DATABASE HEALTH CHECK")
    print(f"{'=' * 70}\n")

    healthy = health_check_db()

    if healthy:
        print("✓ Database connection: HEALTHY")
    else:
        print("✗ Database connection: UNHEALTHY")
        return

    # Additional health metrics
    try:
        with get_db_session() as db:
            # Check database size
            query = text("""
                SELECT pg_size_pretty(pg_database_size(current_database())) AS db_size
            """)
            result = db.execute(query)
            row = result.fetchone()
            print(f"Database Size: {row.db_size}")

            # Check active connections
            query = text("""
                SELECT count(*) AS active_connections
                FROM pg_stat_activity
                WHERE state = 'active'
            """)
            result = db.execute(query)
            row = result.fetchone()
            print(f"Active Connections: {row.active_connections}")

    except Exception as e:
        print(f"Error fetching health metrics: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Database query analysis tool for TreeBeard application"
    )

    parser.add_argument(
        "--mode",
        choices=["all", "slow", "pool", "indexes", "sizes", "cache", "health"],
        default="all",
        help="Analysis mode (default: all)",
    )

    parser.add_argument(
        "--threshold",
        type=int,
        default=100,
        help="Slow query threshold in milliseconds (default: 100)",
    )

    args = parser.parse_args()

    print(f"\n{'=' * 70}")
    print("TREEBEARD DATABASE ANALYSIS")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'=' * 70}")

    try:
        if args.mode in ["all", "health"]:
            health_check()

        if args.mode in ["all", "pool"]:
            analyze_pool_status()

        if args.mode in ["all", "slow"]:
            analyze_slow_queries(args.threshold)

        if args.mode in ["all", "indexes"]:
            analyze_indexes()

        if args.mode in ["all", "sizes"]:
            analyze_table_sizes()

        if args.mode in ["all", "cache"]:
            analyze_cache_hit_rate()

        print(f"\n{'=' * 70}")
        print("Analysis complete!")
        print(f"{'=' * 70}\n")

    except KeyboardInterrupt:
        print("\nAnalysis cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
