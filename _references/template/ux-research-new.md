# TEMPLATE -- UX RESEARCH (NEW / UNPROCESSED)

<!-- maintained-by: human (designer/researcher) -->

> **How to use this template:** Copy this file to `project/ux-research-new.md` and record fresh UX research insights that have **not yet** been processed into the current design. When these insights are incorporated into a design iteration (via `/plan` or `/design`), move the processed entries to `project/ux-research-established.md`.
>
> For research that has already informed the current design, see `project/ux-research-established.md`.
> For the metacommunication message built on user understanding, see `project/design-intent-to-be.md`.
> For visual journey maps, see `project/design-intent-to-be.md §15 (Designed User Journeys)`.
>
> **Consistency checking:** The agent can verify consistency between user research, design intent (`project/design-intent-to-be.md`), and the implemented solution via `/explain spec-drift` or `/check validate`. The agent does not maintain or modify user research files -- only humans do.

---

## 1. Personas

> Define the people who use (or will use) your system. A persona may have multiple goals. Keep personas minimal -- elaborate only as understanding grows. Sections can be marked "N/A -- single-persona product" for simple projects.

### Persona Inventory

| Name | Role / Archetype | Goals |
|------|-----------------|-------|
| {{PersonaName}} | {{role}} | {{goal 1, goal 2, ...}} |

### {{PersonaName}}

> **Role / Archetype:** {{role}}
>
> **Bio:** {{1-2 sentences of relevant context -- who they are, what they do, how they relate to the problem domain}}
>
> **Goals:**
> - {{G-001}}: {{goal description}}
> - {{G-002}}: {{goal description}}
>
> **Key Frustrations:**
> - {{frustration related to G-001}}
> - {{frustration related to G-002}}
>
> **Relevant Context:**
> - Technical proficiency: {{novice / intermediate / expert}}
> - Usage frequency: {{daily / weekly / occasional}}
> - Domain knowledge: {{description of their domain expertise}}

---

## 2. Problem Scenarios

> Describe the user's pain *without* the system (or with the current system's limitations). Problem scenarios ground design decisions in real user pain. Each scenario uses a narrative structure: setting, actor, and current pain. A scenario is associated with one or more persona goals.

### {{PS-001}}: {{Problem Scenario Title}}

- **Persona:** {{PersonaName}}
- **Goals:** {{G-001}}, {{G-002}}
- **Setting:** {{where and when the user encounters this problem}}

{{2-3 paragraphs describing the problem narrative. What is the user trying to do? What goes wrong? What is frustrating, slow, or impossible? Write concretely -- use the persona's context to make the scenario vivid and specific.}}

> Are there misuse contexts for this scenario? If so, note them for security review in `project/security-checklists.md`.

---

## 3. Cross-Reference Map

> Explicit links between user research artifacts and the design-intent files. Personas and problem scenarios feed the EMT's analysis section in `project/design-intent-to-be.md`. Solution representations (scenarios, user stories) are recorded in `project/design-intent-to-be.md` Section 13, not here -- they are design decisions, not research.

| Artifact ID | Artifact Title | Design Artifact | Relationship |
|-------------|---------------|----------------|-------------|
| {{PersonaName}} | {{title}} | design-intent-to-be EMT 1.1 (What I know about you) | Feeds |
| {{PS-001}} | {{title}} | design-intent-to-be EMT 1.1, 1.3 (Contexts of use) | Feeds |
| JM-E-NNN | {{journey title}} | ux-research-established.md §5 (after processing) | Research evidence |

> Journey map entries from research sessions are documented in §5 below.

---

## 4. Processing Status

> Track which new research entries have been processed into the design. When an entry is fully processed, move it to `project/ux-research-established.md`.

| Artifact | ID | Status | Design Iteration | Notes |
|----------|-----|--------|-----------------|-------|
| {{persona / problem scenario}} | {{ID}} | {{new / in progress / processed}} | {{plan ID or design session}} | {{notes}} |
| Discovered journey | JM-E-NNN | {{new / in progress / processed}} | {{plan ID or design session}} | {{notes}} |

---

## 5. Discovered User Journeys (Unprocessed)

<!-- maintained-by: human (researcher/designer) -- agents must NOT modify this file -->

> Fresh journey maps from recent research sessions that have not yet been processed into
> design intent. When findings are incorporated into a design iteration, move the JM-E-NNN
> entries to `project/ux-research-established.md §5 (Discovered User Journeys)`.
>
> Use the same JM-E-NNN entry pattern as `project/ux-research-established.md §5`.
> Each entry requires a research source (method | YYYY-MM | n=N).
>
> **Related files:**
> - `project/ux-research-established.md §5` -- processed discovered journeys
> - `project/design-intent-to-be.md §15` -- designed journeys informed by this research

<!--
  ENTRY PATTERN -- same as ux-research-established.md §5
  Use JM-E-NNN IDs. Required: Research source (method | YYYY-MM | n=N).
  When processed, move entry to ux-research-established.md §5.
-->
