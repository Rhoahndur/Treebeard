#!/bin/bash
# Database Initialization Script for Railway
# Run this after deploying to set up the database schema

set -e

echo "🚀 Starting database initialization..."

# Navigate to backend directory
cd "$(dirname "$0")/../src/backend"

echo "📦 Running Alembic migrations..."
alembic upgrade head

echo "✅ Database initialization complete!"
