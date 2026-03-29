# Template: .claude/rules/frontend.md

> Copy to `.claude/rules/frontend.md` and customize for your project.

```yaml
---
paths:
  - "${FRONTEND_DIR}/src/**"
---
```

# Frontend Rules

- **TypeScript required** for new files. Convert existing JS files when substantively modified.
- **Feature co-location**: place domain-specific code in feature directories, not scattered across top-level folders.
- **Page components** own state and effects; delegate rendering to sub-components.
- **CSS naming**: follow the project's CSS naming convention (e.g., BEM).
- **Design tokens**: use centralized style tokens instead of hardcoded colors/fonts.
- **Data fetching**: use the project's data fetching library for server state.
- **i18n**: all user-facing strings must use translation functions. Never hardcode text.
- **Security**: sanitize HTML before rendering user content. Never render raw HTML without sanitization.

## Test Conventions

- Mock API modules, not HTTP clients directly.
- Use stable translation mocks that return referentially stable objects.
- Clear all mocks in `beforeEach`.
- Mock child components as simple stubs when testing parent behavior.
