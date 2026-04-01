---
name: explain
description: "Explains behavior, code, data model, architecture, or spec drift with visual diagrams and analogies."
argument-hint: "<architecture|behavior|behavior-evolution|code|data-model|spec-drift> [brief]"
metadata:
  last-updated: 2026-03-28 12:40:00
  version: 1.1.0
  category: analysis
  context_budget: standard
  references:
    - project/conceptual-design-as-is.md
    - project/conceptual-design-to-be.md
    - project/metacomm-as-is.md
    - project/metacomm-to-be.md
    - general/shared-definitions.md
    - general/report-conventions.md
---

## Quick Guide

**What it does**: Get a clear explanation of how something works — a feature's behavior, the data model, the overall architecture, or the drift between your design specs. Includes diagrams and analogies to make complex topics accessible. The **spec-drift** type also offers an interactive sync workflow to realign diverged specs.

**Example**:
> You: /explain architecture How does the authentication flow work?
> Agent: Produces a visual diagram of the auth flow, explains each step in plain language, and highlights key design decisions. Uses analogies to clarify complex parts.

> You: /explain spec-drift
> Agent: "3 entities in to-be not yet in as-is. 1 permission removed. 2 UX patterns modified." Then asks whether you want to sync the specs.

**When to use**: You want to understand how a part of the system works, need to onboard yourself on unfamiliar code, want a visual overview of the architecture, or want to see and resolve the gap between as-is and to-be design specs.

**See also**: `/document` -- generate project documentation artifacts (READMEs, changelogs, API references, ADRs).

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `architecture [brief]` | -- | Explain system architecture, component relationships, and design choices |
| `behavior [brief]` | -- | Explain emergent behavior from a user's perspective |
| `behavior-evolution [brief]` | -- | Explain current behavior AND how it evolved over time |
| `code [brief]` | -- | Explain how code works, aimed at junior developers |
| `data-model [brief]` | -- | Explain data model, pitfalls, and refactoring opportunities |
| `spec-drift [scope]` | -- | Compare as-is and to-be design specs, with optional sync. Scope: `all`, `conceptual-design`, `metacomm` |

> One type is required. Types are mutually exclusive.

# Explain

If there are no arguments, ask for a user brief.

If the explanation type (architecture, behavior, behavior-evolution, code, data-model, or spec-drift) is not specified or cannot be inferred from the brief, use the AskUserQuestion tool to ask which kind of explanation they want (if AskUserQuestion is not available, present as a numbered text list), with these options:
- "1. Architecture -- system architecture, component relationships, and design choices"
- "2. Behavior -- emergent behavior and pitfalls from a user's perspective"
- "3. Behavior evolution -- current behavior AND how it evolved over time"
- "4. Code -- how code works, aimed at junior developers being onboarded"
- "5. Data model -- data model, pitfalls, and refactoring opportunities"
- "6. Spec drift -- drift between as-is and to-be design specs, then optionally sync"

## Definitions per type

### behavior
- Output folder: `${EXPLAINED_BEHAVIORS_DIR}` (see project/conventions.md)
- Filename pattern: `behavior-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)
- Reserve ID: `python .claude/skills/scripts/reserve_id.py --type behavior --title '<short title>'`
- Header pattern: `# Behavior <id> | <prefix><scope> | <current datetime> | <short title>`
- General instructions: Keep explanations conversational and centered on the user (including user roles), user goals and activities, user interface, and user-system interactions. For complex concepts, use multiple analogies.

### behavior-evolution
- Output folder: `${BEHAVIOR_EVOLUTION_DIR}` (see project/conventions.md)
- Filename pattern: `evolution-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)
- Reserve ID: `python .claude/skills/scripts/reserve_id.py --type evolution --title '<short title>'`
- Header pattern: `# Behavior Evolution <id> | <prefix><scope> | <current datetime> | <short title>`
- General instructions: Keep explanations conversational and centered on the user (including user roles), user goals and activities, user interface, and user-system interactions. The goal is to tell the **story** of how a feature or behavior area reached its current state — not just what it does today, but *why* it is the way it is, through the lens of design decisions captured in plans.

### code
- Output folder: `${EXPLAINED_CODE_DIR}` (see project/conventions.md)
- Filename pattern: `dev-onboarding-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)
- Reserve ID: `python .claude/skills/scripts/reserve_id.py --type dev-onboarding --title '<short title>'`
- Header pattern: `# Dev-Onboarding <id> | <prefix><scope> | <current datetime> | <short title>`
- General instructions: Keep explanations conversational and consider junior developers who are just learning the dev stack. For complex concepts, use multiple analogies.

### data-model
- Output folder: `${EXPLAINED_DATA_MODEL_DIR}` (see project/conventions.md)
- Filename pattern: `data-model-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)
- Reserve ID: `python .claude/skills/scripts/reserve_id.py --type data-model --title '<short title>'`
- Header pattern: `# Data Model <id> | <prefix><scope> | <current datetime> | <short title>`
- General instructions: Keep explanations conversational and centered on the user (including user roles), user goals and activities, user interface, and user-system interactions. For complex concepts, use multiple analogies.
- If no scope is provided, consider the entire database. Otherwise, consider the scope and its dependencies.

### architecture
- Output folder: `${EXPLAINED_ARCHITECTURE_DIR}` (see project/conventions.md)
- Filename pattern: `architecture-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)
- Reserve ID: `python .claude/skills/scripts/reserve_id.py --type architecture --title '<short title>'`
- Header pattern: `# Architecture <id> | <prefix><scope> | <current datetime> | <short title>`
- General instructions: Keep explanations conversational and aimed at developers being onboarded. Focus on the *why* behind each architectural decision, not just the *what*. For complex concepts, use multiple analogies. Treat the architecture as a set of trade-offs, not absolute truths.
- If no scope is provided, consider the entire system. Otherwise, consider the scoped area and its interactions with the rest of the system.

### spec-drift
- Output folder: `${ADVISORY_DIR}` (see project/conventions.md)
- Filename pattern: `advisory-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)
- Reserve ID: `python .claude/skills/scripts/reserve_id.py --type advisory --title '<short title>'`
- Header pattern: `# Advisory <id> | <prefix><scope> | <current datetime> | <short title>`
- General instructions: This type combines drift analysis and optional sync. It replaces the former `/spec` skill. The scope can be `all` (default), `conceptual-design`, or `metacomm`.

## Skill-specific Instructions

1. Run /pre-skill "explain" $ARGUMENTS to add general instructions to the context window.

2. Generate the explanation based on the selected type:

### If behavior:
- **Start with an analogy**: Compare the system behavior to something from everyday life
- **Draw a diagram**: Use ASCII art to show the flow, structure, or relationships
- **Walk through all the possible user-system interactions**: Explain step-by-step what happens
- **Highlight a gotcha**: What are common mistakes or misconceptions?
- **Highlight dangers**: What problems may ensue due to incorrect, inadequate, ill-intended, or unethical use?
- **Metacommunication message**: Create two versions of the designer's metacommunication message related to the explained behavior, using I as the designer and you as the user: a summarized version and a detailed version.

### If behavior-evolution:

#### Step A — Mine the plan history

1. Read `${OUTPUT_DIR}/INDEX.md` (the global artifact index). If it does not exist, run `python .claude/skills/scripts/generate_macro_index.py` to generate it.
2. Filter relevant plan IDs from the index — a plan is relevant if its title or prefix-scope touches the feature area under analysis. Include plans with any prefix (FEATURE, FIX, REFACTOR, REDESIGN, CHORE) — all of them can change user-facing behavior.
3. Read only the full plan files for the relevant IDs identified in step 2.
4. Sort the relevant plans chronologically by their plan date.

#### Step B — Build the evolution timeline

For each relevant plan, extract:
- **Plan ID and date**
- **What changed** — summarize in 1-2 sentences the user-facing behavior change (not code details)
- **Why it changed** — the motivation from the user brief (new capability, bug fix, UX improvement, compliance, etc.)
- **Rules/constraints introduced or removed** — any new validation rules, permission changes, workflow constraints, or behavioral guardrails that were added, modified, or dropped

#### Step C — Write the explanation

The report must contain these sections in order:

1. **Current behavior snapshot** — A complete description of the behavior as it exists today, written in the same style as the `behavior` type:
   - **Analogy**: Compare the current system behavior to something from everyday life
   - **Diagram**: ASCII art showing the current flow, structure, or relationships
   - **User-system interactions**: Walk through all possible interactions as they work today
   - **Active rules and constraints**: List all validation rules, permissions, workflow constraints, and behavioral guardrails currently in effect
   - **Gotchas**: Common mistakes or misconceptions
   - **Dangers**: Problems from incorrect, inadequate, ill-intended, or unethical use

2. **Evolution timeline** — A chronological table or timeline showing how the behavior evolved:

   ```
   | Wave | Plan(s) | Date | Change | Motivation | Rules affected |
   |------|---------|------|--------|------------|----------------|
   ```

   Group related plans into **waves** when multiple plans contributed to the same logical change (e.g., a feature plan + a follow-up fix plan). Each wave represents a user-visible behavioral shift.

3. **Before/after narratives** — For each wave (or the most significant ones if there are many), write a short "before → after" narrative:
   - *Before wave N:* How did the system behave from the user's perspective?
   - *After wave N:* What changed? What can the user now do (or no longer do)?
   - *Design rationale:* Why was this change made?

4. **Cumulative rule ledger** — A table tracking the lifecycle of every rule/constraint in the scope:

   ```
   | Rule | Introduced | Modified | Removed | Current status |
   |------|-----------|----------|---------|----------------|
   ```

5. **Metacommunication message** — Two versions (summarized and detailed) of the designer's metacommunication message, written in first person (I as designer, you as user), reflecting not just the current state but also the design intent and evolution trajectory.

### If architecture:

#### Step A — Survey the system

1. Read `AGENTS.md` (or `README.md`) for the high-level project description and stack.
2. Read `project/conventions.md` for directory structure and key variables.
3. Scan the top-level directory layout and primary source directories to identify major components (backend, frontend, shared libraries, infrastructure, etc.).
4. If a scope is provided, focus on that area and its direct dependencies. Otherwise, cover the full system.

#### Step B — Identify architectural decisions

For each major component or cross-cutting concern, identify the key design decisions by examining:
- Directory and module structure (layering, grouping strategy)
- Dependency flow (what depends on what, boundary enforcement)
- Communication patterns (sync/async, API contracts, event buses, message queues)
- Data flow (where data enters, how it transforms, where it persists)
- Infrastructure choices (deployment model, scaling strategy, caching, observability)

#### Step C — Write the explanation

The report must contain these sections in order:

1. **System overview** — A concise description of what the system does and who it serves, written for a new team member on their first day.

2. **Architecture diagram** — ASCII art showing the major components, their boundaries, and how they communicate. Use a layered or C4-style representation as appropriate. Include a legend if symbols are non-obvious.

3. **Component inventory** — For each major component:
   - **Role**: what it does in one sentence
   - **Key technologies**: frameworks, libraries, runtime
   - **Boundary**: what it owns and what it delegates

4. **Design decisions and trade-offs** — The core of the explanation. For each significant architectural choice:
   - **Decision**: what was chosen (e.g., "monorepo with shared types", "event-driven communication between services")
   - **Alternatives considered**: what other options exist (briefly)
   - **Why this choice**: the motivating constraints — team size, performance requirements, compliance, simplicity, etc.
   - **Trade-offs accepted**: what downsides were knowingly accepted
   - **When to revisit**: conditions under which this decision should be reconsidered

5. **Data flow walkthrough** — Trace 1-2 representative user actions end-to-end through the system, showing which components participate and how data moves between them.

6. **Cross-cutting concerns** — How the architecture addresses:
   - Error handling and resilience
   - Authentication and authorization
   - Observability (logging, monitoring, tracing)
   - Configuration management
   - Testing strategy at the architectural level (unit / integration / e2e boundaries)

7. **Gotchas and pitfalls** — Architectural traps a new developer is likely to fall into (e.g., "don't bypass the service layer to access the DB directly", "this cache is eventually consistent — reads may lag by up to 5s").

8. **Metacommunication message** — Two versions (summarized and detailed) of the designer's metacommunication message, written in first person (I as designer, you as developer), conveying the architectural intent and the principles that should guide future changes.

### If spec-drift:

The spec-drift type combines drift analysis (read-only comparison) with an optional sync workflow. It accepts an optional scope argument: `all` (default), `conceptual-design`, or `metacomm`.

#### Step A — Drift Analysis

1. Determine the scope from the argument (default: `all`).

2. For each pair in scope, read both the as-is and to-be files. If either file in a pair does not exist, report it and skip that pair.

3. **Conceptual Design Drift Analysis** (if in scope):

   Compare `${CONCEPTUAL_DESIGN_AS_IS}` and `${CONCEPTUAL_DESIGN_TO_BE}` section by section:

   | Category | What to compare |
   |----------|----------------|
   | Entities | Names, attributes, relationships present in to-be but not as-is (added), present in as-is but not to-be (removed), present in both but different (modified) |
   | Permissions | Role-permission mappings that differ between the two files |
   | UX Patterns | Interaction patterns, page flows, navigation structures that differ |
   | Business Rules | Validation rules, constraints, workflows that differ |

   For each difference, classify as: **Added** (in to-be, not in as-is), **Removed** (in as-is, not in to-be), or **Modified** (in both, but different).

4. **Metacomm Drift Analysis** (if in scope):

   Compare `${METACOMM_AS_IS}` and `${METACOMM_TO_BE}`:

   | Category | What to compare |
   |----------|----------------|
   | Feature Intentions | Metacommunication intentions present in to-be but not implemented in as-is |
   | Implementation Status | Features marked as "Implemented" in as-is but modified/removed in to-be |
   | Designer Intent | Changes in the designer's stated intent between as-is and to-be |

5. Compile the drift report:

   ```
   ## Drift Summary

   | Scope | Added | Removed | Modified | Total |
   |-------|-------|---------|----------|-------|
   | Entities | N | N | N | N |
   | Permissions | N | N | N | N |
   | UX Patterns | N | N | N | N |
   | Business Rules | N | N | N | N |
   | Metacomm Intentions | N | N | N | N |

   ## Detailed Changes
   (list each change with its category, type, and description)
   ```

6. Save the drift report to the output file per report conventions.

7. Present the summary to the user.

#### Step B — Sync Prompt

After presenting the drift report, use the AskUserQuestion tool to ask the user whether to sync (if AskUserQuestion is not available, present as a numbered text list), with these options:
- "1. Conceptual-design to metacomm -- align metacomm with the conceptual design"
- "2. Metacomm to conceptual-design -- align conceptual design with the metacomm"
- "3. Bidirectional -- reconcile both (with user confirmation for conflicts)"
- "4. No -- skip sync"

If the user chooses **No**, run /post-skill <id> and stop.

#### Step C — Sync Workflow

If the user chooses to sync, perform the following based on the chosen direction.

##### Provenance Tracking

Every entry created or modified by this workflow must carry:
- `source`: one of `human`, `agent (explain)`, `agent (post-skill)`, `agent (plan)`
- `last-synced`: datetime of this sync run (format: `YYYY-MM-DD HH:mm:ss UTC`)

##### Sync Directions

**Direction 1 — conceptual-design -> metacomm**:
For each entity, feature, or UX pattern in `${CONCEPTUAL_DESIGN_TO_BE}` that lacks a corresponding entry in `${METACOMM_TO_BE}`:
- Draft a metacommunication intention describing what the designer communicates to the user through this feature
- Present the draft to the user for confirmation or revision
- If the user revises the draft, record their revision **verbatim** (see `general/shared-definitions.md` § Verbatim rule)
- On confirmation, add the entry to `${METACOMM_TO_BE}` with `source: agent (explain)`

**Direction 2 — metacomm -> conceptual-design**:
For each metacommunication intention in `${METACOMM_TO_BE}` that implies entities, permissions, or UX patterns not present in `${CONCEPTUAL_DESIGN_TO_BE}`:
- Propose additions to the conceptual design (new entities, permissions, or UX patterns)
- Present the proposal to the user for confirmation or revision
- On confirmation, add the entry to `${CONCEPTUAL_DESIGN_TO_BE}` with `source: agent (explain)`

**Direction 3 — bidirectional**:
Run both directions sequentially. Present all gaps and conflicts together for human resolution.

##### Conflict Detection

When the two files disagree (e.g., `${CONCEPTUAL_DESIGN_TO_BE}` removes an entity but `${METACOMM_TO_BE}` still references it):
- Present the conflict with both sides clearly shown
- Ask the user to resolve: keep conceptual-design version, keep metacomm version, or provide a new resolution
- **Never auto-resolve conflicts** — always ask the user

##### Finalization

1. After all changes are confirmed, update the `last-synced` field on all modified entries.
2. Update the "Delta from As-Is" sections in both to-be files if the as-is files exist.
3. Run /post-skill <id>.

### If code:
- **Start with an analogy**: Compare the code to something from everyday life
- **Draw a diagram**: Use ASCII art to show the flow, structure, or relationships
- **Walk through the code**: Explain step-by-step what happens
- **Highlight a gotcha**: What's a common mistake or misconception?

### If data-model:
- **Visual representation**: Provide a visual representation (preferably in a standardized or vector-based format) of the affected entities, attributes, and relationships.
- **Walk through the data model**: Explain the data model as if onboarding a new dev.
- **Highlight a gotcha**: What are common mistakes or misconceptions?
- **Highlight dangers**: What problems may ensue due to incorrect, inadequate, ill-intended, or unethical use of the data model?
- **SQL statements**: Create the SQL statements necessary to recreate the portion of the database in the scope.

3. Save a report to the output file, including:
- *header*: per the header pattern for the selected type
- *user brief* (and scope, if any), *agent interpretation*, *files* — per _references/general/report-conventions.md
  - For data-model, split files into *creation files* (relevant to creation) and *client files* (relevant to use)
  - For behavior-evolution, split files into *current implementation files* and *plan files* (the plans that document the evolution)
  - For architecture, split files into *structural files* (entry points, configs, module boundaries) and *implementation files* (key source files that exemplify the architecture)
- *explanation*: the generated explanation, including the sections defined above

4. Run /post-skill <id>.
