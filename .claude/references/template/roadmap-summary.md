---
designer_description: "When /plan --roadmap produces the roadmap summary file, I'm the canonical shape for the header, ## Source list, ## Checkpoint Schedule section (records which wave transitions get a review, or 'None'), ## Wave Summary tables (one per wave, with Plan and Status columns), and ## Execution Instructions block (including Checkpoint Review blocks between waves per the schedule, and the anti-pattern note that Plan column entries start as plan-TBD and are filled in only after /plan reserves the real ID)."
---

# Template: Roadmap Summary File

Canonical shape referenced by: `.claude/skills/plan/SKILL.md` Roadmap Workflow (Mode 1 step 8; Mode 2 step 7).

## File shape

```markdown
# Roadmap <id> | <datetime> | <title>

## Source
- product-design/product-design-as-coded.md (read)
- product-design/product-design-as-intended.md (read)
- product-design/conventions.md (read)
- ... (list all files read)

## Checkpoint Schedule
- After Wave 0 → before Wave 1
- After Wave 2 → before Wave 3

## Wave Summary

### Wave 0 -- Foundation (sequential)
| # | ID | Title | Scope | Type | Plan | Status |
|---|-----|-------|-------|------|------|--------|
| 1 | user-model | User entity + migration | backend | technical | plan-TBD | pending |
| 2 | group-model | Group entity + migration | backend | technical | plan-TBD | pending |

### Wave 1 -- Services/API (parallel)
| # | ID | Title | Scope | Type | Plan | Depends on | Status |
|---|-----|-------|-------|------|------|-----------|--------|
| 3 | user-api | User CRUD API | backend | technical | plan-TBD | user-model | pending |
| 4 | group-api | Group CRUD API | backend | technical | plan-TBD | group-model | pending |

### Wave 2 -- Frontend (parallel)
| # | ID | Title | Scope | Type | Plan | Depends on | Status |
|---|-----|-------|-------|------|------|-----------|--------|
| 5 | home-page | Home page UX flow | frontend | design | plan-TBD | user-api | pending |

> The `Plan` column starts as `plan-TBD` for every row. Fill in the real ID (e.g., `plan-000042`) **only after** `/plan` has been invoked for that work item and has returned the ID it reserved. Do not pre-reserve IDs up front -- see the anti-pattern note in Mode 1 step 8.

## Execution Instructions

### Wave 0 (sequential)
Execute these plans one at a time, in order:
1. /implement XXXX (user-model)
2. /implement XXXX (group-model)

#### Checkpoint Review — before Wave 1

Before starting Wave 1:
1. Read the Verify sections of completed Wave 0 plans to confirm what was built.
2. Compare with Wave 1 planned work — check for API contract changes, new entity shapes, revised file structures, or scope shifts that affect Wave 1 plans.
3. If any Wave 1 plan needs revision: run `/plan <revised-brief>` for the affected item, then update this roadmap's Wave 1 Plan column with the new plan ID.
4. Proceed to Wave 1 only when all needed revisions are committed.

### Wave 1 (parallel -- 2 plans)
All depend on Wave 0. Execute in parallel via:
- Multiple Claude Code sessions, or
- Worktree-isolated agents from a single session

### Wave 2 (parallel -- 1 plan)
Depends on Wave 1. Execute after Wave 1 completes.
```

> Checkpoint Review blocks appear between waves per the `## Checkpoint Schedule` above.
> When `## Checkpoint Schedule` lists `- None`, the Execution Instructions contain no checkpoint blocks.
