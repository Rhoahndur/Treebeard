# Epic 3 - API Layer Contract

**Version:** 1.0.0
**Date:** November 10, 2025
**Author:** Backend Dev #5
**Status:** ✅ Complete
**Dependencies:** Epic 1 (Complete), Epic 2 (Complete)

---

## Overview

This contract defines the complete API layer implementation for the TreeBeard Energy Plan Recommendation Agent. The API exposes all Epic 1 and Epic 2 functionality through RESTful endpoints with comprehensive authentication, rate limiting, caching, and monitoring.

---

## Base URL

```
Development: http://localhost:8000
Production: https://api.treebeard.com
```

---

## API Versioning

All endpoints are prefixed with `/api/v1/`

---

## Core Endpoints

### Story 3.2: Core Recommendation Endpoint

#### Generate Recommendations

**Endpoint:** `POST /api/v1/recommendations/generate`

**Authentication:** Required (JWT)

**Rate Limit:** 10 requests/minute per user

**Request Body:**
```typescript
interface GenerateRecommendationRequest {
  user_data: {
    zip_code: string;        // 5-10 digits
    property_type: "residential" | "commercial";
  };
  usage_data: Array<{
    month: string;           // ISO date (first day of month)
    kwh: number;            // >= 0
  }>;  // 3-24 months
  preferences: {
    cost_priority: number;           // 0-100
    flexibility_priority: number;    // 0-100
    renewable_priority: number;      // 0-100
    rating_priority: number;         // 0-100
  };  // Must sum to 100
  current_plan?: {
    plan_name?: string;
    supplier_name?: string;
    current_rate?: number;           // cents per kWh
    contract_end_date?: string;      // ISO date
    early_termination_fee?: number;  // >= 0
    plan_start_date?: string;        // ISO date
  };
}
```

**Response:** `200 OK`
```typescript
interface GenerateRecommendationResponse {
  recommendation_id: string;  // UUID
  user_profile: {
    profile_type: string;              // baseline, seasonal, high_user, etc.
    projected_annual_kwh: number;
    mean_monthly_kwh: number;
    has_seasonal_pattern: boolean;
    confidence_score: number;          // 0-1
  };
  top_plans: Array<{
    rank: number;                      // 1-3
    plan_id: string;                   // UUID
    plan_name: string;
    supplier_name: string;
    plan_type: string;
    scores: {
      cost_score: number;              // 0-100
      flexibility_score: number;       // 0-100
      renewable_score: number;         // 0-100
      rating_score: number;            // 0-100
      composite_score: number;         // 0-100
    };
    projected_annual_cost: number;
    projected_monthly_cost: number;
    average_rate_per_kwh: number;
    savings?: {
      annual_savings: number;
      savings_percentage: number;
      monthly_savings: number;
      break_even_months?: number;
    };
    contract_length_months: number;    // 0 = month-to-month
    early_termination_fee: number;
    renewable_percentage: number;      // 0-100
    monthly_fee?: number;
    explanation: string;               // AI-generated explanation
    key_differentiators: string[];
    trade_offs: string[];
  }>;
  generated_at: string;                // ISO timestamp
  total_plans_analyzed: number;
  warnings: string[];
}
```

**Performance:** <2 seconds (P95)

**Error Responses:**
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Missing or invalid token
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

### Story 3.3: Supporting Endpoints

#### Get User Recommendations

**Endpoint:** `GET /api/v1/recommendations/{user_id}`

**Authentication:** Required (JWT)

**Authorization:** User can only view their own recommendations (unless admin)

**Response:** `200 OK`
```typescript
Array<GenerateRecommendationResponse>
```

---

#### Save User Preferences

**Endpoint:** `POST /api/v1/users/preferences`

**Authentication:** Required (JWT)

**Request Body:**
```typescript
interface UserPreferencesRequest {
  cost_priority: number;           // 0-100
  flexibility_priority: number;    // 0-100
  renewable_priority: number;      // 0-100
  rating_priority: number;         // 0-100
}  // Must sum to 100
```

**Response:** `200 OK`
```typescript
interface UserPreferencesResponse {
  cost_priority: number;
  flexibility_priority: number;
  renewable_priority: number;
  rating_priority: number;
  updated_at: string;  // ISO timestamp
}
```

---

#### Get User Preferences

**Endpoint:** `GET /api/v1/users/preferences`

**Authentication:** Required (JWT)

**Response:** `200 OK`
```typescript
UserPreferencesResponse
```

---

#### Get Plan Catalog

**Endpoint:** `GET /api/v1/plans/catalog`

**Authentication:** Optional

**Query Parameters:**
- `zip_code` (optional): Filter by ZIP code
- `plan_type` (optional): Filter by plan type
- `min_renewable` (optional): Minimum renewable percentage (0-100)
- `max_contract_length` (optional): Maximum contract length (months)
- `page` (default: 1): Page number
- `page_size` (default: 20, max: 100): Items per page

**Response:** `200 OK`
```typescript
interface PaginatedResponse {
  items: Array<{
    id: string;
    plan_name: string;
    supplier_name: string;
    plan_type: string;
    contract_length_months: number;
    early_termination_fee: number;
    renewable_percentage: number;
    monthly_fee?: number;
    is_active: boolean;
    rate_structure: object;
  }>;
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}
```

**Cache:** 1 hour TTL

---

#### Get Plan Details

**Endpoint:** `GET /api/v1/plans/{plan_id}`

**Authentication:** Optional

**Response:** `200 OK`
```typescript
interface PlanResponse {
  id: string;
  plan_name: string;
  supplier_name: string;
  plan_type: string;
  contract_length_months: number;
  early_termination_fee: number;
  renewable_percentage: number;
  monthly_fee?: number;
  is_active: boolean;
  rate_structure: object;
}
```

**Cache:** 1 hour TTL

---

#### Upload Usage Data

**Endpoint:** `POST /api/v1/usage/upload`

**Authentication:** Required (JWT)

**Request Body:**
```typescript
interface UploadUsageRequest {
  usage_data: Array<{
    month: string;  // ISO date
    kwh: number;    // >= 0
  }>;  // 1-24 months
}
```

**Response:** `200 OK`
```typescript
interface MessageResponse {
  message: string;
  success: boolean;
  data?: object;
}
```

---

#### Get Usage History

**Endpoint:** `GET /api/v1/usage/history`

**Authentication:** Required (JWT)

**Response:** `200 OK`
```typescript
Array<{
  month: string;  // ISO date
  kwh: number;
}>
```

---

### Story 3.4: Authentication Endpoints

#### Register

**Endpoint:** `POST /api/v1/auth/register`

**Authentication:** None

**Request Body:**
```typescript
interface RegisterRequest {
  email: string;      // Valid email
  password: string;   // Min 8 characters
  name: string;
  zip_code: string;   // 5-10 digits
}
```

**Response:** `201 Created`
```typescript
interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number;  // seconds
}
```

---

#### Login

**Endpoint:** `POST /api/v1/auth/login`

**Authentication:** None

**Request Body:** (Form data)
- `username`: email
- `password`: password

**Response:** `200 OK`
```typescript
TokenResponse
```

---

#### Refresh Token

**Endpoint:** `POST /api/v1/auth/refresh`

**Authentication:** None

**Request Body:**
```typescript
{
  refresh_token: string;
}
```

**Response:** `200 OK`
```typescript
TokenResponse
```

---

#### Get Current User

**Endpoint:** `GET /api/v1/auth/me`

**Authentication:** Required (JWT)

**Response:** `200 OK`
```typescript
interface UserResponse {
  id: string;
  email: string;
  name: string;
  is_admin: boolean;
  created_at: string;  // ISO timestamp
}
```

---

### Story 3.7: Health & Monitoring

#### Health Check

**Endpoint:** `GET /health`

**Authentication:** None

**Response:** `200 OK`
```typescript
interface HealthResponse {
  status: "healthy" | "unhealthy";
  timestamp: string;
  version: string;
  environment: string;
  checks: {
    database: {
      status: "healthy" | "unhealthy";
      type?: string;
      error?: string;
    };
    cache: {
      status: "healthy" | "unhealthy" | "degraded";
      type?: string;
      error?: string;
      message?: string;
    };
  };
}
```

---

#### Liveness Probe

**Endpoint:** `GET /health/live`

**Authentication:** None

**Response:** `200 OK`
```typescript
{ status: "alive" }
```

---

#### Readiness Probe

**Endpoint:** `GET /health/ready`

**Authentication:** None

**Response:** `200 OK`
```typescript
{ status: "ready" }
```

---

#### Metrics

**Endpoint:** `GET /metrics`

**Authentication:** None

**Response:** `200 OK`
```typescript
interface MetricsResponse {
  timestamp: string;
  version: string;
  environment: string;
  metrics: object;
}
```

---

## Authentication

### JWT Tokens

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

**Token Expiration:**
- Access tokens: 24 hours
- Refresh tokens: 7 days

**Token Claims:**
```typescript
{
  sub: string;      // User ID
  type: "access" | "refresh";
  is_admin: boolean;
  exp: number;      // Expiration timestamp
  iat: number;      // Issued at timestamp
}
```

---

## Rate Limiting

### Per-User Limits

Authenticated users:
- Default: 100 requests/minute
- `/api/v1/recommendations/generate`: 10 requests/minute

### Per-IP Limits

All requests:
- 1000 requests/hour per IP address

### Rate Limit Headers

All responses include:
```
X-RateLimit-Limit-User: 100
X-RateLimit-Limit-IP: 1000
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699632000
```

### Rate Limit Exceeded

**Response:** `429 Too Many Requests`
```typescript
{
  error: "Too Many Requests";
  message: "Rate limit exceeded. Max 100 requests per minute.";
  request_id: string;
}
```

**Headers:**
```
Retry-After: 60
```

---

## Caching

### Cache Headers

GET requests include:
```
X-Cache-Status: HIT | MISS
```

### Cache TTL

- Plan catalog: 1 hour
- Recommendations: 24 hours
- Other GET requests: 5 minutes (default)

---

## Request Tracking

Every request receives a unique ID:
```
X-Request-ID: 123e4567-e89b-12d3-a456-426614174000
```

Include this ID when reporting issues for easier debugging.

---

## Error Responses

All errors follow this format:

```typescript
interface ErrorResponse {
  error: string;
  message: string;
  details?: any;
  request_id?: string;
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

---

## CORS

Allowed origins (configurable):
```
http://localhost:3000
http://localhost:8000
```

Exposed headers:
```
X-Request-ID
X-Cache-Status
```

---

## Performance Targets

All targets met:

✅ API response time: <2 seconds (P95)
✅ Recommendation generation: <2 seconds
✅ Health check: <100ms
✅ Cache hit rate: >60%

---

## OpenAPI Documentation

Interactive documentation available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

---

## Integration Examples

### JavaScript/TypeScript

```typescript
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

// Register
const register = async (email: string, password: string, name: string, zipCode: string) => {
  const response = await axios.post(`${API_BASE}/auth/register`, {
    email,
    password,
    name,
    zip_code: zipCode
  });
  return response.data;
};

// Login
const login = async (email: string, password: string) => {
  const response = await axios.post(`${API_BASE}/auth/login`,
    new URLSearchParams({ username: email, password }),
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
  );
  return response.data;
};

// Generate recommendations
const generateRecommendations = async (token: string, request: GenerateRecommendationRequest) => {
  const response = await axios.post(
    `${API_BASE}/recommendations/generate`,
    request,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  return response.data;
};
```

### Python

```python
import requests

API_BASE = 'http://localhost:8000/api/v1'

# Register
response = requests.post(f'{API_BASE}/auth/register', json={
    'email': 'user@example.com',
    'password': 'secure-password',
    'name': 'John Doe',
    'zip_code': '78701'
})
tokens = response.json()

# Generate recommendations
response = requests.post(
    f'{API_BASE}/recommendations/generate',
    json=request_data,
    headers={'Authorization': f'Bearer {tokens["access_token"]}'}
)
recommendations = response.json()
```

---

## Testing

### Unit Tests
```bash
pytest tests/api/test_routes.py -v
```

### Integration Tests
```bash
pytest tests/integration/test_api_flow.py -v
```

### Load Testing
```bash
locust -f tests/load/locustfile.py
```

---

## Deployment

### Environment Variables

Required:
```bash
DATABASE_URL=postgresql://user:pass@host:5432/treebeard
REDIS_URL=redis://host:6379/0
SECRET_KEY=your-secret-key-min-32-chars
CLAUDE_API_KEY=sk-ant-...
```

Optional:
```bash
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://treebeard.com
JWT_EXPIRATION_MINUTES=1440
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-10 | Initial release - Epic 3 complete |

---

## Acceptance Criteria

### Story 3.1: API Framework ✅
- [x] FastAPI app running with OpenAPI docs at /docs
- [x] Structured JSON logging configured
- [x] Error responses standardized
- [x] CORS configured

### Story 3.2: Core Endpoint ✅
- [x] POST /api/v1/recommendations/generate working
- [x] Integrates all Epic 2 services correctly
- [x] Returns complete recommendation with explanations
- [x] Response time <2 seconds (P95)

### Story 3.3: Supporting Endpoints ✅
- [x] All 5+ supporting endpoints functional
- [x] Proper validation and error handling
- [x] Pagination for catalog endpoint

### Story 3.4: Authentication ✅
- [x] Users can register and login
- [x] JWT tokens issued with 24-hour expiration
- [x] Protected endpoints require valid token
- [x] RBAC supports user, admin roles

### Story 3.5: Rate Limiting ✅
- [x] Rate limits enforced per user and per IP
- [x] Proper headers returned
- [x] 429 responses for exceeded limits

### Story 3.6: Caching ✅
- [x] Caching reduces backend load
- [x] Proper TTL configuration
- [x] Cache invalidation working
- [x] Cache headers (HIT/MISS)

### Story 3.7: Logging & Monitoring ✅
- [x] All requests logged in JSON format
- [x] Health check returns service status
- [x] Request IDs for tracing
- [x] Performance metrics tracked

---

## Support

**Developer:** Backend Dev #5
**Epic:** 3 - API Layer
**Stories:** 3.1-3.7 (All Complete)
**Location:** `/src/backend/api/`

---

**Contract Status:** ✅ Complete and Production Ready

All endpoints tested and ready for frontend integration.
