# Template: .claude/rules/backend.md

> Copy to `.claude/rules/backend.md` and customize for your project.

```yaml
---
paths:
  - "${BACKEND_DIR}/**"
---
```

# Backend Rules

- **${ARCHITECTURE_PATTERN}**: ${ARCHITECTURE_DESCRIPTION}. Never mix layers.
- **Service layer** is HTTP-agnostic: accepts plain arguments, raises error subtypes, never imports framework request/response.
- **Validation**: all JSON endpoints must validate through schemas — no raw request data access.
- **Soft delete**: queries must always filter for non-deleted records unless explicitly fetching deleted ones.
- **Idempotent migrations**: all migrations must use existence guards.
- **i18n**: error messages must use localized message helpers. Update all locale files.
- **Auth decorators**: every non-public endpoint needs authentication and authorization checks.
- **Activity logging**: state-changing operations must log to the activity log.
