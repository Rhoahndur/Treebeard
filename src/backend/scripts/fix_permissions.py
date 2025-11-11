"""
Fix PostgreSQL database permissions for treebeard user.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect as postgres superuser (modify if needed)
# Try common postgres connection strings
connection_attempts = [
    "postgresql://postgres@localhost:5432/treebeard_dev",
    "postgresql://postgres:postgres@localhost:5432/treebeard_dev",
    "postgresql://aleksandrgaun@localhost:5432/treebeard_dev",
    "postgresql://treebeard:dev_password_123@localhost:5432/postgres",
]

print("Attempting to fix database permissions...")
print("="*60)

connected = False
conn = None

for conn_string in connection_attempts:
    try:
        print(f"\nTrying connection: {conn_string.split('@')[0]}@...")
        conn = psycopg2.connect(conn_string)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        connected = True
        print("✓ Connected successfully!")
        break
    except Exception as e:
        print(f"✗ Failed: {e}")
        continue

if not connected:
    print("\n" + "="*60)
    print("ERROR: Could not connect to PostgreSQL")
    print("="*60)
    print("\nPlease run one of these commands manually:")
    print("\n1. If you have Postgres.app:")
    print("   /Applications/Postgres.app/Contents/Versions/*/bin/psql -U postgres -d treebeard_dev")
    print("\n2. If you have Homebrew PostgreSQL:")
    print("   psql -U postgres -d treebeard_dev")
    print("\n3. Or connect as your macOS user:")
    print(f"   psql -U aleksandrgaun -d treebeard_dev")
    print("\nThen run these SQL commands:")
    print("   GRANT ALL ON SCHEMA public TO treebeard;")
    print("   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO treebeard;")
    print("   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO treebeard;")
    print("   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO treebeard;")
    print("   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO treebeard;")
    sys.exit(1)

# Grant permissions
try:
    cursor = conn.cursor()

    commands = [
        "GRANT ALL ON SCHEMA public TO treebeard;",
        "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO treebeard;",
        "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO treebeard;",
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO treebeard;",
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO treebeard;",
    ]

    print("\nGranting permissions...")
    for cmd in commands:
        try:
            cursor.execute(cmd)
            print(f"✓ {cmd}")
        except Exception as e:
            print(f"⚠ {cmd} - {e}")

    cursor.close()
    conn.close()

    print("\n" + "="*60)
    print("✓ Permissions fixed successfully!")
    print("="*60)
    print("\nYou can now run:")
    print("  alembic upgrade head")
    print("  python backend/scripts/seed_database.py")

except Exception as e:
    print(f"\n✗ Error granting permissions: {e}")
    sys.exit(1)
