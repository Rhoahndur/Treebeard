"""
Unit Tests for Usage Pattern Analysis Service
Story 1.4 - Epic 1: Data Infrastructure & Pipeline

Test coverage targets:
- Seasonal pattern detection
- User profile classification
- Usage projection
- Edge case handling
- Data quality assessment
- Outlier detection

Target: >80% code coverage
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
import statistics

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from backend.schemas.usage_analysis import (
    MonthlyUsage,
    UserProfileType,
    SeasonType,
)
from backend.services.usage_analysis import UsageAnalysisService


class TestUsageAnalysisService:
    """Test suite for UsageAnalysisService"""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return UsageAnalysisService()

    @pytest.fixture
    def baseline_usage_data(self):
        """
        Generate baseline usage data (consistent year-round).
        """
        base_date = date(2024, 1, 1)
        usage_data = []

        for i in range(12):
            month = base_date.replace(month=i + 1)
            # Consistent usage around 800 kWh with minor variation
            kwh = 800 + (i % 3) * 10
            usage_data.append(MonthlyUsage(month, kwh))

        return usage_data

    @pytest.fixture
    def seasonal_usage_data(self):
        """
        Generate seasonal usage data (summer peak).
        """
        base_date = date(2024, 1, 1)
        usage_data = []

        # Seasonal pattern: high in summer, low in winter
        monthly_kwh = {
            1: 700,   # Jan - winter
            2: 680,   # Feb - winter
            3: 750,   # Mar - spring
            4: 800,   # Apr - spring
            5: 850,   # May - spring
            6: 1200,  # Jun - summer peak
            7: 1400,  # Jul - summer peak
            8: 1300,  # Aug - summer peak
            9: 900,   # Sep - fall
            10: 800,  # Oct - fall
            11: 750,  # Nov - fall
            12: 720,  # Dec - winter
        }

        for month_num, kwh in monthly_kwh.items():
            month = base_date.replace(month=month_num)
            usage_data.append(MonthlyUsage(month, kwh))

        return usage_data

    @pytest.fixture
    def variable_usage_data(self):
        """
        Generate variable usage data (high coefficient of variation).
        """
        base_date = date(2024, 1, 1)
        usage_data = []

        # Highly variable usage
        monthly_kwh = [500, 1200, 600, 1400, 550, 1100, 650, 1300, 700, 1000, 800, 900]

        for i, kwh in enumerate(monthly_kwh):
            month = base_date.replace(month=i + 1)
            usage_data.append(MonthlyUsage(month, kwh))

        return usage_data

    @pytest.fixture
    def high_user_data(self):
        """
        Generate high user data (consistently high usage).
        """
        base_date = date(2024, 1, 1)
        usage_data = []

        for i in range(12):
            month = base_date.replace(month=i + 1)
            # Consistently high usage
            kwh = 2000 + (i % 3) * 50
            usage_data.append(MonthlyUsage(month, kwh))

        return usage_data

    @pytest.fixture
    def incomplete_usage_data(self):
        """
        Generate incomplete usage data (only 6 months).
        """
        base_date = date(2024, 1, 1)
        usage_data = []

        for i in range(6):
            month = base_date.replace(month=i + 1)
            kwh = 800 + i * 10
            usage_data.append(MonthlyUsage(month, kwh))

        return usage_data

    @pytest.fixture
    def usage_with_gaps(self):
        """
        Generate usage data with missing months.
        """
        base_date = date(2024, 1, 1)
        usage_data = []

        # Skip months 3, 5, 8
        for i in [1, 2, 4, 6, 7, 9, 10, 11, 12]:
            month = base_date.replace(month=i)
            kwh = 800
            usage_data.append(MonthlyUsage(month, kwh))

        return usage_data

    @pytest.fixture
    def usage_with_outliers(self):
        """
        Generate usage data with anomalous spikes.
        """
        base_date = date(2024, 1, 1)
        usage_data = []

        for i in range(12):
            month = base_date.replace(month=i + 1)
            # Normal usage except for two outliers
            if i == 3:  # April - unusually high
                kwh = 2500
            elif i == 8:  # September - unusually low
                kwh = 100
            else:
                kwh = 800
            usage_data.append(MonthlyUsage(month, kwh))

        return usage_data

    # ========================================================================
    # TEST: Basic Analysis
    # ========================================================================

    def test_analyze_baseline_profile(self, service, baseline_usage_data):
        """Test analysis of baseline (consistent) usage profile."""
        profile = service.analyze_usage_patterns(baseline_usage_data, user_id="user_001")

        assert profile.profile_type == UserProfileType.BASELINE
        assert profile.user_id == "user_001"
        assert profile.num_months_analyzed == 12
        assert profile.overall_confidence > 0.5
        assert profile.statistics.coefficient_of_variation < 0.1  # Low variation

    def test_analyze_seasonal_profile(self, service, seasonal_usage_data):
        """Test analysis of seasonal usage profile."""
        profile = service.analyze_usage_patterns(seasonal_usage_data, user_id="user_002")

        assert profile.profile_type == UserProfileType.SEASONAL
        assert profile.seasonal_analysis.has_seasonal_pattern is True
        assert profile.seasonal_analysis.summer_to_winter_ratio > 1.5
        assert profile.seasonal_analysis.dominant_season == SeasonType.SUMMER

    def test_analyze_variable_profile(self, service, variable_usage_data):
        """Test analysis of variable usage profile."""
        profile = service.analyze_usage_patterns(variable_usage_data, user_id="user_003")

        # Should be either VARIABLE or SEASONAL depending on pattern
        assert profile.profile_type in [UserProfileType.VARIABLE, UserProfileType.SEASONAL]
        assert profile.statistics.coefficient_of_variation > 0.2  # High variation

    def test_analyze_high_user_profile(self, service, high_user_data):
        """Test analysis of high user profile."""
        profile = service.analyze_usage_patterns(high_user_data, user_id="user_004")

        assert profile.profile_type in [UserProfileType.HIGH_USER, UserProfileType.BASELINE]
        assert profile.statistics.mean_kwh > 1500  # High average usage

    # ========================================================================
    # TEST: Seasonal Pattern Detection
    # ========================================================================

    def test_detect_summer_peak(self, service, seasonal_usage_data):
        """Test detection of summer peak pattern."""
        seasonal = service.detect_seasonal_patterns(seasonal_usage_data)

        assert seasonal.has_seasonal_pattern is True
        assert seasonal.dominant_season == SeasonType.SUMMER
        assert seasonal.summer_to_winter_ratio > 1.5
        assert seasonal.confidence_score > 0.5

        # Check that we have patterns for all seasons
        assert len(seasonal.patterns) == 4

    def test_detect_no_seasonal_pattern(self, service, baseline_usage_data):
        """Test detection when no seasonal pattern exists."""
        seasonal = service.detect_seasonal_patterns(baseline_usage_data)

        assert seasonal.has_seasonal_pattern is False
        assert abs(seasonal.summer_to_winter_ratio - 1.0) < 0.35  # Close to 1

    def test_seasonal_pattern_insufficient_data(self, service):
        """Test seasonal detection with insufficient data."""
        # Only 3 months
        data = [
            MonthlyUsage(date(2024, 1, 1), 800),
            MonthlyUsage(date(2024, 2, 1), 820),
            MonthlyUsage(date(2024, 3, 1), 810),
        ]

        seasonal = service.detect_seasonal_patterns(data)

        assert seasonal.confidence_score < 0.5

    # ========================================================================
    # TEST: User Profile Classification
    # ========================================================================

    def test_classify_baseline(self, service, baseline_usage_data):
        """Test baseline classification."""
        profile_type = service.classify_user_profile(baseline_usage_data)
        assert profile_type == UserProfileType.BASELINE

    def test_classify_seasonal(self, service, seasonal_usage_data):
        """Test seasonal classification."""
        profile_type = service.classify_user_profile(seasonal_usage_data)
        assert profile_type == UserProfileType.SEASONAL

    def test_classify_variable(self, service, variable_usage_data):
        """Test variable classification."""
        profile_type = service.classify_user_profile(variable_usage_data)
        assert profile_type in [UserProfileType.VARIABLE, UserProfileType.SEASONAL]

    def test_classify_insufficient_data(self, service):
        """Test classification with insufficient data."""
        data = [MonthlyUsage(date(2024, 1, 1), 800)]
        profile_type = service.classify_user_profile(data)
        assert profile_type == UserProfileType.INSUFFICIENT_DATA

    # ========================================================================
    # TEST: Usage Projection
    # ========================================================================

    def test_project_baseline_usage(self, service, baseline_usage_data):
        """Test 12-month projection for baseline usage."""
        projection = service.project_usage(baseline_usage_data)

        assert len(projection.projected_monthly_kwh) == 12
        assert projection.projected_annual_kwh > 0
        assert len(projection.confidence_lower) == 12
        assert len(projection.confidence_upper) == 12
        assert 0 <= projection.confidence_score <= 1.0
        assert projection.method in ["seasonal_average", "moving_average", "simple_average"]

        # Confidence bounds should be reasonable
        for i in range(12):
            assert projection.confidence_lower[i] <= projection.projected_monthly_kwh[i]
            assert projection.confidence_upper[i] >= projection.projected_monthly_kwh[i]

    def test_project_seasonal_usage(self, service, seasonal_usage_data):
        """Test projection for seasonal usage."""
        projection = service.project_usage(seasonal_usage_data)

        assert len(projection.projected_monthly_kwh) == 12
        assert projection.confidence_score > 0.5
        # Seasonal projection should show variation
        max_proj = max(projection.projected_monthly_kwh)
        min_proj = min(projection.projected_monthly_kwh)
        assert max_proj > min_proj * 1.2  # At least 20% variation

    def test_project_insufficient_data(self, service):
        """Test projection with minimal data."""
        data = [
            MonthlyUsage(date(2024, 1, 1), 800),
            MonthlyUsage(date(2024, 2, 1), 820),
        ]
        projection = service.project_usage(data)

        assert len(projection.projected_monthly_kwh) == 12
        assert projection.confidence_score < 0.5
        assert "insufficient" in projection.method.lower()

    # ========================================================================
    # TEST: Edge Cases
    # ========================================================================

    def test_incomplete_data_handling(self, service, incomplete_usage_data):
        """Test handling of incomplete data (6 months)."""
        profile = service.analyze_usage_patterns(incomplete_usage_data)

        assert profile.num_months_analyzed == 6
        assert profile.data_quality.total_months == 6
        # Should still produce a profile
        assert profile.profile_type in [
            UserProfileType.BASELINE,
            UserProfileType.VARIABLE,
            UserProfileType.HIGH_USER,
            UserProfileType.SEASONAL,
        ]

    def test_missing_months_interpolation(self, service, usage_with_gaps):
        """Test interpolation of missing months."""
        profile = service.analyze_usage_patterns(usage_with_gaps)

        assert profile.data_quality.has_gaps is True
        assert profile.data_quality.missing_months > 0
        assert "missing months" in " ".join(profile.warnings).lower()

    def test_outlier_detection(self, service, usage_with_outliers):
        """Test outlier detection."""
        profile = service.analyze_usage_patterns(usage_with_outliers)

        assert profile.outliers.has_outliers is True
        assert len(profile.outliers.outlier_months) > 0
        assert len(profile.outliers.outlier_values) > 0
        assert "anomalous" in " ".join(profile.warnings).lower()

    def test_very_limited_data(self, service):
        """Test handling of very limited data (<3 months)."""
        data = [
            MonthlyUsage(date(2024, 1, 1), 800),
            MonthlyUsage(date(2024, 2, 1), 820),
        ]
        profile = service.analyze_usage_patterns(data)

        assert profile.profile_type == UserProfileType.INSUFFICIENT_DATA
        assert profile.overall_confidence < 0.5
        assert len(profile.warnings) > 0

    def test_new_customer_with_regional_average(self, service):
        """Test handling of new customer with regional average."""
        data = []  # No data
        regional_avg = 950.0

        profile = service.analyze_usage_patterns(
            data, user_id="new_user", regional_avg_kwh=regional_avg
        )

        assert profile.profile_type == UserProfileType.INSUFFICIENT_DATA
        assert profile.statistics.mean_kwh == regional_avg
        assert "regional average" in " ".join(profile.warnings).lower()

    def test_zero_usage_months(self, service):
        """Test handling of zero usage months (e.g., vacant property)."""
        base_date = date(2024, 1, 1)
        data = []

        for i in range(12):
            month = base_date.replace(month=i + 1)
            # Some months with zero usage
            kwh = 0 if i in [2, 3, 7] else 800
            data.append(MonthlyUsage(month, kwh))

        profile = service.analyze_usage_patterns(data)

        # Should handle zeros gracefully
        assert profile.statistics.min_kwh == 0
        assert profile.data_quality.quality_score < 1.0

    # ========================================================================
    # TEST: Data Quality Assessment
    # ========================================================================

    def test_data_quality_complete(self, service, baseline_usage_data):
        """Test data quality assessment for complete data."""
        profile = service.analyze_usage_patterns(baseline_usage_data)

        assert profile.data_quality.completeness_pct == 100.0
        assert profile.data_quality.has_gaps is False
        assert profile.data_quality.missing_months == 0
        assert profile.data_quality.quality_score > 0.8

    def test_data_quality_with_gaps(self, service, usage_with_gaps):
        """Test data quality assessment with gaps."""
        profile = service.analyze_usage_patterns(usage_with_gaps)

        assert profile.data_quality.completeness_pct < 100.0
        assert profile.data_quality.has_gaps is True
        assert profile.data_quality.missing_months > 0

    # ========================================================================
    # TEST: Statistical Calculations
    # ========================================================================

    def test_statistics_calculation(self, service, baseline_usage_data):
        """Test statistical measures calculation."""
        profile = service.analyze_usage_patterns(baseline_usage_data)
        stats = profile.statistics

        # Verify calculations
        kwh_values = [u.kwh for u in baseline_usage_data]
        assert stats.min_kwh == min(kwh_values)
        assert stats.max_kwh == max(kwh_values)
        assert abs(stats.mean_kwh - statistics.mean(kwh_values)) < 0.01
        assert abs(stats.median_kwh - statistics.median(kwh_values)) < 0.01
        assert stats.total_annual_kwh == sum(kwh_values)

    def test_coefficient_of_variation(self, service, baseline_usage_data, variable_usage_data):
        """Test coefficient of variation calculation."""
        baseline_profile = service.analyze_usage_patterns(baseline_usage_data)
        variable_profile = service.analyze_usage_patterns(variable_usage_data)

        # Baseline should have low CV, variable should have high CV
        assert baseline_profile.statistics.coefficient_of_variation < 0.15
        assert variable_profile.statistics.coefficient_of_variation > 0.20

    # ========================================================================
    # TEST: Peak/Off-Peak Analysis
    # ========================================================================

    def test_peak_offpeak_analysis(self, service, seasonal_usage_data):
        """Test peak and off-peak analysis."""
        profile = service.analyze_usage_patterns(seasonal_usage_data)
        peak_offpeak = profile.peak_offpeak

        assert len(peak_offpeak.peak_months) > 0
        assert len(peak_offpeak.off_peak_months) > 0
        assert peak_offpeak.peak_avg_kwh > peak_offpeak.off_peak_avg_kwh
        assert peak_offpeak.peak_to_offpeak_ratio > 1.0

    # ========================================================================
    # TEST: Performance
    # ========================================================================

    def test_performance_12_months(self, service, baseline_usage_data):
        """Test that analysis completes within performance target (<100ms)."""
        start = datetime.now()
        profile = service.analyze_usage_patterns(baseline_usage_data)
        elapsed_ms = (datetime.now() - start).total_seconds() * 1000

        # Should complete in under 100ms
        assert elapsed_ms < 100, f"Analysis took {elapsed_ms:.1f}ms (target: <100ms)"

    # ========================================================================
    # TEST: Serialization
    # ========================================================================

    def test_profile_to_dict(self, service, baseline_usage_data):
        """Test profile serialization to dictionary."""
        profile = service.analyze_usage_patterns(baseline_usage_data)
        profile_dict = profile.to_dict()

        # Verify structure
        assert isinstance(profile_dict, dict)
        assert "user_id" in profile_dict
        assert "profile_type" in profile_dict
        assert "statistics" in profile_dict
        assert "seasonal_analysis" in profile_dict
        assert "projection" in profile_dict
        assert "overall_confidence" in profile_dict

    # ========================================================================
    # TEST: Edge Cases - Invalid Data
    # ========================================================================

    def test_negative_kwh_validation(self):
        """Test that negative kWh values raise an error."""
        with pytest.raises(ValueError):
            MonthlyUsage(date(2024, 1, 1), -100)

    def test_empty_usage_data(self, service):
        """Test handling of empty usage data."""
        profile = service.analyze_usage_patterns([], user_id="empty_user")

        assert profile.profile_type == UserProfileType.INSUFFICIENT_DATA
        assert profile.overall_confidence < 0.5

    # ========================================================================
    # TEST: Confidence Scoring
    # ========================================================================

    def test_confidence_score_complete_data(self, service, baseline_usage_data):
        """Test confidence scoring with complete data."""
        profile = service.analyze_usage_patterns(baseline_usage_data)
        assert profile.overall_confidence > 0.6

    def test_confidence_score_incomplete_data(self, service, incomplete_usage_data):
        """Test confidence scoring with incomplete data."""
        profile = service.analyze_usage_patterns(incomplete_usage_data)
        # Should have lower confidence than complete data
        assert profile.overall_confidence < 0.9

    def test_confidence_score_with_gaps(self, service, usage_with_gaps):
        """Test confidence scoring with data gaps."""
        profile = service.analyze_usage_patterns(usage_with_gaps)
        # Gaps should reduce confidence
        assert profile.overall_confidence < 0.85


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
