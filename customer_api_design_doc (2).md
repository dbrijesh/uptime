# Customer API Design Document
## Layered Architecture with Branch Authorization

**Version:** 1.0  
**Date:** November 6, 2025  
**Status:** Design Phase

---

## Table of Contents

1. System Overview
2. Architecture Layers
3. API Flow and Business Logic
4. API Specifications
5. Security and Authentication
6. Error Handling
7. Implementation Guidelines
8. Monitoring and Logging
9. Appendix: Mermaid Flow Diagram

---

## 1. System Overview

### 1.1 Purpose
This document describes a three-tier layered API architecture for customer data retrieval with branch-based authorization. The system provides secure, filtered access to customer information based on branch permissions and supports both account-based and criteria-based searches.

### 1.2 Architecture Pattern
The system follows a separation of concerns principle with three distinct layers:

- **Experience Layer**: External-facing API gateway handling authentication, logging, and request/response transformation
- **Business Layer**: Core business logic orchestration with four specialized APIs
- **Integration/Data Layer**: Direct AWS RDS connectivity for data access (already implemented)

### 1.3 Key Features

- Branch-based authorization with fine-grained access control
- Dual search modes: account-based and criteria-based customer lookup
- Aggregated customer data retrieval with authorization filtering
- Comprehensive audit trail and logging
- Scalable microservices architecture
- Rate limiting and throttling protection

---

## 2. Architecture Layers

### 2.1 Experience API Layer

**Base Path:** `/api/v1/`

**Primary Responsibilities:**
- JWT/OAuth token validation and authentication
- Request logging with correlation ID generation
- Rate limiting and throttling enforcement
- Input validation and sanitization
- Response transformation to external format
- Error handling with standardized responses
- API versioning management
- Cross-cutting concerns (CORS, compression, etc.)

**Technology Recommendations:**
- Node.js with Express or Fastify
- AWS API Gateway or Kong for API management
- Redis for rate limiting and session management
- Winston or Pino for structured logging

### 2.2 Business Layer APIs

**Base Path:** `/business/v1/`

The business layer consists of four core APIs that implement the business logic and orchestration:

#### 2.2.1 Branch Authorization API
**Endpoint:** `/business/v1/branch-authorization`

Validates whether the requesting branch has authorization to access customer data and returns the list of customers the branch is permitted to view.

**Key Functions:**
- Validate branch code and user credentials
- Retrieve branch permissions from data layer
- Return authorized customer ID list
- Cache authorization results for performance

#### 2.2.2 Get Account Owner API
**Endpoint:** `/business/v1/account-owner`

Retrieves the list of customer IDs associated with a specific account number.

**Key Functions:**
- Query account-customer relationships
- Handle joint accounts with multiple owners
- Validate account existence
- Return customer ID list for the account

#### 2.2.3 Get Customer List API
**Endpoint:** `/business/v1/customers/search`

Searches for customers based on name, company name, or customer ID criteria.

**Key Functions:**
- Execute fuzzy search across customer attributes
- Support partial matching
- Rank results by relevance
- Handle pagination for large result sets

#### 2.2.4 Get Customer Details API
**Endpoint:** `/business/v1/customers/:customerId`

Fetches complete customer profile including personal information, addresses, and associated accounts.

**Key Functions:**
- Retrieve comprehensive customer data
- Aggregate data from multiple tables
- Format response with all customer attributes
- Handle data not found scenarios

**Technology Recommendations:**
- Java Spring Boot or Node.js for business services
- RESTful API design principles
- Resilience4j for circuit breakers and retry logic
- Async processing with message queues for heavy operations

### 2.3 Integration/Data Layer

**Base Path:** `/data/v1/`

**Status:** Already Implemented

The data layer provides direct access to AWS RDS databases and abstracts the data access logic from business operations.

**Available Endpoints:**
- Branch authorization data retrieval
- Account-customer relationship queries
- Customer search with filtering
- Customer detail retrieval
- Transaction logging

**Technology Stack:**
- Connection pooling (HikariCP or similar)
- ORM/Query Builder (Hibernate, Sequelize, TypeORM)
- AWS RDS (PostgreSQL/MySQL)
- Database migration tools (Flyway/Liquibase)

---

## 3. API Flow and Business Logic

### 3.1 Overall Flow Description

The customer retrieval process follows a secure, multi-step validation and aggregation workflow:

1. **Authentication**: Client request arrives at Experience API with authentication token
2. **Branch Authorization**: System validates branch permissions and retrieves authorized customer list
3. **Customer Identification**: Based on search criteria (account number OR search parameters)
4. **Data Retrieval**: For each identified customer, fetch complete details
5. **Authorization Filtering**: Filter results against branch authorization list
6. **Aggregation**: Combine filtered results into response payload
7. **Response**: Return formatted response to client

### 3.2 Detailed Flow Steps

#### Step 1: Client Request Processing
- Client sends GET request to `/api/v1/customers` with query parameters
- Experience API validates authentication token (JWT/OAuth)
- If authentication fails → Return 401 Unauthorized
- If authentication succeeds → Generate correlation ID and log request

#### Step 2: Branch Authorization Check
- Experience API calls Business Layer: Branch Authorization API
- Pass branch code, user ID, and request type
- Business Layer calls Data Layer to retrieve branch permissions
- Data Layer returns authorized customer ID list
- If not authorized → Return 403 Forbidden
- If authorized → Store authorized customer list and continue

#### Step 3: Customer Identification (Fork Based on Input)

**Path A: Account Number Provided**
- Experience API calls Business Layer: Get Account Owner API
- Business Layer calls Data Layer with account number
- Data Layer queries account-customer relationship table
- Returns list of customer IDs associated with the account

**Path B: Search Criteria Provided (No Account Number)**
- Experience API calls Business Layer: Get Customer List API
- Business Layer calls Data Layer with search parameters (name, company, or customer ID)
- Data Layer performs search query with fuzzy matching
- Returns list of matching customer IDs

#### Step 4: Customer Details Retrieval
- For each customer ID from Step 3:
  - Call Business Layer: Get Customer Details API
  - Business Layer calls Data Layer to fetch complete customer profile
  - Retrieve personal info, addresses, accounts, and status
  - Store customer details in temporary collection

#### Step 5: Authorization Filtering
- For each retrieved customer:
  - Check if customer ID exists in authorized customer list from Step 2
  - If authorized → Add to final result set
  - If not authorized → Skip customer (do not include in response)

#### Step 6: Response Aggregation
- Combine all authorized customer details
- Add metadata (total count, correlation ID, timestamp)
- Transform to external API format
- Log response details (excluding PII)

#### Step 7: Return Response
- Return HTTP 200 OK with customer data array
- Include correlation ID for troubleshooting
- Client receives filtered, authorized customer list

### 3.3 Error Scenarios

- **Authentication Failure**: Return 401 at Step 1
- **Authorization Failure**: Return 403 at Step 2
- **No Customers Found**: Return 200 with empty array
- **Account Not Found**: Return 404 with appropriate message
- **Data Layer Timeout**: Return 503 Service Unavailable
- **Invalid Parameters**: Return 400 Bad Request

---

## 4. API Specifications

### 4.1 Experience Layer API

#### GET /api/v1/customers

Retrieves customer information based on account number or search criteria, filtered by branch authorization.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| accountNumber | string | No | Account number to search by |
| customerName | string | No | Customer name for search |
| companyName | string | No | Company name for search |
| customerId | string | No | Customer ID for direct lookup |

**Note:** Either `accountNumber` OR at least one of (`customerName`, `companyName`, `customerId`) must be provided.

**Request Headers:**

```
Authorization: Bearer <jwt_token>
X-Branch-Code: BR001
X-Correlation-ID: uuid-1234 (optional, generated if not provided)
Content-Type: application/json
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-11-06T10:30:00Z",
  "data": {
    "customers": [
      {
        "customerId": "CUST001",
        "personalInfo": {
          "name": "John Doe",
          "email": "john.doe@example.com",
          "phone": "+1-555-123-4567",
          "dateOfBirth": "1980-01-15"
        },
        "address": {
          "street": "123 Main Street",
          "city": "Springfield",
          "state": "IL",
          "zipCode": "62701",
          "country": "USA"
        },
        "companyName": "Acme Corporation",
        "accounts": [
          {
            "accountNumber": "ACC123456",
            "accountType": "SAVINGS",
            "balance": 15000.00,
            "currency": "USD",
            "status": "ACTIVE"
          }
        ],
        "status": "ACTIVE",
        "createdAt": "2020-01-01T00:00:00Z",
        "lastModified": "2025-11-01T10:00:00Z"
      }
    ],
    "totalCount": 1,
    "searchCriteria": {
      "accountNumber": "ACC123456"
    }
  }
}
```

**Error Responses:**

```json
// 401 Unauthorized
{
  "success": false,
  "error": {
    "code": "AUTH_001",
    "message": "Invalid or expired authentication token",
    "correlationId": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-11-06T10:30:00Z"
  }
}

// 403 Forbidden
{
  "success": false,
  "error": {
    "code": "AUTH_002",
    "message": "Branch not authorized to access customer data",
    "correlationId": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-11-06T10:30:00Z"
  }
}

// 400 Bad Request
{
  "success": false,
  "error": {
    "code": "VAL_001",
    "message": "Missing required parameters. Provide either accountNumber or search criteria",
    "correlationId": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-11-06T10:30:00Z"
  }
}
```

### 4.2 Business Layer APIs

#### 4.2.1 POST /business/v1/branch-authorization

Validates branch authorization and returns list of customers the branch can access.

**Request Body:**

```json
{
  "branchCode": "BR001",
  "userId": "USR123",
  "requestType": "CUSTOMER_DETAILS"
}
```

**Response (200 OK):**

```json
{
  "authorized": true,
  "authorizedCustomerIds": [
    "CUST001",
    "CUST002",
    "CUST003"
  ],
  "permissions": ["READ", "UPDATE"],
  "branchInfo": {
    "branchCode": "BR001",
    "branchName": "Downtown Branch",
    "region": "CENTRAL"
  },
  "expiresAt": "2025-11-06T12:00:00Z"
}
```

**Response (403 Forbidden):**

```json
{
  "authorized": false,
  "reason": "Branch does not have permissions for this request type",
  "branchCode": "BR001"
}
```

#### 4.2.2 GET /business/v1/account-owner

Retrieves customer IDs associated with an account number.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| accountNumber | string | Yes | Account number to query |

**Response (200 OK):**

```json
{
  "accountNumber": "ACC123456",
  "customerIds": [
    "CUST001",
    "CUST002"
  ],
  "accountType": "JOINT",
  "accountStatus": "ACTIVE",
  "primaryCustomerId": "CUST001",
  "openedDate": "2020-01-01"
}
```

**Response (404 Not Found):**

```json
{
  "error": "Account not found",
  "accountNumber": "ACC123456"
}
```

#### 4.2.3 GET /business/v1/customers/search

Searches for customers by name, company, or customer ID.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| customerName | string | No | Customer name (partial match) |
| companyName | string | No | Company name (partial match) |
| customerId | string | No | Exact customer ID |
| limit | integer | No | Max results (default: 50, max: 100) |
| offset | integer | No | Pagination offset (default: 0) |

**Response (200 OK):**

```json
{
  "customers": [
    {
      "customerId": "CUST001",
      "name": "John Doe",
      "companyName": "Acme Corporation",
      "email": "john.doe@example.com",
      "status": "ACTIVE",
      "matchScore": 0.95
    },
    {
      "customerId": "CUST002",
      "name": "John Smith",
      "companyName": "Smith Industries",
      "email": "john.smith@example.com",
      "status": "ACTIVE",
      "matchScore": 0.87
    }
  ],
  "totalMatches": 2,
  "limit": 50,
  "offset": 0
}
```

#### 4.2.4 GET /business/v1/customers/:customerId

Retrieves complete customer details by customer ID.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| customerId | string | Yes | Customer unique identifier |

**Response (200 OK):**

```json
{
  "customerId": "CUST001",
  "personalInfo": {
    "firstName": "John",
    "lastName": "Doe",
    "fullName": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-123-4567",
    "alternatePhone": "+1-555-987-6543",
    "dateOfBirth": "1980-01-15",
    "ssn": "***-**-4567",
    "nationality": "US"
  },
  "address": {
    "type": "PRIMARY",
    "street": "123 Main Street",
    "apartment": "Apt 4B",
    "city": "Springfield",
    "state": "IL",
    "zipCode": "62701",
    "country": "USA"
  },
  "companyInfo": {
    "companyName": "Acme Corporation",
    "position": "Senior Manager",
    "employmentStatus": "EMPLOYED"
  },
  "accounts": [
    {
      "accountNumber": "ACC123456",
      "accountType": "SAVINGS",
      "balance": 15000.00,
      "currency": "USD",
      "status": "ACTIVE",
      "openedDate": "2020-01-01",
      "lastTransactionDate": "2025-11-05"
    }
  ],
  "preferences": {
    "contactMethod": "EMAIL",
    "language": "en",
    "marketingOptIn": true
  },
  "status": "ACTIVE",
  "riskProfile": "LOW",
  "customerSince": "2020-01-01",
  "createdAt": "2020-01-01T00:00:00Z",
  "lastModified": "2025-11-01T10:00:00Z",
  "lastModifiedBy": "SYSTEM"
}
```

**Response (404 Not Found):**

```json
{
  "error": "Customer not found",
  "customerId": "CUST999"
}
```

---

## 5. Security and Authentication

### 5.1 Authentication

**Token-Based Authentication:**
- All API requests must include a valid JWT or OAuth 2.0 bearer token
- Tokens are validated at the Experience Layer
- Token validation includes:
  - Signature verification
  - Expiration check
  - Issuer validation
  - Audience validation

**Token Format:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token Claims:**
- `sub`: User ID
- `branch`: Branch code
- `role`: User role (BRANCH_MANAGER, TELLER, etc.)
- `exp`: Expiration timestamp
- `iat`: Issued at timestamp

### 5.2 Authorization

**Branch-Level Authorization:**
- Each branch has a defined list of customers they can access
- Authorization is checked before any customer data retrieval
- Authorization results are cached for 5-15 minutes to reduce load

**Customer-Level Filtering:**
- Even if customers are found, only those in the authorized list are returned
- Unauthorized customers are silently filtered from results
- No information about filtered customers is disclosed

**Permission Types:**
- `READ`: View customer information
- `UPDATE`: Modify customer information (future)
- `CREATE`: Create new customers (future)
- `DELETE`: Deactivate customers (future)

### 5.3 Data Protection

**Encryption:**
- TLS 1.3 for all API communications
- Data encryption at rest in AWS RDS
- Sensitive fields (SSN, account numbers) encrypted in database

**PII Handling:**
- Social Security Numbers (SSN) masked in logs and most responses
- Full SSN only returned with explicit permission
- Email addresses and phone numbers logged in hashed form
- Credit card information never stored or transmitted

**Input Validation:**
- All inputs validated against whitelist patterns
- SQL injection prevention through parameterized queries
- XSS prevention through input sanitization
- Maximum request size limits enforced

### 5.4 Rate Limiting

**Per-User Limits:**
- 100 requests per minute per user
- 1000 requests per hour per user
- Burst allowance: 20 requests per 10 seconds

**Per-Branch Limits:**
- 1000 requests per minute per branch
- 10,000 requests per hour per branch

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699267200
```

**Rate Limit Response (429):**
```json
{
  "success": false,
  "error": {
    "code": "RATE_001",
    "message": "Rate limit exceeded. Please try again later",
    "retryAfter": 60,
    "correlationId": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### 5.5 Circuit Breaker Pattern

**Configuration:**
- Failure threshold: 50% of requests failing
- Timeout threshold: 10 seconds per request
- Circuit open duration: 30 seconds
- Half-open test requests: 3

**States:**
- **Closed**: Normal operation, requests pass through
- **Open**: Too many failures, requests immediately fail
- **Half-Open**: Testing if service recovered

---

## 6. Error Handling

### 6.1 Standard Error Response Format

All error responses follow a consistent structure:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional context or technical details",
    "correlationId": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-11-06T10:30:00Z",
    "path": "/api/v1/customers"
  }
}
```

### 6.2 HTTP Status Codes

| Status Code | Description | When Used |
|-------------|-------------|-----------|
| 200 OK | Success | Successful request with data |
| 400 Bad Request | Invalid input | Missing or invalid parameters |
| 401 Unauthorized | Authentication failed | Invalid or missing token |
| 403 Forbidden | Not authorized | Branch lacks permissions |
| 404 Not Found | Resource not found | Customer or account doesn't exist |
| 429 Too Many Requests | Rate limited | Exceeded rate limits |
| 500 Internal Server Error | Server error | Unexpected system error |
| 503 Service Unavailable | Service down | Downstream service failure |
| 504 Gateway Timeout | Timeout | Request took too long |

### 6.3 Error Code Categories

**Authentication Errors (AUTH_xxx):**
- `AUTH_001`: Invalid or expired token
- `AUTH_002`: Missing authentication token
- `AUTH_003`: Token signature verification failed

**Authorization Errors (AUTHZ_xxx):**
- `AUTHZ_001`: Branch not authorized
- `AUTHZ_002`: Insufficient permissions
- `AUTHZ_003`: Customer access denied

**Validation Errors (VAL_xxx):**
- `VAL_001`: Missing required parameters
- `VAL_002`: Invalid parameter format
- `VAL_003`: Parameter value out of range

**Resource Errors (RES_xxx):**
- `RES_001`: Customer not found
- `RES_002`: Account not found
- `RES_003`: Resource already exists

**Rate Limiting Errors (RATE_xxx):**
- `RATE_001`: Rate limit exceeded
- `RATE_002`: Concurrent request limit exceeded

**System Errors (SYS_xxx):**
- `SYS_001`: Internal server error
- `SYS_002`: Database connection error
- `SYS_003`: Service unavailable

### 6.4 Error Handling Strategy

**Retry Logic:**
- Automatic retry for transient errors (3 attempts with exponential backoff)
- Idempotency keys for mutation operations
- No retry for client errors (4xx status codes)

**Fallback Mechanisms:**
- Return cached data if available during service outage
- Graceful degradation for non-critical features
- Circuit breaker to prevent cascade failures

**Error Logging:**
- All errors logged with correlation ID
- Stack traces logged only in non-production
- PII removed from error logs
- Error metrics tracked in monitoring system

---

## 7. Implementation Guidelines

### 7.1 Technology Stack

**Experience Layer:**
- **Framework**: Node.js with Express.js or Fastify
- **API Gateway**: AWS API Gateway or Kong
- **Rate Limiting**: Redis with sliding window algorithm
- **Caching**: Redis or AWS ElastiCache
- **Logging**: Winston or Pino with JSON formatting
- **Monitoring**: AWS CloudWatch or Datadog

**Business Layer:**
- **Framework**: Java Spring Boot or Node.js
- **API Style**: RESTful APIs
- **Resilience**: Resilience4j or Hystrix for circuit breakers
- **Async Processing**: AWS SQS or RabbitMQ
- **Service Discovery**: AWS Cloud Map or Consul
- **Configuration**: AWS Parameter Store or Vault

**Data Layer (Existing):**
- **Database**: AWS RDS (PostgreSQL or MySQL)
- **Connection Pool**: HikariCP (Java) or pg-pool (Node.js)
- **ORM**: Hibernate (Java) or Sequelize (Node.js)
- **Migrations**: Flyway or Liquibase

**Cross-Cutting:**
- **Containerization**: Docker
- **Orchestration**: AWS ECS or Kubernetes
- **Service Mesh**: AWS App Mesh (optional)
- **API Documentation**: OpenAPI/Swagger

### 7.2 Development Best Practices

**Code Organization:**
- Separate concerns: controllers, services, repositories
- Dependency injection for loose coupling
- Interface-based programming
- Unit tests with 80%+ coverage
- Integration tests for critical paths

**API Design:**
- RESTful resource naming conventions
- Consistent endpoint structure
- Semantic versioning (v1, v2, etc.)
- HATEOAS links for navigation (optional)
- Pagination for list endpoints

**Database Access:**
- Use prepared statements to prevent SQL injection
- Connection pooling for performance
- Read replicas for read-heavy operations
- Database indexing on frequently queried fields
- Query optimization and EXPLAIN analysis

**Configuration Management:**
- Environment-specific configurations
- Secrets stored in AWS Secrets Manager
- Feature flags for gradual rollout
- Externalized configuration (12-factor app)

### 7.3 Performance Optimization

**Caching Strategy:**
- Branch authorization results: 5-15 minute TTL
- Customer data: 2-5 minute TTL (for frequently accessed)
- Cache invalidation on data updates
- Distributed caching with Redis

**Parallel Processing:**
- Fetch customer details in parallel (Promise.all in Node.js)
- Use thread pools for concurrent operations
- Async/non-blocking I/O where possible
- Batch database queries when feasible

**Database Optimization:**
- Index on customerIds, accountNumbers, branchCodes
- Denormalize read-heavy data if needed
- Partition large tables by date or region
- Regular VACUUM and ANALYZE (PostgreSQL)

**Network Optimization:**
- HTTP/2 for multiplexing
- Response compression (gzip/brotli)
- Connection keep-alive
- CDN for static assets (if any)

**Timeout Configuration:**
- Experience Layer: 30 seconds total timeout
- Business Layer: 20 seconds per operation
- Data Layer: 10 seconds per query
- Circuit breaker: 5 second timeout before opening

### 7.4 Scalability Considerations

**Horizontal Scaling:**
- Stateless API design for easy scaling
- Load balancing with health checks
- Auto-scaling based on CPU/memory/request metrics
- Database read replicas for scaling reads

**Microservices Patterns:**
- Service per business capability
- API composition for aggregation
- Event-driven for async operations
- Saga pattern for distributed transactions (future)

**Data Partitioning:**
- Shard by branch or region if needed
- Separate read and write databases (CQRS pattern)
- Archive old customer data to cold storage

---

## 8. Monitoring and Logging

### 8.1 Logging Standards

**Structured Logging Format:**

```json
{
  "timestamp": "2025-11-06T10:30:00.123Z",
  "level": "INFO",
  "service": "experience-api",
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "userId": "USR123",
  "branchCode": "BR001",
  "method": "GET",
  "path": "/api/v1/customers",
  "statusCode": 200,
  "duration": 1250,
  "message": "Customer request completed successfully"
}
```

**Log Levels:**
- **ERROR**: System errors, exceptions, failures
- **WARN**: Degraded performance, missing optional data
- **INFO**: Request/response, business events
- **DEBUG**: Detailed flow information (non-production)

**PII Masking:**
- Email: j***@example.com
- Phone: +1-555-***-4567
- SSN: ***-**-4567
- Account: ACC****456

**Correlation ID:**
- Generated at Experience Layer if not provided
- Propagated to all downstream services
- Included in all log entries
- Returned in response headers

### 8.2 Metrics and KPIs

**API Metrics:**
- Request rate (requests per second)
- Error rate (percentage of failed requests)
- Latency (p50, p95, p99 response times)
- Throughput (successful requests per second)

**Business Metrics:**
- Authorization success rate
- Average customers per request
- Search result accuracy
- Cache hit ratio

**Infrastructure Metrics:**
- CPU utilization
- Memory usage
- Database connection pool status
- Network I/O

**Custom Metrics:**
- Branch authorization cache hit rate
- Parallel customer fetch efficiency
- Data layer response times
- Circuit breaker state transitions

### 8.3 Alerting

**Critical Alerts (Page immediately):**
- API availability < 99.9%
- Error rate > 5%
- p99 latency > 5 seconds
- Database connection failures
- Circuit breaker open for > 2 minutes

**Warning Alerts (Email/Slack):**
- Error rate > 1%
- p95 latency > 2 seconds
- Rate limit exceeded frequently
- Cache miss rate > 30%
- Disk space > 80%

**Alert Configuration:**
- Define clear escalation paths
- Include runbooks with alerts
- Set appropriate thresholds
- Avoid alert fatigue

### 8.4 Distributed Tracing

**Implementation:**
- AWS X-Ray or Jaeger for tracing
- Trace spans for each layer transition
- Annotate spans with business context
- Visualize request flow across services

**Trace Information:**
- Entry point and exit point timestamps
- Service-to-service call latency
- Database query execution time
- External API call duration
- Error and exception details

### 8.5 Health Checks

**Liveness Probe:**
- Endpoint: `/health/live`
- Purpose: Is the service running?
- Response: 200 OK or 503 Service Unavailable

**Readiness Probe:**
- Endpoint: `/health/ready`
- Purpose: Is the service ready to accept traffic?
- Checks: Database connectivity, downstream services
- Response: 200 OK or 503 Service Unavailable

**Detailed Health Check:**
- Endpoint: `/health/detailed` (authenticated)
- Response: Status of all dependencies

```json
{
  "status": "UP",
  "components": {
    "database": {
      "status": "UP",
      "responseTime": 45
    },
    "redis": {
      "status": "UP",
      "responseTime": 12
    },
    "businessLayer": {
      "status": "UP",
      "responseTime": 120
    }
  }
}
```

---

## 9. Appendix: Mermaid Flow Diagram

### Complete System Flow

```mermaid
graph TB
    Start([Client Request]) --> ExpAPI[Experience API<br/>/api/v1/customers]
    
    ExpAPI --> Auth{Authenticate<br/>JWT/OAuth}
    Auth -->|Invalid| AuthFail[Return 401<br/>Unauthorized]
    Auth -->|Valid| Log[Log Request<br/>Generate Correlation ID]
    
    Log --> BranchAuth[Business Layer<br/>Branch Authorization API]
    
    BranchAuth --> CheckAuth{Branch<br/>Authorized?}
    CheckAuth -->|No| NotAuth[Return 403<br/>Not Authorized]
    CheckAuth -->|Yes| StoreAuth[Store Authorized<br/>Customer List]
    
    StoreAuth --> AccCheck{Account Number<br/>Supplied?}
    
    AccCheck -->|Yes| GetAccOwner[Business Layer<br/>Get Account Owner API]
    GetAccOwner --> DataAccOwner[Data Layer<br/>Query Account-Customer<br/>Relationship]
    DataAccOwner --> CustList1[Customer ID List]
    
    AccCheck -->|No| GetCustList[Business Layer<br/>Get Customer List API]
    GetCustList --> DataCustSearch[Data Layer<br/>Search by Name/Company/ID]
    DataCustSearch --> CustList2[Customer ID List]
    
    CustList1 --> LoopStart{For Each<br/>Customer ID}
    CustList2 --> LoopStart
    
    LoopStart --> GetCustDetail[Business Layer<br/>Get Customer API]
    GetCustDetail --> DataCustDetail[Data Layer<br/>Fetch Customer Details]
    DataCustDetail --> FilterAuth{Customer in<br/>Authorized List?}
    
    FilterAuth -->|Yes| AddResult[Add to Result Set]
    FilterAuth -->|No| SkipCust[Skip Customer]
    
    AddResult --> MoreCust{More<br/>Customers?}
    SkipCust --> MoreCust
    MoreCust -->|Yes| LoopStart
    MoreCust -->|No| Aggregate[Aggregate Results]
    
    Aggregate --> LogResp[Log Response]
    LogResp --> Transform[Transform to<br/>External Format]
    Transform --> Return[Return 200 OK<br/>with Customer Data]
    
    NotAuth --> End([End])
    AuthFail --> End
    Return --> End
    
    style ExpAPI fill:#3b82f6,color:#fff
    style BranchAuth fill:#6366f1,color:#fff
    style GetAccOwner fill:#6366f1,color:#fff
    style GetCustList fill:#6366f1,color:#fff
    style GetCustDetail fill:#6366f1,color:#fff
    style DataAccOwner fill:#9333ea,color:#fff
    style DataCustSearch fill:#9333ea,color:#fff
    style DataCustDetail fill:#9333ea,color:#fff
    style Return fill:#10b981,color:#fff
    style NotAuth fill:#ef4444,color:#fff
    style AuthFail fill:#ef4444,color:#fff
```

### Layer Interaction Diagram

```mermaid
graph LR
    subgraph "Experience Layer"
        EXP[Experience API]
    end
    
    subgraph "Business Layer"
        BA[Branch Authorization API]
        AO[Account Owner API]
        CS[Customer Search API]
        CD[Customer Details API]
    end
    
    subgraph "Data Layer"
        DA[Data Access APIs]
        DB[(AWS RDS Database)]
    end
    
    EXP --> BA
    EXP --> AO
    EXP --> CS
    EXP --> CD
    
    BA --> DA
    AO --> DA
    CS --> DA
    CD --> DA
    
    DA --> DB
    
    style EXP fill:#3b82f6,color:#fff
    style BA fill:#6366f1,color:#fff
    style AO fill:#6366f1,color:#fff
    style CS fill:#6366f1,color:#fff
    style CD fill:#6366f1,color:#fff
    style DA fill:#9333ea,color:#fff
    style DB fill:#1f2937,color:#fff
```

### Decision Flow for Customer Retrieval

```mermaid
flowchart TD
    A[Start: Receive Request] --> B{Authenticated?}
    B -->|No| C[401 Unauthorized]
    B -->|Yes| D[Branch Authorization Check]
    
    D --> E{Authorized?}
    E -->|No| F[403 Forbidden]
    E -->|Yes| G{Account Number<br/>Provided?}
    
    G -->|Yes| H[Get Account Owners]
    G -->|No| I[Search Customers]
    
    H --> J[Loop Through Customers]
    I --> J
    
    J --> K[Get Customer Details]
    K --> L{In Authorized<br/>List?}
    
    L -->|Yes| M[Include in Results]
    L -->|No| N[Exclude from Results]
    
    M --> O{More Customers?}
    N --> O
    
    O -->|Yes| J
    O -->|No| P[Return Aggregated Response]
    
    C --> Q[End]
    F --> Q
    P --> Q
    
    style A fill:#60a5fa
    style P fill:#10b981
    style C fill:#ef4444
    style F fill:#ef4444
    style Q fill:#6b7280
```

---

## 10. Deployment Architecture

### 10.1 Environment Strategy

**Environments:**

| Environment | Purpose | Configuration |
|-------------|---------|---------------|
| Development | Local development and unit testing | Mock services, local DB |
| Integration | Integration testing with all services | Shared test DB |
| Staging | Pre-production testing | Production-like setup |
| Production | Live customer traffic | High availability, monitoring |

### 10.2 Infrastructure Components

**Load Balancing:**
- Application Load Balancer (ALB) for HTTP/HTTPS traffic
- Health checks on `/health/ready` endpoint
- SSL/TLS termination at load balancer
- Sticky sessions disabled (stateless APIs)

**Container Orchestration:**
- Amazon ECS with Fargate or Kubernetes (EKS)
- Auto-scaling based on CPU and request metrics
- Rolling deployment strategy with zero downtime
- Blue-green deployment for major releases

**Database Configuration:**
- AWS RDS Multi-AZ for high availability
- Read replicas for read-heavy operations
- Automated backups with 30-day retention
- Point-in-time recovery enabled

**Caching Layer:**
- Amazon ElastiCache (Redis) cluster
- Multi-node for high availability
- Separate cache for each environment
- Cache warming on deployment

### 10.3 CI/CD Pipeline

**Build Pipeline:**
1. Code commit triggers build
2. Run unit tests and code coverage
3. Static code analysis (SonarQube)
4. Security scanning (Snyk, OWASP Dependency Check)
5. Build Docker images
6. Push to container registry (ECR)

**Deployment Pipeline:**
1. Deploy to Integration environment
2. Run integration tests
3. Deploy to Staging environment
4. Run smoke tests and load tests
5. Manual approval gate
6. Deploy to Production
7. Run production smoke tests
8. Monitor key metrics for 30 minutes

**Rollback Strategy:**
- Automated rollback on health check failures
- Manual rollback capability
- Database migration rollback scripts
- Feature flags for quick disable

### 10.4 Disaster Recovery

**Backup Strategy:**
- Database: Daily automated backups
- Configuration: Versioned in Git
- Secrets: Backed up in AWS Secrets Manager

**Recovery Objectives:**
- RTO (Recovery Time Objective): 1 hour
- RPO (Recovery Point Objective): 15 minutes

**DR Procedures:**
- Database restore from backup
- Deploy from last known good version
- Failover to secondary region (if multi-region)

---

## 11. API Versioning and Deprecation

### 11.1 Versioning Strategy

**URL-Based Versioning:**
- Current version: `/api/v1/customers`
- Future versions: `/api/v2/customers`, `/api/v3/customers`

**Version Support Policy:**
- Support current and previous major version
- Minimum 12-month deprecation notice
- Security patches for deprecated versions

### 11.2 Backward Compatibility

**Non-Breaking Changes (Patch/Minor):**
- Adding new optional parameters
- Adding new fields to responses
- Adding new endpoints
- Performance improvements
- Bug fixes

**Breaking Changes (Major Version):**
- Removing fields from responses
- Changing field types
- Changing authentication methods
- Removing endpoints
- Changing error response format

### 11.3 Deprecation Process

1. Announce deprecation with 12-month notice
2. Add deprecation headers to old version:
   ```
   Sunset: Sat, 01 Nov 2026 00:00:00 GMT
   Deprecation: true
   Link: </api/v2/customers>; rel="successor-version"
   ```
3. Update documentation with migration guide
4. Monitor usage of deprecated endpoints
5. Send notifications to API consumers
6. Decommission after sunset date

---

## 12. Testing Strategy

### 12.1 Unit Testing

**Coverage Requirements:**
- Minimum 80% code coverage
- 100% coverage for business logic
- Test all error paths
- Mock external dependencies

**Test Framework:**
- Java: JUnit 5, Mockito
- Node.js: Jest, Mocha

**Sample Unit Tests:**
- Branch authorization validation
- Customer filtering logic
- Input validation
- Error handling
- Data transformation

### 12.2 Integration Testing

**Scope:**
- API endpoint testing with real database
- Service-to-service communication
- Database queries and transactions
- Cache behavior
- Authentication and authorization flow

**Test Data:**
- Dedicated test database
- Known test customers and accounts
- Test branch configurations
- Test users with various permissions

**Test Scenarios:**
- Successful customer retrieval by account
- Successful customer search by name
- Branch authorization failure
- Account not found
- Empty search results
- Rate limit enforcement
- Concurrent requests

### 12.3 Performance Testing

**Load Testing:**
- Target: 1000 requests per second
- Concurrent users: 500
- Test duration: 30 minutes
- Tool: JMeter, Gatling, or k6

**Stress Testing:**
- Gradually increase load until system breaks
- Identify bottlenecks
- Measure recovery time

**Endurance Testing:**
- Sustained load for 24 hours
- Monitor for memory leaks
- Database connection pool behavior

**Performance Benchmarks:**
- p50 latency: < 200ms
- p95 latency: < 500ms
- p99 latency: < 1000ms
- Error rate: < 0.1%

### 12.4 Security Testing

**OWASP Top 10 Testing:**
- SQL Injection attempts
- Authentication bypass attempts
- Authorization bypass attempts
- XSS prevention validation
- CSRF protection (if applicable)

**Penetration Testing:**
- Annual third-party pen testing
- Automated security scans weekly
- Dependency vulnerability scanning

**Security Test Cases:**
- Invalid JWT tokens
- Expired tokens
- Token without required claims
- Attempt to access unauthorized customers
- Attempt to bypass branch authorization
- Rate limit bypass attempts

---

## 13. Documentation and API Governance

### 13.1 API Documentation

**OpenAPI/Swagger Specification:**
- Complete API specification in OpenAPI 3.0 format
- Interactive documentation with Swagger UI
- Code generation for client SDKs
- Automated documentation deployment

**Developer Portal:**
- Getting started guide
- Authentication guide
- Code examples in multiple languages
- Postman collection
- FAQ and troubleshooting

**Change Log:**
- Maintain detailed change log for each version
- Breaking vs non-breaking changes
- Migration guides between versions

### 13.2 API Governance

**Design Standards:**
- RESTful API design principles
- Consistent naming conventions
- Standard error response format
- Pagination standards
- Filtering and sorting standards

**Review Process:**
- API design review before implementation
- Security review for all changes
- Performance review for new endpoints
- Documentation review

**API Lifecycle:**
- Design → Review → Implement → Test → Deploy → Monitor → Deprecate

### 13.3 Client SDK Support

**Supported Languages:**
- Java
- Python
- Node.js
- C#

**SDK Features:**
- Type-safe API clients
- Automatic retry logic
- Built-in authentication
- Error handling
- Request/response logging

---

## 14. Compliance and Audit

### 14.1 Regulatory Compliance

**Data Privacy:**
- GDPR compliance for EU customers
- CCPA compliance for California customers
- Right to access customer data
- Right to deletion (data retention policies)

**Financial Regulations:**
- SOC 2 Type II compliance
- PCI DSS compliance (if handling payments)
- Know Your Customer (KYC) data handling

**Audit Trail:**
- All customer data access logged
- Who accessed what, when, and why
- Retention: 7 years for audit logs
- Immutable audit logs

### 14.2 Data Retention

**Customer Data:**
- Active customers: Retained indefinitely
- Inactive customers: Archived after 5 years
- Deleted customers: Anonymized, retain for 7 years

**Log Data:**
- Application logs: 90 days
- Audit logs: 7 years
- Access logs: 1 year

**Backup Data:**
- Daily backups: 30 days
- Monthly backups: 1 year
- Yearly backups: 7 years

---

## 15. Glossary

**API (Application Programming Interface):** Interface that allows software applications to communicate with each other.

**Branch Authorization:** Permission system that controls which branches can access specific customer data.

**Circuit Breaker:** Design pattern that prevents cascading failures by temporarily blocking requests to failing services.

**Correlation ID:** Unique identifier that tracks a request across multiple services for debugging and monitoring.

**Experience Layer:** External-facing API layer that handles authentication, logging, and transformation.

**Integration Layer:** Layer that connects to data sources and external systems.

**JWT (JSON Web Token):** Compact, self-contained way of securely transmitting information between parties.

**OAuth 2.0:** Industry-standard protocol for authorization.

**PII (Personally Identifiable Information):** Information that can identify an individual (e.g., SSN, email).

**Rate Limiting:** Controlling the number of requests a client can make in a given time period.

**RTO (Recovery Time Objective):** Maximum acceptable time to restore service after a failure.

**RPO (Recovery Point Objective):** Maximum acceptable data loss measured in time.

**TLS (Transport Layer Security):** Cryptographic protocol for secure communication over networks.

---

## 16. References and Additional Resources

**Internal Documentation:**
- Data Layer API Documentation (existing)
- Enterprise Architecture Guidelines
- Security Standards and Policies
- Database Schema Documentation

**External Standards:**
- OpenAPI Specification 3.0: https://spec.openapis.org/oas/v3.0.0
- OAuth 2.0 RFC 6749: https://tools.ietf.org/html/rfc6749
- JWT RFC 7519: https://tools.ietf.org/html/rfc7519
- REST API Design Best Practices

**Tools and Frameworks:**
- Spring Boot Documentation: https://spring.io/projects/spring-boot
- Express.js Documentation: https://expressjs.com
- AWS RDS Documentation: https://aws.amazon.com/rds/
- Redis Documentation: https://redis.io/documentation

---

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Solution Architect | | | |
| Security Architect | | | |
| Database Administrator | | | |
| Development Lead | | | |
| Product Owner | | | |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-06 | System | Initial design document |

---

**End of Document**