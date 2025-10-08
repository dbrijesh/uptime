# Project Structure

## Clean Architecture Layers

The project follows Clean Architecture principles with clear separation of concerns:

```
Src/
├── Domain/          # Core business entities and rules (innermost layer)
├── Application/     # Use cases, CQRS handlers, business logic
├── Common/          # Shared utilities and cross-cutting concerns
├── Infrastructure/  # External services, file system, email, etc.
├── Database/        # Contains DDL, DML Database scripts
├── Persistence/     # Database context, repositories, configurations
├── Presentation/    # Contanins API Controllers, DTO's, and handle HTTP requests
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
├── public/
│   ├── index.html      # static assets
│   ├── favicon.ico     # static file
├── src/
│   ├── app/         # Angular components, services, modules
│   ├── app/         # Angular components, services, modules
│   ├── assets/      # Static assets
│       ├── images/        # Global image files
│       ├── icons/         # Global icons
│       ├── fonts/         # Global fonts
│       ├── styles/        # Global style, themes, variables
│   ├── components/      #  reusable, presentational components that are not tied to specific pages or features (e.g., Button, Modal, Input, Card)
│   ├── pages/      #  main entry-point components for different routes or pages of the application
│   ├── hooks/      #  Stores custom React hooks for encapsulating reusable logic (e.g., useAuth, useForm)
│   ├── utils/      #  Contains utility functions, helpers, constants, and other generic JavaScript modules not directly related to UI components or state management
│   ├── services/   # Handles logic related to interacting with external APIs or backend services
│   ├── store/   # Contains files related to global state management using Redux, including reducers, actions, selectors, store configuration
│   ├── routes/   # Defines the application's routing configuration using React Router
│   ├── types/   # Contains general TypeScript types, interfaces, and enums
│   ├── configs/   # Stores application configurations, such as environment variables
│   ├── environments/ # Environment configurations
├── app.tsx     # Serves as the top-level container for all other components in the application
├── index.js     # Entry point for rendering the root component and mounting it to the DOM
├── package.json     # npm dependencies

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

- **React 18.2** - Frontend framework
- **TypeScript 5.9** - Primary language
- **Angular CLI** - Build tooling
- **NgBootstrap 19.0.1** - UI components
- **React Icon 15.6.0** - Icons
- **OIDC Client TS 8.0.16** - Authentication

## Testing

- **xUnit 2.9.3** - Unit testing framework
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

