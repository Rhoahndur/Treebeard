# TreeBeard - Agent Coordination Guide
**Multi-Agent Development Playbook**

---

## Overview

This guide establishes protocols for coordinating multiple AI subagents (and human developers) working in parallel on the TreeBeard project. The goal is to maximize parallelization while preventing integration failures, duplicated work, and communication gaps.

---

## Agent Types & Specializations

### Backend Development Agents (Backend Dev #1-8)
**Specialization Areas:**
- **Data/DB Specialist:** Database schema, ETL, data validation
- **Algorithm Specialist:** Recommendation engine, scoring, matching
- **API Specialist:** REST endpoints, authentication, rate limiting
- **Integration Specialist:** Service integration, third-party APIs

**Assignment Strategy:**
- Assign agents to streams based on expertise
- Rotate agents between sprints to build broader context
- Pair senior/junior agents on complex integrations

---

### Frontend Development Agents (Frontend Dev #1-5)
**Specialization Areas:**
- **Design System Specialist:** Components, Storybook, theming
- **Form/UX Specialist:** Complex forms, validation, user flows
- **Visualization Specialist:** Charts, dashboards, data viz
- **Accessibility Specialist:** A11y, WCAG compliance, screen readers

**Assignment Strategy:**
- Assign design system work to most experienced frontend agent
- Distribute feature work across agents with clear boundaries
- Centralize accessibility reviews with specialist

---

### DevOps Agents (DevOps #1-2)
**Specialization Areas:**
- **Infrastructure:** Terraform, K8s, cloud resources
- **Observability:** Monitoring, logging, alerting, APM
- **Performance:** Caching, CDN, optimization

**Assignment Strategy:**
- DevOps #1: Infrastructure and performance
- DevOps #2: Observability and security

---

### Specialized Agents
- **ML Engineer:** Claude API integration, NLG, prompt engineering
- **Data Analyst:** Analytics, dashboards, business metrics
- **Security Engineer:** Security audit, penetration testing
- **QA Engineer:** Test strategy, end-to-end testing
- **UX Designer:** Wireframes, user research (supporting role)

---

## Communication Protocols

### Daily Async Standup
**Platform:** Slack #treebeard-daily
**Time:** 9 AM local time (each agent posts)
**Format:**
```
🤖 Agent: Backend Dev #3
📅 Date: 2025-11-15

✅ YESTERDAY:
- Completed Story 2.1 (Scoring Algorithm)
- Published `CompositeScore` schema to #treebeard-contracts

🎯 TODAY:
- Starting Story 2.2 (Plan Matching)
- Will need `UserProfile` schema from Backend Dev #2

🚧 BLOCKERS:
- None

📊 Sprint Progress: 3/8 stories complete
```

**Rules:**
- Post by 10 AM or within 1 hour of starting work
- Tag dependencies (@Backend Dev #2, @Frontend Dev #1)
- Update blockers immediately when they arise

---

### Integration Checkpoints (Mid-Sprint)
**Platform:** Zoom/Meet (synchronous)
**Cadence:** Wednesday mid-sprint
**Duration:** 30 minutes
**Attendees:** Agents on dependent streams only

**Agenda Template:**
```
1. Interface Contract Review (10 min)
   - Have any schemas/APIs changed?
   - Are mocks still accurate?

2. Integration Blocker Discussion (10 min)
   - Any discovered incompatibilities?
   - Data format mismatches?

3. Joint Testing Plan (10 min)
   - When will we integration test?
   - Who writes the tests?
   - What scenarios to cover?
```

**Output:** Updated integration test plan in `docs/integration-tests/sprint-N.md`

---

### Sprint Planning (Bi-weekly)
**Platform:** Zoom/Meet (synchronous)
**Cadence:** First Monday of sprint
**Duration:** 2 hours
**Attendees:** All active agents + SM + PM

**Agenda:**
```
1. Sprint Review (30 min)
   - Demo completed work
   - Discuss what went well / challenges

2. Story Assignment (45 min)
   - Assign stories to agents
   - Identify dependencies
   - Confirm story points

3. Integration Planning (30 min)
   - Map handoff points
   - Schedule mid-sprint checkpoint
   - Define interface contracts

4. Risk Assessment (15 min)
   - Technical risks
   - Resource risks
   - Schedule risks
```

**Output:**
- `docs/sprints/sprint-N-plan.md`
- Updated agent assignments in GitHub Project
- Scheduled integration checkpoint

---

### Handoff Protocol

When completing a story that other agents depend on:

#### Step 1: Publish Interface Contract
**Location:** `docs/contracts/{story-id}-contract.md`

**Template:**
```markdown
# Story X.Y Interface Contract

## Story: [Story Name]
**Owner:** Backend Dev #3
**Completed:** 2025-11-15
**Consumers:** Backend Dev #4 (Story 2.4), Frontend Dev #1 (Story 4.2)

---

## Published Interfaces

### Data Schema
\`\`\`python
from pydantic import BaseModel
from typing import List
from uuid import UUID

class RankedPlan(BaseModel):
    """A plan with its composite score and ranking"""
    plan_id: UUID
    rank: int  # 1, 2, or 3
    composite_score: float  # 0-100
    cost_score: float
    flexibility_score: float
    renewable_score: float
    rating_score: float

class RecommendationResult(BaseModel):
    """Complete recommendation output"""
    user_id: UUID
    top_plans: List[RankedPlan]
    generated_at: datetime
\`\`\`

### API Endpoint (if applicable)
N/A (internal service)

### Mock Implementation
\`\`\`python
# Use this mock for development before integration
def mock_recommendation_result(user_id: UUID) -> RecommendationResult:
    return RecommendationResult(
        user_id=user_id,
        top_plans=[
            RankedPlan(plan_id=UUID(...), rank=1, composite_score=85.5, ...),
            RankedPlan(plan_id=UUID(...), rank=2, composite_score=82.3, ...),
            RankedPlan(plan_id=UUID(...), rank=3, composite_score=78.1, ...)
        ],
        generated_at=datetime.now()
    )
\`\`\`

---

## Integration Points

### Backend Dev #4 (Story 2.4 - Savings Calculator)
**What they need:** `RecommendationResult` with top 3 plans
**How to integrate:**
\`\`\`python
from recommendation.engine import get_recommendations

result = get_recommendations(user_id, usage_profile, preferences)
# result is RecommendationResult with top_plans
\`\`\`

**Test coverage:** 95% (unit tests in `tests/recommendation/test_engine.py`)

### Frontend Dev #1 (Story 4.2 - Plan Card)
**What they need:** API response matching `RecommendationResult` schema
**How to integrate:** Call `GET /api/v1/recommendations/{userId}`
**Sample response:** See `docs/api-samples/recommendation-response.json`

---

## Known Limitations
- Current implementation does not handle ties in composite scores (uses plan_id alphabetical sort as tiebreaker)
- Variable rate plans show expected cost only, no confidence intervals yet (coming in Story 6.1)

---

## Testing
**Unit tests:** `tests/recommendation/test_engine.py` (23 tests, 95% coverage)
**Integration tests:** TBD (scheduled for Sprint 5 end)
**Performance:** Processes 1000 plans in <500ms

---

## Next Steps for Consumers
1. Review schema and mock implementation
2. Start development using mock
3. Schedule integration testing (Friday Week 10)
4. Replace mock with real implementation
```

---

#### Step 2: Announce in Slack
Post in #treebeard-handoffs:
```
✅ Story 2.2 COMPLETE: Plan Matching & Ranking

📄 Contract: docs/contracts/story-2.2-contract.md
🎯 Consumers: @Backend Dev #4, @Frontend Dev #1
🧪 Mock available: recommendation.mocks.mock_recommendation_result()
📅 Integration testing: Friday 11/22

Questions? Reply here or DM me!
```

---

#### Step 3: Update Dependencies
Create PR to update:
- `docs/execution-plan.md` (mark story complete)
- `docs/sprint-plan.md` (update sprint progress)
- GitHub Project board (move card to "Done")

---

## Conflict Resolution

### Schema Conflicts
**Problem:** Two agents modify the same data schema

**Resolution Protocol:**
1. **Detect:** CI fails with schema validation error
2. **Discuss:** Agents meet synchronously (30 min max)
3. **Decide:** Senior agent or Architect makes final call
4. **Document:** Update contract with decision rationale
5. **Migrate:** Both agents update their code to match

**Example:**
```
Backend Dev #3 changed `CompositeScore` to have 5 factors
Backend Dev #4 expects 4 factors (old schema)
→ Meet, decide on 5 factors, update Story 2.4 code
```

---

### Integration Test Failures
**Problem:** Integration test fails when merging two streams

**Resolution Protocol:**
1. **Isolate:** Determine which component is incorrect
2. **Negotiate:** Agents discuss expected behavior
3. **Fix:** Owner updates code or contract (whichever was wrong)
4. **Re-test:** Joint testing session
5. **Document:** Add regression test to prevent recurrence

---

### Blocking Dependencies
**Problem:** Agent is blocked waiting for another agent

**Resolution Protocol:**
1. **Immediate:** Post in #treebeard-blockers with @mention
2. **Within 2 hours:** Blocking agent responds with ETA
3. **If ETA > 1 day:** SM reassigns story or creates temporary workaround
4. **Fallback:** Use mock implementation to unblock

**Example:**
```
@Backend Dev #2: I'm blocked on Story 2.4 waiting for UserProfile schema from Story 1.4.
When can you publish the contract?

@Backend Dev #2 responds: Will publish by EOD today (5 PM). Here's a draft:
[paste schema]

Unblocked! Backend Dev #4 can proceed with draft schema.
```

---

## Integration Testing Strategy

### Contract Tests (Between Services)
**Owner:** Consumer agent (the one depending on the interface)
**Location:** `tests/contracts/`

**Example:**
```python
# tests/contracts/test_recommendation_savings_contract.py
# Owner: Backend Dev #4 (consumes Story 2.2 output)

import pytest
from recommendation.engine import get_recommendations
from savings.calculator import calculate_savings

def test_recommendation_output_schema():
    """Verify Story 2.2 outputs match expected schema"""
    result = get_recommendations(user_id=..., ...)

    # Contract: RecommendationResult must have these fields
    assert hasattr(result, 'top_plans')
    assert len(result.top_plans) == 3
    assert all(hasattr(plan, 'composite_score') for plan in result.top_plans)

def test_savings_can_consume_recommendation():
    """Integration: Story 2.4 can use Story 2.2 output"""
    result = get_recommendations(user_id=..., ...)

    # Should not raise exception
    savings = calculate_savings(result.top_plans[0], current_plan=...)

    assert savings.annual_savings > 0 or savings.annual_savings < 0  # valid number
```

**Run:** On every PR that touches either service

---

### Joint Integration Tests (Full Flow)
**Owner:** Both agents collaborate
**Location:** `tests/integration/`

**Example:**
```python
# tests/integration/test_recommendation_flow.py
# Owners: Backend Dev #3 + Backend Dev #4

def test_complete_recommendation_flow():
    """End-to-end: User data → Recommendations → Savings"""
    # Setup
    user = create_test_user()
    usage_data = create_test_usage_data(user_id=user.id)

    # Story 2.2: Get recommendations
    recs = get_recommendations(user.id, usage_data, default_preferences())
    assert len(recs.top_plans) == 3

    # Story 2.4: Calculate savings for each
    for plan in recs.top_plans:
        savings = calculate_savings(plan, user.current_plan)
        assert savings.annual_savings is not None
        assert savings.monthly_breakdown is not None

    # Verify consistency
    assert recs.top_plans[0].composite_score >= recs.top_plans[1].composite_score
```

**Run:** At end of sprint before merging to main

---

### Load Integration Tests (Performance)
**Owner:** DevOps
**Location:** `tests/load/`

**Tool:** Locust or k6

**Example:**
```python
# tests/load/test_recommendation_load.py

from locust import HttpUser, task, between

class RecommendationUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_recommendation(self):
        self.client.post("/api/v1/recommendations/generate", json={
            "user_id": self.generate_user_id(),
            "usage_data": self.mock_usage_data(),
            "preferences": {"cost": 40, "flexibility": 30, ...}
        })
```

**Run:** Sprint 11 (week 22)
**Target:** 10,000 concurrent users, P95 response time <2s

---

## Parallel Work Coordination

### Example: Sprint 9-10 (4 Concurrent Streams)

#### Monday (Sprint Start)
- **9-11 AM:** Sprint planning (all agents)
- **11 AM:** Agents post initial standups
- **11 AM - 5 PM:** Development begins

**Coordination:**
```
Frontend Dev #1 (Stream 4): Starting Story 4.2 (Plan Cards)
→ Needs API response format
→ Backend Dev #5 publishes mock API response (from Sprint 8 contract)
→ Frontend Dev #1 unblocked, proceeds with mock data

Frontend Dev #2 (Stream 5): Starting Story 5.1 (Form Framework)
→ No dependencies, proceeds independently

Frontend Dev #3 (Stream 4C): Starting Story 4.6 (Accessibility)
→ Waits for Story 4.3 (Results Page) from Frontend Dev #1
→ Uses Storybook to start with isolated components
→ Will integrate when 4.3 is ready (Thursday)

Backend Dev #7 (Stream 6): Starting Story 6.1 (Risk Rules)
→ Depends on Epic 2 (complete in Sprint 6)
→ Proceeds independently
```

---

#### Wednesday (Mid-Sprint Checkpoint)
**Integration Sync:**
- Frontend Dev #1 + Backend Dev #5: Verify API contract still valid
- Frontend Dev #1 + Frontend Dev #3: Plan accessibility integration (4.3 → 4.6)

**Status:**
- Stream 4: 60% done
- Stream 5: 50% done
- Stream 4C: 30% done (blocked until Thursday)
- Stream 6: 70% done

---

#### Thursday (Integration Day)
- Frontend Dev #1 completes Story 4.3 (Results Page)
- Frontend Dev #3 integrates Story 4.6 (Accessibility) with 4.3
- Joint testing between Dev #1 and #3

---

#### Friday (Sprint End)
- All streams complete their stories
- Integration testing (if needed)
- Sprint review / Demo
- Retrospective

---

## Tooling & Automation

### GitHub Project Board
**Columns:**
- Backlog
- Ready (dependencies met)
- In Progress
- In Review
- Testing
- Done

**Automation:**
- PR opened → moves to "In Review"
- PR merged → moves to "Testing"
- Integration tests pass → moves to "Done"

**Agent Responsibilities:**
- Update card daily with progress comments
- Tag dependencies ("Blocked by #42")
- Assign yourself when starting work

---

### Contract Registry
**Location:** `docs/contracts/README.md`

**Purpose:** Central registry of all published interfaces

**Format:**
```markdown
# Interface Contract Registry

| Story | Owner | Published | Schema | Consumers |
|-------|-------|-----------|--------|-----------|
| 1.4 | Backend Dev #2 | 2025-11-08 | [UserProfile](story-1.4-contract.md) | Story 2.1, 2.2 |
| 2.2 | Backend Dev #3 | 2025-11-15 | [RecommendationResult](story-2.2-contract.md) | Story 2.4, 4.2 |
| 3.2 | Backend Dev #5 | 2025-11-22 | [API Spec](story-3.2-contract.md) | Story 4.2, 5.6 |
```

**Update:** Automatically via PR (add entry when publishing contract)

---

### Shared Mocks Library
**Location:** `src/mocks/` (for dev) and `tests/mocks/` (for testing)

**Purpose:** Provide consistent mocks for all agents

**Example:**
```python
# src/mocks/recommendation_mocks.py

def mock_user_profile(user_type='baseline'):
    """Mock user profile for testing

    Args:
        user_type: 'baseline', 'high', 'variable', or 'seasonal'
    """
    profiles = {
        'baseline': UserProfile(
            user_id=UUID('...'),
            monthly_avg=500,
            seasonal_variance=0.1,
            profile_type='baseline'
        ),
        'high': UserProfile(...),
        ...
    }
    return profiles[user_type]
```

**Usage:**
```python
from mocks.recommendation_mocks import mock_user_profile

# Backend Dev #4 can develop Story 2.4 before Story 1.4 is complete
profile = mock_user_profile('baseline')
result = get_recommendations(user_id, profile, ...)
```

---

## Best Practices

### For Backend Agents
1. **Publish schemas early:** Don't wait until story is 100% done
2. **Version your APIs:** Use `/api/v1/` to allow future changes
3. **Write contract tests:** Ensure consumers can rely on your output
4. **Document edge cases:** What happens with null values, empty arrays?
5. **Provide mock data:** Make it easy for others to develop against your code

### For Frontend Agents
1. **Use TypeScript interfaces:** Match backend schemas exactly
2. **Handle loading/error states:** Don't assume API always succeeds
3. **Test with mock data:** Don't wait for real backend integration
4. **Component isolation:** Use Storybook to develop components independently
5. **Accessibility first:** Don't bolt on A11y later

### For DevOps Agents
1. **Infrastructure as Code:** Everything in Terraform/config
2. **Document environments:** How to access dev, staging, prod
3. **Automate deploys:** No manual steps
4. **Monitor from day 1:** Don't wait until production to add monitoring
5. **Security by default:** Enable security features from the start

### For All Agents
1. **Commit often:** Small, focused commits with clear messages
2. **Test before PR:** Run all tests locally
3. **Review thoroughly:** Review other agents' PRs carefully
4. **Communicate early:** Don't wait until standup to mention blockers
5. **Document decisions:** Use ADRs for architectural choices

---

## Escalation Path

### Level 1: Agent-to-Agent (Direct)
**When:** Simple questions, clarifications
**How:** Slack DM or mention in #treebeard-daily
**Response Time:** <2 hours

**Example:** "Hey @Frontend Dev #1, what format do you need for the date field?"

---

### Level 2: Stream Lead (Technical)
**When:** Technical disagreements, integration issues
**How:** Post in #treebeard-tech-questions, tag stream leads
**Response Time:** <4 hours

**Example:** "We have a schema conflict between Story 2.2 and 2.4. @Stream-Lead-2A and @Stream-Lead-2B, can you help resolve?"

---

### Level 3: Scrum Master (Process)
**When:** Blockers lasting >1 day, resource issues
**How:** Post in #treebeard-blockers, tag @SM
**Response Time:** <24 hours (or next business day)

**Example:** "@SM: Backend Dev #3 is blocked waiting for Story 1.4 which is delayed. Can we re-prioritize or bring in another agent?"

---

### Level 4: Product Manager / Tech Lead (Strategic)
**When:** Scope changes, requirement conflicts
**How:** Schedule synchronous meeting, tag @PM or @Tech-Lead
**Response Time:** <2 business days

**Example:** "The PRD says we need 5 scoring factors, but Epic 2 only implements 4. @PM: Should we update the PRD or add the 5th factor?"

---

## Agent Onboarding

### New Agent Joins Project

#### Day 1: Context & Setup
- [ ] Read PRD.md, architecture.md, execution-plan.md
- [ ] Read this coordination guide
- [ ] Clone repository, setup local environment
- [ ] Run all tests to verify setup
- [ ] Introduce yourself in #treebeard-general

#### Day 2: Codebase Tour
- [ ] Review existing contracts in `docs/contracts/`
- [ ] Read code in your assigned epic
- [ ] Run specific tests for your epic
- [ ] Ask questions in #treebeard-questions

#### Day 3: First Task
- [ ] Pick a small, low-dependency story (marked "good first story")
- [ ] Read handoff contract for dependencies
- [ ] Start development with mocks
- [ ] Post first standup

#### Week 1 Goal
- [ ] Complete first story
- [ ] Submit first PR
- [ ] Participate in integration sync
- [ ] Attend sprint planning

---

## Metrics & Success Criteria

### Agent Productivity
- **Story completion rate:** Target 2 stories/sprint/agent
- **PR cycle time:** <2 days from open to merge
- **Rework rate:** <15% (stories needing major changes after review)

### Collaboration Quality
- **Integration test success:** >85% pass rate on first run
- **Contract stability:** <10% of contracts require breaking changes
- **Handoff smoothness:** <20% of handoffs result in blockers

### Communication Health
- **Standup participation:** 100% daily (excluding PTO)
- **Blocker response time:** <2 hours average
- **Meeting attendance:** >90% for required meetings

---

## Appendix: Quick Reference

### Key Slack Channels
- `#treebeard-daily` - Daily standups
- `#treebeard-blockers` - Urgent blocks
- `#treebeard-handoffs` - Contract publications
- `#treebeard-questions` - Technical Q&A
- `#treebeard-general` - General discussion

### Key Documents
- `docs/execution-plan.md` - Epics, stories, dependencies
- `docs/sprint-plan.md` - Sprint schedule, agent assignments
- `docs/contracts/` - All interface contracts
- `docs/integration-tests/` - Integration test plans

### Key Commands
```bash
# Run all tests
npm test              # Frontend
pytest                # Backend

# Run specific epic tests
pytest tests/epic1/
npm test -- epic4

# Check code coverage
pytest --cov
npm test -- --coverage

# Run integration tests
pytest tests/integration/
npm run test:integration
```

---

**End of Agent Coordination Guide**

This guide provides the operational framework for managing multi-agent parallelized development on the TreeBeard project.
