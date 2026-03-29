# TEMPLATE - TESTING STANDARDS REFERENCE

> **How to use this template:** Copy this file to `project-testing-standards.md` and customize for your project. Replace `{{placeholders}}` with your actual values. Remove sections that don't apply to your stack.

---

## 1. Backend Testing (pytest)

> If stack includes Python + pytest:

### Stack

| Tool | Purpose |
|------|---------|
| pytest | Test runner |
| pytest-cov | Coverage reporting |
| In-memory SQLite + StaticPool | Fast, isolated unit tests |

### Fixtures (conftest.py)

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `app` | session | App with test config (in-memory SQLite) |
| `client` | function | Test client for HTTP calls |
| `db_session` | function | ORM session (auto-rollback between tests) |
| `admin_token` | function | JWT access token for admin user |
| `member_user` / `guest_user` | function | Pre-created test users with cleanup |

### Factory Fixtures

Factory fixtures create entities with sensible defaults and auto-incrementing IDs:

```python
@pytest.fixture
def create_entity(db_session):
    def _create(name='test_entity', **kwargs):
        defaults = {'name': name, 'status': STATUS_ACTIVE}
        defaults.update(kwargs)
        entity = Entity(**defaults)
        db.session.add(entity)
        db.session.flush()
        return entity
    return _create
```

**Rules:**
- Factories return flushed (not committed) model instances.
- Factories accept `**kwargs` to override any default.
- Factories handle FK dependencies.

### Test Pattern

```python
def test_create_entity(client, admin_token):
    response = client.post('/api/{{entities}}/', json={'title': 'Test'},
                           headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 201
    assert response.json['title'] == 'Test'
```

**Rules:**
- File naming: `test_<module>.py`
- Test both success and error paths (401, 403, 404, 400).
- Use fixtures for common setup — avoid repeated boilerplate.
- In-memory SQLite keeps tests fast; no external DB required.

### Integration Tests (Database-Specific)

> If your project has a separate integration test suite against a real database:

**Setup:**
1. Start the test stack: `docker compose -f docker-compose.test.yml up -d`
2. Run integration tests: `cd {{BACKEND_DIR}} && pytest -m integration`
3. Tear down: `docker compose -f docker-compose.test.yml down -v`

**Marker segregation:**
- All integration tests use `pytestmark = pytest.mark.integration`
- Default `pytest` runs only unit tests
- `pytest -m integration` runs only the database-specific suite

**Focus areas for integration tests:**
- Row-level locking behavior
- Unique and FK constraint enforcement
- Timezone-aware datetime behavior
- Transaction rollback, savepoints, error recovery
- Full CRUD cycle for core entities

---

## 2. Frontend Testing (vitest)

> If stack includes React + Vitest:

### Stack

| Tool | Purpose |
|------|---------|
| Vitest | Test runner (Vite-native) |
| @testing-library/react | Component rendering and queries |
| happy-dom | Lightweight DOM environment |
| @vitest/coverage-v8 | Coverage via V8 provider |

### Mock Hierarchy

Mocks are set up in a consistent order at the top of test files:

1. **i18n** — stable `useTranslation` mock (critical)
2. **react-router-dom** — `useNavigate`, `useParams`, `Link`
3. **Context hooks** — `useAuth`, etc.
4. **API modules** — mock the API module, not the HTTP client
5. **Custom hooks** — mock hooks consumed by the component under test
6. **Child components** — render as `data-testid` containers

### Stable useTranslation Mock (CRITICAL)

**Always use this pattern** — unstable mocks cause flaky tests and hangs:

```javascript
vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key) => key,
    i18n: { language: "en-US", changeLanguage: vi.fn() },
  }),
}));
```

**Never** return a new object reference on each call. The mock must be referentially stable.

### Test Setup Helpers

```javascript
beforeEach(() => {
  vi.clearAllMocks();
  // set up mock return values
});

afterEach(() => { cleanup(); });
```

### Component Test Pattern

```javascript
describe("ComponentName", () => {
  it("should render expected content", () => {
    render(<ComponentName />);
    expect(screen.getByText("expected.i18n.key")).toBeTruthy();
  });

  it("should handle user interaction", async () => {
    render(<ComponentName />);
    await act(() => fireEvent.click(screen.getByTestId("action-btn")));
    expect(mockApi.create).toHaveBeenCalled();
  });
});
```

### Hook Test Pattern

```javascript
import { renderHook, act } from "@testing-library/react";

it("should update state", () => {
  const { result } = renderHook(() => useMyHook());
  act(() => { result.current.doSomething(); });
  expect(result.current.value).toBe("expected");
});
```

### Timer-Based Tests

```javascript
beforeEach(() => { vi.useFakeTimers({ shouldAdvanceTime: true }); });
afterEach(() => { vi.runOnlyPendingTimers(); vi.useRealTimers(); });

it("should debounce", async () => {
  const { result } = renderHook(() => useDebouncedSearch(mockFn));
  await act(async () => { result.current.setQuery("test"); });
  vi.advanceTimersByTime(300);
  expect(mockFn).toHaveBeenCalled();
});
```

**Rules:**
- Mock **API modules**, not the HTTP client directly.
- Mock child components as `data-testid` containers when testing parent behavior.
- Use `vi.clearAllMocks()` in `beforeEach`, `cleanup()` in `afterEach`.
- Wrap state updates in `act()`.
- For async operations, use `waitFor()` or `await act(async () => {...})`.

---

## 3. E2E Testing (Playwright)

> If stack includes Playwright:

### Stack & Configuration

| Setting | Value |
|---------|-------|
| Base URL | `{{base_url}}` |
| Parallel | `false` — sequential execution |
| Retries | 0 locally, 1 in CI |
| Timeouts | 60s test, 10s expect, 15s navigation |
| Browser | Chromium only |

### Auth Fixtures (worker-scoped)

```javascript
// Pre-authenticated pages — cached per worker
adminPage   // Browser context with admin JWT
memberPage  // Browser context with member JWT
```

**Rules:**
- Tests share database state — order matters.
- Use pre-authenticated fixtures, not manual login in each test.

---

## 4. Cross-Cutting Rules

### File Naming

| Layer | Pattern | Example |
|-------|---------|---------|
| Backend | `test_<module>.py` | `test_auth_endpoints.py` |
| Frontend component | `ComponentName.test.tsx` | `SettingsPage.test.tsx` |
| Frontend hook | `useHookName.test.ts` | `useToast.test.ts` |
| Frontend utility | `utilityName.test.ts` | `errorUtils.test.ts` |
| E2E | `<feature>.spec.js` | `auth.spec.js` |

### What to Test

- **Always:** success path, common error paths (401, 403, 404, 400)
- **Components:** rendering, user interactions, error display, loading states
- **Hooks:** state transitions, side effects, edge cases
- **API endpoints:** CRUD operations, permission enforcement, input validation
- **E2E:** critical user flows, RBAC enforcement

### What NOT to Test

- Implementation details (internal state shape, private methods)
- Third-party library internals
- Styling/CSS classes (unless behavior-dependent)

### Coverage

- Coverage is reported but no hard threshold is enforced.
- Aim for broad coverage of business logic and user-facing behavior.
- Prioritize untested critical paths over reaching a percentage target.

---

## 5. TanStack Query Testing Patterns

> If stack includes TanStack Query:

Components and hooks using TanStack Query require a `QueryClientProvider` wrapper in tests.

### QueryWrapper Setup

```tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

export const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });

export const QueryWrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={createTestQueryClient()}>
    {children}
  </QueryClientProvider>
);
```

### Usage

```tsx
render(<MyComponent />, { wrapper: QueryWrapper });

const { result } = renderHook(() => useMyQueryHook(), {
  wrapper: QueryWrapper,
});
```

**Rules:**
- Always wrap components/hooks that use `useQuery`/`useMutation` in `QueryWrapper`.
- Use `retry: false` and `gcTime: 0` in test QueryClient.
- Use `waitFor` for async query resolution.
- Mock the API module functions, not the query hooks themselves.

---

## 6. Smoke Testing (Registry-Driven)

> If stack includes a backend framework (Flask, Django, FastAPI, Express):

Smoke tests provide a fast, automated sanity check that all API endpoints respond without server errors. They are driven by a JSON registry file and a generic engine — no per-endpoint test code is needed.

### Architecture

| Component | Location | Purpose |
|-----------|----------|---------|
| `smoke_test_core.py` | `.claude/skills/scripts/` | Generic engine: runner, registry loader, framework adapters, auth adapters |
| `smoke_test_registry.json` | `.claude/skills/scripts/` | Endpoint registry: groups, expected statuses, auth requirements, ID capture |
| `smoke_test_api.py` | `.claude/skills/scripts/` | Thin project-specific runner: imports core, creates test client, loads registry |

### How It Works

1. The runner creates an in-memory test client (e.g., Flask test client with SQLite)
2. Auth setup: registers a test user, logs in, captures JWT
3. For each endpoint group in the registry, sends requests in order
4. Records PASS (expected status), WARN (auth/client errors), or FAIL (5xx or unexpected)
5. Prints a summary report: `PASS: N | WARN: N | FAIL: N`

### Registry Format

```json
{
  "framework": "flask",
  "test_config": "unit_testing",
  "auth": { "register_path": "/api/auth/register", "login_path": "/api/auth/login", ... },
  "groups": [
    {
      "name": "Entity Name",
      "endpoints": [
        { "method": "POST", "path": "/api/entities", "body": {...}, "expect": [201], "auth": true, "capture_id": true },
        { "method": "GET", "path": "/api/entities/{id}", "expect": [200], "auth": true }
      ]
    }
  ]
}
```

### Adding Endpoints

To add a new endpoint to smoke tests, edit `smoke_test_registry.json` — no Python changes needed:

1. Add the endpoint to the appropriate group (or create a new group)
2. Set `expect` to the list of acceptable status codes
3. Set `auth: true` if the endpoint requires authentication, `admin: true` for admin-only
4. Set `capture_id: true` on POST endpoints whose response `id` is needed by subsequent requests
5. Use `{id}` in paths to reference the current group's captured ID, or `{GroupName.id}` for cross-group references

### Running

```bash
# Via the /smoke-test skill (recommended):
/smoke-test api          # API only — fast, no servers needed
/smoke-test ui           # Playwright UI tests only
/smoke-test              # Both (default)

# Directly:
cd backend && python ../.claude/skills/scripts/smoke_test_api.py
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All endpoints responded as expected |
| 1 | One or more endpoints returned unexpected errors |
| 2 | Script-level error (import failure, app creation failure) |

**Rules:**
- Keep the registry up to date when adding new endpoints.
- Smoke tests are not a substitute for unit tests — they verify that endpoints respond, not that business logic is correct.
- The API scope uses an in-memory database, so tests are fast and isolated.

---

## 7. Security Testing Patterns

Security testing should be a first-class concern alongside functional testing.

### Backend — Auth & Permission Tests

```python
# Test unauthenticated access (expect 401)
def test_create_entity_unauthenticated(client):
    response = client.post('/api/{{entities}}/', json={'title': 'Test'})
    assert response.status_code == 401

# Test wrong role (expect 403)
def test_create_entity_as_guest(client, guest_token):
    response = client.post('/api/{{entities}}/', json={'title': 'Test'},
                           headers={'Authorization': f'Bearer {guest_token}'})
    assert response.status_code == 403
```

### Backend — Input Validation Tests

```python
# Test oversized input (expect 400)
def test_create_entity_title_too_long(client, admin_token):
    response = client.post('/api/{{entities}}/', json={'title': 'A' * 1000},
                           headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 400
```

### Frontend — Security-Relevant Component Tests

```javascript
// Test that user-generated HTML is sanitized before rendering
it("should sanitize HTML content before rendering", () => {
  const maliciousContent = '<img src=x onerror="alert(1)">';
  render(<RichTextContent content={maliciousContent} />);
  const img = document.querySelector('img[onerror]');
  expect(img).toBeNull();
});

// Test that admin-only UI is hidden for non-admins
it("should not render admin controls for members", () => {
  mockUseAuth.mockReturnValue({ user: mockUser, isAdmin: () => false });
  render(<SettingsPage />);
  expect(screen.queryByTestId("admin-actions")).toBeNull();
});
```

### Rules

- Every new endpoint must have at least one unauthenticated test (401) and one unauthorized test (403).
- Every endpoint accepting user input must test oversized values against `VALIDATION` constants.
- Every endpoint with schemas must test invalid input shapes (missing required fields, wrong types).
- Components rendering user-generated HTML must test that `<script>` and event handlers are stripped.
