"""
Tests for template-based explanation generation.

Covers TemplateExplanationGenerator methods and get_context_aware_message.
"""

from decimal import Decimal
from typing import Any
from uuid import uuid4

import pytest

from schemas.explanation_schemas import (
    CurrentPlan,
    PersonaType,
    RankedPlan,
    UserPreferences,
)
from services.explanation_templates import (
    TemplateExplanationGenerator,
    get_context_aware_message,
)

# ========== Fixtures ==========


@pytest.fixture
def sample_plan() -> RankedPlan:
    """Reusable sample RankedPlan with reasonable defaults."""
    return RankedPlan(
        plan_id=uuid4(),
        rank=1,
        plan_name="Sample Plan",
        supplier_name="Sample Energy Co",
        plan_type="fixed",
        composite_score=Decimal("85.0"),
        cost_score=Decimal("80.0"),
        flexibility_score=Decimal("70.0"),
        renewable_score=Decimal("60.0"),
        rating_score=Decimal("75.0"),
        projected_annual_cost=Decimal("1100.00"),
        projected_annual_savings=Decimal("200.00"),
        break_even_months=5,
        contract_length_months=12,
        early_termination_fee=Decimal("150.00"),
        renewable_percentage=Decimal("50.0"),
        monthly_fee=Decimal("0.00"),
        rate_structure={"type": "fixed", "rate_per_kwh": 9.0},
        average_rate=Decimal("9.0"),
        risk_flags=None,
    )


@pytest.fixture
def current_plan() -> CurrentPlan:
    """Current plan for comparison."""
    return CurrentPlan(
        plan_name="Old Plan",
        supplier_name="Old Supplier",
        annual_cost=Decimal("1300.00"),
        early_termination_fee=Decimal("100.00"),
    )


@pytest.fixture
def user_profile() -> dict[str, Any]:
    """Mock user profile with usage statistics."""
    return {
        "profile_type": "seasonal",
        "statistics": {
            "mean_kwh": 1000.0,
            "total_annual_kwh": 12000.0,
        },
    }


@pytest.fixture
def budget_preferences() -> UserPreferences:
    """Budget-conscious preferences (cost_priority > 50)."""
    return UserPreferences(
        cost_priority=60,
        flexibility_priority=15,
        renewable_priority=15,
        rating_priority=10,
    )


@pytest.fixture
def eco_preferences() -> UserPreferences:
    """Eco-conscious preferences (renewable_priority > 50)."""
    return UserPreferences(
        cost_priority=10,
        flexibility_priority=10,
        renewable_priority=70,
        rating_priority=10,
    )


@pytest.fixture
def flexibility_preferences() -> UserPreferences:
    """Flexibility-focused preferences (flexibility_priority > 50)."""
    return UserPreferences(
        cost_priority=10,
        flexibility_priority=70,
        renewable_priority=10,
        rating_priority=10,
    )


@pytest.fixture
def balanced_preferences() -> UserPreferences:
    """Balanced preferences (all <= 50)."""
    return UserPreferences(
        cost_priority=25,
        flexibility_priority=25,
        renewable_priority=25,
        rating_priority=25,
    )


@pytest.fixture
def generator() -> TemplateExplanationGenerator:
    """Shared generator instance."""
    return TemplateExplanationGenerator()


# ========== generate_explanation per persona ==========


class TestGenerateExplanation:
    """Tests for generate_explanation across all persona types."""

    def test_budget_conscious_persona(
        self, generator, sample_plan, user_profile, budget_preferences, current_plan
    ):
        """Budget-conscious persona returns a non-empty explanation."""
        result = generator.generate_explanation(
            plan=sample_plan,
            user_profile=user_profile,
            preferences=budget_preferences,
            current_plan=current_plan,
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_eco_conscious_persona(
        self, generator, sample_plan, user_profile, eco_preferences, current_plan
    ):
        """Eco-conscious persona returns a non-empty explanation."""
        result = generator.generate_explanation(
            plan=sample_plan,
            user_profile=user_profile,
            preferences=eco_preferences,
            current_plan=current_plan,
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_flexibility_focused_persona(
        self, generator, sample_plan, user_profile, flexibility_preferences
    ):
        """Flexibility-focused persona returns a non-empty explanation."""
        result = generator.generate_explanation(
            plan=sample_plan,
            user_profile=user_profile,
            preferences=flexibility_preferences,
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_balanced_persona(
        self, generator, sample_plan, user_profile, balanced_preferences
    ):
        """Balanced persona returns a non-empty explanation."""
        result = generator.generate_explanation(
            plan=sample_plan,
            user_profile=user_profile,
            preferences=balanced_preferences,
        )
        assert isinstance(result, str)
        assert len(result) > 0


# ========== _get_intro per persona ==========


class TestGetIntro:
    """Tests for _get_intro persona-specific intro sentences."""

    def test_budget_conscious_mentions_value(self, generator, sample_plan):
        """Budget-conscious intro mentions 'value'."""
        intro = generator._get_intro(
            sample_plan, PersonaType.BUDGET_CONSCIOUS, "cost"
        )
        assert "value" in intro.lower()

    def test_eco_conscious_mentions_renewable_percentage(self, generator, sample_plan):
        """Eco-conscious intro mentions the renewable percentage."""
        intro = generator._get_intro(
            sample_plan, PersonaType.ECO_CONSCIOUS, "renewable"
        )
        assert "50%" in intro or "renewable" in intro.lower()

    def test_flexibility_focused_mentions_flexibility(self, generator, sample_plan):
        """Flexibility-focused intro mentions 'flexibility'."""
        intro = generator._get_intro(
            sample_plan, PersonaType.FLEXIBILITY_FOCUSED, "flexibility"
        )
        assert "flexibility" in intro.lower()

    def test_balanced_mentions_overall(self, generator, sample_plan):
        """Balanced intro mentions 'overall'."""
        intro = generator._get_intro(
            sample_plan, PersonaType.BALANCED, "cost"
        )
        assert "overall" in intro.lower()


# ========== _get_benefits ==========


class TestGetBenefits:
    """Tests for _get_benefits under various preference / plan combinations."""

    def test_with_savings(
        self, generator, sample_plan, budget_preferences, user_profile, current_plan
    ):
        """When cost_priority > 30 and savings > 0, mentions dollar savings."""
        # sample_plan has projected_annual_savings=200, budget cost_priority=60
        benefits = generator._get_benefits(
            sample_plan, budget_preferences, user_profile, current_plan
        )
        assert "$200" in benefits

    def test_without_savings_shows_annual_cost(
        self, generator, sample_plan, budget_preferences, user_profile
    ):
        """Without savings, falls back to projected annual cost."""
        sample_plan.projected_annual_savings = None
        benefits = generator._get_benefits(
            sample_plan, budget_preferences, user_profile, None
        )
        assert "$1100" in benefits

    def test_renewable_benefit(self, generator, sample_plan, eco_preferences, user_profile):
        """When renewable_priority > 30 and renewable >= 50, mentions renewable."""
        # eco_preferences renewable_priority=70, sample_plan renewable_percentage=50
        benefits = generator._get_benefits(
            sample_plan, eco_preferences, user_profile, None
        )
        assert "renewable" in benefits.lower()

    def test_flexibility_month_to_month(
        self, generator, sample_plan, flexibility_preferences, user_profile
    ):
        """Month-to-month plans mention 'no long-term contract'."""
        sample_plan.contract_length_months = 0
        benefits = generator._get_benefits(
            sample_plan, flexibility_preferences, user_profile, None
        )
        assert "no long-term contract" in benefits.lower()


# ========== _get_tradeoff ==========


class TestGetTradeoff:
    """Tests for _get_tradeoff under various plan conditions."""

    def test_high_etf_mentions_fee_amount(self, generator, sample_plan):
        """ETF > 100 mentions the fee amount."""
        sample_plan.early_termination_fee = Decimal("200.00")
        sample_plan.break_even_months = None
        tradeoff = generator._get_tradeoff(sample_plan, None)
        assert "$200" in tradeoff

    def test_high_etf_with_break_even(self, generator, sample_plan):
        """When break_even_months is available, tradeoff includes it."""
        sample_plan.early_termination_fee = Decimal("200.00")
        sample_plan.break_even_months = 6
        tradeoff = generator._get_tradeoff(sample_plan, None)
        assert "6 months" in tradeoff

    def test_variable_rate_mentions_change(self, generator, sample_plan):
        """Variable rate plan mentions 'change month-to-month'."""
        sample_plan.plan_type = "variable"
        sample_plan.early_termination_fee = Decimal("0.00")
        sample_plan.contract_length_months = 0
        tradeoff = generator._get_tradeoff(sample_plan, None)
        assert "change month-to-month" in tradeoff.lower()

    def test_no_issues_returns_empty(self, generator, sample_plan):
        """Plan with no tradeoff conditions returns empty string."""
        sample_plan.early_termination_fee = Decimal("0.00")
        sample_plan.contract_length_months = 6
        sample_plan.plan_type = "fixed"
        sample_plan.projected_annual_savings = None
        tradeoff = generator._get_tradeoff(sample_plan, None)
        assert tradeoff == ""


# ========== identify_key_differentiators ==========


class TestIdentifyKeyDifferentiators:
    """Tests for identify_key_differentiators in standalone and comparative mode."""

    def test_standalone_high_renewable(self, generator, sample_plan):
        """Standalone: high renewable percentage is a differentiator."""
        sample_plan.renewable_percentage = Decimal("95.0")
        diffs = generator.identify_key_differentiators(sample_plan)
        assert any("renewable" in d.lower() for d in diffs)

    def test_standalone_month_to_month(self, generator, sample_plan):
        """Standalone: month-to-month shows flexibility differentiator."""
        sample_plan.contract_length_months = 0
        diffs = generator.identify_key_differentiators(sample_plan)
        assert any("month-to-month" in d.lower() for d in diffs)

    def test_standalone_fixed_rate(self, generator, sample_plan):
        """Standalone: fixed rate plan shows price stability differentiator."""
        sample_plan.plan_type = "fixed"
        diffs = generator.identify_key_differentiators(sample_plan)
        assert any("fixed rate" in d.lower() for d in diffs)

    def test_standalone_no_cancellation_fee(self, generator, sample_plan):
        """Standalone: zero ETF shows no cancellation fees differentiator."""
        sample_plan.early_termination_fee = Decimal("0.00")
        diffs = generator.identify_key_differentiators(sample_plan)
        assert any("no cancellation" in d.lower() for d in diffs)

    def test_standalone_max_three(self, generator, sample_plan):
        """Standalone differentiators are capped at 3."""
        sample_plan.renewable_percentage = Decimal("95.0")
        sample_plan.contract_length_months = 0
        sample_plan.plan_type = "fixed"
        sample_plan.early_termination_fee = Decimal("0.00")
        diffs = generator.identify_key_differentiators(sample_plan)
        assert len(diffs) <= 3

    def test_comparative_lowest_cost(self, generator, sample_plan):
        """Comparative: plan with highest cost_score is identified as lowest cost."""
        other = sample_plan.model_copy(update={
            "plan_id": uuid4(),
            "cost_score": Decimal("50.0"),
        })
        all_plans = [sample_plan, other]
        diffs = generator.identify_key_differentiators(sample_plan, all_plans)
        assert any("lowest cost" in d.lower() for d in diffs)

    def test_comparative_highest_renewable(self, generator, sample_plan):
        """Comparative: plan with highest renewable_percentage is flagged."""
        sample_plan.renewable_percentage = Decimal("80.0")
        other = sample_plan.model_copy(update={
            "plan_id": uuid4(),
            "renewable_percentage": Decimal("20.0"),
        })
        all_plans = [sample_plan, other]
        diffs = generator.identify_key_differentiators(sample_plan, all_plans)
        assert any("renewable" in d.lower() for d in diffs)

    def test_comparative_best_rated(self, generator, sample_plan):
        """Comparative: plan with highest rating_score is identified as top-rated."""
        sample_plan.rating_score = Decimal("95.0")
        other = sample_plan.model_copy(update={
            "plan_id": uuid4(),
            "rating_score": Decimal("60.0"),
        })
        all_plans = [sample_plan, other]
        diffs = generator.identify_key_differentiators(sample_plan, all_plans)
        assert any("top-rated" in d.lower() for d in diffs)


# ========== identify_trade_offs ==========


class TestIdentifyTradeOffs:
    """Tests for identify_trade_offs."""

    def test_high_etf(self, generator, sample_plan):
        """ETF > 50 is listed as a trade-off."""
        sample_plan.early_termination_fee = Decimal("100.00")
        trade_offs = generator.identify_trade_offs(sample_plan)
        assert any("termination" in t.lower() for t in trade_offs)

    def test_long_contract(self, generator, sample_plan):
        """Contract >= 12 months is listed as a trade-off."""
        sample_plan.contract_length_months = 24
        trade_offs = generator.identify_trade_offs(sample_plan)
        assert any("24-month" in t for t in trade_offs)

    def test_variable_rate(self, generator, sample_plan):
        """Variable plan type is listed as a trade-off."""
        sample_plan.plan_type = "variable"
        trade_offs = generator.identify_trade_offs(sample_plan)
        assert any("rate" in t.lower() and "change" in t.lower() for t in trade_offs)

    def test_monthly_fee(self, generator, sample_plan):
        """Monthly fee > $5 is listed as a trade-off."""
        sample_plan.monthly_fee = Decimal("10.00")
        trade_offs = generator.identify_trade_offs(sample_plan)
        assert any("monthly" in t.lower() and "$10" in t for t in trade_offs)

    def test_max_three(self, generator, sample_plan):
        """Trade-offs are capped at 3."""
        sample_plan.early_termination_fee = Decimal("100.00")
        sample_plan.contract_length_months = 24
        sample_plan.plan_type = "variable"
        sample_plan.monthly_fee = Decimal("10.00")
        trade_offs = generator.identify_trade_offs(sample_plan)
        assert len(trade_offs) <= 3


# ========== get_context_aware_message ==========


class TestGetContextAwareMessage:
    """Tests for the module-level get_context_aware_message function."""

    def test_stay_with_current(self, sample_plan, current_plan):
        """stay_with_current=True returns a stay message."""
        msg = get_context_aware_message(
            plan=sample_plan,
            current_plan=current_plan,
            stay_with_current=True,
        )
        assert "staying with your current plan" in msg.lower()

    def test_high_etf_warning(self, sample_plan):
        """ETF > 150 returns an ETF warning mentioning the fee."""
        sample_plan.early_termination_fee = Decimal("200.00")
        sample_plan.break_even_months = None
        msg = get_context_aware_message(plan=sample_plan)
        assert "$200" in msg
        assert "termination fee" in msg.lower()

    def test_high_etf_with_break_even(self, sample_plan):
        """ETF > 150 with break_even_months includes break-even info."""
        sample_plan.early_termination_fee = Decimal("200.00")
        sample_plan.break_even_months = 8
        msg = get_context_aware_message(plan=sample_plan)
        assert "8 months" in msg

    def test_variable_rate_warning(self, sample_plan):
        """Variable rate plan returns a variable rate warning."""
        sample_plan.plan_type = "variable"
        sample_plan.early_termination_fee = Decimal("0.00")
        sample_plan.rate_structure = {"type": "variable", "base_rate": 9.0}
        msg = get_context_aware_message(plan=sample_plan)
        assert "variable rate plan" in msg.lower()

    def test_low_savings_warning(self, sample_plan, current_plan):
        """Modest savings (0 < pct < 5) returns a low-savings warning."""
        # savings = 40 / 1300 ~ 3.1%, which is < 5%
        sample_plan.projected_annual_savings = Decimal("40.00")
        sample_plan.early_termination_fee = Decimal("0.00")
        sample_plan.plan_type = "fixed"
        msg = get_context_aware_message(
            plan=sample_plan,
            current_plan=current_plan,
        )
        assert "modest" in msg.lower() or "savings" in msg.lower()

    def test_no_special_context_returns_empty(self, sample_plan):
        """Plan with no special conditions returns empty string."""
        sample_plan.early_termination_fee = Decimal("0.00")
        sample_plan.plan_type = "fixed"
        sample_plan.projected_annual_savings = None
        msg = get_context_aware_message(plan=sample_plan)
        assert msg == ""
