"""
Standalone Unit Tests for Usage Pattern Analysis Service
Story 1.4 - Epic 1: Data Infrastructure & Pipeline

This test file imports only the necessary modules for testing the usage analysis
service without requiring all project dependencies.

Run with: python3 test_usage_analysis_standalone.py
"""

from datetime import date
import sys
import os

# Add src to path for imports - bypass __init__.py by importing modules directly
src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
sys.path.insert(0, src_path)

# Import modules directly without triggering __init__.py imports
import importlib.util

# Load usage_analysis schemas
spec = importlib.util.spec_from_file_location(
    "usage_analysis_schemas",
    os.path.join(src_path, "backend/schemas/usage_analysis.py")
)
usage_schemas = importlib.util.module_from_spec(spec)
spec.loader.exec_module(usage_schemas)

MonthlyUsage = usage_schemas.MonthlyUsage
UserProfileType = usage_schemas.UserProfileType
SeasonType = usage_schemas.SeasonType
UsageProfile = usage_schemas.UsageProfile

# Load service (it will import schemas correctly)
spec = importlib.util.spec_from_file_location(
    "usage_analysis_service",
    os.path.join(src_path, "backend/services/usage_analysis.py")
)
usage_service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(usage_service)

UsageAnalysisService = usage_service.UsageAnalysisService


def create_baseline_usage_data():
    """Generate baseline usage data (consistent year-round)."""
    base_date = date(2024, 1, 1)
    usage_data = []

    for i in range(12):
        month = base_date.replace(month=i + 1)
        kwh = 800 + (i % 3) * 10
        usage_data.append(MonthlyUsage(month, kwh))

    return usage_data


def create_seasonal_usage_data():
    """Generate seasonal usage data (summer peak)."""
    base_date = date(2024, 1, 1)
    usage_data = []

    monthly_kwh = {
        1: 700, 2: 680, 3: 750, 4: 800, 5: 850, 6: 1200,
        7: 1400, 8: 1300, 9: 900, 10: 800, 11: 750, 12: 720,
    }

    for month_num, kwh in monthly_kwh.items():
        month = base_date.replace(month=month_num)
        usage_data.append(MonthlyUsage(month, kwh))

    return usage_data


def test_baseline_analysis():
    """Test analysis of baseline profile."""
    print("Test 1: Baseline Usage Analysis...")
    service = UsageAnalysisService()
    data = create_baseline_usage_data()

    profile = service.analyze_usage_patterns(data, user_id="test_001")

    assert profile.profile_type == UserProfileType.BASELINE, f"Expected BASELINE, got {profile.profile_type}"
    assert profile.num_months_analyzed == 12
    assert profile.overall_confidence > 0.5
    print(f"  ✓ Profile type: {profile.profile_type.value}")
    print(f"  ✓ Confidence: {profile.overall_confidence:.2f}")
    print(f"  ✓ Mean usage: {profile.statistics.mean_kwh:.1f} kWh")


def test_seasonal_analysis():
    """Test analysis of seasonal profile."""
    print("\nTest 2: Seasonal Usage Analysis...")
    service = UsageAnalysisService()
    data = create_seasonal_usage_data()

    profile = service.analyze_usage_patterns(data, user_id="test_002")

    assert profile.profile_type == UserProfileType.SEASONAL
    assert profile.seasonal_analysis.has_seasonal_pattern is True
    assert profile.seasonal_analysis.dominant_season == SeasonType.SUMMER
    print(f"  ✓ Profile type: {profile.profile_type.value}")
    print(f"  ✓ Dominant season: {profile.seasonal_analysis.dominant_season.value}")
    print(f"  ✓ Summer/Winter ratio: {profile.seasonal_analysis.summer_to_winter_ratio:.2f}")


def test_projection():
    """Test 12-month usage projection."""
    print("\nTest 3: Usage Projection...")
    service = UsageAnalysisService()
    data = create_baseline_usage_data()

    profile = service.analyze_usage_patterns(data)
    projection = profile.projection

    assert len(projection.projected_monthly_kwh) == 12
    assert projection.projected_annual_kwh > 0
    assert projection.confidence_score > 0
    print(f"  ✓ Projected annual usage: {projection.projected_annual_kwh:.1f} kWh")
    print(f"  ✓ Projection method: {projection.method}")
    print(f"  ✓ Confidence: {projection.confidence_score:.2f}")


def test_edge_cases():
    """Test edge case handling."""
    print("\nTest 4: Edge Cases...")
    service = UsageAnalysisService()

    # Test with minimal data
    minimal_data = [
        MonthlyUsage(date(2024, 1, 1), 800),
        MonthlyUsage(date(2024, 2, 1), 820),
    ]

    profile = service.analyze_usage_patterns(minimal_data)
    assert profile.profile_type == UserProfileType.INSUFFICIENT_DATA
    print(f"  ✓ Minimal data handled: {profile.profile_type.value}")

    # Test with regional average
    profile_regional = service.analyze_usage_patterns([], regional_avg_kwh=950.0)
    assert profile_regional.statistics.mean_kwh == 950.0
    print(f"  ✓ Regional average used: {profile_regional.statistics.mean_kwh:.1f} kWh")


def test_performance():
    """Test performance requirement (<100ms for 12 months)."""
    print("\nTest 5: Performance Check...")
    import time
    service = UsageAnalysisService()
    data = create_baseline_usage_data()

    start = time.time()
    profile = service.analyze_usage_patterns(data)
    elapsed_ms = (time.time() - start) * 1000

    print(f"  ✓ Analysis completed in {elapsed_ms:.1f}ms")
    if elapsed_ms < 100:
        print(f"  ✓ Performance target met (<100ms)")
    else:
        print(f"  ⚠ Performance target missed (target: <100ms)")


def test_data_quality():
    """Test data quality assessment."""
    print("\nTest 6: Data Quality Assessment...")
    service = UsageAnalysisService()

    # Create data with gaps
    base_date = date(2024, 1, 1)
    data_with_gaps = []
    for i in [1, 2, 4, 6, 7, 9, 10, 11, 12]:  # Skip months 3, 5, 8
        month = base_date.replace(month=i)
        data_with_gaps.append(MonthlyUsage(month, 800))

    profile = service.analyze_usage_patterns(data_with_gaps)

    assert profile.data_quality.has_gaps is True
    assert profile.data_quality.missing_months > 0
    print(f"  ✓ Gaps detected: {profile.data_quality.missing_months} missing months")
    print(f"  ✓ Completeness: {profile.data_quality.completeness_pct:.1f}%")
    print(f"  ✓ Quality score: {profile.data_quality.quality_score:.2f}")


def test_serialization():
    """Test profile serialization."""
    print("\nTest 7: Profile Serialization...")
    service = UsageAnalysisService()
    data = create_baseline_usage_data()

    profile = service.analyze_usage_patterns(data)
    profile_dict = profile.to_dict()

    assert isinstance(profile_dict, dict)
    assert "user_id" in profile_dict
    assert "profile_type" in profile_dict
    assert "statistics" in profile_dict
    assert "seasonal_analysis" in profile_dict
    print(f"  ✓ Profile serialized to dictionary")
    print(f"  ✓ Keys present: {len(profile_dict)} top-level fields")


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("Usage Pattern Analysis Service - Test Suite")
    print("Story 1.4 - Epic 1: Data Infrastructure & Pipeline")
    print("=" * 70)

    try:
        test_baseline_analysis()
        test_seasonal_analysis()
        test_projection()
        test_edge_cases()
        test_performance()
        test_data_quality()
        test_serialization()

        print("\n" + "=" * 70)
        print("✓ All tests passed!")
        print("=" * 70)
        return True

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
