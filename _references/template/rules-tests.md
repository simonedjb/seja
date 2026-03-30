# Template: .claude/rules/tests.md

> Copy to `.claude/rules/tests.md` and customize for your project.

```yaml
---
paths:
  - "**/*.test.*"
  - "${BACKEND_DIR}/tests/**"
---
```

# Test File Rules

- **Test framework**: use the project's configured test runner (vitest/jest for frontend, pytest for backend). Never mix test framework globals.
- **Stable mocks** (critical): mock return values must be referentially stable — new references per call cause hanging tests.
- **Integration tests**: require the real database and appropriate markers — unit tests use in-memory alternatives.

See `project/testing-standards.md` for full conventions.
