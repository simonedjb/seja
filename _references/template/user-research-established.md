# TEMPLATE -- USER RESEARCH (ESTABLISHED)

<!-- maintained-by: human (designer/researcher) -->

> **How to use this template:** Copy this file to `project/user-research-established.md` and record user research that has **already been processed** into the current design. These are the personas, goals, and scenarios that informed the design decisions reflected in `project/conceptual-design-as-is.md` and `project/metacomm-as-is.md`.
>
> For fresh research not yet processed, see `project/user-research-new.md`.
> For the metacommunication message built on this understanding, see `project/metacomm-as-is.md`.
>
> **Lifecycle:** When new research entries in `project/user-research-new.md` are processed into a design iteration (via `/plan` or `/design`), move them here and record the design iteration that incorporated them.
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

---

## 4. Processing Log

> Record when research was moved from `project/user-research-new.md` to this file.

| Date | Artifacts Processed | Design Iteration | Notes |
|------|-------------------|-----------------|-------|
| {{YYYY-MM-DD}} | {{PS-001, PersonaName}} | {{plan-NNNNNN or design session}} | {{notes}} |
