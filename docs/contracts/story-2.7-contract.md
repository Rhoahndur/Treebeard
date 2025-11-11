# Story 2.7 - Plan Explanation Generation Interface Contract

**Version:** 1.0
**Date:** November 10, 2025
**Author:** ML Engineer (Epic 2 - Stories 2.6, 2.7, 2.8)
**Status:** Complete
**Depends On:** Story 1.4 (Usage Profile), Story 2.2 (Recommendation Result - to be published)
**Required By:** Story 3.2 (API Endpoints), Story 4.2 (Plan Card UI)

---

## Overview

This document defines the interface contract for the AI-powered Explanation Generation service (Stories 2.6, 2.7, 2.8). This contract enables other services to generate personalized, natural language explanations for energy plan recommendations using Claude API with template-based fallback and Redis caching.

---

## Core Service

### `ClaudeExplanationService`

**Location:** `/src/backend/services/explanation_service.py`

The main service class that generates AI-powered explanations with persona-based personalization, readability optimization, and caching.

#### Primary Method

```python
async def generate_explanation(
    plan: RankedPlan,
    user_profile: Dict[str, Any],
    preferences: UserPreferences,
    current_plan: Optional[CurrentPlan] = None,
    force_regenerate: bool = False,
) -> PlanExplanation
```

**Parameters:**
- `plan`: The ranked plan to explain
- `user_profile`: User's usage profile (from Story 1.4)
- `preferences`: User's stated preferences
- `current_plan`: Optional current plan for comparison
- `force_regenerate`: Skip cache and force regeneration

**Returns:** Complete `PlanExplanation` with all details

**Performance:**
- Cached: <50ms
- Uncached (Claude API): <2 seconds
- Fallback (Template): <100ms

**Behavior:**
1. Checks Redis cache for existing explanation
2. If not cached, generates via Claude API
3. If API fails, falls back to template-based generation
4. Calculates readability score (target: >60)
5. Identifies key differentiators and trade-offs
6. Caches result for 24 hours
7. Tracks metrics

---

## Data Schemas

### Input Schemas

#### `RankedPlan`

**Location:** `/src/backend/schemas/explanation_schemas.py`

Complete plan information needed for explanation generation.

```python
@dataclass
class RankedPlan(BaseModel):
    plan_id: UUID
    rank: int  # 1-3
    plan_name: str
    supplier_name: str
    plan_type: str  # "fixed", "variable", "tiered", "time_of_use"

    # Scores
    composite_score: Decimal  # 0-100
    cost_score: Decimal  # 0-100
    flexibility_score: Decimal  # 0-100
    renewable_score: Decimal  # 0-100
    rating_score: Decimal  # 0-100

    # Financial details
    projected_annual_cost: Decimal
    projected_annual_savings: Optional[Decimal]  # vs current plan
    break_even_months: Optional[int]

    # Plan details
    contract_length_months: int  # 0 = month-to-month
    early_termination_fee: Decimal
    renewable_percentage: Decimal  # 0-100
    monthly_fee: Optional[Decimal]

    # Rate structure
    rate_structure: dict[str, Any]
    average_rate: Optional[Decimal]

    # Risk flags
    risk_flags: Optional[dict[str, Any]]
```

#### `UserPreferences`

**Location:** `/src/backend/schemas/explanation_schemas.py`

User's stated priorities for plan selection.

```python
@dataclass
class UserPreferences(BaseModel):
    cost_priority: int  # 0-100
    flexibility_priority: int  # 0-100
    renewable_priority: int  # 0-100
    rating_priority: int  # 0-100

    def get_persona_type(self) -> str:
        """Determine user persona based on priorities."""
        # Returns: "budget_conscious", "eco_conscious",
        #          "flexibility_focused", or "balanced"
```

**Persona Detection Logic:**
- `cost_priority > 50` → Budget-Conscious
- `renewable_priority > 50` → Eco-Conscious
- `flexibility_priority > 50` → Flexibility-Focused
- Otherwise → Balanced

#### `CurrentPlan`

**Location:** `/src/backend/schemas/explanation_schemas.py`

Current plan information for comparison.

```python
@dataclass
class CurrentPlan(BaseModel):
    plan_name: Optional[str]
    supplier_name: Optional[str]
    annual_cost: Optional[Decimal]
    contract_end_date: Optional[datetime]
    early_termination_fee: Optional[Decimal]
```

---

### Output Schema

#### `PlanExplanation`

**Location:** `/src/backend/schemas/explanation_schemas.py`

Complete explanation with all metadata.

```python
@dataclass
class PlanExplanation(BaseModel):
    plan_id: UUID
    explanation_text: str  # 2-3 sentences, 8th grade reading level
    key_differentiators: List[str]  # What makes this plan stand out
    trade_offs: List[str]  # Important compromises or considerations
    persona_type: str  # User persona detected
    readability_score: float  # Flesch-Kincaid score (0-100)
    generated_via: str  # "claude_api" or "template"
    generated_at: datetime
```

**Explanation Text Requirements:**
- Length: 2-3 sentences (100-300 words)
- Reading level: 8th grade (Flesch-Kincaid score >60)
- Tone: Friendly, conversational, specific
- Format: Active voice, concrete numbers, minimal jargon
- Content: Why plan matches needs, key benefits, one trade-off

**Key Differentiators (max 3):**
- "Lowest cost option"
- "100% renewable energy"
- "No contract commitment"
- "Top-rated supplier"
- "Fixed rate for price stability"

**Trade-offs (max 3):**
- "Early termination fee of $150"
- "12-month contract commitment"
- "Rate can change based on market conditions"
- "Costs $50 more per year for renewable energy"

---

## Persona-Based Messaging

### Budget-Conscious Persona

**Detection:** `cost_priority > 50`

**Messaging Focus:**
- Emphasize dollar savings and ROI
- Use specific dollar amounts prominently
- Highlight cost comparisons
- Mention break-even periods
- Tone: Practical, numbers-driven

**Example:**
```
This plan will save you $425 per year compared to your current plan, which is 18%
less. Based on your average usage of 950 kWh per month, you'll pay a predictable
rate with no surprise charges. Keep in mind there's a $150 cancellation fee if you
need to end the contract early, but you'll break even in just 5 months.
```

### Eco-Conscious Persona

**Detection:** `renewable_priority > 50`

**Messaging Focus:**
- Highlight renewable energy percentage
- Emphasize environmental impact
- Use sustainability language
- Mention carbon footprint reduction
- Tone: Values-driven, inspirational

**Example:**
```
This plan is 100% renewable energy, which aligns with your environmental priorities.
While it costs $10 more per month than the cheapest option, you'll be supporting
wind and solar power for your entire 12,000 kWh annual usage. The 12-month contract
locks in this rate and includes no cancellation fees.
```

### Flexibility-Focused Persona

**Detection:** `flexibility_priority > 50`

**Messaging Focus:**
- Emphasize no-contract or month-to-month options
- Highlight low/no early termination fees
- Stress freedom and lack of commitment
- Mention easy switching
- Tone: Freedom-focused, flexible

**Example:**
```
This plan gives you complete flexibility with no long-term commitment. You can
cancel anytime without penalties, and while the rate may adjust monthly, you'll
never be locked in. Based on your usage, you'll pay about $92 per month with a
small $5 service fee.
```

### Balanced Persona

**Detection:** No dominant priority

**Messaging Focus:**
- Emphasize overall value and best-fit
- Balance multiple benefits
- Highlight composite score
- Mention well-rounded offering
- Tone: Comprehensive, balanced

**Example:**
```
This plan provides the best overall match for your needs with strong performance
across cost, reliability, and green energy. You'll save $200 annually with 50%
renewable energy and a well-rated supplier. The 12-month commitment comes with a
moderate $100 early termination fee.
```

---

## Readability Optimization

### Target Reading Level

**Flesch-Kincaid Score:** >60 (8th grade or easier)

### Guidelines

**Sentence Structure:**
- Average 15-20 words per sentence
- Use active voice
- Avoid complex subordinate clauses

**Word Choice:**
- Use simple, everyday words
- Avoid jargon or explain it: "Early termination fee (cancellation charge)"
- Prefer concrete over abstract: "$300 savings" not "substantial savings"

**Good Examples:**
- ✅ "You'll save $300 per year"
- ❌ "Annual savings of $300 will be realized"
- ✅ "This plan is 100% renewable energy"
- ❌ "This plan leverages entirely sustainable energy sources"
- ✅ "You can cancel anytime"
- ❌ "Contract termination is available at the customer's discretion"

---

## Context-Aware Messaging

### Special Situations

#### High Early Termination Fee (>$150)

```python
if plan.early_termination_fee > 150:
    if plan.break_even_months:
        # Include break-even analysis
        "This plan has a ${etf} early termination fee, but you'll break even
        in {months} months. Consider waiting until your current contract expires
        if it ends soon."
    else:
        # Warn without break-even
        "Important: This plan has a ${etf} early termination fee. Make sure
        you're comfortable with the commitment."
```

#### Variable Rate Plans

```python
if plan.plan_type == "variable":
    "This is a variable rate plan, which means your rate can change monthly.
    While it starts competitive, your costs could increase if market rates rise.
    Monitor your bills regularly."
```

#### Low Savings (<5%)

```python
if 0 < savings_pct < 5:
    "While this plan saves you ${savings} per year, the savings are modest
    ({pct}%). Consider whether switching is worth the administrative effort."
```

#### Recommend Staying with Current Plan

```python
if stay_with_current:
    "Based on your usage and preferences, staying with your current plan is
    the best option. The potential savings from switching are too small to
    justify the effort and any switching costs."
```

---

## Caching Strategy

### Cache Configuration

**Backend:** Redis
**Key Format:** `explanation:{hash}`
**Hash Input:** `{plan_id}:{profile_type}:{persona_type}`
**TTL:** 24 hours (86400 seconds)

### Cache Operations

#### Get Cached Explanation

```python
async def _get_cached_explanation(
    plan: RankedPlan,
    user_profile: Dict[str, Any],
    preferences: UserPreferences,
) -> Optional[PlanExplanation]:
    cache_key = _generate_cache_key(plan, user_profile, preferences)
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return PlanExplanation(**json.loads(cached_data))
    return None
```

#### Cache Explanation

```python
async def _cache_explanation(
    plan: RankedPlan,
    user_profile: Dict[str, Any],
    preferences: UserPreferences,
    explanation: PlanExplanation,
) -> None:
    cache_key = _generate_cache_key(plan, user_profile, preferences)
    data = explanation.model_dump(mode="json")
    await redis_client.setex(cache_key, 86400, json.dumps(data))
```

### Cache Invalidation

**Manual Invalidation:**
```python
# Invalidate specific plan
await service.invalidate_cache(plan_id="uuid")

# Invalidate all
await service.invalidate_cache()
```

**Automatic Invalidation:**
- When plan details change in catalog
- When Claude API configuration changes
- After 24 hours (TTL expires)

### Cache Warming

Pre-generate explanations for popular combinations:

```python
# Warm cache for top 20 plans × 4 personas = 80 explanations
await service.warm_cache(
    plans=top_20_plans,
    personas=["budget_conscious", "eco_conscious",
              "flexibility_focused", "balanced"],
    mock_profile=typical_profile,
)
```

**When to Warm:**
- On deployment
- After plan catalog update
- Nightly background job
- Before peak usage times

---

## Metrics Tracking

### `ExplanationMetrics`

**Location:** `/src/backend/schemas/explanation_schemas.py`

```python
@dataclass
class ExplanationMetrics(BaseModel):
    total_generated: int
    cache_hits: int
    cache_misses: int
    api_calls: int
    fallback_used: int
    avg_generation_time_ms: float
    avg_readability_score: float

    @property
    def cache_hit_rate(self) -> float:
        """Cache hit rate as percentage (target: >60%)"""

    @property
    def fallback_rate(self) -> float:
        """Fallback usage rate as percentage"""
```

**Access Metrics:**
```python
metrics = service.get_metrics()
print(f"Cache hit rate: {metrics.cache_hit_rate:.1f}%")
print(f"Fallback rate: {metrics.fallback_rate:.1f}%")
print(f"Avg readability: {metrics.avg_readability_score:.1f}")
```

**Target Metrics:**
- Cache hit rate: >60%
- Fallback rate: <10%
- Avg readability score: >60
- Avg generation time: <500ms

---

## API Configuration

### Claude API Settings

**Model:** `claude-3-5-sonnet-20241022` (or latest)
**Max Tokens:** 200-300 (concise explanations)
**Temperature:** 0.7 (consistent but natural)
**Timeout:** 10 seconds
**Max Retries:** 3 attempts with exponential backoff

### Error Handling

**API Failures:**
1. Retry with exponential backoff (2^attempt seconds)
2. After 3 failures, fall back to template
3. Log error and increment `fallback_used` metric

**Rate Limiting:**
- Queue requests if rate limited
- Implement exponential backoff
- Fall back to template if queue too long

**Timeouts:**
- 10-second timeout per request
- Fall back to template on timeout

**Invalid Responses:**
- Validate response length (>50 characters)
- Re-attempt generation once
- Fall back to template if validation fails

---

## Usage Examples

### Example 1: Generate Single Explanation

```python
from backend.services.explanation_service import create_explanation_service
from backend.schemas.explanation_schemas import (
    RankedPlan, UserPreferences, CurrentPlan
)

# Initialize service
service = create_explanation_service(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    redis_client=redis_client,
)

# Prepare data
plan = RankedPlan(
    plan_id=uuid4(),
    rank=1,
    plan_name="Green Energy 100",
    supplier_name="EcoEnergy Inc",
    # ... other fields
)

preferences = UserPreferences(
    cost_priority=10,
    flexibility_priority=10,
    renewable_priority=70,
    rating_priority=10,
)

user_profile = {
    "profile_type": "seasonal",
    "statistics": {"mean_kwh": 1000.0},
    "seasonal_analysis": {"has_seasonal_pattern": True},
}

current_plan = CurrentPlan(
    plan_name="Old Plan",
    annual_cost=Decimal("1200.00"),
)

# Generate explanation
explanation = await service.generate_explanation(
    plan=plan,
    user_profile=user_profile,
    preferences=preferences,
    current_plan=current_plan,
)

# Access results
print(f"Explanation: {explanation.explanation_text}")
print(f"Persona: {explanation.persona_type}")
print(f"Differentiators: {explanation.key_differentiators}")
print(f"Trade-offs: {explanation.trade_offs}")
print(f"Readability: {explanation.readability_score:.1f}")
print(f"Generated via: {explanation.generated_via}")
```

### Example 2: Bulk Generation for Multiple Plans

```python
# Generate explanations for top 3 recommendations
plans = [plan1, plan2, plan3]  # RankedPlan objects

explanations = await service.generate_bulk_explanations(
    plans=plans,
    user_profile=user_profile,
    preferences=preferences,
    current_plan=current_plan,
)

# All 3 generated in parallel
for i, explanation in enumerate(explanations, 1):
    print(f"Plan {i}: {explanation.explanation_text}")
```

### Example 3: Integration with Recommendation Flow (Story 3.2)

```python
async def get_recommendations_with_explanations(user_id: UUID):
    """
    Complete flow: Get recommendations and generate explanations.
    """
    # Step 1: Get user data
    user = await get_user(user_id)
    usage_data = await get_usage_history(user_id)
    preferences = await get_user_preferences(user_id)
    current_plan = await get_current_plan(user_id)

    # Step 2: Analyze usage (Story 1.4)
    from backend.services.usage_analysis import UsageAnalysisService
    usage_service = UsageAnalysisService()
    user_profile = usage_service.analyze_usage_patterns(usage_data)

    # Step 3: Get recommendations (Story 2.2 - from Backend Dev #3)
    from backend.services.recommendation_service import get_recommendations
    ranked_plans = await get_recommendations(
        user_profile=user_profile,
        preferences=preferences,
        current_plan=current_plan,
    )

    # Step 4: Generate explanations (This service)
    explanation_service = create_explanation_service(
        api_key=settings.ANTHROPIC_API_KEY,
        redis_client=redis_client,
    )

    explanations = await explanation_service.generate_bulk_explanations(
        plans=ranked_plans,
        user_profile=user_profile.to_dict(),
        preferences=preferences,
        current_plan=current_plan,
    )

    # Step 5: Combine and return
    recommendations = []
    for plan, explanation in zip(ranked_plans, explanations):
        recommendations.append({
            "plan": plan,
            "explanation": explanation,
        })

    return recommendations
```

### Example 4: Cache Invalidation on Plan Update

```python
@router.put("/plans/{plan_id}")
async def update_plan(plan_id: UUID, plan_update: PlanUpdate):
    """Update plan and invalidate cached explanations."""
    # Update plan in database
    updated_plan = await db.update_plan(plan_id, plan_update)

    # Invalidate all cached explanations for this plan
    await explanation_service.invalidate_cache(plan_id=str(plan_id))

    return updated_plan
```

### Example 5: Monitor Metrics

```python
@router.get("/admin/explanation-metrics")
async def get_explanation_metrics():
    """Get explanation service metrics."""
    metrics = explanation_service.get_metrics()

    return {
        "total_generated": metrics.total_generated,
        "cache_hit_rate": f"{metrics.cache_hit_rate:.1f}%",
        "fallback_rate": f"{metrics.fallback_rate:.1f}%",
        "avg_generation_time_ms": f"{metrics.avg_generation_time_ms:.1f}",
        "avg_readability_score": f"{metrics.avg_readability_score:.1f}",
    }
```

---

## Template Fallback Service

### `TemplateExplanationGenerator`

**Location:** `/src/backend/services/explanation_templates.py`

Rule-based fallback when Claude API is unavailable.

```python
from backend.services.explanation_templates import TemplateExplanationGenerator

generator = TemplateExplanationGenerator()

explanation_text = generator.generate_explanation(
    plan=plan,
    user_profile=user_profile,
    preferences=preferences,
    current_plan=current_plan,
)

differentiators = generator.identify_key_differentiators(plan, all_plans)
trade_offs = generator.identify_trade_offs(plan, current_plan)
```

**Quality:** Template explanations are designed to be nearly as good as AI-generated ones, using extensive if-else logic for personalization.

---

## Integration Checklist for Story 3.2 (API Endpoints)

- [ ] Import `create_explanation_service` from `backend.services.explanation_service`
- [ ] Import schemas from `backend.schemas.explanation_schemas`
- [ ] Initialize service with API key and Redis client
- [ ] Call `generate_explanation()` or `generate_bulk_explanations()`
- [ ] Include `PlanExplanation` in recommendation API response
- [ ] Implement cache invalidation endpoint
- [ ] Add metrics endpoint for monitoring
- [ ] Handle async/await properly
- [ ] Set up error handling for service failures
- [ ] Configure API key in environment variables

---

## Integration Checklist for Story 4.2 (Plan Card UI)

- [ ] Display `explanation.explanation_text` prominently on plan card
- [ ] Show `explanation.key_differentiators` as bullet points or badges
- [ ] Display `explanation.trade_offs` in collapsible section or tooltip
- [ ] Indicate `explanation.generated_via` for transparency (optional)
- [ ] Show `explanation.persona_type` for debugging (dev mode only)
- [ ] Ensure text is readable (font size, contrast, line spacing)
- [ ] Support expanding/collapsing full explanation
- [ ] Handle loading state while generating
- [ ] Show error message if generation fails

---

## Performance Characteristics

- **Cached Response:** <50ms
- **Claude API (cold):** 1-2 seconds
- **Template Fallback:** <100ms
- **Bulk (3 plans, cached):** <150ms
- **Bulk (3 plans, uncached):** <3 seconds
- **Cache TTL:** 24 hours
- **Target Cache Hit Rate:** >60%

---

## Dependencies

### Required Python Packages

```
anthropic>=0.39.0
textstat>=0.7.3
redis>=5.0.0
httpx>=0.26.0
pydantic>=2.5.0
```

### External Services

- **Claude API:** Anthropic API key required
- **Redis:** For caching (optional but recommended)

### Internal Dependencies

- `backend.schemas.explanation_schemas` (this story)
- `backend.schemas.usage_analysis` (Story 1.4)
- Redis cache service

---

## Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional (defaults shown)
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_MAX_TOKENS=300
CLAUDE_TEMPERATURE=0.7
CLAUDE_TIMEOUT=10.0
EXPLANATION_CACHE_TTL=86400  # 24 hours
```

---

## Error Handling

### Graceful Degradation

The service implements multiple fallback layers:

1. **Primary:** Claude API with retry logic
2. **Fallback:** Template-based generation
3. **Always:** Valid PlanExplanation returned

### Error Scenarios

| Scenario | Behavior |
|----------|----------|
| Claude API down | Fall back to template, log error |
| Rate limited | Exponential backoff, then template |
| Timeout | Fall back to template after 10s |
| Invalid API key | Fall back to template, alert admin |
| Redis unavailable | Skip caching, continue with generation |
| Invalid response | Re-attempt once, then template |

---

## Cost Management

### Claude API Costs

- **Model:** Claude Sonnet 3.5
- **Cost:** ~$0.003 per explanation (300 tokens)
- **Monthly (10K users):** ~$30-$100 depending on cache hit rate

### Optimization Strategies

1. **Caching:** 60%+ cache hit rate reduces costs by 60%
2. **Bulk Generation:** Parallel processing is efficient
3. **Cache Warming:** Pre-generate for popular combinations
4. **Monitoring:** Track `api_calls` metric, set budget alerts

---

## Security Considerations

- **API Key:** Store in environment variable, never commit
- **Rate Limiting:** Implement request throttling
- **Input Validation:** Validate all inputs before API calls
- **Output Sanitization:** Escape HTML in explanations for UI display
- **PII:** Do not include user PII in prompts

---

## Testing

### Test Files

**Location:** `/tests/backend/test_explanation_service.py`

**Coverage:**
- Template generation for all personas
- Claude API integration (mocked)
- Fallback behavior on API failure
- Caching workflow
- Metrics tracking
- Bulk generation
- Readability calculation
- Cache invalidation

**Run Tests:**
```bash
pytest tests/backend/test_explanation_service.py -v
```

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-10 | Initial contract release |

---

## Support

For questions or issues:
- **Author:** ML Engineer (Epic 2)
- **Stories:** 2.6 (API Integration), 2.7 (Personalization), 2.8 (Caching)
- **Epic:** 2 - AI Explanation Generation

---

**End of Contract Document**
