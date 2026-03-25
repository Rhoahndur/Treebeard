"""
Database Seeding Script for TreeBeard on Railway

This script populates the Railway production database with Texas energy plans.
Run: python scripts/seed_railway.py
"""

import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import settings

# Import seed functions from existing script
from scripts.seed_database import seed_admin_user, seed_demo_user, seed_plans, seed_suppliers


def main():
    """Main seeding function for Railway."""
    print("\n" + "=" * 60)
    print("TreeBeard Database Seeding (Railway)")
    print("=" * 60 + "\n")

    # Use DATABASE_URL from environment (Railway sets this automatically)
    db_url = settings.database_url
    print("Connecting to Railway database...")

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Seed in order
        print("\n[1/4] Seeding suppliers...")
        suppliers = seed_suppliers(db)

        print("\n[2/4] Seeding energy plans...")
        plans = seed_plans(db, suppliers)

        print("\n[3/4] Creating admin user...")
        admin = seed_admin_user(db)

        print("\n[4/4] Creating demo user...")
        demo_user = seed_demo_user(db)

        print("\n" + "=" * 60)
        print("✓ RAILWAY SEEDING COMPLETE!")
        print("=" * 60)
        print("\nSummary:")
        print(f"  • Suppliers: {len(suppliers)}")
        print(f"  • Plans: {len(plans)}")
        print("  • Admin user: admin@treebeard.com")
        print("  • Demo user: user@treebeard.com")
        print("\n⚠ Remember to change admin password in production!\n")

    except Exception as e:
        print(f"\n✗ ERROR during seeding: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
