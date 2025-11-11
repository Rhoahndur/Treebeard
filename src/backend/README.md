# TreeBeard Backend - Database Layer

**Story 1.1:** Database Schema Design
**Status:** ✅ Complete
**Python Version:** 3.11+
**Database:** PostgreSQL 15+

## Overview

This directory contains the complete database layer for the TreeBeard Energy Plan Recommendation System, including:

- **SQLAlchemy Models:** 9 database tables with relationships
- **Pydantic Schemas:** Type-safe API contracts
- **Alembic Migrations:** Database schema versioning
- **Configuration:** Database connection and settings management

## Quick Start

### Prerequisites

```bash
# Install Python 3.11+
python --version  # Should be 3.11 or higher

# Install PostgreSQL 15+
# Option 1: Docker
docker-compose up -d postgres

# Option 2: Local installation
brew install postgresql@15  # macOS
```

### Installation

```bash
# 1. Navigate to backend directory
cd src/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# 5. Run database migrations
alembic upgrade head
```

## Project Structure

```
src/backend/
├── models/                 # SQLAlchemy ORM models (9 tables)
│   ├── base.py            # Base model with mixins
│   ├── user.py            # User, UserPreference, CurrentPlan
│   ├── usage.py           # UsageHistory
│   ├── plan.py            # Supplier, PlanCatalog
│   ├── recommendation.py  # Recommendation, RecommendationPlan
│   └── feedback.py        # Feedback
│
├── schemas/               # Pydantic validation schemas
│   ├── user.py            # User-related schemas
│   ├── usage_schemas.py   # Usage and analysis schemas
│   ├── plan.py            # Plan catalog schemas
│   ├── recommendation.py  # Recommendation schemas
│   └── feedback.py        # Feedback schemas
│
├── config/                # Configuration management
│   ├── settings.py        # Application settings
│   └── database.py        # Database connection
│
├── alembic/               # Database migrations
│   └── versions/
│       └── 001_initial_schema.py
│
├── alembic.ini            # Alembic configuration
└── requirements.txt       # Python dependencies
```

## Database Schema

### Tables
1. **users** - User profiles and consent
2. **user_preferences** - Recommendation preference weights
3. **current_plans** - User's current energy plan
4. **usage_history** - Daily energy usage
5. **suppliers** - Energy supplier information
6. **plan_catalog** - Available energy plans
7. **recommendations** - Recommendation sessions
8. **recommendation_plans** - Top 3 plans per recommendation
9. **feedback** - User feedback

**Full Documentation:** See `/docs/database-schema.md`

## Database Migrations

```bash
# Apply all migrations
alembic upgrade head

# Check current migration
alembic current

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

## Integration

For integration with other stories, see:
- **Contract Document:** `/docs/contracts/story-1.1-contract.md`
- **Usage Examples:** Included in contract document
- **Mock Data Functions:** Included in contract document

## Testing

```bash
pytest tests/backend/
```

## Documentation

- Database Schema: `/docs/database-schema.md`
- API Contract: `/docs/contracts/story-1.1-contract.md`
- Architecture: `/architecture.md`
