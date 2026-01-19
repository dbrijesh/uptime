---
last_mapped: 2026-01-19T15:30:00Z
mapped_files: 274
total_lines: ~20000
total_tokens: 189618
technology_stack: .NET 8, ASP.NET Core, Entity Framework Core, Angular 19, MediatR, AutoMapper, FluentValidation
---

# Codebase Map - Northwind Traders

> **Purpose**: Comprehensive map of a Clean Architecture .NET demo application implementing the classic Northwind Traders database

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Directory Structure & File Purpose](#3-directory-structure--file-purpose)
4. [Component Catalog](#4-component-catalog)
5. [Data Flow & Process Maps](#5-data-flow--process-maps)
6. [Integration Points](#6-integration-points)
7. [API Specifications](#7-api-specifications)
8. [Data Models & Schemas](#8-data-models--schemas)
9. [Business Logic & Rules](#9-business-logic--rules)
10. [Development Guide](#10-development-guide)

---

## 1. Executive Summary

**Project Type**: Clean Architecture Demo Application  
**Business Domain**: Northwind Traders (Classic sample database)  
**Last Updated**: January 19, 2026  
**Status**: Archived/Demo Project

### Key Statistics
- **Total Files**: 274 source files (~190k tokens)
- **Core Domain Entities**: 11 (Customer, Order, Product, Employee, etc.)
- **API Endpoints**: ~15 REST endpoints
- **Technology Stack**: .NET 8, Angular 19, SQL Server
- **Architecture Pattern**: Clean Architecture with CQRS

### Purpose
This is a demonstration project showcasing Clean Architecture principles with .NET Core and Angular. It implements a trading company management system with customers, products, orders, and employees.

**⚠️ Note**: This project has been archived and is no longer actively maintained.

---

## 2. Architecture Overview

### High-Level Architecture

```mermaid
graph TB
    subgraph "Client Tier"
        Angular[Angular SPA<br/>TypeScript/HTML/CSS]
        Browser[Web Browser]
    end
    
    subgraph "Presentation Tier"
        WebUI[ASP.NET Core WebUI<br/>Controllers + Razor Pages]
        API[REST API<br/>JSON/HTTP]
        Auth[Identity Server<br/>JWT Authentication]
    end
    
    subgraph "Application Tier"
        App[Application Layer<br/>MediatR + CQRS]
        Commands[Command Handlers]
        Queries[Query Handlers]
        Behaviors[Pipeline Behaviors<br/>Validation + Logging]
    end
    
    subgraph "Domain Tier"
        Domain[Domain Entities]
        ValueObjects[Value Objects]
        DomainServices[Domain Services]
    end
    
    subgraph "Infrastructure Tier"
        Persistence[Entity Framework Core<br/>SQL Server]
        Infrastructure[Infrastructure Services<br/>Email, Files, etc.]
        Identity[ASP.NET Core Identity]
    end
    
    subgraph "External Systems"
        SQLDB[(SQL Server<br/>LocalDB)]
        Files[File System]
    end
    
    Browser --> Angular
    Angular --> WebUI
    WebUI --> API
    API --> Auth
    WebUI --> App
    App --> Commands
    App --> Queries
    App --> Behaviors
    Commands --> Domain
    Queries --> Domain
    App --> Persistence
    App --> Infrastructure
    Persistence --> SQLDB
    Infrastructure --> Files
    Auth --> Identity
```

### Clean Architecture Layers

```mermaid
graph LR
    subgraph "Core"
        Domain[Domain Layer<br/>Entities, Value Objects<br/>Business Rules]
        Application[Application Layer<br/>Use Cases, Interfaces<br/>Commands, Queries]
    end
    
    subgraph "Infrastructure"
        Persistence[Persistence Layer<br/>EF Core, Configurations<br/>Data Access]
        Infrastructure[Infrastructure Layer<br/>External Services<br/>Email, Files, Identity]
    end
    
    subgraph "Presentation"
        WebUI[Web UI Layer<br/>Controllers, Pages<br/>Angular SPA]
    end
    
    Application --> Domain
    Persistence --> Application
    Infrastructure --> Application
    WebUI --> Application
    
    style Domain fill:#e1f5fe
    style Application fill:#f3e5f5
    style Persistence fill:#fff3e0
    style Infrastructure fill:#fff3e0
    style WebUI fill:#e8f5e8
```

### Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Angular 19, TypeScript, Bootstrap, ngx-bootstrap |
| **Backend** | .NET 8, ASP.NET Core, C# |
| **Architecture** | MediatR (CQRS), AutoMapper, FluentValidation |
| **Database** | Entity Framework Core, SQL Server LocalDB |
| **Authentication** | ASP.NET Core Identity, JWT Bearer tokens |
| **API** | REST, OpenAPI/Swagger (NSwag) |
| **Testing** | xUnit, Integration tests |

---

## 3. Directory Structure & File Purpose

### 📁 Project Organization

```
Northwind.sln                          # Solution file (6 projects + tests)
├── 📁 Src/                            # Source code (Clean Architecture layers)
│   ├── 📁 Common/                     # Shared utilities and interfaces
│   │   ├── IDateTime.cs              # Abstraction for system time
│   │   └── Common.csproj             # Shared contracts project
│   │
│   ├── 📁 Domain/                     # Core business domain (innermost layer)
│   │   ├── 📁 Entities/              # Domain entities (11 business objects)
│   │   │   ├── Customer.cs          # Customer aggregate root
│   │   │   ├── Order.cs             # Order aggregate with order details
│   │   │   ├── Product.cs           # Product entity with inventory
│   │   │   ├── Employee.cs          # Employee with hierarchy support
│   │   │   └── [7 more entities]     # Category, Supplier, Shipper, etc.
│   │   ├── 📁 Common/                # Base classes and shared domain logic
│   │   │   └── AuditableEntity.cs   # Base class with audit fields
│   │   ├── 📁 ValueObjects/          # Domain value objects
│   │   └── 📁 Exceptions/            # Domain-specific exceptions
│   │
│   ├── 📁 Application/               # Application/Use case layer (CQRS)
│   │   ├── DependencyInjection.cs   # MediatR and AutoMapper registration
│   │   ├── 📁 Common/                # Shared application concerns
│   │   │   ├── 📁 Interfaces/        # Application interfaces
│   │   │   │   └── INorthwindDbContext.cs  # Database contract
│   │   │   ├── 📁 Behaviours/        # MediatR pipeline behaviors
│   │   │   │   ├── RequestValidationBehavior.cs  # FluentValidation
│   │   │   │   └── RequestPerformanceBehaviour.cs  # Logging
│   │   │   ├── 📁 Mappings/          # AutoMapper profiles
│   │   │   ├── 📁 Models/            # Application DTOs
│   │   │   └── 📁 Exceptions/        # Application exceptions
│   │   ├── 📁 Customers/             # Customer feature (CQRS)
│   │   │   ├── 📁 Commands/          # Customer commands (CUD operations)
│   │   │   │   ├── 📁 CreateCustomer/     # Create customer use case
│   │   │   │   ├── 📁 UpdateCustomer/     # Update customer use case
│   │   │   │   └── 📁 DeleteCustomer/     # Delete customer use case
│   │   │   └── 📁 Queries/           # Customer queries (read operations)
│   │   │       ├── 📁 GetCustomersList/   # List customers
│   │   │       └── 📁 GetCustomerDetail/  # Get single customer
│   │   ├── 📁 Products/              # Product feature (same CQRS pattern)
│   │   ├── 📁 Employees/             # Employee feature
│   │   ├── 📁 Categories/            # Category feature
│   │   └── 📁 System/                # System-level commands (seeding)
│   │
│   ├── 📁 Infrastructure/            # Infrastructure services
│   │   ├── DependencyInjection.cs   # Service registrations
│   │   ├── MachineDateTime.cs        # System time implementation
│   │   ├── NotificationService.cs    # Email/notification service
│   │   ├── 📁 Identity/              # ASP.NET Identity configuration
│   │   │   ├── ApplicationDbContext.cs    # Identity database context
│   │   │   ├── ApplicationUser.cs         # Custom user entity
│   │   │   └── UserManagerService.cs      # User management service
│   │   └── 📁 Files/                 # File processing services
│   │
│   ├── 📁 Persistence/              # Data access layer (EF Core)
│   │   ├── DependencyInjection.cs   # DbContext registration
│   │   ├── NorthwindDbContext.cs     # Main database context
│   │   ├── 📁 Configurations/        # EF Core entity configurations (12 files)
│   │   │   ├── CustomerConfiguration.cs   # Customer entity mapping
│   │   │   ├── OrderConfiguration.cs      # Order entity mapping
│   │   │   └── [10 more configs]           # One per entity
│   │   └── 📁 Migrations/            # EF Core database migrations (12 files)
│   │
│   └── 📁 WebUI/                     # Presentation layer (ASP.NET Core + Angular)
│       ├── Program.cs                # Application entry point
│       ├── Startup.cs               # Service configuration and middleware
│       ├── 📁 Controllers/          # REST API controllers (6 controllers)
│       │   ├── BaseController.cs    # Base controller with MediatR
│       │   ├── CustomersController.cs    # Customer CRUD API
│       │   ├── ProductsController.cs     # Product CRUD API
│       │   ├── EmployeesController.cs    # Employee API
│       │   └── [2 more controllers]      # Categories, Identity
│       ├── 📁 Services/             # Presentation services
│       ├── 📁 Common/               # Shared web concerns
│       ├── 📁 Areas/Identity/       # ASP.NET Identity UI
│       ├── 📁 Pages/                # Razor Pages
│       └── 📁 ClientApp/            # Angular SPA (85 files)
│           ├── package.json         # NPM dependencies
│           ├── angular.json         # Angular CLI configuration
│           ├── 📁 src/              # Angular source code
│           │   ├── 📁 app/          # Angular components (8 components)
│           │   │   ├── app.module.ts       # Main Angular module
│           │   │   ├── northwind-traders-api.ts  # Generated API client
│           │   │   ├── 📁 customers/       # Customer management UI
│           │   │   ├── 📁 products/        # Product management UI
│           │   │   └── [6 more components] # Navigation, home, etc.
│           │   ├── 📁 api-authorization/   # OIDC authentication (9 files)
│           │   └── 📁 environments/        # Environment configs
│           └── 📁 e2e/              # End-to-end tests
│
├── 📁 Tests/                        # Test projects (4 test suites)
│   ├── 📁 Application.UnitTests/    # Application layer unit tests
│   ├── 📁 Domain.UnitTests/         # Domain layer unit tests  
│   ├── 📁 Persistence.IntegrationTests/  # Database integration tests
│   └── 📁 WebUI.IntegrationTests/   # API integration tests (14 test files)
│
└── 📁 Docs/                         # Documentation
    └── [This documentation]
```

### Key File Purposes

| File | Purpose | Tokens | Key Responsibilities |
|------|---------|--------|---------------------|
| **Core Architecture** |
| `Startup.cs` | Application configuration | 922 | Service registration, middleware pipeline, SPA hosting |
| `Program.cs` | Application entry point | 583 | Host configuration, application startup |
| **Domain Layer** |
| `Customer.cs` | Customer aggregate root | - | Customer data and business rules |
| `Order.cs` | Order aggregate | - | Order management with audit trail |
| `Product.cs` | Product entity | - | Product catalog with inventory |
| **Application Layer** |
| `CreateCustomerCommand.cs` | Customer creation use case | - | Command handling for customer creation |
| `GetCustomersListQuery.cs` | Customer list query | - | Query for retrieving customer lists |
| `RequestValidationBehavior.cs` | Validation pipeline | - | Cross-cutting validation using FluentValidation |
| **Infrastructure** |
| `NorthwindDbContext.cs` | Main database context | 443 | Entity Framework configuration, audit handling |
| `DependencyInjection.cs` (multiple) | Service registration | - | IoC container configuration per layer |
| **Presentation** |
| `CustomersController.cs` | Customer API endpoints | 369 | RESTful CRUD operations for customers |
| `app.module.ts` | Angular root module | 407 | Frontend application configuration |
| `northwind-traders-api.ts` | Generated API client | 17247 | TypeScript client for backend API |

---

## 4. Component Catalog

### 🏛️ Domain Entities

#### Core Business Objects

```mermaid
erDiagram
    CUSTOMER {
        string CustomerId PK
        string CompanyName
        string ContactName
        string ContactTitle
        string Address
        string City
        string Region
        string PostalCode
        string Country
        string Phone
        string Fax
    }
    
    ORDER {
        int OrderId PK
        string CustomerId FK
        int EmployeeId FK
        datetime OrderDate
        datetime RequiredDate
        datetime ShippedDate
        int ShipVia FK
        decimal Freight
        string ShipName
        string ShipAddress
        string ShipCity
        string ShipRegion
        string ShipPostalCode
        string ShipCountry
        string CreatedBy
        datetime Created
        string LastModifiedBy
        datetime LastModified
    }
    
    ORDERDETAIL {
        int OrderId PK,FK
        int ProductId PK,FK
        decimal UnitPrice
        short Quantity
        float Discount
    }
    
    PRODUCT {
        int ProductId PK
        string ProductName
        int SupplierId FK
        int CategoryId FK
        string QuantityPerUnit
        decimal UnitPrice
        short UnitsInStock
        short UnitsOnOrder
        short ReorderLevel
        bool Discontinued
        string CreatedBy
        datetime Created
        string LastModifiedBy
        datetime LastModified
    }
    
    EMPLOYEE {
        int EmployeeId PK
        string UserId
        string LastName
        string FirstName
        string Title
        datetime BirthDate
        datetime HireDate
        string Address
        string City
        string Region
        string PostalCode
        string Country
        string HomePhone
        string Extension
        int ReportsTo FK
        string CreatedBy
        datetime Created
        string LastModifiedBy
        datetime LastModified
    }
    
    CATEGORY {
        int CategoryId PK
        string CategoryName
        string Description
    }
    
    SUPPLIER {
        int SupplierId PK
        string CompanyName
        string ContactName
        string ContactTitle
        string Address
        string City
        string Region
        string PostalCode
        string Country
        string Phone
        string Fax
        string HomePage
    }
    
    SHIPPER {
        int ShipperId PK
        string CompanyName
        string Phone
    }
    
    CUSTOMER ||--o{ ORDER : places
    EMPLOYEE ||--o{ ORDER : processes
    SHIPPER ||--o{ ORDER : ships
    ORDER ||--o{ ORDERDETAIL : contains
    PRODUCT ||--o{ ORDERDETAIL : "included in"
    CATEGORY ||--o{ PRODUCT : categorizes
    SUPPLIER ||--o{ PRODUCT : supplies
    EMPLOYEE ||--o{ EMPLOYEE : reports_to
```

### 🔧 Application Services

#### Command Handlers (Write Operations)

| Component | Purpose | Input | Output | Dependencies |
|-----------|---------|-------|--------|--------------|
| **CreateCustomerCommand.Handler** | Creates new customer | Customer data | Success notification | INorthwindDbContext, IMediator |
| **UpdateCustomerCommand.Handler** | Updates existing customer | Customer ID + data | Success notification | INorthwindDbContext |
| **DeleteCustomerCommand.Handler** | Removes customer | Customer ID | Success notification | INorthwindDbContext |
| **CreateProductCommand.Handler** | Creates new product | Product data | Product ID | INorthwindDbContext |
| **UpdateProductCommand.Handler** | Updates product details | Product ID + data | Success notification | INorthwindDbContext |

#### Query Handlers (Read Operations)

| Component | Purpose | Input | Output | Dependencies |
|-----------|---------|-------|--------|--------------|
| **GetCustomersListQuery.Handler** | Retrieves customer list | None | CustomersListVm | INorthwindDbContext, IMapper |
| **GetCustomerDetailQuery.Handler** | Gets single customer | Customer ID | CustomerDetailVm | INorthwindDbContext, IMapper |
| **GetProductsListQuery.Handler** | Retrieves product list | None | ProductsListVm | INorthwindDbContext, IMapper |
| **GetProductDetailQuery.Handler** | Gets single product | Product ID | ProductDetailVm | INorthwindDbContext, IMapper |

#### Pipeline Behaviors (Cross-Cutting Concerns)

| Component | Purpose | When Applied | Dependencies |
|-----------|---------|--------------|--------------|
| **RequestValidationBehavior** | Validates commands/queries using FluentValidation | All requests | IValidator<TRequest> |
| **RequestPerformanceBehaviour** | Logs slow-performing requests | All requests | ILogger, ICurrentUserService |

### 🌐 Web Controllers

#### REST API Endpoints

| Controller | Base Route | Methods | Purpose |
|------------|------------|---------|---------|
| **CustomersController** | `/api/customers` | GET, GET/{id}, POST, PUT/{id}, DELETE/{id} | Customer CRUD operations |
| **ProductsController** | `/api/products` | GET, GET/{id}, POST, PUT/{id}, DELETE/{id} | Product CRUD operations |
| **EmployeesController** | `/api/employees` | GET, PUT/{id}, DELETE/{id} | Employee management |
| **CategoriesController** | `/api/categories` | GET, PUT/{id}, DELETE/{id} | Category management |

### 🎨 Angular Components

#### Frontend UI Components

| Component | Route | Purpose | Services Used |
|-----------|-------|---------|---------------|
| **CustomersComponent** | `/customers` | Customer list management | CustomersClient |
| **CustomerDetailComponent** | `/customers/:id` | Customer detail view/edit | CustomersClient |
| **ProductsComponent** | `/products` | Product catalog view | ProductsClient |
| **HomeComponent** | `/` | Dashboard and welcome page | None |
| **NavSideMenuComponent** | - | Navigation sidebar | AuthorizeService |
| **NavTopMenuComponent** | - | Top navigation bar | AuthorizeService |

---

## 5. Data Flow & Process Maps

### Customer Management Flow

```mermaid
sequenceDiagram
    participant U as User
    participant C as CustomerComponent
    participant API as CustomersController
    participant M as MediatR
    participant H as CommandHandler
    participant DB as NorthwindDbContext
    participant SQL as SQL Server

    Note over U,SQL: Create Customer Flow
    
    U->>C: Enter customer data
    C->>API: POST /api/customers<br/>{customerData}
    API->>M: Send CreateCustomerCommand
    M->>H: Handle command
    H->>DB: Add customer entity
    DB->>SQL: INSERT INTO Customers
    SQL-->>DB: Success
    DB-->>H: SaveChanges result
    H->>M: Publish CustomerCreated event
    M-->>API: Success response
    API-->>C: HTTP 204 No Content
    C-->>U: Success notification

    Note over U,SQL: Get Customer List Flow
    
    U->>C: Load customers page
    C->>API: GET /api/customers
    API->>M: Send GetCustomersListQuery
    M->>H: Handle query
    H->>DB: Query customers with mapping
    DB->>SQL: SELECT * FROM Customers
    SQL-->>DB: Customer records
    DB-->>H: Customer entities
    H-->>M: CustomersListVm
    M-->>API: Query result
    API-->>C: HTTP 200 + customer list JSON
    C-->>U: Display customer table
```

### Product Catalog Flow

```mermaid
sequenceDiagram
    participant U as User
    participant P as ProductComponent
    participant API as ProductsController
    participant M as MediatR
    participant QH as QueryHandler
    participant CH as CommandHandler
    participant DB as NorthwindDbContext

    Note over U,DB: Product Lifecycle Management
    
    U->>P: View products
    P->>API: GET /api/products
    API->>M: GetProductsListQuery
    M->>QH: Execute query
    QH->>DB: LINQ query with joins
    Note right of DB: Includes Category & Supplier
    DB-->>QH: Product entities
    QH-->>M: ProductsListVm
    M-->>API: Mapped results
    API-->>P: Product list JSON
    P-->>U: Display product grid

    U->>P: Edit product
    P->>API: PUT /api/products/123<br/>{productData}
    API->>M: UpdateProductCommand
    M->>CH: Execute command
    CH->>DB: Update product entity
    Note right of DB: Audit fields updated
    DB-->>CH: Success
    CH-->>M: Success
    M-->>API: Success response
    API-->>P: HTTP 204 No Content
    P-->>U: Show success message
```

### Request Processing Pipeline

```mermaid
flowchart TD
    A[HTTP Request] --> B[ASP.NET Core Pipeline]
    B --> C[Authentication Middleware]
    C --> D[Authorization Check]
    D --> E[Controller Action]
    E --> F[MediatR Request]
    
    F --> G{Request Type?}
    G -->|Command| H[Validation Behavior]
    G -->|Query| I[Performance Behavior]
    
    H --> J[Command Handler]
    I --> K[Query Handler]
    
    J --> L[Database Write]
    K --> M[Database Read]
    
    L --> N[Audit Logging]
    M --> O[AutoMapper]
    
    N --> P[Success Response]
    O --> P
    
    P --> Q[JSON Serialization]
    Q --> R[HTTP Response]
    
    style F fill:#e1f5fe
    style J fill:#f3e5f5
    style K fill:#f3e5f5
    style L fill:#fff3e0
    style M fill:#fff3e0
```

### Authentication Flow

```mermaid
sequenceDiagram
    participant B as Browser
    participant A as Angular App
    participant I as Identity Server
    participant API as Web API
    participant DB as Identity DB

    Note over B,DB: JWT Authentication Flow
    
    B->>A: Access protected page
    A->>A: Check local token
    alt No valid token
        A->>I: Redirect to login
        I->>B: Show login form
        B->>I: POST credentials
        I->>DB: Validate user
        DB-->>I: User identity
        I->>I: Generate JWT token
        I-->>A: Return token + user info
        A->>A: Store token in localStorage
    end
    
    A->>API: HTTP request + Authorization header
    Note right of A: Bearer {jwtToken}
    API->>API: Validate JWT signature
    API->>API: Extract user claims
    API->>API: Execute business logic
    API-->>A: Protected resource data
    A-->>B: Display data
```

---

## 6. Integration Points

### 🗄️ Database Integration

#### SQL Server LocalDB Connection

**Connection String**: `Server=(localdb)\\mssqllocaldb;Database=NorthwindTraders;Trusted_Connection=True;MultipleActiveResultSets=true`

**Key Database Operations**:

| Operation | Entity | SQL Pattern | Triggered By |
|-----------|--------|-------------|--------------|
| **Customer CRUD** | Customer | `INSERT INTO Customers`, `UPDATE Customers SET`, `DELETE FROM Customers` | CustomersController actions |
| **Product Queries** | Product | `SELECT p.*, c.CategoryName, s.CompanyName FROM Products p JOIN Categories c ON...` | Product list/detail queries |
| **Order Processing** | Order + OrderDetail | Transaction: `INSERT INTO Orders`, `INSERT INTO OrderDetails` (batch) | Order creation (not fully implemented) |
| **Employee Hierarchy** | Employee | Recursive CTE: `WITH EmployeeHierarchy AS (...) SELECT * FROM EmployeeHierarchy` | Employee reporting structure |

**Entity Framework Configurations**:
- **Audit Trail**: Automatic `CreatedBy`/`Created`/`LastModifiedBy`/`LastModified` for AuditableEntity
- **Relationships**: Configured via Fluent API in `Configurations/` folder
- **Migrations**: Version-controlled schema changes in `Migrations/` folder

### 🔐 Identity & Authentication Integration

#### ASP.NET Core Identity

**Components**:
- **ApplicationUser**: Custom user entity extending IdentityUser
- **ApplicationDbContext**: Separate context for identity data
- **JWT Bearer Authentication**: Token-based API authentication

**Authentication Flow**:
```csharp
// JWT Configuration (Infrastructure/DependencyInjection.cs)
services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options => {
        options.TokenValidationParameters = new TokenValidationParameters {
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(key),
            ValidateIssuer = false,
            ValidateAudience = false
        };
    });
```

### 🌐 Frontend Integration

#### Angular SPA Integration

**Generated API Client**: `northwind-traders-api.ts` (17,247 tokens)
- Auto-generated TypeScript client using NSwag
- Type-safe API calls with full IntelliSense support
- Automatic request/response mapping

**Key Service Integrations**:

| Service | Purpose | API Calls |
|---------|---------|-----------|
| **CustomersClient** | Customer management | GET, POST, PUT, DELETE `/api/customers` |
| **ProductsClient** | Product catalog | GET, POST, PUT, DELETE `/api/products` |
| **AuthorizeService** | Authentication | OIDC flows, token management |

**Example API Usage**:
```typescript
// Angular Component (customers.component.ts)
export class CustomersComponent {
    customers: CustomerLookupDto[];
    
    constructor(private client: CustomersClient) {}
    
    ngOnInit() {
        this.client.getAll().subscribe(result => {
            this.customers = result.customers;
        });
    }
    
    deleteCustomer(id: string) {
        this.client.delete(id).subscribe(() => {
            // Remove from list
        });
    }
}
```

### 📧 External Service Integration

#### Notification Service

**Location**: `Infrastructure/NotificationService.cs`
**Interface**: `INotificationService`
**Purpose**: Email notifications for business events (placeholder implementation)

```csharp
public class NotificationService : INotificationService
{
    public Task SendAsync(Message message)
    {
        // TODO: Implement email sending
        // Could integrate with SendGrid, AWS SES, etc.
        return Task.CompletedTask;
    }
}
```

### 📁 File System Integration

#### File Processing Service

**Location**: `Infrastructure/Files/CsvFileBuilder.cs`
**Purpose**: Export data to CSV format
**Usage**: Product export functionality

---

## 7. API Specifications

### 🔗 REST API Endpoints

#### Customer Management API

**Base URL**: `/api/customers`

| Method | Endpoint | Request Body | Response | Status Codes | Description |
|--------|----------|--------------|----------|--------------|-------------|
| **GET** | `/` | None | `CustomersListVm` | 200 | Get all customers |
| **GET** | `/{id}` | None | `CustomerDetailVm` | 200, 404 | Get customer by ID |
| **POST** | `/` | `CreateCustomerCommand` | None | 204, 400 | Create new customer |
| **PUT** | `/{id}` | `UpdateCustomerCommand` | None | 204, 400, 404 | Update existing customer |
| **DELETE** | `/{id}` | None | None | 204, 404 | Delete customer |

**Example Request/Response**:

```json
// POST /api/customers
{
  "id": "ALFKI",
  "companyName": "Alfreds Futterkiste",
  "contactName": "Maria Anders",
  "contactTitle": "Sales Representative",
  "address": "Obere Str. 57",
  "city": "Berlin",
  "region": null,
  "postalCode": "12209",
  "country": "Germany",
  "phone": "030-0074321",
  "fax": "030-0076545"
}

// GET /api/customers response
{
  "customers": [
    {
      "id": "ALFKI",
      "companyName": "Alfreds Futterkiste",
      "contactName": "Maria Anders",
      "city": "Berlin",
      "country": "Germany",
      "phone": "030-0074321"
    }
  ]
}
```

#### Product Catalog API

**Base URL**: `/api/products`

| Method | Endpoint | Request Body | Response | Status Codes | Description |
|--------|----------|--------------|----------|--------------|-------------|
| **GET** | `/` | None | `ProductsListVm` | 200 | Get all products |
| **GET** | `/{id}` | None | `ProductDetailVm` | 200, 404 | Get product by ID |
| **GET** | `/file` | None | `ProductsFileVm` | 200 | Export products as CSV |
| **POST** | `/` | `CreateProductCommand` | Product ID | 201, 400 | Create new product |
| **PUT** | `/{id}` | `UpdateProductCommand` | None | 204, 400, 404 | Update existing product |
| **DELETE** | `/{id}` | None | None | 204, 404 | Delete product |

**Example Request/Response**:

```json
// POST /api/products
{
  "productName": "Chai",
  "supplierId": 1,
  "categoryId": 1,
  "quantityPerUnit": "10 boxes x 20 bags",
  "unitPrice": 18.00,
  "unitsInStock": 39,
  "unitsOnOrder": 0,
  "reorderLevel": 10,
  "discontinued": false
}

// GET /api/products response
{
  "products": [
    {
      "productId": 1,
      "productName": "Chai",
      "categoryName": "Beverages",
      "supplierCompanyName": "Exotic Liquids",
      "unitPrice": 18.00,
      "unitsInStock": 39,
      "discontinued": false
    }
  ]
}
```

### 🔐 Authentication API

**OIDC Configuration**: Handled by ASP.NET Core Identity
**Token Endpoint**: `/connect/token`
**Authorization**: JWT Bearer tokens

**Example Authentication**:
```http
POST /api/customers
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "companyName": "New Customer Inc."
}
```

### 📋 API Documentation

**OpenAPI/Swagger**: Available at `/api` endpoint
**Generated Client**: Auto-generated TypeScript client for Angular
**API Specification**: Available at `/api/specification.json`

---

## 8. Data Models & Schemas

### 🏢 Core Domain Models

#### Customer Aggregate

```csharp
public class Customer
{
    // Primary Key
    public string CustomerId { get; set; }        // 5-char customer code (e.g., "ALFKI")
    
    // Company Information
    public string CompanyName { get; set; }       // Required, max 40 chars
    public string ContactName { get; set; }       // Contact person name
    public string ContactTitle { get; set; }      // Contact person title
    
    // Address Information
    public string Address { get; set; }
    public string City { get; set; }
    public string Region { get; set; }           // State/Province (optional)
    public string PostalCode { get; set; }
    public string Country { get; set; }
    
    // Contact Information
    public string Phone { get; set; }
    public string Fax { get; set; }
    
    // Navigation Properties
    public ICollection<Order> Orders { get; private set; }
}
```

#### Product Catalog Model

```csharp
public class Product : AuditableEntity
{
    // Primary Key
    public int ProductId { get; set; }
    
    // Product Information
    public string ProductName { get; set; }       // Required, max 40 chars
    public int? SupplierId { get; set; }         // Foreign key to Supplier
    public int? CategoryId { get; set; }         // Foreign key to Category
    public string QuantityPerUnit { get; set; }  // e.g., "10 boxes x 20 bags"
    
    // Pricing & Inventory
    public decimal? UnitPrice { get; set; }      // Current unit price
    public short? UnitsInStock { get; set; }     // Current inventory
    public short? UnitsOnOrder { get; set; }     // Pending orders
    public short? ReorderLevel { get; set; }     // Minimum stock level
    public bool Discontinued { get; set; }       // Product status
    
    // Navigation Properties
    public Category Category { get; set; }
    public Supplier Supplier { get; set; }
    public ICollection<OrderDetail> OrderDetails { get; private set; }
}
```

### 📊 Data Transfer Objects

#### Customer DTOs

```csharp
// List View DTO
public class CustomerLookupDto
{
    public string Id { get; set; }
    public string CompanyName { get; set; }
    public string ContactName { get; set; }
    public string City { get; set; }
    public string Country { get; set; }
    public string Phone { get; set; }
}

// Detail View DTO
public class CustomerDetailVm
{
    public string Id { get; set; }
    public string CompanyName { get; set; }
    public string ContactName { get; set; }
    public string ContactTitle { get; set; }
    public string Address { get; set; }
    public string City { get; set; }
    public string Region { get; set; }
    public string PostalCode { get; set; }
    public string Country { get; set; }
    public string Phone { get; set; }
    public string Fax { get; set; }
}
```

### 🗂️ Database Schema

#### Key Tables & Relationships

```sql
-- Customer Table
CREATE TABLE [dbo].[Customers] (
    [CustomerId] NVARCHAR(5) NOT NULL PRIMARY KEY,
    [CompanyName] NVARCHAR(40) NOT NULL,
    [ContactName] NVARCHAR(30) NULL,
    [ContactTitle] NVARCHAR(30) NULL,
    [Address] NVARCHAR(60) NULL,
    [City] NVARCHAR(15) NULL,
    [Region] NVARCHAR(15) NULL,
    [PostalCode] NVARCHAR(10) NULL,
    [Country] NVARCHAR(15) NULL,
    [Phone] NVARCHAR(24) NULL,
    [Fax] NVARCHAR(24) NULL
);

-- Product Table (with audit fields)
CREATE TABLE [dbo].[Products] (
    [ProductId] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    [ProductName] NVARCHAR(40) NOT NULL,
    [SupplierId] INT NULL,
    [CategoryId] INT NULL,
    [QuantityPerUnit] NVARCHAR(20) NULL,
    [UnitPrice] MONEY NULL,
    [UnitsInStock] SMALLINT NULL,
    [UnitsOnOrder] SMALLINT NULL,
    [ReorderLevel] SMALLINT NULL,
    [Discontinued] BIT NOT NULL DEFAULT(0),
    [CreatedBy] NVARCHAR(MAX) NULL,
    [Created] DATETIME2 NOT NULL DEFAULT(GETUTCDATE()),
    [LastModifiedBy] NVARCHAR(MAX) NULL,
    [LastModified] DATETIME2 NULL,
    
    CONSTRAINT [FK_Products_Categories] 
        FOREIGN KEY ([CategoryId]) REFERENCES [Categories] ([CategoryId]),
    CONSTRAINT [FK_Products_Suppliers] 
        FOREIGN KEY ([SupplierId]) REFERENCES [Suppliers] ([SupplierId])
);

-- Order Header Table
CREATE TABLE [dbo].[Orders] (
    [OrderId] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    [CustomerId] NVARCHAR(5) NULL,
    [EmployeeId] INT NULL,
    [OrderDate] DATETIME NULL,
    [RequiredDate] DATETIME NULL,
    [ShippedDate] DATETIME NULL,
    [ShipVia] INT NULL,
    [Freight] MONEY NULL DEFAULT(0),
    [ShipName] NVARCHAR(40) NULL,
    [ShipAddress] NVARCHAR(60) NULL,
    [ShipCity] NVARCHAR(15) NULL,
    [ShipRegion] NVARCHAR(15) NULL,
    [ShipPostalCode] NVARCHAR(10) NULL,
    [ShipCountry] NVARCHAR(15) NULL,
    [CreatedBy] NVARCHAR(MAX) NULL,
    [Created] DATETIME2 NOT NULL DEFAULT(GETUTCDATE()),
    [LastModifiedBy] NVARCHAR(MAX) NULL,
    [LastModified] DATETIME2 NULL,
    
    CONSTRAINT [FK_Orders_Customers] 
        FOREIGN KEY ([CustomerId]) REFERENCES [Customers] ([CustomerId]),
    CONSTRAINT [FK_Orders_Employees] 
        FOREIGN KEY ([EmployeeId]) REFERENCES [Employees] ([EmployeeId]),
    CONSTRAINT [FK_Orders_Shippers] 
        FOREIGN KEY ([ShipVia]) REFERENCES [Shippers] ([ShipperId])
);
```

### 🔄 AutoMapper Configurations

**Mapping Profiles** (located in `Application/Common/Mappings/`):

```csharp
// Customer Mappings
public class CustomerMappingProfile : Profile
{
    public CustomerMappingProfile()
    {
        CreateMap<Customer, CustomerLookupDto>();
        CreateMap<Customer, CustomerDetailVm>();
        CreateMap<CreateCustomerCommand, Customer>();
    }
}

// Product Mappings
public class ProductMappingProfile : Profile
{
    public ProductMappingProfile()
    {
        CreateMap<Product, ProductDto>()
            .ForMember(d => d.CategoryName, opt => opt.MapFrom(s => s.Category.CategoryName))
            .ForMember(d => d.SupplierCompanyName, opt => opt.MapFrom(s => s.Supplier.CompanyName));
    }
}
```

---

## 9. Business Logic & Rules

### 🔍 Validation Rules

#### Customer Validation

**FluentValidation Rules** (`CreateCustomerCommandValidator.cs`):

```csharp
public class CreateCustomerCommandValidator : AbstractValidator<CreateCustomerCommand>
{
    public CreateCustomerCommandValidator()
    {
        RuleFor(v => v.Id)
            .NotEmpty().WithMessage("Customer ID is required")
            .Length(5).WithMessage("Customer ID must be exactly 5 characters")
            .Matches("^[A-Z]{5}$").WithMessage("Customer ID must be 5 uppercase letters");
            
        RuleFor(v => v.CompanyName)
            .NotEmpty().WithMessage("Company name is required")
            .MaximumLength(40).WithMessage("Company name must not exceed 40 characters");
            
        RuleFor(v => v.ContactName)
            .MaximumLength(30).WithMessage("Contact name must not exceed 30 characters");
            
        RuleFor(v => v.Phone)
            .Matches(@"^[\d\s\-\(\)\+]+$").WithMessage("Invalid phone format")
            .When(v => !string.IsNullOrEmpty(v.Phone));
    }
}
```

#### Product Business Rules

**Inventory Management**:
- Products with `UnitsInStock` ≤ `ReorderLevel` trigger reorder alerts
- `Discontinued` products cannot be ordered
- `UnitPrice` must be ≥ 0
- `UnitsInStock` cannot be negative

### 📋 Business Processes

#### Customer Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Active : Create Customer
    Active --> Active : Update Information
    Active --> Active : Place Orders
    Active --> Inactive : Mark Inactive
    Inactive --> Active : Reactivate
    Active --> [*] : Delete Customer
    
    note right of Active
        Customer can place orders
        Receive notifications
        Access full features
    end note
    
    note left of Inactive
        Orders preserved
        No new orders allowed
        Limited access
    end note
```

#### Order Processing Workflow (Conceptual)

```mermaid
flowchart TD
    A[Customer Places Order] --> B{Inventory Available?}
    B -->|Yes| C[Reserve Stock]
    B -->|No| D[Back Order]
    
    C --> E[Calculate Total]
    E --> F[Process Payment]
    F --> G{Payment Success?}
    
    G -->|Yes| H[Confirm Order]
    G -->|No| I[Release Stock]
    
    H --> J[Assign Employee]
    J --> K[Schedule Shipment]
    K --> L[Generate Invoice]
    L --> M[Ship Order]
    
    D --> N[Notify Customer]
    I --> O[Payment Failed]
    M --> P[Order Complete]
    
    style A fill:#e8f5e8
    style P fill:#e8f5e8
    style O fill:#ffebee
    style D fill:#fff3e0
```

### ⚖️ Business Rules Implementation

#### Audit Trail Rules

**Automatic Audit Fields** (implemented in `NorthwindDbContext.SaveChangesAsync()`):

```csharp
foreach (var entry in ChangeTracker.Entries<AuditableEntity>())
{
    switch (entry.State)
    {
        case EntityState.Added:
            entry.Entity.CreatedBy = _currentUserService.UserId;
            entry.Entity.Created = _dateTime.Now;
            break;
        case EntityState.Modified:
            entry.Entity.LastModifiedBy = _currentUserService.UserId;
            entry.Entity.LastModified = _dateTime.Now;
            break;
    }
}
```

**Rules**:
- All `AuditableEntity` instances automatically track creation and modification
- User context captured from JWT claims via `ICurrentUserService`
- System time abstracted via `IDateTime` for testability

#### Data Consistency Rules

**Entity Framework Configurations**:
- Foreign key constraints enforced at database level
- Required fields enforced via `[Required]` attributes and Fluent API
- String length limits prevent data truncation
- Cascade delete rules prevent orphaned records

### 📊 Reporting & Analytics

#### Query Optimization Patterns

**Customer List Query** (optimized for performance):
```csharp
public async Task<CustomersListVm> Handle(GetCustomersListQuery request, CancellationToken cancellationToken)
{
    var customers = await _context.Customers
        .ProjectTo<CustomerLookupDto>(_mapper.ConfigurationProvider)
        .OrderBy(c => c.CompanyName)
        .ToListAsync(cancellationToken);
        
    return new CustomersListVm { Customers = customers };
}
```

**Product Queries with Related Data**:
```csharp
var products = await _context.Products
    .Include(p => p.Category)
    .Include(p => p.Supplier)
    .Where(p => !p.Discontinued)
    .ProjectTo<ProductDto>(_mapper.ConfigurationProvider)
    .ToListAsync(cancellationToken);
```

---

## 10. Development Guide

### 🚀 Getting Started

#### Prerequisites

- **.NET 8 SDK**: Download from Microsoft
- **Visual Studio 2022** or **VS Code** with C# extension
- **Node.js 18+**: For Angular development
- **SQL Server LocalDB**: Included with Visual Studio

#### Setup Instructions

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd SampleApp
   ```

2. **Restore Dependencies**:
   ```bash
   dotnet restore
   cd Src/WebUI/ClientApp
   npm install
   cd ../../..
   ```

3. **Database Setup**:
   ```bash
   cd Src/WebUI
   dotnet ef database update --context NorthwindDbContext
   dotnet ef database update --context ApplicationDbContext
   ```

4. **Run Application**:
   ```bash
   cd Src/WebUI
   dotnet run
   ```
   Application available at: `https://localhost:5001`

### 🛠️ Development Workflow

#### Adding a New Feature (CQRS Pattern)

**Example: Add Category Management**

1. **Create Domain Entity** (if needed):
   ```csharp
   // Src/Domain/Entities/Category.cs
   public class Category
   {
       public int CategoryId { get; set; }
       public string CategoryName { get; set; }
       public string Description { get; set; }
       public ICollection<Product> Products { get; private set; }
   }
   ```

2. **Add Commands**:
   ```csharp
   // Src/Application/Categories/Commands/CreateCategory/CreateCategoryCommand.cs
   public class CreateCategoryCommand : IRequest<int>
   {
       public string CategoryName { get; set; }
       public string Description { get; set; }
       
       public class Handler : IRequestHandler<CreateCategoryCommand, int>
       {
           // Implementation...
       }
   }
   ```

3. **Add Queries**:
   ```csharp
   // Src/Application/Categories/Queries/GetCategoriesList/GetCategoriesListQuery.cs
   public class GetCategoriesListQuery : IRequest<CategoriesListVm>
   {
       public class Handler : IRequestHandler<GetCategoriesListQuery, CategoriesListVm>
       {
           // Implementation...
       }
   }
   ```

4. **Create Controller**:
   ```csharp
   // Src/WebUI/Controllers/CategoriesController.cs
   public class CategoriesController : BaseController
   {
       [HttpGet]
       public async Task<ActionResult<CategoriesListVm>> GetAll()
       {
           return Ok(await Mediator.Send(new GetCategoriesListQuery()));
       }
   }
   ```

5. **Add Angular Component**:
   ```typescript
   // Src/WebUI/ClientApp/src/app/categories/categories.component.ts
   export class CategoriesComponent implements OnInit {
       categories: CategoryDto[] = [];
       
       constructor(private categoriesClient: CategoriesClient) {}
       
       ngOnInit() {
           this.categoriesClient.getAll().subscribe(result => {
               this.categories = result.categories;
           });
       }
   }
   ```

#### Testing Strategy

**Unit Tests** (Application Layer):
```csharp
// Tests/Application.UnitTests/Categories/Queries/GetCategoriesListQueryHandlerTests.cs
[Test]
public async Task GetCategoriesListQuery_ShouldReturnAllCategories()
{
    // Arrange
    var context = NorthwindContextFactory.Create();
    var mapper = MapperFactory.Create();
    var handler = new GetCategoriesListQueryHandler(context, mapper);
    
    // Act
    var result = await handler.Handle(new GetCategoriesListQuery(), CancellationToken.None);
    
    // Assert
    Assert.That(result.Categories.Count, Is.EqualTo(8));
}
```

**Integration Tests** (API Layer):
```csharp
// Tests/WebUI.IntegrationTests/Controllers/Categories/GetAll.cs
[Test]
public async Task GetAll_ShouldReturnCategoriesList()
{
    // Arrange
    var client = _factory.CreateClient();
    await TestHelper.AuthenticateAsync(client);
    
    // Act
    var response = await client.GetAsync("/api/categories");
    
    // Assert
    response.StatusCode.Should().Be(HttpStatusCode.OK);
    var categories = JsonSerializer.Deserialize<CategoriesListVm>(
        await response.Content.ReadAsStringAsync());
    categories.Categories.Should().NotBeEmpty();
}
```

### 📁 Project Structure Guidelines

#### Folder Conventions

```
Src/Application/[Feature]/
├── Commands/
│   ├── Create[Feature]/
│   │   ├── Create[Feature]Command.cs
│   │   ├── Create[Feature]CommandHandler.cs
│   │   └── Create[Feature]CommandValidator.cs
│   └── Update[Feature]/
└── Queries/
    ├── Get[Feature]List/
    │   ├── Get[Feature]ListQuery.cs
    │   ├── Get[Feature]ListQueryHandler.cs
    │   ├── [Feature]ListVm.cs
    │   └── [Feature]LookupDto.cs
    └── Get[Feature]Detail/
```

#### Naming Conventions

- **Commands**: `{Verb}{EntityName}Command` (e.g., `CreateCustomerCommand`)
- **Queries**: `Get{EntityName}{Qualifier}Query` (e.g., `GetCustomersListQuery`)
- **Handlers**: `{RequestName}Handler` (e.g., `CreateCustomerCommandHandler`)
- **ViewModels**: `{EntityName}{Context}Vm` (e.g., `CustomersListVm`)
- **DTOs**: `{EntityName}{Context}Dto` (e.g., `CustomerLookupDto`)

### 🔧 Configuration Management

#### Environment-Specific Settings

| File | Purpose | Environment |
|------|---------|-------------|
| `appsettings.json` | Base configuration | All |
| `appsettings.Development.json` | Development overrides | Development |
| `appsettings.Production.json` | Production settings | Production |
| `appsettings.Test.json` | Testing configuration | Testing |

#### Key Configuration Sections

```json
{
  "ConnectionStrings": {
    "NorthwindDatabase": "Server=(localdb)\\mssqllocaldb;Database=NorthwindTraders;...",
    "IdentityDatabase": "Server=(localdb)\\mssqllocaldb;Database=NorthwindTradersIdentity;..."
  },
  "JwtSettings": {
    "SecretKey": "YourSuperSecretKeyThatIsAtLeast32CharactersLong!",
    "ExpiryInMinutes": 60
  },
  "UseInMemoryDatabase": false,
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning"
    }
  }
}
```

### 🐛 Debugging & Troubleshooting

#### Common Issues

1. **Database Connection Errors**:
   - Verify LocalDB is installed and running
   - Check connection string in appsettings.json
   - Run `dotnet ef database update`

2. **Angular Build Errors**:
   - Delete `node_modules` and run `npm install`
   - Check Node.js version (18+ required)
   - Verify TypeScript client is generated

3. **Authentication Issues**:
   - Check JWT secret key configuration
   - Verify Identity database is created
   - Clear browser localStorage

#### Useful Commands

```bash
# Database commands
dotnet ef migrations add [MigrationName] --project Src/Persistence
dotnet ef database update --project Src/WebUI

# Build commands  
dotnet build
dotnet test
dotnet publish -c Release

# Angular commands
ng build --prod
ng test
ng lint

# Package management
dotnet add package [PackageName]
npm install [package-name]
```

### 📈 Performance Considerations

#### Database Optimization

- **Indexes**: Consider adding indexes on frequently queried columns
- **Lazy Loading**: Disabled by default, use explicit `Include()` for related data
- **Projection**: Use AutoMapper's `ProjectTo()` for efficient queries
- **Async Operations**: All database operations are async

#### Frontend Optimization

- **Lazy Loading**: Implement route-based code splitting
- **Change Detection**: Use OnPush strategy for large lists
- **Bundle Optimization**: Configure webpack for production builds
- **API Caching**: Consider HTTP caching for read-heavy operations

---

## Summary

This Northwind Traders application demonstrates a well-structured implementation of Clean Architecture with .NET and Angular. The codebase showcases modern development practices including CQRS, dependency injection, automated testing, and responsive web design.

**Key Strengths**:
- ✅ Clean separation of concerns across architectural layers
- ✅ Comprehensive CQRS implementation with MediatR  
- ✅ Type-safe frontend integration with auto-generated API client
- ✅ Robust validation and error handling
- ✅ Automated audit trailing and testing infrastructure

**Areas for Enhancement** (if extending the project):
- 🔄 Complete order management workflow implementation
- 📊 Add comprehensive reporting features
- 🔐 Implement role-based authorization
- 📱 Add mobile-responsive optimizations
- ⚡ Implement caching strategies
- 📧 Complete notification service integration

This codebase serves as an excellent reference for implementing Clean Architecture patterns in .NET applications and provides a solid foundation for understanding enterprise application development best practices.
