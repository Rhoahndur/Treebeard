"""
Usage Pattern Analysis Data Schemas
Story 1.4 - Epic 1: Data Infrastructure & Pipeline

This module defines the data models for usage pattern analysis.
These schemas are used as mock structures until Backend Dev #1
publishes the official database schema contract from Story 1.1.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from decimal import Decimal


# ============================================================================
# INPUT SCHEMAS (Mock - Will be replaced by Story 1.1 contract)
# ============================================================================

@dataclass
class MonthlyUsage:
    """
    Monthly electricity usage data point.
    Mock schema until Story 1.1 is complete.
    """
    month: date  # First day of the month
    kwh: float  # Kilowatt-hours consumed

    def __post_init__(self):
        """Validate the data."""
        if self.kwh < 0:
            raise ValueError("kWh cannot be negative")


# ============================================================================
# ANALYSIS OUTPUT SCHEMAS
# ============================================================================

class UserProfileType(str, Enum):
    """
    User classification based on usage patterns.
    """
    BASELINE = "baseline"  # Consistent usage year-round
    HIGH_USER = "high_user"  # Above-average consumption
    VARIABLE = "variable"  # Significant month-to-month variation
    SEASONAL = "seasonal"  # Strong summer/winter peaks
    INSUFFICIENT_DATA = "insufficient_data"  # Not enough data to classify


class SeasonType(str, Enum):
    """Season classification for pattern detection."""
    WINTER = "winter"  # Dec, Jan, Feb
    SPRING = "spring"  # Mar, Apr, May
    SUMMER = "summer"  # Jun, Jul, Aug
    FALL = "fall"  # Sep, Oct, Nov


@dataclass
class SeasonalPattern:
    """
    Detected seasonal usage pattern.
    """
    season: SeasonType
    avg_kwh: float
    peak_month: str  # Month name (e.g., "July")
    peak_kwh: float
    variation_pct: float  # Percentage variation from annual average


@dataclass
class SeasonalAnalysis:
    """
    Complete seasonal pattern analysis results.
    """
    has_seasonal_pattern: bool
    dominant_season: Optional[SeasonType]
    patterns: List[SeasonalPattern]
    summer_to_winter_ratio: float  # Ratio of summer avg to winter avg
    peak_to_avg_ratio: float  # Ratio of peak month to annual average
    confidence_score: float  # 0.0 to 1.0


@dataclass
class PeakOffPeakAnalysis:
    """
    Peak and off-peak usage analysis.
    This is a simplified version assuming monthly granularity.
    For time-of-use analysis, hourly data would be needed.
    """
    peak_months: List[str]  # Months with above-average usage
    off_peak_months: List[str]  # Months with below-average usage
    peak_avg_kwh: float
    off_peak_avg_kwh: float
    peak_to_offpeak_ratio: float


@dataclass
class OutlierDetection:
    """
    Anomalous usage detection results.
    """
    has_outliers: bool
    outlier_months: List[str]  # Months with anomalous usage
    outlier_values: List[float]  # Corresponding kWh values
    method: str  # Detection method used (e.g., "IQR", "Z-score")


@dataclass
class DataQualityMetrics:
    """
    Metrics about the quality and completeness of input data.
    """
    total_months: int
    missing_months: int
    interpolated_months: int
    has_gaps: bool
    completeness_pct: float  # Percentage of complete data
    quality_score: float  # 0.0 to 1.0


@dataclass
class UsageProjection:
    """
    12-month forward usage projection with confidence intervals.
    """
    projected_monthly_kwh: List[float]  # 12 months of projected usage
    projected_annual_kwh: float
    confidence_lower: List[float]  # Lower bound (95% CI)
    confidence_upper: List[float]  # Upper bound (95% CI)
    confidence_score: float  # Overall projection confidence (0.0 to 1.0)
    method: str  # Projection method used
    assumptions: List[str]  # Key assumptions made


@dataclass
class UsageStatistics:
    """
    Basic statistical measures of usage patterns.
    """
    min_kwh: float
    max_kwh: float
    mean_kwh: float
    median_kwh: float
    std_dev: float
    coefficient_of_variation: float  # std_dev / mean
    total_annual_kwh: float


@dataclass
class UsageProfile:
    """
    Complete usage pattern analysis profile.
    This is the primary output of the analysis service.
    """
    user_id: Optional[str]  # User identifier (if available)
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
    overall_confidence: float  # Weighted average of all confidence scores
    warnings: List[str] = field(default_factory=list)  # Analysis warnings

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "user_id": self.user_id,
            "profile_type": self.profile_type.value,
            "statistics": {
                "min_kwh": self.statistics.min_kwh,
                "max_kwh": self.statistics.max_kwh,
                "mean_kwh": self.statistics.mean_kwh,
                "median_kwh": self.statistics.median_kwh,
                "std_dev": self.statistics.std_dev,
                "coefficient_of_variation": self.statistics.coefficient_of_variation,
                "total_annual_kwh": self.statistics.total_annual_kwh,
            },
            "seasonal_analysis": {
                "has_seasonal_pattern": self.seasonal_analysis.has_seasonal_pattern,
                "dominant_season": self.seasonal_analysis.dominant_season.value if self.seasonal_analysis.dominant_season else None,
                "patterns": [
                    {
                        "season": p.season.value,
                        "avg_kwh": p.avg_kwh,
                        "peak_month": p.peak_month,
                        "peak_kwh": p.peak_kwh,
                        "variation_pct": p.variation_pct,
                    }
                    for p in self.seasonal_analysis.patterns
                ],
                "summer_to_winter_ratio": self.seasonal_analysis.summer_to_winter_ratio,
                "peak_to_avg_ratio": self.seasonal_analysis.peak_to_avg_ratio,
                "confidence_score": self.seasonal_analysis.confidence_score,
            },
            "peak_offpeak": {
                "peak_months": self.peak_offpeak.peak_months,
                "off_peak_months": self.peak_offpeak.off_peak_months,
                "peak_avg_kwh": self.peak_offpeak.peak_avg_kwh,
                "off_peak_avg_kwh": self.peak_offpeak.off_peak_avg_kwh,
                "peak_to_offpeak_ratio": self.peak_offpeak.peak_to_offpeak_ratio,
            },
            "outliers": {
                "has_outliers": self.outliers.has_outliers,
                "outlier_months": self.outliers.outlier_months,
                "outlier_values": self.outliers.outlier_values,
                "method": self.outliers.method,
            },
            "data_quality": {
                "total_months": self.data_quality.total_months,
                "missing_months": self.data_quality.missing_months,
                "interpolated_months": self.data_quality.interpolated_months,
                "has_gaps": self.data_quality.has_gaps,
                "completeness_pct": self.data_quality.completeness_pct,
                "quality_score": self.data_quality.quality_score,
            },
            "projection": {
                "projected_monthly_kwh": self.projection.projected_monthly_kwh,
                "projected_annual_kwh": self.projection.projected_annual_kwh,
                "confidence_lower": self.projection.confidence_lower,
                "confidence_upper": self.projection.confidence_upper,
                "confidence_score": self.projection.confidence_score,
                "method": self.projection.method,
                "assumptions": self.projection.assumptions,
            },
            "analysis_date": self.analysis_date.isoformat(),
            "data_period_start": self.data_period_start.isoformat(),
            "data_period_end": self.data_period_end.isoformat(),
            "num_months_analyzed": self.num_months_analyzed,
            "overall_confidence": self.overall_confidence,
            "warnings": self.warnings,
        }
