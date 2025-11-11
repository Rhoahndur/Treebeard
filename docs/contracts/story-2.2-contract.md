# Story 2.2 - Plan Matching & Ranking Contract

**Version:** 1.0.0
**Date:** November 10, 2025
**Author:** Backend Dev #3
**Status:** Complete
**Epic:** 2 - Recommendation Core

---

## Purpose

This contract defines the interface for the Plan Matching & Ranking service (Story 2.2), which is the core recommendation engine. This contract is required by:

- **Story 2.4** - Savings Calculator (Backend Dev #4)
- **Story 2.6** - Claude API Integration (ML Engineer)
- **Story 3.2** - API Endpoints (Backend Dev #5)
- **Frontend** - Recommendation display

---

## Table of Contents

1. [Core Service](#core-service)
2. [Data Schemas](#data-schemas)
3. [Usage Examples](#usage-examples)
4. [Integration Points](#integration-points)
5. [Performance Characteristics](#performance-characteristics)
6. [Testing](#testing)

---

## Core Service

### `RecommendationEngine`

**Location:** `/src/backend/services/recommendation_engine.py`

The main recommendation engine that filters, scores, and ranks energy plans.

### Primary Functions

#### `get_recommendations()`

```python
def get_recommendations(
    user_id: UUID,
    usage_profile: UsageProjection,
    preferences: UserPreferences,
    db: Session,
    zip_code: str,
    top_n: int = 3
) -> RecommendationResult
```

**Purpose:** Generate top N plan recommendations for a user (Story 2.2 core function).

**Parameters:**
- `user_id`: User identifier
- `usage_profile`: Usage projection from Story 1.4 analysis
- `preferences`: User preference weights (cost, flexibility, renewable, rating)
- `db`: Database session for plan queries
- `zip_code`: User's ZIP code for regional filtering
- `top_n`: Number of recommendations to return (default: 3)

**Returns:** `RecommendationResult` with top plans and scores

**Performance:** <500ms for 1000 plans

**Example:**
```python
from backend.services.recommendation_engine import get_recommendations
from backend.schemas.recommendation_schemas import UserPreferences
from backend.schemas.usage_analysis import UsageProjection

# Create usage projection (from Story 1.4)
usage_profile = UsageProjection(
    projected_monthly_kwh=[850.0, 820.0, 780.0, 900.0, 950.0, 1400.0,
                           1600.0, 1500.0, 1000.0, 850.0, 800.0, 820.0],
    projected_annual_kwh=12270.0,
    confidence_score=0.85
)

# Create user preferences
preferences = UserPreferences(
    cost_priority=40,
    flexibility_priority=30,
    renewable_priority=20,
    rating_priority=10
)

# Get recommendations
result = get_recommendations(
    user_id=user_id,
    usage_profile=usage_profile,
    preferences=preferences,
    db=db_session,
    zip_code="75001",
    top_n=3
)

# Access top plans
for plan in result.top_plans:
    print(f"Rank {plan.rank}: {plan.plan_name}")
    print(f"  Composite Score: {plan.scores.composite_score:.1f}")
    print(f"  Annual Cost: ${plan.projected_annual_cost:.2f}")
```

---

#### `get_enhanced_recommendations()` (Story 2.3)

```python
def get_enhanced_recommendations(
    user_id: UUID,
    usage_profile: UsageProjection,
    preferences: UserPreferences,
    db: Session,
    zip_code: str,
    current_plan: Optional[CurrentPlan] = None,
    top_n: int = 3
) -> EnhancedRecommendationResult
```

**Purpose:** Generate recommendations with switching timing analysis (Story 2.3).

**Additional Parameters:**
- `current_plan`: User's current plan for switching analysis

**Returns:** `EnhancedRecommendationResult` with switching analysis

**Example:**
```python
from backend.services.recommendation_engine import get_enhanced_recommendations

# Get enhanced recommendations with switching analysis
result = get_enhanced_recommendations(
    user_id=user_id,
    usage_profile=usage_profile,
    preferences=preferences,
    db=db_session,
    zip_code="75001",
    current_plan=current_plan,
    top_n=3
)

# Check switching analysis
if result.switching_analysis:
    print(f"Monthly Savings: ${result.switching_analysis.monthly_savings:.2f}")
    print(f"Should Wait: {result.switching_analysis.should_wait}")
    print(f"Recommendation: {result.switching_analysis.switching_recommendation}")
```

---

## Data Schemas

### Input Schemas

#### `UserPreferences`

```python
@dataclass
class UserPreferences:
    """User preference weights for scoring (must sum to 100)."""
    cost_priority: int = 40
    flexibility_priority: int = 30
    renewable_priority: int = 20
    rating_priority: int = 10
```

**Default values from PRD:** cost=40%, flexibility=30%, renewable=20%, rating=10%

---

#### `PlanFilter`

```python
@dataclass
class PlanFilter:
    """Criteria for filtering eligible plans."""
    zip_code: str  # Required
    is_active: bool = True
    max_contract_length: Optional[int] = None
    min_renewable_percentage: Optional[Decimal] = None
    plan_types: Optional[List[str]] = None
```

---

### Output Schemas

#### `RankedPlan`

**The primary output for a single recommended plan.**

```python
@dataclass
class RankedPlan:
    """A plan with its ranking and scoring details."""
    plan_id: UUID
    rank: int  # 1, 2, or 3

    # Plan details
    plan_name: str
    supplier_name: str
    plan_type: str
    contract_length_months: int
    early_termination_fee: Decimal
    renewable_percentage: Decimal

    # Scores
    scores: PlanScores

    # Cost analysis
    projected_annual_cost: Decimal
    projected_monthly_cost: Decimal
    cost_breakdown: CostBreakdown

    # Additional details
    rate_structure: Dict[str, Any]
    monthly_fee: Optional[Decimal] = None
    connection_fee: Optional[Decimal] = None
```

**Key Fields:**
- `rank`: 1 (best), 2 (second), 3 (third)
- `scores.composite_score`: Overall score (0-100)
- `projected_annual_cost`: Total annual cost including all fees

---

#### `PlanScores`

```python
@dataclass
class PlanScores:
    """Individual factor scores and composite score (all 0-100)."""
    cost_score: float
    flexibility_score: float
    renewable_score: float
    rating_score: float
    composite_score: float
```

**All scores are 0-100, where higher is better.**

---

#### `CostBreakdown`

```python
@dataclass
class CostBreakdown:
    """Detailed cost breakdown for a plan."""
    base_cost: Decimal  # Cost based on usage and rate
    monthly_fees: Decimal  # Total annual monthly fees (monthly_fee * 12)
    connection_fee: Decimal  # One-time connection fee
    total_annual_cost: Decimal  # Sum of all costs
    rate_type: str  # Type of rate structure
    avg_rate_per_kwh: Decimal  # Effective average rate
```

---

#### `RecommendationResult`

**The main output contract for Story 2.2.**

```python
@dataclass
class RecommendationResult:
    """Complete recommendation result for a user."""
    user_id: UUID
    top_plans: List[RankedPlan]  # Top 3 plans (or fewer if <3 available)

    # Metadata
    generated_at: datetime
    usage_profile_summary: Dict[str, Any]  # Summary from Story 1.4

    # Statistics
    total_plans_analyzed: int
    total_plans_eligible: int
```

**Example Response:**
```python
RecommendationResult(
    user_id=UUID('...'),
    top_plans=[
        RankedPlan(rank=1, plan_name='Solar Saver 12', composite_score=91.2, ...),
        RankedPlan(rank=2, plan_name='Green Power Plus', composite_score=88.5, ...),
        RankedPlan(rank=3, plan_name='Flex Energy', composite_score=85.1, ...)
    ],
    generated_at=datetime(2025, 11, 10, 14, 30, 0),
    usage_profile_summary={
        'projected_annual_kwh': 12270.0,
        'confidence_score': 0.85
    },
    total_plans_analyzed=156,
    total_plans_eligible=156
)
```

---

#### `EnhancedRecommendationResult` (Story 2.3)

**Extends `RecommendationResult` with switching analysis.**

```python
@dataclass
class EnhancedRecommendationResult(RecommendationResult):
    """Enhanced result with switching timing analysis."""
    switching_analysis: Optional[SwitchingAnalysis] = None
    stay_with_current: bool = False
    stay_reason: Optional[str] = None
```

---

#### `SwitchingAnalysis` (Story 2.3)

```python
@dataclass
class SwitchingAnalysis:
    """Analysis of switching costs and optimal timing."""
    current_contract_end_date: date
    days_until_contract_end: int
    early_termination_fee: Decimal

    # Break-even analysis
    monthly_savings: Decimal
    break_even_months: Optional[int]  # None if negative savings

    # Recommendation
    should_wait: bool
    optimal_switch_date: date
    switching_recommendation: str  # Plain-language explanation
```

**Example:**
```python
SwitchingAnalysis(
    current_contract_end_date=date(2026, 3, 15),
    days_until_contract_end=125,
    early_termination_fee=Decimal('200.00'),
    monthly_savings=Decimal('25.50'),
    break_even_months=8,
    should_wait=False,
    optimal_switch_date=date(2025, 11, 10),
    switching_recommendation="Save $25.50/month ($306/year). Worth paying $200 ETF. Break-even in 8 months."
)
```

---

## Usage Examples

### Example 1: Basic Recommendation Flow

```python
from backend.services.recommendation_engine import get_recommendations
from backend.schemas.recommendation_schemas import UserPreferences
from backend.schemas.usage_analysis import UsageProjection
from backend.config.database import get_db

# Step 1: Get user's usage profile (from Story 1.4)
# Assume you've already called UsageAnalysisService.analyze_usage_patterns()
usage_profile = UsageProjection(
    projected_monthly_kwh=[...],  # 12 months
    projected_annual_kwh=12270.0,
    confidence_score=0.85
)

# Step 2: Get user preferences (from database or use defaults)
preferences = UserPreferences(
    cost_priority=40,
    flexibility_priority=30,
    renewable_priority=20,
    rating_priority=10
)

# Step 3: Generate recommendations
db = next(get_db())
result = get_recommendations(
    user_id=user_id,
    usage_profile=usage_profile,
    preferences=preferences,
    db=db,
    zip_code="75001",
    top_n=3
)

# Step 4: Use the results
for plan in result.top_plans:
    print(f"Rank {plan.rank}: {plan.plan_name} by {plan.supplier_name}")
    print(f"  Score: {plan.scores.composite_score:.1f}/100")
    print(f"  Cost: ${plan.projected_annual_cost:.2f}/year")
    print(f"  Renewable: {plan.renewable_percentage}%")
    print(f"  Contract: {plan.contract_length_months} months")
    print()
```

---

### Example 2: Custom Preferences (Green Energy Focus)

```python
# User who prioritizes renewable energy
green_preferences = UserPreferences(
    cost_priority=10,
    flexibility_priority=10,
    renewable_priority=70,  # 70% weight on renewable
    rating_priority=10
)

result = get_recommendations(
    user_id=user_id,
    usage_profile=usage_profile,
    preferences=green_preferences,
    db=db,
    zip_code="75001",
    top_n=3
)

# Top plan will likely have high renewable %
best_plan = result.top_plans[0]
print(f"Best green plan: {best_plan.plan_name}")
print(f"Renewable: {best_plan.renewable_percentage}%")
print(f"Renewable Score: {best_plan.scores.renewable_score:.1f}/100")
```

---

### Example 3: With Switching Analysis (Story 2.3)

```python
from backend.services.recommendation_engine import get_enhanced_recommendations
from backend.models.user import CurrentPlan

# Get user's current plan
current_plan = db.query(CurrentPlan).filter(
    CurrentPlan.user_id == user_id
).first()

# Get enhanced recommendations
result = get_enhanced_recommendations(
    user_id=user_id,
    usage_profile=usage_profile,
    preferences=preferences,
    db=db,
    zip_code="75001",
    current_plan=current_plan,
    top_n=3
)

# Check if should switch
if result.stay_with_current:
    print(f"Recommendation: Stay with current plan")
    print(f"Reason: {result.stay_reason}")
else:
    if result.switching_analysis:
        print(f"Recommendation: {result.switching_analysis.switching_recommendation}")
        print(f"Monthly Savings: ${result.switching_analysis.monthly_savings:.2f}")
        print(f"Break-even: {result.switching_analysis.break_even_months} months")
```

---

### Example 4: Accessing Cost Breakdown

```python
result = get_recommendations(...)

for plan in result.top_plans:
    breakdown = plan.cost_breakdown

    print(f"{plan.plan_name} Cost Breakdown:")
    print(f"  Base Cost: ${breakdown.base_cost:.2f}")
    print(f"  Monthly Fees (annual): ${breakdown.monthly_fees:.2f}")
    print(f"  Connection Fee: ${breakdown.connection_fee:.2f}")
    print(f"  Total Annual: ${breakdown.total_annual_cost:.2f}")
    print(f"  Rate Type: {breakdown.rate_type}")
    print(f"  Avg Rate: {breakdown.avg_rate_per_kwh:.2f}¢/kWh")
```

---

## Integration Points

### For Backend Dev #4 (Story 2.4 - Savings Calculator)

**You will need:**

1. **Import the service:**
   ```python
   from backend.services.recommendation_engine import get_recommendations
   ```

2. **Use RankedPlan for savings calculation:**
   ```python
   result = get_recommendations(...)

   for plan in result.top_plans:
       # plan.projected_annual_cost - current plan cost
       annual_savings = current_plan_cost - plan.projected_annual_cost
       monthly_savings = annual_savings / 12

       # You have access to:
       # - plan.cost_breakdown (detailed costs)
       # - plan.projected_monthly_cost (monthly cost)
   ```

3. **Key fields for savings:**
   - `plan.projected_annual_cost`: Total annual cost
   - `plan.cost_breakdown`: Detailed breakdown
   - `plan.scores.cost_score`: Cost score (0-100)

---

### For ML Engineer (Story 2.6 - Claude API Integration)

**You will need:**

1. **Import schemas:**
   ```python
   from backend.schemas.recommendation_schemas import (
       RecommendationResult,
       RankedPlan,
       PlanScores
   )
   ```

2. **Use recommendations for explanation generation:**
   ```python
   result = get_recommendations(...)

   for plan in result.top_plans:
       # Generate explanation using:
       explanation = generate_explanation(
           plan_name=plan.plan_name,
           supplier_name=plan.supplier_name,
           scores=plan.scores,
           cost=plan.projected_annual_cost,
           renewable_pct=plan.renewable_percentage,
           contract_length=plan.contract_length_months,
           user_preferences=preferences
       )
   ```

3. **Explanation inputs available:**
   - All scoring factors (cost, flexibility, renewable, rating)
   - Plan details (name, supplier, type, contract)
   - Cost analysis (annual, monthly, breakdown)
   - User preferences (to personalize explanations)

---

### For Backend Dev #5 (Story 3.2 - API Endpoints)

**You will need:**

1. **Create FastAPI endpoint:**
   ```python
   from fastapi import APIRouter, Depends
   from backend.services.recommendation_engine import get_enhanced_recommendations
   from backend.schemas.recommendation_schemas import EnhancedRecommendationResult

   router = APIRouter()

   @router.post("/recommendations", response_model=EnhancedRecommendationResult)
   async def generate_recommendations(
       user_id: UUID,
       preferences: UserPreferences,
       db: Session = Depends(get_db)
   ):
       # Get user data
       user = db.query(User).filter(User.id == user_id).first()
       current_plan = user.current_plan

       # Get usage profile (from Story 1.4 service)
       usage_profile = analyze_usage(user_id, db)

       # Generate recommendations
       result = get_enhanced_recommendations(
           user_id=user_id,
           usage_profile=usage_profile,
           preferences=preferences,
           db=db,
           zip_code=user.zip_code,
           current_plan=current_plan
       )

       return result
   ```

---

## Rate Structure Support

The recommendation engine supports all rate types defined in the PRD:

### Fixed Rate

```python
rate_structure = {
    'type': 'fixed',
    'rate_per_kwh': 12.5  # cents per kWh
}
```

Cost calculation: `rate_per_kwh * annual_kwh`

---

### Tiered Rate

```python
rate_structure = {
    'type': 'tiered',
    'tiers': [
        {'max_kwh': 1000, 'rate_per_kwh': 8.0},
        {'max_kwh': 2000, 'rate_per_kwh': 10.0},
        {'max_kwh': float('inf'), 'rate_per_kwh': 12.0}
    ]
}
```

Cost calculation: Sum costs per tier based on usage levels

---

### Time-of-Use Rate

```python
rate_structure = {
    'type': 'time_of_use',
    'peak_rate': 15.0,
    'off_peak_rate': 8.0,
    'peak_hours': [14, 15, 16, 17, 18, 19],
    'peak_pct': 0.5  # 50% of usage during peak
}
```

Cost calculation: `(peak_kwh * peak_rate) + (off_peak_kwh * off_peak_rate)`

---

### Variable Rate

```python
rate_structure = {
    'type': 'variable',
    'base_rate': 10.0,
    'historical_avg_rate': 12.0
}
```

Cost calculation: Historical average with uncertainty buffer

---

## Performance Characteristics

**Measured Performance:**
- **Plan Filtering:** <100ms for 1000 plans
- **Cost Calculation:** <5ms per plan
- **Scoring:** <2ms per plan
- **Complete Recommendation:** <500ms for 1000 plans
- **Memory:** ~50MB for 1000 plans

**Optimization Techniques:**
- Database indexes on `available_regions`, `is_active`, `plan_type`
- Bulk cost calculation before scoring
- In-memory sorting and ranking
- Optional Redis caching (7-day TTL)

**Scalability:**
- Handles 10,000+ plans efficiently
- Thread-safe for concurrent requests
- Can process multiple users in parallel

---

## Testing

### Unit Tests

Located at: `/tests/backend/test_recommendation_engine.py`

**Coverage:** >80% for all recommendation engine functions

**Key test categories:**
1. **Scoring Tests:** All four factors (cost, flexibility, renewable, rating)
2. **Cost Calculation Tests:** All rate types (fixed, tiered, time-of-use, variable)
3. **Ranking Tests:** Tie-breaking, preference weighting
4. **Switching Analysis Tests:** ETF, break-even, timing recommendations
5. **Determinism Tests:** Same inputs = same outputs
6. **Edge Case Tests:** Missing data, zero values, extremes

**Run tests:**
```bash
pytest tests/backend/test_recommendation_engine.py -v
```

---

### Mock Data for Testing

```python
# Mock usage projection
usage_profile = UsageProjection(
    projected_monthly_kwh=[850.0] * 12,
    projected_annual_kwh=10200.0,
    confidence_score=0.85
)

# Mock preferences
preferences = UserPreferences(
    cost_priority=40,
    flexibility_priority=30,
    renewable_priority=20,
    rating_priority=10
)
```

---

## Error Handling

The recommendation engine handles edge cases gracefully:

1. **No eligible plans:** Returns empty `top_plans` list
2. **Fewer than 3 plans:** Returns available plans (1 or 2)
3. **Missing rate structure:** Falls back to fixed rate calculation
4. **Invalid plan data:** Logs warning, skips plan
5. **Low confidence usage:** Applies uncertainty buffer to variable rates

**All errors are logged but don't crash the service.**

---

## Dependencies

### Internal Dependencies
- Story 1.1: Database models (`PlanCatalog`, `Supplier`, `User`, `CurrentPlan`)
- Story 1.4: Usage analysis schemas (`UsageProjection`)
- Story 2.1: Scoring service

### External Dependencies
- SQLAlchemy (database ORM)
- Decimal (for precise currency calculations)
- Python standard library (datetime, logging, typing)

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-10 | Initial contract release |

---

## Support

For questions or issues with this contract:
- **Author:** Backend Dev #3
- **Story:** 2.2 - Plan Matching & Ranking
- **Epic:** 2 - Recommendation Core
- **Location:** `/src/backend/services/recommendation_engine.py`

---

**Contract Status:** ✅ Complete and Ready for Integration

This contract is now published and available for all dependent stories (2.4, 2.6, 3.2).
