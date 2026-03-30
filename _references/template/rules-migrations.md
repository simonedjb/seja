# Template: .claude/rules/migrations.md

> Copy to `.claude/rules/migrations.md` and customize for your project.

```yaml
---
paths:
  - "${MIGRATIONS_DIR}/**"
---
```

# Migration Rules

- **Idempotency required**: all operations must use guards (`IF NOT EXISTS`, `IF EXISTS`, existence checks via inspector).
- **Database syntax**: use the production database's SQL dialect — avoid SQLite or other database-specific syntax.
- **Chain integrity**: `down_revision` must reference an existing revision. Run the migration chain validation script after creating migrations.

See `project/backend-standards.md` for full conventions.
