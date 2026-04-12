#!/bin/bash
set -e

echo "=== Running database migrations ==="
alembic upgrade head

# Seed only if the database is empty (idempotent across deploys)
PLAN_COUNT=$(python -c "
from sqlalchemy import create_engine, text
from config.settings import settings
with create_engine(settings.database_url).connect() as c:
    print(c.execute(text('SELECT count(*) FROM plan_catalog')).scalar())
")

if [ "$PLAN_COUNT" = "0" ]; then
    echo "=== Seeding database (empty) ==="
    python scripts/seed_railway.py
else
    echo "=== Database already seeded (${PLAN_COUNT} plans), skipping ==="
fi

echo "=== Starting server ==="
exec python -m uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
