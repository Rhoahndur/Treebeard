# AI Energy Plan Recommendation Agent - Architecture Diagrams

## System Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Browser]
        MOBILE[Mobile Browser]
    end

    subgraph "CDN Layer"
        CDN[CloudFront/Cloud CDN]
    end

    subgraph "Frontend Layer"
        REACT[React Application]
        STATIC[Static Assets]
    end

    subgraph "API Gateway"
        APIGW[API Gateway/Load Balancer]
        AUTH[Authentication Service]
        RATELIMIT[Rate Limiter]
    end

    subgraph "Backend Services"
        API[FastAPI Backend]
        RECOMMEND[Recommendation Engine]
        ANALYZE[Usage Analysis Service]
        EXPLAIN[Explanation Generator]
        CALC[Cost Calculator]
        RISK[Risk Detection Service]
    end

    subgraph "AI/ML Layer"
        CLAUDE[Claude API]
        ML[ML Models]
    end

    subgraph "Data Layer"
        POSTGRES[(PostgreSQL)]
        REDIS[(Redis Cache)]
        S3[Object Storage]
    end

    subgraph "External Services"
        UTILITY[Utility APIs]
        SUPPLIER[Supplier Data APIs]
        ANALYTICS[Analytics Service]
        MONITORING[Monitoring/APM]
        SENTRY[Error Tracking]
    end

    WEB --> CDN
    MOBILE --> CDN
    CDN --> REACT
    CDN --> STATIC
    
    REACT --> APIGW
    APIGW --> AUTH
    APIGW --> RATELIMIT
    RATELIMIT --> API
    
    API --> RECOMMEND
    API --> ANALYZE
    API --> EXPLAIN
    API --> CALC
    API --> RISK
    
    RECOMMEND --> ML
    EXPLAIN --> CLAUDE
    
    API --> POSTGRES
    API --> REDIS
    API --> S3
    
    ANALYZE --> POSTGRES
    CALC --> POSTGRES
    RECOMMEND --> POSTGRES
    RECOMMEND --> REDIS
    
    API --> UTILITY
    API --> SUPPLIER
    API --> ANALYTICS
    API --> MONITORING
    API --> SENTRY

    style WEB fill:#e1f5ff
    style MOBILE fill:#e1f5ff
    style CDN fill:#fff3e0
    style REACT fill:#e8f5e9
    style API fill:#f3e5f5
    style POSTGRES fill:#ffebee
    style REDIS fill:#fff9c4
    style CLAUDE fill:#e0f2f1
```

## Detailed Component Architecture

```mermaid
graph TB
    subgraph "Frontend Components"
        LANDING[Landing Page]
        ONBOARD[Onboarding Flow]
        PREFFORM[Preference Form]
        UPLOAD[Data Upload]
        RESULTS[Results Display]
        COMPARE[Comparison View]
        CHARTS[Visualization Charts]
    end

    subgraph "API Endpoints"
        AUTH_EP[/auth/*]
        USER_EP[/users/*]
        REC_EP[/recommendations/*]
        PLAN_EP[/plans/*]
        UPLOAD_EP[/usage/*]
        FEEDBACK_EP[/feedback/*]
    end

    subgraph "Business Logic Layer"
        subgraph "Core Engine"
            PROFILER[Usage Profiler]
            MATCHER[Plan Matcher]
            RANKER[Plan Ranker]
            SCORER[Scoring Algorithm]
        end
        
        subgraph "Calculators"
            COST_CALC[Cost Calculator]
            SAVINGS_CALC[Savings Calculator]
            BREAKEVEN[Break-even Analyzer]
        end
        
        subgraph "AI Services"
            NLG[Explanation Generator]
            PERSONALIZE[Personalization Engine]
        end
        
        subgraph "Safety"
            VALIDATOR[Data Validator]
            RISK_DETECT[Risk Detector]
            QUALITY[Data Quality Checker]
        end
    end

    subgraph "Data Access Layer"
        USER_DAO[User DAO]
        USAGE_DAO[Usage DAO]
        PLAN_DAO[Plan DAO]
        PREF_DAO[Preference DAO]
        CACHE_SERVICE[Cache Service]
    end

    subgraph "Data Storage"
        USER_DB[(Users Table)]
        USAGE_DB[(Usage History)]
        PLAN_DB[(Plan Catalog)]
        PREF_DB[(Preferences)]
        REC_DB[(Recommendations)]
        FEEDBACK_DB[(Feedback)]
        CACHE[(Redis)]
    end

    LANDING --> ONBOARD
    ONBOARD --> PREFFORM
    ONBOARD --> UPLOAD
    PREFFORM --> REC_EP
    UPLOAD --> UPLOAD_EP
    RESULTS --> COMPARE
    RESULTS --> CHARTS

    REC_EP --> PROFILER
    PROFILER --> MATCHER
    MATCHER --> RANKER
    RANKER --> SCORER
    
    SCORER --> COST_CALC
    COST_CALC --> SAVINGS_CALC
    SAVINGS_CALC --> BREAKEVEN
    
    RANKER --> NLG
    NLG --> PERSONALIZE
    
    PROFILER --> VALIDATOR
    RANKER --> RISK_DETECT
    VALIDATOR --> QUALITY

    PROFILER --> USAGE_DAO
    MATCHER --> PLAN_DAO
    SCORER --> PREF_DAO
    
    USAGE_DAO --> USAGE_DB
    PLAN_DAO --> PLAN_DB
    PREF_DAO --> PREF_DB
    USER_DAO --> USER_DB
    
    CACHE_SERVICE --> CACHE
    PLAN_DAO --> CACHE_SERVICE
    RANKER --> CACHE_SERVICE

    style LANDING fill:#e3f2fd
    style RESULTS fill:#e8f5e9
    style PROFILER fill:#fff3e0
    style MATCHER fill:#f3e5f5
    style NLG fill:#e0f2f1
    style CACHE fill:#fff9c4
```

## Data Flow Diagram - Recommendation Generation

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Analyzer
    participant Matcher
    participant Calculator
    participant ExplainGen
    participant Database
    participant Cache
    participant ClaudeAPI

    User->>Frontend: Complete onboarding
    Frontend->>API: POST /recommendations/generate
    
    API->>Cache: Check cached recommendations
    alt Cache Hit
        Cache-->>API: Return cached data
        API-->>Frontend: Return recommendations
    else Cache Miss
        API->>Database: Fetch user data
        Database-->>API: User, usage, preferences
        
        API->>Analyzer: Analyze usage patterns
        Analyzer->>Analyzer: Detect seasonal patterns
        Analyzer->>Analyzer: Calculate projections
        Analyzer-->>API: Usage profile
        
        API->>Database: Fetch plan catalog
        Database-->>API: Available plans
        
        API->>Matcher: Match plans to profile
        Matcher->>Matcher: Score each plan
        Matcher->>Matcher: Apply preference weights
        Matcher->>Matcher: Rank plans
        Matcher-->>API: Top 3 plans
        
        API->>Calculator: Calculate costs & savings
        Calculator->>Calculator: Project annual costs
        Calculator->>Calculator: Compare to current
        Calculator->>Calculator: Calculate break-even
        Calculator-->>API: Cost analysis
        
        API->>ExplainGen: Generate explanations
        ExplainGen->>ClaudeAPI: Request explanation
        ClaudeAPI-->>ExplainGen: Generated text
        ExplainGen->>ExplainGen: Personalize message
        ExplainGen-->>API: Explanations
        
        API->>Database: Store recommendations
        API->>Cache: Cache results (24h TTL)
        API-->>Frontend: Return recommendations
    end
    
    Frontend->>Frontend: Render plan cards
    Frontend-->>User: Display recommendations
```

## Database Schema Diagram

```mermaid
erDiagram
    USERS ||--o{ USAGE_HISTORY : has
    USERS ||--|| USER_PREFERENCES : has
    USERS ||--|| CURRENT_PLANS : has
    USERS ||--o{ RECOMMENDATIONS : receives
    USERS ||--o{ FEEDBACK : provides
    
    RECOMMENDATIONS ||--|{ RECOMMENDATION_PLANS : contains
    PLAN_CATALOG ||--o{ RECOMMENDATION_PLANS : includes
    PLAN_CATALOG }o--|| SUPPLIERS : from
    
    USERS {
        uuid id PK
        string email
        string name
        string zip_code
        string property_type
        timestamp created_at
        timestamp updated_at
        boolean consent_given
    }
    
    USAGE_HISTORY {
        uuid id PK
        uuid user_id FK
        date usage_date
        decimal kwh_consumed
        string data_source
        timestamp created_at
    }
    
    USER_PREFERENCES {
        uuid id PK
        uuid user_id FK
        int cost_priority
        int flexibility_priority
        int renewable_priority
        int rating_priority
        timestamp updated_at
    }
    
    CURRENT_PLANS {
        uuid id PK
        uuid user_id FK
        string supplier_name
        decimal current_rate
        date contract_end_date
        decimal early_termination_fee
        date plan_start_date
        timestamp created_at
    }
    
    PLAN_CATALOG {
        uuid id PK
        uuid supplier_id FK
        string plan_name
        string plan_type
        jsonb rate_structure
        int contract_length_months
        decimal early_termination_fee
        decimal renewable_percentage
        decimal monthly_fee
        decimal connection_fee
        string[] available_regions
        boolean is_active
        timestamp last_updated
    }
    
    SUPPLIERS {
        uuid id PK
        string supplier_name
        decimal average_rating
        int review_count
        string website
        timestamp created_at
    }
    
    RECOMMENDATIONS {
        uuid id PK
        uuid user_id FK
        jsonb usage_profile
        timestamp generated_at
        timestamp expires_at
    }
    
    RECOMMENDATION_PLANS {
        uuid id PK
        uuid recommendation_id FK
        uuid plan_id FK
        int rank
        decimal composite_score
        decimal projected_annual_cost
        decimal projected_annual_savings
        text explanation
        jsonb risk_flags
    }
    
    FEEDBACK {
        uuid id PK
        uuid user_id FK
        uuid recommendation_id FK
        uuid plan_id FK
        int rating
        text feedback_text
        string feedback_type
        decimal sentiment_score
        timestamp created_at
    }
```

## Recommendation Algorithm Flow

```mermaid
flowchart TD
    START([Start Recommendation Process]) --> LOAD_DATA[Load User Data]
    LOAD_DATA --> CHECK_DATA{Data Complete?}
    
    CHECK_DATA -->|No| FLAG_QUALITY[Flag Data Quality Issues]
    CHECK_DATA -->|Yes| ANALYZE
    FLAG_QUALITY --> ANALYZE[Analyze Usage Patterns]
    
    ANALYZE --> SEASONAL[Detect Seasonal Patterns]
    SEASONAL --> CLASSIFY[Classify User Profile]
    CLASSIFY --> PROJECT[Project 12-Month Usage]
    
    PROJECT --> LOAD_PLANS[Load Available Plans]
    LOAD_PLANS --> FILTER[Filter by Region]
    
    FILTER --> SCORE_LOOP{More Plans?}
    SCORE_LOOP -->|Yes| CALC_COST[Calculate Plan Cost]
    CALC_COST --> SCORE_FACTORS[Score Multiple Factors]
    
    SCORE_FACTORS --> COST_SCORE[Cost Score]
    SCORE_FACTORS --> FLEX_SCORE[Flexibility Score]
    SCORE_FACTORS --> RENEW_SCORE[Renewable Score]
    SCORE_FACTORS --> RATING_SCORE[Rating Score]
    
    COST_SCORE --> COMPOSITE[Calculate Composite Score]
    FLEX_SCORE --> COMPOSITE
    RENEW_SCORE --> COMPOSITE
    RATING_SCORE --> COMPOSITE
    
    COMPOSITE --> WEIGHT[Apply User Weights]
    WEIGHT --> STORE_SCORE[Store Plan Score]
    STORE_SCORE --> SCORE_LOOP
    
    SCORE_LOOP -->|No| RANK[Rank All Plans]
    RANK --> CHECK_CONTRACT[Check Contract Timing]
    CHECK_CONTRACT --> CALC_SWITCH[Calculate Switching Costs]
    CALC_SWITCH --> SELECT_TOP[Select Top 3]
    
    SELECT_TOP --> DETECT_RISK[Detect Risk Factors]
    DETECT_RISK --> HIGH_ETF{High ETF?}
    HIGH_ETF -->|Yes| ADD_WARNING[Add ETF Warning]
    HIGH_ETF -->|No| LOW_SAVINGS
    
    ADD_WARNING --> LOW_SAVINGS{Low Savings?}
    LOW_SAVINGS -->|Yes| ADD_WARNING2[Add Savings Warning]
    LOW_SAVINGS -->|No| GEN_EXPLAIN
    
    ADD_WARNING2 --> GEN_EXPLAIN[Generate Explanations]
    GEN_EXPLAIN --> PERSONALIZE[Personalize Messages]
    PERSONALIZE --> CHECK_STAY{Stay Better?}
    
    CHECK_STAY -->|Yes| RECOMMEND_STAY[Recommend Current Plan]
    CHECK_STAY -->|No| RETURN_RECS[Return Top 3 Plans]
    
    RECOMMEND_STAY --> END([End])
    RETURN_RECS --> END

    style START fill:#e8f5e9
    style END fill:#ffebee
    style ANALYZE fill:#e3f2fd
    style SCORE_FACTORS fill:#fff3e0
    style DETECT_RISK fill:#fce4ec
    style GEN_EXPLAIN fill:#e0f2f1
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment - AWS/GCP"
        subgraph "Region: US-East"
            subgraph "Availability Zone 1"
                LB1[Load Balancer]
                API1[API Server 1]
                API2[API Server 2]
                WORKER1[Background Worker 1]
            end
            
            subgraph "Availability Zone 2"
                API3[API Server 3]
                API4[API Server 4]
                WORKER2[Background Worker 2]
            end
            
            subgraph "Managed Services"
                RDS[(RDS PostgreSQL<br/>Multi-AZ)]
                ELASTICACHE[(ElastiCache Redis<br/>Cluster Mode)]
                S3_PROD[S3 Bucket]
            end
        end
        
        subgraph "CDN & Edge"
            CLOUDFRONT[CloudFront Distribution]
            WAF[Web Application Firewall]
        end
        
        subgraph "Monitoring"
            CLOUDWATCH[CloudWatch]
            DATADOG[DataDog APM]
            SENTRY_PROD[Sentry]
        end
    end
    
    subgraph "Staging Environment"
        LB_STAGE[Load Balancer]
        API_STAGE[API Server]
        RDS_STAGE[(RDS PostgreSQL)]
        REDIS_STAGE[(Redis)]
    end
    
    subgraph "CI/CD Pipeline"
        GITHUB[GitHub Repository]
        ACTIONS[GitHub Actions]
        TEST[Automated Tests]
        BUILD[Build & Package]
        DEPLOY[Deploy to Staging]
        APPROVE[Manual Approval]
        PROD_DEPLOY[Deploy to Production]
    end
    
    subgraph "External Services"
        CLAUDE_API[Claude API]
        UTILITY_API[Utility APIs]
        SUPPLIER_API[Supplier APIs]
        ANALYTICS_EXT[Google Analytics]
    end
    
    CLOUDFRONT --> WAF
    WAF --> LB1
    LB1 --> API1
    LB1 --> API2
    LB1 --> API3
    LB1 --> API4
    
    API1 --> RDS
    API2 --> RDS
    API3 --> RDS
    API4 --> RDS
    
    API1 --> ELASTICACHE
    API2 --> ELASTICACHE
    API3 --> ELASTICACHE
    API4 --> ELASTICACHE
    
    API1 --> S3_PROD
    WORKER1 --> RDS
    WORKER2 --> RDS
    
    API1 --> CLOUDWATCH
    API1 --> DATADOG
    API1 --> SENTRY_PROD
    
    API1 --> CLAUDE_API
    API1 --> UTILITY_API
    API1 --> SUPPLIER_API
    
    GITHUB --> ACTIONS
    ACTIONS --> TEST
    TEST --> BUILD
    BUILD --> DEPLOY
    DEPLOY --> LB_STAGE
    LB_STAGE --> API_STAGE
    API_STAGE --> RDS_STAGE
    API_STAGE --> REDIS_STAGE
    
    DEPLOY --> APPROVE
    APPROVE --> PROD_DEPLOY
    PROD_DEPLOY --> LB1

    style CLOUDFRONT fill:#ff9800
    style RDS fill:#e91e63
    style ELASTICACHE fill:#ffc107
    style API1 fill:#4caf50
    style DATADOG fill:#2196f3
    style GITHUB fill:#333
```

## Security Architecture

```mermaid
graph TB
    subgraph "Internet"
        USER[End User]
        ATTACKER[Potential Attacker]
    end
    
    subgraph "Edge Security"
        DDOS[DDoS Protection<br/>CloudFlare]
        WAF[Web Application Firewall]
        CDN[CDN with SSL/TLS]
    end
    
    subgraph "Application Security"
        APIGW[API Gateway]
        AUTH[Authentication<br/>JWT/OAuth2]
        RATELIMIT[Rate Limiting]
        INPUTVAL[Input Validation]
        RBAC[Role-Based Access]
    end
    
    subgraph "Data Security"
        ENCRYPT_TRANSIT[Encryption in Transit<br/>TLS 1.3]
        ENCRYPT_REST[Encryption at Rest<br/>AES-256]
        TOKENIZE[PII Tokenization]
        HASH[Password Hashing<br/>bcrypt]
    end
    
    subgraph "Network Security"
        VPC[Virtual Private Cloud]
        SUBNET_PUB[Public Subnet]
        SUBNET_PRIV[Private Subnet]
        SUBNET_DATA[Data Subnet]
        NACL[Network ACLs]
        SG[Security Groups]
    end
    
    subgraph "Monitoring & Response"
        IDS[Intrusion Detection]
        AUDIT[Audit Logging]
        ALERT[Security Alerts]
        INCIDENT[Incident Response]
    end
    
    subgraph "Compliance"
        GDPR[GDPR Controls]
        CCPA[CCPA Controls]
        SOC2[SOC 2 Controls]
    end
    
    USER --> DDOS
    ATTACKER -.Block.-> DDOS
    DDOS --> WAF
    WAF --> CDN
    CDN --> APIGW
    
    APIGW --> AUTH
    APIGW --> RATELIMIT
    APIGW --> INPUTVAL
    AUTH --> RBAC
    
    APIGW --> VPC
    VPC --> SUBNET_PUB
    SUBNET_PUB --> SUBNET_PRIV
    SUBNET_PRIV --> SUBNET_DATA
    
    NACL --> SUBNET_PUB
    SG --> SUBNET_PRIV
    SG --> SUBNET_DATA
    
    SUBNET_DATA --> ENCRYPT_REST
    APIGW --> ENCRYPT_TRANSIT
    ENCRYPT_REST --> TOKENIZE
    AUTH --> HASH
    
    SUBNET_PRIV --> IDS
    IDS --> AUDIT
    AUDIT --> ALERT
    ALERT --> INCIDENT
    
    ENCRYPT_REST --> GDPR
    TOKENIZE --> CCPA
    AUDIT --> SOC2

    style DDOS fill:#f44336
    style WAF fill:#ff5722
    style AUTH fill:#4caf50
    style ENCRYPT_REST fill:#2196f3
    style GDPR fill:#9c27b0
```

## Caching Strategy

```mermaid
graph LR
    subgraph "Request Flow with Caching"
        REQ[API Request] --> CHECK_CACHE{Cache Hit?}
        
        CHECK_CACHE -->|Yes| RETURN_CACHED[Return Cached Data]
        CHECK_CACHE -->|No| PROCESS[Process Request]
        
        PROCESS --> QUERY_DB[Query Database]
        QUERY_DB --> COMPUTE[Compute Results]
        COMPUTE --> STORE_CACHE[Store in Cache]
        STORE_CACHE --> RETURN_FRESH[Return Fresh Data]
    end
    
    subgraph "Cache Layers"
        L1[L1: Browser Cache<br/>Static Assets]
        L2[L2: CDN Cache<br/>Public Content]
        L3[L3: API Response Cache<br/>Redis]
        L4[L4: Database Query Cache<br/>PostgreSQL]
    end
    
    subgraph "Cache Keys & TTL"
        KEY1["plan_catalog:{region}<br/>TTL: 1 hour"]
        KEY2["recommendations:{user_id}<br/>TTL: 24 hours"]
        KEY3["user_profile:{user_id}<br/>TTL: 24 hours"]
        KEY4["analysis:{user_id}<br/>TTL: 1 week"]
    end
    
    subgraph "Cache Invalidation"
        INV1[User Data Change] --> CLEAR1[Clear User Caches]
        INV2[Catalog Update] --> CLEAR2[Clear Plan Caches]
        INV3[Preference Change] --> CLEAR3[Clear Recommendation Cache]
        INV4[Manual Trigger] --> CLEAR4[Clear All Caches]
    end
    
    REQ --> L1
    L1 --> L2
    L2 --> L3
    L3 --> L4
    
    style CHECK_CACHE fill:#fff3e0
    style RETURN_CACHED fill:#c8e6c9
    style L3 fill:#fff9c4
    style KEY2 fill:#e1f5fe
```

## Monitoring & Observability

```mermaid
graph TB
    subgraph "Application"
        API[API Services]
        FRONTEND[Frontend App]
        WORKERS[Background Workers]
    end
    
    subgraph "Metrics Collection"
        METRICS[Custom Metrics]
        TRACES[Distributed Traces]
        LOGS[Application Logs]
        ERRORS[Error Events]
    end
    
    subgraph "Monitoring Tools"
        APM[DataDog APM]
        SENTRY[Sentry]
        CLOUDWATCH[CloudWatch]
        ANALYTICS[Google Analytics]
    end
    
    subgraph "Dashboards"
        PERF_DASH[Performance Dashboard]
        BIZ_DASH[Business Metrics Dashboard]
        ERROR_DASH[Error Dashboard]
        INFRA_DASH[Infrastructure Dashboard]
    end
    
    subgraph "Alerting"
        ALERT_RULES[Alert Rules]
        PAGERDUTY[PagerDuty]
        SLACK[Slack Notifications]
        EMAIL[Email Alerts]
    end
    
    subgraph "Key Metrics"
        LATENCY[API Latency<br/>P50, P95, P99]
        THROUGHPUT[Requests/sec]
        ERROR_RATE[Error Rate]
        CONVERSION[Conversion Rate]
        UPTIME[Uptime %]
        CACHE_HIT[Cache Hit Rate]
    end
    
    API --> METRICS
    API --> TRACES
    API --> LOGS
    API --> ERRORS
    FRONTEND --> METRICS
    WORKERS --> LOGS
    
    METRICS --> APM
    TRACES --> APM
    LOGS --> CLOUDWATCH
    ERRORS --> SENTRY
    FRONTEND --> ANALYTICS
    
    APM --> PERF_DASH
    ANALYTICS --> BIZ_DASH
    SENTRY --> ERROR_DASH
    CLOUDWATCH --> INFRA_DASH
    
    PERF_DASH --> LATENCY
    PERF_DASH --> THROUGHPUT
    BIZ_DASH --> CONVERSION
    ERROR_DASH --> ERROR_RATE
    INFRA_DASH --> UPTIME
    PERF_DASH --> CACHE_HIT
    
    APM --> ALERT_RULES
    SENTRY --> ALERT_RULES
    CLOUDWATCH --> ALERT_RULES
    
    ALERT_RULES --> PAGERDUTY
    ALERT_RULES --> SLACK
    ALERT_RULES --> EMAIL

    style API fill:#4caf50
    style METRICS fill:#2196f3
    style APM fill:#ff9800
    style PERF_DASH fill:#9c27b0
    style ALERT_RULES fill:#f44336
```

## Integration Architecture

```mermaid
graph TB
    subgraph "Internal System"
        API[API Server]
        SCHEDULER[Job Scheduler]
        WEBHOOK[Webhook Handler]
    end
    
    subgraph "External Integrations"
        UTILITY[Utility Smart Meter API<br/>OAuth 2.0]
        SUPPLIER[Supplier Data Feed<br/>REST API]
        CLAUDE[Claude AI API<br/>API Key]
        PAYMENT[Payment Gateway<br/>Stripe (Future)]
    end
    
    subgraph "Analytics & Marketing"
        GA[Google Analytics<br/>Tracking]
        MIXPANEL[Mixpanel<br/>Events]
        MAILCHIMP[Email Marketing<br/>MailChimp]
        INTERCOM[Support Chat<br/>Intercom]
    end
    
    subgraph "Infrastructure Services"
        TWILIO[SMS Notifications<br/>Twilio]
        SENDGRID[Email Service<br/>SendGrid]
        S3_EXT[File Storage<br/>S3]
        CLOUDINARY[Image CDN<br/>Cloudinary]
    end
    
    subgraph "Integration Patterns"
        SYNC[Synchronous<br/>REST Calls]
        ASYNC[Asynchronous<br/>Job Queue]
        BATCH[Batch Processing<br/>Daily/Hourly]
        STREAM[Real-time<br/>Webhooks]
    end
    
    API --> UTILITY
    SCHEDULER --> SUPPLIER
    API --> CLAUDE
    
    API --> GA
    API --> MIXPANEL
    WEBHOOK --> MAILCHIMP
    API --> INTERCOM
    
    API --> TWILIO
    API --> SENDGRID
    API --> S3_EXT
    API --> CLOUDINARY
    
    API -.uses.-> SYNC
    SCHEDULER -.uses.-> ASYNC
    SCHEDULER -.uses.-> BATCH
    WEBHOOK -.uses.-> STREAM

    style UTILITY fill:#4caf50
    style CLAUDE fill:#00bcd4
    style GA fill:#ff9800
    style SYNC fill:#e1f5fe
    style ASYNC fill:#fff9c4
```

---

## Architecture Decision Records (ADRs)

### ADR-001: Database Choice - PostgreSQL
**Decision:** Use PostgreSQL as the primary database  
**Rationale:**
- Strong ACID compliance for transactional data
- Excellent JSON/JSONB support for flexible plan structures
- Mature ecosystem and tooling
- Good performance for read-heavy workloads
- Built-in full-text search capabilities

### ADR-002: Caching Strategy - Redis
**Decision:** Use Redis for distributed caching  
**Rationale:**
- In-memory performance for sub-millisecond response times
- Support for complex data structures
- Built-in TTL and expiration
- Widely supported and stable
- Good clustering support for scalability

### ADR-003: API Framework - FastAPI
**Decision:** Use FastAPI (Python) for backend API  
**Rationale:**
- Native async support for high concurrency
- Automatic API documentation (OpenAPI/Swagger)
- Strong typing with Pydantic
- Python ecosystem for ML/data science
- High performance comparable to Node.js

### ADR-004: Frontend Framework - React
**Decision:** Use React for frontend development  
**Rationale:**
- Large ecosystem and community
- Component reusability
- Strong accessibility support
- Good performance with virtual DOM
- Wide talent pool

### ADR-005: AI Service - Claude API
**Decision:** Use Claude API for explanation generation  
**Rationale:**
- Superior natural language generation
- Strong instruction-following
- Context window size supports full recommendation context
- Reliability and low latency
- Strong safety and alignment

### ADR-006: Cloud Provider - AWS or GCP
**Decision:** Use AWS or GCP (configurable)  
**Rationale:**
- Both provide comprehensive managed services
- Strong global infrastructure
- Good compliance certifications (GDPR, SOC 2)
- Mature monitoring and logging tools
- Competitive pricing with reserved instances

### ADR-007: Deployment Strategy - Containerized with Kubernetes
**Decision:** Use Docker containers with Kubernetes orchestration  
**Rationale:**
- Consistent environments across dev/stage/prod
- Easy horizontal scaling
- Rolling updates with zero downtime
- Resource isolation and limits
- Strong ecosystem (Helm, operators)

---

## Scalability Considerations

### Horizontal Scaling
```mermaid
graph LR
    LB[Load Balancer]
    
    subgraph "API Tier - Auto-scaling"
        API1[API Pod 1]
        API2[API Pod 2]
        API3[API Pod 3]
        APIN[API Pod N]
    end
    
    subgraph "Worker Tier - Auto-scaling"
        W1[Worker 1]
        W2[Worker 2]
        WN[Worker N]
    end
    
    subgraph "Data Tier"
        PRIMARY[(Primary DB)]
        REPLICA1[(Read Replica 1)]
        REPLICA2[(Read Replica 2)]
        CACHE[(Redis Cluster)]
    end
    
    LB --> API1
    LB --> API2
    LB --> API3
    LB --> APIN
    
    API1 --> PRIMARY
    API2 --> REPLICA1
    API3 --> REPLICA2
    
    API1 --> CACHE
    API2 --> CACHE
    API3 --> CACHE
    
    W1 --> PRIMARY
    W2 --> PRIMARY
    
    style LB fill:#ff9800
    style PRIMARY fill:#e91e63
    style CACHE fill:#ffc107
```

### Performance Targets
- **API Response Time:** < 2 seconds (P95)
- **Page Load Time:** < 1 second
- **Concurrent Users:** 10,000+
- **Cache Hit Rate:** > 80%
- **Database Query Time:** < 100ms (P95)
- **Uptime SLA:** 99.9%

---

**End of Architecture Diagrams**

These diagrams provide comprehensive views of the system architecture from multiple perspectives: system overview, component details, data flow, deployment, security, and scalability.
