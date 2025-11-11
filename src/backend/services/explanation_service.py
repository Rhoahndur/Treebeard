"""
AI-powered explanation generation service using Claude API.

This service generates personalized, natural language explanations for
energy plan recommendations using Anthropic's Claude API with fallback
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

# Import OpenAI service
from .explanation_service_openai import OpenAIExplanationService

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


class ClaudeExplanationService:
    """
    Service for generating AI-powered plan explanations.

    Features:
    - Claude API integration with retry logic
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
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 300,
        temperature: float = 0.7,
        timeout: float = 10.0,
        max_retries: int = 3,
        cache_ttl: int = 86400,  # 24 hours
    ):
        """
        Initialize the explanation service.

        Args:
            api_key: Anthropic API key
            redis_client: Optional Redis client for caching
            model: Claude model to use
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

        # Initialize Claude client
        self.client = AsyncAnthropic(api_key=api_key)

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
        Generate explanation for a recommended plan.

        Args:
            plan: The plan to explain
            user_profile: User's usage profile
            preferences: User's stated preferences
            current_plan: Current plan for comparison
            force_regenerate: Skip cache and regenerate

        Returns:
            PlanExplanation with all details
        """
        start_time = time.time()

        # Check cache first
        if not force_regenerate and self.redis_client:
            cached = await self._get_cached_explanation(
                plan, user_profile, preferences
            )
            if cached:
                self.metrics.cache_hits += 1
                logger.info(f"Cache hit for plan {plan.plan_id}")
                return cached

        self.metrics.cache_misses += 1

        # Generate explanation
        try:
            explanation_text = await self._generate_with_claude(
                plan, user_profile, preferences, current_plan
            )
            generated_via = "claude_api"
            self.metrics.api_calls += 1
            logger.info(f"Generated explanation via Claude API for plan {plan.plan_id}")

        except Exception as e:
            logger.error(f"Claude API failed, using template fallback: {e}")
            explanation_text = self.template_generator.generate_explanation(
                plan, user_profile, preferences, current_plan
            )
            generated_via = "template"
            self.metrics.fallback_used += 1

        # Calculate readability score
        readability_score = self._calculate_readability(explanation_text)

        # Identify differentiators and trade-offs
        key_differentiators = self.template_generator.identify_key_differentiators(
            plan
        )
        trade_offs = self.template_generator.identify_trade_offs(plan, current_plan)

        # Get persona type
        persona_type = preferences.get_persona_type()

        # Create explanation object
        explanation = PlanExplanation(
            plan_id=plan.plan_id,
            explanation_text=explanation_text,
            key_differentiators=key_differentiators,
            trade_offs=trade_offs,
            persona_type=persona_type,
            readability_score=readability_score,
            generated_via=generated_via,
        )

        # Cache the result
        if self.redis_client:
            await self._cache_explanation(
                plan, user_profile, preferences, explanation
            )

        # Update metrics
        generation_time = (time.time() - start_time) * 1000
        self._update_metrics(generation_time, readability_score)
        self.metrics.total_generated += 1

        return explanation

    async def generate_bulk_explanations(
        self,
        plans: List[RankedPlan],
        user_profile: Dict[str, Any],
        preferences: UserPreferences,
        current_plan: Optional[CurrentPlan] = None,
    ) -> List[PlanExplanation]:
        """
        Generate explanations for multiple plans efficiently.

        Args:
            plans: List of plans to explain (max 3)
            user_profile: User's usage profile
            preferences: User preferences
            current_plan: Current plan for comparison

        Returns:
            List of PlanExplanation objects
        """
        tasks = [
            self.generate_explanation(plan, user_profile, preferences, current_plan)
            for plan in plans
        ]
        return await asyncio.gather(*tasks)

    async def _generate_with_claude(
        self,
        plan: RankedPlan,
        user_profile: Dict[str, Any],
        preferences: UserPreferences,
        current_plan: Optional[CurrentPlan] = None,
    ) -> str:
        """
        Generate explanation using Claude API with retry logic.

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
                response: Message = await self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt}],
                    timeout=self.timeout,
                )

                # Extract text from response
                explanation = response.content[0].text.strip()

                # Validate response
                if len(explanation) < 50:
                    raise ValueError("Response too short")

                return explanation

            except Exception as e:
                logger.warning(
                    f"Claude API attempt {attempt + 1}/{self.max_retries} failed: {e}"
                )

                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise

        raise Exception("All Claude API retry attempts failed")

    def _build_prompt(
        self,
        plan: RankedPlan,
        user_profile: Dict[str, Any],
        preferences: UserPreferences,
        current_plan: Optional[CurrentPlan] = None,
    ) -> str:
        """
        Build Claude API prompt with all context.

        Uses XML tags for structure and includes few-shot examples
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
        if current_plan and current_plan.annual_cost:
            savings = plan.projected_annual_savings or Decimal("0")
            current_plan_context = f"""
<current_plan>
- Annual cost: ${current_plan.annual_cost:.0f}
- Annual savings with new plan: ${savings:.0f}
- Savings percentage: {(savings / current_plan.annual_cost * 100):.1f}%
</current_plan>
"""

        # Build rate description
        rate_desc = self._describe_rate_structure(plan.rate_structure)

        prompt = f"""You are an energy plan advisor. Explain to a customer why this plan is recommended for them.

<user_profile>
- Average monthly usage: {avg_kwh:.0f} kWh
- Usage pattern: {profile_type}{"with strong seasonal variation" if has_seasonal else ""}
- Top priorities: {priorities_str}
- Persona: {persona_type}
</user_profile>

<recommended_plan>
- Name: {plan.plan_name}
- Supplier: {plan.supplier_name}
- Type: {plan.plan_type}
- Rate: {rate_desc}
- Contract: {plan.contract_length_months} months{"(month-to-month)" if plan.contract_length_months == 0 else ""}
- Renewable: {plan.renewable_percentage:.0f}%
- Projected annual cost: ${plan.projected_annual_cost:.0f}
- Early termination fee: ${plan.early_termination_fee:.0f}
</recommended_plan>
{current_plan_context}
<requirements>
Generate a clear, friendly explanation (2-3 sentences) at 8th grade reading level explaining:
1. Why this plan matches their priorities
2. Key benefits compared to their current plan (if applicable)
3. One important consideration or trade-off (if significant)

Be specific and use numbers. Avoid jargon or explain it in parentheses.
Use active voice: "You'll save $300" not "Savings of $300 will be realized".

Tone: {self._get_tone_guidance(persona_type)}
</requirements>

<example_good>
For budget-conscious user:
"This plan will save you $425 per year compared to your current plan, which is 18% less. Based on your average usage of 950 kWh per month, you'll pay a predictable rate with no surprise charges. Keep in mind there's a $150 cancellation fee if you need to end the contract early, but you'll break even in just 5 months."

For eco-conscious user:
"This plan is 100% renewable energy, which aligns with your environmental priorities. While it costs $10 more per month than the cheapest option, you'll be supporting wind and solar power for your entire 12,000 kWh annual usage. The 12-month contract locks in this rate and includes no cancellation fees."
</example_good>

Generate the explanation now. Do not include labels or headers, just the explanation text:"""

        return prompt

    def _describe_rate_structure(self, rate_structure: Dict[str, Any]) -> str:
        """Describe rate structure in plain language."""
        rate_type = rate_structure.get("type", "unknown")

        if rate_type == "fixed":
            rate = rate_structure.get("rate_per_kwh", 0)
            return f"{rate:.2f}¢ per kWh (fixed)"
        elif rate_type == "variable":
            base_rate = rate_structure.get("base_rate", 0)
            return f"{base_rate:.2f}¢ per kWh base rate (variable)"
        elif rate_type == "tiered":
            return "tiered pricing based on usage"
        elif rate_type == "time_of_use":
            return "time-of-use pricing (different rates for peak/off-peak)"
        else:
            return "competitive market rate"

    def _get_tone_guidance(self, persona_type: str) -> str:
        """Get tone guidance for different personas."""
        tones = {
            PersonaType.BUDGET_CONSCIOUS: "Emphasize savings and ROI. Use dollar amounts prominently.",
            PersonaType.ECO_CONSCIOUS: "Highlight environmental impact and renewable energy. Use sustainability language.",
            PersonaType.FLEXIBILITY_FOCUSED: "Emphasize flexibility, no-contract, and freedom. Stress lack of commitment.",
            PersonaType.BALANCED: "Emphasize overall value and best-fit. Balance multiple benefits.",
        }
        return tones.get(persona_type, tones[PersonaType.BALANCED])

    def _calculate_readability(self, text: str) -> float:
        """
        Calculate Flesch-Kincaid readability score.

        Target: >60 (8th grade level or easier)

        Returns:
            Readability score (0-100, higher = easier)
        """
        try:
            import textstat

            score = textstat.flesch_reading_ease(text)
            return max(0.0, min(100.0, score))
        except ImportError:
            # Fallback: simple heuristic based on sentence and word length
            sentences = text.count(".") + text.count("!") + text.count("?")
            words = len(text.split())
            avg_words_per_sentence = words / max(sentences, 1)

            # Rough estimate: shorter sentences = higher score
            # Target: 15-20 words per sentence = ~60 score
            if avg_words_per_sentence <= 15:
                return 70.0
            elif avg_words_per_sentence <= 20:
                return 60.0
            elif avg_words_per_sentence <= 25:
                return 50.0
            else:
                return 40.0

    async def _get_cached_explanation(
        self,
        plan: RankedPlan,
        user_profile: Dict[str, Any],
        preferences: UserPreferences,
    ) -> Optional[PlanExplanation]:
        """Get cached explanation if available."""
        if not self.redis_client:
            return None

        cache_key = self._generate_cache_key(plan, user_profile, preferences)

        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                return PlanExplanation(**data)
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")

        return None

    async def _cache_explanation(
        self,
        plan: RankedPlan,
        user_profile: Dict[str, Any],
        preferences: UserPreferences,
        explanation: PlanExplanation,
    ) -> None:
        """Cache explanation with TTL."""
        if not self.redis_client:
            return

        cache_key = self._generate_cache_key(plan, user_profile, preferences)

        try:
            # Convert to JSON-serializable dict
            data = explanation.model_dump(mode="json")
            await self.redis_client.setex(
                cache_key, self.cache_ttl, json.dumps(data)
            )
            logger.debug(f"Cached explanation with key: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")

    def _generate_cache_key(
        self,
        plan: RankedPlan,
        user_profile: Dict[str, Any],
        preferences: UserPreferences,
    ) -> str:
        """
        Generate cache key from plan, profile, and preferences.

        Key format: explanation:{hash}
        Hash includes: plan_id, profile_type, persona_type
        """
        # Extract key attributes
        profile_type = user_profile.get("profile_type", "unknown")
        persona_type = preferences.get_persona_type()

        # Create hash input
        hash_input = f"{plan.plan_id}:{profile_type}:{persona_type}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()

        return f"explanation:{hash_value}"

    def _update_metrics(self, generation_time_ms: float, readability_score: float):
        """Update running metrics."""
        # Update average generation time
        total = self.metrics.total_generated
        if total > 0:
            current_avg = self.metrics.avg_generation_time_ms
            self.metrics.avg_generation_time_ms = (
                current_avg * total + generation_time_ms
            ) / (total + 1)
        else:
            self.metrics.avg_generation_time_ms = generation_time_ms

        # Update average readability
        if total > 0:
            current_avg = self.metrics.avg_readability_score
            self.metrics.avg_readability_score = (
                current_avg * total + readability_score
            ) / (total + 1)
        else:
            self.metrics.avg_readability_score = readability_score

    def get_metrics(self) -> ExplanationMetrics:
        """Get current metrics."""
        return self.metrics

    async def invalidate_cache(self, plan_id: Optional[str] = None) -> int:
        """
        Invalidate cached explanations.

        Args:
            plan_id: Specific plan ID to invalidate (None = all)

        Returns:
            Number of keys invalidated
        """
        if not self.redis_client:
            return 0

        try:
            if plan_id:
                # Invalidate specific plan (all personas)
                pattern = f"explanation:*{plan_id}*"
            else:
                # Invalidate all explanations
                pattern = "explanation:*"

            # Scan and delete matching keys
            deleted = 0
            async for key in self.redis_client.scan_iter(match=pattern):
                await self.redis_client.delete(key)
                deleted += 1

            logger.info(f"Invalidated {deleted} cached explanations")
            return deleted

        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")
            return 0

    async def warm_cache(
        self,
        plans: List[RankedPlan],
        personas: List[str],
        mock_profile: Dict[str, Any],
    ) -> int:
        """
        Pre-generate explanations for popular plan/persona combinations.

        Args:
            plans: List of plans to pre-generate for
            personas: List of persona types to generate
            mock_profile: Mock usage profile to use

        Returns:
            Number of explanations generated
        """
        generated = 0

        for plan in plans:
            for persona in personas:
                # Create mock preferences for this persona
                prefs = self._create_mock_preferences(persona)

                try:
                    await self.generate_explanation(
                        plan=plan,
                        user_profile=mock_profile,
                        preferences=prefs,
                        force_regenerate=True,
                    )
                    generated += 1
                    logger.debug(
                        f"Warmed cache for plan {plan.plan_id}, persona {persona}"
                    )

                except Exception as e:
                    logger.warning(
                        f"Failed to warm cache for plan {plan.plan_id}: {e}"
                    )

        logger.info(f"Warmed cache with {generated} explanations")
        return generated

    def _create_mock_preferences(self, persona: str) -> UserPreferences:
        """Create mock preferences for a persona."""
        if persona == PersonaType.BUDGET_CONSCIOUS:
            return UserPreferences(
                cost_priority=60, flexibility_priority=20, renewable_priority=10, rating_priority=10
            )
        elif persona == PersonaType.ECO_CONSCIOUS:
            return UserPreferences(
                cost_priority=10, flexibility_priority=10, renewable_priority=70, rating_priority=10
            )
        elif persona == PersonaType.FLEXIBILITY_FOCUSED:
            return UserPreferences(
                cost_priority=10, flexibility_priority=70, renewable_priority=10, rating_priority=10
            )
        else:  # BALANCED
            return UserPreferences(
                cost_priority=25, flexibility_priority=25, renewable_priority=25, rating_priority=25
            )


def create_explanation_service(
    api_key: str,
    redis_client: Optional[Any] = None,
    **kwargs,
) -> OpenAIExplanationService:
    """
    Factory function to create explanation service.

    Args:
        api_key: OpenAI API key
        redis_client: Optional Redis client
        **kwargs: Additional configuration

    Returns:
        Configured OpenAIExplanationService
    """
    return OpenAIExplanationService(api_key=api_key, redis_client=redis_client, **kwargs)
