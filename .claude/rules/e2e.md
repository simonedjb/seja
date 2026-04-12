---
paths:
  - "e2e/**"
---

# E2E Test Rules

- **Hover before click**: always `hover()` before `click()` for visible cursor movement during recordings.
- **Pre-authenticated fixtures**: use `adminPage`, `memberPage`, `adminToken` — never log in during each test.
- **Selectors**: prefer `data-testid` attributes over CSS class selectors for stability.

See `project/standards.md § Testing > 3` for full conventions.

## Perspective Alignment

This rule is governed by: **TEST** (testability), **UX** (user experience), **A11Y** (accessibility).
