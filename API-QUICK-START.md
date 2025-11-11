# TreeBeard API - Quick Start Guide

**Epic:** 3 - API Layer
**Version:** 1.0.0
**Audience:** Frontend Developers & API Consumers

---

## Overview

The TreeBeard API is a REST API that provides AI-powered energy plan recommendations. This guide will help you get started quickly.

**Base URL (Development):** `http://localhost:8000`
**Base URL (Production):** `https://api.treebeard.com`

---

## Quick Start (5 Minutes)

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure-password-123",
    "name": "John Doe",
    "zip_code": "78701"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Save the `access_token` for subsequent requests!**

---

### 2. Upload Usage Data

```bash
curl -X POST "http://localhost:8000/api/v1/usage/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "usage_data": [
      {"month": "2024-01-01", "kwh": 850},
      {"month": "2024-02-01", "kwh": 820},
      {"month": "2024-03-01", "kwh": 780},
      {"month": "2024-04-01", "kwh": 750},
      {"month": "2024-05-01", "kwh": 900},
      {"month": "2024-06-01", "kwh": 1100},
      {"month": "2024-07-01", "kwh": 1200},
      {"month": "2024-08-01", "kwh": 1150},
      {"month": "2024-09-01", "kwh": 950},
      {"month": "2024-10-01", "kwh": 800},
      {"month": "2024-11-01", "kwh": 820},
      {"month": "2024-12-01", "kwh": 880}
    ]
  }'
```

---

### 3. Set Preferences

```bash
curl -X POST "http://localhost:8000/api/v1/users/preferences" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cost_priority": 50,
    "flexibility_priority": 20,
    "renewable_priority": 20,
    "rating_priority": 10
  }'
```

**Note:** Priorities must sum to exactly 100!

---

### 4. Generate Recommendations

```bash
curl -X POST "http://localhost:8000/api/v1/recommendations/generate" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_data": {
      "zip_code": "78701",
      "property_type": "residential"
    },
    "usage_data": [
      {"month": "2024-01-01", "kwh": 850},
      {"month": "2024-02-01", "kwh": 820},
      {"month": "2024-03-01", "kwh": 780},
      {"month": "2024-04-01", "kwh": 750},
      {"month": "2024-05-01", "kwh": 900},
      {"month": "2024-06-01", "kwh": 1100},
      {"month": "2024-07-01", "kwh": 1200},
      {"month": "2024-08-01", "kwh": 1150},
      {"month": "2024-09-01", "kwh": 950},
      {"month": "2024-10-01", "kwh": 800},
      {"month": "2024-11-01", "kwh": 820},
      {"month": "2024-12-01", "kwh": 880}
    ],
    "preferences": {
      "cost_priority": 50,
      "flexibility_priority": 20,
      "renewable_priority": 20,
      "rating_priority": 10
    },
    "current_plan": {
      "plan_name": "Standard Plan",
      "supplier_name": "Current Energy",
      "current_rate": 14.5,
      "contract_end_date": "2025-06-30",
      "early_termination_fee": 150
    }
  }'
```

**Response:** Top 3 recommended plans with AI explanations!

---

## JavaScript/TypeScript Example

### Setup

```bash
npm install axios
```

### Complete Flow

```typescript
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

interface Tokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface MonthlyUsage {
  month: string;
  kwh: number;
}

// 1. Register
async function register() {
  const response = await axios.post(`${API_BASE}/auth/register`, {
    email: 'user@example.com',
    password: 'secure-password-123',
    name: 'John Doe',
    zip_code: '78701'
  });
  return response.data as Tokens;
}

// 2. Login
async function login(email: string, password: string) {
  const response = await axios.post(
    `${API_BASE}/auth/login`,
    new URLSearchParams({ username: email, password }),
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
  );
  return response.data as Tokens;
}

// 3. Upload Usage Data
async function uploadUsage(token: string, usageData: MonthlyUsage[]) {
  const response = await axios.post(
    `${API_BASE}/usage/upload`,
    { usage_data: usageData },
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  return response.data;
}

// 4. Set Preferences
async function setPreferences(token: string) {
  const response = await axios.post(
    `${API_BASE}/users/preferences`,
    {
      cost_priority: 50,
      flexibility_priority: 20,
      renewable_priority: 20,
      rating_priority: 10
    },
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  return response.data;
}

// 5. Generate Recommendations
async function generateRecommendations(token: string, usageData: MonthlyUsage[]) {
  const response = await axios.post(
    `${API_BASE}/recommendations/generate`,
    {
      user_data: {
        zip_code: '78701',
        property_type: 'residential'
      },
      usage_data: usageData,
      preferences: {
        cost_priority: 50,
        flexibility_priority: 20,
        renewable_priority: 20,
        rating_priority: 10
      },
      current_plan: {
        plan_name: 'Standard Plan',
        current_rate: 14.5,
        contract_end_date: '2025-06-30',
        early_termination_fee: 150
      }
    },
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  return response.data;
}

// Main Flow
async function main() {
  try {
    // 1. Register (or login if already registered)
    console.log('Registering user...');
    const tokens = await register();
    console.log('Got access token:', tokens.access_token.substring(0, 20) + '...');

    // 2. Upload usage data
    console.log('Uploading usage data...');
    const usageData = [
      { month: '2024-01-01', kwh: 850 },
      { month: '2024-02-01', kwh: 820 },
      // ... add more months
    ];
    await uploadUsage(tokens.access_token, usageData);
    console.log('Usage data uploaded!');

    // 3. Set preferences
    console.log('Setting preferences...');
    await setPreferences(tokens.access_token);
    console.log('Preferences saved!');

    // 4. Generate recommendations
    console.log('Generating recommendations...');
    const recommendations = await generateRecommendations(tokens.access_token, usageData);
    console.log('Recommendations:');
    console.log(JSON.stringify(recommendations, null, 2));

    // Display top plan
    const topPlan = recommendations.top_plans[0];
    console.log('\nTop Recommendation:');
    console.log(`Plan: ${topPlan.plan_name}`);
    console.log(`Supplier: ${topPlan.supplier_name}`);
    console.log(`Annual Cost: $${topPlan.projected_annual_cost}`);
    console.log(`Savings: $${topPlan.savings?.annual_savings}`);
    console.log(`Explanation: ${topPlan.explanation}`);

  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('API Error:', error.response?.data);
    } else {
      console.error('Error:', error);
    }
  }
}

main();
```

---

## Python Example

```python
import requests
from typing import List, Dict

API_BASE = 'http://localhost:8000/api/v1'

# 1. Register
def register():
    response = requests.post(f'{API_BASE}/auth/register', json={
        'email': 'user@example.com',
        'password': 'secure-password-123',
        'name': 'John Doe',
        'zip_code': '78701'
    })
    return response.json()

# 2. Login
def login(email: str, password: str):
    response = requests.post(
        f'{API_BASE}/auth/login',
        data={'username': email, 'password': password}
    )
    return response.json()

# 3. Upload Usage Data
def upload_usage(token: str, usage_data: List[Dict]):
    response = requests.post(
        f'{API_BASE}/usage/upload',
        json={'usage_data': usage_data},
        headers={'Authorization': f'Bearer {token}'}
    )
    return response.json()

# 4. Set Preferences
def set_preferences(token: str):
    response = requests.post(
        f'{API_BASE}/users/preferences',
        json={
            'cost_priority': 50,
            'flexibility_priority': 20,
            'renewable_priority': 20,
            'rating_priority': 10
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    return response.json()

# 5. Generate Recommendations
def generate_recommendations(token: str, usage_data: List[Dict]):
    response = requests.post(
        f'{API_BASE}/recommendations/generate',
        json={
            'user_data': {
                'zip_code': '78701',
                'property_type': 'residential'
            },
            'usage_data': usage_data,
            'preferences': {
                'cost_priority': 50,
                'flexibility_priority': 20,
                'renewable_priority': 20,
                'rating_priority': 10
            },
            'current_plan': {
                'plan_name': 'Standard Plan',
                'current_rate': 14.5,
                'contract_end_date': '2025-06-30',
                'early_termination_fee': 150
            }
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    return response.json()

# Main
if __name__ == '__main__':
    # 1. Register
    print('Registering user...')
    tokens = register()
    access_token = tokens['access_token']
    print(f'Got access token: {access_token[:20]}...')

    # 2. Upload usage
    print('Uploading usage data...')
    usage_data = [
        {'month': '2024-01-01', 'kwh': 850},
        {'month': '2024-02-01', 'kwh': 820},
        # ... add more months
    ]
    upload_usage(access_token, usage_data)
    print('Usage data uploaded!')

    # 3. Set preferences
    print('Setting preferences...')
    set_preferences(access_token)
    print('Preferences saved!')

    # 4. Generate recommendations
    print('Generating recommendations...')
    recommendations = generate_recommendations(access_token, usage_data)

    # Display
    top_plan = recommendations['top_plans'][0]
    print(f'\nTop Recommendation:')
    print(f"Plan: {top_plan['plan_name']}")
    print(f"Supplier: {top_plan['supplier_name']}")
    print(f"Annual Cost: ${top_plan['projected_annual_cost']}")
    print(f"Savings: ${top_plan['savings']['annual_savings']}")
    print(f"Explanation: {top_plan['explanation']}")
```

---

## React Example

```tsx
import React, { useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

function EnergyRecommendations() {
  const [token, setToken] = useState('');
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    try {
      const response = await axios.post(`${API_BASE}/auth/register`, {
        email: 'user@example.com',
        password: 'secure-password-123',
        name: 'John Doe',
        zip_code: '78701'
      });
      setToken(response.data.access_token);
      alert('Registered successfully!');
    } catch (error) {
      alert('Registration failed: ' + error.response?.data?.detail);
    }
  };

  const handleGenerateRecommendations = async () => {
    setLoading(true);
    try {
      const usageData = [
        { month: '2024-01-01', kwh: 850 },
        { month: '2024-02-01', kwh: 820 },
        // ... 12 months total
      ];

      const response = await axios.post(
        `${API_BASE}/recommendations/generate`,
        {
          user_data: {
            zip_code: '78701',
            property_type: 'residential'
          },
          usage_data: usageData,
          preferences: {
            cost_priority: 50,
            flexibility_priority: 20,
            renewable_priority: 20,
            rating_priority: 10
          }
        },
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      setRecommendations(response.data);
    } catch (error) {
      alert('Failed to generate recommendations: ' + error.response?.data?.detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>TreeBeard Energy Recommendations</h1>

      {!token ? (
        <button onClick={handleRegister}>Register & Login</button>
      ) : (
        <>
          <button onClick={handleGenerateRecommendations} disabled={loading}>
            {loading ? 'Generating...' : 'Generate Recommendations'}
          </button>

          {recommendations && (
            <div>
              <h2>Top Recommendations:</h2>
              {recommendations.top_plans.map((plan, index) => (
                <div key={index} style={{ border: '1px solid #ccc', padding: '1rem', margin: '1rem 0' }}>
                  <h3>#{plan.rank} - {plan.plan_name}</h3>
                  <p><strong>Supplier:</strong> {plan.supplier_name}</p>
                  <p><strong>Annual Cost:</strong> ${plan.projected_annual_cost}</p>
                  <p><strong>Savings:</strong> ${plan.savings?.annual_savings || 0}/year</p>
                  <p><strong>Renewable:</strong> {plan.renewable_percentage}%</p>
                  <p><em>{plan.explanation}</em></p>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default EnergyRecommendations;
```

---

## Common Error Handling

```typescript
try {
  const response = await axios.post(url, data, { headers });
} catch (error) {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const data = error.response?.data;

    switch (status) {
      case 400:
        console.error('Bad Request:', data.detail);
        break;
      case 401:
        console.error('Unauthorized - login again');
        // Redirect to login
        break;
      case 422:
        console.error('Validation Error:', data.detail);
        break;
      case 429:
        console.error('Rate limit exceeded - wait and retry');
        const retryAfter = error.response?.headers['retry-after'];
        console.log(`Retry after ${retryAfter} seconds`);
        break;
      case 500:
        console.error('Server error:', data.detail);
        break;
      default:
        console.error('Unknown error:', error);
    }
  }
}
```

---

## API Documentation

### Interactive Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Contracts
- **Story 3.2 Contract:** `/docs/contracts/story-3.2-contract.md`
- **Epic 3 Contract:** `/docs/contracts/epic-3-api-contract.md`

---

## Rate Limiting

**Be aware of rate limits:**
- Default: 100 requests/minute per user
- Recommendations: 10 requests/minute
- Include proper error handling for 429 responses

**Rate limit headers:**
```
X-RateLimit-Limit-User: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699632000
```

---

## Authentication

**All protected endpoints require:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Token expires after 24 hours.** Use refresh token to get new access token:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

---

## Need Help?

1. **Check Documentation:** Visit `/docs` for interactive API documentation
2. **Review Contracts:** Check `/docs/contracts/` for detailed specifications
3. **Check Health:** `GET /health` to verify API status
4. **Review Logs:** Request IDs are in `X-Request-ID` header for debugging

---

**Happy Coding!**

The TreeBeard API is ready to power your energy recommendation application. Start building amazing user experiences!
