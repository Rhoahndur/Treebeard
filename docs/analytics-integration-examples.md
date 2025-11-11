# Analytics Integration Examples

## Overview

This document provides practical examples of integrating analytics tracking into the TreeBeard application.

---

## Frontend Integration Examples

### Example 1: Tracking Page Views in React Router

```typescript
// src/frontend/src/App.tsx
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import analytics from './utils/analytics';

function App() {
  const location = useLocation();

  useEffect(() => {
    // Track page view on route change
    analytics.trackPageView({
      page_path: location.pathname,
      page_title: document.title,
      page_location: window.location.href,
    });
  }, [location]);

  return (
    // Your app
  );
}
```

### Example 2: Tracking Onboarding Flow

```typescript
// src/frontend/src/pages/OnboardingPage.tsx
import { useState, useEffect } from 'react';
import analytics from '../utils/analytics';

export function OnboardingPage() {
  const [currentStep, setCurrentStep] = useState(1);
  const [stepStartTime, setStepStartTime] = useState(Date.now());
  const [onboardingStartTime] = useState(Date.now());

  useEffect(() => {
    // Track onboarding started (only on mount)
    analytics.trackOnboardingStarted();
  }, []);

  const handleStepComplete = (stepNumber: number, stepName: string) => {
    // Calculate time spent on step
    const timeSpent = Math.floor((Date.now() - stepStartTime) / 1000);

    // Track step completion
    analytics.trackOnboardingStepCompleted(stepNumber, stepName, timeSpent);

    // Move to next step
    setCurrentStep(stepNumber + 1);
    setStepStartTime(Date.now());
  };

  const handleOnboardingComplete = () => {
    const totalTime = Math.floor((Date.now() - onboardingStartTime) / 1000);
    analytics.trackOnboardingCompleted(totalTime);

    // Set user properties
    analytics.setUserProperties({
      property_type: formData.propertyType,
      zip_code: formData.zipCode,
      user_segment: getUserSegment(formData),
    });

    // Navigate to results
    navigate('/results');
  };

  const handleAbandon = (reason?: string) => {
    const stepName = getStepName(currentStep);
    analytics.trackOnboardingAbandoned(currentStep, stepName, reason);
  };

  // Track abandonment on component unmount (if not completed)
  useEffect(() => {
    return () => {
      if (currentStep < 5) {
        handleAbandon('navigated_away');
      }
    };
  }, [currentStep]);

  return (
    // Onboarding UI
  );
}
```

### Example 3: Tracking File Uploads

```typescript
// src/frontend/src/components/FileUpload.tsx
import { useState } from 'react';
import analytics from '../utils/analytics';

export function FileUpload() {
  const [uploading, setUploading] = useState(false);

  const handleFileUpload = async (file: File, method: 'drag_drop' | 'file_picker') => {
    const fileSizeKb = Math.round(file.size / 1024);
    const fileType = file.name.split('.').pop() || 'unknown';

    // Track upload attempt
    analytics.trackFileUploadAttempted(fileType, fileSizeKb, method);

    setUploading(true);

    try {
      // Upload file
      await api.uploadUsageData(file);

      // Track success
      analytics.trackFileUploadSucceeded(fileType, fileSizeKb);

      // Show success message
      toast.success('File uploaded successfully!');
    } catch (error) {
      // Track failure
      analytics.trackFileUploadFailed(
        fileType,
        error instanceof Error ? error.message : 'Unknown error'
      );

      // Show error message
      toast.error('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileUpload(file, 'drag_drop');
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileUpload(file, 'file_picker');
    }
  };

  return (
    <div onDrop={handleDrop}>
      <input type="file" onChange={handleFileSelect} />
    </div>
  );
}
```

### Example 4: Tracking Recommendation Interactions

```typescript
// src/frontend/src/pages/ResultsPage.tsx
import { useState, useEffect } from 'react';
import analytics from '../utils/analytics';

export function ResultsPage() {
  const [recommendations, setRecommendations] = useState([]);
  const [generationStartTime] = useState(Date.now());

  useEffect(() => {
    async function loadRecommendations() {
      try {
        const response = await api.getRecommendations();
        const generationTime = Date.now() - generationStartTime;

        setRecommendations(response.data);

        // Track recommendation generation
        analytics.trackRecommendationGenerated(
          response.data.length,
          response.profileType,
          generationTime
        );
      } catch (error) {
        console.error('Failed to load recommendations', error);
      }
    }

    loadRecommendations();
  }, []);

  const handlePlanCardExpand = (plan: Plan, position: number) => {
    analytics.trackPlanCardExpanded(plan.id, plan.name, position);
  };

  const handlePlanCardClick = (plan: Plan, position: number) => {
    analytics.trackPlanCardClicked(plan.id, plan.name, position);
  };

  const handleCostBreakdownView = (planId: string) => {
    analytics.trackCostBreakdownViewed(planId);
  };

  const handleComparisonView = (planIds: string[]) => {
    analytics.trackComparisonViewed(planIds);
  };

  return (
    <div>
      {recommendations.map((plan, index) => (
        <PlanCard
          key={plan.id}
          plan={plan}
          position={index + 1}
          onExpand={() => handlePlanCardExpand(plan, index + 1)}
          onClick={() => handlePlanCardClick(plan, index + 1)}
          onViewCostBreakdown={() => handleCostBreakdownView(plan.id)}
        />
      ))}
    </div>
  );
}
```

### Example 5: Tracking Preference Changes

```typescript
// src/frontend/src/components/PreferencesSlider.tsx
import { useState, useEffect } from 'react';
import { debounce } from 'lodash';
import analytics from '../utils/analytics';

export function PreferencesSlider() {
  const [preferences, setPreferences] = useState({
    costPriority: 70,
    renewablePriority: 50,
    flexibilityPriority: 60,
    ratingsPriority: 65,
  });

  // Debounce analytics tracking to avoid excessive events
  const trackPreferencesChange = debounce((prefs) => {
    analytics.trackPreferencesChanged(prefs);
  }, 1000);

  const handlePreferenceChange = (key: string, value: number) => {
    const newPreferences = { ...preferences, [key]: value };
    setPreferences(newPreferences);
    trackPreferencesChange(newPreferences);
  };

  return (
    <div>
      <Slider
        label="Cost Priority"
        value={preferences.costPriority}
        onChange={(val) => handlePreferenceChange('costPriority', val)}
      />
      {/* Other sliders... */}
    </div>
  );
}
```

### Example 6: Setting Up Analytics in Main App

```typescript
// src/frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import CookieConsent from './components/CookieConsent';
import analytics from './utils/analytics';

// Initialize analytics
analytics.initialize({
  enabled: import.meta.env.VITE_ANALYTICS_ENABLED === 'true',
  platform: 'ga4',
  ga4MeasurementId: import.meta.env.VITE_GA4_MEASUREMENT_ID,
  debug: import.meta.env.DEV,
  anonymizeIp: true,
  cookieConsent: true,
});

// Generate anonymous user ID (or get from session)
const getAnonymousUserId = () => {
  let userId = localStorage.getItem('anonymous_user_id');
  if (!userId) {
    userId = `anon-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('anonymous_user_id', userId);
  }
  return userId;
};

// Identify user
analytics.identifyUser(getAnonymousUserId());

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
    <CookieConsent showSettings={true} />
  </React.StrictMode>
);
```

---

## Backend Integration Examples

### Example 1: Setting Up Analytics Service

```python
# src/backend/api/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from services.analytics_service import init_analytics, AnalyticsBackend
from api.middleware.analytics import AnalyticsMiddleware
from config.settings import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    analytics = init_analytics(
        backend=AnalyticsBackend.MIXPANEL if settings.ANALYTICS_BACKEND == "mixpanel"
                else AnalyticsBackend.LOGGING,
        mixpanel_token=settings.MIXPANEL_TOKEN,
        enabled=settings.ANALYTICS_ENABLED
    )

    yield

    # Shutdown
    await analytics.shutdown()

app = FastAPI(lifespan=lifespan)

# Add analytics middleware
app.add_middleware(AnalyticsMiddleware)
```

### Example 2: Tracking Recommendation Generation

```python
# src/backend/api/routes/recommendations.py
from fastapi import APIRouter, Depends, HTTPException
from services.recommendation_engine import RecommendationEngine
from services.analytics_service import get_analytics_service
from uuid import UUID
import time

router = APIRouter()

@router.post("/generate")
async def generate_recommendations(
    request: RecommendationRequest,
    user_id: UUID = Depends(get_current_user_id),
    engine: RecommendationEngine = Depends(get_recommendation_engine),
    analytics = Depends(get_analytics_service)
):
    start_time = time.time()

    try:
        # Generate recommendations
        recommendations = await engine.generate_recommendations(
            user_id=user_id,
            usage_profile=request.usage_profile,
            preferences=request.preferences
        )

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Calculate total savings
        total_savings = sum(r.annual_savings for r in recommendations)

        # Track successful recommendation generation
        await analytics.track_recommendation_generated(
            user_id=user_id,
            profile_type=recommendations.profile_type,
            num_plans=len(recommendations.plans),
            duration_ms=duration_ms,
            total_savings=total_savings
        )

        return {
            "recommendations": recommendations,
            "metadata": {
                "profile_type": recommendations.profile_type,
                "generation_time_ms": duration_ms
            }
        }

    except Exception as e:
        # Track error
        await analytics.track_error(
            endpoint="/api/v1/recommendations/generate",
            error_type=type(e).__name__,
            status_code=500,
            error_message=str(e),
            user_id=user_id
        )
        raise HTTPException(status_code=500, detail=str(e))
```

### Example 3: Tracking with Performance Timer

```python
# src/backend/services/recommendation_engine.py
from services.analytics_service import get_analytics_service
from api.middleware.analytics import PerformanceTimer

class RecommendationEngine:
    def __init__(self):
        self.analytics = get_analytics_service()

    async def generate_recommendations(self, user_id, usage_profile, preferences):
        # Track overall operation
        async with PerformanceTimer("recommendation_generation", user_id):
            # Analyze usage
            async with PerformanceTimer("usage_analysis", user_id):
                usage_analysis = await self.analyze_usage(usage_profile)

            # Score plans
            async with PerformanceTimer("plan_scoring", user_id):
                scored_plans = await self.score_plans(usage_analysis, preferences)

            # Generate explanations
            async with PerformanceTimer("explanation_generation", user_id):
                explanations = await self.generate_explanations(scored_plans)

            return self.format_recommendations(scored_plans, explanations)
```

### Example 4: Tracking Risk Warnings

```python
# src/backend/services/risk_detector.py
from services.analytics_service import get_analytics_service
from typing import List
from uuid import UUID

class RiskDetector:
    def __init__(self):
        self.analytics = get_analytics_service()

    async def detect_risks(
        self,
        plan: Plan,
        user_profile: UserProfile,
        user_id: UUID
    ) -> List[RiskWarning]:
        warnings = []

        # Check for high ETF
        if plan.early_termination_fee > 150:
            warnings.append(RiskWarning(
                type="high_etf",
                severity="warning",
                message=f"High early termination fee: ${plan.early_termination_fee}"
            ))

            # Track risk warning
            await self.analytics.track_risk_warning(
                risk_type="high_etf",
                severity="warning",
                user_id=user_id
            )

        # Check for marginal savings
        if plan.annual_savings < 50:
            warnings.append(RiskWarning(
                type="marginal_savings",
                severity="info",
                message=f"Low savings: Only ${plan.annual_savings}/year"
            ))

            await self.analytics.track_risk_warning(
                risk_type="marginal_savings",
                severity="info",
                user_id=user_id
            )

        # Check data confidence
        if user_profile.data_completeness < 0.7:
            warnings.append(RiskWarning(
                type="insufficient_data",
                severity="warning",
                message="Recommendations based on limited data"
            ))

            await self.analytics.track_risk_warning(
                risk_type="insufficient_data",
                severity="warning",
                user_id=user_id
            )

        return warnings
```

### Example 5: Tracking Cache Operations

```python
# src/backend/services/cache_service.py
from redis import Redis
from services.analytics_service import get_analytics_service
import json

class CacheService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.analytics = get_analytics_service()

    async def get(self, key: str):
        value = self.redis.get(key)

        # Track cache hit/miss
        await self.analytics.track_cache_hit(
            cache_key=key,
            hit=value is not None
        )

        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: any, ttl: int = 3600):
        self.redis.setex(key, ttl, json.dumps(value))
```

### Example 6: Tracking User Events

```python
# src/backend/api/routes/users.py
from fastapi import APIRouter, Depends
from services.analytics_service import get_analytics_service
from uuid import UUID

router = APIRouter()

@router.post("/")
async def create_user(
    request: CreateUserRequest,
    analytics = Depends(get_analytics_service)
):
    # Create user
    user = await user_service.create_user(request)

    # Track user creation
    await analytics.track_user_created(
        user_id=user.id,
        property_type=request.property_type,
        zip_code=request.zip_code
    )

    return user

@router.put("/{user_id}/preferences")
async def update_preferences(
    user_id: UUID,
    preferences: PreferencesUpdate,
    analytics = Depends(get_analytics_service)
):
    # Update preferences
    updated_user = await user_service.update_preferences(user_id, preferences)

    # Track preference update
    await analytics.track_preferences_updated(
        user_id=user_id,
        preferences=preferences.dict()
    )

    return updated_user
```

### Example 7: Environment Configuration

```python
# src/backend/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Analytics
    ANALYTICS_ENABLED: bool = True
    ANALYTICS_BACKEND: str = "mixpanel"  # or "logging", "database"
    MIXPANEL_TOKEN: Optional[str] = None
    ANALYTICS_BATCH_SIZE: int = 100
    ANALYTICS_FLUSH_INTERVAL: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
```

```bash
# .env file
ANALYTICS_ENABLED=true
ANALYTICS_BACKEND=mixpanel
MIXPANEL_TOKEN=your_mixpanel_project_token
ANALYTICS_BATCH_SIZE=100
ANALYTICS_FLUSH_INTERVAL=60
```

---

## Testing Analytics Integration

### Frontend Tests

```typescript
// src/frontend/src/utils/analytics.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import analytics from './analytics';

describe('Analytics Integration', () => {
  beforeEach(() => {
    // Mock gtag
    (window as any).gtag = vi.fn();

    // Initialize analytics
    analytics.initialize({
      enabled: true,
      platform: 'ga4',
      ga4MeasurementId: 'G-TEST123',
      cookieConsent: true,
      debug: true,
    });
  });

  it('should track onboarding flow', () => {
    analytics.trackOnboardingStarted();
    expect((window as any).gtag).toHaveBeenCalledWith(
      'event',
      'onboarding_started',
      expect.any(Object)
    );

    analytics.trackOnboardingStepCompleted(1, 'welcome', 30);
    expect((window as any).gtag).toHaveBeenCalledWith(
      'event',
      'onboarding_step_completed',
      expect.objectContaining({
        step: 1,
        step_name: 'welcome',
        time_spent_seconds: 30,
      })
    );
  });

  it('should track file uploads', () => {
    analytics.trackFileUploadAttempted('csv', 250, 'drag_drop');
    analytics.trackFileUploadSucceeded('csv', 250);

    expect((window as any).gtag).toHaveBeenCalledTimes(2);
  });
});
```

### Backend Tests

```python
# tests/backend/test_analytics_integration.py
import pytest
from services.analytics_service import AnalyticsService, AnalyticsBackend
from uuid import uuid4

@pytest.mark.asyncio
async def test_recommendation_tracking():
    analytics = AnalyticsService(
        backend=AnalyticsBackend.LOGGING,
        enabled=True
    )

    user_id = uuid4()

    await analytics.track_recommendation_generated(
        user_id=user_id,
        profile_type="budget_conscious",
        num_plans=3,
        duration_ms=1250,
        total_savings=245.50
    )

    # Verify event queued
    assert len(analytics.event_queue) == 1
    event = analytics.event_queue[0]
    assert event["event"] == "recommendation_generated"
    assert event["properties"]["profile_type"] == "budget_conscious"

@pytest.mark.asyncio
async def test_risk_warning_tracking():
    analytics = AnalyticsService(backend=AnalyticsBackend.LOGGING)

    user_id = uuid4()

    await analytics.track_risk_warning(
        risk_type="high_etf",
        severity="warning",
        user_id=user_id
    )

    assert len(analytics.event_queue) == 1
```

---

## Best Practices

### 1. **Don't Block User Experience**
```typescript
// BAD: Blocking
await analytics.trackEvent(...);  // Waits for completion

// GOOD: Fire and forget
analytics.trackEvent(...);  // Async, non-blocking
```

### 2. **Debounce Frequent Events**
```typescript
// BAD: Track every slider change
<Slider onChange={(val) => analytics.track...} />

// GOOD: Debounce
const trackChange = debounce((val) => analytics.track..., 1000);
<Slider onChange={trackChange} />
```

### 3. **Never Send PII**
```typescript
// BAD: Sending email
analytics.setUserProperties({ email: user.email });

// GOOD: Anonymized or generic properties
analytics.setUserProperties({
  property_type: user.propertyType,
  zip_code: user.zipCode  // OK if not full address
});
```

### 4. **Handle Errors Gracefully**
```typescript
try {
  analytics.trackEvent(...);
} catch (error) {
  // Don't let analytics errors break the app
  console.error('Analytics error:', error);
}
```

### 5. **Use Consistent Event Names**
```typescript
// BAD: Inconsistent naming
analytics.trackEvent('userClickedButton');
analytics.trackEvent('button_clicked');

// GOOD: Consistent snake_case
analytics.trackEvent('button_clicked');
analytics.trackEvent('form_submitted');
```

### 6. **Include Context**
```typescript
// BAD: Minimal context
analytics.trackEvent('button_clicked');

// GOOD: Rich context
analytics.trackEvent('button_clicked', {
  button_name: 'submit_onboarding',
  page: '/onboarding/step-2',
  user_segment: 'budget_conscious',
});
```

### 7. **Test in Development**
```typescript
// Enable debug mode in development
analytics.initialize({
  debug: process.env.NODE_ENV === 'development',
  // ...
});
```
