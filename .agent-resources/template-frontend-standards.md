# TEMPLATE - FRONTEND STANDARDS REFERENCE

> **How to use this template:** Copy this file to `project-frontend-standards.md` and customize for your project. Replace `{{placeholders}}` with your project's actual values. Remove sections that don't apply to your stack. Add project-specific components, hooks, and patterns as they emerge.

---

## 1. Project Structure

> Adapt this tree to your project. The key principle is **feature co-location**: domain-specific code lives together, shared code is centralized.

```
{{FRONTEND_DIR}}/src/
├── api/              # One module per entity + shared HTTP client instance
├── assets/           # Static images and resources
├── components/
│   ├── common/         # Reusable, domain-agnostic components
│   ├── forms/          # Shared form primitives
│   ├── layout/         # Layout wrapper and page structure
│   └── {{domain}}/     # Domain-specific shared components
├── context/          # React Context providers
├── features/         # Feature-scoped components, hooks, forms, utils by domain
│   └── {{domain}}/     # Domain feature folder
├── hooks/            # Cross-cutting custom hooks only
├── i18n/
│   └── locales/      # Translation files
├── pages/            # Page-level orchestrator components (one per route)
├── routes/           # Route definitions and guards
├── services/         # Non-API services (storage, event bus)
├── types/            # TypeScript type definitions
├── utils/            # Utility functions and constants
├── App.{{ext}}       # Root component with provider hierarchy
├── index.css         # CSS framework directives + custom component classes
└── main.{{ext}}      # Entry point
```

**Rules:**
- `components/common/` holds reusable, domain-agnostic components.
- `components/forms/` holds **shared form primitives** only.
- `features/{{domain}}/` holds feature-scoped components, hooks, forms, and utils for a single domain.
- `pages/` holds one **orchestrator** per route — state and effects live here, rendering delegated to sub-components.
- `hooks/` holds **only cross-cutting** hooks used by 2+ unrelated domains.
- Feature-specific hooks live **co-located** in `features/{{domain}}/`.

---

## 2. Component Patterns

> If stack includes React:

All components are **functional components** using React Hooks. No class components. All source files use TypeScript (`.ts`/`.tsx`).

### Structure Template

```tsx
/**
 * @fileoverview Brief description of the component's purpose.
 * @module components/path/ComponentName
 */
import { useState, useEffect, useCallback } from "react";
import { useTranslation } from "react-i18next";

/**
 * Description of the component.
 * @param {Object} props
 * @param {string} props.title - The title to display
 * @param {Function} props.onSubmit - Callback when form submits
 * @returns {JSX.Element}
 */
const ComponentName = ({ title, onSubmit }: Props) => {
  const { t } = useTranslation();
  const [value, setValue] = useState("");

  return <div>{t("key")}</div>;
};

export default ComponentName;
```

**Rules:**
- Props are destructured in the function signature.
- Default export for components and hooks.
- JSDoc on all exported symbols.

### Complexity Thresholds

| Metric | Soft Limit | Action |
|--------|-----------|--------|
| Component line count | 400 lines | Consider extraction |
| Component line count | 500+ lines | Must split into sub-components |
| Import count per file | 15 imports | Consider extracting sections |
| Import count per file | 25+ imports | Must extract sub-components or modals |

Pages act as **orchestrators**: they own state, effects, and business logic, then delegate rendering to focused sub-components in `features/{{domain}}/`.

---

## 3. State Management

> Choose and document your state management approach. Common options: React Context + hooks, Redux, Zustand, Jotai.

**Approach:** {{state_management_approach}}

### Context Providers

> List your application's context providers:

| Context | Purpose | Hook |
|---------|---------|------|
| `AuthContext` | User session, login/logout, profile | `useAuth()` |
| `NotificationContext` | Global toast queue | `useNotifications()` |
| `ThemeContext` | Dark/light/system colour scheme preference | `useTheme()` |
| {{additional contexts}} | | |

### Provider Hierarchy

```
<BrowserRouter>
  <AuthProvider>
    <ThemeProvider>
      <NotificationProvider>
        <QueryClientProvider>
          <AppRoutes />
        </QueryClientProvider>
      </NotificationProvider>
    </ThemeProvider>
  </AuthProvider>
</BrowserRouter>
```

**Rules:**
- Local `useState` for UI state (modals, form data, toggles).
- Context for cross-cutting concerns (auth, notifications, shared reference data).
- Custom hooks to encapsulate business logic.

---

## 4. Routing

> If stack includes React Router:

**Framework:** React Router DOM v{{version}}

### Structure

- All page routes lazy-loaded with `React.lazy()` + `<Suspense>`.
- Route guard via `<ProtectedRoute>`:

```tsx
<ProtectedRoute adminOnly={false} useLayout={true}>
  <PageComponent />
</ProtectedRoute>
```

**Rules:**
- Every new page must be lazy-loaded.
- Admin-only routes use `adminOnly={true}`.
- `ProtectedRoute` redirects unauthenticated users to `/`, non-admins away from admin routes.

### URL & Navigation Patterns

- **Query params** for transient state (search filters, pagination): `?page=2&q=term`.
- **Hash fragments** for scroll targets: `#entity-123`.
- **`useSearchParams()`** for reading/writing URL query params.
- Deep links should resolve to the same view regardless of entry point.

### List Page Pattern

> If your application has standardized list pages, document the shared hook/pattern here.

---

## 5. Styling & CSS

> If stack includes Tailwind CSS:

**Framework:** Tailwind CSS v{{version}} — utility-first with semantic component layer.

### Architecture

All custom styles live in `src/index.css` using Tailwind layers:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn--primary { @apply ... ; }
  .chip--status-active { @apply ... ; }
}
```

### Class Naming Convention — BEM

All custom component classes follow the **BEM (Block Element Modifier)** convention:

```css
.block                     /* standalone entity */
.block__element            /* part of a block */
.block--modifier           /* variant or state of a block */
.block__element--modifier  /* variant or state of an element */
```

**Separators:** double underscore `__` for elements, double dash `--` for modifiers.

> Document your project's BEM blocks as they emerge:

| Block | Role | Example classes |
|-------|------|----------------|
| `btn` | Button variants | `btn--primary`, `btn--secondary`, `btn--danger` |
| `chip` | Badge/pill variants | `chip--status-active`, `chip--tag` |
| `alert` | Alert variants | `alert--error`, `alert--success`, `alert--info` |
| `nav` | Navigation elements | `nav__link--active` |
| `card` | Card containers | `card--container`, `card--interactive` |
| `form` | Form elements | `form__label` |

### Design Tokens

> Centralize all style primitives in a tokens file:

```ts
// src/styles/tokens.ts
export const colors = {
  primary: "{{primary_hex}}",
  secondary: "{{secondary_hex}}",
} as const;

export const fontFamily = {
  sans: ["{{sans_font}}", "sans-serif"],
  serif: ["{{serif_font}}", "serif"],
} as const;
```

**Rules:**
- All color hex values and font definitions must originate from a tokens file.
- Token names use semantic meaning (`primary`, `secondary`) not visual descriptions.
- No CSS Modules, no styled-components, no separate `.css` files per component.
- All custom component classes go in `index.css` under `@layer components`.
- Prefer Tailwind utility classes inline; extract to `@layer components` only when a pattern repeats 3+ times.

### Dark Mode

> If your application supports dark mode, document the strategy (Tailwind `class` strategy, CSS variables, etc.) and the token structure.

---

## 6. Internationalization (i18n)

> If stack includes i18n:

**Framework:** react-i18next + i18next

### Setup

- Languages: `{{PRIMARY_LOCALE}}` (default), `{{SECONDARY_LOCALE}}`.
- Translation files: `src/i18n/locales/{{primary}}.json`, `src/i18n/locales/{{secondary}}.json`.

### Usage

```tsx
const { t, i18n } = useTranslation();

// String lookup
<h1>{t("{{section}}.title")}</h1>

// Current language
const lang = i18n.language;

// Change language
i18n.changeLanguage("{{locale}}");
```

**Rules:**
- Every user-facing string must use an i18n key. No hardcoded text.
- Translation keys use **dot notation**: `"errors.loadFailed"`, `"auth.loginPlaceholder"`.
- When creating or modifying strings, update **all** locale files.
- `escapeValue: false` when React handles escaping.
- **Security warning:** Never interpolate user-supplied values into translation keys rendered via `dangerouslySetInnerHTML` without sanitization.

---

## 7. API Layer

> If stack includes Axios or similar HTTP client:

**Framework:** Axios v{{version}} with a shared instance.

### Architecture

```
src/api/
├── axios.ts          # Shared instance, interceptors, error normalization
├── apiFactories.ts   # createCrudApi() factory
├── authApi.ts        # Auth-specific endpoints
└── {{entity}}Api.ts  # One module per entity
```

### Error Normalization

Every rejected promise carries:

| Property | Type | Description |
|----------|------|-------------|
| `error.message` | `string` | Human-readable message |
| `error.status` | `number` | HTTP status code |
| `error.details` | `object` | Raw response body |
| `error.errorType` | `string` | One of: `"network"`, `"timeout"`, `"canceled"`, `"server"`, `"unknown"` |

### CRUD Factory Pattern

```ts
export const createCrudApi = (basePath: string) => ({
  list: async (params?) => { ... },
  getById: async (id: number) => { ... },
  create: async (data: unknown) => { ... },
  update: async (id: number, data: unknown) => { ... },
  remove: async (id: number) => { ... },
});
```

### JWT Token Flow

> Document your authentication token flow:

1. Backend sets tokens as `HttpOnly; Secure; SameSite=Lax` cookies on login/refresh.
2. Browser automatically sends cookies with every request.
3. Response interceptor detects 401 and attempts token refresh.
4. On session expiry -> event -> AuthContext clears user state.

### Backend-Frontend API Contract

#### Endpoint Naming

| Pattern | HTTP Method | Purpose | Example |
|---------|-------------|---------|---------|
| `/api/{{entity}}/` | GET | List (paginated) | `GET /api/{{entities}}/` |
| `/api/{{entity}}/` | POST | Create | `POST /api/{{entities}}/` |
| `/api/{{entity}}/<id>` | GET | Get by ID | `GET /api/{{entities}}/5` |
| `/api/{{entity}}/<id>` | PUT | Update | `PUT /api/{{entities}}/5` |
| `/api/{{entity}}/<id>` | DELETE | Delete | `DELETE /api/{{entities}}/5` |

URL entities use **kebab-case**.

#### Response Envelope

| Backend Builder | HTTP Status | Frontend Shape |
|-----------------|-------------|----------------|
| `rb.success(data)` | 200 | `{ ...data }` |
| `rb.created(data)` | 201 | `{ ...data }` |
| `rb.no_content()` | 204 | empty body |
| `rb.error(msg)` | 4xx/5xx | `{ "error": "msg" }` |
| `rb.paginated(items, total, page, pages, has_next)` | 200 | `{ "items": [...], "total", "page", "pages", "has_next" }` |

#### Constants Sync

> List the constants that must stay in sync between backend and frontend:

| Constant | Backend Location | Frontend Location |
|----------|-----------------|-------------------|
| Role levels | `{{backend_constants_path}}` | `{{frontend_constants_path}}` |
| Validation limits | `{{backend_validation_path}}` | `{{frontend_constants_path}}` |

**Rules:**
- One API module per entity.
- Use `createCrudApi()` for standard CRUD; extend with custom methods as needed.
- Components consume API modules, never the HTTP client directly.

---

## 8. Data Fetching & Caching

> If stack includes TanStack Query:

**Framework:** TanStack Query v{{version}}

### Query Pattern

```tsx
const { data = [], isLoading, error } = useQuery({
  queryKey: queryKeys.{{entity}}.list({ page, search }),
  queryFn: () => {{entity}}Api.list({ page, search }),
  enabled: !!userId,
});
```

### Mutation Pattern

```tsx
const createMutation = useMutation({
  mutationFn: (data) => {{entity}}Api.create(data),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.{{entity}}.all });
  },
  onError: (err) => {
    setError(extractApiError(err, "errors.createFailed", t));
  },
});
```

### Query Key Factory

All queries **must** use keys from a centralized factory:

```tsx
queryKeys.{{entity}}.all           // ["{{entity}}"]
queryKeys.{{entity}}.list(params)  // ["{{entity}}", "list", params]
queryKeys.{{entity}}.detail(id)    // ["{{entity}}", "detail", id]
```

### QueryClient Defaults

| Setting | Value | Rationale |
|---------|-------|-----------|
| `staleTime` | {{value}} | {{rationale}} |
| `gcTime` | {{value}} | {{rationale}} |
| `retry` | 1 (queries) / 0 (mutations) | One retry for transient errors |
| `refetchOnWindowFocus` | {{value}} | {{rationale}} |

### Expected UI States

Every data-fetching component must handle:

| State | UI | Implementation |
|-------|-----|----------------|
| **Loading** | Spinner or skeleton | `if (isLoading) return <LoadingSpinner />;` |
| **Error** | Alert with retry | `if (error) return <AlertMessage variant="error">...` |
| **Empty** | Informational message | `if (data.length === 0) return <p>{t("noResults")}</p>;` |
| **Success** | Render data | Normal rendering path |

**Rules:**
- Always handle all 4 UI states.
- Use `useQuery` for fetching; `useMutation` for state-changing operations.
- Use the `queryKeys` factory — never hardcode key arrays.
- Invalidate via parent keys after mutations.

---

## 9. Form Handling

> Document your form handling approach: manual state, React Hook Form, Formik, etc.

**Approach:** {{form_approach}}

### Validation

- Client-side validation uses shared `VALIDATION` constants.
- Validation in submit handlers; server-side errors shown via alert components.

**Rules:**
- Validate against shared constants for field length/format.
- Provide keyboard shortcuts for form submission (Enter) and cancellation (Escape).

---

## 10. Rich Text Editor

> If your application includes a rich text editor, document the framework and content flow:

**Framework:** {{editor_framework}}

### Content Flow

1. User edits via rich text editor
2. Content serialized as HTML
3. HTML sanitized with DOMPurify before storage
4. Backend stores HTML; frontend renders via sanitized component

**Rules:**
- All rich text content must be sanitized with DOMPurify before rendering user-generated HTML.
- Editor toolbar components are shared primitives — do not duplicate.

---

## 11. Modal Management

### Hook Selection Guide

| Hook | Use Case | Manages |
|------|----------|---------|
| `useModalState()` | Single modal toggle | `{ isOpen, open, close }` |
| `useCrudModals()` | Create/edit/delete modal trio | `{ isOpen(name), open(name, item), close(name), selected }` |

**Rules:**
- Maximum 1 modal visible at a time (no stacking).
- Use form-specific modal variants for dialogs containing forms (prevent data loss from backdrop clicks).
- For complex pages, consolidate modals into a dedicated sub-component.

---

## 12. Performance

### Memoization Guidelines

| Technique | When to Use | When NOT to Use |
|-----------|------------|-----------------|
| `useMemo` | Expensive computations (tree building, sorting large lists) | Simple derivations, small arrays |
| `useCallback` | Callbacks passed to memoized children | Handlers used only in the same component |
| `React.memo` | Leaf components that re-render frequently with same props | Components that always receive new props |

### Lazy Loading

- All page routes lazy-loaded via `React.lazy()` + `<Suspense>`.
- Heavy components imported dynamically.

**Rules:**
- Profile before optimizing — don't prematurely memoize.
- Always clean up blob URLs with `URL.revokeObjectURL()` in effect cleanup.
- Debounce search inputs (300ms default).

---

## 13. Accessibility (WCAG 2.1 AAA Target)

### Keyboard Navigation (WCAG 2.1.3)

- All interactive elements must be reachable via Tab.
- Modals trap focus and return focus to trigger on close.
- Dropdown/selector components support ArrowUp/ArrowDown, Enter, Escape.

### ARIA Guidelines (WCAG 4.1.2)

- Modals: `role="dialog"`, `aria-modal="true"`, `aria-labelledby`.
- Alerts: `role="alert"` for error messages, `role="status"` for info/success.
- Toast notifications: `aria-live="polite"`, `role="status"`, `aria-atomic="true"`.
- Loading states: `aria-busy="true"` on containers.
- Icon-only buttons: always include `aria-label` or `title`.
- Toggle buttons: `aria-pressed="true/false"`.
- Form inputs: `aria-required`, `aria-invalid`, `aria-describedby`.

### Form Labels (WCAG 1.3.1, 3.3.2)

- Every form input must have a visible `<label>` with `htmlFor`.
- Placeholder text is supplementary — never the sole label.
- Error messages linked via `aria-describedby`.

### Color Contrast (WCAG 1.4.6 AAA Enhanced)

> Document your color contrast ratios:

- Primary color on white: {{ratio}} (target: ≥7:1 for AAA)
- All text on light backgrounds: minimum ~5.7:1

### Visual Presentation (WCAG 1.4.8)

- Body font size: relative units for zoom support.
- Minimum font size: 14px equivalent.
- Text content blocks: `max-width: 80ch`.

### Skip Navigation (WCAG 2.4.1)

- "Skip to main content" link as first child of Layout.

### Reduced Motion (WCAG 2.3.2)

- `@media (prefers-reduced-motion: reduce)` disables animations.

**Rules:**
- Every icon-only button must have an `aria-label`.
- Destructive actions use type-to-confirm dialogs.
- Error messages use `role="alert"`.
- All form inputs must have associated `<label>` elements.
- New table headers must include `scope="col"`.

---

## 14. Testing

> If stack includes Vitest:

**Stack:** Vitest + @testing-library/react + happy-dom

### File Naming

- Component tests: `ComponentName.test.tsx`
- Hook tests: `useHookName.test.ts`
- Utility tests: `utilityName.test.ts`

### Test Pattern

```tsx
vi.mock("../../api/{{entity}}Api", () => ({
  {{entity}}Api: { list: vi.fn(), create: vi.fn() },
}));
vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key, i18n: { language: "en-US" } }),
}));

describe("ComponentName", () => {
  it("should render expected content", () => {
    render(<ComponentName />);
    expect(screen.getByText("expected.i18n.key")).toBeTruthy();
  });
});
```

**Rules:**
- Mock **API modules**, not the HTTP client, in component tests.
- Use a stable `useTranslation` mock: `(key) => key`.
- Test files live alongside their source files (co-located).

---

## 15. Naming Conventions

| Category | Convention | Examples |
|----------|-----------|---------|
| Components | PascalCase `.tsx` | `LoginForm.tsx`, `SettingsPage.tsx` |
| Hooks | camelCase, `use` prefix `.ts` | `useAsyncData.ts`, `useModalState.ts` |
| Utilities | camelCase `.ts` | `errorUtils.ts`, `dateFormatter.ts` |
| Constants | UPPER_SNAKE_CASE | `SESSION_EXPIRED`, `STALE_THRESHOLD_MS` |
| API modules | camelCase + `Api` suffix `.ts` | `authApi.ts`, `{{entity}}Api.ts` |
| Pages | PascalCase + `Page` suffix `.tsx` | `SettingsPage.tsx`, `DashboardPage.tsx` |
| Contexts | PascalCase + `Context` suffix `.tsx` | `AuthContext.tsx` |
| Type definitions | PascalCase or camelCase `.ts` | `src/types/api.ts`, `src/types/entities.ts` |
| CSS classes | BEM (`block__element--modifier`) | `btn--primary`, `nav__link--active` |
| i18n keys | dot notation | `errors.loadFailed`, `auth.loginPlaceholder` |

---

## 16. Import Conventions

> If stack includes Vite:

**Path alias imports** (`@/`) for cross-boundary imports. Relative paths for co-located imports.

### Import Order

1. React + external libraries
2. Internal API modules (`@/api/`)
3. Context and hooks (`@/context/`, `@/hooks/`)
4. Utilities (`@/utils/`)
5. Components (`@/components/`, `@/features/`)
6. Co-located relative imports (`./`, `../`)
7. Assets/styles

---

## 17. Error Handling

### In Components (TanStack Query)

```tsx
const { data, error, isLoading } = useQuery({
  queryKey: queryKeys.{{entity}}.list(params),
  queryFn: () => {{entity}}Api.list(params),
});

if (error) {
  return <AlertMessage variant="error">{error.message}</AlertMessage>;
}
```

### Error Extraction

```ts
import { extractApiError } from "@/utils/errorUtils";

try {
  await api.create(data);
} catch (err) {
  setError(extractApiError(err, "errors.createFailed", t));
}
```

### Error Boundary

- Wrap each page route in an error boundary to prevent blank screens.

**Rules:**
- Always use a centralized error extraction utility.
- Provide an i18n fallback key for error messages.
- Display errors via alert components.

---

## 18. Authentication & Permissions

### AuthContext API

| Method/Property | Description |
|-----------------|-------------|
| `user` | Current user object or `null` |
| `loading` | Auth state initializing |
| `login(username, password)` | Returns `{ success, error? }` |
| `logout()` | Ends session |
| `isAdmin()` | Admin check |

### Permission Hook

```ts
const { isSystemAdmin, canWrite, canRead } = usePermissions(resourceContext);
```

### Route Protection

```tsx
<ProtectedRoute adminOnly={true}>
  <AdminOnlyPage />
</ProtectedRoute>
```

**Rules:**
- Use a centralized permission evaluator — never inline role comparisons.
- Use route guards for route-level access control.
- JWT tokens stored as HttpOnly cookies; user profile cached in localStorage for optimistic rendering.

---

## 19. Reusable Components

> Document your shared component library as it grows:

| Component | Purpose |
|-----------|---------|
| `AlertMessage` | Dismissible alerts — `error`, `success`, `info`, `warning` |
| `Modal` | Generic modal dialog wrapper |
| `DoubleConfirmationModal` | Type-to-confirm destructive action dialog |
| `Breadcrumb` | Navigation breadcrumb |
| `Toast` | Auto-dismissing notification |
| `ErrorBoundary` | Catches rendering errors per page |

**Rules:**
- Before creating a new component, check `components/common/`.
- New reusable components go in `components/common/`.
- Domain-specific components go in `features/{{domain}}/`.

---

## 20. Custom Hooks

### Cross-cutting hooks (`hooks/`)

> Document hooks shared across 2+ domains:

| Hook | Purpose |
|------|---------|
| `usePermissions` | Derive permission flags from auth + resource context |
| `useModalState` | Manage modal open/close state |
| `useCrudModals` | Manage CRUD action modals |
| `useFormKeyboardShortcuts` | Enter-to-submit, Escape-to-cancel |
| `useToast` | Local toast notification state |
| `useDebouncedSearch` | Debounced search input |
| `useListPage` | Shared list page behavior |

**Rules:**
- Cross-cutting hooks (used by 2+ unrelated domains) go in `hooks/`.
- Feature-specific hooks go in `features/{{domain}}/`.
- Each hook has JSDoc with `@param` and `@returns`.
- All feature folders use barrel exports (`index.ts`).

---

## 21. Type System

> If stack includes TypeScript:

**Approach:** TypeScript with `strict: {{true|false}}`, `allowJs: {{true|false}}`.

### Directory Structure

```text
src/types/
├── index.ts      # Barrel re-export
├── api.ts        # API error shapes, response envelopes
├── auth.ts       # Authentication types
├── entities.ts   # Domain entity types
└── hooks.ts      # Custom hook return types
```

**Rules:**
- Organize types by concern, not by feature.
- Use barrel export in `types/index.ts`.
- Use `as const` assertions for immutable objects.
- Import types via `import type { ... }`.

---

## 22. File & Attachment Handling

> If your application handles file uploads/downloads, document the utilities here.

**Rules:**
- Normalize attachment data from API responses.
- Always revoke blob URLs in cleanup.
- File type detection uses extension-based checks; MIME validation happens server-side.

---

## 23. Date & Time Formatting

> Document your date/time formatting approach (library or pure JS):

**Rules:**
- Always parse UTC strings from the API with timezone awareness.
- Use a consistent formatter as the default for user-facing timestamps.

---

## 24. URL Construction Utilities

> If the application runs under a configurable base path, document the URL utilities:

| Function | Purpose |
|----------|---------|
| `withAppBase(path)` | Prepends base path to absolute paths |
| `stripAppBase(pathname)` | Removes base path prefix |

**Rules:**
- Use `import.meta.env.*` (Vite) for environment variables.
- Always strip trailing slashes from API URLs.

---

## 25. Local Storage Service

> Document your localStorage abstraction:

**Rules:**
- Never access `localStorage` directly in components.
- All storage operations wrapped in try/catch for graceful degradation.
- Only cache non-sensitive, reconstructible data.
- **Never store tokens or secrets in localStorage.**

---

## 26. Search Patterns

> Document your search hook selection guide:

### Debounce Standard

All search hooks use a **300ms debounce** by default.

**Rules:**
- Use the appropriate search hook for each use case (list page search, type-ahead, full-text).
- Separate input state from applied/submitted search state.
