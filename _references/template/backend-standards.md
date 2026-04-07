# TEMPLATE - BACKEND STANDARDS REFERENCE

> **How to use this template:** Copy this file to `project/backend-standards.md` and customize for your project. Replace `{{placeholders}}` with your project's actual values. Remove sections that don't apply to your stack.
>
> **Section markers:**
> - **`[Core]`** -- implement from day one in every project
> - **`[Extended]`** -- add when the project requires it
> - **`> Applies to: Flask`** / **`> Applies to: FastAPI`** -- framework-specific content; sections without this marker are framework-agnostic

---

## 1. [Core] Project Structure

> Adapt this tree to your project. The key principle is **layered architecture**: API, services, and models are separated.
>
> **See also:** Section 4 (Three-Layer Architecture) for the architectural principles behind this structure; Section 19 (Service Layer Contract) for boundary rules.

```
{{BACKEND_DIR}}/
├── app/                          # Main application package
│   ├── __init__.py              # App factory (create_app)
│   ├── config.py                # Environment-aware configuration classes
│   ├── extensions.py            # Extension singletons
│   ├── exceptions.py            # Custom exception hierarchy
│   ├── api/                     # HTTP layer — one blueprint per entity
│   │   ├── auth.py              # Auth endpoints
│   │   ├── {{entity}}.py        # Entity CRUD
│   │   └── ...
│   ├── models/                  # ORM models
│   │   ├── mixins.py            # Shared mixins (Timestamp, SoftDelete)
│   │   ├── user.py
│   │   ├── {{entity}}.py
│   │   └── ...
│   ├── services/                # Business logic — HTTP-agnostic
│   │   ├── auth_service.py
│   │   ├── {{entity}}_service.py
│   │   └── ...
│   ├── schemas/                 # Validation schemas
│   │   ├── common_schemas.py    # Shared patterns
│   │   ├── {{entity}}_schemas.py
│   │   └── ...
│   ├── utils/                   # Helper utilities
│   │   ├── constants.py         # System-wide constants
│   │   ├── decorators.py        # View decorators
│   │   ├── response_builder.py  # JSON response envelope builders
│   │   ├── validators.py        # Input validation
│   │   └── helpers.py           # Common helpers
│   └── middleware/              # Request/response interceptors
│       ├── permissions.py       # Permission evaluator, route decorators
│       ├── security_headers.py  # HTTP security headers
│       ├── csrf.py              # CSRF protection
│       └── logging_config.py    # Structured logging
├── translations/                # i18n catalogs (if applicable)
├── migrations/                  # Database migrations
├── tests/                       # Test suite
│   ├── conftest.py              # Fixtures
│   └── test_*.py
├── run.py                       # Entry point
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Dev/test dependencies
└── Dockerfile
```

**Rules:**
- `api/` holds only HTTP concerns (request parsing, response building). No business logic.
- `services/` holds HTTP-agnostic business logic. Services never import framework request/response.
- `models/` holds ORM definitions, relationships, and serialization.
- `schemas/` holds validation schemas for request validation.
- `utils/` holds stateless helpers shared across layers.
- `middleware/` holds request/response interceptors.

---

## 2. [Core] Application Factory

> **Applies to: Flask**

**Pattern:** App factory via `create_app(config_name)`.

```python
def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'production')
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # Initialize extensions, register blueprints, install error handlers
    return app
```

**Initialization order:**
1. Load config class -> validate production secrets
2. Initialize extensions
3. Configure CORS
4. Register blueprints
5. Install error handlers
6. Configure structured logging
7. Initialize middleware modules
8. Attach activity logging

**Rules:**
- All extension instances created as module-level singletons in `extensions.py`.
- Production config validates that secrets differ from defaults.
- Guards (CSRF, maintenance) defined in `middleware/` modules, each exposing an `init_<name>(app)` function.

---

## 3. [Core] Configuration

**Pattern:** Class-based configuration with environment override.

| Class | Purpose |
|-------|---------|
| `Config` | Base — loads from `.env`, provides defaults |
| `DevelopmentConfig` | `DEBUG=True`, relaxed CORS |
| `ProductionConfig` | `DEBUG=False`, validates secrets, secure cookies |
| `TestConfig` | Test database |
| `UnitTestConfig` | In-memory SQLite for fast tests |

**Rules:**
- All secrets come from environment variables; never hardcode production secrets.
- `ProductionConfig.validate()` runs at startup and rejects known dev defaults.

---

## 4. [Core] Three-Layer Architecture

> **See also:** Section 1 (Project Structure) for the directory layout implementing these layers; Section 19 (Service Layer Contract) for detailed boundary rules.

```
┌─────────────────────────────┐
│  API Layer (Blueprints)     │  <- HTTP concerns only
│  request -> validate -> call │
├─────────────────────────────┤
│  Service Layer              │  <- Business logic, HTTP-agnostic
│  orchestration, rules       │
├─────────────────────────────┤
│  Data Layer (Models)        │  <- ORM, relationships, serialization
│  ORM + Database             │
└─────────────────────────────┘
```

### API Layer

Responsibilities: parse request, validate input (schema), call service/model, build response.

**Decorator stacking order:**
1. `@bp.route()` — route registration
2. `@jwt_required()` — authentication
3. `@limiter.limit()` — rate limiting (where applicable)
4. `@admin_required()` / `@member_required()` — authorization
5. `@require_json_body` — payload validation

### Service Layer

Responsibilities: business rules, orchestration, raise error hierarchy.

**Rules:**
- Services never import framework request/response objects.
- Services raise typed error subtypes; the API layer catches and maps to HTTP status.
- Services receive plain Python arguments (strings, ints, dicts).

### Data Layer (Models)

Responsibilities: ORM mapping, relationships, `to_dict()` serialization.

**Rules:**
- Models define `to_dict()` for JSON serialization.
- Models may define query helpers but not business rules.

---

## 5. [Core] Exception Hierarchy

> **See also:** Section 8 (API Response Patterns) for how exceptions map to HTTP responses.

```python
class ServiceError(Exception):        # Base — maps to 400
class NotFoundError(ServiceError):     # Maps to 404
class PermissionError(ServiceError):   # Maps to 403
class ValidationError(ServiceError):   # Maps to 400
class AuthenticationError(ServiceError): # Maps to 401
```

**Rules:**
- Services raise `ServiceError` subtypes; never `abort()` or raw HTTP status codes.
- Global `@app.errorhandler` hooks map each exception to its HTTP status.
- Error messages are localized before being sent to the client.

---

## 6. [Core] Models & ORM Patterns

> **See also:** Section 10 (Database Access Patterns) for query style conventions.

> **Applies to: SQLAlchemy**

### Mixins

| Mixin | Provides | Used By |
|-------|----------|---------|
| `TimestampMixin` | `created_at`, `updated_at` (timezone-aware UTC) | Most models |
| `SoftDeleteMixin` | `deleted_at`, `is_active`/`is_deleted`, `soft_delete()`/`restore()` | Soft-deletable entities |

### Relationship Loading Strategies

| Strategy | When to Use |
|----------|------------|
| `lazy='select'` | Default; one-off access to small relations |
| `lazy='selectin'` | Small collections always needed (e.g., translations) |
| `lazy='joined'` | Always-needed 1:1 or small 1:N loaded with parent |
| `lazy='dynamic'` | Large collections that need filtering/pagination |

### Soft Deletes

```python
from sqlalchemy import select

# Query active records (SQLAlchemy 2.0 style)
stmt = select(Entity).where(Entity.deleted_at.is_(None))
entities = db.session.execute(stmt).scalars().all()

# Soft-delete a record
entity.soft_delete()  # sets deleted_at = utcnow()
db.session.commit()
```

**Rules:**
- Soft delete entities must always filter by `deleted_at.is_(None)`.
- All timestamps are timezone-aware UTC.
- Use a naming convention for deterministic migration constraint names.

---

## 7. [Core] Authentication & Authorization

### JWT Authentication

- **Library:** Flask-JWT-Extended with HS256
- **Access token:** {{access_token_expiry}}
- **Refresh token:** {{refresh_token_expiry}}
- **Identity:** User ID stored as string in JWT `sub` claim
- **Revocation:** Tokens added to blocklist table on logout

### Brute-Force Protection

- Exponential back-off lockout
- Rate limiting on auth endpoints

### CSRF Protection

**Pattern:** Double-submit cookie.

### Permission Model

> Reference your `project/conceptual-design-as-is.md` for domain-level permission rationale.

**System-Level:**

| Constant | Value | Capability |
|----------|-------|------------|
| `PROFILE_GUEST` | {{value}} | View only |
| `PROFILE_MEMBER` | {{value}} | Full participation |
| `PROFILE_ADMINISTRATOR` | {{value}} | Full system access |

**Resource-Level:**

> Define resource-scoped permission constants if applicable.

### PermissionEvaluator

Centralized static methods — one rule per method:

```python
PermissionEvaluator.can_admin_system(user)
PermissionEvaluator.can_access_resource(user, resource)
PermissionEvaluator.can_edit_entity(user, entity, resource)
```

### Route Decorators

| Decorator | Effect |
|-----------|--------|
| `@jwt_required()` | Validates JWT, checks revocation |
| `@admin_required()` | Requires administrator |
| `@member_required()` | Requires member or higher |
| `@require_json_body` | Validates JSON payload |

**Rules:**
- Always use `PermissionEvaluator` methods — never inline role comparisons.
- Permission decorators stack after `@jwt_required()`.
- Constants synced between backend and frontend.

---

## 7b. [Core] Object-Level Authorization (BOLA Prevention)

> **See also:** Section 7 (Authentication & Authorization) for role-level checks and route decorators.

> OWASP API Security #1: Broken Object-Level Authorization (BOLA). Every service method that accesses a resource must verify that the requesting user is authorized to access **that specific resource instance**, not just that they have the correct role.

### Pattern

Every service method that retrieves, updates, or deletes a resource should include an ownership or authorization check as its **first operation** after fetching the resource:

```python
def get_entity(entity_id: int, current_user_id: int) -> Entity:
    entity = db.session.get(Entity, entity_id)
    if entity is None:
        raise NotFoundError(f"Entity {entity_id} not found")

    # Object-level authorization — MUST come before any business logic
    if not PermissionEvaluator.can_access_entity(current_user_id, entity):
        raise PermissionError("Not authorized to access this resource")

    return entity
```

### When to Apply

| Check Type | When to Use |
|-----------|-------------|
| **Role-level** (system permissions) | Operations not tied to a specific resource (e.g., "can create entities", "can view admin dashboard") |
| **Object-level** (resource ownership) | Any read, update, or delete of a specific resource instance (e.g., "can edit *this* entity") |
| **Both** | Most mutating operations: first check role, then check object-level ownership |

### Rules

- Never assume that a valid JWT or role check implies access to a specific resource.
- Object-level checks belong in the **service layer**, not in route decorators (decorators handle role-level checks).
- Test both positive and negative authorization paths: a user who owns resource A must NOT be able to access resource B.
- For list endpoints, apply filtering in the query (e.g., `WHERE owner_id = :current_user_id`) rather than post-fetch filtering.

---

## 8. [Core] API Response Patterns

> **See also:** Section 5 (Exception Hierarchy) for the error types these responses map to.

### Response Builder

| Function | HTTP Status | Envelope |
|----------|-------------|----------|
| `rb.success(data)` | 200 | `{ ...data }` |
| `rb.created(data)` | 201 | `{ ...data }` |
| `rb.no_content()` | 204 | empty body |
| `rb.error(msg, status)` | 4xx/5xx | `{ "error": "msg" }` |
| `rb.not_found(msg)` | 404 | `{ "error": "msg" }` |
| `rb.forbidden(msg)` | 403 | `{ "error": "msg" }` |
| `rb.paginated(items, total, page, pages, has_next)` | 200 | `{ "items": [...], ... }` |

**Rules:**
- Always use response builder — never `jsonify()` + manual status codes.
- Success data at top level (no wrapping envelope).
- Error messages localized.

---

## 9. [Extended] Internationalization (i18n)

> **Applies to: Flask-Babel**

### Setup

- **Framework:** Flask-Babel with gettext catalogs
- **Catalogs:** `translations/{locale}/LC_MESSAGES/messages.po`
- **Default locale:** `{{BACKEND_DEFAULT_LOCALE}}`

### Locale Negotiation

Priority: query string (`?lang=...`) -> `Accept-Language` header -> default.

### Adding New Translatable Strings

1. Add the string to all `.po` files
2. Compile catalogs: `pybabel compile -d translations`
3. Use helper functions in code

**Rules:**
- Every user-facing error or message must be localized.
- `.mo` files are compiled build artifacts — rebuild via `pybabel compile`.

---

## 10. [Core] Database Access Patterns

> **See also:** Section 6 (Models & ORM Patterns) for model definitions and mixins.

### Query Patterns

```python
from sqlalchemy import select

# Get by primary key (SQLAlchemy 2.0+)
entity = db.session.get(Entity, entity_id)

# Filter queries (SQLAlchemy 2.0 style)
stmt = select(Entity).where(Entity.status == 0)
entities = db.session.execute(stmt).scalars().all()

# Soft-delete aware queries
stmt = select(Entity).where(Entity.deleted_at.is_(None))
entities = db.session.execute(stmt).scalars().all()

# Paginated queries
stmt = select(Entity).where(Entity.deleted_at.is_(None)).limit(per_page).offset((page - 1) * per_page)
items = db.session.execute(stmt).scalars().all()
total = db.session.execute(select(func.count()).select_from(Entity).where(Entity.deleted_at.is_(None))).scalar()
```

**Rules:**
- Use SQLAlchemy 2.0 `select()` statement style for all queries. Avoid the legacy `Model.query` interface.
- Use `db.session.get(Model, pk)` for primary key lookups.
- Always filter soft-deleted records.

---

## 11. [Core] Migrations

> **Applies to: Alembic**

**Rules:**
- All migrations must be **idempotent** — use `IF NOT EXISTS`, `IF EXISTS`, etc.
- Use PostgreSQL syntax (not MySQL backticks).
- Seed data migrations should be idempotent (insert-if-not-exists).
- Never create cycles in revision dependencies.
- Use separate admin credentials for DDL migrations when possible.

---

## 12. [Core] Security

### Security Headers

Applied via `after_request`:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `Content-Security-Policy: default-src 'self'`
- `Strict-Transport-Security` (production)
- `Referrer-Policy: strict-origin-when-cross-origin`

### Rate Limiting

- Default: {{default_rate_limit}} per IP
- Auth endpoints: stricter limits
- Production storage: Redis; development: in-memory fallback

### Input Validation

- Schema validation for structured request validation
- Format checks (email, login, password strength)
- Shared `VALIDATION` constants for field length limits (synced with frontend)
- File upload validation: blocked executable extensions, MIME type checks

### Maintenance Mode

- Toggled via system setting
- `before_request` guard blocks non-admin requests with 503

**Rules:**
- Never trust client input — validate at the API boundary.
- CORS restricted to `/api/*` routes with explicit origin allowlist.
- Secure cookies in production.

### Dependency Vulnerability Scanning

Regularly scan dependencies for known vulnerabilities:

| Tool | Command | Use Case |
|------|---------|----------|
| `pip-audit` | `pip-audit` | Audit installed packages against PyPI advisory database |
| `safety` | `safety check` | Check requirements against Safety DB |

**Rules:**
- Run dependency scanning in CI on every pull request.
- Block merges when critical or high-severity vulnerabilities are found.
- Reference: [OWASP API Security Top 10](https://owasp.org/API-Security/) for comprehensive API threat coverage.

---

## 13. [Core] Activity Logging

### Automatic Logging

- Attached as `after_request` hook
- Routes mapped to semantic tuples: `(action, entity_type, entity_id)`
- **Logged:** create, update, delete, login, logout, register, search, export, import
- **Skipped:** passive reads

**Rules:**
- When adding a new state-changing endpoint, add route mapping to the activity log service.

---

## 14. [Core] Testing

> **Applies to: pytest**

### Key Fixtures

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `app` | session | App with in-memory SQLite |
| `client` | function | Test client |
| `db_session` | function | SQLAlchemy session (auto-rollback) |
| `admin_token` | function | JWT access token for admin user |

### Test Pattern

```python
def test_create_entity(client, admin_token):
    response = client.post('/api/{{entities}}/', json={'title': 'Test'},
                           headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 201
```

### Integration Tests

> If your project uses a separate integration test suite against a real database, document the setup here.

**Rules:**
- Test files follow `test_<module>.py` naming.
- Use fixtures for common setup.
- Test both success and error paths (401, 403, 404, 400).

---

## 15. [Extended] Extensions & Libraries

> Document your extensions and their singleton names:

| Extension | Purpose | Singleton |
|-----------|---------|-----------|
| {{extension}} | {{purpose}} | `{{name}}` |

**Rules:**
- Extensions instantiated in `extensions.py` as module-level singletons.
- Extensions initialized with `init_app(app)` in the factory.

---

## 16. [Core] Naming Conventions

| Category | Convention | Examples |
|----------|-----------|---------|
| Modules | `snake_case.py` | `auth_service.py`, `{{entity}}_schemas.py` |
| Classes | `PascalCase` | `User`, `PermissionEvaluator` |
| Functions | `snake_case` | `create_app`, `authenticate_user` |
| Constants | `UPPER_SNAKE_CASE` | `PROFILE_ADMINISTRATOR` |
| Blueprints | `snake_case` | `auth`, `{{entity}}` |
| URL prefixes | `kebab-case` | `/api/{{entities}}` |
| DB tables | `snake_case` (plural) | `users`, `{{entities}}` |
| DB columns | `snake_case` | `user_id`, `created_at` |
| Config vars | `UPPER_SNAKE_CASE` | `JWT_SECRET_KEY`, `UPLOAD_FOLDER` |
| Test files | `test_<module>.py` | `test_auth.py`, `test_{{entity}}.py` |

---

## 17. [Extended] File & Media Handling

### Upload Flow

1. Validate file uploads — block executable extensions, check MIME types
2. Save with UUID filenames
3. Generate previews if applicable

**Rules:**
- Never serve uploaded files with their original filename — use UUID-based names.
- Validate both file extension and MIME type.

---

## 18. [Extended] Import/Export

> If applicable, document your import/export architecture:

### Export Formats

> List supported export formats and their serializers.

### Import Architecture

> Document format detection, delegation pattern, and author attribution rules.

**Rules:**
- Import operations are transactional — rollback on failure.

---

## 19. [Core] Service Layer Contract

> **See also:** Section 4 (Three-Layer Architecture) for the overall layer model; Section 1 (Project Structure) for file organization.

### Boundary Rules

Services are the **sole owners of business logic**.

**Services must:**
- Accept plain Python arguments — never framework request/response objects.
- Raise typed error subtypes — never `abort()` or raw HTTP status codes.
- Return plain Python objects — never serialized responses.

**Services should not:**
- Import framework request objects.
- Use `current_app.logger` — use `logging.getLogger(__name__)`.
- Access `current_app.config` directly — prefer dependency injection.

### Config Access Pattern

**Preferred (dependency injection):**

```python
def save_file(file_data, upload_folder: str):
    path = os.path.join(upload_folder, generate_uuid_filename())
    ...
```

**Acceptable (config dataclass):**

```python
@dataclasses.dataclass(frozen=True)
class ServiceConfig:
    some_setting: str = 'default'

    @classmethod
    def from_flask_config(cls, cfg: dict) -> 'ServiceConfig':
        return cls(some_setting=cfg.get('SOME_SETTING', 'default'))
```

### Caching Strategy

Caching is a service-layer concern. Apply caching within services, not in route handlers or models.

| Level | When to Use | Implementation |
|-------|-------------|----------------|
| **Application cache** | Expensive computations, repeated lookups | Redis or in-memory cache (e.g., `cachetools`, `functools.lru_cache`) |
| **HTTP cache headers** | Responses that are safe to cache at the client or CDN | `Cache-Control`, `ETag`, `Last-Modified` headers in the API layer |
| **Query result cache** | Frequently accessed, rarely changed data | Cache at the service layer with TTL-based invalidation |

**Rules:**
- Cache at the service layer — never at the model or route layer.
- Use TTL-based expiration as the default invalidation strategy.
- Invalidate caches explicitly on write operations (create, update, delete) that affect cached data.
- Never cache user-specific or permission-dependent data without including the user/role in the cache key.
- Log cache hit/miss ratios for observability.

---

## 20. [Core] Schema Validation Policy

> **See also:** Section 19 (Service Layer Contract) for how validated data flows into services.

### Mandatory Schema Usage

Every endpoint accepting JSON **must** validate through a schema. Raw `json_data.get()` without schema validation is prohibited.

### Library Choice

| Library | Best For | Decision Criteria |
|---------|----------|-------------------|
| **Pydantic** | FastAPI projects, data parsing/coercion, settings management, JSON Schema generation | Native FastAPI integration; automatic type coercion; excellent for request/response models and configuration. Preferred for new projects. |
| **Marshmallow** | Flask projects, complex nested schemas, custom field-level validation, serialization/deserialization asymmetry | Mature Flask ecosystem support; fine-grained control over load vs. dump behavior; better for complex validation pipelines. |

Choose one library per project and use it consistently. Do not mix Pydantic and Marshmallow in the same codebase.

### Marshmallow Schema Pattern

> **Applies to: Marshmallow**

```python
class CreateEntitySchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(load_default='')

class UpdateEntitySchema(Schema):
    title = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String()
```

### Pydantic Schema Pattern

> **Applies to: Pydantic**

```python
from pydantic import BaseModel, Field

class CreateEntityRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = ""

class UpdateEntityRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
```

### Schema File Naming

- One schema file per entity: `<entity>_schemas.py`
- Shared schemas: `common_schemas.py`
- Classes: `Create<Entity>Schema`, `Update<Entity>Schema` (Marshmallow) or `Create<Entity>Request`, `Update<Entity>Request` (Pydantic)

---

## 21. [Core] Logging Standards

### Module-Level Logger

```python
import logging
logger = logging.getLogger(__name__)
```

### Log Levels

| Level | When to Use |
|-------|------------|
| `logger.debug()` | Detailed diagnostics (disabled in production) |
| `logger.info()` | Normal operational events |
| `logger.warning()` | Unexpected but recoverable situations |
| `logger.error()` | Failures affecting a single request |
| `logger.exception()` | Same as error with stack trace |
| `logger.critical()` | System-wide failures |

### Structured JSON Logging

All log output JSON-formatted with request context enrichment:

| Field | Source |
|-------|--------|
| `timestamp` | ISO 8601 with timezone |
| `level` | Python log level |
| `name` | Logger name |
| `message` | Log message |
| `request_id` | UUID4 per request |
| `user_id` | From JWT identity |

**Rules:**
- Never use `current_app.logger` in services.
- Include relevant context in log messages.
- Suppress noisy third-party loggers in production.

---

## 22. [Core] Dependency Management

### Recommended: `pyproject.toml` + Lock File

Use `pyproject.toml` as the single source of truth for project metadata and dependencies. Use a lock file for reproducible installs.

| Tool | Lock File | Install Command |
|------|-----------|-----------------|
| `uv` | `uv.lock` | `uv sync` |
| `pip-tools` | `requirements.lock` | `pip install -r requirements.lock` |

```toml
# pyproject.toml (example)
[project]
name = "{{PROJECT_NAME}}"
requires-python = ">=3.11"
dependencies = [
    "flask>=3.0",
    # ... production dependencies
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    # ... dev/test dependencies
]
```

### Legacy Alternative: `requirements.txt`

For simpler projects or legacy codebases:

| File | Contents | Used By |
|------|----------|---------|
| `requirements.txt` | Production runtime dependencies only | Docker, production |
| `requirements-dev.txt` | Dev/test tools (includes `-r requirements.txt`) | Local dev, CI |

### Rules

- **Pin all versions** in lock files for reproducible builds.
- **Use ranges** in `pyproject.toml` (e.g., `>=3.0,<4.0`) to allow compatible updates.
- **Production deps** separated from dev deps (via `[project.optional-dependencies]` or separate files).
- Review and update dependencies periodically; run tests after each upgrade.

---

## 23. [Extended] Test Data Factories

### Factory Fixtures

```python
@pytest.fixture
def create_entity(db_session):
    def _create(name='Test Entity', **kwargs):
        defaults = {'name': name, 'status': STATUS_ACTIVE}
        defaults.update(kwargs)
        entity = Entity(**defaults)
        db.session.add(entity)
        db.session.flush()
        return entity
    return _create
```

**Rules:**
- Each factory returns the created model instance (flushed but not committed).
- Factories accept `**kwargs` for overriding any default.
- Factories handle FK dependencies.

---

## 24. [Extended] OpenAPI / Swagger Documentation

> If applicable:

Auto-generated OpenAPI spec via `apispec` with schema plugin.

| Route | Response |
|-------|----------|
| `GET /api/docs` | Swagger UI |
| `GET /api/docs/openapi.json` | Raw OpenAPI spec |

**Rules:**
- New endpoints automatically included.
- Schemas must be importable to appear in the spec.
- Docstrings on route handlers used as operation descriptions.

---

## 25. [Extended] Module-Level README Convention

Every backend sub-package directory should contain a `README.md` with a module index table and update instructions.

**Required in:** `app/api/`, `app/models/`, `app/services/`, `app/schemas/`, `app/utils/`, `app/middleware/`

**Template:**

| File | Responsibility |
|------|---------------|
| `{{filename}}.py` | {{one-line description}} |

**Rules:**
- Update the README when adding, removing, or renaming files in the directory.
- Keep descriptions to one line per file.
- Include a "Design Conventions" subsection if the module follows specific patterns (e.g., "all services accept and return dicts, not model instances").

---

## 26. [Core] Operational Readiness

### Health Check Endpoints

Every deployed backend must expose health check endpoints for orchestrator probes:

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `GET /health/live` | Liveness probe -- process is running | `200 {"status": "ok"}` |
| `GET /health/ready` | Readiness probe -- dependencies are reachable | `200 {"status": "ready"}` or `503 {"status": "not_ready", "checks": {...}}` |

**Readiness checks** should verify critical dependencies:
- Database connection (execute a lightweight query like `SELECT 1`)
- Cache connectivity (Redis ping, if applicable)
- External service availability (if critical to request handling)

**Rules:**
- Health endpoints must not require authentication.
- Liveness probes must not check external dependencies (they only confirm the process is alive).
- Readiness probes must have timeouts to avoid blocking the orchestrator.

### Graceful Shutdown

- Handle `SIGTERM` by stopping acceptance of new requests and completing in-flight requests within a configurable timeout.
- Close database connections and flush logs before exiting.
- If using background workers (Celery, task queues), allow active tasks to complete or re-queue them.

### Container Security

When deploying via Docker (referenced in section 1 project structure):

```dockerfile
# Use multi-stage builds to minimize image size
FROM python:{{python_version}}-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

FROM python:{{python_version}}-slim
# Run as non-root user
RUN useradd --create-home appuser
USER appuser
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .
CMD [".venv/bin/python", "run.py"]
```

**Rules:**
- **Run as non-root**: always set a `USER` directive in production Dockerfiles.
- **Pin base image digests**: use `python:3.12-slim@sha256:...` for reproducible builds.
- **Multi-stage builds**: separate build dependencies from runtime image.
- **No secrets in images**: use environment variables or secret managers, never bake secrets into layers.
- **Minimize attack surface**: use slim/distroless base images; remove build tools from the runtime stage.

---

## 27. [Extended] Async Patterns

### When to Use Async

| Pattern | Best For | Framework |
|---------|----------|-----------|
| **Sync (WSGI)** | CPU-bound work, simple CRUD, projects using Flask/Django | Flask, Django |
| **Async (ASGI)** | I/O-bound work, high-concurrency APIs, WebSockets, streaming | FastAPI, Starlette |

Choose one paradigm per service and use it consistently. Do not mix sync and async handlers in the same application unless the framework explicitly supports it.

### Async Database Access

> **Applies to: FastAPI / ASGI**

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select

async def get_entity(session: AsyncSession, entity_id: int) -> Entity:
    result = await session.execute(select(Entity).where(Entity.id == entity_id))
    return result.scalar_one_or_none()
```

**Rules:**
- Use `create_async_engine` with an async-compatible driver (e.g., `asyncpg` for PostgreSQL).
- Use `AsyncSession` for all database operations in async code.
- Never call sync database operations inside `async def` functions -- use `run_in_executor` if wrapping legacy sync code.

### Background Task Processing

| Tool | When to Use |
|------|-------------|
| **Celery** | Long-running tasks, scheduled jobs, distributed task queues across multiple workers |
| **asyncio tasks** | Short-lived I/O-bound tasks within the same process (e.g., sending an email after responding) |
| **arq / dramatiq** | Lightweight async-native alternatives to Celery |

**Rules:**
- Offload any operation that takes >500ms to a background task.
- Background tasks must be idempotent -- they may be retried on failure.
- Use a dead-letter queue for tasks that fail repeatedly.
- Log task start, completion, and failure for observability.

---

## 28. [Extended] API Versioning

### Strategy

Choose a versioning strategy and apply it consistently:

| Strategy | Format | Pros | Cons |
|----------|--------|------|------|
| **URL path** (recommended) | `/api/v1/entities` | Explicit, easy to route, cacheable | URL proliferation |
| **Header** | `Accept: application/vnd.api+json; version=2` | Clean URLs | Harder to test, not cacheable by default |
| **Query parameter** | `/api/entities?version=1` | Simple to implement | Pollutes query string, caching issues |

### Deprecation Policy

When retiring an API version:

1. **Announce**: add a `Sunset` header to responses from the deprecated version: `Sunset: Sat, 01 Mar 2025 00:00:00 GMT`
2. **Warn**: add a `Deprecation` header: `Deprecation: true`
3. **Grace period**: maintain the deprecated version for at least {{deprecation_grace_period}} after the announcement
4. **Remove**: return `410 Gone` after the sunset date

**Rules:**
- Never break an existing API version -- breaking changes require a new version.
- Document version differences in the OpenAPI spec (section 24).
- Default to the latest stable version when no version is specified.
