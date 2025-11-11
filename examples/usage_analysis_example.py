"""
Usage Pattern Analysis - Quick Start Example
Story 1.4 - For Story 2.1 Integration

This example demonstrates how to use the Usage Pattern Analysis service.
Run with: python3 examples/usage_analysis_example.py
"""

import sys
import os
from datetime import date

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Note: This will require dependencies to be installed: numpy, scipy
# pip install numpy scipy

try:
    from backend.schemas.usage_analysis import MonthlyUsage, UserProfileType, SeasonType
    from backend.services.usage_analysis import UsageAnalysisService
except ImportError as e:
    print(f"Error: {e}")
    print("\nPlease install dependencies first:")
    print("  pip install numpy scipy")
    sys.exit(1)


def example_1_baseline_user():
    """Example 1: Analyzing a baseline user with consistent usage."""
    print("=" * 70)
    print("Example 1: Baseline User (Consistent Usage)")
    print("=" * 70)

    # Create service
    service = UsageAnalysisService()

    # Generate baseline usage data (consistent ~800 kWh/month)
    usage_data = [
        MonthlyUsage(date(2024, 1, 1), 820.0),
        MonthlyUsage(date(2024, 2, 1), 790.0),
        MonthlyUsage(date(2024, 3, 1), 810.0),
        MonthlyUsage(date(2024, 4, 1), 800.0),
        MonthlyUsage(date(2024, 5, 1), 830.0),
        MonthlyUsage(date(2024, 6, 1), 850.0),
        MonthlyUsage(date(2024, 7, 1), 840.0),
        MonthlyUsage(date(2024, 8, 1), 820.0),
        MonthlyUsage(date(2024, 9, 1), 810.0),
        MonthlyUsage(date(2024, 10, 1), 800.0),
        MonthlyUsage(date(2024, 11, 1), 790.0),
        MonthlyUsage(date(2024, 12, 1), 810.0),
    ]

    # Analyze
    profile = service.analyze_usage_patterns(usage_data, user_id="baseline_user_001")

    # Display results
    print(f"\n📊 Analysis Results:")
    print(f"  Profile Type: {profile.profile_type.value}")
    print(f"  Mean Usage: {profile.statistics.mean_kwh:.1f} kWh/month")
    print(f"  Annual Total: {profile.statistics.total_annual_kwh:.1f} kWh")
    print(f"  Variation (CV): {profile.statistics.coefficient_of_variation:.3f}")
    print(f"  Confidence: {profile.overall_confidence:.2%}")

    print(f"\n📈 Projection:")
    print(f"  Projected Annual: {profile.projection.projected_annual_kwh:.1f} kWh")
    print(f"  Method: {profile.projection.method}")
    print(f"  Confidence: {profile.projection.confidence_score:.2%}")

    print(f"\n🌡️  Seasonal Analysis:")
    print(f"  Has Seasonal Pattern: {profile.seasonal_analysis.has_seasonal_pattern}")
    print(f"  Summer/Winter Ratio: {profile.seasonal_analysis.summer_to_winter_ratio:.2f}")

    if profile.warnings:
        print(f"\n⚠️  Warnings:")
        for warning in profile.warnings:
            print(f"  - {warning}")


def example_2_seasonal_user():
    """Example 2: Analyzing a seasonal user with summer peak."""
    print("\n\n" + "=" * 70)
    print("Example 2: Seasonal User (Summer Peak)")
    print("=" * 70)

    service = UsageAnalysisService()

    # Generate seasonal usage data with summer peak
    usage_data = [
        MonthlyUsage(date(2024, 1, 1), 700.0),   # Winter
        MonthlyUsage(date(2024, 2, 1), 680.0),   # Winter
        MonthlyUsage(date(2024, 3, 1), 750.0),   # Spring
        MonthlyUsage(date(2024, 4, 1), 800.0),   # Spring
        MonthlyUsage(date(2024, 5, 1), 950.0),   # Spring
        MonthlyUsage(date(2024, 6, 1), 1400.0),  # Summer - A/C usage
        MonthlyUsage(date(2024, 7, 1), 1600.0),  # Summer - Peak
        MonthlyUsage(date(2024, 8, 1), 1500.0),  # Summer
        MonthlyUsage(date(2024, 9, 1), 1000.0),  # Fall
        MonthlyUsage(date(2024, 10, 1), 850.0),  # Fall
        MonthlyUsage(date(2024, 11, 1), 750.0),  # Fall
        MonthlyUsage(date(2024, 12, 1), 720.0),  # Winter
    ]

    # Analyze
    profile = service.analyze_usage_patterns(usage_data, user_id="seasonal_user_001")

    # Display results
    print(f"\n📊 Analysis Results:")
    print(f"  Profile Type: {profile.profile_type.value}")
    print(f"  Mean Usage: {profile.statistics.mean_kwh:.1f} kWh/month")
    print(f"  Annual Total: {profile.statistics.total_annual_kwh:.1f} kWh")
    print(f"  Min/Max: {profile.statistics.min_kwh:.1f} / {profile.statistics.max_kwh:.1f} kWh")

    print(f"\n🌡️  Seasonal Analysis:")
    print(f"  Has Seasonal Pattern: {profile.seasonal_analysis.has_seasonal_pattern}")
    print(f"  Dominant Season: {profile.seasonal_analysis.dominant_season.value if profile.seasonal_analysis.dominant_season else 'None'}")
    print(f"  Summer/Winter Ratio: {profile.seasonal_analysis.summer_to_winter_ratio:.2f}x")
    print(f"  Peak/Average Ratio: {profile.seasonal_analysis.peak_to_avg_ratio:.2f}x")

    print(f"\n📆 Seasonal Patterns:")
    for pattern in profile.seasonal_analysis.patterns:
        print(f"  {pattern.season.value.upper():8s}: {pattern.avg_kwh:6.0f} kWh avg "
              f"(peak in {pattern.peak_month}: {pattern.peak_kwh:.0f} kWh)")

    print(f"\n📈 Projection for Next 12 Months:")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for i, (month, kwh) in enumerate(zip(months, profile.projection.projected_monthly_kwh)):
        print(f"  {month}: {kwh:6.0f} kWh", end="")
        if i % 3 == 2:  # New line every 3 months
            print()


def example_3_new_customer():
    """Example 3: Handling a new customer with no historical data."""
    print("\n\n" + "=" * 70)
    print("Example 3: New Customer (No Historical Data)")
    print("=" * 70)

    service = UsageAnalysisService()

    # No usage data, but we have regional average
    regional_avg = 950.0

    # Analyze
    profile = service.analyze_usage_patterns(
        [],
        user_id="new_customer_001",
        regional_avg_kwh=regional_avg
    )

    print(f"\n📊 Analysis Results:")
    print(f"  Profile Type: {profile.profile_type.value}")
    print(f"  Estimated Usage: {profile.statistics.mean_kwh:.1f} kWh/month")
    print(f"  Source: Regional Average")
    print(f"  Confidence: {profile.overall_confidence:.2%}")

    print(f"\n⚠️  Warnings:")
    for warning in profile.warnings:
        print(f"  - {warning}")

    print(f"\n💡 Recommendation:")
    print(f"  Use conservative estimates for plan selection")
    print(f"  Re-analyze after 3+ months of actual usage data")


def example_4_integration_with_scoring():
    """Example 4: How Story 2.1 would integrate this for plan scoring."""
    print("\n\n" + "=" * 70)
    print("Example 4: Integration with Plan Scoring (Story 2.1)")
    print("=" * 70)

    service = UsageAnalysisService()

    # User's historical data
    usage_data = [
        MonthlyUsage(date(2024, 1, 1), 750.0),
        MonthlyUsage(date(2024, 2, 1), 720.0),
        MonthlyUsage(date(2024, 3, 1), 780.0),
        MonthlyUsage(date(2024, 4, 1), 850.0),
        MonthlyUsage(date(2024, 5, 1), 1100.0),
        MonthlyUsage(date(2024, 6, 1), 1400.0),
        MonthlyUsage(date(2024, 7, 1), 1600.0),
        MonthlyUsage(date(2024, 8, 1), 1500.0),
        MonthlyUsage(date(2024, 9, 1), 1000.0),
        MonthlyUsage(date(2024, 10, 1), 850.0),
        MonthlyUsage(date(2024, 11, 1), 800.0),
        MonthlyUsage(date(2024, 12, 1), 750.0),
    ]

    # Analyze usage
    profile = service.analyze_usage_patterns(usage_data, user_id="scoring_example")

    # Simulate plan details (Story 2.1 would get this from plan catalog)
    class MockPlan:
        def __init__(self, name, rate, has_seasonal_rates):
            self.name = name
            self.rate_per_kwh = rate
            self.has_seasonal_rates = has_seasonal_rates

    plans = [
        MockPlan("Standard Fixed", 0.12, False),
        MockPlan("Seasonal Saver", 0.11, True),
        MockPlan("Budget Basic", 0.13, False),
    ]

    print(f"\n📊 User Profile:")
    print(f"  Type: {profile.profile_type.value}")
    print(f"  Projected Annual: {profile.projection.projected_annual_kwh:.0f} kWh")
    print(f"  Has Seasonal Pattern: {profile.seasonal_analysis.has_seasonal_pattern}")
    if profile.seasonal_analysis.dominant_season:
        print(f"  Peak Season: {profile.seasonal_analysis.dominant_season.value}")

    print(f"\n💰 Plan Cost Estimates:")
    for plan in plans:
        # Base cost calculation
        estimated_cost = profile.projection.projected_annual_kwh * plan.rate_per_kwh

        # Adjust for seasonal plans and seasonal users
        bonus = 1.0
        if plan.has_seasonal_rates and profile.profile_type == UserProfileType.SEASONAL:
            if profile.seasonal_analysis.dominant_season == SeasonType.SUMMER:
                bonus = 0.95  # 5% discount for summer seasonal users
                estimated_cost *= bonus

        # Add uncertainty buffer for low confidence
        if profile.overall_confidence < 0.7:
            estimated_cost *= 1.1  # 10% buffer

        print(f"\n  {plan.name}:")
        print(f"    Rate: ${plan.rate_per_kwh:.3f}/kWh")
        print(f"    Estimated Annual Cost: ${estimated_cost:.2f}")
        if bonus < 1.0:
            print(f"    Seasonal Match Bonus: {(1-bonus)*100:.0f}% discount applied")
        print(f"    Confidence: {profile.overall_confidence:.0%}")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("USAGE PATTERN ANALYSIS - QUICK START EXAMPLES")
    print("Story 1.4 - For Story 2.1 Integration")
    print("=" * 70)

    try:
        example_1_baseline_user()
        example_2_seasonal_user()
        example_3_new_customer()
        example_4_integration_with_scoring()

        print("\n\n" + "=" * 70)
        print("✅ All examples completed successfully!")
        print("=" * 70)
        print("\nNext Steps for Story 2.1 Integration:")
        print("1. Review /docs/contracts/story-1.4-contract.md")
        print("2. Import UsageAnalysisService in your scoring code")
        print("3. Use mock functions from contract for testing")
        print("4. Integrate with plan catalog for cost calculations")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
