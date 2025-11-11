"""
AI-powered explanation generation service using OpenAI API.

This service generates personalized, natural language explanations for
energy plan recommendations using OpenAI's GPT models with fallback
to template-based generation.

Stories: 2.6 (API Integration), 2.7 (Personalization), 2.8 (Caching)
"""

import asyncio
import hashlib
import json
import logging
import time
from decimal import Decimal
from typing import List, Optional, Dict, Any

import httpx
from openai import AsyncOpenAI

from ..schemas.explanation_schemas import (
    RankedPlan,
    UserPreferences,
    CurrentPlan,
    PlanExplanation,
    PersonaType,
    ExplanationMetrics,
)
from .explanation_templates import (
    TemplateExplanationGenerator,
    get_context_aware_message,
)

logger = logging.getLogger(__name__)


class OpenAIExplanationService:
    """
    Service for generating AI-powered plan explanations using OpenAI.

    Features:
    - OpenAI API integration with retry logic
    - Persona-based personalization
    - Readability optimization
    - Fallback to template-based generation
    - Redis caching (24-hour TTL)
    - Performance metrics tracking
    """

    def __init__(
        self,
        api_key: str,
        redis_client: Optional[Any] = None,
        model: str = "gpt-4o-mini",  # Fast and cost-effective
        max_tokens: int = 300,
        temperature: float = 0.7,
        timeout: float = 10.0,
        max_retries: int = 3,
        cache_ttl: int = 86400,  # 24 hours
    ):
        """
        Initialize the explanation service.

        Args:
            api_key: OpenAI API key
            redis_client: Optional Redis client for caching
            model: OpenAI model to use (gpt-4o-mini, gpt-4o, gpt-3.5-turbo)
            max_tokens: Maximum tokens for response
            temperature: Temperature for generation (0.7 = consistent but natural)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            cache_ttl: Cache TTL in seconds (default 24 hours)
        """
        self.api_key = api_key
        self.redis_client = redis_client
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache_ttl = cache_ttl

        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=api_key, timeout=timeout)

        # Initialize template fallback
        self.template_generator = TemplateExplanationGenerator()

        # Metrics tracking
        self.metrics = ExplanationMetrics()

    async def generate_explanation(
        self,
        plan: RankedPlan,
        user_profile: Dict[str, Any],
        preferences: UserPreferences,
        current_plan: Optional[CurrentPlan] = None,
        force_regenerate: bool = False,
    ) -> PlanExplanation:
        """
        Generate personalized explanation for a recommended plan.

        Args:
            plan: Recommended plan with scoring details
            user_profile: User usage analysis profile
            preferences: User's priority preferences
            current_plan: Optional current plan for comparison
            force_regenerate: Skip cache and force new generation

        Returns:
            PlanExplanation with generated text and metadata
        """
        start_time = time.time()

        try:
            # Check cache first (unless force regenerate)
            if not force_regenerate and self.redis_client:
                cached = await self._get_cached_explanation(
                    plan, user_profile, preferences, current_plan
                )
                if cached:
                    logger.info(f"Cache hit for plan {plan.plan_id}")
                    self.metrics.cache_hits += 1
                    return cached

            # Generate with OpenAI
            explanation_text = await self._generate_with_openai(
                plan, user_profile, preferences, current_plan
            )

            # Calculate readability
            readability_score = self._calculate_readability(explanation_text)

            # Create response
            explanation = PlanExplanation(
                plan_id=plan.plan_id,
                explanation_text=explanation_text,
                persona_type=preferences.get_persona_type(),
                readability_score=readability_score,
                generated_via="openai",
                generation_time_ms=int((time.time() - start_time) * 1000),
                model_used=self.model,
                is_fallback=False,
            )

            # Cache result
            if self.redis_client:
                await self._cache_explanation(
                    explanation, plan, user_profile, preferences, current_plan
                )

            self.metrics.generations += 1
            self.metrics.total_generation_time_ms += explanation.generation_time_ms

            return explanation

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}, using template fallback")
            self.metrics.fallback_used += 1

            # Fallback to template
            explanation_text = self.template_generator.generate_explanation(
                plan, user_profile, preferences, current_plan
            )

            # Wrap template result in PlanExplanation object
            return PlanExplanation(
                plan_id=plan.plan_id,
                explanation_text=explanation_text,
                persona_type=preferences.get_persona_type() if hasattr(preferences, 'get_persona_type') else "balanced",
                readability_score=65.0,  # Default acceptable score
                generated_via="template",
                generation_time_ms=int((time.time() - start_time) * 1000),
                model_used="template",
                is_fallback=True,
            )

    async def generate_batch(
        self,
        plans: List[RankedPlan],
        user_profile: Dict[str, Any],
        preferences: UserPreferences,
        current_plan: Optional[CurrentPlan] = None,
    ) -> List[PlanExplanation]:
        """
        Generate explanations for multiple plans concurrently.

        Args:
            plans: List of plans to explain
            user_profile: User usage profile
            preferences: User preferences
            current_plan: Optional current plan

        Returns:
            List of explanations in same order as plans
        """
        tasks = [
            self.generate_explanation(plan, user_profile, preferences, current_plan)
            for plan in plans
        ]
        return await asyncio.gather(*tasks)

    async def _generate_with_openai(
        self,
        plan: RankedPlan,
        user_profile: Dict[str, Any],
        preferences: UserPreferences,
        current_plan: Optional[CurrentPlan] = None,
    ) -> str:
        """
        Generate explanation using OpenAI API with retry logic.

        Args:
            plan: Plan to explain
            user_profile: User's usage profile
            preferences: User preferences
            current_plan: Current plan for comparison

        Returns:
            Generated explanation text

        Raises:
            Exception: If all retries fail
        """
        prompt = self._build_prompt(plan, user_profile, preferences, current_plan)

        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert energy plan advisor who explains recommendations in clear, friendly language at an 8th grade reading level.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )

                # Extract text from response
                explanation = response.choices[0].message.content.strip()

                # Validate response
                if len(explanation) < 50:
                    raise ValueError("Response too short")

                return explanation

            except Exception as e:
                logger.warning(
                    f"OpenAI API attempt {attempt + 1}/{self.max_retries} failed: {e}"
                )

                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    await asyncio.sleep(2**attempt)
                else:
                    raise

        raise Exception("All OpenAI API retry attempts failed")

    def _build_prompt(
        self,
        plan: RankedPlan,
        user_profile: Dict[str, Any],
        preferences: UserPreferences,
        current_plan: Optional[CurrentPlan] = None,
    ) -> str:
        """
        Build OpenAI API prompt with all context.

        Uses clear structure and includes few-shot examples
        for better results.
        """
        # Extract profile details
        stats = user_profile.get("statistics", {})
        avg_kwh = stats.get("mean_kwh", 0)
        profile_type = user_profile.get("profile_type", "unknown")
        seasonal = user_profile.get("seasonal_analysis", {})
        has_seasonal = seasonal.get("has_seasonal_pattern", False)

        # Get persona
        persona_type = preferences.get_persona_type()

        # Determine top priorities
        priorities = []
        if preferences.cost_priority > 40:
            priorities.append(f"cost savings ({preferences.cost_priority}%)")
        if preferences.renewable_priority > 40:
            priorities.append(f"renewable energy ({preferences.renewable_priority}%)")
        if preferences.flexibility_priority > 40:
            priorities.append(f"flexibility ({preferences.flexibility_priority}%)")
        if preferences.rating_priority > 40:
            priorities.append(f"supplier ratings ({preferences.rating_priority}%)")

        priorities_str = ", ".join(priorities) if priorities else "balanced value"

        # Build current plan comparison
        current_plan_context = ""
        annual_cost = getattr(current_plan, 'annual_cost', None) if current_plan else None
        if current_plan and annual_cost:
            savings = getattr(plan, 'projected_annual_savings', None) or Decimal("0")
            savings_pct = (savings / annual_cost * 100) if annual_cost > 0 else 0
            current_plan_context = f"""
Current Plan:
- Annual cost: ${annual_cost:.0f}
- Annual savings with new plan: ${savings:.0f}
- Savings percentage: {savings_pct:.1f}%
"""

        # Build rate description
        rate_desc = self._describe_rate_structure(plan.rate_structure)

        prompt = f"""Explain why this energy plan is recommended for a customer.

USER PROFILE:
- Average monthly usage: {avg_kwh:.0f} kWh
- Usage pattern: {profile_type}{"with strong seasonal variation" if has_seasonal else ""}
- Top priorities: {priorities_str}
- Persona: {persona_type}

RECOMMENDED PLAN:
- Name: {plan.plan_name}
- Supplier: {plan.supplier_name}
- Type: {plan.plan_type}
- Rate: {rate_desc}
- Contract: {plan.contract_length_months} months{"(month-to-month)" if plan.contract_length_months == 0 else ""}
- Renewable: {plan.renewable_percentage:.0f}%
- Projected annual cost: ${plan.projected_annual_cost:.0f}
- Early termination fee: ${plan.early_termination_fee:.0f}

{current_plan_context}

REQUIREMENTS:
Generate a clear, friendly explanation (2-3 sentences) at 8th grade reading level:
1. Why this plan matches their priorities
2. Key benefits compared to their current plan (if applicable)
3. One important consideration or trade-off (if significant)

Guidelines:
- Be specific and use numbers
- Avoid jargon or explain it in parentheses
- Use active voice: "You'll save $300" not "Savings of $300"
- Tone: {self._get_tone_guidance(persona_type)}

EXAMPLE (budget-conscious user):
"This plan will save you $425 per year compared to your current plan, which is 18% less. Based on your average usage of 950 kWh per month, you'll pay a predictable rate with no surprise charges. Keep in mind there's a $150 cancellation fee if you need to end the contract early, but you'll break even in just 5 months."

Generate the explanation now (just the explanation text, no labels):"""

        return prompt

    def _describe_rate_structure(self, rate_structure: Dict[str, Any]) -> str:
        """Describe rate structure in plain language."""
        rate_type = rate_structure.get("type", "unknown")

        if rate_type == "fixed":
            base_rate = rate_structure.get("base_rate", 0)
            return f"{base_rate:.1f}¢ per kWh (fixed)"
        elif rate_type == "variable":
            base_rate = rate_structure.get("base_rate", 0)
            return f"{base_rate:.1f}¢ per kWh base rate (variable)"
        elif rate_type == "tiered":
            return "tiered pricing based on usage"
        elif rate_type == "time_of_use":
            return "time-of-use pricing (different rates for peak/off-peak)"
        else:
            return "custom pricing structure"

    def _get_tone_guidance(self, persona_type: PersonaType) -> str:
        """Get tone guidance based on persona."""
        tones = {
            PersonaType.BUDGET_CONSCIOUS: "Emphasize savings and ROI. Use dollar amounts prominently. Be practical and numbers-driven.",
            PersonaType.ECO_CONSCIOUS: "Highlight environmental impact and renewable energy. Use sustainability language. Be inspirational about values alignment.",
            PersonaType.FLEXIBILITY_FOCUSED: "Emphasize flexibility, no-contract, and freedom. Stress lack of commitment. Be freedom-focused.",
            PersonaType.BALANCED: "Emphasize overall value and best-fit. Balance multiple benefits. Be comprehensive.",
        }
        return tones.get(persona_type, tones[PersonaType.BALANCED])

    def _calculate_readability(self, text: str) -> float:
        """
        Calculate Flesch-Kincaid readability score.

        Target: >60 (8th-9th grade level)

        Returns:
            Readability score (0-100, higher = easier)
        """
        try:
            import textstat

            score = textstat.flesch_reading_ease(text)
            return max(0.0, min(100.0, score))
        except Exception as e:
            logger.warning(f"Readability calculation failed: {e}")
            return 65.0  # Default to acceptable score

    def _generate_cache_key(
        self,
        plan: RankedPlan,
        user_profile: Dict[str, Any],
        preferences: UserPreferences,
        current_plan: Optional[CurrentPlan] = None,
    ) -> str:
        """Generate deterministic cache key."""
        key_data = {
            "plan_id": str(plan.plan_id),
            "model": self.model,
            "profile_type": user_profile.get("profile_type"),
            "avg_kwh": user_profile.get("statistics", {}).get("mean_kwh"),
            "preferences": {
                "cost": preferences.cost_priority,
                "renewable": preferences.renewable_priority,
                "flexibility": preferences.flexibility_priority,
                "rating": preferences.rating_priority,
            },
            "current_plan_cost": getattr(current_plan, 'annual_cost', None) if current_plan else None,
        }

        key_str = json.dumps(key_data, sort_keys=True)
        hash_obj = hashlib.sha256(key_str.encode())
        return f"explanation:{hash_obj.hexdigest()[:16]}"

    async def _get_cached_explanation(
        self,
        plan: RankedPlan,
        user_profile: Dict[str, Any],
        preferences: UserPreferences,
        current_plan: Optional[CurrentPlan] = None,
    ) -> Optional[PlanExplanation]:
        """Retrieve cached explanation if available."""
        try:
            cache_key = self._generate_cache_key(
                plan, user_profile, preferences, current_plan
            )
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                data = json.loads(cached_data)
                return PlanExplanation(**data)

            return None
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
            return None

    async def _cache_explanation(
        self,
        explanation: PlanExplanation,
        plan: RankedPlan,
        user_profile: Dict[str, Any],
        preferences: UserPreferences,
        current_plan: Optional[CurrentPlan] = None,
    ):
        """Cache explanation for future use."""
        try:
            cache_key = self._generate_cache_key(
                plan, user_profile, preferences, current_plan
            )
            data = explanation.dict()
            await self.redis_client.setex(
                cache_key, self.cache_ttl, json.dumps(data)
            )
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")

    def get_metrics(self) -> ExplanationMetrics:
        """Get current metrics."""
        return self.metrics

    def reset_metrics(self):
        """Reset metrics counters."""
        self.metrics = ExplanationMetrics()
