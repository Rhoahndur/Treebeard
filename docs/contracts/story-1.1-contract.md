# Story 1.1 - Database Schema Contract

**Version:** 1.0.0
**Date:** November 10, 2025
**Author:** Backend Dev #1
**Status:** Complete

## Purpose

This contract defines the interface between Story 1.1 (Database Schema) and other stories, particularly:
- **Story 1.4** - Usage Analysis Engine (Backend Dev #2)
- **Story 1.5** - Plan Matching Algorithm
- **Frontend** - API integration

All Pydantic schemas, database models, and example queries are provided here for integration.

---

## Table of Contents

1. [Database Access](#database-access)
2. [Pydantic Schemas](#pydantic-schemas)
3. [Usage Examples](#usage-examples)
4. [Mock Data Functions](#mock-data-functions)
5. [Query Examples](#query-examples)
6. [Integration Guide](#integration-guide)

---

## Database Access

### Connection Setup

```python
from config.database import get_db, SessionLocal
from sqlalchemy.orm import Session

# Option 1: FastAPI dependency injection
from fastapi import Depends

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# Option 2: Direct session
db = SessionLocal()
try:
    users = db.query(User).all()
finally:
    db.close()

# Option 3: Context manager
from contextlib import contextmanager

@contextmanager
def get_db_context():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

with get_db_context() as db:
    users = db.query(User).all()
```

### Import Models

```python
# All models
from models import (
    User, UserPreference, CurrentPlan,
    UsageHistory,
    Supplier, PlanCatalog,
    Recommendation, RecommendationPlan,
    Feedback
)

# Or import individually
from models.user import User
from models.usage import UsageHistory
from models.plan import PlanCatalog
```

---

## Pydantic Schemas

### User Schemas

```python
from schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPreferenceCreate,
    UserPreferenceUpdate,
    UserPreferenceResponse,
    CurrentPlanCreate,
    CurrentPlanUpdate,
    CurrentPlanResponse,
    UserProfileResponse
)

# Example: Create a new user
user_data = UserCreate(
    email="sarah@example.com",
    name="Sarah Johnson",
    zip_code="75001",
    property_type="residential",
    consent_given=True
)

# Example: Update user preferences
preferences_data = UserPreferenceUpdate(
    cost_priority=50,  # Increase cost priority
    renewable_priority=30  # Increase renewable priority
)

# Example: Complete user profile response
profile_response = UserProfileResponse(
    user=user,
    preferences=preferences,
    current_plan=current_plan
)
```

### Usage Schemas

**CRITICAL FOR BACKEND DEV #2**

```python
from schemas import (
    UsageHistoryCreate,
    UsageHistoryBulkCreate,
    UsageHistoryResponse,
    UsageProfile,
    UsageSummary,
    UsageStatistics,
    SeasonalPattern,
    DataQualityMetrics,
    MonthlyUsage
)

# Example: Bulk create usage records
from datetime import date
from decimal import Decimal

usage_bulk = UsageHistoryBulkCreate(
    user_id="123e4567-e89b-12d3-a456-426614174000",
    usage_records=[
        UsageHistoryCreate(
            usage_date=date(2024, 1, 1),
            kwh_consumed=Decimal("35.5"),
            data_source="upload",
            data_quality="complete"
        ),
        UsageHistoryCreate(
            usage_date=date(2024, 1, 2),
            kwh_consumed=Decimal("42.3"),
            data_source="upload",
            data_quality="complete"
        ),
        # ... more records
    ]
)

# Example: Usage profile (OUTPUT of Usage Analysis Engine - Story 1.4)
usage_profile = UsageProfile(
    user_id="123e4567-e89b-12d3-a456-426614174000",
    profile_type="seasonal_user",
    analysis_period_start=date(2023, 11, 1),
    analysis_period_end=date(2024, 10, 31),

    statistics=UsageStatistics(
        total_kwh=Decimal("12500.50"),
        avg_daily_kwh=Decimal("34.25"),
        avg_monthly_kwh=Decimal("1041.71"),
        min_daily_kwh=Decimal("18.5"),
        max_daily_kwh=Decimal("65.3"),
        std_dev_kwh=Decimal("12.4")
    ),

    seasonal_patterns=[
        SeasonalPattern(
            season="summer",
            avg_daily_kwh=Decimal("48.5"),
            total_kwh=Decimal("4462.5"),
            percentage_of_annual=Decimal("35.7")
        ),
        SeasonalPattern(
            season="winter",
            avg_daily_kwh=Decimal("38.2"),
            total_kwh=Decimal("3510.4"),
            percentage_of_annual=Decimal("28.1")
        ),
        # ... other seasons
    ],

    projected_annual_kwh=Decimal("13200.00"),
    projected_monthly_kwh=[
        Decimal("950.0"),  # Jan
        Decimal("920.0"),  # Feb
        Decimal("880.0"),  # Mar
        Decimal("810.0"),  # Apr
        Decimal("780.0"),  # May
        Decimal("1200.0"), # Jun
        Decimal("1450.0"), # Jul
        Decimal("1380.0"), # Aug
        Decimal("1100.0"), # Sep
        Decimal("850.0"),  # Oct
        Decimal("920.0"),  # Nov
        Decimal("960.0"),  # Dec
    ],

    data_quality=DataQualityMetrics(
        total_days_expected=365,
        total_days_available=358,
        completeness_percentage=Decimal("98.08"),
        missing_days=7,
        has_gaps=True,
        quality_flag="excellent",
        quality_issues=["7 days missing in March"]
    ),

    confidence_score=Decimal("0.95"),
    notes=["Strong seasonal pattern detected", "Summer peak usage 50% above baseline"]
)
```

### Plan Schemas

```python
from schemas import (
    SupplierCreate,
    SupplierResponse,
    PlanCatalogCreate,
    PlanCatalogResponse,
    PlanCatalogSummary,
    PlanFilterParams
)

# Example: Create a supplier
supplier_data = SupplierCreate(
    supplier_name="Green Energy Co",
    average_rating=Decimal("4.5"),
    review_count=1250,
    website="https://greenenergy.com",
    is_active=True
)

# Example: Create a plan with fixed rate
plan_data = PlanCatalogCreate(
    supplier_id="supplier-uuid",
    plan_name="Solar Saver 12",
    plan_type="fixed",
    rate_structure={
        "type": "fixed",
        "rate_per_kwh": 12.5
    },
    contract_length_months=12,
    early_termination_fee=Decimal("150.00"),
    renewable_percentage=Decimal("100.00"),
    monthly_fee=Decimal("9.95"),
    available_regions=["75001", "75002", "75003"],
    is_active=True
)

# Example: Plan filtering
filter_params = PlanFilterParams(
    zip_code="75001",
    plan_type="fixed",
    max_contract_length=12,
    min_renewable_percentage=Decimal("50.0"),
    is_active=True
)
```

### Recommendation Schemas

```python
from schemas import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendationPlanResponse,
    PlanScores
)

# Example: Request recommendations
request = RecommendationRequest(
    user_id="user-uuid",
    force_refresh=False
)

# Example: Recommendation response structure
response = RecommendationResponse(
    id="recommendation-uuid",
    user_id="user-uuid",
    usage_profile={
        "profile_type": "seasonal_user",
        "projected_annual_kwh": 13200.0,
        # ... (stored as JSONB)
    },
    recommended_plans=[
        RecommendationPlanResponse(
            id="rec-plan-uuid",
            rank=1,
            plan=plan_catalog_response,
            scores=PlanScores(
                cost_score=Decimal("92.5"),
                flexibility_score=Decimal("85.0"),
                renewable_score=Decimal("100.0"),
                rating_score=Decimal("90.0"),
                composite_score=Decimal("91.2")
            ),
            projected_annual_cost=Decimal("1650.00"),
            projected_annual_savings=Decimal("320.00"),
            break_even_months=5,
            explanation="This plan offers the best overall value...",
            risk_flags=None
        ),
        # ... rank 2 and 3
    ],
    generated_at=datetime.now(),
    expires_at=datetime.now() + timedelta(hours=24),
    algorithm_version="1.0.0",
    stay_with_current=False,
    stay_reason=None
)
```

### Feedback Schemas

```python
from schemas import (
    FeedbackCreate,
    FeedbackResponse
)

# Example: Create feedback
feedback_data = FeedbackCreate(
    recommendation_id="recommendation-uuid",
    recommended_plan_id="rec-plan-uuid",
    plan_id="plan-uuid",
    rating=5,
    feedback_text="Very helpful! Switched to this plan.",
    feedback_type="selected"
)
```

---

## Usage Examples

### Example 1: Fetch User with All Related Data

```python
from sqlalchemy.orm import Session, joinedload
from models import User

def get_user_profile(db: Session, user_id: str):
    """Fetch user with preferences, current plan, and latest recommendations."""
    user = db.query(User).options(
        joinedload(User.preferences),
        joinedload(User.current_plan),
        joinedload(User.recommendations)
    ).filter(User.id == user_id).first()

    return user
```

### Example 2: Fetch Usage History for Analysis (FOR BACKEND DEV #2)

```python
from datetime import date, timedelta
from sqlalchemy import and_
from models import UsageHistory

def get_usage_history(db: Session, user_id: str, months: int = 12):
    """
    Fetch usage history for the specified number of months.

    This is the primary function Backend Dev #2 will use to retrieve
    usage data for analysis.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=months * 30)

    usage_records = db.query(UsageHistory).filter(
        and_(
            UsageHistory.user_id == user_id,
            UsageHistory.usage_date >= start_date,
            UsageHistory.usage_date <= end_date
        )
    ).order_by(UsageHistory.usage_date.asc()).all()

    return usage_records

# Convert to list of (date, kwh) tuples for analysis
def get_usage_data_for_analysis(db: Session, user_id: str):
    """Format usage data for analysis engine."""
    records = get_usage_history(db, user_id, months=12)
    return [(r.usage_date, float(r.kwh_consumed)) for r in records]
```

### Example 3: Query Plans by Region

```python
from models import PlanCatalog, Supplier
from sqlalchemy import and_

def get_plans_for_region(db: Session, zip_code: str):
    """Fetch all active plans available in a ZIP code."""
    plans = db.query(PlanCatalog).join(Supplier).filter(
        and_(
            PlanCatalog.is_active == True,
            Supplier.is_active == True,
            PlanCatalog.available_regions.contains([zip_code])
        )
    ).all()

    return plans
```

### Example 4: Create Recommendation with Plans

```python
from datetime import datetime, timedelta
from models import Recommendation, RecommendationPlan
from decimal import Decimal

def save_recommendation(
    db: Session,
    user_id: str,
    usage_profile: dict,
    recommended_plans: list
):
    """
    Save recommendation session with top 3 plans.

    This is what the Plan Matching Algorithm (Story 1.5) will call
    to store recommendations.
    """
    # Create recommendation session
    recommendation = Recommendation(
        user_id=user_id,
        usage_profile=usage_profile,
        generated_at=datetime.now(),
        expires_at=datetime.now() + timedelta(hours=24),
        algorithm_version="1.0.0"
    )
    db.add(recommendation)
    db.flush()  # Get recommendation.id

    # Add recommended plans
    for i, plan_data in enumerate(recommended_plans[:3], start=1):
        rec_plan = RecommendationPlan(
            recommendation_id=recommendation.id,
            plan_id=plan_data['plan_id'],
            rank=i,
            composite_score=plan_data['composite_score'],
            cost_score=plan_data['cost_score'],
            flexibility_score=plan_data['flexibility_score'],
            renewable_score=plan_data['renewable_score'],
            rating_score=plan_data['rating_score'],
            projected_annual_cost=plan_data['projected_annual_cost'],
            projected_annual_savings=plan_data['projected_annual_savings'],
            break_even_months=plan_data.get('break_even_months'),
            explanation=plan_data['explanation'],
            risk_flags=plan_data.get('risk_flags')
        )
        db.add(rec_plan)

    db.commit()
    db.refresh(recommendation)
    return recommendation
```

---

## Mock Data Functions

### Mock User Creation

```python
from uuid import uuid4
from datetime import date, datetime, timedelta
from decimal import Decimal
from models import *

def create_mock_user(db: Session):
    """Create a complete mock user with all related data."""
    user_id = uuid4()

    # Create user
    user = User(
        id=user_id,
        email=f"user_{user_id.hex[:8]}@example.com",
        name="Sarah Johnson",
        zip_code="75001",
        property_type="residential",
        consent_given=True
    )
    db.add(user)

    # Create preferences
    preferences = UserPreference(
        user_id=user_id,
        cost_priority=40,
        flexibility_priority=30,
        renewable_priority=20,
        rating_priority=10
    )
    db.add(preferences)

    # Create current plan
    current_plan = CurrentPlan(
        user_id=user_id,
        supplier_name="Old Energy Co",
        plan_name="Standard Rate",
        current_rate=Decimal("14.5"),
        contract_start_date=date(2023, 1, 1),
        contract_end_date=date(2024, 12, 31),
        early_termination_fee=Decimal("200.00"),
        monthly_fee=Decimal("12.00")
    )
    db.add(current_plan)

    # Create 12 months of usage history
    start_date = date.today() - timedelta(days=365)
    for day in range(365):
        usage_date = start_date + timedelta(days=day)

        # Simulate seasonal pattern
        month = usage_date.month
        if month in [6, 7, 8]:  # Summer
            base_kwh = 45.0
        elif month in [12, 1, 2]:  # Winter
            base_kwh = 38.0
        else:
            base_kwh = 28.0

        # Add some randomness
        import random
        kwh = Decimal(str(base_kwh + random.uniform(-5, 5)))

        usage = UsageHistory(
            user_id=user_id,
            usage_date=usage_date,
            kwh_consumed=kwh,
            data_source="mock",
            data_quality="complete"
        )
        db.add(usage)

    db.commit()
    return user_id

# Usage
db = SessionLocal()
user_id = create_mock_user(db)
print(f"Created mock user: {user_id}")
db.close()
```

### Mock Plan Catalog

```python
def create_mock_plans(db: Session):
    """Create mock suppliers and plans."""
    # Create suppliers
    suppliers = [
        Supplier(
            supplier_name="Green Energy Co",
            average_rating=Decimal("4.5"),
            review_count=1250,
            website="https://greenenergy.com",
            is_active=True
        ),
        Supplier(
            supplier_name="Solar Power Plus",
            average_rating=Decimal("4.2"),
            review_count=890,
            website="https://solarplus.com",
            is_active=True
        ),
        Supplier(
            supplier_name="Budget Power",
            average_rating=Decimal("3.8"),
            review_count=2100,
            website="https://budgetpower.com",
            is_active=True
        )
    ]

    for supplier in suppliers:
        db.add(supplier)
    db.flush()

    # Create plans
    plans = [
        PlanCatalog(
            supplier_id=suppliers[0].id,
            plan_name="Solar Saver 12",
            plan_type="fixed",
            rate_structure={"type": "fixed", "rate_per_kwh": 12.5},
            contract_length_months=12,
            early_termination_fee=Decimal("150.00"),
            renewable_percentage=Decimal("100.00"),
            monthly_fee=Decimal("9.95"),
            available_regions=["75001", "75002", "75003"],
            is_active=True
        ),
        PlanCatalog(
            supplier_id=suppliers[1].id,
            plan_name="Flex Power",
            plan_type="variable",
            rate_structure={"type": "variable", "base_rate": 11.0},
            contract_length_months=0,  # Month-to-month
            early_termination_fee=Decimal("0.00"),
            renewable_percentage=Decimal("75.00"),
            monthly_fee=None,
            available_regions=["75001", "75002"],
            is_active=True
        ),
        PlanCatalog(
            supplier_id=suppliers[2].id,
            plan_name="Budget Basic",
            plan_type="fixed",
            rate_structure={"type": "fixed", "rate_per_kwh": 13.8},
            contract_length_months=24,
            early_termination_fee=Decimal("250.00"),
            renewable_percentage=Decimal("10.00"),
            monthly_fee=Decimal("5.00"),
            available_regions=["75001", "75002", "75003", "75004"],
            is_active=True
        )
    ]

    for plan in plans:
        db.add(plan)

    db.commit()
    return [s.id for s in suppliers], [p.id for p in plans]
```

---

## Query Examples

### Complex Query: Get User's Latest Recommendation with Plans

```python
from sqlalchemy.orm import joinedload

def get_latest_recommendation(db: Session, user_id: str):
    """Get user's most recent recommendation with all plans."""
    recommendation = db.query(Recommendation).options(
        joinedload(Recommendation.recommendation_plans)
        .joinedload(RecommendationPlan.plan)
        .joinedload(PlanCatalog.supplier)
    ).filter(
        Recommendation.user_id == user_id
    ).order_by(
        Recommendation.generated_at.desc()
    ).first()

    return recommendation
```

### Aggregation Query: Monthly Usage Summary

```python
from sqlalchemy import func, extract

def get_monthly_usage_summary(db: Session, user_id: str, year: int):
    """Get monthly usage totals for a year."""
    results = db.query(
        extract('month', UsageHistory.usage_date).label('month'),
        func.sum(UsageHistory.kwh_consumed).label('total_kwh'),
        func.avg(UsageHistory.kwh_consumed).label('avg_kwh'),
        func.count(UsageHistory.id).label('days_count')
    ).filter(
        and_(
            UsageHistory.user_id == user_id,
            extract('year', UsageHistory.usage_date) == year
        )
    ).group_by(
        extract('month', UsageHistory.usage_date)
    ).order_by(
        extract('month', UsageHistory.usage_date)
    ).all()

    return results
```

### Filter Query: Plans by Criteria

```python
def find_plans_by_criteria(
    db: Session,
    zip_code: str,
    max_contract_months: int = None,
    min_renewable: Decimal = None,
    max_rate: Decimal = None
):
    """Find plans matching specific criteria."""
    query = db.query(PlanCatalog).join(Supplier).filter(
        and_(
            PlanCatalog.is_active == True,
            Supplier.is_active == True,
            PlanCatalog.available_regions.contains([zip_code])
        )
    )

    if max_contract_months is not None:
        query = query.filter(PlanCatalog.contract_length_months <= max_contract_months)

    if min_renewable is not None:
        query = query.filter(PlanCatalog.renewable_percentage >= min_renewable)

    if max_rate is not None:
        # For fixed rate plans only
        query = query.filter(
            and_(
                PlanCatalog.plan_type == 'fixed',
                PlanCatalog.rate_structure['rate_per_kwh'].astext.cast(Numeric) <= max_rate
            )
        )

    return query.all()
```

---

## Integration Guide

### For Backend Dev #2 (Usage Analysis Engine - Story 1.4)

**Your primary interface points:**

1. **Input: Get usage data**
   ```python
   from models import UsageHistory
   from config.database import get_db

   def analyze_user_usage(user_id: str):
       db = SessionLocal()
       try:
           usage_records = db.query(UsageHistory).filter(
               UsageHistory.user_id == user_id
           ).order_by(UsageHistory.usage_date).all()

           # Convert to your analysis format
           usage_data = [(r.usage_date, float(r.kwh_consumed)) for r in usage_records]

           # Run your analysis
           profile = run_usage_analysis(usage_data)

           return profile
       finally:
           db.close()
   ```

2. **Output: Return UsageProfile schema**
   ```python
   from schemas import UsageProfile, UsageStatistics, SeasonalPattern, DataQualityMetrics

   def run_usage_analysis(usage_data) -> UsageProfile:
       # Your analysis logic here
       # ...

       return UsageProfile(
           user_id=user_id,
           profile_type="seasonal_user",
           # ... fill in all required fields
       )
   ```

3. **Storage: Save usage profile in recommendation**
   The usage profile will be stored as JSONB in the `recommendations.usage_profile` field:
   ```python
   recommendation = Recommendation(
       user_id=user_id,
       usage_profile=usage_profile.model_dump(),  # Pydantic v2
       # or usage_profile.dict() in Pydantic v1
       ...
   )
   ```

### For Frontend Team

**Endpoints to implement (examples):**

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from schemas import UserCreate, UserResponse, RecommendationResponse

app = FastAPI()

@app.post("/api/v1/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Create user logic
    pass

@app.get("/api/v1/users/{user_id}/recommendations", response_model=list[RecommendationResponse])
def get_user_recommendations(user_id: str, db: Session = Depends(get_db)):
    # Get recommendations logic
    pass

@app.post("/api/v1/users/{user_id}/usage/bulk")
def upload_usage_data(user_id: str, data: UsageHistoryBulkCreate, db: Session = Depends(get_db)):
    # Bulk upload logic
    pass
```

---

## Testing

### Unit Test Example

```python
import pytest
from datetime import date
from decimal import Decimal
from models import User, UsageHistory
from config.database import SessionLocal

def test_create_user_with_usage():
    """Test creating a user and adding usage records."""
    db = SessionLocal()

    # Create user
    user = User(
        email="test@example.com",
        name="Test User",
        zip_code="75001",
        property_type="residential",
        consent_given=True
    )
    db.add(user)
    db.flush()

    # Add usage
    usage = UsageHistory(
        user_id=user.id,
        usage_date=date(2024, 1, 1),
        kwh_consumed=Decimal("35.5"),
        data_source="test"
    )
    db.add(usage)
    db.commit()

    # Verify
    assert user.id is not None
    assert len(user.usage_history) == 1
    assert user.usage_history[0].kwh_consumed == Decimal("35.5")

    # Cleanup
    db.delete(user)
    db.commit()
    db.close()
```

---

## Environment Setup

### .env File Template

```bash
# Database
DATABASE_URL=postgresql://treebeard:treebeard@localhost:5432/treebeard

# Redis
REDIS_URL=redis://localhost:6379/0

# API
API_V1_PREFIX=/api/v1
DEBUG=True
ENVIRONMENT=development

# Security
SECRET_KEY=your-secret-key-here

# Recommendation Engine
RECOMMENDATION_CACHE_TTL_SECONDS=86400
MAX_RECOMMENDATIONS=3

# External APIs
CLAUDE_API_KEY=your-claude-api-key
```

### Database Setup

```bash
# 1. Start PostgreSQL
docker-compose up -d postgres

# 2. Run migrations
cd src/backend
alembic upgrade head

# 3. Verify
psql postgresql://treebeard:treebeard@localhost:5432/treebeard
\dt  # List tables
```

---

## Questions & Support

For questions or issues with this contract:

1. Check the [Database Schema Documentation](/docs/database-schema.md)
2. Review the [Architecture Diagrams](/architecture.md)
3. Consult the [PRD](/PRD.md) for requirements
4. Contact Backend Dev #1 for clarifications

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-10 | Initial contract published |

---

**Contract Status:** ✅ Complete and Ready for Integration

This contract is now published and available for all dependent stories.
