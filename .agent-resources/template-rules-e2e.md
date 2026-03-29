# Template: .claude/rules/e2e.md

> Copy to `.claude/rules/e2e.md` and customize for your project.

```yaml
---
paths:
  - "e2e/**"
---
```

# E2E Test Rules

- **Hover before click**: always `hover()` before `click()` for visible cursor movement during recordings.
- **Pre-authenticated fixtures**: use pre-authenticated page fixtures — never log in during each test.
- **Selectors**: prefer `data-testid` attributes over CSS class selectors for stability.
- **Sequential execution**: tests share database state — order matters. Use `workers: 1`.

See `project-testing-standards.md` for full conventions.
