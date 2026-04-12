---
paths:
  - "**/*.test.*"
  - "**/test_*.py"
  - "backend/tests/**"
---

# Test File Rules

- **vitest, not jest**: use `vi.mock()`, `vi.fn()`, `vi.clearAllMocks()`. Never use `jest.*` globals.
- **Stable i18n mock** (critical): `useTranslation` mock must return a referentially stable object — new references cause hanging tests.
- **Backend integration tests**: require PostgreSQL and `@pytest.mark.integration` marker — unit tests use in-memory SQLite.

See `project/standards.md § Testing` for full conventions.

## Perspective Alignment

This rule is governed by: **TEST** (testability), **DX** (developer experience).
