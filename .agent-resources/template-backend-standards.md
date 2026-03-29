# TEMPLATE - BACKEND STANDARDS REFERENCE

> **How to use this template:** Copy this file to `project-backend-standards.md` and customize for your project. Replace `{{placeholders}}` with your project's actual values. Remove sections that don't apply to your stack.

---

## 1. Project Structure

> Adapt this tree to your project. The key principle is **layered architecture**: API, services, and models are separated.

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

## 2. Application Factory

> If stack includes Flask:

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

## 3. Configuration

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

## 4. Three-Layer Architecture

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

## 5. Exception Hierarchy

```python
class ServiceError(ValueError):       # Base — maps to 400
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

## 6. Models & ORM Patterns

> If stack includes SQLAlchemy:

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
# Query active records
entities = Entity.query.filter(Entity.deleted_at.is_(None))

# Soft-delete a record
entity.soft_delete()  # sets deleted_at = utcnow()
db.session.commit()
```

**Rules:**
- Soft-delete entities must always filter by `deleted_at.is_(None)`.
- All timestamps are timezone-aware UTC.
- Use a naming convention for deterministic migration constraint names.

---

## 7. Authentication & Authorization

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

> Reference your `project-conceptual-design-as-is.md` for domain-level permission rationale.

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

## 8. API Response Patterns

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

## 9. Internationalization (i18n)

> If stack includes Flask-Babel:

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

## 10. Database Access Patterns

### Query Patterns

```python
# Get by primary key (SQLAlchemy 2.0+)
entity = db.session.get(Entity, entity_id)

# Filter queries
entities = Entity.query.filter_by(status=0).all()

# Soft-delete aware queries
entities = Entity.query.filter(Entity.deleted_at.is_(None))

# Paginated queries
page = Entity.query.paginate(page=1, per_page=20, error_out=False)
```

**Rules:**
- Prefer `db.session.get(Model, pk)` (SQLAlchemy 2.0+ style).
- Always filter soft-deleted records.

---

## 11. Migrations

> If stack includes Alembic:

**Rules:**
- All migrations must be **idempotent** — use `IF NOT EXISTS`, `IF EXISTS`, etc.
- Use PostgreSQL syntax (not MySQL backticks).
- Seed data migrations should be idempotent (insert-if-not-exists).
- Never create cycles in revision dependencies.
- Use separate admin credentials for DDL migrations when possible.

---

## 12. Security

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

---

## 13. Activity Logging

### Automatic Logging

- Attached as `after_request` hook
- Routes mapped to semantic tuples: `(action, entity_type, entity_id)`
- **Logged:** create, update, delete, login, logout, register, search, export, import
- **Skipped:** passive reads

**Rules:**
- When adding a new state-changing endpoint, add route mapping to the activity log service.

---

## 14. Testing

> If stack includes pytest:

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

## 15. Extensions & Libraries

> Document your extensions and their singleton names:

| Extension | Purpose | Singleton |
|-----------|---------|-----------|
| {{extension}} | {{purpose}} | `{{name}}` |

**Rules:**
- Extensions instantiated in `extensions.py` as module-level singletons.
- Extensions initialized with `init_app(app)` in the factory.

---

## 16. Naming Conventions

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

## 17. File & Media Handling

### Upload Flow

1. Validate file uploads — block executable extensions, check MIME types
2. Save with UUID filenames
3. Generate previews if applicable

**Rules:**
- Never serve uploaded files with their original filename — use UUID-based names.
- Validate both file extension and MIME type.

---

## 18. Import/Export

> If applicable, document your import/export architecture:

### Export Formats

> List supported export formats and their serializers.

### Import Architecture

> Document format detection, delegation pattern, and author attribution rules.

**Rules:**
- Import operations are transactional — rollback on failure.

---

## 19. Service Layer Contract

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

---

## 20. Schema Validation Policy

> If stack includes Marshmallow:

### Mandatory Schema Usage

Every endpoint accepting JSON **must** validate through a schema. Raw `json_data.get()` without schema validation is prohibited.

### Schema Pattern

```python
class CreateEntitySchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(load_default='')

class UpdateEntitySchema(Schema):
    title = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String()
```

### Schema File Naming

- One schema file per entity: `<entity>_schemas.py`
- Shared schemas: `common_schemas.py`
- Classes: `Create<Entity>Schema`, `Update<Entity>Schema`

---

## 21. Logging Standards

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

## 22. Dependency Management

### File Structure

| File | Contents | Used By |
|------|----------|---------|
| `requirements.txt` | Production runtime dependencies only | Docker, production |
| `requirements-dev.txt` | Dev/test tools (includes `-r requirements.txt`) | Local dev, CI |

### Rules

- **Pin all versions** with `==`.
- **Production deps** only in `requirements.txt`.
- **Dev deps** in `requirements-dev.txt`.
- Review and update dependencies periodically; run tests after each upgrade.

---

## 23. Test Data Factories

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

## 24. OpenAPI / Swagger Documentation

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
