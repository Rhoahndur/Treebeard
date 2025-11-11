# Story 8.5-8.6 Contract: Admin API with RBAC and Audit Logging

**Epic:** Wave 5 - Admin Capabilities and Audit Logging
**Stories:** 8.5 (Admin API with RBAC), 8.6 (Audit Logging System)
**Implementation Date:** 2025-11-10
**Developer:** Backend Dev #8

---

## Executive Summary

This document outlines the implementation of admin-specific API endpoints with Role-Based Access Control (RBAC) and a comprehensive audit logging system. All admin actions are tracked in an append-only audit log for compliance and security.

---

## 1. Admin API Endpoints (Story 8.5)

### 1.1 User Management

#### GET /api/v1/admin/users
List all users with pagination and filtering.

**Authentication:** Required (Admin only)

**Query Parameters:**
- `limit` (int, optional): Number of results per page (default: 50, max: 100)
- `offset` (int, optional): Number of results to skip (default: 0)
- `is_active` (bool, optional): Filter by active status
- `is_admin` (bool, optional): Filter by admin role

**Response (200):**
```json
{
  "users": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "name": "John Doe",
      "zip_code": "78701",
      "property_type": "residential",
      "is_active": true,
      "is_admin": false,
      "created_at": "2025-01-15T10:30:00Z",
      "last_login": "2025-01-20T14:25:00Z"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

**Errors:**
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not an admin user

---

#### GET /api/v1/admin/users/{user_id}
Get detailed information about a specific user.

**Authentication:** Required (Admin only)

**Path Parameters:**
- `user_id` (UUID): User ID

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "zip_code": "78701",
  "property_type": "residential",
  "is_active": true,
  "is_admin": false,
  "consent_given": true,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-20T14:25:00Z",
  "activity": {
    "total_recommendations": 5,
    "total_feedback": 3,
    "last_recommendation": "2025-01-20T10:00:00Z",
    "last_feedback": "2025-01-19T15:30:00Z",
    "usage_data_points": 365
  }
}
```

**Errors:**
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not an admin user
- `404 Not Found`: User not found

---

#### PUT /api/v1/admin/users/{user_id}/role
Update a user's admin role (promote to admin or demote to user).

**Authentication:** Required (Admin only)

**Path Parameters:**
- `user_id` (UUID): User ID

**Request Body:**
```json
{
  "is_admin": true
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "is_admin": true,
  ...
}
```

**Errors:**
- `400 Bad Request`: Cannot change own role
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not an admin user
- `404 Not Found`: User not found

**Audit Log:** Creates audit log entry with action `user_role_updated`

---

#### DELETE /api/v1/admin/users/{user_id}
Soft delete a user account (sets is_active to False).

**Authentication:** Required (Admin only)

**Path Parameters:**
- `user_id` (UUID): User ID

**Response (204):** No content

**Errors:**
- `400 Bad Request`: Cannot delete own account
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not an admin user
- `404 Not Found`: User not found

**Audit Log:** Creates audit log entry with action `user_deleted`

---

### 1.2 Plan Management

#### GET /api/v1/admin/plans
List all plans with pagination and filtering.

**Authentication:** Required (Admin only)

**Query Parameters:**
- `limit` (int, optional): Number of results per page (default: 50, max: 100)
- `offset` (int, optional): Number of results to skip (default: 0)
- `supplier_id` (UUID, optional): Filter by supplier ID
- `is_active` (bool, optional): Filter by active status

**Response (200):**
```json
{
  "plans": [
    {
      "id": "uuid",
      "supplier_id": "uuid",
      "supplier_name": "TXU Energy",
      "plan_name": "Green Choice 12",
      "plan_type": "fixed",
      "rate_structure": {"base_rate": 0.089},
      "contract_length_months": 12,
      "early_termination_fee": 150.00,
      "renewable_percentage": 100.00,
      "monthly_fee": 9.95,
      "connection_fee": null,
      "available_regions": ["78701", "78702", "78703"],
      "is_active": true,
      "plan_description": "100% renewable energy plan",
      "terms_url": "https://example.com/terms",
      "created_at": "2025-01-10T10:00:00Z",
      "updated_at": "2025-01-15T14:30:00Z",
      "last_updated": "2025-01-15T14:30:00Z"
    }
  ],
  "total": 45,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

---

#### POST /api/v1/admin/plans
Add a new plan to the catalog.

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "supplier_id": "uuid",
  "plan_name": "Green Choice 12",
  "plan_type": "fixed",
  "rate_structure": {"base_rate": 0.089},
  "contract_length_months": 12,
  "early_termination_fee": 150.00,
  "renewable_percentage": 100.00,
  "monthly_fee": 9.95,
  "connection_fee": null,
  "available_regions": ["78701", "78702"],
  "plan_description": "100% renewable energy plan",
  "terms_url": "https://example.com/terms"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "supplier_id": "uuid",
  "supplier_name": "TXU Energy",
  "plan_name": "Green Choice 12",
  ...
}
```

**Errors:**
- `400 Bad Request`: Invalid input or supplier not found
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not an admin user

**Audit Log:** Creates audit log entry with action `plan_created`

---

#### PUT /api/v1/admin/plans/{plan_id}
Update an existing plan's details.

**Authentication:** Required (Admin only)

**Path Parameters:**
- `plan_id` (UUID): Plan ID

**Request Body:** (All fields optional)
```json
{
  "plan_name": "Updated Plan Name",
  "renewable_percentage": 75.00,
  "is_active": true
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "plan_name": "Updated Plan Name",
  "renewable_percentage": 75.00,
  ...
}
```

**Errors:**
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not an admin user
- `404 Not Found`: Plan not found

**Audit Log:** Creates audit log entry with action `plan_updated`

---

#### DELETE /api/v1/admin/plans/{plan_id}
Soft delete a plan from the catalog (sets is_active to False).

**Authentication:** Required (Admin only)

**Path Parameters:**
- `plan_id` (UUID): Plan ID

**Response (204):** No content

**Errors:**
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not an admin user
- `404 Not Found`: Plan not found

**Audit Log:** Creates audit log entry with action `plan_deleted`

---

### 1.3 Recommendation Management

#### GET /api/v1/admin/recommendations
List all recommendations with pagination and filtering.

**Authentication:** Required (Admin only)

**Query Parameters:**
- `limit` (int, optional): Number of results per page (default: 50, max: 100)
- `offset` (int, optional): Number of results to skip (default: 0)
- `user_id` (UUID, optional): Filter by user ID
- `start_date` (datetime, optional): Filter by start date
- `end_date` (datetime, optional): Filter by end date

**Response (200):**
```json
{
  "recommendations": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "user_email": "user@example.com",
      "user_name": "John Doe",
      "generated_at": "2025-01-20T10:30:00Z",
      "expires_at": "2025-02-20T10:30:00Z",
      "algorithm_version": "1.0.0",
      "plan_count": 3
    }
  ],
  "total": 523,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

---

### 1.4 System Statistics

#### GET /api/v1/admin/stats
Get system-wide statistics dashboard data.

**Authentication:** Required (Admin only)

**Response (200):**
```json
{
  "total_users": 1250,
  "active_users": 1180,
  "inactive_users": 70,
  "admin_users": 5,
  "total_recommendations": 3456,
  "total_feedback": 892,
  "avg_recommendations_per_user": 2.76,
  "total_plans": 145,
  "active_plans": 132,
  "inactive_plans": 13,
  "total_suppliers": 28,
  "cache_hit_rate": 87.5,
  "api_response_time_p50": 45.2,
  "api_response_time_p95": 120.8,
  "api_response_time_p99": 250.3
}
```

---

## 2. Audit Logging System (Story 8.6)

### 2.1 Audit Log Schema

**Database Table:** `audit_logs`

**Columns:**
- `id` (UUID): Primary key
- `timestamp` (DateTime): When the action occurred (indexed)
- `admin_user_id` (UUID): ID of the admin who performed the action (indexed, nullable)
- `action` (String): Action type (indexed) - e.g., "user_role_updated", "plan_created"
- `resource_type` (String): Type of resource affected (indexed) - e.g., "user", "plan"
- `resource_id` (UUID): ID of the affected resource (indexed, nullable for bulk operations)
- `details` (JSONB): Action-specific details
- `ip_address` (String): IP address of the admin (IPv4 or IPv6)
- `user_agent` (Text): User agent string from the request

**Indexes:**
- `idx_audit_logs_timestamp`: On `timestamp`
- `idx_audit_logs_admin_user`: On `admin_user_id`
- `idx_audit_logs_action`: On `action`
- `idx_audit_logs_resource_type`: On `resource_type`
- `idx_audit_logs_resource_id`: On `resource_id`
- `idx_audit_logs_admin_timestamp`: Composite on `(admin_user_id, timestamp)`
- `idx_audit_logs_resource`: Composite on `(resource_type, resource_id)`

---

### 2.2 Audit Log Actions

**User Management Actions:**
- `user_role_updated`: Admin changed user role
- `user_deleted`: Admin soft deleted user account
- `user_restored`: Admin restored deleted user account

**Plan Management Actions:**
- `plan_created`: Admin added new plan to catalog
- `plan_updated`: Admin modified plan details
- `plan_deleted`: Admin soft deleted plan
- `plan_restored`: Admin restored deleted plan

**System Actions:**
- `bulk_operation`: Admin performed bulk actions
- `settings_updated`: System settings changed

---

### 2.3 Audit Log API Endpoints

#### GET /api/v1/admin/audit-logs
View audit logs with filtering and pagination.

**Authentication:** Required (Admin only)

**Query Parameters:**
- `limit` (int, optional): Number of results per page (default: 100, max: 500)
- `offset` (int, optional): Number of results to skip (default: 0)
- `admin_user_id` (UUID, optional): Filter by admin user ID
- `action` (string, optional): Filter by action type
- `resource_type` (string, optional): Filter by resource type
- `resource_id` (UUID, optional): Filter by resource ID
- `start_date` (datetime, optional): Filter by start date
- `end_date` (datetime, optional): Filter by end date

**Response (200):**
```json
{
  "logs": [
    {
      "id": "uuid",
      "timestamp": "2025-01-20T14:25:30Z",
      "admin_user_id": "uuid",
      "admin_email": "admin@example.com",
      "admin_name": "Admin User",
      "action": "user_role_updated",
      "resource_type": "user",
      "resource_id": "uuid",
      "details": {
        "old_role": "user",
        "new_role": "admin",
        "user_email": "promoted@example.com"
      },
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    }
  ],
  "total": 1523,
  "limit": 100,
  "offset": 0,
  "has_more": true
}
```

---

#### GET /api/v1/admin/audit-logs/stats
Get audit log statistics.

**Authentication:** Required (Admin only)

**Response (200):**
```json
{
  "total_logs": 1523,
  "total_admins": 5,
  "actions_by_type": {
    "user_role_updated": 45,
    "user_deleted": 12,
    "plan_created": 28,
    "plan_updated": 156,
    "plan_deleted": 8
  },
  "recent_activity": [
    {
      "id": "uuid",
      "timestamp": "2025-01-20T14:25:30Z",
      "admin_user_id": "uuid",
      "admin_email": "admin@example.com",
      "admin_name": "Admin User",
      "action": "user_role_updated",
      "resource_type": "user",
      "resource_id": "uuid",
      "details": {...},
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    }
  ]
}
```

---

### 2.4 Data Sanitization

The audit logging system automatically sanitizes sensitive data before storing it in the `details` field. The following keys are redacted:

**Redacted Keys:**
- `password`
- `hashed_password`
- `new_password`
- `old_password`
- `token`
- `api_key`
- `secret`
- `access_token`
- `refresh_token`
- `credit_card`
- `ssn`
- `social_security`

**Example:**
```json
// Input
{
  "email": "user@example.com",
  "password": "secret123",
  "token": "abc123"
}

// Stored
{
  "email": "user@example.com",
  "password": "[REDACTED]",
  "token": "[REDACTED]"
}
```

---

## 3. Role-Based Access Control (RBAC)

### 3.1 User Roles

**User Model Fields:**
- `is_active` (Boolean): Whether the account is active (soft delete support)
- `is_admin` (Boolean): Whether the user has admin privileges

**Role Mapping:**
- `is_admin=False`: Regular user (default)
- `is_admin=True`: Admin user

### 3.2 Admin Dependency

All admin endpoints use the `require_admin` dependency:

```python
from api.dependencies.admin import AdminUser

@router.get("/admin/users")
async def list_users(admin: AdminUser):
    # Only admins can access this endpoint
    ...
```

**Behavior:**
1. Checks if user is authenticated (via JWT)
2. Checks if user account is active
3. Checks if user has `is_admin=True`
4. Returns 403 Forbidden if any check fails

---

## 4. Security Considerations

### 4.1 Audit Log Security

1. **Append-Only:** No UPDATE or DELETE operations allowed on audit logs
2. **Tamper-Proof:** All actions are logged with timestamp, IP, and user agent
3. **Retention:** 30-day retention policy (can be configured)
4. **Data Sanitization:** Sensitive data automatically redacted

### 4.2 Admin Action Restrictions

1. **Self-Protection:** Admins cannot:
   - Change their own role
   - Delete their own account

2. **Authentication:** All admin endpoints require:
   - Valid JWT token
   - Active user account
   - Admin role

3. **IP Tracking:** All admin actions include IP address for security auditing

---

## 5. Database Migrations

### Migration 002: Add User Auth Fields
**File:** `/src/backend/alembic/versions/002_add_user_auth_fields.py`

**Changes:**
- Add `hashed_password` column to `users` table
- Add `is_active` column (default: true)
- Add `is_admin` column (default: false)
- Create indexes on `is_active` and `is_admin`

### Migration 003: Add Audit Logs
**File:** `/src/backend/alembic/versions/003_add_audit_logs.py`

**Changes:**
- Create `audit_logs` table
- Create 7 indexes for efficient querying
- Set up foreign key to `users` table (ON DELETE SET NULL)

---

## 6. Performance Considerations

### 6.1 Indexing Strategy

All frequently queried fields are indexed:
- User queries: `is_active`, `is_admin`, `email`
- Audit log queries: `timestamp`, `admin_user_id`, `action`, `resource_type`, `resource_id`
- Composite indexes for common query patterns

### 6.2 Pagination

All list endpoints support pagination:
- Default limits: 50-100 items per page
- Maximum limits: 100-500 items per page
- Offset-based pagination for simplicity

### 6.3 Caching

System statistics can be cached (5-minute TTL):
```python
# Redis cache key
cache_key = "admin:stats"
ttl = 300  # 5 minutes
```

---

## 7. Testing Strategy

### 7.1 Admin API Tests
**File:** `/tests/backend/test_admin_api.py`

**Test Coverage:**
- RBAC enforcement (403 for non-admins)
- User management (list, detail, role update, soft delete)
- Plan management (list, create, update, soft delete)
- Recommendation listing
- System statistics
- Self-protection rules

### 7.2 Audit Logging Tests
**File:** `/tests/backend/test_audit_logging.py`

**Test Coverage:**
- Audit log creation
- Data sanitization
- Querying and filtering
- Pagination
- Statistics
- Append-only constraint
- IP and user agent capture

---

## 8. Integration with Existing System

### 8.1 Middleware

**AuditMiddleware:** Automatically logs all admin API calls

**Order:**
1. RequestIDMiddleware
2. LoggingMiddleware
3. **AuditMiddleware** (NEW)
4. CacheMiddleware
5. RateLimitMiddleware
6. ErrorHandlerMiddleware

### 8.2 Main Application

**Updated:** `/src/backend/api/main.py`

**Changes:**
- Import `AuditMiddleware`
- Import `admin` router
- Add middleware to app
- Include admin router at `/api/v1/admin`

---

## 9. Example Usage

### 9.1 Promote User to Admin

```bash
# Login as admin
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=admin@example.com&password=secret"

# Get access token
ACCESS_TOKEN="eyJ..."

# Promote user
curl -X PUT http://localhost:8000/api/v1/admin/users/UUID/role \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_admin": true}'
```

### 9.2 View Audit Logs

```bash
# Get all audit logs
curl -X GET http://localhost:8000/api/v1/admin/audit-logs \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Filter by action
curl -X GET "http://localhost:8000/api/v1/admin/audit-logs?action=user_role_updated" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Get statistics
curl -X GET http://localhost:8000/api/v1/admin/audit-logs/stats \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## 10. Implementation Files

### Models
- `/src/backend/models/audit_log.py` (NEW)
- `/src/backend/models/user.py` (UPDATED - added is_admin, is_active, hashed_password)

### Schemas
- `/src/backend/schemas/admin_schemas.py` (NEW)
- `/src/backend/schemas/audit_schemas.py` (NEW)

### Services
- `/src/backend/services/admin_service.py` (NEW)
- `/src/backend/services/audit_service.py` (NEW)

### API Routes
- `/src/backend/api/routes/admin.py` (NEW)

### Dependencies
- `/src/backend/api/dependencies/admin.py` (NEW)

### Middleware
- `/src/backend/api/middleware/audit_middleware.py` (NEW)

### Migrations
- `/src/backend/alembic/versions/002_add_user_auth_fields.py` (NEW)
- `/src/backend/alembic/versions/003_add_audit_logs.py` (NEW)

### Tests
- `/tests/backend/test_admin_api.py` (NEW)
- `/tests/backend/test_audit_logging.py` (NEW)

---

## 11. Success Criteria

✅ All admin endpoints require admin role (RBAC enforced)
✅ Non-admin users receive 403 Forbidden
✅ Admin can manage users (list, view, update role, soft delete)
✅ Admin can manage plan catalog (CRUD operations)
✅ System stats endpoint returns accurate metrics
✅ All admin actions logged to audit_logs table
✅ Audit logs are append-only (no updates/deletes)
✅ Audit logs include IP address and user agent
✅ Audit log filtering and pagination work correctly
✅ All tests pass

---

## 12. Future Enhancements

1. **Audit Log Retention:** Implement automatic 30-day retention policy
2. **Cache Metrics:** Integrate Redis cache hit rate into system stats
3. **API Metrics:** Integrate APM response time metrics into system stats
4. **Bulk Operations:** Add endpoints for bulk user/plan operations
5. **Export:** Add CSV/JSON export for audit logs
6. **Alerts:** Set up alerts for suspicious admin activity
7. **Two-Factor Auth:** Add 2FA requirement for admin actions

---

**Document Version:** 1.0
**Last Updated:** 2025-11-10
**Status:** Implementation Complete
