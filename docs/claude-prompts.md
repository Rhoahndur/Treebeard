# Claude API Prompts for Energy Plan Explanations

**Version:** 1.0
**Date:** November 10, 2025
**Author:** ML Engineer (Epic 2)

---

## Overview

This document contains the prompt engineering templates and examples used for generating personalized energy plan explanations using Claude API. These prompts are designed to produce clear, friendly, 8th-grade reading level explanations that help users understand why a plan is recommended.

---

## Core Prompt Template

### Base Structure

The prompt uses XML tags for structure and includes:
1. User profile context
2. Recommended plan details
3. Current plan comparison (if available)
4. Generation requirements
5. Persona-specific tone guidance
6. Few-shot examples

```
You are an energy plan advisor. Explain to a customer why this plan is recommended for them.

<user_profile>
- Average monthly usage: {avg_kwh} kWh
- Usage pattern: {profile_type} {seasonal_info}
- Top priorities: {priorities_str}
- Persona: {persona_type}
</user_profile>

<recommended_plan>
- Name: {plan_name}
- Supplier: {supplier_name}
- Type: {plan_type}
- Rate: {rate_description}
- Contract: {contract_length} months {month_to_month_note}
- Renewable: {renewable_percentage}%
- Projected annual cost: ${annual_cost}
- Early termination fee: ${etf}
</recommended_plan>

<current_plan>
- Annual cost: ${current_annual_cost}
- Annual savings with new plan: ${savings}
- Savings percentage: {savings_pct}%
</current_plan>

<requirements>
Generate a clear, friendly explanation (2-3 sentences) at 8th grade reading level explaining:
1. Why this plan matches their priorities
2. Key benefits compared to their current plan (if applicable)
3. One important consideration or trade-off (if significant)

Be specific and use numbers. Avoid jargon or explain it in parentheses.
Use active voice: "You'll save $300" not "Savings of $300 will be realized".

Tone: {tone_guidance}
</requirements>

<example_good>
{persona_specific_examples}
</example_good>

Generate the explanation now. Do not include labels or headers, just the explanation text:
```

---

## Persona-Specific Variations

### 1. Budget-Conscious Persona

**When to Use:** `cost_priority > 50`

**Tone Guidance:**
```
Emphasize savings and ROI. Use dollar amounts prominently. Be practical and numbers-driven.
```

**Example Prompts:**

#### High Savings Scenario

**Input:**
```
<user_profile>
- Average monthly usage: 950 kWh
- Usage pattern: baseline
- Top priorities: cost savings (60%)
- Persona: budget_conscious
</user_profile>

<recommended_plan>
- Name: Value Saver Fixed
- Supplier: Budget Energy Co
- Type: fixed
- Rate: 7.8¢ per kWh (fixed)
- Contract: 12 months
- Renewable: 25%
- Projected annual cost: $850
- Early termination fee: $150
</recommended_plan>

<current_plan>
- Annual cost: $1,275
- Annual savings with new plan: $425
- Savings percentage: 33.3%
</current_plan>
```

**Expected Output:**
```
This plan will save you $425 per year compared to your current plan, which is 33% less.
Based on your average usage of 950 kWh per month, you'll pay a predictable fixed rate
with no surprise charges. Keep in mind there's a $150 cancellation fee if you need to
end the contract early, but you'll break even in just 5 months.
```

#### Modest Savings with Benefits

**Input:**
```
<user_profile>
- Average monthly usage: 1200 kWh
- Usage pattern: high_user
- Top priorities: cost savings (55%), reliability (30%)
- Persona: budget_conscious
</user_profile>

<recommended_plan>
- Name: Reliable Energy Plus
- Supplier: Trusted Power Inc
- Type: fixed
- Rate: 8.2¢ per kWh (fixed)
- Contract: 24 months
- Renewable: 30%
- Projected annual cost: $1,180
- Early termination fee: $100
</recommended_plan>

<current_plan>
- Annual cost: $1,250
- Annual savings with new plan: $70
- Savings percentage: 5.6%
</current_plan>
```

**Expected Output:**
```
This plan saves you $70 per year while giving you the reliability of a top-rated
supplier. Your rate is locked in for 24 months, protecting you from market increases
on your 1,200 kWh monthly usage. While the savings are modest at 6%, the stability
and excellent customer service ratings make this a solid choice.
```

---

### 2. Eco-Conscious Persona

**When to Use:** `renewable_priority > 50`

**Tone Guidance:**
```
Highlight environmental impact and renewable energy. Use sustainability language.
Be inspirational about values alignment.
```

**Example Prompts:**

#### 100% Renewable Plan

**Input:**
```
<user_profile>
- Average monthly usage: 1000 kWh
- Usage pattern: seasonal with summer peaks
- Top priorities: renewable energy (70%), cost (20%)
- Persona: eco_conscious
</user_profile>

<recommended_plan>
- Name: Green Energy 100
- Supplier: EcoEnergy Inc
- Type: fixed
- Rate: 10.4¢ per kWh (fixed)
- Contract: 12 months
- Renewable: 100%
- Projected annual cost: $1,250
- Early termination fee: $0
</recommended_plan>

<current_plan>
- Annual cost: $1,200
- Annual savings with new plan: -$50
- Savings percentage: -4.2%
</current_plan>
```

**Expected Output:**
```
This plan is 100% renewable energy, which perfectly aligns with your environmental
priorities. While it costs $50 more per year than your current plan (just $4 per
month), you'll be supporting wind and solar power for your entire 12,000 kWh annual
usage. The 12-month contract locks in this green rate with no cancellation fees.
```

#### High Renewable with Savings

**Input:**
```
<user_profile>
- Average monthly usage: 850 kWh
- Usage pattern: baseline
- Top priorities: renewable energy (65%), flexibility (25%)
- Persona: eco_conscious
</user_profile>

<recommended_plan>
- Name: Wind Power 75
- Supplier: Green Choice Energy
- Type: fixed
- Rate: 9.1¢ per kWh (fixed)
- Contract: 6 months
- Renewable: 75%
- Projected annual cost: $925
- Early termination fee: $50
</recommended_plan>

<current_plan>
- Annual cost: $1,100
- Annual savings with new plan: $175
- Savings percentage: 15.9%
</current_plan>
```

**Expected Output:**
```
This plan delivers 75% renewable energy from wind farms while saving you $175 per
year—a win for both your values and your wallet. The short 6-month contract gives
you flexibility, and with your 850 kWh monthly usage, you'll be powering your home
with mostly clean energy. Plus, there's only a $50 early termination fee if you need
to switch.
```

---

### 3. Flexibility-Focused Persona

**When to Use:** `flexibility_priority > 50`

**Tone Guidance:**
```
Emphasize flexibility, no-contract, and freedom. Stress lack of commitment. Be
freedom-focused.
```

**Example Prompts:**

#### Month-to-Month Plan

**Input:**
```
<user_profile>
- Average monthly usage: 900 kWh
- Usage pattern: variable
- Top priorities: flexibility (70%), cost (20%)
- Persona: flexibility_focused
</user_profile>

<recommended_plan>
- Name: No Commitment Plus
- Supplier: FlexPower
- Type: variable
- Rate: 9.0¢ per kWh base rate (variable)
- Contract: 0 months (month-to-month)
- Renewable: 20%
- Projected annual cost: $1,035
- Early termination fee: $0
</recommended_plan>

<current_plan>
- Annual cost: $1,150
- Annual savings with new plan: $115
- Savings percentage: 10.0%
</current_plan>
```

**Expected Output:**
```
This plan gives you complete flexibility with no long-term commitment—you can cancel
anytime without any penalties. You'll save about $115 per year with your 900 kWh
monthly usage. Keep in mind the rate can adjust monthly based on market conditions,
but you're never locked in if you find a better option.
```

#### Low ETF with Short Contract

**Input:**
```
<user_profile>
- Average monthly usage: 1100 kWh
- Usage pattern: seasonal
- Top priorities: flexibility (60%), renewable (30%)
- Persona: flexibility_focused
</user_profile>

<recommended_plan>
- Name: Flexible Green 3
- Supplier: Smart Energy Co
- Type: fixed
- Rate: 9.5¢ per kWh (fixed)
- Contract: 3 months
- Renewable: 50%
- Projected annual cost: $1,254
- Early termination fee: $25
</recommended_plan>

<current_plan>
- Annual cost: $1,320
- Annual savings with new plan: $66
- Savings percentage: 5.0%
</current_plan>
```

**Expected Output:**
```
This plan combines flexibility with green energy—a short 3-month contract with 50%
renewable power. You'll save $66 annually, and if you need to switch, there's only
a minimal $25 fee. Based on your 1,100 kWh monthly usage, this gives you stability
for a season without a long-term commitment.
```

---

### 4. Balanced Persona

**When to Use:** No dominant priority (all <50%)

**Tone Guidance:**
```
Emphasize overall value and best-fit. Balance multiple benefits. Be comprehensive.
```

**Example Prompts:**

#### Well-Rounded Plan

**Input:**
```
<user_profile>
- Average monthly usage: 975 kWh
- Usage pattern: seasonal
- Top priorities: balanced priorities across cost, flexibility, renewable, ratings
- Persona: balanced
</user_profile>

<recommended_plan>
- Name: Complete Value Plan
- Supplier: Reliable Energy Corp
- Type: fixed
- Rate: 8.7¢ per kWh (fixed)
- Contract: 12 months
- Renewable: 50%
- Projected annual cost: $1,018
- Early termination fee: $100
</recommended_plan>

<current_plan>
- Annual cost: $1,215
- Annual savings with new plan: $197
- Savings percentage: 16.2%
</current_plan>
```

**Expected Output:**
```
This plan provides the best overall value for your needs, with $197 in annual savings,
50% renewable energy, and a top-rated supplier. Based on your 975 kWh monthly usage,
you'll have stable rates for a year with excellent customer service. The 12-month
commitment includes a standard $100 early termination fee.
```

---

## Rate Structure Descriptions

### Fixed Rate

**Template:**
```
{rate}¢ per kWh (fixed)
```

**Example:**
```
8.5¢ per kWh (fixed)
```

**Explanation in Prompt:**
```
with a stable, fixed rate for predictable billing
```

---

### Variable Rate

**Template:**
```
{base_rate}¢ per kWh base rate (variable)
```

**Example:**
```
9.0¢ per kWh base rate (variable)
```

**Explanation in Prompt:**
```
Keep in mind the rate can change month-to-month based on market conditions
```

---

### Tiered Rate

**Template:**
```
tiered pricing based on usage
```

**Example:**
```
tiered pricing: 7.5¢ for first 1000 kWh, then 9.0¢
```

**Explanation in Prompt:**
```
with lower rates for typical usage and higher rates if you exceed your average
```

---

### Time-of-Use Rate

**Template:**
```
time-of-use pricing (different rates for peak/off-peak)
```

**Example:**
```
time-of-use: 6.5¢ off-peak, 12.0¢ peak hours
```

**Explanation in Prompt:**
```
You'll pay less during off-peak hours, which works well with your usage patterns
```

---

## Special Scenarios

### High Early Termination Fee with Break-Even

**Prompt Addition:**
```
<risk_warning>
This plan has a ${etf} early termination fee. However, based on your projected
savings of ${monthly_savings}/month, you'll break even in {break_even_months} months.
</risk_warning>
```

**Example Output:**
```
This plan will save you $450 per year with a competitive fixed rate. There's a $200
early termination fee, but you'll break even in just 6 months, so it's still a great
deal if you stay for at least that long. Based on your 1,100 kWh monthly usage, this
plan offers excellent value.
```

---

### Low Savings Warning

**Prompt Addition:**
```
<context>
The savings from this plan are modest ({savings_pct}%). Consider whether the
administrative effort of switching is worthwhile for this level of savings.
</context>
```

**Example Output:**
```
This plan saves you $45 per year compared to your current plan, which is a modest
3.6% reduction. While the savings are small, you'll also get 60% renewable energy
and a well-rated supplier. Consider whether switching is worth the effort for this
level of savings.
```

---

### Recommend Staying with Current Plan

**Prompt Variation:**
```
You are an energy plan advisor. After analyzing this customer's options, you've
determined they should STAY with their current plan. Explain why switching is not
recommended.

<analysis>
- Potential savings: ${small_savings}
- Switching costs: ${switching_costs}
- Net benefit: ${net_benefit} (negative or very small)
</analysis>

Generate a friendly explanation for why staying is the best choice:
```

**Example Output:**
```
Based on your usage and available plans, staying with your current plan is the best
option. While you could save about $30 per year by switching, the administrative
effort and potential early termination fee on your current plan make it not worth it.
Your current plan is serving you well.
```

---

## Readability Optimization Techniques

### Active Voice

❌ **Passive (Avoid):**
```
Savings of $300 per year will be realized by you.
```

✅ **Active (Use):**
```
You'll save $300 per year.
```

---

### Concrete Numbers

❌ **Abstract (Avoid):**
```
This plan offers substantial savings and significant renewable energy content.
```

✅ **Concrete (Use):**
```
This plan saves you $425 per year and is 75% renewable energy.
```

---

### Simple Words

❌ **Jargon (Avoid):**
```
This energy procurement option leverages predominantly sustainable generation sources.
```

✅ **Simple (Use):**
```
This plan uses mostly renewable energy from wind and solar.
```

---

### Short Sentences

❌ **Long (Avoid):**
```
Notwithstanding the aforementioned early termination fee considerations, this
particular plan demonstrates considerable economic advantages relative to your
current energy service agreement, particularly when evaluated across the projected
twelve-month utilization period.
```

✅ **Short (Use):**
```
This plan saves you $300 per year. There's a $100 early termination fee, but you'll
break even in 4 months. The savings make it worthwhile.
```

---

## Testing Prompts

### Test Different Personas

Run the same plan through different personas to verify personalization:

```python
personas = [
    ("budget_conscious", UserPreferences(cost_priority=60, ...)),
    ("eco_conscious", UserPreferences(renewable_priority=70, ...)),
    ("flexibility_focused", UserPreferences(flexibility_priority=65, ...)),
    ("balanced", UserPreferences(cost_priority=25, ...)),
]

for persona_name, preferences in personas:
    explanation = await service.generate_explanation(
        plan=test_plan,
        user_profile=test_profile,
        preferences=preferences,
    )
    print(f"{persona_name}: {explanation.explanation_text}")
```

**Expected:** Each persona should have noticeably different emphasis and tone.

---

## Prompt Engineering Best Practices

1. **Be Specific:** Include exact requirements (word count, reading level)
2. **Use Examples:** Few-shot learning improves consistency
3. **Use XML Tags:** Structured input helps Claude parse context
4. **Set Tone:** Explicitly state desired tone for each persona
5. **Validate Output:** Check length, readability, specificity
6. **Iterate:** Test with real plans and refine prompts

---

## Monitoring Prompt Performance

Track these metrics to evaluate prompt quality:

- **Readability Score:** Should average >60
- **Length:** Should be 2-3 sentences (100-300 words)
- **Specificity:** Should include actual dollar amounts and percentages
- **Personalization:** Should vary by persona
- **Fallback Rate:** Should be <10% (prompts reliable enough)

---

## Prompt Versioning

When updating prompts:

1. Create new version in code with version number
2. A/B test new vs. old prompts
3. Measure readability and user feedback
4. Gradually roll out if successful
5. Document changes in this file

---

## Cost Optimization

- **Token Usage:** Current prompts use ~1,000 input + 200 output = 1,200 total tokens
- **Cost per Explanation:** ~$0.003 (Claude Sonnet 3.5 pricing)
- **Optimization:** Shorter prompts without quality loss can reduce costs

---

**End of Document**
