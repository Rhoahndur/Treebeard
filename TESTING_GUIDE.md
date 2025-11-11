# TreeBeard Testing Guide
## How to Test the System Locally

**Version**: 1.0
**Date**: November 10, 2025
**Environment**: Local Development

---

## Quick Start (5 Minutes)

**Want to test right away? Follow these steps:**

1. **Start Backend**:
   ```bash
   cd src/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn api.main:app --reload
   ```

2. **Start Frontend** (new terminal):
   ```bash
   cd src/frontend
   npm install
   npm run dev
   ```

3. **Open Browser**: http://localhost:5173

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Environment Setup](#2-environment-setup)
3. [Backend Testing](#3-backend-testing)
4. [Frontend Testing](#4-frontend-testing)
5. [Integration Testing](#5-integration-testing)
6. [Manual Testing Scenarios](#6-manual-testing-scenarios)
7. [Performance Testing](#7-performance-testing)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Prerequisites

### Required Software

**Install these first:**

```bash
# Python 3.11+
python3 --version
# Should show: Python 3.11.x or higher

# Node.js 18+ and npm
node --version
npm --version
# Should show: v18.x.x or higher

# PostgreSQL 15+ (for database)
psql --version
# Should show: psql (PostgreSQL) 15.x or higher

# Redis (for caching)
redis-cli --version
# Should show: redis-cli 7.x.x or higher
```

**Installation guides if needed:**

**macOS**:
```bash
# Install Homebrew first if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install all prerequisites
brew install python@3.11 node postgresql@15 redis
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv nodejs npm postgresql-15 redis-server
```

**Windows**:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/
- PostgreSQL: https://www.postgresql.org/download/windows/
- Redis: https://github.com/microsoftarchive/redis/releases

---

## 2. Environment Setup

### Step 1: Clone/Navigate to Project

```bash
cd /Users/aleksandrgaun/Downloads/TreeBeard
```

### Step 2: Set Up PostgreSQL Database

**Start PostgreSQL**:
```bash
# macOS (Homebrew)
brew services start postgresql@15

# Ubuntu/Debian
sudo systemctl start postgresql

# Windows
# Start from Services app or pgAdmin
```

**Create Database**:
```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE treebeard_dev;
CREATE USER treebeard WITH PASSWORD 'dev_password_123';
GRANT ALL PRIVILEGES ON DATABASE treebeard_dev TO treebeard;
\q
```

**Verify Connection**:
```bash
psql -h localhost -U treebeard -d treebeard_dev
# Enter password: dev_password_123
# If successful, you'll see: treebeard_dev=#
\q
```

### Step 3: Set Up Redis Cache

**Start Redis**:
```bash
# macOS (Homebrew)
brew services start redis

# Ubuntu/Debian
sudo systemctl start redis-server

# Windows
# Start from Services or run: redis-server
```

**Verify Redis Running**:
```bash
redis-cli ping
# Should respond: PONG
```

### Step 4: Backend Environment Setup

**Create Environment File**:
```bash
cd src/backend
cp .env.example .env
```

**Edit `.env` file** (use any text editor):
```bash
# Open with nano, vim, or VS Code
nano .env
# Or: code .env
```

**Update with these values**:
```bash
# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
SECRET_KEY=dev-secret-key-change-in-production-abc123

# Database
DATABASE_URL=postgresql://treebeard:dev_password_123@localhost:5432/treebeard_dev
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=5

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_SSL=false
CACHE_TTL=3600

# Claude API (Optional for testing - will use fallback templates if not set)
ANTHROPIC_API_KEY=your-api-key-here-or-leave-blank
CLAUDE_MODEL=claude-sonnet-3.5-20241022
CLAUDE_MAX_TOKENS=1024

# JWT Authentication
JWT_SECRET_KEY=dev-jwt-secret-change-in-production-xyz789
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS (allow frontend)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
CORS_ALLOW_CREDENTIALS=true

# Rate Limiting (relaxed for development)
RATE_LIMIT_PER_USER=1000/minute
RATE_LIMIT_PER_IP=10000/hour
```

**Install Backend Dependencies**:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Run Database Migrations**:
```bash
# Initialize Alembic (if not already done)
alembic upgrade head

# You should see output like:
# INFO  [alembic.runtime.migration] Running upgrade  -> 001, initial_schema
# INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, add_user_auth_fields
# INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, add_audit_logs
```

**Verify Database Tables Created**:
```bash
psql -h localhost -U treebeard -d treebeard_dev

# List tables
\dt

# You should see:
# users, user_preferences, current_plans, usage_history,
# suppliers, plan_catalog, recommendations, recommendation_plans,
# feedback, audit_logs

\q
```

### Step 5: Frontend Environment Setup

**Create Frontend Environment File**:
```bash
cd ../../src/frontend
# You're now in /TreeBeard/src/frontend

# Create .env file
cat > .env.local << 'EOF'
VITE_API_BASE_URL=http://localhost:8000
VITE_ENVIRONMENT=development
EOF
```

**Install Frontend Dependencies**:
```bash
npm install
```

**Verify Installation**:
```bash
# Should complete without errors
# You should see: added XXX packages
```

---

## 3. Backend Testing

### Step 1: Start Backend Server

```bash
cd /Users/aleksandrgaun/Downloads/TreeBeard/src/backend

# Activate virtual environment if not already active
source venv/bin/activate

# Start server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**You should see**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Keep this terminal open!**

### Step 2: Test API Endpoints

**Open a new terminal** and test the API:

**Health Check**:
```bash
curl http://localhost:8000/api/v1/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-10T...",
  "version": "1.0.0",
  "database": "connected",
  "cache": "connected"
}
```

**API Documentation**:
Open browser: http://localhost:8000/docs

You should see **Swagger UI** with all 40+ API endpoints documented!

**Test User Registration**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User",
    "property_type": "house",
    "zip_code": "78701"
  }'
```

**Expected Response**:
```json
{
  "id": "uuid-here",
  "email": "test@example.com",
  "full_name": "Test User",
  "created_at": "...",
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Copy the `access_token` from response!**

**Test User Login**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

**Test Authenticated Endpoint** (use your token):
```bash
TOKEN="your-access-token-here"

curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### Step 3: Run Backend Unit Tests

```bash
cd /Users/aleksandrgaun/Downloads/TreeBeard

# Run all backend tests
pytest tests/backend/ -v

# Run specific test file
pytest tests/backend/test_usage_analysis.py -v

# Run with coverage report
pytest tests/backend/ --cov=src/backend --cov-report=html

# View coverage report
open htmlcov/index.html
```

**Expected Output**:
```
========================= test session starts ==========================
collected 45 items

tests/backend/test_usage_analysis.py::test_analyze_patterns PASSED
tests/backend/test_recommendation_engine.py::test_score_plan PASSED
tests/backend/test_savings_calculator.py::test_calculate_savings PASSED
...

========================= 45 passed in 12.34s ==========================
```

### Step 4: Test Backend Services Manually

**Test Usage Analysis**:
```python
# Open Python shell
cd /Users/aleksandrgaun/Downloads/TreeBeard/src/backend
source venv/bin/activate
python

# In Python shell:
from services.usage_analysis import UsageAnalysisService
from schemas.usage_schemas import MonthlyUsage
from datetime import date

service = UsageAnalysisService()

# Create sample data
usage_data = [
    MonthlyUsage(month=date(2024, 1, 1), kwh_used=850, estimated_cost=95.0),
    MonthlyUsage(month=date(2024, 2, 1), kwh_used=920, estimated_cost=102.0),
    MonthlyUsage(month=date(2024, 3, 1), kwh_used=780, estimated_cost=87.0),
    # ... more months
]

# Analyze
profile = service.analyze_usage_patterns(usage_data)
print(f"Profile Type: {profile.profile_type}")
print(f"Average Monthly Usage: {profile.average_monthly_kwh} kWh")
```

---

## 4. Frontend Testing

### Step 1: Start Frontend Development Server

```bash
cd /Users/aleksandrgaun/Downloads/TreeBeard/src/frontend

npm run dev
```

**You should see**:
```
  VITE v5.0.x  ready in 850 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

**Keep this terminal open!**

### Step 2: Open Application in Browser

**Open Browser**: http://localhost:5173

You should see the **TreeBeard homepage**!

### Step 3: Test User Flow Manually

**Create an Account**:
1. Click "Get Started" or "Sign Up"
2. Fill in registration form:
   - Email: `test2@example.com`
   - Password: `Test123!`
   - Full Name: `Test User 2`
   - Property Type: `House`
   - ZIP Code: `78701`
3. Click "Create Account"
4. **Expected**: Redirect to onboarding flow

**Onboarding Flow**:

**Step 1: User Info**
- Should be pre-filled from registration
- Click "Next"

**Step 2: Current Plan**
- Select "I have a plan"
- Supplier: `TXU Energy`
- Plan Name: `Energy Saver 12`
- Rate: `9.5` cents/kWh
- Contract Length: `12` months
- Click "Next"

**Step 3: Upload Usage Data**
- Click "Manual Entry" (easier for testing)
- Enter monthly usage for 12 months:
  - Jan: 850 kWh
  - Feb: 920 kWh
  - Mar: 780 kWh
  - Apr: 650 kWh
  - May: 1100 kWh
  - Jun: 1450 kWh
  - Jul: 1550 kWh
  - Aug: 1500 kWh
  - Sep: 1200 kWh
  - Oct: 850 kWh
  - Nov: 700 kWh
  - Dec: 800 kWh
- Click "Next"

**Step 4: Set Preferences**
- Adjust sliders (they auto-balance to 100%):
  - Cost Savings: 40%
  - Renewable Energy: 30%
  - Flexibility: 20%
  - Supplier Rating: 10%
- Or select a preset: "Budget Focused"
- Click "Next"

**Step 5: Review**
- Verify all information
- Click "Get Recommendations"

**Results Page**:
- **Expected**: Should show loading spinner, then 3 recommended plans
- Each plan should show:
  - Plan name, supplier, rate
  - Annual cost projection
  - Savings vs current plan
  - AI explanation (or template if no Claude API key)
  - "View Details" button
- **Feedback Widget**: Should appear on each plan card
- **Charts**: Monthly cost comparison, cumulative savings

**Test Plan Details**:
- Click "View Details" on any plan
- Should show:
  - Cost breakdown chart
  - 12-month projection
  - Rate structure visualization
  - Risk warnings (if any)

**Test Feedback**:
- Click thumbs up/down on a plan
- Optionally add text feedback
- Click "Submit Feedback"
- **Expected**: Success message

### Step 4: Test Admin Dashboard

**Create Admin User** (via database):
```bash
psql -h localhost -U treebeard -d treebeard_dev

-- Update your test user to admin
UPDATE users SET is_admin = true WHERE email = 'test@example.com';

\q
```

**Access Admin Dashboard**:
1. Log in as `test@example.com`
2. Navigate to: http://localhost:5173/admin
3. **Expected**: Admin dashboard with sidebar navigation

**Test Admin Features**:

**Dashboard**:
- Should show 6 stat cards (Total Users, Recommendations, etc.)
- Should show 3 charts (if mock data enabled)
- Should show recent activity feed

**Users Page** (`/admin/users`):
- Should show user table with search/filter
- Click on a user to view details
- Try updating a user's role
- Try soft-deleting a user

**Plans Page** (`/admin/plans`):
- Should show plan catalog
- Click "Add Plan" to create a new plan
- Fill in plan details and submit
- Edit an existing plan
- Delete a plan

**Audit Logs** (`/admin/audit-logs`):
- Should show all admin actions
- Test filtering by action type
- Test date range filter
- Try CSV export

### Step 5: Run Frontend Tests

```bash
cd /Users/aleksandrgaun/Downloads/TreeBeard/src/frontend

# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

**Expected Output**:
```
 ✓ src/components/PlanCard/PlanCard.test.tsx (5)
 ✓ src/components/FeedbackWidget/FeedbackWidget.test.tsx (8)
 ✓ src/hooks/useFeedback.test.ts (4)

Test Files  3 passed (3)
     Tests  17 passed (17)
```

---

## 5. Integration Testing

### Test Complete User Journey

**Run Integration Test**:
```bash
cd /Users/aleksandrgaun/Downloads/TreeBeard

# Run integration tests
pytest tests/integration/test_epic1_epic2_integration.py -v
```

**Or test manually end-to-end**:

**Step 1**: Create user via API
**Step 2**: Upload usage data via API
**Step 3**: Set preferences via API
**Step 4**: Generate recommendation via API
**Step 5**: Submit feedback via API
**Step 6**: Verify all data in database

**Script for End-to-End Test**:
```bash
# Save this as test_e2e.sh

#!/bin/bash

API_URL="http://localhost:8000/api/v1"

# 1. Register user
echo "1. Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "e2e@example.com",
    "password": "Test123!",
    "full_name": "E2E Test User",
    "property_type": "house",
    "zip_code": "78701"
  }')

TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.access_token')
USER_ID=$(echo $REGISTER_RESPONSE | jq -r '.id')

echo "✓ User created: $USER_ID"

# 2. Upload usage data
echo "2. Uploading usage data..."
curl -s -X POST "$API_URL/usage/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "usage_data": [
      {"month": "2024-01-01", "kwh_used": 850, "estimated_cost": 95.0},
      {"month": "2024-02-01", "kwh_used": 920, "estimated_cost": 102.0},
      {"month": "2024-03-01", "kwh_used": 780, "estimated_cost": 87.0},
      {"month": "2024-04-01", "kwh_used": 650, "estimated_cost": 72.0},
      {"month": "2024-05-01", "kwh_used": 1100, "estimated_cost": 123.0},
      {"month": "2024-06-01", "kwh_used": 1450, "estimated_cost": 162.0},
      {"month": "2024-07-01", "kwh_used": 1550, "estimated_cost": 173.0},
      {"month": "2024-08-01", "kwh_used": 1500, "estimated_cost": 168.0},
      {"month": "2024-09-01", "kwh_used": 1200, "estimated_cost": 134.0},
      {"month": "2024-10-01", "kwh_used": 850, "estimated_cost": 95.0},
      {"month": "2024-11-01", "kwh_used": 700, "estimated_cost": 78.0},
      {"month": "2024-12-01", "kwh_used": 800, "estimated_cost": 89.0}
    ]
  }'

echo "✓ Usage data uploaded"

# 3. Set preferences
echo "3. Setting preferences..."
curl -s -X PUT "$API_URL/users/me/preferences" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cost_priority": 40,
    "renewable_priority": 30,
    "flexibility_priority": 20,
    "rating_priority": 10
  }'

echo "✓ Preferences set"

# 4. Generate recommendations
echo "4. Generating recommendations..."
REC_RESPONSE=$(curl -s -X POST "$API_URL/recommendations/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}')

REC_ID=$(echo $REC_RESPONSE | jq -r '.id')
PLAN_COUNT=$(echo $REC_RESPONSE | jq '.ranked_plans | length')

echo "✓ Recommendations generated: $PLAN_COUNT plans"

# 5. Submit feedback
echo "5. Submitting feedback..."
curl -s -X POST "$API_URL/feedback/recommendation" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recommendation_id": "'$REC_ID'",
    "rating": 5,
    "feedback_type": "helpful",
    "feedback_text": "Great recommendations!"
  }'

echo "✓ Feedback submitted"

echo ""
echo "========================================="
echo "✅ End-to-End Test Complete!"
echo "========================================="
echo "User ID: $USER_ID"
echo "Recommendation ID: $REC_ID"
echo "Plans Recommended: $PLAN_COUNT"
```

**Run it**:
```bash
chmod +x test_e2e.sh
./test_e2e.sh
```

---

## 6. Manual Testing Scenarios

### Scenario 1: Budget-Conscious User

**User Profile**:
- Monthly usage: ~1000 kWh (consistent)
- Top priority: Cost savings (60%)
- Current plan: Expensive ($12/kWh)

**Expected Behavior**:
- Recommendation engine should prioritize low-cost plans
- AI explanation should emphasize savings in dollars
- Should show clear annual savings calculation

**Test It**:
1. Create user with these characteristics
2. Generate recommendations
3. Verify top plan has lowest annual cost
4. Verify explanation mentions "save $XXX" prominently

---

### Scenario 2: Eco-Conscious User

**User Profile**:
- Monthly usage: ~800 kWh
- Top priority: Renewable energy (70%)
- Willing to pay more for green energy

**Expected Behavior**:
- Recommendation engine should prioritize 100% renewable plans
- AI explanation should highlight renewable percentage
- May show plans that cost more but are greener

**Test It**:
1. Set renewable_priority to 70%
2. Generate recommendations
3. Verify top plans have high renewable %
4. Verify explanation discusses environmental impact

---

### Scenario 3: Seasonal User (AC in Summer)

**User Profile**:
- Monthly usage: 600 kWh (winter) → 1800 kWh (summer)
- Seasonal pattern detected
- Needs flexible plan for high summer usage

**Expected Behavior**:
- Usage analysis detects "seasonal" profile
- Projections use seasonal multipliers
- Recommendations avoid plans with low usage caps
- Risk warnings for tiered plans that penalize high usage

**Test It**:
1. Upload usage data with 3x summer spike
2. Verify profile_type = "seasonal"
3. Check recommendations avoid tiered plans
4. Verify risk warnings present if applicable

---

### Scenario 4: Admin User Management

**Admin Actions**:
- View all users
- Promote user to admin
- Soft-delete user
- View audit logs

**Test It**:
1. Log in as admin
2. Go to `/admin/users`
3. Click on a user
4. Update role to "admin"
5. Go to `/admin/audit-logs`
6. Verify "user_role_updated" action logged with details

---

## 7. Performance Testing

### Load Test with Apache Bench

**Install Apache Bench**:
```bash
# macOS (included with Apache)
which ab

# Ubuntu/Debian
sudo apt install apache2-utils
```

**Test Health Endpoint** (warm-up):
```bash
ab -n 100 -c 10 http://localhost:8000/api/v1/health
```

**Test Recommendation Generation** (with auth):
```bash
# First, get a token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123!"}' \
  | jq -r '.access_token')

# Create request file
cat > post_data.json << EOF
{}
EOF

# Run load test
ab -n 50 -c 5 -p post_data.json -T application/json \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/recommendations/generate
```

**Analyze Results**:
```
Requests per second:    10.5 [#/sec]  # Should be >5
Time per request:       476 [ms]      # Should be <2000ms (P95)
```

### Monitor Cache Performance

```bash
redis-cli

# Get cache stats
INFO stats

# Look for:
# keyspace_hits: should be increasing
# keyspace_misses: should be low
# hit rate = hits / (hits + misses)
```

### Monitor Database Performance

```bash
psql -h localhost -U treebeard -d treebeard_dev

-- Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check active connections
SELECT count(*) FROM pg_stat_activity;
```

---

## 8. Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solution: Activate virtual environment
cd src/backend
source venv/bin/activate
pip install -r requirements.txt
```

**Error**: `Could not connect to database`
```bash
# Solution: Check PostgreSQL is running
brew services list | grep postgresql
# Or: sudo systemctl status postgresql

# Verify connection manually
psql -h localhost -U treebeard -d treebeard_dev
```

**Error**: `Could not connect to Redis`
```bash
# Solution: Start Redis
brew services start redis
# Or: sudo systemctl start redis-server

# Verify
redis-cli ping
```

---

### Frontend Won't Start

**Error**: `Cannot find module 'vite'`
```bash
# Solution: Install dependencies
cd src/frontend
rm -rf node_modules package-lock.json
npm install
```

**Error**: `Port 5173 already in use`
```bash
# Solution: Kill process or use different port
lsof -ti:5173 | xargs kill -9
# Or: npm run dev -- --port 3000
```

---

### API Returns 500 Errors

**Check Backend Logs**:
```bash
# Terminal where uvicorn is running should show error traceback
# Look for Python exceptions
```

**Check Database**:
```bash
# Verify tables exist
psql -h localhost -U treebeard -d treebeard_dev -c "\dt"
```

**Check Migrations**:
```bash
cd src/backend
alembic current
# Should show latest migration

# If not, run migrations
alembic upgrade head
```

---

### Authentication Not Working

**Error**: `401 Unauthorized`

**Check Token**:
```bash
# Login and get fresh token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123!"}'
```

**Check JWT Secret**:
```bash
# Verify JWT_SECRET_KEY is set in .env
cat src/backend/.env | grep JWT_SECRET_KEY
```

---

### Claude API Not Working

**If you don't have Claude API key**:
- System will automatically use template-based fallback
- Explanations will be generic but functional
- No action needed for testing

**If you have API key but getting errors**:
```bash
# Verify API key in .env
cat src/backend/.env | grep ANTHROPIC_API_KEY

# Test API key manually
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-3.5-20241022","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}'
```

---

## Quick Testing Checklist

**Basic Functionality** (15 minutes):
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Health endpoint returns 200
- [ ] User registration works
- [ ] User login works
- [ ] Recommendation generation works (with mock data)
- [ ] Frontend displays results correctly

**Core Features** (30 minutes):
- [ ] Usage analysis detects seasonal patterns
- [ ] Recommendation engine ranks plans correctly
- [ ] Savings calculator shows accurate projections
- [ ] AI explanations generate (or fallback templates work)
- [ ] Risk detection identifies warnings
- [ ] Feedback submission works
- [ ] Admin dashboard accessible

**Performance** (15 minutes):
- [ ] API responds in <2s for recommendations
- [ ] Cache hit rate >50% (check Redis INFO)
- [ ] Database queries <100ms (check pg_stat_statements)
- [ ] Frontend loads in <2s

**Security** (10 minutes):
- [ ] Cannot access admin without admin role
- [ ] Cannot access user data without authentication
- [ ] Rate limiting works (try 100 requests rapidly)
- [ ] Input validation rejects invalid data

---

## Next Steps After Testing

Once local testing passes:

1. **Fix any issues** discovered during testing
2. **Run full test suite**: `pytest tests/ -v`
3. **Check code coverage**: `pytest --cov=src --cov-report=html`
4. **Deploy to staging** (follow DEPLOYMENT_CHECKLIST.md)
5. **Run load tests** on staging (target: 10,000+ concurrent users)
6. **Security testing** (penetration testing, OWASP scan)
7. **Production deployment**

---

## Getting Help

**Documentation**:
- API Docs: http://localhost:8000/docs (when backend running)
- Project Metrics: See `PROJECT_METRICS_REPORT.md`
- Deployment Guide: See `DEPLOYMENT_CHECKLIST.md`
- Operations: See `OPERATIONS_HANDOFF.md`

**Logs**:
- Backend: Terminal where `uvicorn` is running
- Frontend: Browser console (F12)
- Database: `psql` logs or RDS logs
- Redis: `redis-cli monitor`

---

**Happy Testing!** 🧪

If you encounter issues not covered here, check the logs and error messages carefully. Most issues are related to:
1. Services not running (PostgreSQL, Redis)
2. Environment variables not set correctly
3. Dependencies not installed
4. Database migrations not applied

