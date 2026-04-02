# TEMPLATE -- JOURNEY MAPS AS-IS

<!-- maintained-by: agent (post-skill) -->

> **How to use this template:** This file is automatically maintained by post-skill after plan execution. It reflects the user journeys that the current implementation actually supports. Do not edit manually.
>
> For the intended journey design, see `project/journey-maps.md` (to-be).
> For solution scenario narratives, see `project/design-intent-to-be.md` Section 13.
> For implementation coverage, see `project/user-research-as-is.md`.

---

## {{Journey Title}}

- **Persona:** {{PersonaName}} (from `project/user-research-to-be.md`)
- **Solution Scenario:** {{SS-001}} (from `project/user-research-to-be.md` Section 3)
- **Goal:** {{what the user wants to achieve}}
- **Implementation Status:** {{implemented / partial / not started}}

### Steps

| # | Action | Touchpoint | Implemented | Notes |
|---|--------|-----------|-------------|-------|
| 1 | {{what the user does}} | {{where they interact}} | {{yes / partial / no}} | {{implementation notes or gaps}} |
| 2 | {{action}} | {{touchpoint}} | {{yes / partial / no}} | {{notes}} |
| 3 | {{action}} | {{touchpoint}} | {{yes / partial / no}} | {{notes}} |

### Mermaid Diagram (optional)

> Mirror the to-be diagram structure but annotate with implementation status.

---

## Delta from To-Be

> Summary of gaps between current implementation and intended journey design (`project/journey-maps.md`). Updated automatically by post-skill or manually via `/explain spec-drift`.

### Not Yet Implemented

| Journey | Step(s) | Gap Description |
|---------|---------|----------------|
| {{journey title}} | {{step numbers}} | {{what is missing}} |

### Differs from Intent

| Journey | Step(s) | To-Be | As-Is | Reason |
|---------|---------|-------|-------|--------|
| {{journey title}} | {{step numbers}} | {{intended}} | {{current}} | {{why it differs}} |

---

## Changelog

### v1 -- {{YYYY-MM-DD}}

- **Added/Changed/Removed**: {{description}}
- **Source**: agent (post-skill)
- **Plan**: {{plan-id}}
