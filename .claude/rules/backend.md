---
paths:
  - "backend/**"
designer_description: "When you touch anything under backend/, I surface the P0 review questions for security, database, and architecture alongside your project's backend standards, so the most expensive classes of mistake -- auth holes, schema drift, layering violations -- get a second look before you move on."
---

# Backend Rules

When editing files under these paths:

- **Review questions**: see `.claude/references/general/review-perspectives/sec.md`, `.claude/references/general/review-perspectives/db.md`, `.claude/references/general/review-perspectives/arch.md` -- P0 questions are the critical checks.
- **Full conventions**: see `project/standards.md § Backend` -- stack-specific rules.

## Perspective Alignment

This rule is governed by: **SEC** (security), **DB** (database), **ARCH** (architecture).
