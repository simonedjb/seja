---
recommended: true
depends_on: [all]
freshness: immutable-once-accepted
diataxis: explanation
description: "Architecture Decision Record format with status tracking, numbering convention, and index template."
---

# TEMPLATE -- ARCHITECTURE DECISION RECORDS (ADRs)

> **How to use this template:** Create a `docs/adr/` directory in your project. Use this format for every significant architectural or design decision. An ADR captures the *why* behind a decision so future developers don't undo it without understanding the trade-offs.

## File Organization

| Path | Purpose |
|------|---------|
| `docs/adr/` | All ADR files |
| `docs/adr/INDEX.md` | ADR index (auto-maintained or manual) |
| `docs/adr/adr-NNNN-<slug>.md` | Individual ADR files |

## ADR Format

```markdown
# ADR-NNNN: {{Decision Title}}

- **Status**: {{Proposed | Accepted | Deprecated | Superseded by ADR-MMMM}}
- **Date**: {{YYYY-MM-DD}}
- **Deciders**: {{who was involved in the decision}}

## Context

{{What is the issue? What forces are at play? What problem needs solving?
Include relevant constraints, requirements, and prior art.}}

## Decision

{{What is the change that we're proposing or have agreed to?
State it as an imperative: "We will use X for Y."}}

## Consequences

### Positive
- {{Benefit 1}}
- {{Benefit 2}}

### Negative
- {{Trade-off 1}}
- {{Trade-off 2}}

### Neutral
- {{Side effect that is neither positive nor negative}}
```

## ADR Index Template

```markdown
# Architecture Decision Records

| # | Title | Status | Date |
|---|-------|--------|------|
| [ADR-0001](adr-0001-<slug>.md) | {{title}} | Accepted | {{date}} |
```

## Numbering Convention

- ADRs are numbered sequentially: ADR-0001, ADR-0002, etc.
- Numbers are never reused, even if an ADR is deprecated
- Use 4-digit zero-padded numbers

## When to Write an ADR

- Choosing a framework, library, or tool
- Defining an architectural pattern (e.g., event-driven, layered)
- Making a significant trade-off (performance vs. simplicity, consistency vs. availability)
- Changing an established pattern
- Deciding NOT to do something (these are often the most valuable ADRs)

## Migration Hint

> If your project already has architectural rationale buried in documentation prose (e.g., in `architecture.md` or `README.md`), extract each distinct decision into its own ADR. Look for phrases like "we chose X because", "the reason for", "we decided to", "the trade-off is".

## Freshness Policy

ADRs are immutable once their status is Accepted. Do not edit accepted ADRs -- instead, create a new ADR that supersedes the old one. Update status to 'Superseded by ADR-NNNN'.
