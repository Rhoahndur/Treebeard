# TreeBeard - AI Energy Plan Recommendation Agent

TreeBeard helps customers in deregulated energy markets find the best energy plans. It analyzes usage patterns, applies user preferences, and delivers personalized top-3 plan recommendations with AI-generated explanations, risk warnings, and savings projections.

---

## Key Features

- **Usage Analysis** - Ingests 3-24 months of consumption data, detects seasonal patterns, classifies user profiles, and projects annual usage
- **Multi-Factor Plan Scoring** - Scores plans across cost, flexibility, renewable percentage, and supplier rating, weighted by user preferences
- **Savings Calculations** - Annual/monthly savings projections, break-even analysis for switching costs, and total cost of ownership comparisons
- **AI Explanations** - Claude/OpenAI-powered natural language explanations personalized to user context
- **Risk Detection** - Flags high termination fees, low-savings situations, data quality issues, variable rate volatility, and contract timing risks
- **Admin Dashboard** - Plan/supplier management, user administration, audit logs, system statistics
- **Feedback System** - User feedback collection with sentiment analysis and analytics

---

## Technology Stack

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React 18.3 + TypeScript 5.3 |
| Build Tool | Vite 5.0 |
| Styling | Tailwind CSS 3.4 |
| Charts | Recharts 2.10 |
| Forms | React Hook Form 7.66 + Zod validation |
| HTTP | Axios 1.6 |
| Routing | React Router 6.21 |
| UI Components | Radix UI, Lucide React |
| Testing | Vitest, React Testing Library |
| Component Dev | Storybook 7.6 |

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | FastAPI 0.115 + Uvicorn |
| Language | Python 3.11+ |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic 1.14 |
| Validation | Pydantic 2.9 |
| Data Processing | Pandas, NumPy, SciPy |
| Auth | JWT (python-jose) + bcrypt |
| AI | OpenAI API (gpt-4o-mini), Claude API support |

### Infrastructure
| Component | Technology |
|-----------|-----------|
| Database | PostgreSQL 15+ |
| Cache | Redis 7+ |
| Deployment | Railway.app (Nixpacks) |
| Error Tracking | Sentry |
| APM | DataDog |
| Alerting | PagerDuty, Slack |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+ (optional, graceful fallback)

### Backend Setup
```bash
cd src/backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env            # Edit with your database URL, API keys, etc.

# Initialize database
alembic upgrade head

# Run server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
cd src/frontend
npm install

# Configure environment
cp .env.example .env            # Set VITE_API_BASE_URL

# Run dev server
npm run dev                     # Starts on http://localhost:3000
```

### Other Commands
```bash
# Frontend
npm run build                   # Production build → dist/
npm run preview                 # Preview production build on :8080
npm run test                    # Run Vitest tests
npm run storybook               # Component library on :6006

# Backend
pytest                          # Run test suite
alembic revision --autogenerate -m "description"  # Create migration
```

---

## Project Structure

```
TreeBeard/
├── src/
│   ├── backend/
│   │   ├── api/
│   │   │   ├── main.py                 # FastAPI app entry point
│   │   │   ├── routes/                 # API route handlers
│   │   │   │   ├── auth.py             # Authentication (login, register, refresh)
│   │   │   │   ├── users.py            # User profiles & preferences
│   │   │   │   ├── recommendations.py  # Recommendation generation
│   │   │   │   ├── plans.py            # Plan catalog browsing
│   │   │   │   ├── usage.py            # Usage data upload/retrieval
│   │   │   │   ├── feedback.py         # Feedback submission
│   │   │   │   ├── admin.py            # Admin operations
│   │   │   │   └── health.py           # Health checks
│   │   │   ├── middleware/             # Request pipeline middleware
│   │   │   │   ├── request_id.py       # X-Request-ID tracing
│   │   │   │   ├── logging.py          # Request/response logging
│   │   │   │   ├── audit_middleware.py  # Admin action auditing
│   │   │   │   ├── cache.py            # HTTP response caching
│   │   │   │   ├── rate_limit.py       # Per-user/IP rate limiting
│   │   │   │   ├── error_handler.py    # Global error handling
│   │   │   │   └── analytics.py        # Event tracking
│   │   │   └── auth/                   # JWT + RBAC implementation
│   │   ├── services/                   # Business logic
│   │   │   ├── recommendation_engine.py  # Plan matching & ranking
│   │   │   ├── usage_analysis.py         # Usage pattern profiling
│   │   │   ├── savings_calculator.py     # Cost projections & savings
│   │   │   ├── risk_detection.py         # Risk flagging & warnings
│   │   │   ├── explanation_service.py    # AI explanation generation (Claude)
│   │   │   ├── explanation_service_openai.py  # OpenAI fallback
│   │   │   ├── scoring_service.py        # Plan scoring algorithm
│   │   │   ├── feedback_service.py       # Feedback aggregation
│   │   │   ├── cache_service.py          # Redis caching layer
│   │   │   ├── cache_warming.py          # Cache pre-warming
│   │   │   ├── cache_optimization.py     # Cache strategy tuning
│   │   │   ├── analytics_service.py      # Usage tracking
│   │   │   ├── audit_service.py          # Audit logging
│   │   │   └── admin_service.py          # Admin operations
│   │   ├── models/                     # SQLAlchemy ORM models
│   │   ├── config/
│   │   │   ├── settings.py             # Pydantic Settings (env vars)
│   │   │   └── database.py             # Connection pooling & setup
│   │   ├── alembic/                    # Database migrations
│   │   └── requirements.txt
│   └── frontend/
│       ├── src/
│       │   ├── App.tsx                 # Root component + routing
│       │   ├── api/                    # HTTP client & API services
│       │   ├── components/
│       │   │   ├── design-system/      # Reusable UI (Button, Card, Badge, etc.)
│       │   │   ├── PlanCard/           # Recommendation card display
│       │   │   ├── OnboardingFlow/     # Registration wizard
│       │   │   ├── FileUpload/         # CSV data upload
│       │   │   ├── PreferenceSliders/  # Preference weight selectors
│       │   │   ├── CostBreakdown/      # Cost analysis visualization
│       │   │   ├── charts/             # 7+ chart types (usage, cost, savings, etc.)
│       │   │   ├── comparison/         # Plan comparison view
│       │   │   ├── FeedbackWidget/     # In-app feedback
│       │   │   ├── admin/              # Admin panel components
│       │   │   ├── auth/               # Login/signup flows
│       │   │   ├── scenarios/          # What-if analysis
│       │   │   └── export/             # PDF/CSV export
│       │   ├── hooks/                  # Custom React hooks
│       │   ├── pages/                  # Page components
│       │   ├── types/                  # TypeScript type definitions
│       │   └── utils/                  # Formatters, validation, analytics
│       ├── package.json
│       ├── vite.config.ts
│       ├── tailwind.config.js
│       └── tsconfig.json
├── tests/
│   ├── backend/                        # pytest test suite
│   │   ├── test_recommendation_engine.py
│   │   ├── test_usage_analysis.py
│   │   ├── test_savings_calculator.py
│   │   ├── test_risk_detection.py
│   │   ├── test_explanation_service.py
│   │   ├── test_feedback_api.py
│   │   ├── test_admin_api.py
│   │   ├── test_audit_logging.py
│   │   └── test_scoring_standalone.py
│   └── frontend/                       # Vitest component tests
├── docs/                               # Technical documentation
│   ├── contracts/                      # Interface contracts (12 files)
│   ├── runbooks/                       # Incident response (5 runbooks)
│   ├── execution-plan.md
│   ├── database-schema.md
│   ├── caching-strategy.md
│   ├── monitoring-setup.md
│   ├── analytics-setup.md
│   ├── performance-optimization.md
│   ├── EXPLANATION_SERVICE.md
│   └── ...
├── infrastructure/                     # Monitoring & CDN configs
│   ├── monitoring-config.yml
│   ├── alerting-config.yml
│   └── cdn-config.yml
├── dashboards/                         # Grafana dashboard JSON
├── migrations/                         # SQL performance indexes
├── scripts/                            # Utility scripts
├── architecture.md                     # System architecture diagrams
├── Procfile                            # Railway process config
└── .bmad/                              # BMad Method agent/workflow config
```

---

## API Overview

All endpoints are prefixed with `/api/v1`.

| Group | Endpoints | Description |
|-------|-----------|-------------|
| **Auth** | `POST /auth/register`, `/login`, `/refresh`, `GET /auth/me` | User registration, JWT authentication |
| **Users** | `POST /users/preferences`, `GET /users/preferences`, `PUT /users/profile` | Profile and preference management |
| **Recommendations** | `POST /recommendations/generate`, `GET /recommendations/{user_id}` | Core recommendation engine |
| **Plans** | `GET /plans/catalog`, `GET /plans/{plan_id}` | Plan catalog with filtering |
| **Usage** | `POST /usage/upload`, `GET /usage/history` | Usage data ingestion |
| **Feedback** | `POST /feedback/plan`, `POST /feedback/recommendation`, `GET /feedback/analytics` | Feedback collection |
| **Admin** | User CRUD, plan CRUD, statistics, audit logs, cache management | Admin-only operations |
| **Health** | `GET /health` | Health check with DB/Redis status |

---

## Database Schema

10 tables with PostgreSQL + JSONB for flexible rate structures:

- **users** - Profiles, auth, consent tracking
- **user_preferences** - Cost/flexibility/renewable/rating weights (0-10)
- **current_plans** - User's current energy plan details
- **usage_history** - Daily kWh consumption records
- **suppliers** - Energy company info and ratings
- **plan_catalog** - Available plans with JSONB rate structures (fixed/tiered/TOU/variable)
- **recommendations** - Recommendation sessions
- **recommendation_plans** - Top 3 plans per recommendation with scores
- **feedback** - User ratings and comments
- **audit_logs** - Admin action trail

See [docs/database-schema.md](docs/database-schema.md) for full schema documentation.

---

## Recommendation Engine Flow

1. **Usage Analysis** - Analyze 3-24 months of data, detect seasonal patterns, classify user profile, project annual consumption
2. **Plan Matching** - Filter plan catalog by region/ZIP code, calculate cost per plan based on rate structure type
3. **Multi-Factor Scoring** - Score each plan on cost, flexibility, renewable %, and supplier rating, then apply user preference weights
4. **Savings Calculation** - Compare against current plan, calculate annual savings, monthly breakdown, break-even timeline
5. **Risk Detection** - Flag high ETF, low savings, data quality issues, contract timing risks; recommend staying if risks outweigh benefits
6. **AI Explanations** - Generate personalized natural language explanations via Claude/OpenAI with template fallback

---

## Deployment

The application deploys to **Railway.app** using Nixpacks:

- **Backend**: `src/backend/railway.toml` - FastAPI on port 8000
- **Frontend**: `src/frontend/railway.toml` - Vite preview on port 8080
- **Database**: Railway PostgreSQL service
- **Cache**: Railway Redis service (optional)

See `.env.production.example` for required environment variables.

---

## Documentation

| Document | Description |
|----------|-------------|
| [architecture.md](architecture.md) | System architecture with Mermaid diagrams |
| [docs/execution-plan.md](docs/execution-plan.md) | Epic/story breakdown and parallelization strategy |
| [docs/database-schema.md](docs/database-schema.md) | Complete database schema documentation |
| [docs/caching-strategy.md](docs/caching-strategy.md) | Redis caching design and TTL policies |
| [docs/monitoring-setup.md](docs/monitoring-setup.md) | Sentry, DataDog, and metrics setup |
| [docs/EXPLANATION_SERVICE.md](docs/EXPLANATION_SERVICE.md) | AI explanation service integration guide |
| [docs/analytics-setup.md](docs/analytics-setup.md) | Event tracking and analytics |
| [docs/performance-optimization.md](docs/performance-optimization.md) | Performance tuning guide |
| [docs/agent-coordination-guide.md](docs/agent-coordination-guide.md) | Multi-agent development coordination |
| [docs/contracts/](docs/contracts/) | 12 interface contracts for cross-component boundaries |
| [docs/runbooks/](docs/runbooks/) | 5 operational incident runbooks |

---

## Performance Targets

| Metric | Target |
|--------|--------|
| API Response Time | < 2 seconds (P95) |
| Page Load Time | < 1 second |
| Cache Hit Rate | > 80% |
| Database Query Time | < 100ms (P95) |
| Concurrent Users | 10,000+ |
| Uptime SLA | 99.9% |

---

**Status:** MVP in active development
