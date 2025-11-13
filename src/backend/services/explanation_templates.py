"""
Template-based explanation generation.

This module provides fallback explanations when Claude API is unavailable.
Uses rule-based logic to generate personalized explanations.
"""

from decimal import Decimal
from typing import List, Optional, Dict, Any

from schemas.explanation_schemas import (
    RankedPlan,
    UserPreferences,
    CurrentPlan,
    PersonaType,
)


class TemplateExplanationGenerator:
    """Generates explanations using rule-based templates."""

    def generate_explanation(
        self,
        plan: RankedPlan,
        user_profile: Dict[str, Any],
        preferences: UserPreferences,
        current_plan: Optional[CurrentPlan] = None,
    ) -> str:
        """
        Generate a template-based explanation.

        Args:
            plan: The plan to explain
            user_profile: User's usage profile
            preferences: User's stated preferences
            current_plan: Current plan for comparison

        Returns:
            Explanation text (2-3 sentences)
        """
        persona = preferences.get_persona_type()
        dominant_pref = preferences.get_dominant_preference()

        # Build explanation components
        intro = self._get_intro(plan, persona, dominant_pref)
        benefits = self._get_benefits(plan, preferences, user_profile, current_plan)
        tradeoff = self._get_tradeoff(plan, current_plan)

        # Combine into 2-3 sentences
        if tradeoff:
            explanation = f"{intro} {benefits} {tradeoff}"
        else:
            explanation = f"{intro} {benefits}"

        return explanation

    def _get_intro(self, plan: RankedPlan, persona: str, dominant_pref: str) -> str:
        """Get personalized intro based on persona."""
        intros = {
            PersonaType.BUDGET_CONSCIOUS: (
                f"This plan offers the best value for your money."
            ),
            PersonaType.ECO_CONSCIOUS: (
                f"This plan aligns with your environmental priorities with "
                f"{plan.renewable_percentage:.0f}% renewable energy."
            ),
            PersonaType.FLEXIBILITY_FOCUSED: (
                f"This plan gives you the flexibility you're looking for."
            ),
            PersonaType.BALANCED: (
                f"This plan provides the best overall match for your needs."
            ),
        }
        return intros.get(persona, intros[PersonaType.BALANCED])

    def _get_benefits(
        self,
        plan: RankedPlan,
        preferences: UserPreferences,
        user_profile: Dict[str, Any],
        current_plan: Optional[CurrentPlan],
    ) -> str:
        """Get specific benefits based on preferences."""
        benefits = []

        # Cost benefit
        if preferences.cost_priority > 30:
            projected_savings = getattr(plan, 'projected_annual_savings', None)
            if projected_savings and projected_savings > 0:
                annual_cost = getattr(current_plan, 'annual_cost', None) if current_plan else None
                savings_pct = (
                    projected_savings / annual_cost * 100
                    if current_plan and annual_cost
                    else 0
                )
                if savings_pct > 10:
                    benefits.append(
                        f"You'll save ${projected_savings:.0f} per year "
                        f"({savings_pct:.0f}% less than your current plan)"
                    )
                else:
                    benefits.append(
                        f"You'll save ${projected_savings:.0f} annually"
                    )
            else:
                avg_usage = user_profile.get("statistics", {}).get("mean_kwh", 1000)
                benefits.append(
                    f"Based on your average usage of {avg_usage:.0f} kWh per month, "
                    f"your annual cost would be ${plan.projected_annual_cost:.0f}"
                )

        # Renewable benefit
        if preferences.renewable_priority > 30 and plan.renewable_percentage > 0:
            if plan.renewable_percentage == 100:
                benefits.append("it's 100% renewable energy")
            elif plan.renewable_percentage >= 50:
                benefits.append(
                    f"it includes {plan.renewable_percentage:.0f}% renewable energy"
                )

        # Flexibility benefit
        if preferences.flexibility_priority > 30:
            if plan.contract_length_months == 0:
                benefits.append("with no long-term contract required")
            elif plan.early_termination_fee == 0:
                benefits.append(
                    f"with a {plan.contract_length_months}-month agreement "
                    f"and no cancellation fee"
                )

        # Rating benefit
        if preferences.rating_priority > 30 and plan.rating_score > 80:
            benefits.append(f"{plan.supplier_name} has excellent customer ratings")

        # Plan type benefit
        if plan.plan_type == "fixed":
            benefits.append("with a stable, fixed rate for predictable billing")

        # Combine benefits
        if len(benefits) == 0:
            return f"It meets your key priorities with a projected annual cost of ${plan.projected_annual_cost:.0f}."
        elif len(benefits) == 1:
            return benefits[0] + "."
        else:
            return benefits[0] + ", and " + benefits[1] + "."

    def _get_tradeoff(
        self,
        plan: RankedPlan,
        current_plan: Optional[CurrentPlan],
    ) -> str:
        """Get trade-off explanation if significant."""
        tradeoffs = []

        # High ETF
        if plan.early_termination_fee > 100:
            if plan.break_even_months:
                tradeoffs.append(
                    f"Note that there's a ${plan.early_termination_fee:.0f} "
                    f"early termination fee, but you'll break even in "
                    f"{plan.break_even_months} months"
                )
            else:
                tradeoffs.append(
                    f"Keep in mind there's a ${plan.early_termination_fee:.0f} "
                    f"cancellation fee if you end the contract early"
                )

        # Contract commitment
        elif plan.contract_length_months >= 12 and plan.early_termination_fee > 0:
            tradeoffs.append(
                f"This requires a {plan.contract_length_months}-month commitment"
            )

        # Variable rate
        elif plan.plan_type == "variable":
            tradeoffs.append(
                "Keep in mind that the rate can change month-to-month based on market conditions"
            )

        # Low savings
        projected_savings = getattr(plan, 'projected_annual_savings', None)
        annual_cost = getattr(current_plan, 'annual_cost', None) if current_plan else None
        if (
            projected_savings
            and current_plan
            and annual_cost
        ):
            savings_pct = projected_savings / annual_cost * 100
            if 0 < savings_pct < 5:
                tradeoffs.append(
                    "The savings are modest, so switching may not be worth the effort"
                )

        # Return first tradeoff or empty string
        return tradeoffs[0] + "." if tradeoffs else ""

    def identify_key_differentiators(
        self,
        plan: RankedPlan,
        all_plans: Optional[List[RankedPlan]] = None,
    ) -> List[str]:
        """
        Identify what makes this plan stand out.

        Args:
            plan: The plan to analyze
            all_plans: All plans for comparison (optional)

        Returns:
            List of key differentiators
        """
        differentiators = []

        # Check if this plan is best in specific categories
        if all_plans:
            # Lowest cost
            if plan.cost_score >= max(p.cost_score for p in all_plans) - 5:
                differentiators.append("Lowest cost option")

            # Highest renewable
            if plan.renewable_percentage >= max(
                p.renewable_percentage for p in all_plans
            ) - 10:
                differentiators.append(
                    f"{plan.renewable_percentage:.0f}% renewable energy"
                )

            # Most flexible
            if plan.contract_length_months == 0:
                differentiators.append("No contract commitment")

            # Best rated
            if plan.rating_score >= max(p.rating_score for p in all_plans) - 5:
                differentiators.append("Top-rated supplier")
        else:
            # Standalone differentiators
            if plan.renewable_percentage >= 90:
                differentiators.append("Nearly 100% renewable energy")
            elif plan.renewable_percentage >= 50:
                differentiators.append(
                    f"{plan.renewable_percentage:.0f}% renewable energy"
                )

            if plan.contract_length_months == 0:
                differentiators.append("Month-to-month flexibility")

            if plan.plan_type == "fixed":
                differentiators.append("Fixed rate for price stability")

            if plan.early_termination_fee == 0:
                differentiators.append("No cancellation fees")

        return differentiators[:3]  # Return top 3

    def identify_trade_offs(
        self,
        plan: RankedPlan,
        current_plan: Optional[CurrentPlan] = None,
    ) -> List[str]:
        """
        Identify important trade-offs for this plan.

        Args:
            plan: The plan to analyze
            current_plan: Current plan for comparison

        Returns:
            List of trade-offs
        """
        trade_offs = []

        # Early termination fee
        if plan.early_termination_fee > 50:
            trade_offs.append(
                f"Early termination fee of ${plan.early_termination_fee:.0f}"
            )

        # Contract commitment
        if plan.contract_length_months >= 12:
            trade_offs.append(
                f"{plan.contract_length_months}-month contract commitment"
            )

        # Variable rate risk
        if plan.plan_type == "variable":
            trade_offs.append("Rate can change based on market conditions")

        # Cost vs renewable trade-off
        projected_savings = getattr(plan, 'projected_annual_savings', None)
        if current_plan and projected_savings:
            if projected_savings < 0:
                cost_increase = abs(projected_savings)
                if plan.renewable_percentage > 50:
                    trade_offs.append(
                        f"Costs ${cost_increase:.0f} more per year for renewable energy"
                    )

        # Monthly fees
        if plan.monthly_fee and plan.monthly_fee > 5:
            trade_offs.append(f"${plan.monthly_fee:.0f} monthly service fee")

        return trade_offs[:3]  # Return top 3


def get_context_aware_message(
    plan: RankedPlan,
    current_plan: Optional[CurrentPlan] = None,
    stay_with_current: bool = False,
) -> str:
    """
    Generate context-aware messaging for special situations.

    Args:
        plan: The recommended plan
        current_plan: Current plan
        stay_with_current: Whether we recommend staying

    Returns:
        Context-aware message
    """
    if stay_with_current:
        return (
            "Based on your usage and preferences, staying with your current plan "
            "is the best option. The potential savings from switching are too small "
            "to justify the effort and any switching costs."
        )

    # High ETF warning
    if plan.early_termination_fee > 150:
        if plan.break_even_months:
            return (
                f"This plan has a ${plan.early_termination_fee:.0f} early termination fee, "
                f"but you'll break even in {plan.break_even_months} months. "
                f"Consider waiting until your current contract expires if it ends soon."
            )
        else:
            return (
                f"Important: This plan has a ${plan.early_termination_fee:.0f} early "
                f"termination fee. Make sure you're comfortable with the commitment."
            )

    # Variable rate warning
    if plan.plan_type == "variable":
        # Get rate range if available
        rate_info = plan.rate_structure.get("base_rate", "")
        return (
            "This is a variable rate plan, which means your rate can change monthly. "
            "While it starts competitive, your costs could increase if market rates rise. "
            "Monitor your bills regularly."
        )

    # Low savings warning
    projected_savings = getattr(plan, 'projected_annual_savings', None)
    annual_cost = getattr(current_plan, 'annual_cost', None) if current_plan else None
    if projected_savings and current_plan and annual_cost:
        savings_pct = projected_savings / annual_cost * 100
        if 0 < savings_pct < 5:
            return (
                f"While this plan saves you ${projected_savings:.0f} per year, "
                f"the savings are modest ({savings_pct:.1f}%). Consider whether switching "
                f"is worth the administrative effort."
            )

    return ""
