# Story 2.4 & 2.5 - Savings Calculator & Comparison Features Contract

**Version:** 1.0
**Date:** November 10, 2025
**Author:** Backend Dev #4
**Status:** Complete
**Depends On:** Story 1.4 (Usage Projection), Story 2.2 (Plan Matching - via mock)
**Required By:** Story 3.2 (API Endpoints), Story 4.4 (Cost Breakdown UI)

---

## Overview

This document defines the interface contract for the Savings Calculator and Plan Comparison services (Stories 2.4 & 2.5). These services enable detailed cost analysis, savings projections, and side-by-side plan comparisons for the TreeBeard recommendation engine.

---

## Core Services

### `SavingsCalculatorService`

**Location:** `/src/backend/services/savings_calculator.py`

The main service class that provides savings analysis and plan comparison functionality.

---

## Story 2.4: Savings Calculator

### Primary Method: `calculate_annual_savings`

```python
def calculate_annual_savings(
    current_plan: CurrentPlanResponse,
    recommended_plan: PlanCatalogResponse,
    usage_projection: UsageProjection,
    user_id: UUID,
) -> SavingsAnalysis
```

**Parameters:**
- `current_plan`: User's current energy plan (from User schemas)
- `recommended_plan`: Recommended plan from catalog
- `usage_projection`: 12-month usage projection (from Story 1.4)
- `user_id`: User identifier

**Returns:** Complete `SavingsAnalysis` with:
- Annual savings calculation ($ and %)
- Month-by-month cost breakdown (12 months)
- Total Cost of Ownership (TCO)
- Break-even analysis (if switching cost exists)
- Uncertainty range (for variable rate plans)
- All fees included (monthly, connection, ETF)

**Performance:** <200ms typical

---

## Data Schemas

### Output Schema: `SavingsAnalysis`

**Location:** `/src/backend/schemas/savings_schemas.py`

Complete savings analysis with all cost comparisons and projections.

```python
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from uuid import UUID

class SavingsAnalysis(BaseModel):
    plan_id: UUID
    user_id: UUID

    # Annual cost comparison
    projected_annual_cost: Decimal
    current_annual_cost: Decimal
    annual_savings: Decimal
    savings_percentage: Decimal

    # Monthly breakdown (12 months)
    monthly_breakdown: list[MonthlyCost]

    # Total Cost of Ownership
    total_cost_of_ownership: Decimal
    tco_current_plan: Decimal
    contract_length_months: int

    # Break-even analysis
    break_even_months: Optional[int]
    switching_cost: Decimal
    cumulative_savings_12_months: Decimal

    # Variable rate uncertainty
    uncertainty_range: Optional[CostRange]
    is_variable_rate: bool

    # Fees breakdown
    total_upfront_fees: Decimal
    total_monthly_fees: Decimal
    total_energy_cost: Decimal

    # Metadata
    analysis_date: datetime
    assumptions: list[str]
    warnings: list[str]
```

### Supporting Schema: `MonthlyCost`

Month-by-month cost breakdown:

```python
class MonthlyCost(BaseModel):
    month: int  # 1-12
    year: int
    projected_kwh: Decimal
    energy_cost: Decimal
    monthly_fee: Decimal
    other_fees: Decimal
    total_cost: Decimal
```

### Supporting Schema: `CostRange`

For variable rate plans with uncertainty:

```python
class CostRange(BaseModel):
    low_estimate: Decimal
    high_estimate: Decimal
    expected_value: Decimal
    confidence_level: Decimal  # e.g., 0.95 for 95% CI
    volatility_note: Optional[str]
```

---

## Story 2.5: Comparison Features

### Primary Method: `generate_comparison`

```python
def generate_comparison(
    plans: list[RankedPlan],
    current_plan: CurrentPlanResponse,
    usage_projection: UsageProjection,
    plan_catalog: dict[UUID, PlanCatalogResponse],
    user_id: UUID,
) -> PlanComparison
```

**Parameters:**
- `plans`: Ranked plans from Story 2.2 (recommendation engine)
- `current_plan`: User's current plan for baseline
- `usage_projection`: 12-month usage projection
- `plan_catalog`: Dict mapping plan_id to full plan details
- `user_id`: User identifier

**Returns:** Complete `PlanComparison` with:
- Side-by-side comparison data for all plans
- Best plan identification by category
- Trade-off analysis
- Multi-year projections (1-3 years)

**Performance:** <300ms for 3 plans

---

### Output Schema: `PlanComparison`

**Location:** `/src/backend/schemas/savings_schemas.py`

Complete side-by-side comparison structure:

```python
class PlanComparison(BaseModel):
    comparison_id: UUID
    user_id: UUID

    # Plans being compared
    plans: list[ComparisonPlan]
    current_plan: ComparisonPlan

    # Best in category
    best_by_category: dict[str, UUID]  # category -> plan_id

    # Trade-off analysis
    trade_offs: list[TradeOffNote]

    # Multi-year projections
    multi_year_projections: dict[str, list[MultiYearProjection]]

    # Metadata
    generated_at: datetime
    projection_basis: str
    assumptions: list[str]
```

### Supporting Schema: `ComparisonPlan`

Plan data structured for comparison:

```python
class ComparisonPlan(BaseModel):
    plan_id: UUID
    plan_name: str
    supplier_name: str

    # Cost metrics
    annual_cost: Decimal
    monthly_average: Decimal
    first_year_total: Decimal

    # Contract terms
    contract_length_months: int
    early_termination_fee: Decimal
    monthly_fee: Decimal

    # Plan attributes
    renewable_percentage: Decimal
    plan_type: str
    rate_per_kwh: Optional[Decimal]

    # Supplier rating
    supplier_rating: Optional[Decimal]

    # Savings vs current
    savings_vs_current_annual: Decimal
    savings_vs_current_percentage: Decimal

    # Rank and scores
    rank: Optional[int]
    composite_score: Optional[Decimal]

    # Comparison indicators
    is_current_plan: bool
    is_recommended: bool
```

### Supporting Schema: `TradeOffNote`

Trade-off analysis between plans:

```python
class TradeOffNote(BaseModel):
    category: str  # cost, contract, renewable, flexibility, rating
    description: str
    affected_plans: list[UUID]
    severity: str  # info, warning, critical
```

### Supporting Schema: `MultiYearProjection`

Cost projection over multiple years:

```python
class MultiYearProjection(BaseModel):
    year: int  # 1-3
    annual_cost: Decimal
    cumulative_cost: Decimal
    cumulative_savings: Decimal
    notes: list[str]
```

---

## Usage Examples

### Example 1: Calculate Savings for Top Recommendation

```python
from uuid import UUID
from src.backend.services.savings_calculator import SavingsCalculatorService
from src.backend.schemas.user import CurrentPlanResponse
from src.backend.schemas.plan import PlanCatalogResponse
from src.backend.schemas.usage_schemas import UsageProjection

# Initialize service
service = SavingsCalculatorService()

# Assume we have these from previous steps
current_plan: CurrentPlanResponse = ...  # User's current plan
recommended_plan: PlanCatalogResponse = ...  # Top recommendation
usage_projection: UsageProjection = ...  # From Story 1.4
user_id: UUID = ...

# Calculate savings
savings = service.calculate_annual_savings(
    current_plan=current_plan,
    recommended_plan=recommended_plan,
    usage_projection=usage_projection,
    user_id=user_id,
)

# Access results
print(f"Annual Savings: ${savings.annual_savings:.2f}")
print(f"Savings Percentage: {savings.savings_percentage:.1f}%")
print(f"Break-even: {savings.break_even_months} months")
print(f"Total Cost of Ownership: ${savings.total_cost_of_ownership:.2f}")

# Check for warnings
for warning in savings.warnings:
    print(f"⚠️  {warning}")

# Access monthly breakdown
for month_cost in savings.monthly_breakdown:
    print(f"Month {month_cost.month}: ${month_cost.total_cost:.2f}")
```

### Example 2: Generate Side-by-Side Comparison

```python
from src.backend.services.savings_calculator import SavingsCalculatorService
from src.backend.schemas.savings_schemas import RankedPlan, RecommendationResult

# Initialize service
service = SavingsCalculatorService()

# Get recommendations from Story 2.2
recommendation_result: RecommendationResult = ...  # From Story 2.2
ranked_plans: list[RankedPlan] = recommendation_result.top_plans

# Get plan details
plan_catalog: dict[UUID, PlanCatalogResponse] = ...  # Full plan details

# Generate comparison
comparison = service.generate_comparison(
    plans=ranked_plans,
    current_plan=current_plan,
    usage_projection=usage_projection,
    plan_catalog=plan_catalog,
    user_id=user_id,
)

# Identify best in each category
best_cost_id = comparison.best_by_category["lowest_cost"]
best_renewable_id = comparison.best_by_category["highest_renewable"]
best_flexible_id = comparison.best_by_category["most_flexible"]

print(f"Best Cost: {best_cost_id}")
print(f"Best Renewable: {best_renewable_id}")
print(f"Most Flexible: {best_flexible_id}")

# Review trade-offs
for trade_off in comparison.trade_offs:
    print(f"{trade_off.category.upper()}: {trade_off.description}")

# Multi-year outlook
for plan_id_str, projections in comparison.multi_year_projections.items():
    print(f"\nPlan {plan_id_str}:")
    for proj in projections:
        print(f"  Year {proj.year}: ${proj.annual_cost:.2f} "
              f"(Cumulative savings: ${proj.cumulative_savings:.2f})")
```

### Example 3: Integration with Story 2.2 (Recommendation Engine)

```python
# Complete flow: Recommendation → Savings → Comparison

# Step 1: Get recommendations (from Story 2.2)
recommendation_result = recommendation_engine.generate_recommendations(
    user_id=user_id,
    usage_profile=usage_profile,
    preferences=user_preferences,
)

# Step 2: Calculate savings for top plan (Story 2.4)
top_plan = recommendation_result.top_plans[0]
full_plan = plan_catalog[top_plan.plan_id]

savings = savings_service.calculate_annual_savings(
    current_plan=current_plan,
    recommended_plan=full_plan,
    usage_projection=usage_projection,
    user_id=user_id,
)

# Step 3: Generate comparison for all top 3 (Story 2.5)
comparison = savings_service.generate_comparison(
    plans=recommendation_result.top_plans,
    current_plan=current_plan,
    usage_projection=usage_projection,
    plan_catalog=plan_catalog,
    user_id=user_id,
)

# Now you have complete data for UI display
return {
    "recommendations": recommendation_result,
    "top_plan_savings": savings,
    "comparison": comparison,
}
```

---

## Mock Data for Testing (Story 2.2 Integration)

Until Backend Dev #3 publishes the Story 2.2 contract, use these mock structures:

### `RankedPlan` (Temporary Mock)

```python
from pydantic import BaseModel
from decimal import Decimal
from uuid import UUID

class RankedPlan(BaseModel):
    plan_id: UUID
    rank: int  # 1-3
    composite_score: Decimal  # 0.0-1.0
    cost_score: Decimal
    flexibility_score: Decimal
    renewable_score: Decimal
    rating_score: Decimal
    projected_annual_cost: Decimal
```

### `RecommendationResult` (Temporary Mock)

```python
from datetime import datetime

class RecommendationResult(BaseModel):
    user_id: UUID
    top_plans: list[RankedPlan]  # Top 3 plans
    generated_at: datetime
```

**⚠️ Important:** Replace these mocks when `/docs/contracts/story-2.2-contract.md` is published by Backend Dev #3.

---

## Integration Checklist for Story 3.2 (API Endpoints)

- [ ] Import `SavingsCalculatorService` from `backend.services.savings_calculator`
- [ ] Import schemas from `backend.schemas.savings_schemas`
- [ ] Create endpoint: `POST /api/v1/savings/calculate`
- [ ] Create endpoint: `POST /api/v1/comparison/generate`
- [ ] Handle `CurrentPlanResponse` input from user data
- [ ] Handle `PlanCatalogResponse` input from plan catalog
- [ ] Handle `UsageProjection` input from Story 1.4
- [ ] Handle `RankedPlan` input from Story 2.2 (update when contract published)
- [ ] Implement error handling for missing plans
- [ ] Add response caching (24-hour TTL)
- [ ] Add input validation for all parameters
- [ ] Write API integration tests

---

## Integration Checklist for Story 4.4 (Cost Breakdown UI)

- [ ] Display annual savings prominently ($ and %)
- [ ] Show month-by-month cost breakdown (chart or table)
- [ ] Display Total Cost of Ownership comparison
- [ ] Show break-even timeline (if ETF exists)
- [ ] Display uncertainty range for variable rate plans
- [ ] Render all warnings from `savings.warnings`
- [ ] Show assumptions used in calculations
- [ ] Implement side-by-side plan comparison table
- [ ] Highlight "best in category" badges
- [ ] Display trade-off notes
- [ ] Show multi-year projections (expandable)
- [ ] Add tooltips for technical terms (TCO, ETF, etc.)

---

## Fee Handling

All savings calculations include:

1. **Upfront Fees:**
   - Connection fee (one-time)
   - Switching cost / ETF (if applicable)

2. **Recurring Fees:**
   - Monthly base fee
   - Energy cost (kWh × rate)

3. **Total Cost of Ownership includes:**
   - All energy costs over contract period
   - All monthly fees over contract period
   - Connection fee (one-time)
   - Does NOT include current plan's ETF (shown separately)

---

## Variable Rate Uncertainty

For variable rate plans (`plan_type` = "variable" or "indexed"):

- **Default Volatility:** ±10% for variable, ±15% for indexed
- **Confidence Interval:** 95% (configurable)
- **Cost Range:** Provides low estimate, expected value, high estimate
- **Warning:** Always includes warning about rate volatility risk

Users can update volatility assumptions via configuration:

```python
service = SavingsCalculatorService()
service.default_variable_rate_volatility = Decimal("0.12")  # ±12%
```

---

## Break-Even Analysis

Break-even calculation logic:

1. **If switching_cost > 0:**
   - Calculate monthly savings: `annual_savings / 12`
   - Calculate months to offset: `switching_cost / monthly_savings`
   - Round up to next whole month
   - Return `break_even_months`

2. **If switching_cost = 0:**
   - Return `0` (immediate break-even)

3. **If annual_savings <= 0:**
   - Return `None` (never breaks even)

---

## Seasonal Variation Handling

The service uses `usage_projection.projected_monthly_kwh` from Story 1.4, which already accounts for:
- Seasonal patterns (summer/winter peaks)
- Historical usage trends
- User profile classification

This ensures accurate monthly cost calculations that reflect real usage patterns.

---

## Performance Characteristics

- **Savings Calculation:** <200ms typical
- **Comparison Generation:** <300ms for 3 plans
- **Memory:** ~1MB per analysis
- **Cache Recommended:** 24-hour TTL for computed savings
- **Concurrency:** Thread-safe, can process multiple users in parallel

---

## Error Handling

The service handles:

1. **Missing Plan Data:** Skips plans not found in catalog
2. **Invalid Rate Structure:** Falls back to simple rate calculation
3. **Missing Fees:** Defaults to $0.00 for optional fees
4. **Zero Usage:** Handles vacant properties correctly
5. **Negative Savings:** Generates appropriate warnings

All errors are logged; calculations continue with best available data.

---

## Best Practices

### For Backend Dev #5 (API Endpoints):

1. **Cache Results:** Savings calculations don't change often
   ```python
   cache_key = f"savings:{user_id}:{plan_id}"
   ttl = 24 * 60 * 60  # 24 hours
   ```

2. **Validate Inputs:** Ensure plan exists in catalog before calculating

3. **Handle Timeouts:** Set reasonable timeouts for bulk calculations

4. **Return Partial Results:** If one plan fails, return others

### For Frontend Dev #1 (Cost Breakdown UI):

1. **Highlight Savings:** Use green for positive, red for negative
2. **Explain Warnings:** Don't just display, add context
3. **Visualize Monthly Costs:** Charts work better than tables
4. **Show Confidence:** For variable rates, show ranges clearly
5. **Progressive Disclosure:** Show summary, expand for details

---

## Dependencies

### Required Python Packages

```
pydantic>=2.0.0
```

### Internal Dependencies

- `backend.schemas.plan` (Plan catalog schemas)
- `backend.schemas.user` (User and current plan schemas)
- `backend.schemas.usage_schemas` (Usage projection from Story 1.4)
- `backend.schemas.savings_schemas` (This module's schemas)

### External Dependencies

- Story 1.4: `UsageProjection` (usage analysis)
- Story 2.2: `RankedPlan`, `RecommendationResult` (recommendations)

---

## Testing

### Unit Tests

**Location:** `/tests/backend/test_savings_calculator.py`

Coverage includes:
- Annual savings calculation accuracy
- Monthly breakdown correctness
- TCO calculation with all fees
- Break-even analysis logic
- Variable rate uncertainty ranges
- Plan comparison generation
- Best category identification
- Trade-off analysis
- Multi-year projections
- Edge cases (negative savings, zero ETF, etc.)

Run tests:
```bash
pytest tests/backend/test_savings_calculator.py -v
```

### Integration Tests

**Location:** `/tests/integration/test_recommendation_savings.py`

Coverage includes:
- Story 2.2 → Story 2.4 integration
- Story 2.2 → Story 2.5 integration
- End-to-end recommendation flow
- Data consistency across services
- Complete decision support data

Run integration tests:
```bash
pytest tests/integration/test_recommendation_savings.py -v
```

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-10 | Initial contract release |

---

## Support

For questions or issues:
- **Author:** Backend Dev #4
- **Stories:** 2.4 (Savings Calculator), 2.5 (Comparison Features)
- **Epic:** 2 - Data Analysis & Personalization

**Next Steps:**
1. ✅ Review this contract
2. ✅ Run unit tests to verify implementation
3. ⏳ Wait for Story 2.2 contract from Backend Dev #3
4. ⏳ Update mocks with actual Story 2.2 schemas
5. ⏳ Backend Dev #5: Create API endpoints
6. ⏳ Frontend Dev #1: Build cost breakdown UI

---

**End of Contract Document**
