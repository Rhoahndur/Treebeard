"""
Usage Pattern Analysis Service
Story 1.4 - Epic 1: Data Infrastructure & Pipeline

This service provides comprehensive usage pattern analysis including:
- Seasonal pattern detection
- User profile classification
- 12-month usage projections
- Peak/off-peak analysis
- Outlier detection
- Data quality assessment

Performance target: Process 1 year of data in <100ms
"""

import statistics
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple
import calendar

import numpy as np
from scipy import stats

from ..schemas.usage_analysis import (
    MonthlyUsage,
    UsageProfile,
    UserProfileType,
    SeasonalAnalysis,
    SeasonalPattern,
    SeasonType,
    PeakOffPeakAnalysis,
    OutlierDetection,
    DataQualityMetrics,
    UsageProjection,
    UsageStatistics,
)


class UsageAnalysisService:
    """
    Service for analyzing electricity usage patterns and generating user profiles.
    """

    # Classification thresholds (these can be tuned based on real data)
    HIGH_USER_THRESHOLD = 1.3  # 30% above median
    VARIABLE_CV_THRESHOLD = 0.25  # Coefficient of variation threshold
    SEASONAL_RATIO_THRESHOLD = 1.35  # Summer/winter ratio for seasonal classification
    OUTLIER_IQR_MULTIPLIER = 1.5  # Standard IQR outlier detection
    MIN_CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for reliable analysis

    def __init__(self):
        """Initialize the usage analysis service."""
        pass

    def analyze_usage_patterns(
        self,
        usage_data: List[MonthlyUsage],
        user_id: Optional[str] = None,
        regional_avg_kwh: Optional[float] = None,
    ) -> UsageProfile:
        """
        Perform comprehensive usage pattern analysis.

        Args:
            usage_data: List of monthly usage data points
            user_id: Optional user identifier
            regional_avg_kwh: Optional regional average for new customer fallback

        Returns:
            Complete UsageProfile with all analysis results

        Performance: <100ms for 12 months of data
        """
        analysis_start = datetime.now()

        # Validate and prepare data
        usage_data = self._sort_usage_data(usage_data)
        data_quality = self._assess_data_quality(usage_data)

        # Handle edge cases
        if data_quality.total_months < 3:
            return self._create_insufficient_data_profile(
                usage_data, user_id, data_quality, regional_avg_kwh
            )

        # Fill gaps if needed
        filled_data = self._fill_missing_months(usage_data)

        # Detect and handle outliers
        outliers = self._detect_outliers(filled_data)
        cleaned_data = self._handle_outliers(filled_data, outliers)

        # Perform statistical analysis
        statistics_result = self._calculate_statistics(cleaned_data)

        # Detect seasonal patterns
        seasonal_analysis = self.detect_seasonal_patterns(cleaned_data)

        # Peak/off-peak analysis
        peak_offpeak = self._analyze_peak_offpeak(cleaned_data, statistics_result)

        # Classify user profile
        profile_type = self.classify_user_profile(
            cleaned_data, statistics_result, seasonal_analysis
        )

        # Project future usage
        projection = self.project_usage(cleaned_data, seasonal_analysis)

        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(
            data_quality, seasonal_analysis, projection
        )

        # Generate warnings
        warnings = self._generate_warnings(
            data_quality, outliers, overall_confidence
        )

        # Build the complete profile
        profile = UsageProfile(
            user_id=user_id,
            profile_type=profile_type,
            statistics=statistics_result,
            seasonal_analysis=seasonal_analysis,
            peak_offpeak=peak_offpeak,
            outliers=outliers,
            data_quality=data_quality,
            projection=projection,
            analysis_date=datetime.now(),
            data_period_start=usage_data[0].month,
            data_period_end=usage_data[-1].month,
            num_months_analyzed=len(usage_data),
            overall_confidence=overall_confidence,
            warnings=warnings,
        )

        # Performance check
        elapsed_ms = (datetime.now() - analysis_start).total_seconds() * 1000
        if elapsed_ms > 100:
            profile.warnings.append(
                f"Analysis took {elapsed_ms:.1f}ms (target: <100ms)"
            )

        return profile

    def detect_seasonal_patterns(
        self, usage_data: List[MonthlyUsage]
    ) -> SeasonalAnalysis:
        """
        Detect seasonal usage patterns (summer/winter peaks).

        Algorithm:
        1. Group usage by meteorological seasons
        2. Calculate average usage per season
        3. Identify dominant season (highest average)
        4. Calculate summer-to-winter ratio
        5. Compute confidence score based on consistency

        Args:
            usage_data: List of monthly usage data (should be sorted)

        Returns:
            SeasonalAnalysis with detected patterns
        """
        if len(usage_data) < 6:
            # Not enough data for reliable seasonal detection
            return SeasonalAnalysis(
                has_seasonal_pattern=False,
                dominant_season=None,
                patterns=[],
                summer_to_winter_ratio=1.0,
                peak_to_avg_ratio=1.0,
                confidence_score=0.0,
            )

        # Group data by season
        season_data = {season: [] for season in SeasonType}

        for usage in usage_data:
            month = usage.month.month
            season = self._get_season(month)
            season_data[season].append(usage.kwh)

        # Calculate seasonal patterns
        patterns = []
        annual_avg = statistics.mean([u.kwh for u in usage_data])

        for season, kwh_values in season_data.items():
            if not kwh_values:
                continue

            avg_kwh = statistics.mean(kwh_values)
            peak_kwh = max(kwh_values)
            peak_idx = kwh_values.index(peak_kwh)

            # Find the month name for the peak
            season_months = [
                u for u in usage_data if self._get_season(u.month.month) == season
            ]
            peak_month = season_months[peak_idx].month.strftime("%B")

            variation_pct = ((avg_kwh - annual_avg) / annual_avg) * 100

            patterns.append(
                SeasonalPattern(
                    season=season,
                    avg_kwh=avg_kwh,
                    peak_month=peak_month,
                    peak_kwh=peak_kwh,
                    variation_pct=variation_pct,
                )
            )

        # Identify dominant season
        if patterns:
            dominant_pattern = max(patterns, key=lambda p: p.avg_kwh)
            dominant_season = dominant_pattern.season
        else:
            dominant_season = None

        # Calculate summer-to-winter ratio
        summer_avg = statistics.mean(season_data[SeasonType.SUMMER]) if season_data[SeasonType.SUMMER] else annual_avg
        winter_avg = statistics.mean(season_data[SeasonType.WINTER]) if season_data[SeasonType.WINTER] else annual_avg
        summer_to_winter_ratio = summer_avg / winter_avg if winter_avg > 0 else 1.0

        # Calculate peak-to-average ratio
        peak_kwh = max([u.kwh for u in usage_data])
        peak_to_avg_ratio = peak_kwh / annual_avg if annual_avg > 0 else 1.0

        # Determine if there's a significant seasonal pattern
        has_seasonal_pattern = (
            summer_to_winter_ratio >= self.SEASONAL_RATIO_THRESHOLD
            or summer_to_winter_ratio <= (1.0 / self.SEASONAL_RATIO_THRESHOLD)
        )

        # Calculate confidence score
        # Higher confidence if we have full year data and consistent patterns
        data_completeness = min(len(usage_data) / 12.0, 1.0)

        # Measure consistency using coefficient of variation within seasons
        season_cvs = []
        for kwh_values in season_data.values():
            if len(kwh_values) >= 2:
                mean_val = statistics.mean(kwh_values)
                std_val = statistics.stdev(kwh_values)
                cv = std_val / mean_val if mean_val > 0 else 0
                season_cvs.append(cv)

        consistency_score = 1.0 - (
            statistics.mean(season_cvs) if season_cvs else 0.5
        )
        consistency_score = max(0.0, min(1.0, consistency_score))

        confidence_score = (data_completeness * 0.6) + (consistency_score * 0.4)

        return SeasonalAnalysis(
            has_seasonal_pattern=has_seasonal_pattern,
            dominant_season=dominant_season,
            patterns=patterns,
            summer_to_winter_ratio=summer_to_winter_ratio,
            peak_to_avg_ratio=peak_to_avg_ratio,
            confidence_score=confidence_score,
        )

    def classify_user_profile(
        self,
        usage_data: List[MonthlyUsage],
        statistics_result: Optional[UsageStatistics] = None,
        seasonal_analysis: Optional[SeasonalAnalysis] = None,
    ) -> UserProfileType:
        """
        Classify user into profile types based on usage patterns.

        Classification logic:
        1. INSUFFICIENT_DATA: < 3 months of data
        2. SEASONAL: Strong seasonal pattern detected
        3. HIGH_USER: Usage significantly above average
        4. VARIABLE: High coefficient of variation in usage
        5. BASELINE: Consistent usage year-round

        Args:
            usage_data: List of monthly usage data
            statistics_result: Pre-computed statistics (optional)
            seasonal_analysis: Pre-computed seasonal analysis (optional)

        Returns:
            UserProfileType classification
        """
        if len(usage_data) < 3:
            return UserProfileType.INSUFFICIENT_DATA

        # Calculate statistics if not provided
        if statistics_result is None:
            statistics_result = self._calculate_statistics(usage_data)

        # Perform seasonal analysis if not provided
        if seasonal_analysis is None:
            seasonal_analysis = self.detect_seasonal_patterns(usage_data)

        # Classification decision tree
        cv = statistics_result.coefficient_of_variation

        # Check for seasonal pattern first (strongest indicator)
        if seasonal_analysis.has_seasonal_pattern:
            return UserProfileType.SEASONAL

        # Check for high user (based on coefficient of variation being low but mean being high)
        # Note: In production, this would compare against regional/national averages
        # For now, we use a simple heuristic based on absolute usage
        if statistics_result.mean_kwh > 1500 and cv < self.VARIABLE_CV_THRESHOLD:
            return UserProfileType.HIGH_USER

        # Check for variable usage (high CV indicates inconsistent usage)
        if cv >= self.VARIABLE_CV_THRESHOLD:
            return UserProfileType.VARIABLE

        # Default to baseline (consistent, predictable usage)
        return UserProfileType.BASELINE

    def project_usage(
        self,
        usage_data: List[MonthlyUsage],
        seasonal_analysis: Optional[SeasonalAnalysis] = None,
    ) -> UsageProjection:
        """
        Project 12-month forward usage based on historical patterns.

        Projection method:
        1. If strong seasonal pattern: Use seasonal averages
        2. If trend detected: Apply trend to moving average
        3. Otherwise: Use simple moving average

        Confidence intervals: ±1.96 * std_dev (95% CI)

        Args:
            usage_data: Historical monthly usage data
            seasonal_analysis: Pre-computed seasonal analysis (optional)

        Returns:
            UsageProjection with 12-month forecast
        """
        if len(usage_data) < 3:
            # Not enough data for projection - use what we have
            avg_kwh = statistics.mean([u.kwh for u in usage_data])
            return UsageProjection(
                projected_monthly_kwh=[avg_kwh] * 12,
                projected_annual_kwh=avg_kwh * 12,
                confidence_lower=[avg_kwh * 0.7] * 12,
                confidence_upper=[avg_kwh * 1.3] * 12,
                confidence_score=0.2,
                method="insufficient_data_average",
                assumptions=[
                    "Less than 3 months of data available",
                    "Using simple average with wide confidence intervals",
                ],
            )

        # Perform seasonal analysis if not provided
        if seasonal_analysis is None:
            seasonal_analysis = self.detect_seasonal_patterns(usage_data)

        assumptions = []
        kwh_values = [u.kwh for u in usage_data]

        # Choose projection method based on patterns
        if (
            seasonal_analysis.has_seasonal_pattern
            and seasonal_analysis.confidence_score >= self.MIN_CONFIDENCE_THRESHOLD
        ):
            # Use seasonal projection
            projected_monthly = self._project_seasonal(usage_data, seasonal_analysis)
            method = "seasonal_average"
            assumptions.append("Strong seasonal pattern detected")
            assumptions.append("Using historical seasonal averages")
            confidence_score = seasonal_analysis.confidence_score * 0.9

        elif len(usage_data) >= 6:
            # Check for trend
            months_numeric = list(range(len(usage_data)))
            slope, intercept, r_value, _, _ = stats.linregress(
                months_numeric, kwh_values
            )

            if abs(r_value) > 0.5:  # Significant trend
                projected_monthly = self._project_with_trend(
                    usage_data, slope, intercept
                )
                method = "linear_trend"
                assumptions.append(f"Detected {'upward' if slope > 0 else 'downward'} trend")
                assumptions.append("Applied linear regression for projection")
                confidence_score = min(abs(r_value), 0.85)
            else:
                # Use moving average
                projected_monthly = self._project_moving_average(usage_data)
                method = "moving_average"
                assumptions.append("No strong trend detected")
                assumptions.append("Using 12-month moving average")
                confidence_score = 0.7
        else:
            # Simple average for limited data
            avg_kwh = statistics.mean(kwh_values)
            projected_monthly = [avg_kwh] * 12
            method = "simple_average"
            assumptions.append("Limited historical data (6-11 months)")
            assumptions.append("Using simple average")
            confidence_score = 0.6

        # Calculate confidence intervals (95% CI)
        std_dev = statistics.stdev(kwh_values) if len(kwh_values) > 1 else statistics.mean(kwh_values) * 0.15
        margin = 1.96 * std_dev

        confidence_lower = [max(0, x - margin) for x in projected_monthly]
        confidence_upper = [x + margin for x in projected_monthly]

        projected_annual = sum(projected_monthly)

        # Adjust confidence based on data quality
        data_completeness = min(len(usage_data) / 12.0, 1.0)
        confidence_score *= data_completeness

        return UsageProjection(
            projected_monthly_kwh=projected_monthly,
            projected_annual_kwh=projected_annual,
            confidence_lower=confidence_lower,
            confidence_upper=confidence_upper,
            confidence_score=confidence_score,
            method=method,
            assumptions=assumptions,
        )

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    def _sort_usage_data(self, usage_data: List[MonthlyUsage]) -> List[MonthlyUsage]:
        """Sort usage data by month chronologically."""
        return sorted(usage_data, key=lambda x: x.month)

    def _get_season(self, month: int) -> SeasonType:
        """
        Get the meteorological season for a given month.

        Winter: Dec(12), Jan(1), Feb(2)
        Spring: Mar(3), Apr(4), May(5)
        Summer: Jun(6), Jul(7), Aug(8)
        Fall: Sep(9), Oct(10), Nov(11)
        """
        if month in [12, 1, 2]:
            return SeasonType.WINTER
        elif month in [3, 4, 5]:
            return SeasonType.SPRING
        elif month in [6, 7, 8]:
            return SeasonType.SUMMER
        else:  # 9, 10, 11
            return SeasonType.FALL

    def _calculate_statistics(
        self, usage_data: List[MonthlyUsage]
    ) -> UsageStatistics:
        """Calculate basic statistical measures."""
        kwh_values = [u.kwh for u in usage_data]

        mean_val = statistics.mean(kwh_values)
        std_dev = statistics.stdev(kwh_values) if len(kwh_values) > 1 else 0.0
        cv = std_dev / mean_val if mean_val > 0 else 0.0

        return UsageStatistics(
            min_kwh=min(kwh_values),
            max_kwh=max(kwh_values),
            mean_kwh=mean_val,
            median_kwh=statistics.median(kwh_values),
            std_dev=std_dev,
            coefficient_of_variation=cv,
            total_annual_kwh=sum(kwh_values),
        )

    def _assess_data_quality(
        self, usage_data: List[MonthlyUsage]
    ) -> DataQualityMetrics:
        """
        Assess the quality and completeness of usage data.
        """
        if not usage_data:
            return DataQualityMetrics(
                total_months=0,
                missing_months=0,
                interpolated_months=0,
                has_gaps=True,
                completeness_pct=0.0,
                quality_score=0.0,
            )

        total_months = len(usage_data)

        # Check for gaps in the time series
        sorted_data = sorted(usage_data, key=lambda x: x.month)
        start_date = sorted_data[0].month
        end_date = sorted_data[-1].month

        # Calculate expected number of months
        months_diff = (
            (end_date.year - start_date.year) * 12
            + end_date.month
            - start_date.month
            + 1
        )

        missing_months = months_diff - total_months
        has_gaps = missing_months > 0

        # Completeness percentage
        completeness_pct = (total_months / months_diff * 100) if months_diff > 0 else 0

        # Quality score (0.0 to 1.0)
        # Based on completeness and presence of zero values
        zero_count = sum(1 for u in usage_data if u.kwh == 0)
        zero_penalty = (zero_count / total_months) * 0.3 if total_months > 0 else 0

        quality_score = (completeness_pct / 100.0) - zero_penalty
        quality_score = max(0.0, min(1.0, quality_score))

        return DataQualityMetrics(
            total_months=total_months,
            missing_months=missing_months,
            interpolated_months=0,  # Will be updated by _fill_missing_months
            has_gaps=has_gaps,
            completeness_pct=completeness_pct,
            quality_score=quality_score,
        )

    def _fill_missing_months(
        self, usage_data: List[MonthlyUsage]
    ) -> List[MonthlyUsage]:
        """
        Fill missing months using linear interpolation.

        Returns:
            Usage data with gaps filled
        """
        if not usage_data:
            return []

        sorted_data = sorted(usage_data, key=lambda x: x.month)
        start_date = sorted_data[0].month
        end_date = sorted_data[-1].month

        # Create a complete month range
        filled_data = []
        current_date = start_date

        usage_dict = {u.month: u.kwh for u in sorted_data}

        while current_date <= end_date:
            if current_date in usage_dict:
                filled_data.append(MonthlyUsage(current_date, usage_dict[current_date]))
            else:
                # Interpolate missing value
                interpolated_kwh = self._interpolate_value(
                    current_date, usage_dict, sorted_data
                )
                filled_data.append(MonthlyUsage(current_date, interpolated_kwh))

            # Move to next month
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)

        return filled_data

    def _interpolate_value(
        self,
        target_date: date,
        usage_dict: dict,
        sorted_data: List[MonthlyUsage],
    ) -> float:
        """
        Interpolate a missing value using neighboring months.
        """
        # Find closest previous and next values
        prev_val = None
        next_val = None

        for usage in sorted_data:
            if usage.month < target_date:
                prev_val = usage.kwh
            elif usage.month > target_date:
                next_val = usage.kwh
                break

        # Interpolate
        if prev_val is not None and next_val is not None:
            return (prev_val + next_val) / 2.0
        elif prev_val is not None:
            return prev_val
        elif next_val is not None:
            return next_val
        else:
            # Fallback to overall average if available
            return statistics.mean([u.kwh for u in sorted_data])

    def _detect_outliers(self, usage_data: List[MonthlyUsage]) -> OutlierDetection:
        """
        Detect anomalous usage using IQR method.
        """
        if len(usage_data) < 4:
            return OutlierDetection(
                has_outliers=False,
                outlier_months=[],
                outlier_values=[],
                method="IQR",
            )

        kwh_values = [u.kwh for u in usage_data]

        # Calculate IQR
        q1 = np.percentile(kwh_values, 25)
        q3 = np.percentile(kwh_values, 75)
        iqr = q3 - q1

        lower_bound = q1 - (self.OUTLIER_IQR_MULTIPLIER * iqr)
        upper_bound = q3 + (self.OUTLIER_IQR_MULTIPLIER * iqr)

        # Identify outliers
        outlier_months = []
        outlier_values = []

        for usage in usage_data:
            if usage.kwh < lower_bound or usage.kwh > upper_bound:
                outlier_months.append(usage.month.strftime("%B %Y"))
                outlier_values.append(usage.kwh)

        return OutlierDetection(
            has_outliers=len(outlier_months) > 0,
            outlier_months=outlier_months,
            outlier_values=outlier_values,
            method="IQR",
        )

    def _handle_outliers(
        self, usage_data: List[MonthlyUsage], outliers: OutlierDetection
    ) -> List[MonthlyUsage]:
        """
        Handle outliers by replacing with interpolated values.
        For now, we keep the original data but flag the outliers.
        In production, you might want to replace extreme outliers.
        """
        # For now, return original data
        # In a more sophisticated version, we could replace outliers
        return usage_data

    def _analyze_peak_offpeak(
        self, usage_data: List[MonthlyUsage], statistics_result: UsageStatistics
    ) -> PeakOffPeakAnalysis:
        """
        Analyze peak and off-peak usage patterns.
        """
        mean_kwh = statistics_result.mean_kwh

        peak_months = []
        off_peak_months = []
        peak_values = []
        off_peak_values = []

        for usage in usage_data:
            month_name = usage.month.strftime("%B")
            if usage.kwh > mean_kwh:
                peak_months.append(month_name)
                peak_values.append(usage.kwh)
            else:
                off_peak_months.append(month_name)
                off_peak_values.append(usage.kwh)

        peak_avg = statistics.mean(peak_values) if peak_values else mean_kwh
        off_peak_avg = statistics.mean(off_peak_values) if off_peak_values else mean_kwh
        ratio = peak_avg / off_peak_avg if off_peak_avg > 0 else 1.0

        return PeakOffPeakAnalysis(
            peak_months=peak_months,
            off_peak_months=off_peak_months,
            peak_avg_kwh=peak_avg,
            off_peak_avg_kwh=off_peak_avg,
            peak_to_offpeak_ratio=ratio,
        )

    def _project_seasonal(
        self, usage_data: List[MonthlyUsage], seasonal_analysis: SeasonalAnalysis
    ) -> List[float]:
        """
        Project 12 months using seasonal averages.
        """
        # Create a mapping of month to season
        season_averages = {
            pattern.season: pattern.avg_kwh for pattern in seasonal_analysis.patterns
        }

        # Project each month based on its season
        projected = []
        for month_num in range(1, 13):
            season = self._get_season(month_num)
            avg = season_averages.get(season, statistics.mean([u.kwh for u in usage_data]))
            projected.append(avg)

        return projected

    def _project_with_trend(
        self, usage_data: List[MonthlyUsage], slope: float, intercept: float
    ) -> List[float]:
        """
        Project 12 months using linear trend.
        """
        last_index = len(usage_data) - 1
        projected = []

        for i in range(12):
            future_index = last_index + i + 1
            value = slope * future_index + intercept
            projected.append(max(0, value))  # Ensure non-negative

        return projected

    def _project_moving_average(self, usage_data: List[MonthlyUsage]) -> List[float]:
        """
        Project 12 months using moving average.
        """
        # Use the last 6 months as moving average window
        window_size = min(6, len(usage_data))
        recent_usage = usage_data[-window_size:]
        avg = statistics.mean([u.kwh for u in recent_usage])

        return [avg] * 12

    def _calculate_overall_confidence(
        self,
        data_quality: DataQualityMetrics,
        seasonal_analysis: SeasonalAnalysis,
        projection: UsageProjection,
    ) -> float:
        """
        Calculate weighted overall confidence score.
        """
        weights = {
            "data_quality": 0.4,
            "seasonal": 0.3,
            "projection": 0.3,
        }

        confidence = (
            data_quality.quality_score * weights["data_quality"]
            + seasonal_analysis.confidence_score * weights["seasonal"]
            + projection.confidence_score * weights["projection"]
        )

        return round(confidence, 3)

    def _generate_warnings(
        self,
        data_quality: DataQualityMetrics,
        outliers: OutlierDetection,
        overall_confidence: float,
    ) -> List[str]:
        """
        Generate warnings about analysis quality.
        """
        warnings = []

        if data_quality.has_gaps:
            warnings.append(
                f"Data has {data_quality.missing_months} missing months - values interpolated"
            )

        if data_quality.completeness_pct < 75:
            warnings.append(
                f"Data completeness is only {data_quality.completeness_pct:.1f}% - analysis may be unreliable"
            )

        if outliers.has_outliers:
            warnings.append(
                f"Detected {len(outliers.outlier_months)} anomalous usage months - may indicate data errors or unusual events"
            )

        if overall_confidence < self.MIN_CONFIDENCE_THRESHOLD:
            warnings.append(
                f"Low confidence score ({overall_confidence:.2f}) - use results with caution"
            )

        return warnings

    def _create_insufficient_data_profile(
        self,
        usage_data: List[MonthlyUsage],
        user_id: Optional[str],
        data_quality: DataQualityMetrics,
        regional_avg_kwh: Optional[float],
    ) -> UsageProfile:
        """
        Create a minimal profile for cases with insufficient data.
        Uses regional average if provided.
        """
        if usage_data:
            avg_kwh = statistics.mean([u.kwh for u in usage_data])
            data_start = usage_data[0].month
            data_end = usage_data[-1].month
        elif regional_avg_kwh:
            avg_kwh = regional_avg_kwh
            data_start = date.today()
            data_end = date.today()
        else:
            avg_kwh = 0.0
            data_start = date.today()
            data_end = date.today()

        return UsageProfile(
            user_id=user_id,
            profile_type=UserProfileType.INSUFFICIENT_DATA,
            statistics=UsageStatistics(
                min_kwh=avg_kwh,
                max_kwh=avg_kwh,
                mean_kwh=avg_kwh,
                median_kwh=avg_kwh,
                std_dev=0.0,
                coefficient_of_variation=0.0,
                total_annual_kwh=avg_kwh * 12,
            ),
            seasonal_analysis=SeasonalAnalysis(
                has_seasonal_pattern=False,
                dominant_season=None,
                patterns=[],
                summer_to_winter_ratio=1.0,
                peak_to_avg_ratio=1.0,
                confidence_score=0.0,
            ),
            peak_offpeak=PeakOffPeakAnalysis(
                peak_months=[],
                off_peak_months=[],
                peak_avg_kwh=avg_kwh,
                off_peak_avg_kwh=avg_kwh,
                peak_to_offpeak_ratio=1.0,
            ),
            outliers=OutlierDetection(
                has_outliers=False,
                outlier_months=[],
                outlier_values=[],
                method="N/A",
            ),
            data_quality=data_quality,
            projection=UsageProjection(
                projected_monthly_kwh=[avg_kwh] * 12,
                projected_annual_kwh=avg_kwh * 12,
                confidence_lower=[avg_kwh * 0.5] * 12,
                confidence_upper=[avg_kwh * 1.5] * 12,
                confidence_score=0.1,
                method="regional_average" if regional_avg_kwh else "insufficient_data",
                assumptions=[
                    "Insufficient historical data (<3 months)",
                    "Using regional average" if regional_avg_kwh else "Using limited data average",
                ],
            ),
            analysis_date=datetime.now(),
            data_period_start=data_start,
            data_period_end=data_end,
            num_months_analyzed=len(usage_data),
            overall_confidence=0.1,
            warnings=[
                "Insufficient data for reliable analysis",
                "Projections based on limited information or regional averages",
            ],
        )
