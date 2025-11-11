# Story 1.4 - Usage Pattern Analysis Interface Contract

**Version:** 1.0
**Date:** November 10, 2025
**Author:** Backend Dev #2
**Status:** Complete
**Depends On:** Story 1.1 (Database Schema)
**Required By:** Story 2.1 (Scoring Algorithm)

---

## Overview

This document defines the interface contract for the Usage Pattern Analysis service (Story 1.4). This contract enables Story 2.1 (Scoring Algorithm) to integrate with the usage analysis functionality.

---

## Core Service

### `UsageAnalysisService`

**Location:** `/src/backend/services/usage_analysis.py`

The main service class that performs comprehensive usage pattern analysis.

#### Primary Method

```python
def analyze_usage_patterns(
    usage_data: List[MonthlyUsage],
    user_id: Optional[str] = None,
    regional_avg_kwh: Optional[float] = None,
) -> UsageProfile
```

**Parameters:**
- `usage_data`: List of MonthlyUsage objects (historical data)
- `user_id`: Optional user identifier for caching
- `regional_avg_kwh`: Optional regional average for new customers

**Returns:** Complete `UsageProfile` with all analysis results

**Performance:** <100ms for 12 months of data

---

## Data Schemas

### Input Schema: `MonthlyUsage`

**Location:** `/src/backend/schemas/usage_analysis.py`

```python
@dataclass
class MonthlyUsage:
    """Monthly electricity usage data point."""
    month: date  # First day of the month
    kwh: float   # Kilowatt-hours consumed
```

**Example:**
```python
from datetime import date
from backend.schemas.usage_analysis import MonthlyUsage

usage = MonthlyUsage(
    month=date(2024, 1, 1),
    kwh=850.5
)
```

---

### Output Schema: `UsageProfile`

**Location:** `/src/backend/schemas/usage_analysis.py`

Complete analysis output containing all pattern detection results, projections, and quality metrics.

```python
@dataclass
class UsageProfile:
    user_id: Optional[str]
    profile_type: UserProfileType

    # Statistical analysis
    statistics: UsageStatistics

    # Pattern detection
    seasonal_analysis: SeasonalAnalysis
    peak_offpeak: PeakOffPeakAnalysis
    outliers: OutlierDetection

    # Data quality
    data_quality: DataQualityMetrics

    # Projections
    projection: UsageProjection

    # Metadata
    analysis_date: datetime
    data_period_start: date
    data_period_end: date
    num_months_analyzed: int

    # Overall confidence
    overall_confidence: float
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        ...
```

---

### Profile Type Classifications

```python
class UserProfileType(str, Enum):
    BASELINE = "baseline"                    # Consistent usage year-round
    HIGH_USER = "high_user"                  # Above-average consumption
    VARIABLE = "variable"                    # Significant month-to-month variation
    SEASONAL = "seasonal"                    # Strong summer/winter peaks
    INSUFFICIENT_DATA = "insufficient_data"  # <3 months of data
```

---

### Key Sub-Schemas

#### `UsageStatistics`

Basic statistical measures:

```python
@dataclass
class UsageStatistics:
    min_kwh: float
    max_kwh: float
    mean_kwh: float
    median_kwh: float
    std_dev: float
    coefficient_of_variation: float  # std_dev / mean
    total_annual_kwh: float
```

#### `SeasonalAnalysis`

Seasonal pattern detection results:

```python
@dataclass
class SeasonalAnalysis:
    has_seasonal_pattern: bool
    dominant_season: Optional[SeasonType]  # WINTER, SPRING, SUMMER, FALL
    patterns: List[SeasonalPattern]
    summer_to_winter_ratio: float
    peak_to_avg_ratio: float
    confidence_score: float  # 0.0 to 1.0
```

#### `UsageProjection`

12-month forward projection:

```python
@dataclass
class UsageProjection:
    projected_monthly_kwh: List[float]  # 12 values
    projected_annual_kwh: float
    confidence_lower: List[float]  # Lower bound (95% CI)
    confidence_upper: List[float]  # Upper bound (95% CI)
    confidence_score: float  # 0.0 to 1.0
    method: str  # Projection method used
    assumptions: List[str]  # Key assumptions
```

#### `DataQualityMetrics`

Data completeness and quality assessment:

```python
@dataclass
class DataQualityMetrics:
    total_months: int
    missing_months: int
    interpolated_months: int
    has_gaps: bool
    completeness_pct: float
    quality_score: float  # 0.0 to 1.0
```

---

## Usage Examples

### Example 1: Basic Usage Analysis

```python
from datetime import date
from backend.schemas.usage_analysis import MonthlyUsage
from backend.services.usage_analysis import UsageAnalysisService

# Create service
service = UsageAnalysisService()

# Prepare usage data (12 months recommended)
usage_data = [
    MonthlyUsage(date(2024, 1, 1), 850.0),
    MonthlyUsage(date(2024, 2, 1), 820.0),
    MonthlyUsage(date(2024, 3, 1), 780.0),
    MonthlyUsage(date(2024, 4, 1), 900.0),
    MonthlyUsage(date(2024, 5, 1), 950.0),
    MonthlyUsage(date(2024, 6, 1), 1400.0),
    MonthlyUsage(date(2024, 7, 1), 1600.0),
    MonthlyUsage(date(2024, 8, 1), 1500.0),
    MonthlyUsage(date(2024, 9, 1), 1000.0),
    MonthlyUsage(date(2024, 10, 1), 850.0),
    MonthlyUsage(date(2024, 11, 1), 800.0),
    MonthlyUsage(date(2024, 12, 1), 820.0),
]

# Analyze patterns
profile = service.analyze_usage_patterns(
    usage_data=usage_data,
    user_id="user_12345"
)

# Access results
print(f"Profile Type: {profile.profile_type.value}")
print(f"Mean Usage: {profile.statistics.mean_kwh:.1f} kWh")
print(f"Projected Annual: {profile.projection.projected_annual_kwh:.1f} kWh")
print(f"Confidence: {profile.overall_confidence:.2f}")

# Check for seasonal pattern
if profile.seasonal_analysis.has_seasonal_pattern:
    print(f"Dominant Season: {profile.seasonal_analysis.dominant_season.value}")
    print(f"Summer/Winter Ratio: {profile.seasonal_analysis.summer_to_winter_ratio:.2f}")
```

### Example 2: Integration with Story 2.1 (Scoring Algorithm)

```python
from backend.services.usage_analysis import UsageAnalysisService

def score_plan_for_user(user_usage_data, plan_details):
    """
    Example function showing how Story 2.1 would use this contract.
    """
    # Step 1: Analyze user's usage patterns
    analysis_service = UsageAnalysisService()
    profile = analysis_service.analyze_usage_patterns(user_usage_data)

    # Step 2: Use profile for plan scoring
    if profile.profile_type == UserProfileType.SEASONAL:
        # Prioritize plans with seasonal rates or high summer capacity
        if profile.seasonal_analysis.dominant_season == SeasonType.SUMMER:
            summer_bonus = 1.2
        else:
            summer_bonus = 1.0

    # Step 3: Use projections for cost calculations
    projected_annual_kwh = profile.projection.projected_annual_kwh
    estimated_annual_cost = projected_annual_kwh * plan_details.rate_per_kwh

    # Step 4: Factor in confidence for risk assessment
    if profile.overall_confidence < 0.5:
        # Low confidence - add uncertainty buffer
        estimated_annual_cost *= 1.1

    return {
        "estimated_cost": estimated_annual_cost,
        "profile_type": profile.profile_type.value,
        "confidence": profile.overall_confidence,
    }
```

### Example 3: Handling Edge Cases

```python
# New customer with no historical data
profile_new = service.analyze_usage_patterns(
    usage_data=[],
    user_id="new_user",
    regional_avg_kwh=900.0  # Use regional average
)

# Limited data (6 months)
limited_data = [
    MonthlyUsage(date(2024, 1, 1), 850.0),
    MonthlyUsage(date(2024, 2, 1), 820.0),
    MonthlyUsage(date(2024, 3, 1), 780.0),
    MonthlyUsage(date(2024, 4, 1), 900.0),
    MonthlyUsage(date(2024, 5, 1), 950.0),
    MonthlyUsage(date(2024, 6, 1), 1400.0),
]

profile_limited = service.analyze_usage_patterns(limited_data)

# Check warnings
if profile_limited.warnings:
    for warning in profile_limited.warnings:
        print(f"Warning: {warning}")

# Check data quality
if profile_limited.data_quality.has_gaps:
    print(f"Data has {profile_limited.data_quality.missing_months} missing months")
```

---

## Caching Integration

### `CacheService`

**Location:** `/src/backend/services/cache_service.py`

Optional Redis caching for improved performance.

```python
from backend.services.cache_service import get_cache_service

# Get cache service
cache = get_cache_service()

# Cache profile
cache.set_profile(user_id="user_123", profile=profile)

# Retrieve cached profile
cached_profile = cache.get_profile(user_id="user_123")

# Invalidate cache when data changes
cache.invalidate_profile(user_id="user_123")
```

**Configuration:**

```python
from backend.services.cache_service import configure_cache

cache = configure_cache(
    redis_host="localhost",
    redis_port=6379,
    redis_db=0,
    enabled=True  # Set to False to disable caching
)
```

---

## Mock Functions for Testing (Story 2.1)

Use these helper functions while testing integration:

```python
def create_mock_baseline_profile() -> UsageProfile:
    """Create mock baseline profile for testing."""
    from datetime import date, datetime
    from backend.schemas.usage_analysis import (
        UsageProfile, UserProfileType, UsageStatistics,
        SeasonalAnalysis, PeakOffPeakAnalysis, OutlierDetection,
        DataQualityMetrics, UsageProjection
    )

    return UsageProfile(
        user_id="mock_user",
        profile_type=UserProfileType.BASELINE,
        statistics=UsageStatistics(
            min_kwh=750.0,
            max_kwh=850.0,
            mean_kwh=800.0,
            median_kwh=800.0,
            std_dev=25.0,
            coefficient_of_variation=0.03,
            total_annual_kwh=9600.0,
        ),
        seasonal_analysis=SeasonalAnalysis(
            has_seasonal_pattern=False,
            dominant_season=None,
            patterns=[],
            summer_to_winter_ratio=1.0,
            peak_to_avg_ratio=1.06,
            confidence_score=0.85,
        ),
        peak_offpeak=PeakOffPeakAnalysis(
            peak_months=["June", "July", "August"],
            off_peak_months=["November", "December", "January"],
            peak_avg_kwh=810.0,
            off_peak_avg_kwh=790.0,
            peak_to_offpeak_ratio=1.025,
        ),
        outliers=OutlierDetection(
            has_outliers=False,
            outlier_months=[],
            outlier_values=[],
            method="IQR",
        ),
        data_quality=DataQualityMetrics(
            total_months=12,
            missing_months=0,
            interpolated_months=0,
            has_gaps=False,
            completeness_pct=100.0,
            quality_score=1.0,
        ),
        projection=UsageProjection(
            projected_monthly_kwh=[800.0] * 12,
            projected_annual_kwh=9600.0,
            confidence_lower=[750.0] * 12,
            confidence_upper=[850.0] * 12,
            confidence_score=0.85,
            method="moving_average",
            assumptions=["Baseline user with consistent patterns"],
        ),
        analysis_date=datetime.now(),
        data_period_start=date(2024, 1, 1),
        data_period_end=date(2024, 12, 1),
        num_months_analyzed=12,
        overall_confidence=0.85,
        warnings=[],
    )


def create_mock_seasonal_profile() -> UsageProfile:
    """Create mock seasonal profile for testing."""
    from datetime import date, datetime
    from backend.schemas.usage_analysis import (
        UsageProfile, UserProfileType, SeasonType, SeasonalPattern,
        UsageStatistics, SeasonalAnalysis, PeakOffPeakAnalysis,
        OutlierDetection, DataQualityMetrics, UsageProjection
    )

    return UsageProfile(
        user_id="mock_seasonal_user",
        profile_type=UserProfileType.SEASONAL,
        statistics=UsageStatistics(
            min_kwh=680.0,
            max_kwh=1600.0,
            mean_kwh=1000.0,
            median_kwh=900.0,
            std_dev=280.0,
            coefficient_of_variation=0.28,
            total_annual_kwh=12000.0,
        ),
        seasonal_analysis=SeasonalAnalysis(
            has_seasonal_pattern=True,
            dominant_season=SeasonType.SUMMER,
            patterns=[
                SeasonalPattern(
                    season=SeasonType.SUMMER,
                    avg_kwh=1433.0,
                    peak_month="July",
                    peak_kwh=1600.0,
                    variation_pct=43.3,
                ),
                SeasonalPattern(
                    season=SeasonType.WINTER,
                    avg_kwh=733.0,
                    peak_month="January",
                    peak_kwh=850.0,
                    variation_pct=-26.7,
                ),
            ],
            summer_to_winter_ratio=1.95,
            peak_to_avg_ratio=1.60,
            confidence_score=0.92,
        ),
        peak_offpeak=PeakOffPeakAnalysis(
            peak_months=["May", "June", "July", "August", "September"],
            off_peak_months=["November", "December", "January", "February", "March"],
            peak_avg_kwh=1260.0,
            off_peak_avg_kwh=762.0,
            peak_to_offpeak_ratio=1.65,
        ),
        outliers=OutlierDetection(
            has_outliers=False,
            outlier_months=[],
            outlier_values=[],
            method="IQR",
        ),
        data_quality=DataQualityMetrics(
            total_months=12,
            missing_months=0,
            interpolated_months=0,
            has_gaps=False,
            completeness_pct=100.0,
            quality_score=1.0,
        ),
        projection=UsageProjection(
            projected_monthly_kwh=[
                750, 720, 780, 850, 1100, 1400, 1600, 1500, 1000, 850, 800, 750
            ],
            projected_annual_kwh=12100.0,
            confidence_lower=[
                650, 620, 680, 750, 1000, 1300, 1500, 1400, 900, 750, 700, 650
            ],
            confidence_upper=[
                850, 820, 880, 950, 1200, 1500, 1700, 1600, 1100, 950, 900, 850
            ],
            confidence_score=0.88,
            method="seasonal_average",
            assumptions=["Strong seasonal pattern with summer peak"],
        ),
        analysis_date=datetime.now(),
        data_period_start=date(2024, 1, 1),
        data_period_end=date(2024, 12, 1),
        num_months_analyzed=12,
        overall_confidence=0.90,
        warnings=[],
    )
```

---

## Integration Checklist for Story 2.1

- [ ] Import `UsageAnalysisService` from `backend.services.usage_analysis`
- [ ] Import schema types from `backend.schemas.usage_analysis`
- [ ] Convert user's historical usage data to `List[MonthlyUsage]`
- [ ] Call `analyze_usage_patterns()` to get `UsageProfile`
- [ ] Use `profile.projection.projected_annual_kwh` for cost calculations
- [ ] Use `profile.profile_type` for plan matching logic
- [ ] Use `profile.seasonal_analysis` for seasonal rate optimization
- [ ] Check `profile.overall_confidence` for risk assessment
- [ ] Handle warnings in `profile.warnings` list
- [ ] Implement caching for frequently accessed profiles
- [ ] Write tests using mock profiles from this contract

---

## Performance Characteristics

- **Target:** <100ms for 12 months of data
- **Average:** ~50ms for complete data
- **Memory:** ~500KB per analysis
- **Cache TTL:** 7 days (configurable)
- **Concurrency:** Thread-safe, can process multiple users in parallel

---

## Error Handling

The service handles edge cases gracefully:

1. **Insufficient Data (<3 months):** Returns `UserProfileType.INSUFFICIENT_DATA` with reduced confidence
2. **Missing Months:** Automatically interpolates gaps
3. **Outliers:** Detects and flags anomalous usage
4. **Zero Usage:** Handles vacant properties correctly
5. **New Customers:** Uses regional averages if provided

All warnings are captured in `profile.warnings` list.

---

## Dependencies

### Required Python Packages

```
numpy>=1.26.0
pandas>=2.1.0
scipy>=1.11.0
redis>=5.0.0  # Optional, for caching
```

### Internal Dependencies

- `backend.schemas.usage_analysis` (this story)
- Redis server (optional, for caching)

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-10 | Initial contract release |

---

## Support

For questions or issues:
- **Author:** Backend Dev #2
- **Story:** 1.4 - Usage Pattern Analysis
- **Epic:** 1 - Data Infrastructure & Pipeline

---

**End of Contract Document**
