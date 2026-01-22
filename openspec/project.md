# Project Context

## Purpose
A comprehensive Python teaching platform designed to deliver interactive coding education through:
- **Course Management**: Structured learning paths with courses, chapters, and problems
- **Interactive Code Execution**: Browser-based Python execution (Pyodide) and server-side judging (Judge0)
- **Progress Tracking**: Detailed monitoring of student learning progress and problem-solving status
- **Assessment System**: Exams with time limits, multiple question types (algorithm, multiple choice, fill-in-blank)
- **Payment Integration**: Alipay-based membership and course enrollment
- **Admin Tools**: Excel import/export for content management and bulk operations

Target users include students learning Python programming, instructors managing course content, and administrators overseeing the platform.

## Tech Stack

### Backend
- **Framework**: Django 5.2.7 with Django REST Framework 3.16.1
- **Database**: PostgreSQL 15
- **Cache/Session**: Redis 7
- **Task Queue**: Celery for asynchronous operations (payment checks, order status)
- **Code Execution**: Judge0 API for server-side judging
- **Package Management**: uv with mirrors for Chinese networks

### Frontend
- **Framework**: React Router v7 (SSR enabled)
- **Language**: TypeScript
- **Styling**: TailwindCSS v4 + MUI (Material-UI)
- **Code Editor**: CodeMirror
- **Browser Execution**: Pyodide for client-side Python execution
- **Package Manager**: pnpm

### DevOps
- **Reverse Proxy**: Nginx 1.28
- **Deployment**: Docker Compose or systemd services
- **Monitoring**: cAdvisor, Prometheus, Grafana
- **Storage**: Multi-backend file storage (Local/S3/MinIO)

## Project Conventions

### Code Style

#### Backend (Python/Django)
- Follow PEP 8 style guide
- Use f-strings for string formatting
- Prefer type hints where applicable
- Model methods: verb-based naming (`get_user_model()`, `run_all_test_cases()`)
- ViewSets: inherit from `ModelViewSet` with appropriate mixins
- Service layer: Business logic in `services.py` files (e.g., `courses/services.py`)

#### Frontend (TypeScript/React)
- Functional components with hooks
- File-based routing convention: `_layout.name.tsx`, `name.$id.tsx`
- Use TypeScript strict mode
- Prefer composition over inheritance
- Custom hooks in `hooks/` directory with `use` prefix
- State management: Zustand for global state
- Avoid excessive abstractions - prefer simple, direct solutions

#### Naming Conventions
- **Backend**: snake_case for variables/functions, PascalCase for classes
- **Frontend**: camelCase for variables/functions, PascalCase for components/types
- **Files**: kebab-case for components, PascalCase for type definitions

### Architecture Patterns

#### Backend
- **App Structure**: Modular Django apps (accounts, courses, commerce, file_management, common)
- **Caching Strategy**: Automatic caching on list/retrieve views (15 min), invalidation on mutations
- **Custom User Model**: Always use `get_user_model()` instead of direct User import
- **Service Layer**: Complex business logic in service classes (e.g., `CodeExecutorService`)
- **Signals**: Auto-create progress records on enrollment
- **Mixin Pattern**: Reusable caching behavior via `CacheListMixin`, `CacheRetrieveMixin`

#### Frontend
- **SSR Proxy Pattern**: Frontend SSR server proxies requests to Django backend
- **Resource Routes**: Loaders for data fetching, actions for mutations (React Router v7)
- **Auth Wrapper**: `withAuth()` for automatic 401 handling and token refresh
- **Centralized Configuration**: Navigation, routes, and API base URLs in config files
- **Component Organization**: Reusable components in `components/`, page-specific in `routes/`

#### API Communication
- **SSR Context**: Server-side requests use `createHttp(request)` to include auth cookies
- **Error Handling**: DRF errors returned with proper `Content-Type: application/json` headers
- **JWT Authentication**: Long-lived tokens with refresh flow on 401
- **Response Format**: Success responses use `data()`, error responses use `data()` with status code

### Testing Strategy

#### Backend
- Unit tests in each app's `tests.py` file
- Load testing with Locust (`test/locustfile.py`)
- Test command: `uv run python manage.py test`
- Focus on critical business logic (code execution, progress tracking, payments)

#### Frontend
- Type checking: `pnpm run typecheck`
- Manual testing for SSR functionality
- No automated unit test suite currently (opportunity for improvement)

### Git Workflow

#### Branching Strategy
- **main**: Production-ready code
- **develop**: Integration branch for features
- **features/**: Feature branches (e.g., `features/problem-exam`)
- **fix/**: Bugfix branches

#### Commit Conventions
- Descriptive commit messages (e.g., "feat:", "fix:", "refactor:")
- Include Co-Authored-By for AI-assisted commits
- PRs require passing builds and reviews
- Use GitHub for code review and CI/CD

#### Example Commit Structure
```
feat: add exam system with timer and auto-submission

- Add Exam, ExamProblem, ExamSubmission models
- Implement timer-based exam taking interface
- Add auto-submission on timeout
```

## Domain Context

### Educational Platform Concepts
- **Enrollment**: Student's registration in a course (creates progress tracking records)
- **Problem Types**:
  - Algorithm: Code execution with test cases
  - Choice: Multiple choice questions
  - Fill-in-blank: Text input with flexible answer validation
- **Progress Hierarchy**: Course → Chapter → Problem (each tracked separately)
- **Unlock Conditions**: Prerequisites (problems must be solved) or time-based unlocks

### Code Execution Flow
1. User submits code via frontend
2. Backend wraps code in template (imports, test case runner)
3. Submit to Judge0 API with test cases
4. Poll for results (status, execution time, memory usage)
5. Return submission record with full results
6. Update progress if all test cases pass

### Payment Flow
1. User selects membership/course
2. Create Order with Alipay trade info
3. Redirect to Alipay for payment
4. Alipay webhook confirms payment
5. Celery task verifies order status
6. Update user's subscription/enrollment

### Exam System
- **Time Limits**: Enforced server-side, frontend shows countdown
- **Question Types**: Choice and fill-in-blank (algorithm support planned)
- **Auto-submission**: When timer expires, current answers are submitted
- **Scoring**: Automatic grading based on correct answers
- **Status Control**: Published/draft mode for exam availability

## Important Constraints

### Performance Constraints
- **Login endpoint**: Known performance issue under high load (4s+ latency) - needs optimization
- **Caching**: 15-minute default cache to reduce database load
- **Code Execution**: Time/memory limits enforced per test case to prevent resource exhaustion

### Security Constraints
- **Code Execution**: Judge0 backend handles sandboxing (never execute user code directly)
- **Authentication**: JWT with long expiry, refresh flow on expiration
- **Payment**: Alipay webhook verification required
- **File Upload**: Multi-backend storage with path validation

### Business Constraints
- **Payment Integration**: Alipay-specific implementation (China market focus)
- **Language**: Chinese-language platform (UI and documentation)
- **Network**: Uses Aliyun mirrors for dependency installation in China

### Development Constraints
- **SSR Compatibility**: All data fetching must work server-side (no browser-only APIs in loaders)
- **Type Safety**: TypeScript strict mode enforced
- **No Time Estimates**: Avoid promising completion timelines (project guideline)

## External Dependencies

### Critical Services
- **Judge0 API**: Server-side code execution (time/memory limits, multiple languages)
- **Alipay SDK**: Payment processing and webhook handling
- **Aliyun Mirrors**: Python package installation (http://mirrors.cloud.aliyuncs.com/pypi/simple/)

### Development Tools
- **uv**: Python package management (faster than pip)
- **pnpm**: Frontend package management
- **Docker Compose**: Local development environment orchestration
- **React Router v7**: SSR-enabled routing with file-based routes

### Monitoring & Infrastructure
- **PostgreSQL 15**: Primary database
- **Redis 7**: Caching, sessions, and Celery broker
- **Nginx 1.28**: Reverse proxy and static file serving
- **cAdvisor/Prometheus/Grafana**: Container metrics and visualization

### Optional/Planned Dependencies
- **S3/MinIO**: Alternative file storage backends (currently local storage default)
- **JupyterLite**: Notebook-style interface (already integrated)
- **Locust**: Load testing framework (configured but not part of runtime)
