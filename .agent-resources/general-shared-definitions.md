# GENERAL - SHARED DEFINITIONS

## Semiotic Engineering concepts

The **metacommunication message** is a designer-to-user message that is conveyed by the designer (I) to the user (you) throughout the system and the user interface. For the full definition and its application to the project. Semiotic engineering posits that the message can be summarized as: "Here is my understanding of who you are, what I've learned you want or need to do, in which preferred ways, and why. This is the system that I have therefore designed for you, and this is the way you can or should use it in order to fulfill a range of purposes that fall within this vision."

**Phrasing rule (non-negotiable)**: All metacommunication messages — in templates, project files, plans, briefs, per-feature logs, and EMT answers — **must** use first-person "I" for the designer and second-person "you" for the user. Never use "the designer", "the system", "the user" (third-person), passive voice, or imperative mood. This applies to all sections of `project-metacomm-*.md` files: the global summary/vision, every EMT answer, and every per-feature intent. Example: write "I designed a postpone shortcut for you because I know you tend to over-schedule" — not "The designer provides a postpone shortcut" or "Enforce privacy with minimal friction."

**Verbatim rule**: When a user provides a metacommunication message as input — during quickstart, in a spec, in `project-metacomm-to-be.md`, or as a `--framing metacomm` brief — the agent must record it **exactly as written**, without summarization, editing, or any textual manipulation. The designer's precise wording carries intentional nuance; paraphrasing risks distorting the design intent.

---

## Generic Terminology

| Term | Definition | Used In |
|------|-----------|---------|
| **Soft delete** | Records are marked as deleted (`deleted_at` timestamp) rather than physically removed. Queries must filter for non-deleted records. | project-backend-standards.md §6 |
| **Double confirmation** | A destructive-action pattern requiring the user to type a confirmation word before the action is enabled. | project-frontend-standards.md §11 |
| **Review perspective** | A domain-based evaluation lens (SEC, PERF, DB, etc.) applied to code, plans, or decisions per `general-review-perspectives.md`. | general-review-perspectives.md |

---

## If stack includes React

| Term | Definition | Used In |
|------|-----------|---------|
| **Orchestrator page** | A page-level component that owns state, effects, and business logic, delegating rendering to sub-components in `features/<domain>/`. | project-frontend-standards.md §1, §2 |
| **Feature co-location** | The practice of placing feature-specific hooks, forms, sub-components, and utils together in `features/<domain>/` rather than scattering them across `hooks/`, `components/`, etc. | project-frontend-standards.md §1, §20 |

## If stack includes Flask/Python

| Term | Definition | Used In |
|------|-----------|---------|
| **Three-layer architecture** | The backend pattern separating API (HTTP), Services (business logic), and Models (data). Services are HTTP-agnostic. | project-backend-standards.md §4 |
| **Service layer contract** | The rule that services accept plain arguments, raise error subtypes, and never import framework request/response objects. | project-backend-standards.md §19 |
| **Response builder** | Utility functions that produce consistent JSON response envelopes (success, error, paginated). | project-backend-standards.md §8 |

## If stack includes CSS/HTML

| Term | Definition | Used In |
|------|-----------|---------|
| **BEM** | Block Element Modifier — the CSS class naming convention used for custom component classes (`block__element--modifier`). | project-frontend-standards.md §5 |

## If stack includes a frontend

| Term | Definition | Used In |
|------|-----------|---------|
| **Design tokens** | Centralized style primitives (colors, fonts) consumed by both the CSS framework config and app code. | project-frontend-standards.md §5 |
