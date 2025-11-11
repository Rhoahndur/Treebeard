"""
Tests for explanation generation service (Stories 2.6, 2.7, 2.8).
"""

import asyncio
import json
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any
from uuid import UUID, uuid4

import pytest
from unittest.mock import AsyncMock, Mock, patch

from src.backend.schemas.explanation_schemas import (
    RankedPlan,
    UserPreferences,
    CurrentPlan,
    PlanExplanation,
    PersonaType,
)
from src.backend.services.explanation_service import ClaudeExplanationService
from src.backend.services.explanation_templates import (
    TemplateExplanationGenerator,
    get_context_aware_message,
)


# ========== Fixtures ==========


@pytest.fixture
def mock_user_profile() -> Dict[str, Any]:
    """Create mock usage profile."""
    return {
        "profile_type": "seasonal",
        "statistics": {
            "mean_kwh": 1000.0,
            "total_annual_kwh": 12000.0,
        },
        "seasonal_analysis": {
            "has_seasonal_pattern": True,
            "dominant_season": "summer",
        },
    }


@pytest.fixture
def budget_preferences() -> UserPreferences:
    """Create budget-conscious user preferences."""
    return UserPreferences(
        cost_priority=60,
        flexibility_priority=20,
        renewable_priority=10,
        rating_priority=10,
    )


@pytest.fixture
def eco_preferences() -> UserPreferences:
    """Create eco-conscious user preferences."""
    return UserPreferences(
        cost_priority=10,
        flexibility_priority=10,
        renewable_priority=70,
        rating_priority=10,
    )


@pytest.fixture
def flexibility_preferences() -> UserPreferences:
    """Create flexibility-focused user preferences."""
    return UserPreferences(
        cost_priority=10,
        flexibility_priority=70,
        renewable_priority=10,
        rating_priority=10,
    )


@pytest.fixture
def balanced_preferences() -> UserPreferences:
    """Create balanced user preferences."""
    return UserPreferences(
        cost_priority=25,
        flexibility_priority=25,
        renewable_priority=25,
        rating_priority=25,
    )


@pytest.fixture
def current_plan() -> CurrentPlan:
    """Create current plan for comparison."""
    return CurrentPlan(
        plan_name="Old Plan",
        supplier_name="Old Supplier",
        annual_cost=Decimal("1200.00"),
        early_termination_fee=Decimal("100.00"),
    )


@pytest.fixture
def budget_plan() -> RankedPlan:
    """Create budget-friendly plan."""
    return RankedPlan(
        plan_id=uuid4(),
        rank=1,
        plan_name="Budget Saver",
        supplier_name="Affordable Energy Co",
        plan_type="fixed",
        composite_score=Decimal("92.5"),
        cost_score=Decimal("95.0"),
        flexibility_score=Decimal("60.0"),
        renewable_score=Decimal("50.0"),
        rating_score=Decimal("85.0"),
        projected_annual_cost=Decimal("900.00"),
        projected_annual_savings=Decimal("300.00"),
        break_even_months=4,
        contract_length_months=12,
        early_termination_fee=Decimal("100.00"),
        renewable_percentage=Decimal("25.0"),
        monthly_fee=Decimal("0.00"),
        rate_structure={"type": "fixed", "rate_per_kwh": 7.5},
        average_rate=Decimal("7.5"),
        risk_flags=None,
    )


@pytest.fixture
def eco_plan() -> RankedPlan:
    """Create eco-friendly plan."""
    return RankedPlan(
        plan_id=uuid4(),
        rank=1,
        plan_name="Green Energy 100",
        supplier_name="EcoEnergy Inc",
        plan_type="fixed",
        composite_score=Decimal("88.0"),
        cost_score=Decimal("70.0"),
        flexibility_score=Decimal("80.0"),
        renewable_score=Decimal("100.0"),
        rating_score=Decimal("90.0"),
        projected_annual_cost=Decimal("1250.00"),
        projected_annual_savings=Decimal("-50.00"),
        break_even_months=None,
        contract_length_months=12,
        early_termination_fee=Decimal("0.00"),
        renewable_percentage=Decimal("100.0"),
        monthly_fee=Decimal("0.00"),
        rate_structure={"type": "fixed", "rate_per_kwh": 10.4},
        average_rate=Decimal("10.4"),
        risk_flags=None,
    )


@pytest.fixture
def flexible_plan() -> RankedPlan:
    """Create flexible month-to-month plan."""
    return RankedPlan(
        plan_id=uuid4(),
        rank=1,
        plan_name="No Commitment Plus",
        supplier_name="FlexPower",
        plan_type="variable",
        composite_score=Decimal("85.0"),
        cost_score=Decimal("80.0"),
        flexibility_score=Decimal("100.0"),
        renewable_score=Decimal("40.0"),
        rating_score=Decimal("75.0"),
        projected_annual_cost=Decimal("1100.00"),
        projected_annual_savings=Decimal("100.00"),
        break_even_months=None,
        contract_length_months=0,
        early_termination_fee=Decimal("0.00"),
        renewable_percentage=Decimal("20.0"),
        monthly_fee=Decimal("5.00"),
        rate_structure={"type": "variable", "base_rate": 9.0},
        average_rate=Decimal("9.0"),
        risk_flags={"variable_rate": {"warning": "Rate may change monthly"}},
    )


@pytest.fixture
def mock_redis():
    """Create mock Redis client."""
    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.setex = AsyncMock()
    redis_mock.delete = AsyncMock()
    redis_mock.scan_iter = AsyncMock(return_value=iter([]))
    return redis_mock


# ========== Template Generator Tests ==========


class TestTemplateExplanationGenerator:
    """Tests for template-based explanation generation."""

    def test_budget_persona_explanation(
        self, budget_plan, mock_user_profile, budget_preferences, current_plan
    ):
        """Test explanation for budget-conscious user."""
        generator = TemplateExplanationGenerator()

        explanation = generator.generate_explanation(
            plan=budget_plan,
            user_profile=mock_user_profile,
            preferences=budget_preferences,
            current_plan=current_plan,
        )

        assert "save" in explanation.lower()
        assert "$300" in explanation
        assert len(explanation) > 50
        assert len(explanation.split(".")) >= 2  # At least 2 sentences

    def test_eco_persona_explanation(
        self, eco_plan, mock_user_profile, eco_preferences, current_plan
    ):
        """Test explanation for eco-conscious user."""
        generator = TemplateExplanationGenerator()

        explanation = generator.generate_explanation(
            plan=eco_plan,
            user_profile=mock_user_profile,
            preferences=eco_preferences,
            current_plan=current_plan,
        )

        assert "renewable" in explanation.lower() or "100%" in explanation
        assert len(explanation) > 50

    def test_flexibility_persona_explanation(
        self, flexible_plan, mock_user_profile, flexibility_preferences
    ):
        """Test explanation for flexibility-focused user."""
        generator = TemplateExplanationGenerator()

        explanation = generator.generate_explanation(
            plan=flexible_plan,
            user_profile=mock_user_profile,
            preferences=flexibility_preferences,
            current_plan=None,
        )

        assert "flexib" in explanation.lower() or "no contract" in explanation.lower()
        assert len(explanation) > 50

    def test_tradeoff_high_etf(self, budget_plan, mock_user_profile, budget_preferences):
        """Test trade-off explanation for high ETF."""
        # Modify plan to have high ETF
        budget_plan.early_termination_fee = Decimal("200.00")

        generator = TemplateExplanationGenerator()
        explanation = generator.generate_explanation(
            plan=budget_plan,
            user_profile=mock_user_profile,
            preferences=budget_preferences,
        )

        assert "termination" in explanation.lower() or "cancellation" in explanation.lower()
        assert "$200" in explanation or "200" in explanation

    def test_tradeoff_variable_rate(
        self, flexible_plan, mock_user_profile, flexibility_preferences
    ):
        """Test trade-off explanation for variable rate."""
        generator = TemplateExplanationGenerator()
        explanation = generator.generate_explanation(
            plan=flexible_plan,
            user_profile=mock_user_profile,
            preferences=flexibility_preferences,
        )

        assert "variable" in explanation.lower() or "change" in explanation.lower()

    def test_key_differentiators_identification(self, eco_plan):
        """Test identification of key differentiators."""
        generator = TemplateExplanationGenerator()

        differentiators = generator.identify_key_differentiators(eco_plan)

        assert len(differentiators) <= 3
        assert any("renewable" in d.lower() for d in differentiators)

    def test_key_differentiators_with_comparison(self, budget_plan, eco_plan, flexible_plan):
        """Test differentiators with plan comparison."""
        generator = TemplateExplanationGenerator()
        all_plans = [budget_plan, eco_plan, flexible_plan]

        differentiators = generator.identify_key_differentiators(budget_plan, all_plans)

        assert len(differentiators) <= 3
        # Budget plan should be identified as lowest cost
        assert any("cost" in d.lower() for d in differentiators)

    def test_trade_offs_identification(self, budget_plan, current_plan):
        """Test identification of trade-offs."""
        generator = TemplateExplanationGenerator()

        trade_offs = generator.identify_trade_offs(budget_plan, current_plan)

        assert len(trade_offs) <= 3
        # Should identify ETF and contract
        assert any("termination" in t.lower() for t in trade_offs)

    def test_context_aware_stay_message(self, budget_plan, current_plan):
        """Test context-aware message for staying with current plan."""
        message = get_context_aware_message(
            plan=budget_plan,
            current_plan=current_plan,
            stay_with_current=True,
        )

        assert "stay" in message.lower()
        assert "current plan" in message.lower()

    def test_context_aware_high_etf_warning(self, budget_plan):
        """Test context-aware message for high ETF."""
        budget_plan.early_termination_fee = Decimal("200.00")
        budget_plan.break_even_months = 6

        message = get_context_aware_message(
            plan=budget_plan,
            stay_with_current=False,
        )

        assert "termination fee" in message.lower() or "$200" in message
        assert "6 months" in message.lower() or "break even" in message.lower()

    def test_context_aware_variable_rate_warning(self, flexible_plan):
        """Test context-aware message for variable rate."""
        message = get_context_aware_message(
            plan=flexible_plan,
            stay_with_current=False,
        )

        assert "variable" in message.lower()
        assert "change" in message.lower()


# ========== Claude Service Tests ==========


class TestClaudeExplanationService:
    """Tests for Claude API-powered explanation service."""

    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test service initializes correctly."""
        service = ClaudeExplanationService(api_key="test_key")

        assert service.model == "claude-3-5-sonnet-20241022"
        assert service.max_tokens == 300
        assert service.temperature == 0.7
        assert service.timeout == 10.0
        assert service.max_retries == 3

    @pytest.mark.asyncio
    async def test_cache_key_generation(
        self, budget_plan, mock_user_profile, budget_preferences
    ):
        """Test cache key generation is consistent."""
        service = ClaudeExplanationService(api_key="test_key")

        key1 = service._generate_cache_key(budget_plan, mock_user_profile, budget_preferences)
        key2 = service._generate_cache_key(budget_plan, mock_user_profile, budget_preferences)

        assert key1 == key2
        assert key1.startswith("explanation:")

    @pytest.mark.asyncio
    async def test_fallback_to_template_on_api_failure(
        self, budget_plan, mock_user_profile, budget_preferences, current_plan
    ):
        """Test fallback to template when Claude API fails."""
        service = ClaudeExplanationService(api_key="invalid_key")

        # Mock Claude API to fail
        with patch.object(
            service.client.messages,
            "create",
            side_effect=Exception("API Error"),
        ):
            explanation = await service.generate_explanation(
                plan=budget_plan,
                user_profile=mock_user_profile,
                preferences=budget_preferences,
                current_plan=current_plan,
            )

        assert explanation.generated_via == "template"
        assert explanation.plan_id == budget_plan.plan_id
        assert len(explanation.explanation_text) > 50
        assert explanation.readability_score > 0
        assert service.metrics.fallback_used == 1

    @pytest.mark.asyncio
    async def test_readability_calculation_simple(self):
        """Test readability score calculation."""
        service = ClaudeExplanationService(api_key="test_key")

        # Short, simple sentence
        text1 = "You will save money. This plan is good. It costs less."
        score1 = service._calculate_readability(text1)

        # Longer, complex sentence
        text2 = (
            "Notwithstanding the aforementioned considerations, "
            "this particular energy procurement option demonstrates "
            "substantial economic advantages."
        )
        score2 = service._calculate_readability(text2)

        # Simple text should have higher score
        assert score1 > score2
        assert 0 <= score1 <= 100
        assert 0 <= score2 <= 100

    @pytest.mark.asyncio
    async def test_caching_workflow(
        self, budget_plan, mock_user_profile, budget_preferences, mock_redis
    ):
        """Test caching stores and retrieves explanations."""
        service = ClaudeExplanationService(
            api_key="test_key",
            redis_client=mock_redis,
        )

        # Mock Claude API
        with patch.object(
            service.client.messages,
            "create",
            side_effect=Exception("Force fallback"),
        ):
            # First call - should miss cache
            explanation1 = await service.generate_explanation(
                plan=budget_plan,
                user_profile=mock_user_profile,
                preferences=budget_preferences,
            )

        # Verify cache was called for storage
        assert mock_redis.setex.called
        cache_key = service._generate_cache_key(
            budget_plan, mock_user_profile, budget_preferences
        )
        assert mock_redis.setex.call_args[0][0] == cache_key

        # Simulate cache hit on second call
        cached_data = json.dumps(explanation1.model_dump(mode="json"))
        mock_redis.get = AsyncMock(return_value=cached_data)

        explanation2 = await service.generate_explanation(
            plan=budget_plan,
            user_profile=mock_user_profile,
            preferences=budget_preferences,
        )

        assert explanation2.plan_id == explanation1.plan_id
        assert service.metrics.cache_hits == 1

    @pytest.mark.asyncio
    async def test_cache_invalidation(self, mock_redis):
        """Test cache invalidation."""
        service = ClaudeExplanationService(
            api_key="test_key",
            redis_client=mock_redis,
        )

        # Mock scan_iter to return some keys
        mock_keys = [b"explanation:abc123", b"explanation:def456"]
        mock_redis.scan_iter = AsyncMock(return_value=iter(mock_keys))

        deleted = await service.invalidate_cache()

        assert deleted == len(mock_keys)
        assert mock_redis.delete.call_count == len(mock_keys)

    @pytest.mark.asyncio
    async def test_bulk_explanation_generation(
        self, budget_plan, eco_plan, flexible_plan, mock_user_profile, balanced_preferences
    ):
        """Test bulk explanation generation."""
        service = ClaudeExplanationService(api_key="test_key")
        plans = [budget_plan, eco_plan, flexible_plan]

        # Mock Claude API to fail (use templates)
        with patch.object(
            service.client.messages,
            "create",
            side_effect=Exception("Force fallback"),
        ):
            explanations = await service.bulk_generate_explanations(
                plans=plans,
                user_profile=mock_user_profile,
                preferences=balanced_preferences,
            )

        assert len(explanations) == 3
        assert all(isinstance(e, PlanExplanation) for e in explanations)
        assert explanations[0].plan_id == budget_plan.plan_id
        assert explanations[1].plan_id == eco_plan.plan_id
        assert explanations[2].plan_id == flexible_plan.plan_id

    @pytest.mark.asyncio
    async def test_metrics_tracking(
        self, budget_plan, mock_user_profile, budget_preferences
    ):
        """Test metrics are tracked correctly."""
        service = ClaudeExplanationService(api_key="test_key")

        # Mock Claude API to fail
        with patch.object(
            service.client.messages,
            "create",
            side_effect=Exception("Force fallback"),
        ):
            await service.generate_explanation(
                plan=budget_plan,
                user_profile=mock_user_profile,
                preferences=budget_preferences,
            )

        metrics = service.get_metrics()

        assert metrics.total_generated == 1
        assert metrics.fallback_used == 1
        assert metrics.cache_misses == 1
        assert metrics.avg_generation_time_ms > 0
        assert metrics.avg_readability_score > 0

    @pytest.mark.asyncio
    async def test_cache_hit_rate_calculation(self):
        """Test cache hit rate calculation."""
        metrics = ExplanationMetrics()
        metrics.cache_hits = 60
        metrics.cache_misses = 40

        assert metrics.cache_hit_rate == 60.0

    @pytest.mark.asyncio
    async def test_fallback_rate_calculation(self):
        """Test fallback rate calculation."""
        metrics = ExplanationMetrics()
        metrics.api_calls = 80
        metrics.fallback_used = 20

        assert metrics.fallback_rate == 20.0

    @pytest.mark.asyncio
    async def test_prompt_building(
        self, budget_plan, mock_user_profile, budget_preferences, current_plan
    ):
        """Test prompt building includes all necessary context."""
        service = ClaudeExplanationService(api_key="test_key")

        prompt = service._build_prompt(
            plan=budget_plan,
            user_profile=mock_user_profile,
            preferences=budget_preferences,
            current_plan=current_plan,
        )

        # Check key elements are in prompt
        assert "1000" in prompt  # avg_kwh
        assert "Budget Saver" in prompt  # plan name
        assert "seasonal" in prompt  # profile type
        assert "budget_conscious" in prompt  # persona
        assert "$300" in prompt  # savings
        assert "8th grade" in prompt  # readability requirement

    @pytest.mark.asyncio
    async def test_persona_detection_budget(self, budget_preferences):
        """Test persona detection for budget-conscious user."""
        persona = budget_preferences.get_persona_type()
        assert persona == PersonaType.BUDGET_CONSCIOUS

    @pytest.mark.asyncio
    async def test_persona_detection_eco(self, eco_preferences):
        """Test persona detection for eco-conscious user."""
        persona = eco_preferences.get_persona_type()
        assert persona == PersonaType.ECO_CONSCIOUS

    @pytest.mark.asyncio
    async def test_persona_detection_flexibility(self, flexibility_preferences):
        """Test persona detection for flexibility-focused user."""
        persona = flexibility_preferences.get_persona_type()
        assert persona == PersonaType.FLEXIBILITY_FOCUSED

    @pytest.mark.asyncio
    async def test_persona_detection_balanced(self, balanced_preferences):
        """Test persona detection for balanced user."""
        persona = balanced_preferences.get_persona_type()
        assert persona == PersonaType.BALANCED

    @pytest.mark.asyncio
    async def test_cache_warming(
        self, budget_plan, eco_plan, mock_user_profile, mock_redis
    ):
        """Test cache warming pre-generates explanations."""
        service = ClaudeExplanationService(
            api_key="test_key",
            redis_client=mock_redis,
        )

        plans = [budget_plan, eco_plan]
        personas = [PersonaType.BUDGET_CONSCIOUS, PersonaType.ECO_CONSCIOUS]

        # Mock Claude API to fail (use templates)
        with patch.object(
            service.client.messages,
            "create",
            side_effect=Exception("Force fallback"),
        ):
            generated = await service.warm_cache(
                plans=plans,
                personas=personas,
                mock_profile=mock_user_profile,
            )

        # Should generate: 2 plans × 2 personas = 4 explanations
        assert generated == 4
        assert mock_redis.setex.call_count >= 4


# ========== Integration Tests ==========


class TestExplanationIntegration:
    """Integration tests for the complete explanation workflow."""

    @pytest.mark.asyncio
    async def test_end_to_end_budget_recommendation(
        self, budget_plan, mock_user_profile, budget_preferences, current_plan
    ):
        """Test complete flow for budget-conscious recommendation."""
        service = ClaudeExplanationService(api_key="test_key")

        # Force template fallback
        with patch.object(
            service.client.messages,
            "create",
            side_effect=Exception("Force fallback"),
        ):
            explanation = await service.generate_explanation(
                plan=budget_plan,
                user_profile=mock_user_profile,
                preferences=budget_preferences,
                current_plan=current_plan,
            )

        # Verify explanation quality
        assert explanation.plan_id == budget_plan.plan_id
        assert explanation.persona_type == PersonaType.BUDGET_CONSCIOUS
        assert "save" in explanation.explanation_text.lower() or "$300" in explanation.explanation_text
        assert len(explanation.key_differentiators) > 0
        assert len(explanation.explanation_text) > 50
        assert explanation.readability_score >= 40  # Reasonable minimum

    @pytest.mark.asyncio
    async def test_end_to_end_eco_recommendation(
        self, eco_plan, mock_user_profile, eco_preferences, current_plan
    ):
        """Test complete flow for eco-conscious recommendation."""
        service = ClaudeExplanationService(api_key="test_key")

        # Force template fallback
        with patch.object(
            service.client.messages,
            "create",
            side_effect=Exception("Force fallback"),
        ):
            explanation = await service.generate_explanation(
                plan=eco_plan,
                user_profile=mock_user_profile,
                preferences=eco_preferences,
                current_plan=current_plan,
            )

        # Verify explanation emphasizes renewable energy
        assert explanation.persona_type == PersonaType.ECO_CONSCIOUS
        assert (
            "renewable" in explanation.explanation_text.lower()
            or "100%" in explanation.explanation_text
        )
        assert any("renewable" in d.lower() for d in explanation.key_differentiators)

    @pytest.mark.asyncio
    async def test_end_to_end_flexibility_recommendation(
        self, flexible_plan, mock_user_profile, flexibility_preferences
    ):
        """Test complete flow for flexibility-focused recommendation."""
        service = ClaudeExplanationService(api_key="test_key")

        # Force template fallback
        with patch.object(
            service.client.messages,
            "create",
            side_effect=Exception("Force fallback"),
        ):
            explanation = await service.generate_explanation(
                plan=flexible_plan,
                user_profile=mock_user_profile,
                preferences=flexibility_preferences,
            )

        # Verify explanation emphasizes flexibility
        assert explanation.persona_type == PersonaType.FLEXIBILITY_FOCUSED
        text_lower = explanation.explanation_text.lower()
        assert "flex" in text_lower or "no contract" in text_lower or "month-to-month" in text_lower
