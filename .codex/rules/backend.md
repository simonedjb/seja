---
paths:
  - "backend/**"
---

# Backend Rules

- **Soft delete**: queries must always filter `deleted_at.is_(None)` — omitting this exposes deleted data.
- **Marshmallow validation**: all JSON endpoints validate through schemas — no raw `json_data.get()`.
- **Service layer** never imports Flask `request`/`response` — accepts plain arguments, raises `ServiceError` subtypes.

See `project/backend-standards.md` for full conventions.

## Perspective Alignment

This rule is governed by: **SEC** (security), **DB** (database), **ARCH** (architecture).
