# Frontend Integration Guide
## Connecting Epic 4 Frontend with Epic 3 Backend

**Version:** 1.0  
**Date:** November 10, 2025  
**Status:** Ready for Integration

---

## Overview

This guide explains how to integrate the Epic 4 frontend with the Epic 3 backend API to create a fully functional TreeBeard Energy Plan Recommendation system.

---

## Prerequisites

### Backend (Epic 3)
- Backend API running on `http://localhost:8000`
- Database populated with energy plans
- All endpoints from Epic 3 contract functional

### Frontend (Epic 4)
- Node.js 18+ installed
- Frontend dependencies installed (`npm install`)

---

## Setup Instructions

### Step 1: Configure Environment Variables

Create `/src/frontend/.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

### Step 2: Start Backend Server

```bash
# From project root
cd /Users/aleksandrgaun/Downloads/TreeBeard
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

Verify backend is running:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-10T...",
  "version": "1.0.0"
}
```

### Step 3: Start Frontend Development Server

```bash
# From frontend directory
cd /Users/aleksandrgaun/Downloads/TreeBeard/src/frontend
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Step 4: Test Integration

Open browser to `http://localhost:3000` and verify:
- Page loads without errors
- API calls are proxied to backend
- CORS is configured correctly

---

## API Integration Points

### 1. Generate Recommendations

**Frontend Component:** `ResultsPage.tsx`  
**API Endpoint:** `POST /api/v1/recommendations/generate`  
**API Module:** `src/api/recommendations.ts`

```typescript
import recommendationsApi from '@/api/recommendations';

const recommendation = await recommendationsApi.generate({
  user_data: {
    zip_code: '78701',
    property_type: 'residential',
  },
  usage_data: [
    { month: '2024-01-01', kwh: 850 },
    { month: '2024-02-01', kwh: 920 },
    // ... 12 months total
  ],
  preferences: {
    cost_priority: 40,
    flexibility_priority: 30,
    renewable_priority: 20,
    rating_priority: 10,
  },
  current_plan: {
    supplier_name: 'Current Provider',
    current_rate: 10.5,
    contract_end_date: '2025-12-31',
    early_termination_fee: 150,
  },
});
```

**Expected Response:** See Epic 3 contract (`GenerateRecommendationResponse`)

### 2. Authentication (Future)

When implementing authentication:

```typescript
import { apiClient } from '@/api/client';

// Login
const response = await apiClient.post('/auth/login', {
  username: 'user@example.com',
  password: 'password',
});

// Set token
apiClient.setToken(response.data.access_token);

// All subsequent requests will include the token
```

---

## CORS Configuration

### Backend CORS Settings

Ensure backend (`backend/api/main.py`) has CORS configured:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend Proxy Configuration

Vite proxy is configured in `vite.config.ts`:

```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

This proxies all `/api/*` requests to the backend.

---

## Data Flow

```
User Action (Frontend)
    ↓
React Component calls API function
    ↓
API Client (Axios) sends HTTP request
    ↓
Vite Dev Server proxies to backend
    ↓
Backend API processes request
    ↓
Backend returns JSON response
    ↓
Frontend receives and displays data
```

---

## Sample Full Integration Flow

### 1. User Submits Preferences

```tsx
// In a future onboarding form component
const handleSubmit = async (formData) => {
  try {
    const recommendation = await recommendationsApi.generate(formData);
    
    // Navigate to results page with data
    navigate('/results', { state: { recommendation } });
  } catch (error) {
    console.error('Failed to generate recommendations:', error);
    setError('Unable to load recommendations. Please try again.');
  }
};
```

### 2. Results Page Displays Recommendations

```tsx
// In ResultsPage.tsx
const ResultsPage = () => {
  const location = useLocation();
  const [recommendation, setRecommendation] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    if (location.state?.recommendation) {
      setRecommendation(location.state.recommendation);
      setIsLoading(false);
    }
  }, [location]);
  
  return (
    <ResultsPage
      recommendation={recommendation}
      isLoading={isLoading}
    />
  );
};
```

---

## Error Handling

### Frontend Error Handling

The API client (`src/api/client.ts`) handles errors:

```typescript
// Interceptor catches errors
this.client.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      window.location.href = '/login';
    }
    
    if (error.response?.status === 429) {
      // Rate limited
      alert('Too many requests. Please wait a moment.');
    }
    
    return Promise.reject(error);
  }
);
```

### Component Error Handling

```tsx
const [error, setError] = useState<string | null>(null);

try {
  const data = await recommendationsApi.generate(request);
  setRecommendation(data);
} catch (err) {
  if (err.response?.status === 422) {
    setError('Invalid input. Please check your data.');
  } else {
    setError('An unexpected error occurred. Please try again.');
  }
}
```

---

## Testing Integration

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. API Documentation

Visit `http://localhost:8000/docs` for Swagger UI

### 3. Test Recommendation Generation

```bash
curl -X POST http://localhost:8000/api/v1/recommendations/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_data": {
      "zip_code": "78701",
      "property_type": "residential"
    },
    "usage_data": [
      {"month": "2024-01-01", "kwh": 850},
      {"month": "2024-02-01", "kwh": 920}
    ],
    "preferences": {
      "cost_priority": 40,
      "flexibility_priority": 30,
      "renewable_priority": 20,
      "rating_priority": 10
    }
  }'
```

---

## Development Workflow

### Typical Development Session

1. **Start Backend:**
   ```bash
   cd /Users/aleksandrgaun/Downloads/TreeBeard
   python -m uvicorn backend.api.main:app --reload
   ```

2. **Start Frontend:**
   ```bash
   cd src/frontend
   npm run dev
   ```

3. **Make Changes:**
   - Edit frontend components in `src/`
   - Hot reload updates instantly
   - Check browser console for errors

4. **Test API Calls:**
   - Open Network tab in DevTools
   - Watch API requests/responses
   - Verify data format matches contract

---

## Common Issues & Solutions

### Issue: CORS Errors

**Error:** `Access to XMLHttpRequest at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solution:**
1. Verify backend CORS configuration includes `http://localhost:3000`
2. Check Vite proxy configuration
3. Restart both servers

### Issue: 404 Not Found

**Error:** `GET http://localhost:3000/api/v1/recommendations 404`

**Solution:**
1. Verify backend is running on port 8000
2. Check API endpoint exists: `http://localhost:8000/docs`
3. Verify Vite proxy configuration

### Issue: Type Errors

**Error:** TypeScript type mismatch

**Solution:**
1. Ensure types in `src/types/recommendation.ts` match backend contract
2. Update types if backend contract changed
3. Run `npm run build` to check for type errors

### Issue: Token Expired

**Error:** 401 Unauthorized

**Solution:**
1. Clear localStorage: `localStorage.clear()`
2. Re-login to get new token
3. Or implement token refresh logic

---

## Production Deployment

### Environment Variables

**Production `.env`:**
```bash
VITE_API_BASE_URL=https://api.treebeard.com
```

### Build for Production

```bash
cd src/frontend
npm run build
```

Output: `dist/` directory

### Serve Production Build

```bash
npm run preview
```

Or deploy to:
- Vercel
- Netlify
- AWS S3 + CloudFront
- Docker container

---

## Monitoring & Debugging

### Frontend

- **Console Logs:** Check browser console for errors
- **Network Tab:** Monitor API calls and responses
- **React DevTools:** Inspect component state
- **Redux DevTools:** (if using Redux)

### Backend

- **API Logs:** Check backend console output
- **Database Logs:** Verify queries
- **Error Tracking:** Sentry or similar

### Performance

- **Lighthouse:** Audit performance, accessibility, SEO
- **Network Throttling:** Test on slow connections
- **Bundle Analyzer:** Check bundle size

---

## Next Steps

1. **Implement Onboarding Flow** (Epic 5)
   - User registration
   - Preference collection
   - Usage data upload

2. **Add Authentication**
   - Login/logout
   - Protected routes
   - Token management

3. **Enhance Features**
   - Plan comparison
   - Favorites
   - Sharing

---

## Support

- **API Contract:** `/docs/contracts/epic-3-api-contract.md`
- **Frontend Docs:** `/src/frontend/FRONTEND-README.md`
- **Backend Docs:** `/README-RECOMMENDATION-ENGINE.md`

---

**Integration Status:** ✅ Ready  
**Last Updated:** November 10, 2025
