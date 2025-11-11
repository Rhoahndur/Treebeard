# TreeBeard API - Quick Start Guide

**5-Minute Setup for Developers**

## Prerequisites

- Python 3.11+
- PostgreSQL running
- Redis running
- Claude API key

## 1. Install Dependencies

```bash
cd /Users/aleksandrgaun/Downloads/TreeBeard/src/backend
pip install -r requirements.txt
```

## 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# Minimum required:
DATABASE_URL=postgresql://treebeard:treebeard@localhost:5432/treebeard
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-super-secret-key-min-32-characters-long
CLAUDE_API_KEY=sk-ant-your-key-here
```

## 3. Run Database Migrations

```bash
# From backend directory
alembic upgrade head
```

## 4. Start the API

```bash
# Development mode (auto-reload)
uvicorn backend.api.main:app --reload

# Or with explicit path
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 5. Test the API

Open your browser to:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Quick Test Commands

### Test Health Check
```bash
curl http://localhost:8000/health
```

### Register a User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "name": "Test User",
    "zip_code": "78701"
  }'
```

Response will include `access_token` - save it!

### Upload Usage Data
```bash
curl -X POST http://localhost:8000/api/v1/usage/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "usage_data": [
      {"month": "2024-01-01", "kwh": 850},
      {"month": "2024-02-01", "kwh": 820},
      {"month": "2024-03-01", "kwh": 780},
      {"month": "2024-04-01", "kwh": 900},
      {"month": "2024-05-01", "kwh": 950},
      {"month": "2024-06-01", "kwh": 1400},
      {"month": "2024-07-01", "kwh": 1600},
      {"month": "2024-08-01", "kwh": 1500},
      {"month": "2024-09-01", "kwh": 1000},
      {"month": "2024-10-01", "kwh": 850},
      {"month": "2024-11-01", "kwh": 800},
      {"month": "2024-12-01", "kwh": 820}
    ]
  }'
```

### Generate Recommendations
```bash
curl -X POST http://localhost:8000/api/v1/recommendations/generate \
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
      {"month": "2024-04-01", "kwh": 900},
      {"month": "2024-05-01", "kwh": 950},
      {"month": "2024-06-01", "kwh": 1400},
      {"month": "2024-07-01", "kwh": 1600},
      {"month": "2024-08-01", "kwh": 1500},
      {"month": "2024-09-01", "kwh": 1000},
      {"month": "2024-10-01", "kwh": 850},
      {"month": "2024-11-01", "kwh": 800},
      {"month": "2024-12-01", "kwh": 820}
    ],
    "preferences": {
      "cost_priority": 50,
      "flexibility_priority": 20,
      "renewable_priority": 20,
      "rating_priority": 10
    }
  }'
```

## Interactive Testing

Use the interactive Swagger UI at http://localhost:8000/docs:

1. Click "Authorize" button
2. Enter: `Bearer YOUR_ACCESS_TOKEN`
3. Click "Authorize"
4. Now you can test all endpoints interactively!

## Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Create database if needed
createdb -U postgres treebeard
```

### Redis Connection Error
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Start Redis if needed
redis-server
```

### Import Errors
```bash
# Ensure you're in the correct directory
cd /Users/aleksandrgaun/Downloads/TreeBeard/src/backend

# Reinstall dependencies
pip install -r requirements.txt
```

## Documentation

- **API Contract:** `/docs/contracts/epic-3-api-contract.md`
- **API README:** `/src/backend/api/README.md`
- **Epic Summary:** `/docs/EPIC-3-COMPLETION-SUMMARY.md`
- **Interactive Docs:** http://localhost:8000/docs

## Next Steps

1. ✅ API is running
2. ✅ You can make requests
3. → Start frontend development (Epic 4)
4. → Or explore the API with Swagger UI

Happy coding! 🎉
