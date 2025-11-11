"""
Seed users into database.
"""

import sys
import os
from uuid import uuid4
from datetime import datetime
from pathlib import Path

# Load .env file explicitly
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.user import User
from backend.api.auth.jwt import get_password_hash

# Use DATABASE_URL directly from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://treebeard:dev_password_123@localhost:5432/treebeard_dev"
)

def seed_users():
    """Seed admin and demo users."""
    print("=" * 60)
    print("SEEDING USERS")
    print("=" * 60)
    print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")

    # Create database connection
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Check if users already exist
        existing_count = db.query(User).count()
        if existing_count > 0:
            print(f"\n⚠ Found {existing_count} existing users")
            response = input("Delete existing users and re-seed? (y/n): ")
            if response.lower() == 'y':
                db.query(User).delete()
                db.commit()
                print("✓ Deleted existing users")
            else:
                print("Skipping user seeding")
                return

        # Create users
        users_data = [
            {
                "email": "admin@treebeard.com",
                "name": "Admin User",
                "password": "admin123",
                "zip_code": "78701",
                "property_type": "residential",
                "is_admin": True,
            },
            {
                "email": "demo@treebeard.com",
                "name": "Demo User",
                "password": "demo123",
                "zip_code": "78701",
                "property_type": "residential",
                "is_admin": False,
            },
            {
                "email": "user@treebeard.com",
                "name": "Test User",
                "password": "user123",
                "zip_code": "78702",
                "property_type": "residential",
                "is_admin": False,
            },
        ]

        print(f"\nCreating {len(users_data)} users...")

        for user_data in users_data:
            try:
                # Hash password with error handling
                try:
                    hashed_password = get_password_hash(user_data["password"])
                except Exception as e:
                    print(f"  ✗ Password hashing failed for {user_data['email']}: {e}")
                    print(f"    Trying with shorter password...")
                    # Try with just "pass123" which is 7 characters
                    hashed_password = get_password_hash("pass123")

                user = User(
                    id=uuid4(),
                    email=user_data["email"],
                    name=user_data["name"],
                    hashed_password=hashed_password,
                    zip_code=user_data["zip_code"],
                    property_type=user_data["property_type"],
                    is_admin=user_data["is_admin"],
                    is_active=True,
                    consent_given=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                db.add(user)
                db.commit()
                print(f"  ✓ Created user: {user_data['email']}")

            except Exception as e:
                print(f"  ✗ Failed to create {user_data['email']}: {e}")
                db.rollback()
                continue

        # Verify
        final_count = db.query(User).count()
        print(f"\n{'=' * 60}")
        print(f"✓ USERS SEEDED: {final_count} total")
        print(f"{'=' * 60}")

        # Display credentials
        print("\n📋 Login Credentials:")
        print("-" * 60)
        for user_data in users_data:
            password = user_data["password"] if user_data["password"] != "pass123" else "pass123"
            print(f"  Email: {user_data['email']}")
            print(f"  Password: {password}")
            print(f"  Admin: {user_data['is_admin']}")
            print()

    except Exception as e:
        print(f"\n✗ Error seeding users: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
