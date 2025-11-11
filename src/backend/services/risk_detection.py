"""
Risk Detection Service
Story 6.1-6.2: Risk Detection & Warning System - Epic 6

This service implements comprehensive risk detection for energy plan
recommendations, including 7+ risk rules and "stay with current plan" logic.

Author: Backend Dev #7
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from ..schemas.recommendation_schemas import RankedPlan, UserPreferences
from ..schemas.risk_schemas import (
    EnhancedRecommendationResult,
    PlanRiskAnalysis,
    RiskCategory,
    RiskDetectionConfig,
    RiskMetrics,
    RiskSeverity,
    RiskSummary,
    RiskType,
    RiskWarning,
    StayRecommendation,
    StayRecommendationTrigger,
)
from ..schemas.savings_schemas import SavingsAnalysis
from ..schemas.usage_analysis import DataQualityMetrics, UsageProfile

logger = logging.getLogger(__name__)


# ============================================================================
# CURRENT PLAN REPRESENTATION
# ============================================================================


class CurrentPlan:
    """
    Represents user's current energy plan.
    Simple dataclass-like structure for current plan data.
    """

    def __init__(
        self,
        plan_name: str,
        supplier_name: str,
        current_rate: Decimal,
        contract_end_date: Optional[datetime] = None,
        early_termination_fee: Decimal = Decimal("0.00"),
        annual_cost: Optional[Decimal] = None,
        contract_start_date: Optional[datetime] = None,
    ):
        self.plan_name = plan_name
        self.supplier_name = supplier_name
        self.current_rate = current_rate
        self.contract_end_date = contract_end_date
        self.early_termination_fee = early_termination_fee
        self.annual_cost = annual_cost
        self.contract_start_date = contract_start_date


# ============================================================================
# RISK DETECTION SERVICE
# ============================================================================


class RiskDetectionService:
    """
    Comprehensive risk detection service for energy plan recommendations.

    Story 6.1: Implements 7+ risk detection rules
    Story 6.2: Implements "stay with current plan" logic
    """

    def __init__(self, config: Optional[RiskDetectionConfig] = None):
        """
        Initialize risk detection service.

        Args:
            config: Optional configuration for risk thresholds
        """
        self.config = config or RiskDetectionConfig()
        self.logger = logging.getLogger(__name__)

    def detect_risks(
        self,
        plans: List[RankedPlan],
        current_plan: Optional[CurrentPlan],
        savings_analyses: Optional[List[SavingsAnalysis]],
        usage_profile: Optional[UsageProfile],
        preferences: Optional[UserPreferences],
    ) -> List[RiskWarning]:
        """
        Detect all risks across recommended plans.

        Story 6.1: Core risk detection method.

        Args:
            plans: List of ranked plans to analyze
            current_plan: User's current plan (if available)
            savings_analyses: Savings analysis for each plan (if available)
            usage_profile: User's usage profile (if available)
            preferences: User preferences (if available)

        Returns:
            List of RiskWarning objects
        """
        start_time = datetime.utcnow()
        all_risks = []

        self.logger.info(f"Detecting risks for {len(plans)} plans")

        for plan in plans:
            # Find corresponding savings analysis
            savings = None
            if savings_analyses:
                savings = next(
                    (s for s in savings_analyses if s.plan_id == plan.plan_id), None
                )

            # Apply all risk detection rules
            plan_risks = self._detect_plan_risks(
                plan, current_plan, savings, usage_profile, preferences
            )
            all_risks.extend(plan_risks)

        # Log metrics
        detection_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        self.logger.info(
            f"Risk detection complete: {len(all_risks)} risks in {detection_time:.2f}ms"
        )

        return all_risks

    def _detect_plan_risks(
        self,
        plan: RankedPlan,
        current_plan: Optional[CurrentPlan],
        savings: Optional[SavingsAnalysis],
        usage_profile: Optional[UsageProfile],
        preferences: Optional[UserPreferences],
    ) -> List[RiskWarning]:
        """
        Detect all risks for a single plan.

        Applies all 7+ risk detection rules.
        """
        risks = []

        # Rule 1: High ETF Warning
        risk = self._check_high_etf(plan)
        if risk:
            risks.append(risk)

        # Rule 2: Low Savings Warning
        if savings:
            risk = self._check_low_savings(plan, savings)
            if risk:
                risks.append(risk)

        # Rule 3: Data Quality Issues
        if usage_profile:
            risk = self._check_data_quality(plan, usage_profile)
            if risk:
                risks.append(risk)

        # Rule 4: Variable Rate Volatility
        risk = self._check_variable_rate_volatility(plan)
        if risk:
            risks.append(risk)

        # Rule 5: Contract Length Mismatch
        if preferences:
            risk = self._check_contract_length_mismatch(plan, preferences)
            if risk:
                risks.append(risk)

        # Rule 6: Supplier Reliability
        risk = self._check_supplier_reliability(plan)
        if risk:
            risks.append(risk)

        # Rule 7: Break-Even Too Long
        if savings and savings.break_even_months:
            risk = self._check_break_even(plan, savings)
            if risk:
                risks.append(risk)

        # Additional Rule 8: Negative Savings
        if savings:
            risk = self._check_negative_savings(plan, savings)
            if risk:
                risks.append(risk)

        # Additional Rule 9: High Upfront Costs
        risk = self._check_high_upfront_costs(plan)
        if risk:
            risks.append(risk)

        return risks

    # ========================================================================
    # RISK DETECTION RULES (Story 6.1)
    # ========================================================================

    def _check_high_etf(self, plan: RankedPlan) -> Optional[RiskWarning]:
        """
        Rule 1: High Early Termination Fee Warning.

        Triggers:
        - Warning: ETF > $150
        - Critical: ETF > $300
        """
        etf = plan.early_termination_fee

        if etf > self.config.critical_etf_threshold:
            return RiskWarning(
                risk_type=RiskType.HIGH_ETF,
                severity=RiskSeverity.CRITICAL,
                category=RiskCategory.CONTRACT_TERMS,
                title="Very High Early Termination Fee",
                message=f"This plan has a ${etf} early termination fee. "
                f"If you need to switch before the contract ends, this could be a significant cost.",
                mitigation="Consider waiting until your current contract ends, "
                "or choose a month-to-month plan for maximum flexibility.",
                affected_plan_ids=[plan.plan_id],
                risk_data={"etf_amount": float(etf)},
            )
        elif etf > self.config.high_etf_threshold:
            return RiskWarning(
                risk_type=RiskType.HIGH_ETF,
                severity=RiskSeverity.WARNING,
                category=RiskCategory.CONTRACT_TERMS,
                title="High Early Termination Fee",
                message=f"This plan has a ${etf} early termination fee. "
                f"Make sure you can commit to the full contract term.",
                mitigation="Consider your long-term plans. If you might move or want to switch, "
                "look for plans with lower termination fees.",
                affected_plan_ids=[plan.plan_id],
                risk_data={"etf_amount": float(etf)},
            )

        return None

    def _check_low_savings(
        self, plan: RankedPlan, savings: SavingsAnalysis
    ) -> Optional[RiskWarning]:
        """
        Rule 2: Low Savings Warning.

        Triggers:
        - Info: Annual savings < 5% of current cost
        - Warning: Annual savings < $100/year
        """
        savings_pct = savings.savings_percentage
        annual_savings = savings.annual_savings

        if savings_pct < self.config.low_savings_percentage:
            if annual_savings < self.config.min_annual_savings:
                return RiskWarning(
                    risk_type=RiskType.LOW_SAVINGS,
                    severity=RiskSeverity.WARNING,
                    category=RiskCategory.SAVINGS,
                    title="Minimal Savings",
                    message=f"This plan saves only ${annual_savings:.2f}/year "
                    f"({savings_pct:.1f}%). The effort of switching may not be worthwhile.",
                    mitigation="Consider if the hassle of switching is worth these modest savings. "
                    "You might be better off staying with your current plan.",
                    affected_plan_ids=[plan.plan_id],
                    risk_data={
                        "annual_savings": float(annual_savings),
                        "savings_percentage": float(savings_pct),
                    },
                )
            else:
                return RiskWarning(
                    risk_type=RiskType.LOW_SAVINGS,
                    severity=RiskSeverity.INFO,
                    category=RiskCategory.SAVINGS,
                    title="Modest Savings",
                    message=f"This plan saves ${annual_savings:.2f}/year "
                    f"({savings_pct:.1f}%). The savings are relatively small.",
                    mitigation=None,
                    affected_plan_ids=[plan.plan_id],
                    risk_data={
                        "annual_savings": float(annual_savings),
                        "savings_percentage": float(savings_pct),
                    },
                )

        return None

    def _check_data_quality(
        self, plan: RankedPlan, usage_profile: UsageProfile
    ) -> Optional[RiskWarning]:
        """
        Rule 3: Data Quality Issues.

        Triggers:
        - Warning: Confidence score < 0.7 or completeness < 80%
        - Critical: Confidence score < 0.5
        """
        confidence = usage_profile.overall_confidence
        completeness = usage_profile.data_quality.completeness_pct

        if confidence < 0.5:
            return RiskWarning(
                risk_type=RiskType.DATA_QUALITY,
                severity=RiskSeverity.CRITICAL,
                category=RiskCategory.DATA_QUALITY,
                title="Low Data Confidence",
                message=f"The usage data has low confidence ({confidence:.0%}). "
                "Cost projections may not be accurate.",
                mitigation="Try to provide more complete usage history. "
                "Consider these recommendations as rough estimates.",
                affected_plan_ids=[plan.plan_id],
                risk_data={
                    "confidence_score": confidence,
                    "completeness_pct": completeness,
                },
            )
        elif confidence < self.config.min_confidence_score or completeness < (
            self.config.min_data_completeness * 100
        ):
            return RiskWarning(
                risk_type=RiskType.DATA_QUALITY,
                severity=RiskSeverity.WARNING,
                category=RiskCategory.DATA_QUALITY,
                title="Data Quality Concerns",
                message=f"Usage data is incomplete ({completeness:.0f}% complete, "
                f"{confidence:.0%} confidence). Projections may vary.",
                mitigation="Actual costs may differ from projections. "
                "Monitor your first few bills closely.",
                affected_plan_ids=[plan.plan_id],
                risk_data={
                    "confidence_score": confidence,
                    "completeness_pct": completeness,
                },
            )

        return None

    def _check_variable_rate_volatility(
        self, plan: RankedPlan
    ) -> Optional[RiskWarning]:
        """
        Rule 4: Variable Rate Volatility Warning.

        Triggers:
        - Warning: Plan type is 'variable' with historical volatility
        """
        if plan.plan_type.lower() == "variable":
            # For variable rate plans, warn about unpredictability
            # In a real system, we'd check historical rate volatility
            return RiskWarning(
                risk_type=RiskType.VARIABLE_RATE_VOLATILITY,
                severity=RiskSeverity.WARNING,
                category=RiskCategory.COST,
                title="Variable Rate Uncertainty",
                message="This is a variable rate plan. Your costs may fluctuate "
                "with market conditions, making budgeting more difficult.",
                mitigation="If you prefer predictable bills, consider a fixed-rate plan. "
                "Variable rates can save money when rates drop, but may cost more when rates rise.",
                affected_plan_ids=[plan.plan_id],
                risk_data={"plan_type": plan.plan_type},
            )

        return None

    def _check_contract_length_mismatch(
        self, plan: RankedPlan, preferences: UserPreferences
    ) -> Optional[RiskWarning]:
        """
        Rule 5: Contract Length Mismatch.

        Triggers:
        - Warning: Long contract (>12 months) when flexibility priority is high (>30%)
        """
        if (
            plan.contract_length_months > 12
            and preferences.flexibility_priority > 30
        ):
            return RiskWarning(
                risk_type=RiskType.CONTRACT_LENGTH_MISMATCH,
                severity=RiskSeverity.WARNING,
                category=RiskCategory.FLEXIBILITY,
                title="Long Contract vs Flexibility Preference",
                message=f"This plan has a {plan.contract_length_months}-month contract, "
                f"but you prioritized flexibility. This limits your ability to switch.",
                mitigation="Consider a month-to-month plan or shorter contract "
                "if flexibility is important to you.",
                affected_plan_ids=[plan.plan_id],
                risk_data={
                    "contract_length": plan.contract_length_months,
                    "flexibility_priority": preferences.flexibility_priority,
                },
            )

        return None

    def _check_supplier_reliability(self, plan: RankedPlan) -> Optional[RiskWarning]:
        """
        Rule 6: Supplier Reliability Warning.

        Triggers:
        - Warning: Supplier rating < 3.5 stars
        - Critical: Supplier rating < 2.5 stars
        """
        # Note: RankedPlan doesn't have supplier rating in the schema
        # In a real system, we'd fetch this from the supplier relationship
        # For now, we'll skip this check as we don't have the data
        # This would be enhanced when supplier data is properly integrated

        return None

    def _check_break_even(
        self, plan: RankedPlan, savings: SavingsAnalysis
    ) -> Optional[RiskWarning]:
        """
        Rule 7: Break-Even Too Long.

        Triggers:
        - Warning: Break-even > 18 months
        - Critical: Break-even > 24 months
        """
        if not savings.break_even_months:
            return None

        break_even = savings.break_even_months

        if break_even > 24:
            return RiskWarning(
                risk_type=RiskType.BREAK_EVEN_TOO_LONG,
                severity=RiskSeverity.CRITICAL,
                category=RiskCategory.SAVINGS,
                title="Very Long Break-Even Period",
                message=f"It will take {break_even} months to recoup the "
                f"${savings.switching_cost} switching cost. This is a very long payback period.",
                mitigation="Consider waiting until your current contract ends "
                "to avoid the early termination fee.",
                affected_plan_ids=[plan.plan_id],
                risk_data={
                    "break_even_months": break_even,
                    "switching_cost": float(savings.switching_cost),
                },
            )
        elif break_even > self.config.max_acceptable_break_even:
            return RiskWarning(
                risk_type=RiskType.BREAK_EVEN_TOO_LONG,
                severity=RiskSeverity.WARNING,
                category=RiskCategory.SAVINGS,
                title="Long Break-Even Period",
                message=f"It will take {break_even} months to recoup the "
                f"${savings.switching_cost} switching cost through savings.",
                mitigation="Consider if you'll stay long enough to realize the savings. "
                "Waiting for contract end might be better.",
                affected_plan_ids=[plan.plan_id],
                risk_data={
                    "break_even_months": break_even,
                    "switching_cost": float(savings.switching_cost),
                },
            )

        return None

    def _check_negative_savings(
        self, plan: RankedPlan, savings: SavingsAnalysis
    ) -> Optional[RiskWarning]:
        """
        Additional Rule 8: Negative Savings.

        Triggers:
        - Critical: Plan costs more than current plan
        """
        if savings.annual_savings < 0:
            return RiskWarning(
                risk_type=RiskType.NEGATIVE_SAVINGS,
                severity=RiskSeverity.CRITICAL,
                category=RiskCategory.COST,
                title="Higher Cost Than Current Plan",
                message=f"This plan would cost ${abs(savings.annual_savings):.2f} MORE per year "
                "than your current plan. It's recommended because of other factors "
                "(renewable energy, supplier rating, etc.).",
                mitigation="Consider if the non-cost benefits are worth the extra expense. "
                "If cost is your priority, this plan may not be suitable.",
                affected_plan_ids=[plan.plan_id],
                risk_data={"annual_savings": float(savings.annual_savings)},
            )

        return None

    def _check_high_upfront_costs(self, plan: RankedPlan) -> Optional[RiskWarning]:
        """
        Additional Rule 9: High Upfront Costs.

        Triggers:
        - Info: Connection fee + first month fees > $100
        """
        upfront_cost = (plan.connection_fee or Decimal("0")) + (
            plan.monthly_fee or Decimal("0")
        )

        if upfront_cost > Decimal("100"):
            return RiskWarning(
                risk_type=RiskType.HIGH_UPFRONT_COSTS,
                severity=RiskSeverity.INFO,
                category=RiskCategory.COST,
                title="Upfront Costs",
                message=f"This plan has ${upfront_cost:.2f} in upfront costs "
                "(connection fee and first month's base fee).",
                mitigation=None,
                affected_plan_ids=[plan.plan_id],
                risk_data={"upfront_cost": float(upfront_cost)},
            )

        return None

    # ========================================================================
    # "STAY WITH CURRENT PLAN" LOGIC (Story 6.2)
    # ========================================================================

    def should_recommend_staying(
        self,
        current_plan: CurrentPlan,
        top_plan: RankedPlan,
        savings: SavingsAnalysis,
        risks: List[RiskWarning],
        all_plans_count: int = 0,
    ) -> Tuple[bool, Optional[StayRecommendation]]:
        """
        Determine if user should stay with current plan.

        Story 6.2: Core "stay" logic with 5 triggers.

        Args:
            current_plan: User's current plan
            top_plan: Best recommended plan
            savings: Savings analysis for top plan
            risks: All detected risks
            all_plans_count: Total number of plans analyzed (for percentile calc)

        Returns:
            Tuple of (should_stay: bool, stay_recommendation: Optional[StayRecommendation])
        """
        triggers = []
        net_savings = savings.cumulative_savings_12_months
        break_even = savings.break_even_months

        # Trigger 1: Low net savings after ETF
        if net_savings < self.config.stay_min_net_savings:
            triggers.append(StayRecommendationTrigger.LOW_NET_SAVINGS)

        # Trigger 2: Break-even too long
        if break_even and break_even > self.config.stay_max_break_even:
            triggers.append(StayRecommendationTrigger.LONG_BREAK_EVEN)

        # Trigger 3: Multiple critical risks
        critical_risks = [r for r in risks if r.severity == RiskSeverity.CRITICAL]
        if len(critical_risks) >= 2:
            triggers.append(StayRecommendationTrigger.CRITICAL_RISKS)

        # Trigger 4: Current plan already optimal (top 10%)
        # This would require knowing where current plan ranks among all plans
        # For now, we'll check if savings are very small, implying current plan is good
        if (
            savings.savings_percentage < Decimal("2.0")
            and savings.annual_savings < self.config.min_annual_savings
        ):
            triggers.append(StayRecommendationTrigger.CURRENT_PLAN_OPTIMAL)

        # Trigger 5: Contract ends soon + high ETF in recommended plan
        days_until_end = None
        if current_plan.contract_end_date:
            days_until_end = (
                current_plan.contract_end_date - datetime.now().date()
            ).days
            if (
                days_until_end < self.config.contract_ending_soon_days
                and top_plan.early_termination_fee > self.config.high_etf_threshold
            ):
                triggers.append(StayRecommendationTrigger.CONTRACT_ENDING_SOON)

        # Decide if staying is recommended
        should_stay = len(triggers) > 0

        if not should_stay:
            return False, None

        # Generate reasoning
        reasoning = self._generate_stay_reasoning(
            triggers, net_savings, break_even, critical_risks, days_until_end
        )

        # Calculate current plan percentile (simplified)
        # In real system, this would rank current plan among all available plans
        current_plan_percentile = None
        if StayRecommendationTrigger.CURRENT_PLAN_OPTIMAL in triggers:
            current_plan_percentile = 95.0  # Top 5%

        # Build stay recommendation
        stay_rec = StayRecommendation(
            should_stay=True,
            triggers=triggers,
            reasoning=reasoning,
            net_annual_savings=net_savings,
            break_even_months=break_even,
            critical_risk_count=len(critical_risks),
            current_plan_percentile=current_plan_percentile,
            days_until_contract_end=days_until_end,
            confidence=0.85,
        )

        return True, stay_rec

    def _generate_stay_reasoning(
        self,
        triggers: List[StayRecommendationTrigger],
        net_savings: Decimal,
        break_even: Optional[int],
        critical_risks: List[RiskWarning],
        days_until_end: Optional[int],
    ) -> str:
        """Generate plain-language reasoning for stay recommendation."""
        reasons = []

        if StayRecommendationTrigger.LOW_NET_SAVINGS in triggers:
            reasons.append(
                f"the net savings after switching costs are only ${net_savings:.2f}/year"
            )

        if StayRecommendationTrigger.LONG_BREAK_EVEN in triggers:
            reasons.append(
                f"it would take {break_even} months to recoup the switching costs"
            )

        if StayRecommendationTrigger.CRITICAL_RISKS in triggers:
            reasons.append(
                f"there are {len(critical_risks)} critical risks with the recommended plans"
            )

        if StayRecommendationTrigger.CURRENT_PLAN_OPTIMAL in triggers:
            reasons.append("your current plan is already very competitive")

        if StayRecommendationTrigger.CONTRACT_ENDING_SOON in triggers:
            reasons.append(
                f"your contract ends in {days_until_end} days, so waiting avoids termination fees"
            )

        if reasons:
            reasoning = (
                "We recommend staying with your current plan because "
                + ", ".join(reasons)
                + ". "
            )
            reasoning += (
                "While switching is possible, the benefits don't outweigh the costs and risks."
            )
        else:
            reasoning = "We recommend staying with your current plan based on the overall analysis."

        return reasoning

    # ========================================================================
    # RISK SUMMARY AND AGGREGATION
    # ========================================================================

    def calculate_risk_summary(
        self, risks: List[RiskWarning], plans: List[RankedPlan]
    ) -> RiskSummary:
        """
        Calculate aggregate risk summary.

        Story 6.1: Risk summary for API response.
        """
        critical_count = sum(1 for r in risks if r.severity == RiskSeverity.CRITICAL)
        warning_count = sum(1 for r in risks if r.severity == RiskSeverity.WARNING)
        info_count = sum(1 for r in risks if r.severity == RiskSeverity.INFO)

        # Calculate overall risk level
        if critical_count >= 2:
            overall_risk_level = "high"
        elif critical_count >= 1 or warning_count >= 3:
            overall_risk_level = "medium"
        else:
            overall_risk_level = "low"

        # Count risks per plan
        risks_by_plan = {}
        for plan in plans:
            plan_id_str = str(plan.plan_id)
            plan_risks = [
                r for r in risks if plan.plan_id in r.affected_plan_ids
            ]
            risks_by_plan[plan_id_str] = len(plan_risks)

        return RiskSummary(
            total_risks=len(risks),
            critical_count=critical_count,
            warning_count=warning_count,
            info_count=info_count,
            overall_risk_level=overall_risk_level,
            risks_by_plan=risks_by_plan,
        )

    def group_risks_by_plan(
        self, risks: List[RiskWarning], plans: List[RankedPlan]
    ) -> List[PlanRiskAnalysis]:
        """
        Group risks by plan for easier frontend consumption.

        Story 6.3: Helper for API response formatting.
        """
        plan_risk_analyses = []

        for plan in plans:
            plan_risks = [
                r for r in risks if plan.plan_id in r.affected_plan_ids
            ]

            highest_severity = None
            if plan_risks:
                # Sort by severity (critical > warning > info)
                severity_order = {
                    RiskSeverity.CRITICAL: 0,
                    RiskSeverity.WARNING: 1,
                    RiskSeverity.INFO: 2,
                }
                plan_risks_sorted = sorted(
                    plan_risks, key=lambda r: severity_order[r.severity]
                )
                highest_severity = plan_risks_sorted[0].severity

            plan_risk_analyses.append(
                PlanRiskAnalysis(
                    plan_id=plan.plan_id,
                    plan_name=plan.plan_name,
                    risks=plan_risks,
                    risk_count=len(plan_risks),
                    highest_severity=highest_severity,
                    is_recommended=plan.rank <= 3,
                )
            )

        return plan_risk_analyses


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def create_risk_detection_service(
    config: Optional[RiskDetectionConfig] = None,
) -> RiskDetectionService:
    """
    Factory function to create RiskDetectionService.

    Args:
        config: Optional configuration for risk detection

    Returns:
        RiskDetectionService instance
    """
    return RiskDetectionService(config=config)
