# GENERAL - SHARED DEFINITIONS

## Semiotic Engineering concepts

The **metacommunication message** is a designer-to-user message that is conveyed by the designer (I) to the user (you) throughout the system and the user interface. For the full definition and its application to the project. Semiotic engineering posits that the message can be summarized as: "Here is my understanding of who you are, what I've learned you want or need to do, in which preferred ways, and why. This is the system that I have therefore designed for you, and this is the way you can or should use it in order to fulfill a range of purposes that fall within this vision."

**Phrasing rule (non-negotiable)**: All metacommunication messages — in templates, project files, plans, briefs, per-feature logs, and EMT answers — **must** use first-person "I" for the designer and second-person "you" for the user. Never use "the designer", "the system", "the user" (third-person), passive voice, or imperative mood. This applies to all sections of `project/metacomm-*.md` files: the global summary/vision, every EMT answer, and every per-feature intent. Example: write "I designed a postpone shortcut for you because I know you tend to over-schedule" — not "The designer provides a postpone shortcut" or "Enforce privacy with minimal friction."

**Verbatim rule**: When a user provides a metacommunication message as input — during /design, in a spec, in `project/design-intent-to-be.md`, or as a `--framing metacomm` brief — the agent must record it **exactly as written**, without summarization, editing, or any textual manipulation. The designer's precise wording carries intentional nuance; paraphrasing risks distorting the design intent.

---

## Lifecycle Markers

> Standard inline markers for tracking the lifecycle of to-be items across all registered
> to-be files (see conventions.md To-Be / As-Is Registry). Defined here so all skills
> and agents use a consistent convention when reading or writing markers.
>
> **Agent rules**: agents may read markers and propose new IMPLEMENTED markers (via
> AskUserQuestion in post-skill). Agents must NEVER remove or alter any existing
> IMPLEMENTED or ESTABLISHED marker -- these are audit records.

### IMPLEMENTED marker (prose sections)

Applied as an inline HTML comment immediately before the section heading -- invisible in
rendered markdown, machine-parseable by agent tooling:

```markdown
<!-- STATUS: IMPLEMENTED | plan-NNNNNN | YYYY-MM-DD -->
### Section Title
```

A marker without a plan ID is valid for items implemented outside the plan workflow:
`<!-- STATUS: IMPLEMENTED | manual | YYYY-MM-DD -->`

### IMPLEMENTED marker (table rows)

For structured tables (e.g. journey map steps), add a Status column:

| # | ... | Status |
|---|-----|--------|
| 1 | ... | DONE (plan-000178, 2026-04-02) |
| 2 | ... | - |

### ESTABLISHED stamp

Applied when a human confirms promotion of an IMPLEMENTED item to its established
counterpart file (via `/explain spec-drift --promote` or manual curation):

```markdown
<!-- ESTABLISHED: plan-NNNNNN | YYYY-MM-DD | vX.Y.Z -->
```

The version field (`vX.Y.Z`) is optional -- projects without semver use date only:
`<!-- ESTABLISHED: plan-000178 | 2026-04-02 -->`.

The stamp is appended to the corresponding established file entry. In the to-be file,
the IMPLEMENTED marker is replaced with the ESTABLISHED stamp (or the entry is removed
-- designer's choice, both are valid).

---

## File Maintainer Classification

Three-value scheme applied to all reference files in `_references/` (principally the `project/` subdirectory, which varies by project). Used as the "Maintained by" column in `project/conventions.md` Key Files table, and summarized in `.claude/rules/framework-structure.md`.

| Value | Meaning | Agent rule |
|-------|---------|-----------|
| **Human** | Authored and updated exclusively by humans. | Agents must NOT write to this file. Agents may read it and propose changes via `AskUserQuestion`. |
| **Agent** | Auto-maintained by agents and skills (e.g., via post-skill). | Agents may read and write. Humans typically do not edit directly. |
| **Human / Agent** | Seeded by an agent (e.g., via /design), then human-owned; both may update. Also applies to framework source files (`general/`, `template/`) maintained by both framework authors and framework tooling. | Agents may write, following the file's own update rules. Humans are the primary curators after initial generation. |

---

## Generic Terminology

| Term | Definition | Used In |
|------|-----------|---------|
| **Soft delete** | Records are marked as deleted (`deleted_at` timestamp) rather than physically removed. Queries must filter for non-deleted records. | project/backend-standards.md §6 |
| **Double confirmation** | A destructive-action pattern requiring the user to type a confirmation word before the action is enabled. | project/frontend-standards.md §11 |
| **Review perspective** | A domain-based evaluation lens (SEC, PERF, DB, etc.) applied to code, plans, or decisions per `general/review-perspectives.md`. | general/review-perspectives.md |

---

## If stack includes React

| Term | Definition | Used In |
|------|-----------|---------|
| **Orchestrator page** | A page-level component that owns state, effects, and business logic, delegating rendering to sub-components in `features/<domain>/`. | project/frontend-standards.md §1, §2 |
| **Feature co-location** | The practice of placing feature-specific hooks, forms, sub-components, and utils together in `features/<domain>/` rather than scattering them across `hooks/`, `components/`, etc. | project/frontend-standards.md §1, §20 |

## If stack includes Flask/Python

| Term | Definition | Used In |
|------|-----------|---------|
| **Three-layer architecture** | The backend pattern separating API (HTTP), Services (business logic), and Models (data). Services are HTTP-agnostic. | project/backend-standards.md §4 |
| **Service layer contract** | The rule that services accept plain arguments, raise error subtypes, and never import framework request/response objects. | project/backend-standards.md §19 |
| **Response builder** | Utility functions that produce consistent JSON response envelopes (success, error, paginated). | project/backend-standards.md §8 |

## If stack includes CSS/HTML

| Term | Definition | Used In |
|------|-----------|---------|
| **BEM** | Block Element Modifier — the CSS class naming convention used for custom component classes (`block__element--modifier`). | project/frontend-standards.md §5 |

## If stack includes a frontend

| Term | Definition | Used In |
|------|-----------|---------|
| **Design tokens** | Centralized style primitives (colors, fonts) consumed by both the CSS framework config and app code. | project/frontend-standards.md §5 |
