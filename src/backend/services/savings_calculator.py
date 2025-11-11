"""
Savings Calculator Service - Stories 2.4 & 2.5

Implements:
- Annual savings calculation
- Total Cost of Ownership (TCO)
- Break-even analysis
- Variable rate uncertainty handling
- Multi-plan comparison

Author: Backend Dev #4
Dependencies: Story 1.4 (Usage Projection), Story 2.2 (Plan Matching - via mock)
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID, uuid4

from ..schemas.plan import PlanCatalogResponse
from ..schemas.savings_schemas import (
    ComparisonPlan,
    CostRange,
    MonthlyCost,
    MultiYearProjection,
    PlanComparison,
    RankedPlan,
    RecommendationResult,
    SavingsAnalysis,
    TradeOffNote,
)
from ..schemas.user import CurrentPlanResponse
from ..schemas.usage_analysis import UsageProjection


class SavingsCalculatorService:
    """
    Service for calculating savings, TCO, and plan comparisons.

    Stories 2.4 & 2.5 implementation.
    """

    def __init__(self):
        """Initialize savings calculator service."""
        self.default_variable_rate_volatility = Decimal("0.10")  # ±10% default

    # ===== STORY 2.4: SAVINGS CALCULATOR =====

    def calculate_annual_savings(
        self,
        current_plan: CurrentPlanResponse,
        recommended_plan: PlanCatalogResponse,
        usage_projection: UsageProjection,
        user_id: UUID,
    ) -> SavingsAnalysis:
        """
        Calculate detailed annual savings analysis.

        Story 2.4 - Primary function for savings calculation.

        Args:
            current_plan: User's current energy plan
            recommended_plan: Recommended plan from catalog
            usage_projection: 12-month usage projection (from Story 1.4)
            user_id: User ID

        Returns:
            SavingsAnalysis with complete cost breakdown and savings
        """
        # Calculate monthly breakdown for both plans
        monthly_breakdown_new = self._calculate_monthly_breakdown(
            plan=recommended_plan,
            usage_projection=usage_projection,
        )

        monthly_breakdown_current = self._calculate_monthly_breakdown_current_plan(
            current_plan=current_plan,
            usage_projection=usage_projection,
        )

        # Calculate annual totals
        projected_annual_cost = sum(month.total_cost for month in monthly_breakdown_new)
        current_annual_cost = sum(month.total_cost for month in monthly_breakdown_current)

        annual_savings = current_annual_cost - projected_annual_cost
        savings_percentage = (
            (annual_savings / current_annual_cost * Decimal("100"))
            if current_annual_cost > 0
            else Decimal("0")
        )

        # Calculate Total Cost of Ownership
        contract_length = max(recommended_plan.contract_length_months, 12)
        tco, tco_current = self._calculate_tco(
            recommended_plan=recommended_plan,
            current_plan=current_plan,
            monthly_breakdown_new=monthly_breakdown_new,
            monthly_breakdown_current=monthly_breakdown_current,
            contract_length_months=contract_length,
        )

        # Break-even analysis
        switching_cost = current_plan.early_termination_fee
        break_even_months = self._calculate_break_even(
            annual_savings=annual_savings,
            switching_cost=switching_cost,
        )

        # Cumulative savings after 12 months
        cumulative_savings_12_months = annual_savings - switching_cost

        # Variable rate uncertainty
        is_variable_rate = recommended_plan.plan_type in ["variable", "indexed"]
        uncertainty_range = None
        if is_variable_rate:
            uncertainty_range = self._calculate_uncertainty_range(
                projected_annual_cost=projected_annual_cost,
                plan_type=recommended_plan.plan_type,
            )

        # Fees breakdown
        total_upfront_fees = recommended_plan.connection_fee or Decimal("0.00")
        total_monthly_fees = (
            (recommended_plan.monthly_fee or Decimal("0.00")) * Decimal(str(contract_length))
        )
        total_energy_cost = projected_annual_cost - total_upfront_fees - (
            recommended_plan.monthly_fee or Decimal("0.00")
        ) * Decimal("12")

        # Generate assumptions and warnings
        assumptions = self._generate_assumptions(
            usage_projection=usage_projection,
            recommended_plan=recommended_plan,
        )
        warnings = self._generate_warnings(
            savings_percentage=savings_percentage,
            switching_cost=switching_cost,
            is_variable_rate=is_variable_rate,
            usage_projection=usage_projection,
        )

        return SavingsAnalysis(
            plan_id=recommended_plan.id,
            user_id=user_id,
            projected_annual_cost=projected_annual_cost,
            current_annual_cost=current_annual_cost,
            annual_savings=annual_savings,
            savings_percentage=savings_percentage,
            monthly_breakdown=monthly_breakdown_new,
            total_cost_of_ownership=tco,
            tco_current_plan=tco_current,
            contract_length_months=contract_length,
            break_even_months=break_even_months,
            switching_cost=switching_cost,
            cumulative_savings_12_months=cumulative_savings_12_months,
            uncertainty_range=uncertainty_range,
            is_variable_rate=is_variable_rate,
            total_upfront_fees=total_upfront_fees,
            total_monthly_fees=total_monthly_fees,
            total_energy_cost=total_energy_cost,
            analysis_date=datetime.now(),
            assumptions=assumptions,
            warnings=warnings,
        )

    def _calculate_monthly_breakdown(
        self,
        plan: PlanCatalogResponse,
        usage_projection: UsageProjection,
    ) -> list[MonthlyCost]:
        """
        Calculate month-by-month costs for a plan.

        Args:
            plan: Energy plan from catalog
            usage_projection: 12-month usage projection

        Returns:
            List of 12 MonthlyCost objects
        """
        monthly_costs = []
        current_date = datetime.now()

        for month_idx, projected_kwh in enumerate(usage_projection.projected_monthly_kwh):
            month_num = (current_date.month + month_idx - 1) % 12 + 1
            year = current_date.year + (current_date.month + month_idx - 1) // 12

            # Calculate energy cost based on rate structure
            energy_cost = self._calculate_energy_cost_for_month(
                kwh=projected_kwh,
                rate_structure=plan.rate_structure,
                plan_type=plan.plan_type,
            )

            monthly_fee = plan.monthly_fee or Decimal("0.00")

            # Connection fee only in first month
            other_fees = plan.connection_fee or Decimal("0.00") if month_idx == 0 else Decimal("0.00")

            total_cost = energy_cost + monthly_fee + other_fees

            monthly_costs.append(
                MonthlyCost(
                    month=month_num,
                    year=year,
                    projected_kwh=Decimal(str(projected_kwh)),
                    energy_cost=energy_cost,
                    monthly_fee=monthly_fee,
                    other_fees=other_fees,
                    total_cost=total_cost,
                )
            )

        return monthly_costs

    def _calculate_monthly_breakdown_current_plan(
        self,
        current_plan: CurrentPlanResponse,
        usage_projection: UsageProjection,
    ) -> list[MonthlyCost]:
        """Calculate monthly costs for user's current plan."""
        monthly_costs = []
        current_date = datetime.now()

        for month_idx, projected_kwh in enumerate(usage_projection.projected_monthly_kwh):
            month_num = (current_date.month + month_idx - 1) % 12 + 1
            year = current_date.year + (current_date.month + month_idx - 1) // 12

            # Current plan uses simple rate * kwh
            energy_cost = Decimal(str(projected_kwh)) * current_plan.current_rate / Decimal("100")

            monthly_fee = current_plan.monthly_fee or Decimal("0.00")

            total_cost = energy_cost + monthly_fee

            monthly_costs.append(
                MonthlyCost(
                    month=month_num,
                    year=year,
                    projected_kwh=Decimal(str(projected_kwh)),
                    energy_cost=energy_cost,
                    monthly_fee=monthly_fee,
                    other_fees=Decimal("0.00"),
                    total_cost=total_cost,
                )
            )

        return monthly_costs

    def _calculate_energy_cost_for_month(
        self,
        kwh: float,
        rate_structure: dict[str, Any],
        plan_type: str,
    ) -> Decimal:
        """
        Calculate energy cost for a month based on rate structure.

        Handles different rate types: fixed, variable, tiered, time_of_use.
        """
        kwh_decimal = Decimal(str(kwh))

        if plan_type == "fixed":
            # Simple fixed rate
            rate_per_kwh = Decimal(str(rate_structure.get("rate_per_kwh", 0)))
            return kwh_decimal * rate_per_kwh / Decimal("100")

        elif plan_type == "variable":
            # Variable rate - use base rate (actual rate varies)
            base_rate = Decimal(str(rate_structure.get("base_rate", 0)))
            return kwh_decimal * base_rate / Decimal("100")

        elif plan_type == "tiered":
            # Tiered pricing
            return self._calculate_tiered_cost(kwh_decimal, rate_structure)

        elif plan_type == "time_of_use":
            # Time-of-use pricing (simplified: assume 50/50 peak/off-peak)
            peak_rate = Decimal(str(rate_structure.get("peak_rate", 0)))
            off_peak_rate = Decimal(str(rate_structure.get("off_peak_rate", 0)))
            avg_rate = (peak_rate + off_peak_rate) / Decimal("2")
            return kwh_decimal * avg_rate / Decimal("100")

        else:
            # Default: use rate_per_kwh if available
            rate = Decimal(str(rate_structure.get("rate_per_kwh", 0)))
            return kwh_decimal * rate / Decimal("100")

    def _calculate_tiered_cost(
        self,
        kwh: Decimal,
        rate_structure: dict[str, Any],
    ) -> Decimal:
        """Calculate cost for tiered pricing structure."""
        tiers = rate_structure.get("tiers", [])
        if not tiers:
            # Fallback to simple rate
            rate = Decimal(str(rate_structure.get("rate_per_kwh", 0)))
            return kwh * rate / Decimal("100")

        total_cost = Decimal("0")
        remaining_kwh = kwh

        for tier in tiers:
            tier_max = Decimal(str(tier.get("usage_max", float("inf"))))
            tier_rate = Decimal(str(tier.get("rate_per_kwh", 0)))

            kwh_in_tier = min(remaining_kwh, tier_max)
            total_cost += kwh_in_tier * tier_rate / Decimal("100")
            remaining_kwh -= kwh_in_tier

            if remaining_kwh <= 0:
                break

        return total_cost

    def _calculate_tco(
        self,
        recommended_plan: PlanCatalogResponse,
        current_plan: CurrentPlanResponse,
        monthly_breakdown_new: list[MonthlyCost],
        monthly_breakdown_current: list[MonthlyCost],
        contract_length_months: int,
    ) -> tuple[Decimal, Decimal]:
        """
        Calculate Total Cost of Ownership over contract length.

        Returns:
            (tco_new_plan, tco_current_plan)
        """
        # TCO for new plan
        months_in_year = 12
        years_needed = (contract_length_months + months_in_year - 1) // months_in_year

        # Sum first year actual costs
        annual_cost_new = sum(month.total_cost for month in monthly_breakdown_new)
        annual_cost_current = sum(month.total_cost for month in monthly_breakdown_current)

        # Project over contract length (assume similar annual costs)
        if contract_length_months <= months_in_year:
            tco_new = annual_cost_new * Decimal(str(contract_length_months)) / Decimal("12")
            tco_current = annual_cost_current * Decimal(str(contract_length_months)) / Decimal("12")
        else:
            tco_new = annual_cost_new * Decimal(str(years_needed))
            tco_current = annual_cost_current * Decimal(str(years_needed))

        # Add connection fee for new plan (one-time)
        tco_new += recommended_plan.connection_fee or Decimal("0.00")

        return tco_new, tco_current

    def _calculate_break_even(
        self,
        annual_savings: Decimal,
        switching_cost: Decimal,
    ) -> Optional[int]:
        """
        Calculate months until savings offset switching cost.

        Returns:
            Months to break-even, or None if no switching cost
        """
        if switching_cost <= 0:
            return 0  # No switching cost, immediate break-even

        if annual_savings <= 0:
            return None  # No savings, never breaks even

        monthly_savings = annual_savings / Decimal("12")
        months = switching_cost / monthly_savings

        return int(months.to_integral_value()) + 1  # Round up

    def _calculate_uncertainty_range(
        self,
        projected_annual_cost: Decimal,
        plan_type: str,
    ) -> CostRange:
        """
        Calculate cost range for variable rate plans.

        Uses historical volatility or default ±10%.
        """
        # Default volatility based on plan type
        if plan_type == "variable":
            volatility = self.default_variable_rate_volatility
        elif plan_type == "indexed":
            volatility = Decimal("0.15")  # Indexed plans may have higher volatility
        else:
            volatility = Decimal("0.05")

        low_estimate = projected_annual_cost * (Decimal("1") - volatility)
        high_estimate = projected_annual_cost * (Decimal("1") + volatility)

        return CostRange(
            low_estimate=low_estimate,
            high_estimate=high_estimate,
            expected_value=projected_annual_cost,
            confidence_level=Decimal("0.95"),
            volatility_note=f"Variable rate plans may vary by ±{volatility * 100}% based on market conditions",
        )

    def _generate_assumptions(
        self,
        usage_projection: UsageProjection,
        recommended_plan: PlanCatalogResponse,
    ) -> list[str]:
        """Generate list of key assumptions for the analysis."""
        assumptions = [
            f"Based on projected annual usage of {usage_projection.projected_annual_kwh:.0f} kWh",
            "Monthly usage follows seasonal patterns from historical data",
            f"Contract length: {recommended_plan.contract_length_months} months",
        ]

        if recommended_plan.plan_type in ["variable", "indexed"]:
            assumptions.append("Variable rate assumed stable at current market rate")

        if usage_projection.confidence_score < 0.7:
            assumptions.append("Usage projection has moderate confidence due to limited data")

        return assumptions

    def _generate_warnings(
        self,
        savings_percentage: Decimal,
        switching_cost: Decimal,
        is_variable_rate: bool,
        usage_projection: UsageProjection,
    ) -> list[str]:
        """Generate warnings about the savings analysis."""
        warnings = []

        # High ETF warning
        if switching_cost > Decimal("150"):
            warnings.append(
                f"High early termination fee (${switching_cost}). "
                "Consider waiting until current contract ends."
            )

        # Low savings warning
        if savings_percentage < Decimal("5") and savings_percentage >= 0:
            warnings.append(
                f"Marginal savings ({savings_percentage:.1f}%). "
                "Switching may not be worth the effort."
            )

        # Negative savings (more expensive)
        if savings_percentage < 0:
            warnings.append(
                "This plan is more expensive than your current plan. "
                "May offer other benefits (renewable energy, flexibility)."
            )

        # Variable rate risk
        if is_variable_rate:
            warnings.append(
                "Variable rate plan: actual costs may differ from projections. "
                "Consider rate volatility risk."
            )

        # Low confidence in usage projection
        if usage_projection.confidence_score < 0.6:
            warnings.append(
                "Low confidence in usage projection. Actual costs may vary significantly."
            )

        return warnings

    # ===== STORY 2.5: COMPARISON FEATURES =====

    def generate_comparison(
        self,
        plans: list[RankedPlan],
        current_plan: CurrentPlanResponse,
        usage_projection: UsageProjection,
        plan_catalog: dict[UUID, PlanCatalogResponse],
        user_id: UUID,
    ) -> PlanComparison:
        """
        Generate side-by-side comparison of multiple plans.

        Story 2.5 - Primary comparison function.

        Args:
            plans: Ranked plans from recommendation engine (Story 2.2)
            current_plan: User's current plan
            usage_projection: Usage projection (Story 1.4)
            plan_catalog: Dict mapping plan_id to full plan details
            user_id: User ID

        Returns:
            PlanComparison with side-by-side analysis
        """
        # Build ComparisonPlan objects for recommended plans
        comparison_plans = []
        for ranked_plan in plans:
            full_plan = plan_catalog.get(ranked_plan.plan_id)
            if not full_plan:
                continue  # Skip if plan not found

            comp_plan = self._build_comparison_plan(
                ranked_plan=ranked_plan,
                full_plan=full_plan,
                current_plan=current_plan,
                usage_projection=usage_projection,
            )
            comparison_plans.append(comp_plan)

        # Build ComparisonPlan for current plan
        current_comp_plan = self._build_current_plan_comparison(
            current_plan=current_plan,
            usage_projection=usage_projection,
        )

        # Identify best in each category
        best_by_category = self._identify_best_by_category(
            plans=comparison_plans,
            current_plan=current_comp_plan,
        )

        # Generate trade-off analysis
        trade_offs = self._generate_trade_offs(
            plans=comparison_plans,
            current_plan=current_comp_plan,
        )

        # Generate multi-year projections
        multi_year_projections = self._generate_multi_year_projections(
            plans=comparison_plans,
            plan_catalog=plan_catalog,
            usage_projection=usage_projection,
        )

        # Generate assumptions
        assumptions = [
            f"Projections based on {usage_projection.projected_annual_kwh:.0f} kWh annual usage",
            "Assumes usage patterns remain consistent",
            "Current market rates used for variable plans",
            "Contract renewal rates assumed similar to initial rates",
        ]

        return PlanComparison(
            comparison_id=uuid4(),
            user_id=user_id,
            plans=comparison_plans,
            current_plan=current_comp_plan,
            best_by_category=best_by_category,
            trade_offs=trade_offs,
            multi_year_projections=multi_year_projections,
            generated_at=datetime.now(),
            projection_basis=f"Historical 12-month usage projection (confidence: {usage_projection.confidence_score:.2f})",
            assumptions=assumptions,
        )

    def _build_comparison_plan(
        self,
        ranked_plan: RankedPlan,
        full_plan: PlanCatalogResponse,
        current_plan: CurrentPlanResponse,
        usage_projection: UsageProjection,
    ) -> ComparisonPlan:
        """Build ComparisonPlan from ranked plan and catalog details."""
        # Calculate costs
        monthly_breakdown = self._calculate_monthly_breakdown(
            plan=full_plan,
            usage_projection=usage_projection,
        )

        annual_cost = sum(month.total_cost for month in monthly_breakdown)
        monthly_average = annual_cost / Decimal("12")
        first_year_total = annual_cost + (full_plan.connection_fee or Decimal("0.00"))

        # Calculate savings vs current
        monthly_breakdown_current = self._calculate_monthly_breakdown_current_plan(
            current_plan=current_plan,
            usage_projection=usage_projection,
        )
        current_annual = sum(month.total_cost for month in monthly_breakdown_current)

        savings_annual = current_annual - annual_cost
        savings_pct = (
            (savings_annual / current_annual * Decimal("100"))
            if current_annual > 0
            else Decimal("0")
        )

        # Extract rate for fixed plans
        rate_per_kwh = None
        if full_plan.plan_type == "fixed":
            rate_per_kwh = Decimal(str(full_plan.rate_structure.get("rate_per_kwh", 0)))

        return ComparisonPlan(
            plan_id=full_plan.id,
            plan_name=full_plan.plan_name,
            supplier_name=full_plan.supplier.supplier_name if full_plan.supplier else "Unknown",
            annual_cost=annual_cost,
            monthly_average=monthly_average,
            first_year_total=first_year_total,
            contract_length_months=full_plan.contract_length_months,
            early_termination_fee=full_plan.early_termination_fee,
            monthly_fee=full_plan.monthly_fee or Decimal("0.00"),
            renewable_percentage=full_plan.renewable_percentage,
            plan_type=full_plan.plan_type,
            rate_per_kwh=rate_per_kwh,
            supplier_rating=full_plan.supplier.average_rating if full_plan.supplier else None,
            savings_vs_current_annual=savings_annual,
            savings_vs_current_percentage=savings_pct,
            rank=ranked_plan.rank,
            composite_score=ranked_plan.composite_score,
            is_current_plan=False,
            is_recommended=True,
        )

    def _build_current_plan_comparison(
        self,
        current_plan: CurrentPlanResponse,
        usage_projection: UsageProjection,
    ) -> ComparisonPlan:
        """Build ComparisonPlan for user's current plan."""
        monthly_breakdown = self._calculate_monthly_breakdown_current_plan(
            current_plan=current_plan,
            usage_projection=usage_projection,
        )

        annual_cost = sum(month.total_cost for month in monthly_breakdown)
        monthly_average = annual_cost / Decimal("12")

        # Calculate remaining contract length
        contract_end = current_plan.contract_end_date
        today = datetime.now().date()
        remaining_months = max(0, ((contract_end.year - today.year) * 12 + (contract_end.month - today.month)), 0)

        return ComparisonPlan(
            plan_id=UUID(int=0),  # Placeholder for current plan
            plan_name=current_plan.plan_name or "Current Plan",
            supplier_name=current_plan.supplier_name,
            annual_cost=annual_cost,
            monthly_average=monthly_average,
            first_year_total=annual_cost,
            contract_length_months=remaining_months,
            early_termination_fee=current_plan.early_termination_fee,
            monthly_fee=current_plan.monthly_fee or Decimal("0.00"),
            renewable_percentage=Decimal("0"),  # Unknown for current plan
            plan_type="unknown",
            rate_per_kwh=current_plan.current_rate,
            supplier_rating=None,
            savings_vs_current_annual=Decimal("0"),  # No savings vs self
            savings_vs_current_percentage=Decimal("0"),
            rank=None,
            composite_score=None,
            is_current_plan=True,
            is_recommended=False,
        )

    def _identify_best_by_category(
        self,
        plans: list[ComparisonPlan],
        current_plan: ComparisonPlan,
    ) -> dict[str, UUID]:
        """Identify best plan in each category."""
        all_plans = plans + [current_plan]

        best = {}

        # Lowest cost
        lowest_cost_plan = min(all_plans, key=lambda p: p.annual_cost)
        best["lowest_cost"] = lowest_cost_plan.plan_id

        # Highest renewable
        highest_renewable_plan = max(all_plans, key=lambda p: p.renewable_percentage)
        best["highest_renewable"] = highest_renewable_plan.plan_id

        # Most flexible (shortest contract or month-to-month)
        most_flexible_plan = min(all_plans, key=lambda p: p.contract_length_months)
        best["most_flexible"] = most_flexible_plan.plan_id

        # Highest rated supplier
        rated_plans = [p for p in all_plans if p.supplier_rating is not None]
        if rated_plans:
            highest_rated_plan = max(rated_plans, key=lambda p: p.supplier_rating or Decimal("0"))
            best["highest_rated"] = highest_rated_plan.plan_id

        # Best value (highest savings with reasonable terms)
        recommended_plans = [p for p in plans if p.is_recommended]
        if recommended_plans:
            best_value_plan = max(
                recommended_plans,
                key=lambda p: p.savings_vs_current_annual - (p.early_termination_fee / Decimal("12"))
            )
            best["best_value"] = best_value_plan.plan_id

        return best

    def _generate_trade_offs(
        self,
        plans: list[ComparisonPlan],
        current_plan: ComparisonPlan,
    ) -> list[TradeOffNote]:
        """Generate trade-off notes comparing plans."""
        trade_offs = []

        if len(plans) < 2:
            return trade_offs

        # Sort by savings
        plans_by_savings = sorted(plans, key=lambda p: p.savings_vs_current_annual, reverse=True)

        # Trade-off: Cost vs Contract Length
        cheapest = min(plans, key=lambda p: p.annual_cost)
        most_flexible = min(plans, key=lambda p: p.contract_length_months)

        if cheapest.plan_id != most_flexible.plan_id:
            trade_offs.append(
                TradeOffNote(
                    category="flexibility",
                    description=f"{cheapest.plan_name} offers lowest cost (${cheapest.annual_cost:.2f}/yr) "
                    f"but requires {cheapest.contract_length_months}-month contract. "
                    f"{most_flexible.plan_name} is more flexible ({most_flexible.contract_length_months}-month contract) "
                    f"but costs ${most_flexible.annual_cost:.2f}/yr.",
                    affected_plans=[cheapest.plan_id, most_flexible.plan_id],
                    severity="info",
                )
            )

        # Trade-off: Cost vs Renewable Energy
        highest_renewable = max(plans, key=lambda p: p.renewable_percentage)
        if highest_renewable.renewable_percentage > Decimal("50"):
            if highest_renewable.savings_vs_current_annual < plans_by_savings[0].savings_vs_current_annual:
                trade_offs.append(
                    TradeOffNote(
                        category="renewable",
                        description=f"{highest_renewable.plan_name} offers {highest_renewable.renewable_percentage}% renewable energy "
                        f"but saves less (${highest_renewable.savings_vs_current_annual:.2f}/yr) "
                        f"compared to {plans_by_savings[0].plan_name} (${plans_by_savings[0].savings_vs_current_annual:.2f}/yr).",
                        affected_plans=[highest_renewable.plan_id, plans_by_savings[0].plan_id],
                        severity="info",
                    )
                )

        # Trade-off: High ETF warning
        for plan in plans:
            if plan.early_termination_fee > Decimal("150"):
                trade_offs.append(
                    TradeOffNote(
                        category="contract",
                        description=f"{plan.plan_name} has high early termination fee (${plan.early_termination_fee}). "
                        f"Ensure you can commit to the full contract length.",
                        affected_plans=[plan.plan_id],
                        severity="warning",
                    )
                )

        return trade_offs

    def _generate_multi_year_projections(
        self,
        plans: list[ComparisonPlan],
        plan_catalog: dict[UUID, PlanCatalogResponse],
        usage_projection: UsageProjection,
    ) -> dict[str, list[MultiYearProjection]]:
        """Generate 1-3 year cost projections for each plan."""
        projections = {}

        for plan in plans:
            plan_projections = []
            cumulative_cost = Decimal("0")
            cumulative_savings = Decimal("0")

            for year in range(1, 4):  # 1-3 years
                # Assume annual cost stays constant (simplification)
                annual_cost = plan.annual_cost

                # Add connection fee in year 1
                if year == 1:
                    annual_cost += plan_catalog[plan.plan_id].connection_fee or Decimal("0.00") if plan.plan_id in plan_catalog else Decimal("0.00")

                cumulative_cost += annual_cost
                cumulative_savings += plan.savings_vs_current_annual

                notes = []
                if year == 1:
                    notes.append("Includes connection fee")

                # Check if contract renews
                full_plan = plan_catalog.get(plan.plan_id)
                if full_plan and full_plan.contract_length_months > 0:
                    if year * 12 > full_plan.contract_length_months:
                        notes.append("Contract renewed (rates may change)")

                plan_projections.append(
                    MultiYearProjection(
                        year=year,
                        annual_cost=annual_cost,
                        cumulative_cost=cumulative_cost,
                        cumulative_savings=cumulative_savings,
                        notes=notes,
                    )
                )

            projections[str(plan.plan_id)] = plan_projections

        return projections
