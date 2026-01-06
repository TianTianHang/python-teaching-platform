# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python teaching platform with a Django REST Framework backend and React Router v7 SSR frontend. It includes course management, interactive coding problems, code execution (via Judge0/Pyodide), progress tracking, and payment processing (Alipay).

**Tech Stack:**
- Backend: Django 5.2.7, DRF 3.16.1, Celery, PostgreSQL/Redis
- Frontend: React Router v7 (SSR), TypeScript, TailwindCSS, MUI, CodeMirror
- Code Execution: Judge0 API (backend) + Pyodide (browser)

## Development Commands

### Backend (Django)
```bash
cd backend

# Install dependencies (using uv)
uv sync --index-url='http://mirrors.cloud.aliyuncs.com/pypi/simple/'

# Run development server
python manage.py runserver

# Run Celery worker (for async tasks)
celery -A core worker -l INFO -P solo

# Database migrations
python manage.py migrate
python manage.py makemigrations

# Create superuser
python manage.py createsuperuser
# or use the custom command
python manage.py create_default_superuser

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test

# Populate sample data
python manage.py populate_sample_data
```

### Frontend (React Router)
```bash
cd frontend/web-student

# Install dependencies
pnpm i

# Development server (with SSR)
pnpm run dev

# Build for production
pnpm run build

# Start production server
pnpm run start

# Type checking
pnpm run typecheck
```

### Docker Deployment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f web-student
```

## Backend Architecture

### Django Apps

**accounts** - User management and authentication
- Custom `User` model (extends AbstractUser) with `st_number` and `avatar` fields
- `MembershipType` and `Subscription` for paid memberships
- JWT authentication via `rest_framework_simplejwt`
- Views: login, register, token refresh, user profile

**courses** - Core educational content
- Models: `Course` → `Chapter` → `Problem` (hierarchical)
- Problem types: `algorithm` (coding) and `choice` (multiple choice)
- `AlgorithmProblem`: time/memory limits, test cases, solution function name
- `ChoiceProblem`: choices, correct answers
- `ProblemUnlockCondition`: prerequisite problems, unlock dates
- Progress tracking: `Enrollment`, `ChapterProgress`, `ProblemProgress`
- `CodeExecutorService` ([services.py](backend/courses/services.py)): Wrapper for Judge0 API
- ViewSets use custom caching mixins from `common/mixins/`

**commerce** - Payment and orders
- `Order` and `OrderItem` models
- Alipay integration via `alipay-sdk-python`
- Celery tasks for order status checks
- Payment webhook handling

**file_management** - File storage abstraction
- Support for local, S3, and MinIO storage backends
- Unified file API with path utilities

**common** - Shared utilities
- `mixins/cache_mixin.py`: `CacheListMixin`, `CacheRetrieveMixin`, `InvalidateCacheMixin`
- `utils/cache.py`: Redis caching helpers

### Key Backend Patterns

**Caching Strategy:**
- List/retrieve views automatically cache responses (15 min default)
- Create/update/delete operations invalidate related caches
- Cache keys include view name, query params, and PK

**Code Execution Flow:**
1. User submits code via API
2. `CodeExecutorService.run_all_test_cases()` wraps user code in template
3. Submits to Judge0 backend with test cases
4. Polls for results, tracks max time/memory
5. Updates `Submission` record with final status

**Custom User Model:**
```python
AUTH_USER_MODEL = 'accounts.User'
```
Always use `get_user_model()` when referencing the User model.

### Backend Configuration

**Environment Variables** ([.env](backend/.env)):
```
SECRET_KEY=...
DEBUG=True/False
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JUDGE0_BASE_URL=http://...
JUDGE0_API_KEY=...
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://...
```

**Settings structure:**
- `core/settings.py` - Main settings with environment-based config
- Uses `django-environ` for .env file parsing
- Session backend: Redis
- Cache backend: Redis (via django-redis)

## Frontend Architecture

### Directory Structure ([app/](frontend/web-student/app/))
```
app/
├── routes/          # File-based routing (React Router v7)
├── components/      # Reusable UI components
├── config/          # Configuration files (navigation, etc.)
├── hooks/           # Custom React hooks
├── stores/          # Zustand state management
├── utils/           # Utility functions
├── design-system/   # Design tokens and theme configuration
├── theme/           # Theme-related code (dark/light mode)
├── types/           # TypeScript type definitions
└── root.tsx         # Root component with providers
```

### Routing

**File-based routing** ([routes.ts](frontend/web-student/app/routes.ts)):
- Uses `@react-router/fs-routes` with `flatRoutes()`
- Route files follow naming convention: `_layout.name.tsx`, `name.$id.tsx`
- SSR enabled by default ([react-router.config.ts](frontend/web-student/react-router.config.ts))

**Key routes:**
- `/home` - Dashboard
- `/courses` - Course listing
- `/courses/$courseId` - Course detail
- `/courses/$courseId/chapters/$chapterId` - Chapter content
- `/problems` - Problem listing
- `/problems/$problemId` - Problem detail
- `/playground` - Code playground (Pyodide-based)
- `/jupyter` - JupyterLite integration
- `/profile` - User profile
- `/membership` - Membership plans

**Navigation config** ([config/navigation.ts](frontend/web-student/app/config/navigation.ts)):
- Single source of truth for navigation items
- Functions: `getNavItems()`, `findNavItem()`, `isActivePath()`

### State Management

- **Zustand** for global state ([stores/globalStore.ts](frontend/web-student/app/stores/globalStore.ts))
- **Session storage** for server-side data ([sessions.server.ts](frontend/web-student/app/sessions.server.ts))
- **Local storage** wrapper ([localstorage.server.ts](frontend/web-student/app/localstorage.server.ts))

### Custom Hooks

- `usePyodide.ts` - Pyodide browser-based Python execution
- `useThemeMode.ts` - Dark/light mode switching
- `useUser.ts` - User authentication state
- `useSubmission` - Code submission tracking

### Styling

- **TailwindCSS** v4 for utility classes
- **MUI** (Material-UI) components for complex UI elements
- **Design system** in [design-system/](frontend/web-student/app/design-system/)
- Theme switching support (dark/light mode)

### API Communication

- **Axios** for HTTP requests
- Base URL configurable via `API_BASE_URL` environment variable
- JWT token handling via refresh endpoint

## Database Schema

### Core Models

**User** (accounts):
- `st_number` (CharField, unique) - Student ID
- `avatar` (TextField) - Avatar URL

**Course** → **Chapter** → **Problem** hierarchy:
- `Course`: title, description, created_at, updated_at
- `Chapter`: course (FK), title, content, order
- `Problem`: chapter (FK, nullable), type (algorithm/choice), title, content, difficulty (1-3)

**AlgorithmProblem** (problem related_name='algorithm_info'):
- `time_limit` (ms)
- `memory_limit` (MB)
- `solution_name` (dict mapping language to function name)
- `test_cases` (ManyToMany to TestCase)

**ChoiceProblem** (problem related_name='choice_info'):
- `choices` (JSONField)
- `correct_answers` (JSONField)

**Submission**:
- user, problem, code, language, status
- execution_time, memory_used, output, error

**Progress Tracking**:
- `Enrollment`: user + course
- `ChapterProgress`: enrollment, chapter, is_completed
- `ProblemProgress`: enrollment, problem, is_solved

## Testing

### Backend Tests
- Located in each app's `tests.py` (e.g., [courses/tests.py](backend/courses/tests.py))
- Run with `python manage.py test`
- Load testing with Locust ([test/locustfile.py](test/locustfile.py))

### Frontend Type Checking
```bash
pnpm run typecheck
```

## Deployment Architecture

### Production Stack (Manual Deployment)
- **Nginx 1.28** as reverse proxy
  - Port 80: Frontend SSR (web-student)
  - Port 8080: Backend admin API
- **PostgreSQL 15** for database
- **Redis 7** for caching/sessions
- **Systemd services** for each component

### Docker Deployment
- Services: db, redis, backend, web-student, nginx, cadvisor, prometheus, grafana
- Nginx proxies to backend (port 8000) and web-student (port 3000)
- Static files served via volume mounts

### Performance Monitoring
- **cAdvisor** - Container metrics (port 8081)
- **Prometheus** - Metrics collection (port 9090)
- **Grafana** - Metrics dashboard (port 3000)

## Important Implementation Notes

1. **Authentication**: JWT tokens with long expiry (configured in settings). Always include `Authorization: Bearer <token>` header.

2. **Code Execution Safety**: Judge0 backend handles actual execution. Time/memory limits enforced per test case.

3. **Caching**: Most list/retrieve endpoints are cached. When modifying data, cache invalidation happens automatically via mixins.

4. **Progress Tracking**: Signals ([courses/signals.py](backend/courses/signals.py)) auto-create progress records on enrollment.

5. **File Uploads**: Configured for multiple backends (local/S3/MinIO). See [file_management/storages.py](backend/file_management/storages.py).

6. **Payment**: Alipay integration uses webhook callbacks. Order status checked via Celery tasks.

7. **Known Issues**:
   - Login endpoint has performance issues under high load (4s+ latency) - see [README.md](README.md)

## File Reference Locations

- Backend settings: [backend/core/settings.py](backend/core/settings.py)
- Main URL config: [backend/core/urls.py](backend/core/urls.py)
- Code execution service: [backend/courses/services.py](backend/courses/services.py)
- Frontend navigation: [frontend/web-student/app/config/navigation.ts](frontend/web-student/app/config/navigation.ts)
- Caching mixins: [backend/common/mixins/cache_mixin.py](backend/common/mixins/cache_mixin.py)
- Judge0 backend wrapper: [backend/courses/judge_backend/](backend/courses/judge_backend/)
