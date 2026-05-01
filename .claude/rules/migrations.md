---
paths:
  - "backend/migrations/**"
designer_description: "When you are about to write or edit a database migration, I surface the P0 review questions for database change and security alongside your project's migration conventions, so reversibility, data loss risk, lock behaviour, and permission implications get weighed before the migration lands rather than after it has already run in staging."
---

# Migration Rules

When editing files under these paths:

- **Review questions**: see `.claude/references/general/review-perspectives/db.md`, `.claude/references/general/review-perspectives/sec.md` -- P0 questions are the critical checks.
- **Full conventions**: see `project/standards.md § Backend > 6` -- stack-specific rules.

## Perspective Alignment

This rule is governed by: **DB** (database), **SEC** (security).
