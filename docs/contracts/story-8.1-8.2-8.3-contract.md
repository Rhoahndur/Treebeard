# Epic 8 Stories 8.1-8.3: User Feedback System - Contract

**Wave 5: Final Polish - User Feedback Collection**

**Author:** Fullstack Dev #1
**Date:** 2025-11-10
**Status:** Implemented ✅

---

## Overview

This contract defines the complete user feedback system for TreeBeard, including UI components for collecting feedback, API endpoints for submission and analytics, and an admin dashboard for monitoring feedback trends.

### Stories Implemented

- **Story 8.1:** Feedback Collection UI
- **Story 8.2:** Feedback API Endpoints
- **Story 8.3:** Feedback Analytics Dashboard

---

## API Endpoints

### Public Endpoints (No Auth Required)

#### 1. Submit Plan Feedback

**Endpoint:** `POST /api/v1/feedback/plan`

**Purpose:** Submit feedback on a specific energy plan

**Request Body:**
```json
{
  "plan_id": "uuid",
  "recommendation_id": "uuid (optional)",
  "rating": 1-5,
  "feedback_text": "string (optional, max 500 chars)",
  "feedback_type": "helpful | not_helpful | selected | did_not_select | other"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Thank you for your feedback!",
  "feedback_id": "uuid"
}
```

**Rate Limit:** 10 submissions per user per day

**Error Responses:**
- `400` - Validation error (invalid rating, text too long)
- `429` - Rate limit exceeded

---

#### 2. Submit Recommendation Feedback

**Endpoint:** `POST /api/v1/feedback/recommendation`

**Purpose:** Submit feedback on the overall recommendation experience

**Request Body:**
```json
{
  "recommendation_id": "uuid",
  "plan_id": "uuid (optional)",
  "rating": 1-5,
  "feedback_text": "string (optional, max 500 chars)",
  "feedback_type": "helpful | not_helpful | selected | did_not_select | other"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Thank you for your feedback!",
  "feedback_id": "uuid"
}
```

**Rate Limit:** 10 submissions per user per day

---

### Admin Endpoints (Require Admin Auth)

#### 3. Get Feedback Statistics

**Endpoint:** `GET /api/v1/feedback/stats`

**Purpose:** Get aggregated feedback statistics

**Response:** `200 OK`
```json
{
  "total_feedback_count": 1523,
  "average_rating": 4.2,
  "thumbs_up_count": 1203,
  "thumbs_down_count": 145,
  "neutral_count": 175,
  "text_feedback_count": 823,
  "sentiment_breakdown": {
    "positive": 1180,
    "neutral": 218,
    "negative": 125
  }
}
```

---

#### 4. Get Comprehensive Analytics

**Endpoint:** `GET /api/v1/admin/feedback/analytics`

**Purpose:** Get complete feedback analytics including time-series and plan breakdowns

**Response:** `200 OK`
```json
{
  "stats": {
    "total_feedback_count": 1523,
    "average_rating": 4.2,
    "thumbs_up_count": 1203,
    "thumbs_down_count": 145,
    "neutral_count": 175,
    "text_feedback_count": 823,
    "sentiment_breakdown": {
      "positive": 1180,
      "neutral": 218,
      "negative": 125
    }
  },
  "time_series": [
    {
      "date": "2025-10-11",
      "count": 45,
      "average_rating": 4.3
    }
    // ... 30 days
  ],
  "top_plans": [
    {
      "plan_id": "uuid",
      "plan_name": "Green Energy Fixed 12",
      "supplier_name": "TXU Energy",
      "total_feedback": 234,
      "average_rating": 4.5,
      "thumbs_up_count": 201,
      "thumbs_down_count": 33,
      "most_recent_feedback": "2025-11-10T12:34:56Z"
    }
    // ... top 10
  ],
  "recent_text_feedback": [
    {
      "id": "uuid",
      "user_id": "uuid or null",
      "recommendation_id": "uuid or null",
      "plan_id": "uuid or null",
      "rating": 5,
      "feedback_text": "Great plan, excellent rates!",
      "feedback_type": "helpful",
      "sentiment_score": 0.87,
      "created_at": "2025-11-10T12:34:56Z"
    }
    // ... 20 most recent
  ]
}
```

---

#### 5. Search Feedback

**Endpoint:** `GET /api/v1/admin/feedback/search`

**Purpose:** Search and filter feedback submissions

**Query Parameters:**
- `plan_id` (optional): Filter by plan UUID
- `min_rating` (optional): Minimum rating (1-5)
- `max_rating` (optional): Maximum rating (1-5)
- `has_text` (optional): Filter by text presence (true/false)
- `sentiment` (optional): Filter by sentiment (positive/neutral/negative)
- `start_date` (optional): Start date (ISO 8601)
- `end_date` (optional): End date (ISO 8601)
- `limit` (optional): Results per page (default: 100, max: 1000)
- `offset` (optional): Pagination offset (default: 0)

**Response:** `200 OK`
```json
{
  "results": [
    {
      "id": "uuid",
      "user_id": "uuid or null",
      "recommendation_id": "uuid or null",
      "plan_id": "uuid or null",
      "rating": 4,
      "feedback_text": "Good plan overall",
      "feedback_type": "helpful",
      "sentiment_score": 0.65,
      "created_at": "2025-11-10T12:34:56Z"
    }
  ],
  "total_count": 543,
  "limit": 100,
  "offset": 0
}
```

---

#### 6. Export Feedback CSV

**Endpoint:** `GET /api/v1/admin/feedback/export`

**Purpose:** Export all feedback data to CSV format

**Response:** `200 OK`
- Content-Type: `text/csv`
- Content-Disposition: `attachment; filename=feedback_export_{admin_id}.csv`

**CSV Columns:**
- Feedback ID
- User ID (or "Anonymous")
- Recommendation ID
- Plan ID
- Plan Name
- Supplier Name
- Rating
- Feedback Type
- Feedback Text
- Sentiment Score
- Created At

---

## Frontend Components

### 1. FeedbackWidget

**Location:** `/src/frontend/src/components/FeedbackWidget/FeedbackWidget.tsx`

**Purpose:** Collect user feedback with thumbs up/down and optional text

**Props:**
```typescript
interface FeedbackWidgetProps {
  planId?: string;              // For plan-specific feedback
  recommendationId?: string;    // For overall recommendation feedback
  onSuccess?: () => void;       // Callback on successful submission
  onError?: (error: string) => void;  // Callback on error
  compact?: boolean;            // Compact mode with minimal UI
  className?: string;           // Custom CSS class
}
```

**Features:**
- Thumbs up/down buttons (accessible, keyboard navigable)
- Expandable text feedback textarea (500 char limit)
- Character counter with visual feedback
- Loading state during submission
- Success confirmation message
- Error handling with retry option
- WCAG 2.1 AA compliant

**Usage:**
```tsx
<FeedbackWidget
  planId="plan-123"
  recommendationId="rec-456"
  onSuccess={() => console.log('Feedback submitted!')}
  compact={false}
/>
```

---

### 2. FeedbackStats

**Location:** `/src/frontend/src/components/FeedbackAnalytics/FeedbackStats.tsx`

**Purpose:** Display aggregated feedback statistics in cards

**Props:**
```typescript
interface FeedbackStatsProps {
  stats: FeedbackStats;
  className?: string;
}
```

**Features:**
- 4 stat cards: Total Feedback, Average Rating, Positive, Negative
- Color-coded by variant (success, danger, neutral)
- Satisfaction rate calculation
- Sentiment breakdown display

---

### 3. FeedbackChart

**Location:** `/src/frontend/src/components/FeedbackAnalytics/FeedbackChart.tsx`

**Purpose:** Time-series visualization of feedback volume and ratings

**Props:**
```typescript
interface FeedbackChartProps {
  data: FeedbackTimeSeriesPoint[];
  className?: string;
}
```

**Features:**
- Bar chart for daily feedback volume
- Line chart for average rating trend
- Last 30 days of data
- Interactive tooltips
- Responsive design using Recharts

---

### 4. FeedbackTable

**Location:** `/src/frontend/src/components/FeedbackAnalytics/FeedbackTable.tsx`

**Purpose:** Display plan-level feedback aggregation in sortable table

**Props:**
```typescript
interface FeedbackTableProps {
  plans: PlanFeedbackAggregation[];
  className?: string;
}
```

**Features:**
- Sortable columns (plan name, total feedback, average rating)
- Color-coded average ratings
- Thumbs up/down counts with satisfaction percentage
- Last updated timestamp
- Empty state handling

---

### 5. FeedbackDashboard (Page)

**Location:** `/src/frontend/src/pages/FeedbackDashboard.tsx`

**Purpose:** Admin-only comprehensive feedback analytics dashboard

**Features:**
- Overview stats cards
- Time-series charts (volume and rating trends)
- Plan feedback table (top 10 most-reviewed)
- Recent text feedback list with search and sentiment filter
- CSV export functionality
- Loading and error states
- Admin role protection

**Access:** Admin users only (role check via existing auth system)

---

## Custom Hooks

### useFeedback

**Location:** `/src/frontend/src/hooks/useFeedback.ts`

**Purpose:** Handle feedback submission with error handling and retry logic

**API:**
```typescript
function useFeedback(options?: UseFeedbackOptions): UseFeedbackReturn

interface UseFeedbackOptions {
  onSuccess?: (response: FeedbackSubmissionResponse) => void;
  onError?: (error: string) => void;
  maxRetries?: number;  // Default: 2
}

interface UseFeedbackReturn {
  submitPlanFeedback: (data: PlanFeedbackData) => Promise<void>;
  submitRecommendationFeedback: (data: RecommendationFeedbackData) => Promise<void>;
  isSubmitting: boolean;
  error: string | null;
  isSuccess: boolean;
  reset: () => void;
}
```

**Features:**
- Automatic retry with exponential backoff (1s, 2s, 4s...)
- No retry on rate limit (429) or validation errors (400, 422)
- User-friendly error messages
- Loading and success state management

---

### useThumbsFeedback

**Location:** `/src/frontend/src/hooks/useFeedback.ts`

**Purpose:** Simplified hook for thumbs up/down feedback

**API:**
```typescript
function useThumbsFeedback(options: {
  planId?: string;
  recommendationId?: string;
  onSuccess?: () => void;
  onError?: (error: string) => void;
})

// Returns
{
  submitThumbsFeedback: (isPositive: boolean, feedbackText?: string) => Promise<void>;
  isSubmitting: boolean;
  error: string | null;
}
```

---

## TypeScript Interfaces

### Core Types

```typescript
type FeedbackRating = 1 | 2 | 3 | 4 | 5;

type FeedbackType =
  | 'helpful'
  | 'not_helpful'
  | 'selected'
  | 'did_not_select'
  | 'other';

type SentimentType = 'positive' | 'neutral' | 'negative';

interface PlanFeedbackData {
  plan_id: string;
  recommendation_id?: string;
  rating: FeedbackRating;
  feedback_text?: string;
  feedback_type: FeedbackType;
}

interface RecommendationFeedbackData {
  recommendation_id: string;
  plan_id?: string;
  rating: FeedbackRating;
  feedback_text?: string;
  feedback_type: FeedbackType;
}

interface FeedbackSubmissionResponse {
  success: boolean;
  message: string;
  feedback_id: string;
}
```

**Full type definitions:** `/src/frontend/src/types/feedback.ts`

---

## Integration Points

### 1. PlanCard Component

**File:** `/src/frontend/src/components/PlanCard/PlanCard.tsx`

**Changes:**
- Added `recommendationId?: string` prop
- Imported `FeedbackWidget`
- Added `<FeedbackWidget>` at bottom of card content

**Usage:**
```tsx
<PlanCard
  plan={plan}
  onSelect={setSelectedPlan}
  isSelected={selectedPlan?.plan_id === plan.plan_id}
  showRank={true}
  recommendationId={recommendation.recommendation_id}
/>
```

---

### 2. ResultsPage Component

**File:** `/src/frontend/src/pages/ResultsPage.tsx`

**Changes:**
- Imported `FeedbackWidget`
- Added page-level feedback widget after cost breakdown
- Passed `recommendationId` to all `PlanCard` components

**Page-level Widget:**
```tsx
<div className="bg-white rounded-lg shadow-card p-6 mb-8">
  <h3 className="text-lg font-semibold text-gray-900 mb-4">
    How was your experience?
  </h3>
  <FeedbackWidget
    recommendationId={recommendation.recommendation_id}
    compact={false}
  />
</div>
```

---

### 3. Backend Main Application

**File:** `/src/backend/api/main.py`

**Changes:**
- Imported `feedback` router
- Added router inclusion:
  ```python
  app.include_router(
      feedback.router,
      prefix=settings.api_v1_prefix,
      tags=["Feedback"]
  )
  ```

---

## Database Schema

### Feedback Model

**Location:** `/src/backend/models/feedback.py` (already exists)

**Table:** `feedback`

**Columns:**
- `id` (UUID, PK)
- `user_id` (UUID, FK to users, nullable for anonymous)
- `recommendation_id` (UUID, FK to recommendations, nullable)
- `recommended_plan_id` (UUID, FK to recommendation_plans, nullable)
- `plan_id` (UUID, FK to plan_catalog, nullable)
- `rating` (Integer, 1-5)
- `feedback_text` (Text, nullable)
- `feedback_type` (String, 50)
- `sentiment_score` (Decimal, nullable, -1.0 to 1.0)
- `created_at` (DateTime with timezone)

**Indexes:**
- `idx_feedback_user_created` (user_id, created_at)
- `idx_feedback_recommendation` (recommendation_id, created_at)
- `idx_feedback_plan` (plan_id)
- `idx_feedback_rating` (rating)

---

## Business Logic

### Sentiment Analysis

**Location:** `/src/backend/services/feedback_service.py`

**Algorithm:** Basic keyword detection

**Positive Keywords:** great, excellent, love, perfect, amazing, wonderful, best, fantastic, helpful, satisfied, recommend, good, happy, pleased, awesome, brilliant, super

**Negative Keywords:** bad, terrible, worst, hate, awful, horrible, poor, disappointed, frustrating, confusing, unclear, expensive, complicated, difficult, unhappy, dissatisfied, useless

**Scoring:**
- Sentiment Score = (positive_count - negative_count) / total_keywords
- Range: -1.0 (most negative) to 1.0 (most positive)
- Classification:
  - Positive: score > 0.3
  - Neutral: -0.3 ≤ score ≤ 0.3
  - Negative: score < -0.3

---

## Rate Limiting

**Implementation:** Custom rate limiter in `/src/backend/services/feedback_service.py`

**Limits:**
- 10 feedback submissions per authenticated user per day
- Tracked by user_id and date (UTC)
- Anonymous submissions bypass user-based rate limiting (rely on IP-based middleware rate limiting)

**Enforcement:**
- Check rate limit before creating feedback
- Return `429 Too Many Requests` if exceeded
- Reset counter at start of each day (UTC)

---

## Testing

### Backend Tests

**Location:** `/tests/backend/test_feedback_api.py`

**Test Coverage:**
- Plan feedback submission (authenticated and anonymous)
- Recommendation feedback submission
- Validation errors (invalid rating, text too long)
- Rate limiting enforcement
- Admin-only endpoints (stats, analytics, search, export)
- CSV export format
- Search filters

**Run Tests:**
```bash
pytest tests/backend/test_feedback_api.py -v
```

---

### Frontend Tests

**Location:** `/tests/frontend/components/FeedbackWidget.test.tsx`

**Test Coverage:**
- Component rendering (plan vs recommendation questions)
- Thumbs up/down interaction
- Form expansion and collapse
- Text feedback input and character counting
- Character limit validation
- Form submission (plan and recommendation)
- Loading states
- Success and error states
- Cancel functionality
- Accessibility (ARIA labels, keyboard navigation)
- Callback invocation (onSuccess, onError)

**Run Tests:**
```bash
npm test FeedbackWidget.test.tsx
```

---

## Analytics Metrics

### Key Metrics

1. **Total Feedback Count:** Total number of feedback submissions
2. **Average Rating:** Mean rating across all feedback (1-5 scale)
3. **Satisfaction Rate:** (Thumbs Up Count / Total Feedback) × 100
4. **Rating Distribution:**
   - Thumbs Up: Rating ≥ 4
   - Neutral: Rating = 3
   - Thumbs Down: Rating ≤ 2
5. **Text Feedback Rate:** (Text Feedback Count / Total Feedback) × 100
6. **Sentiment Breakdown:** Positive / Neutral / Negative counts

### Time-Series Metrics

- **Daily Feedback Volume:** Count of feedback per day (last 30 days)
- **Average Rating Trend:** Daily average rating (last 30 days)

### Plan-Level Metrics

- **Total Feedback per Plan:** Ranked by volume
- **Average Rating per Plan:** Plan quality indicator
- **Satisfaction Rate per Plan:** Plan-specific thumbs up percentage
- **Most Recent Feedback:** Last feedback timestamp per plan

---

## Accessibility Compliance (WCAG 2.1 AA)

### FeedbackWidget

✅ **Keyboard Navigation:**
- All buttons focusable via Tab
- Enter/Space to activate buttons
- Form fields accessible via Tab

✅ **ARIA Labels:**
- `role="region"` with `aria-label="Feedback form"`
- `aria-label` on thumbs buttons ("Thumbs up - helpful", "Thumbs down - not helpful")
- `aria-pressed` state on selected thumb
- `aria-describedby` linking textarea to character count

✅ **Color Contrast:**
- All text meets minimum 4.5:1 contrast ratio
- Button states clearly distinguishable

✅ **Focus Indicators:**
- Visible focus rings on all interactive elements
- `focus:ring-2 focus:ring-primary-500` on buttons

✅ **Screen Reader Support:**
- Success/error messages have `role="alert"` and `aria-live="polite"`
- Loading state announced via "Submitting..." text

---

## Error Handling

### Client-Side

**useFeedback Hook:**
- Network errors: "Network error. Please check your connection and try again."
- Rate limit (429): "You have exceeded the feedback submission limit. Please try again later."
- Validation (400/422): Extract error detail from response or show generic message
- Server error (500): "Server error. Please try again later."
- Unknown errors: "An unexpected error occurred. Please try again."

**Retry Logic:**
- Automatic retry on network/server errors (max 2 retries)
- Exponential backoff: 1s, 2s, 4s
- No retry on 400, 422, or 429 errors

---

### Server-Side

**API Routes:**
- Try-catch blocks on all endpoints
- Specific error handling for rate limiting, validation
- Generic 500 error for unexpected failures
- Structured error responses with detail messages

**Service Layer:**
- Validation in `create_feedback` method
- Rate limit check with clear boolean return
- Database errors caught and logged

---

## Performance Considerations

### Frontend

- Lazy loading of analytics dashboard (admin-only)
- Debounced search input in feedback table
- Pagination for large feedback lists
- Chart rendering optimized with Recharts

### Backend

- Indexed queries for feedback lookup (user_id, plan_id, created_at)
- Aggregation queries optimized with database indexes
- CSV export streams data (doesn't load all into memory)
- Rate limiting cached in Redis (fast lookups)

---

## Future Enhancements

### Potential Improvements

1. **Sentiment Analysis:**
   - Integrate ML-based sentiment analysis (e.g., Hugging Face Transformers)
   - Support multilingual feedback

2. **Feedback Moderation:**
   - Flag inappropriate content
   - Admin approval workflow for public display

3. **Email Notifications:**
   - Notify admins of critical feedback (1-star ratings)
   - Thank-you emails to users who submit detailed feedback

4. **A/B Testing:**
   - Test different feedback prompts
   - Optimize feedback collection rate

5. **Feedback Trends:**
   - Week-over-week comparison
   - Seasonal trend analysis

6. **Integration with BI Tools:**
   - Export to Google Analytics
   - Tableau/Power BI dashboards

---

## Dependencies

### Backend

- `fastapi` - Web framework
- `sqlalchemy` - ORM
- `pydantic` - Data validation
- Existing authentication middleware
- Existing rate limiting middleware

### Frontend

- `react` ^18.0.0
- `typescript` ^5.3.0
- `lucide-react` - Icons
- `recharts` - Charts
- `clsx` - Conditional classes
- Existing API client
- Existing design system components

---

## Migration Notes

### Database Migrations

**Model:** Feedback table already exists (created in Wave 1)

**No migrations required** - The `feedback` table was created with all necessary columns and indexes in the initial schema.

### Optional: Seed Data

To test the dashboard, you can seed sample feedback:

```python
# In Django management command or Alembic seed script
from src.backend.models.feedback import Feedback
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timedelta
import random

# Generate 100 sample feedback records
for i in range(100):
    feedback = Feedback(
        id=uuid4(),
        user_id=random.choice([uuid4(), None]),  # 50% anonymous
        plan_id=random.choice(plan_ids),
        rating=random.randint(1, 5),
        feedback_text="Sample feedback text" if random.random() > 0.5 else None,
        feedback_type=random.choice(['helpful', 'not_helpful']),
        sentiment_score=Decimal(str(random.uniform(-1, 1))),
        created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
    )
    db.add(feedback)

db.commit()
```

---

## File Summary

### Backend Files Created (3)

1. `/src/backend/schemas/feedback_schemas.py` - Pydantic schemas
2. `/src/backend/services/feedback_service.py` - Business logic
3. `/src/backend/api/routes/feedback.py` - API endpoints

### Frontend Files Created (11)

1. `/src/frontend/src/types/feedback.ts` - TypeScript interfaces
2. `/src/frontend/src/hooks/useFeedback.ts` - Custom hook
3. `/src/frontend/src/components/FeedbackWidget/FeedbackWidget.tsx` - Main widget
4. `/src/frontend/src/components/FeedbackWidget/index.ts` - Exports
5. `/src/frontend/src/components/FeedbackAnalytics/FeedbackStats.tsx` - Stats cards
6. `/src/frontend/src/components/FeedbackAnalytics/FeedbackChart.tsx` - Time-series charts
7. `/src/frontend/src/components/FeedbackAnalytics/FeedbackTable.tsx` - Plan table
8. `/src/frontend/src/components/FeedbackAnalytics/index.ts` - Exports
9. `/src/frontend/src/pages/FeedbackDashboard.tsx` - Admin dashboard

### Frontend Files Modified (2)

1. `/src/frontend/src/components/PlanCard/PlanCard.tsx` - Added FeedbackWidget
2. `/src/frontend/src/pages/ResultsPage.tsx` - Added page-level feedback

### Backend Files Modified (1)

1. `/src/backend/api/main.py` - Added feedback router

### Test Files Created (2)

1. `/tests/backend/test_feedback_api.py` - Backend tests
2. `/tests/frontend/components/FeedbackWidget.test.tsx` - Frontend tests

### Documentation (1)

1. `/docs/contracts/story-8.1-8.2-8.3-contract.md` - This file

---

## Contact & Support

**Questions?** Reach out to Fullstack Dev #1 or refer to:
- API documentation: `/docs` endpoint (FastAPI auto-generated)
- Storybook: Frontend component documentation
- Source code comments and docstrings

---

## Changelog

**2025-11-10** - Initial implementation
- Created all feedback endpoints and components
- Integrated feedback widgets into existing UI
- Built admin analytics dashboard
- Implemented sentiment analysis
- Added comprehensive tests and documentation

---

**End of Contract** ✅
