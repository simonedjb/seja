# TEMPLATE -- JOURNEY MAPS AS-IS

<!-- maintained-by: agent (post-skill) -->

> **How to use this template:** This file is automatically maintained by post-skill after plan execution. It reflects the user journeys that the current implementation actually supports. Do not edit manually.
>
> For the intended journey design, see `project/design-intent-to-be.md §15 (Designed User Journeys)` (to-be).
> For solution scenario narratives, see `project/design-intent-to-be.md §13`.
> For implementation coverage, see `project/user-research-as-is.md`.

---

## JM-TB-001: {{Journey Title}}

- **Persona:** {{PersonaName}} (from `project/ux-research-established.md`)
- **Solution Scenario:** {{SS-001}} (from `project/design-intent-to-be.md §13`)
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

> Gaps between current implementation and intended journey design (`project/design-intent-to-be.md §15 (Designed User Journeys)`).
> Updated by post-skill or manually via `/explain spec-drift`.

### Not Yet Implemented

| Journey (JM-TB-NNN) | Step(s) | Gap Description |
|---------------------|---------|----------------|
| {{JM-TB-001}} | {{step numbers}} | {{what is missing}} |

### Differs from Intent

| Journey (JM-TB-NNN) | Step(s) | To-Be | As-Is | Reason |
|---------------------|---------|-------|-------|--------|
| {{JM-TB-001}} | {{step numbers}} | {{intended}} | {{current}} | {{why it differs}} |

---

## Delta from Established

<!-- Populate this section when `project/ux-research-established.md §5` contains JM-E-NNN entries
     (i.e., the project has conducted formal journey research and documented it there).
     This delta compares the current implementation against empirical research findings --
     a qualitatively different signal from the to-be delta above (research-vs-reality, not intent-vs-reality).
     Leave this section empty or omit it when no such entries are present. -->

### Not Yet Matching Research Findings

| Journey (JM-E-NNN) | Step(s) | Research Finding | As-Is State | Gap |
|--------------------|---------|-----------------|-------------|-----|
| {{JM-E-001}} | {{step numbers}} | {{what research showed}} | {{current behavior}} | {{gap description}} |

### Differs from Research

| Journey (JM-E-NNN) | Step(s) | Research Finding | As-Is | Reason |
|--------------------|---------|-----------------|-------|--------|
| {{JM-E-001}} | {{step numbers}} | {{finding}} | {{current}} | {{why it differs}} |

---

## Changelog

### v1 -- {{YYYY-MM-DD}}

- **Added/Changed/Removed**: {{description}}
- **Source**: agent (post-skill)
- **Plan**: {{plan-id}}
