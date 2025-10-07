# Project Structure

## Clean Architecture Layers

The project follows Clean Architecture principles with clear separation of concerns:

```
Src/
├── Domain/          # Core business entities and rules (innermost layer)
├── Application/     # Use cases, CQRS handlers, business logic
├── Common/          # Shared utilities and cross-cutting concerns
├── Infrastructure/  # External services, file system, email, etc.
├── Persistence/     # Database context, repositories, configurations
└── WebUI/          # Presentation layer (API controllers + Angular SPA)
```

## Dependency Flow

- **Domain**: No dependencies (pure business logic)
- **Application**: Depends on Domain only
- **Infrastructure/Persistence**: Depend on Application and Domain
- **WebUI**: Depends on all layers (composition root)

## Key Directories

### Source Code (`Src/`)

- **Domain/**: Entities, value objects, enums, domain events
- **Application/**: 
  - Commands/Queries (CQRS)
  - Handlers (MediatR)
  - DTOs and mapping profiles
  - Interfaces for infrastructure
  - Validation rules (FluentValidation)
- **Common/**: Shared models, exceptions, extensions
- **Infrastructure/**: External service implementations
- **Persistence/**: 
  - DbContext and configurations
  - Repository implementations
  - Database migrations
- **WebUI/**: 
  - Controllers (API endpoints)
  - ClientApp/ (Angular SPA)
  - Configuration and startup

### Frontend Structure (`Src/WebUI/ClientApp/`)

```
ClientApp/
├── src/
│   ├── app/         # Angular components, services, modules
│   ├── assets/      # Static assets
│   └── environments/ # Environment configurations
├── package.json     # npm dependencies
└── angular.json     # Angular CLI configuration
```

### Tests (`Tests/`)

- **Application.UnitTests/**: Application layer unit tests
- **Domain.UnitTests/**: Domain layer unit tests  
- **Persistence.IntegrationTests/**: Database integration tests
- **WebUI.IntegrationTests/**: API and full-stack integration tests

## Naming Conventions

### C# Projects
- **Namespace**: `Northwind.{LayerName}`
- **Assembly**: `Northwind.{LayerName}`
- **Root Namespace**: Matches assembly name

### File Organization
- One class per file
- File name matches class name
- Group related files in folders by feature/aggregate

### CQRS Pattern
- **Commands**: `{Action}Command.cs` (e.g., `CreateProductCommand.cs`)
- **Queries**: `{Action}Query.cs` (e.g., `GetProductsQuery.cs`)
- **Handlers**: `{Action}Handler.cs` (e.g., `CreateProductHandler.cs`)
- **DTOs**: `{Entity}Dto.cs` (e.g., `ProductDto.cs`)

## Configuration Files

- **Solution**: `Northwind.sln`
- **Global SDK**: `global.json` (specifies .NET 8.0)
- **NuGet**: `NuGet.Config`
- **CI/CD**: `azure-pipelines.yml`
- **Git**: `.gitignore`

## Key Patterns

1. **Dependency Injection**: All dependencies registered in WebUI startup
2. **CQRS**: Commands for writes, queries for reads via MediatR
3. **Repository Pattern**: Data access abstraction in Persistence layer
4. **DTO Mapping**: AutoMapper for entity-to-DTO transformations
5. **Validation**: FluentValidation for input validation
6. **Clean Separation**: No circular dependencies between layers



------------------

# Technology Stack

## Backend (.NET)

- **.NET 8.0** - Target framework
- **ASP.NET Core** - Web framework
- **Entity Framework Core 8.0** - ORM and database access
- **MediatR 12.2.0** - CQRS pattern implementation
- **AutoMapper 12.0.1** - Object mapping
- **FluentValidation 11.8.0** - Input validation
- **NSwag 14.0.0** - API documentation and client generation
- **ASP.NET Core Identity** - Authentication and authorization
- **JWT Bearer Authentication** - Token-based auth

## Frontend (Angular)

- **Angular 19.0** - Frontend framework
- **TypeScript 5.6.3** - Primary language
- **Angular CLI** - Build tooling
- **NgBootstrap 18.0.2** - UI components
- **Angular Feather 6.5.0** - Icons
- **OIDC Client TS 3.1.0** - Authentication

## Testing

- **xUnit 2.6.2** - Unit testing framework
- **Moq 4.20.69** - Mocking framework
- **Shouldly 4.2.1** - Assertion library
- **Entity Framework InMemory** - In-memory database for testing
- **Jasmine & Karma** - Angular testing (frontend)

## Build & Deployment

- **Azure Pipelines** - CI/CD
- **NuGet** - Package management
- **npm** - Frontend package management
- **dotnet CLI** - Build tooling

## Common Commands

### Backend Development
```bash
# Build solution
dotnet build

# Run tests
dotnet test

# Run WebUI project
dotnet run --project Src/WebUI/WebUI.csproj

# Restore packages
dotnet restore

# Entity Framework migrations
dotnet ef migrations add <MigrationName> --project Src/Persistence --startup-project Src/WebUI
dotnet ef database update --project Src/Persistence --startup-project Src/WebUI
```

### Frontend Development
```bash
# Navigate to ClientApp
cd Src/WebUI/ClientApp

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint
```

### Full Stack Development
```bash
# Build entire solution
dotnet build

# Run WebUI (includes Angular dev server in development)
dotnet run --project Src/WebUI/WebUI.csproj
```

