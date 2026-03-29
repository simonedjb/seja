---
paths:
  - "backend/migrations/**"
---

# Migration Rules

- **Idempotency required**: all operations must use guards (`IF NOT EXISTS`, `IF EXISTS`, `inspector.has_table()`, `inspector.has_column()`).
- **PostgreSQL syntax**: use PostgreSQL-compatible SQL — avoid SQLite or MySQL-isms.
- **Chain integrity**: `down_revision` must reference an existing revision. Run `check_migration_chain.py` after creating migrations.

See `project-backend-standards.md` §6 for full conventions.

## Perspective Alignment

This rule is governed by: **DB** (database), **SEC** (security).
