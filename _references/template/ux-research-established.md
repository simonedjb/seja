# TEMPLATE -- UX RESEARCH (ESTABLISHED)

<!-- maintained-by: human (designer/researcher) -->

> **How to use this template:** Copy this file to `project/ux-research-established.md` and record UX Research (Established) that has **already been processed** into the current design. These are the personas, goals, and scenarios that informed the design decisions reflected in `project/conceptual-design-as-is.md` and `project/metacomm-as-is.md`.
>
> For fresh research not yet processed, see `project/ux-research-new.md`.
> For the metacommunication message built on this understanding, see `project/metacomm-as-is.md`.
>
> **Lifecycle:** When new research entries in `project/ux-research-new.md` are processed into a design iteration (via `/plan` or `/design`), move them here and record the design iteration that incorporated them.
>
> **Consistency checking:** The agent can verify consistency between established research, design intent, and the implemented solution via `/explain spec-drift` or `/check validate`. The agent does not maintain or modify user research files -- only humans do.

---

## 1. Personas

> Personas whose understanding has already informed the current design. A persona may have multiple goals.

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
>
> **Incorporated in:** {{design iteration -- plan ID, design session date, or version}}

---

## 2. Problem Scenarios

> Problem scenarios that have already been processed into design decisions. Each scenario is associated with one or more persona goals.

### {{PS-001}}: {{Problem Scenario Title}}

- **Persona:** {{PersonaName}}
- **Goals:** {{G-001}}, {{G-002}}
- **Setting:** {{where and when the user encounters this problem}}
- **Incorporated in:** {{design iteration}}

{{2-3 paragraphs describing the problem narrative.}}

---

## 3. Cross-Reference Map

> Links between established research and the current design artifacts. Solution representations (scenarios, user stories) are recorded in `project/metacomm-as-is.md` Section 3, not here -- they are design decisions, not research.

| Artifact ID | Artifact Title | Design Artifact | Relationship |
|-------------|---------------|----------------|-------------|
| {{PersonaName}} | {{title}} | metacomm-as-is EMT 1.1 | Informs |
| {{PS-001}} | {{title}} | metacomm-as-is EMT 1.1, 1.3 | Informs |
| JM-E-NNN | {{journey title}} | ux-research-established.md §5 | Research evidence |

> Journey map entries (JM-E-NNN) are documented in §5 below.

---

## 4. Processing Log

> Record when research was moved from `project/ux-research-new.md` to this file.

| Date | Artifacts Processed | Design Iteration | Notes |
|------|-------------------|-----------------|-------|
| {{YYYY-MM-DD HH:MM UTC}} | {{PS-001, PersonaName}} | {{plan-NNNNNN or design session}} | {{notes}} |

---

## 5. Discovered User Journeys

<!-- maintained-by: human (researcher/designer) -- agents must NOT modify this section -->

> Journey maps discovered through user research sessions (field observations, usability
> studies, contextual inquiry, diary studies, etc.). These are empirical findings --
> they describe what users *actually do*, not what was designed or what is implemented.
>
> **One-directional flow:** Research findings here inform `project/design-intent-to-be.md §15`
> (Designed User Journeys). They do NOT flow back into this file.
> This section is append-only: never edit or delete prior entries.
>
> **Related files:**
> - `project/design-intent-to-be.md §15` -- designed journeys (to-be, human-maintained)
> - `project/journey-maps-as-is.md` -- implemented journeys (as-is, agent-maintained)

<!--
  ENTRY PATTERN -- copy this block for each journey map entry from a research session
  ===================================================================================

  ### JM-E-NNN: {{Journey Title}}

  - **Research source:** {{method}} | {{YYYY-MM}} | n={{N}} (required -- e.g., "contextual inquiry | 2025-11 | n=8")
  - **Persona:** {{PersonaName}} (optional -- link to §1 Persona ID when available)
  - **Problem scenario:** {{PS-NNN}} (optional -- link to §2 Problem Scenario when available)
  - **Goal:** {{what the user is trying to achieve}}
  - **Pre-conditions:** {{what is true when the journey starts}}

  #### Steps

  | # | Observation | Touchpoint | User Emotion | Pain Point | Source |
  |---|------------|-----------|-------------|-----------|--------|
  | 1 | {{what the researcher observed the user doing}} | {{where they interact}} | {{how they appeared to feel}} | {{friction or frustration observed}} | {{specific session / artifact reference}} |
  | 2 | {{observation}} | {{touchpoint}} | {{emotion}} | {{pain point}} | {{source}} |

  > **Source column** (required in template; if unavailable, note the session date):
  > Reference the specific session, recording, or artifact where this observation was
  > made (e.g., "session-2025-11-03", "diary study P4", "usability test recording #7").

  #### Key Findings

  {{2-3 bullet points summarizing the most important insights from this journey.}}

  #### Mermaid Diagram (optional)

  ```mermaid
  journey
      title {{Journey Title}}
      section {{Phase 1}}
          {{Observed action 1}}: {{satisfaction 1-5}}: User
          {{Observed action 2}}: {{satisfaction 1-5}}: User
      section {{Phase 2}}
          {{Observed action 3}}: {{satisfaction 1-5}}: User
  ```

  > Satisfaction scores derived from observed behavior and verbal protocols:
  > 1 = frustrated, 3 = neutral, 5 = delighted.

  ===================================================================================
-->

### Processing Log

> Record when research sessions were conducted and when their journey findings were
> processed into design decisions.

| Date | Research Session | Journeys Produced | Design Impact | Notes |
|------|-----------------|------------------|--------------|-------|
| {{YYYY-MM-DD HH:MM UTC}} | {{session description}} | {{JM-E-001, JM-E-002}} | {{plan-NNNNNN or design session}} | {{notes}} |
