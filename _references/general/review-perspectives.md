# FRAMEWORK - REVIEW PERSPECTIVES

> Domain-based review checklist ensuring structured, deterministic coverage across engineering and design concerns.
> Replaces ad-hoc "simulate a council" instructions (advisory-0005, plan-0283).
> Last revised: 2026-03-27 (P0 questions → Essential, P1-P4 → Deep-dive; expanded with expert council contributions).

---

## How to Use

When reviewing code, plans, or architectural decisions, evaluate against each applicable perspective below. For each perspective, record its tag and status in the plan or report:

- **Adopted**: the perspective was evaluated and its concerns are addressed
- **Deferred**: the perspective was evaluated but its concerns are not addressed (state why, including pros and cons)
- **N/A**: the perspective does not apply to this change

If a best practice is deferred only because it is out of scope, ask the user whether it should be included.

### Loading Perspectives

Each perspective lives in its own file under `general/review-perspectives/`. Each file contains two sections:

- **Essential** — 3-7 P0 (critical/blocking) questions that must always be evaluated. Load these for `standard` context budget or when reviewing against the default shortlist.
- **Deep-dive** — 8-12 P1-P4 questions for thorough reviews. Load these for `heavy` context budget, explicit deep-dive requests, or when the perspective is the primary focus of the review.

All questions are **priority-classified** (`[P0]` critical/blocking through `[P4]` informational) and **sorted by priority** within each tier. When time or context is constrained, focus on P0-P1 questions first.

### Two-Stage Loading

To minimize context usage, use the two-stage select-then-load protocol instead of loading all 16 perspective files:

1. **Load the index**: Read `general/review-perspectives-index.md` (compact table, under 600 tokens).
2. **Select perspectives**: Based on the change type, plan prefix, or review scope, select 4-6 relevant perspectives from the index. Use the **Perspective Shortcuts by Plan Prefix** table below for default shortlists, or select manually based on the change content.
3. **Load selected files only**: Read only the selected `review-perspectives/<tag>.md` files. Skip all others.

This protocol replaces bulk-loading all perspective files. Skills that consume perspectives (e.g., `/plan`, `/check review`) should follow this protocol unless the review depth is **Deep** and the reviewer needs all perspectives.

### Resolving Perspective Conflicts

When two perspectives recommend conflicting approaches (e.g., PERF suggests caching but SEC advises against storing sensitive data), remark the conflict and resolve it as follows:

1. **SEC wins by default** — security concerns override performance or convenience unless the user explicitly accepts the risk.
2. **A11Y is non-negotiable** — accessibility requirements are not traded off against visual design or performance.
3. **Document the trade-off** — when deferring one perspective in favor of another, record both the chosen approach and the deferred concern with its rationale in the plan.
4. **Ask when unclear** — if two non-default-priority perspectives conflict (e.g., PERF vs DX), ask the user for guidance rather than making an assumption.

---

## Engineering Perspectives

| Tag | Name | File |
|-----|------|------|
| SEC | Security | [sec.md](review-perspectives/sec.md) |
| PERF | Performance | [perf.md](review-perspectives/perf.md) |
| DB | Database | [db.md](review-perspectives/db.md) |
| API | API Design | [api.md](review-perspectives/api.md) |
| ARCH | Architecture | [arch.md](review-perspectives/arch.md) |
| DX | Developer Experience | [dx.md](review-perspectives/dx.md) |
| I18N | Internationalization | [i18n.md](review-perspectives/i18n.md) |
| TEST | Testability | [test.md](review-perspectives/test.md) |
| OPS | Operations / DevOps | [ops.md](review-perspectives/ops.md) |
| COMPAT | Compatibility | [compat.md](review-perspectives/compat.md) |
| DATA | Data Integrity & Privacy | [data.md](review-perspectives/data.md) |

## Design Perspectives

| Tag | Name | File |
|-----|------|------|
| UX | User Experience | [ux.md](review-perspectives/ux.md) |
| A11Y | Accessibility | [a11y.md](review-perspectives/a11y.md) |
| VIS | Visual Design | [vis.md](review-perspectives/vis.md) |
| RESP | Responsive Design | [resp.md](review-perspectives/resp.md) |
| MICRO | Microinteractions | [micro.md](review-perspectives/micro.md) |

---

## Perspective Shortcuts by Plan Prefix

When reviewing a plan, use these default shortlists based on the plan's prefix and scope. Add up to 2 additional perspectives if the plan content warrants it.

| Prefix-Scope | Default Perspectives |
|--------------|---------------------|
| `FIX-B` / `REFACTOR-B` | SEC, DB, ARCH, TEST, PERF, DX |
| `FIX-F` / `REFACTOR-F` | UX, A11Y, VIS, TEST, I18N, RESP |
| `FIX-X` / `REFACTOR-X` | SEC, DB, API, ARCH, UX, A11Y, I18N, TEST |
| `FEATURE-B` | SEC, DB, API, ARCH, TEST, PERF |
| `FEATURE-F` | UX, A11Y, VIS, RESP, I18N, TEST, MICRO |
| `FEATURE-X` | SEC, DB, API, ARCH, UX, A11Y, I18N, TEST |
| `REDESIGN-B` | ARCH, DB, SEC, TEST, PERF, DX |
| `REDESIGN-F` | UX, A11Y, VIS, RESP, MICRO, I18N, TEST |
| `REDESIGN-X` | ARCH, UX, A11Y, SEC, DB, API, I18N, TEST |
| `TEST-B` | TEST, DB, ARCH, DX |
| `TEST-F` | TEST, UX, A11Y, DX |
| `TEST-X` | TEST, DB, ARCH, UX, A11Y, DX |
| `DOCUMENT-B` / `DOCUMENT-F` / `DOCUMENT-X` | DX, COMPAT, ARCH |
| `CHORE-O` / `DOCUMENT-O` | DX, OPS, COMPAT |
| `CHORE-B` / `CHORE-F` / `CHORE-X` | DX, OPS, COMPAT, TEST |
