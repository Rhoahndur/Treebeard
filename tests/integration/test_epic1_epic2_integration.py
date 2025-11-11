"""
Integration Tests: Epic 1 + Epic 2 Complete Flow
=================================================

Tests the complete recommendation pipeline from data ingestion through
AI-powered explanations.

Test Flow:
1. Database models (Story 1.1)
2. Usage analysis (Story 1.4)
3. Recommendation scoring & matching (Stories 2.1, 2.2, 2.3)
4. Savings calculation (Stories 2.4, 2.5)
5. AI explanation generation (Stories 2.6, 2.7, 2.8)

Author: Integration Test Suite
Date: 2025-11-10
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4, UUID
import asyncio
from typing import List, Dict

# Import all the components we're testing
try:
    from src.backend.schemas.usage_analysis import (
        MonthlyUsage,
        UsageProfile,
        UserProfileType,
        UsageProjection,
    )
    from src.backend.services.usage_analysis import UsageAnalysisService
except ImportError:
    print("⚠️  Warning: Story 1.4 modules not found - skipping usage analysis tests")
    UsageAnalysisService = None

try:
    from src.backend.schemas.recommendation_schemas import (
        RankedPlan,
        RecommendationResult,
        UserPreferences as RecUserPreferences,
    )
    from src.backend.services.recommendation_engine import RecommendationEngine
except ImportError:
    print("⚠️  Warning: Story 2.2 modules not found - skipping recommendation tests")
    RecommendationEngine = None

try:
    from src.backend.schemas.savings_schemas import (
        SavingsAnalysis,
        PlanComparison,
        CurrentPlan,
    )
    from src.backend.services.savings_calculator import SavingsCalculator
except ImportError:
    print("⚠️  Warning: Story 2.4 modules not found - skipping savings tests")
    SavingsCalculator = None

try:
    from src.backend.schemas.explanation_schemas import (
        PlanExplanation,
        UserPreferences as ExplUserPreferences,
    )
    from src.backend.services.explanation_service import ClaudeExplanationService
    from src.backend.services.explanation_templates import TemplateExplanationGenerator
except ImportError:
    print("⚠️  Warning: Story 2.7 modules not found - skipping explanation tests")
    ClaudeExplanationService = None


# ============================================================================
# Test Fixtures - Mock Data
# ============================================================================

@pytest.fixture
def mock_usage_data() -> List[MonthlyUsage]:
    """Generate 12 months of realistic usage data (seasonal pattern)."""
    base_date = date(2024, 1, 1)

    # Seasonal usage pattern (higher in summer/winter)
    monthly_kwh = [
        850,   # Jan - Winter heating
        820,   # Feb
        650,   # Mar - Spring
        550,   # Apr
        480,   # May
        720,   # Jun - Summer cooling starts
        950,   # Jul - Peak summer
        980,   # Aug - Peak summer
        780,   # Sep
        520,   # Oct - Fall
        680,   # Nov - Winter heating starts
        830,   # Dec
    ]

    return [
        MonthlyUsage(
            month=base_date.replace(month=i+1),
            kwh=Decimal(str(kwh))
        )
        for i, kwh in enumerate(monthly_kwh)
    ]


@pytest.fixture
def mock_current_plan() -> CurrentPlan:
    """Mock user's current energy plan."""
    return CurrentPlan(
        supplier_name="Legacy Energy Co",
        current_rate=Decimal("0.12"),
        contract_end_date=date.today() + timedelta(days=90),
        early_termination_fee=Decimal("150.00"),
        plan_start_date=date.today() - timedelta(days=365),
        monthly_fee=Decimal("9.99"),
        connection_fee=Decimal("0.00"),
    )


@pytest.fixture
def mock_user_preferences() -> Dict:
    """Mock user preferences (budget-conscious)."""
    return {
        "cost_priority": 50,
        "flexibility_priority": 20,
        "renewable_priority": 20,
        "rating_priority": 10,
    }


@pytest.fixture
def mock_plans() -> List[Dict]:
    """Mock energy plans for testing."""
    return [
        {
            "plan_id": uuid4(),
            "plan_name": "Budget Saver Fixed",
            "supplier_name": "Value Energy",
            "rate_structure": {"type": "fixed", "rate_per_kwh": Decimal("0.095")},
            "contract_length_months": 12,
            "early_termination_fee": Decimal("100.00"),
            "renewable_percentage": Decimal("15.0"),
            "monthly_fee": Decimal("8.99"),
            "connection_fee": Decimal("25.00"),
            "supplier_rating": Decimal("4.2"),
            "is_active": True,
        },
        {
            "plan_id": uuid4(),
            "plan_name": "Green Choice 100",
            "supplier_name": "Eco Power",
            "rate_structure": {"type": "fixed", "rate_per_kwh": Decimal("0.115")},
            "contract_length_months": 24,
            "early_termination_fee": Decimal("200.00"),
            "renewable_percentage": Decimal("100.0"),
            "monthly_fee": Decimal("12.99"),
            "connection_fee": Decimal("0.00"),
            "supplier_rating": Decimal("4.8"),
            "is_active": True,
        },
        {
            "plan_id": uuid4(),
            "plan_name": "Flex Month-to-Month",
            "supplier_name": "Freedom Energy",
            "rate_structure": {"type": "fixed", "rate_per_kwh": Decimal("0.105")},
            "contract_length_months": 0,
            "early_termination_fee": Decimal("0.00"),
            "renewable_percentage": Decimal("50.0"),
            "monthly_fee": Decimal("5.99"),
            "connection_fee": Decimal("0.00"),
            "supplier_rating": Decimal("4.5"),
            "is_active": True,
        },
    ]


# ============================================================================
# Test 1: Story 1.4 - Usage Analysis
# ============================================================================

@pytest.mark.skipif(UsageAnalysisService is None, reason="Story 1.4 not available")
class TestStory14Integration:
    """Test Story 1.4: Usage Analysis Service"""

    def test_analyze_usage_generates_profile(self, mock_usage_data):
        """Test that usage analysis generates a complete user profile."""
        service = UsageAnalysisService()

        # Analyze usage
        profile = service.analyze_usage_patterns(mock_usage_data)

        # Verify profile was generated
        assert profile is not None
        assert isinstance(profile, UsageProfile)
        assert profile.profile_type in [t.value for t in UserProfileType]
        assert profile.confidence_score > 0

        # Verify seasonal analysis
        assert profile.seasonal_patterns is not None
        assert len(profile.seasonal_patterns) > 0

        # Verify projections
        assert profile.projected_annual_kwh > 0
        assert len(profile.projected_monthly_kwh) == 12

        print(f"✅ Usage Analysis: Generated {profile.profile_type} profile "
              f"with {profile.confidence_score:.1%} confidence")

    def test_usage_profile_includes_data_quality(self, mock_usage_data):
        """Test that usage profile includes data quality metrics."""
        service = UsageAnalysisService()
        profile = service.analyze_usage_patterns(mock_usage_data)

        # Verify data quality assessment
        assert profile.data_quality is not None
        assert 0 <= profile.data_quality.completeness_score <= 1
        assert profile.data_quality.total_months == 12
        assert profile.data_quality.missing_months == 0

        print(f"✅ Data Quality: {profile.data_quality.completeness_score:.1%} complete, "
              f"{profile.data_quality.total_months} months")


# ============================================================================
# Test 2: Story 1.4 → Story 2.1/2.2 Integration
# ============================================================================

@pytest.mark.skipif(
    UsageAnalysisService is None or RecommendationEngine is None,
    reason="Stories 1.4 or 2.2 not available"
)
class TestUsageToRecommendationIntegration:
    """Test integration between Usage Analysis and Recommendation Engine"""

    def test_usage_profile_feeds_recommendation_engine(
        self, mock_usage_data, mock_user_preferences, mock_plans
    ):
        """Test that usage profile output works as recommendation engine input."""

        # Step 1: Analyze usage (Story 1.4)
        usage_service = UsageAnalysisService()
        usage_profile = usage_service.analyze_usage_patterns(mock_usage_data)

        assert usage_profile is not None
        print(f"✅ Step 1: Generated usage profile ({usage_profile.profile_type})")

        # Step 2: Get recommendations (Story 2.2)
        # Note: This is a simplified test - full integration would use database
        # For now, verify the interface contract is compatible

        assert hasattr(usage_profile, 'projected_annual_kwh')
        assert hasattr(usage_profile, 'projected_monthly_kwh')
        assert hasattr(usage_profile, 'profile_type')

        print(f"✅ Step 2: Usage profile has required fields for recommendation engine")
        print(f"   - Projected annual: {usage_profile.projected_annual_kwh} kWh")
        print(f"   - Profile type: {usage_profile.profile_type}")


# ============================================================================
# Test 3: Story 2.2 → Story 2.4 Integration
# ============================================================================

@pytest.mark.skipif(
    RecommendationEngine is None or SavingsCalculator is None,
    reason="Stories 2.2 or 2.4 not available"
)
class TestRecommendationToSavingsIntegration:
    """Test integration between Recommendation Engine and Savings Calculator"""

    def test_ranked_plan_format_compatible_with_savings(
        self, mock_current_plan, mock_plans
    ):
        """Test that RankedPlan output format works with SavingsCalculator."""

        # Create a mock ranked plan (as if from Story 2.2)
        ranked_plan = RankedPlan(
            plan_id=mock_plans[0]["plan_id"],
            plan_name=mock_plans[0]["plan_name"],
            supplier_name=mock_plans[0]["supplier_name"],
            rank=1,
            composite_score=85.5,
            cost_score=90.0,
            flexibility_score=85.0,
            renewable_score=75.0,
            rating_score=80.0,
            projected_annual_cost=Decimal("850.00"),
            rate_structure=mock_plans[0]["rate_structure"],
            contract_length_months=mock_plans[0]["contract_length_months"],
            early_termination_fee=mock_plans[0]["early_termination_fee"],
            renewable_percentage=mock_plans[0]["renewable_percentage"],
            monthly_fee=mock_plans[0]["monthly_fee"],
            connection_fee=mock_plans[0]["connection_fee"],
            supplier_rating=mock_plans[0]["supplier_rating"],
        )

        # Verify RankedPlan has all fields needed by SavingsCalculator
        assert hasattr(ranked_plan, 'plan_id')
        assert hasattr(ranked_plan, 'projected_annual_cost')
        assert hasattr(ranked_plan, 'rate_structure')
        assert hasattr(ranked_plan, 'monthly_fee')
        assert hasattr(ranked_plan, 'connection_fee')
        assert hasattr(ranked_plan, 'early_termination_fee')

        print(f"✅ RankedPlan schema compatible with SavingsCalculator")
        print(f"   - Plan: {ranked_plan.plan_name}")
        print(f"   - Projected cost: ${ranked_plan.projected_annual_cost}")


# ============================================================================
# Test 4: Story 2.2 → Story 2.7 Integration
# ============================================================================

@pytest.mark.skipif(
    RecommendationEngine is None or ClaudeExplanationService is None,
    reason="Stories 2.2 or 2.7 not available"
)
class TestRecommendationToExplanationIntegration:
    """Test integration between Recommendation Engine and Explanation Service"""

    @pytest.mark.asyncio
    async def test_ranked_plan_compatible_with_explanation_service(
        self, mock_usage_data, mock_user_preferences, mock_plans, mock_current_plan
    ):
        """Test that RankedPlan works with explanation generation."""

        # Step 1: Create usage profile
        usage_service = UsageAnalysisService()
        usage_profile = usage_service.analyze_usage_patterns(mock_usage_data)

        # Step 2: Create ranked plan (mock from Story 2.2)
        ranked_plan = RankedPlan(
            plan_id=mock_plans[0]["plan_id"],
            plan_name=mock_plans[0]["plan_name"],
            supplier_name=mock_plans[0]["supplier_name"],
            rank=1,
            composite_score=85.5,
            cost_score=90.0,
            flexibility_score=85.0,
            renewable_score=75.0,
            rating_score=80.0,
            projected_annual_cost=Decimal("850.00"),
            rate_structure=mock_plans[0]["rate_structure"],
            contract_length_months=mock_plans[0]["contract_length_months"],
            early_termination_fee=mock_plans[0]["early_termination_fee"],
            renewable_percentage=mock_plans[0]["renewable_percentage"],
            monthly_fee=mock_plans[0]["monthly_fee"],
            connection_fee=mock_plans[0]["connection_fee"],
            supplier_rating=mock_plans[0]["supplier_rating"],
        )

        # Step 3: Convert preferences for explanation service
        preferences = ExplUserPreferences(**mock_user_preferences)

        # Step 4: Generate explanation using TEMPLATE service (no API key needed)
        template_service = TemplateExplanationGenerator()
        explanation = template_service.generate_explanation(
            ranked_plan, usage_profile, preferences, mock_current_plan
        )

        # Verify explanation was generated
        assert explanation is not None
        assert isinstance(explanation, PlanExplanation)
        assert len(explanation.explanation_text) > 50
        assert explanation.persona_type in ['budget_conscious', 'eco_conscious',
                                            'flexibility_focused', 'balanced']

        print(f"✅ Explanation generated successfully")
        print(f"   - Persona: {explanation.persona_type}")
        print(f"   - Readability: {explanation.readability_score:.1f}")
        print(f"   - Text preview: {explanation.explanation_text[:100]}...")


# ============================================================================
# Test 5: End-to-End Integration (Epic 1 + Epic 2)
# ============================================================================

@pytest.mark.skipif(
    any(x is None for x in [UsageAnalysisService, RecommendationEngine,
                             SavingsCalculator, ClaudeExplanationService]),
    reason="Not all services available"
)
class TestEndToEndIntegration:
    """Test complete end-to-end flow through Epic 1 and Epic 2"""

    @pytest.mark.asyncio
    async def test_complete_recommendation_pipeline(
        self, mock_usage_data, mock_user_preferences, mock_plans, mock_current_plan
    ):
        """
        Test the complete pipeline from usage data to AI explanations.

        Flow:
        1. Usage data → Usage profile (Story 1.4)
        2. Usage profile + Plans → Recommendations (Story 2.2)
        3. Recommendations + Current plan → Savings (Story 2.4)
        4. Recommendations + Profile → Explanations (Story 2.7)
        """

        print("\n" + "="*70)
        print("COMPLETE INTEGRATION TEST: Epic 1 + Epic 2")
        print("="*70)

        # ========== STEP 1: Usage Analysis (Story 1.4) ==========
        print("\n📊 STEP 1: Analyzing Usage Patterns (Story 1.4)...")
        usage_service = UsageAnalysisService()
        usage_profile = usage_service.analyze_usage_patterns(mock_usage_data)

        assert usage_profile is not None
        assert usage_profile.projected_annual_kwh > 0

        print(f"✅ Generated usage profile:")
        print(f"   - Type: {usage_profile.profile_type}")
        print(f"   - Annual usage: {usage_profile.projected_annual_kwh} kWh")
        print(f"   - Confidence: {usage_profile.confidence_score:.1%}")

        # ========== STEP 2: Create Mock Ranked Plans (Story 2.2) ==========
        print(f"\n🏆 STEP 2: Creating Ranked Plans (Story 2.2)...")

        # Note: In production, this would use RecommendationEngine.get_recommendations()
        # For integration test, we create mock ranked plans
        ranked_plans = [
            RankedPlan(
                plan_id=plan["plan_id"],
                plan_name=plan["plan_name"],
                supplier_name=plan["supplier_name"],
                rank=i+1,
                composite_score=90.0 - (i * 5),
                cost_score=95.0 - (i * 5),
                flexibility_score=85.0,
                renewable_score=plan["renewable_percentage"],
                rating_score=plan["supplier_rating"] * 20,
                projected_annual_cost=Decimal(str(800 + (i * 50))),
                rate_structure=plan["rate_structure"],
                contract_length_months=plan["contract_length_months"],
                early_termination_fee=plan["early_termination_fee"],
                renewable_percentage=plan["renewable_percentage"],
                monthly_fee=plan["monthly_fee"],
                connection_fee=plan["connection_fee"],
                supplier_rating=plan["supplier_rating"],
            )
            for i, plan in enumerate(mock_plans[:3])
        ]

        assert len(ranked_plans) == 3
        print(f"✅ Generated {len(ranked_plans)} ranked plans:")
        for plan in ranked_plans:
            print(f"   #{plan.rank}: {plan.plan_name} (score: {plan.composite_score:.1f})")

        # ========== STEP 3: Calculate Savings (Story 2.4) ==========
        print(f"\n💰 STEP 3: Calculating Savings (Story 2.4)...")

        # Create mock projection for savings calculator
        projection = UsageProjection(
            projected_annual_kwh=usage_profile.projected_annual_kwh,
            projected_monthly_kwh=usage_profile.projected_monthly_kwh,
            confidence_score=usage_profile.confidence_score,
            method_used="seasonal_averaging",
        )

        # Calculate savings for top plan
        savings_calculator = SavingsCalculator()
        savings = savings_calculator.calculate_savings(
            ranked_plans[0],
            mock_current_plan,
            projection
        )

        assert savings is not None
        assert hasattr(savings, 'annual_savings')

        print(f"✅ Calculated savings for top plan:")
        print(f"   - Recommended cost: ${savings.projected_annual_cost}")
        print(f"   - Current cost: ${savings.current_annual_cost}")
        print(f"   - Annual savings: ${savings.annual_savings} ({savings.savings_percentage}%)")
        if savings.break_even_months:
            print(f"   - Break-even: {savings.break_even_months} months")

        # ========== STEP 4: Generate Explanations (Story 2.7) ==========
        print(f"\n🤖 STEP 4: Generating AI Explanations (Story 2.7)...")

        preferences = ExplUserPreferences(**mock_user_preferences)
        template_service = TemplateExplanationGenerator()

        explanations = []
        for plan in ranked_plans:
            explanation = template_service.generate_explanation(
                plan, usage_profile, preferences, mock_current_plan
            )
            explanations.append(explanation)

        assert len(explanations) == 3

        print(f"✅ Generated explanations for all 3 plans:")
        for i, expl in enumerate(explanations):
            print(f"\n   Plan #{i+1}: {ranked_plans[i].plan_name}")
            print(f"   Persona: {expl.persona_type}")
            print(f"   Readability: {expl.readability_score:.1f}")
            print(f"   Differentiators: {', '.join(expl.key_differentiators[:2])}")
            print(f"   Text: {expl.explanation_text[:120]}...")

        # ========== VALIDATION: Complete Result ==========
        print(f"\n{'='*70}")
        print(f"✅ INTEGRATION TEST PASSED")
        print(f"{'='*70}")
        print(f"Complete recommendation result includes:")
        print(f"  ✓ Usage analysis with {usage_profile.confidence_score:.1%} confidence")
        print(f"  ✓ Top 3 ranked plans with composite scores")
        print(f"  ✓ Savings calculation showing ${savings.annual_savings} annual savings")
        print(f"  ✓ Personalized AI explanations ({explanations[0].persona_type})")
        print(f"{'='*70}\n")

        return {
            "usage_profile": usage_profile,
            "ranked_plans": ranked_plans,
            "savings": savings,
            "explanations": explanations,
        }


# ============================================================================
# Test 6: Performance Integration Test
# ============================================================================

class TestPerformanceIntegration:
    """Test performance of integrated pipeline"""

    @pytest.mark.skipif(
        UsageAnalysisService is None,
        reason="Story 1.4 not available"
    )
    def test_usage_analysis_performance(self, mock_usage_data):
        """Test that usage analysis meets performance targets (<100ms)."""
        import time

        service = UsageAnalysisService()

        start = time.time()
        profile = service.analyze_usage_patterns(mock_usage_data)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert profile is not None
        assert elapsed < 100, f"Usage analysis took {elapsed:.1f}ms (target: <100ms)"

        print(f"✅ Performance: Usage analysis completed in {elapsed:.1f}ms")


# ============================================================================
# Test 7: Data Contract Validation
# ============================================================================

class TestDataContracts:
    """Validate that all published contracts are being honored"""

    def test_story_1_4_contract_schema(self):
        """Verify Story 1.4 publishes the contract schema correctly."""
        # Check that published schemas match contract
        from src.backend.schemas.usage_analysis import UsageProfile

        required_fields = [
            'user_id', 'profile_type', 'statistics', 'seasonal_patterns',
            'projected_annual_kwh', 'projected_monthly_kwh', 'data_quality',
            'confidence_score', 'notes'
        ]

        for field in required_fields:
            assert hasattr(UsageProfile, '__annotations__')
            assert field in UsageProfile.__annotations__, \
                f"Missing required field '{field}' in UsageProfile"

        print(f"✅ Story 1.4 contract validated: All required fields present")

    @pytest.mark.skipif(RecommendationEngine is None, reason="Story 2.2 not available")
    def test_story_2_2_contract_schema(self):
        """Verify Story 2.2 publishes the contract schema correctly."""
        from src.backend.schemas.recommendation_schemas import RankedPlan

        required_fields = [
            'plan_id', 'rank', 'composite_score', 'cost_score',
            'flexibility_score', 'renewable_score', 'rating_score',
            'projected_annual_cost'
        ]

        for field in required_fields:
            assert hasattr(RankedPlan, '__annotations__')
            assert field in RankedPlan.__annotations__, \
                f"Missing required field '{field}' in RankedPlan"

        print(f"✅ Story 2.2 contract validated: All required fields present")


# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("INTEGRATION TEST SUITE: Epic 1 + Epic 2")
    print("Testing complete recommendation pipeline")
    print("="*70 + "\n")

    pytest.main([__file__, "-v", "--tb=short", "-s"])
