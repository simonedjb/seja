---
name: explain
description: "Explains behavior, code, data model, architecture, or spec drift with visual diagrams and analogies."
argument-hint: "<architecture|behavior|behavior-evolution|code|data-model|spec-drift> [brief]"
compatibility: "Designed for Claude Code with SEJA framework"
metadata:
  last-updated: 2026-03-28 12:40 UTC
  version: 1.1.0
  category: analysis
  context_budget: standard
  references:
    - project/product-design-as-coded.md
    - project/product-design-as-intended.md
    - general/shared-definitions.md
    - general/report-conventions.md
---

## Quick Guide

**What it does**: Get a clear explanation of how something works — a feature's behavior, the data model, the overall architecture, or the drift between your design specs. Includes diagrams and analogies to make complex topics accessible. The **spec-drift** type also offers an interactive sync workflow to realign diverged specs.

**Example**:
> You: /explain architecture How does the authentication flow work?
> Agent: Produces a visual diagram of the auth flow, explains each step in plain language, and highlights key design decisions. Uses analogies to clarify complex parts.

> You: /explain spec-drift
> Agent: "3 entities in as-intended not yet in as-coded. 1 permission removed. 2 UX patterns modified." Then asks whether you want to sync the specs.

**When to use**: You want to understand how a part of the system works, need to onboard yourself on unfamiliar code, want a visual overview of the architecture, or want to see and resolve the gap between as-coded and as-intended design specs.

**See also**: `/document` -- generate project documentation artifacts (READMEs, changelogs, API references, ADRs).

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `architecture [brief]` | -- | Explain system architecture, component relationships, and design choices |
| `behavior [brief]` | -- | Explain emergent behavior from a user's perspective |
| `behavior-evolution [brief]` | -- | Explain current behavior AND how it evolved over time |
| `code [brief]` | -- | Explain how code works, aimed at junior developers |
| `data-model [brief]` | -- | Explain data model, pitfalls, and refactoring opportunities |
| `spec-drift [scope]` | -- | Compare as-coded and as-intended design specs, with optional sync. Scope: `all`, `conceptual-design`, `metacomm`, `--promote` |

> One type is required. Types are mutually exclusive.

# Explain

If there are no arguments, ask for a user brief.

If the explanation type (architecture, behavior, behavior-evolution, code, data-model, or spec-drift) is not specified or cannot be inferred from the brief, use the AskUserQuestion tool to ask which kind of explanation they want (if AskUserQuestion is not available, present as a numbered text list), with these options:
- "1. Architecture -- system architecture, component relationships, and design choices"
- "2. Behavior -- emergent behavior and pitfalls from a user's perspective"
- "3. Behavior evolution -- current behavior AND how it evolved over time"
- "4. Code -- how code works, aimed at junior developers being onboarded"
- "5. Data model -- data model, pitfalls, and refactoring opportunities"
- "6. Spec drift -- drift between as-coded and as-intended design specs, then optionally sync"

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
- General instructions: This type combines drift analysis and optional sync. It replaces the former `/spec` skill. The scope can be `all` (default), `conceptual-design`, `metacomm`, `--promote` (Phase 3a -- generate a draft Decision proposal for items marked `STATUS: implemented`), or `--promote --apply-markers plan-NNNNNN` (Phase 3b -- flip the STATUS markers after the designer has applied the prose). See Step C below for the two-phase promote workflow.

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

1. Read `CLAUDE.md` (or `README.md`) for the high-level project description and stack.
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

The spec-drift type combines drift analysis (read-only comparison) with an optional sync workflow. It accepts an optional scope argument: `all` (default), `conceptual-design`, `metacomm`, or `--promote` (promotion-only mode -- skip drift analysis and go directly to Step C).

#### Step A — Drift Analysis

If `--promote` is the scope argument, skip Steps A and B entirely and go directly to Step C (Promote Workflow).

1. Determine the scope from the argument (default: `all`).

2. Read the as-intended/as-coded registry from `project/conventions.md` (or `template/conventions.md` if the project file is absent). The registry lists all registered as-intended files and their as-coded counterparts (see "As-Intended / As-Coded Registry" section). The registry includes a Section column indicating which section of the file holds the relevant entries -- use the Section column to narrow scans to the correct heading rather than searching the entire file. For each row, determine whether it falls within the requested scope. If the as-coded counterpart is `-` (research-only row) or either file in a paired row does not exist, report it and skip that row.

   Key registry entries for journey-related IDs:
   - JM-TB-NNN entries live in `project/product-design-as-intended.md §15 (Designed User Journeys)`.
   - JM-E-NNN entries live in `project/ux-research-results.md §5 (Discovered User Journeys)`.

   Also, for each existing as-intended file in scope, scan for `STATUS: implemented` markers (legacy uppercase `STATUS: IMPLEMENTED` is also detected) that do NOT yet carry a corresponding `ESTABLISHED:` stamp. Collect these as "pending promotion" items.

3. **Conceptual Design Drift Analysis** (if in scope):

   Compare `${AS_CODED} § Conceptual Design` (the `## Conceptual Design` H2 section of `project/product-design-as-coded.md`) and Part I (Conceptual Design) of `${DESIGN_INTENT}` section by section:

   | Category | What to compare |
   |----------|----------------|
   | Entities | Names, attributes, relationships present in as-intended but not as-coded (added), present in as-coded but not as-intended (removed), present in both but different (modified) |
   | Permissions | Role-permission mappings that differ between the two files |
   | UX Patterns | Interaction patterns, page flows, navigation structures that differ |
   | Business Rules | Validation rules, constraints, workflows that differ |

   For each difference, classify as: **Added** (in as-intended, not in as-coded), **Removed** (in as-coded, not in as-intended), or **Modified** (in both, but different).

4. **Metacomm Drift Analysis** (if in scope):

   Compare `${AS_CODED} § Metacommunication` (the `## Metacommunication` H2 section of `project/product-design-as-coded.md`) and Part II (Metacommunication) of `${DESIGN_INTENT}`:

   | Category | What to compare |
   |----------|----------------|
   | Feature Intentions | Metacommunication intentions present in as-intended but not implemented in as-coded |
   | Implementation Status | Features marked as "Implemented" in as-coded but modified/removed in as-intended |
   | Designer Intent | Changes in the designer's stated intent between as-coded and as-intended |

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

   ## Pending Promotions

   Items marked `STATUS: implemented` (or legacy `IMPLEMENTED`) in registered Human (markers)
   files but not yet promoted to `established`. These are candidates for
   `/explain spec-drift --promote` (Phase 3a generates a draft Decision entry proposal;
   Phase 3b flips the STATUS markers after you apply the prose).

   | File | Section / Row | Marker | Plan |
   |------|--------------|--------|------|
   | (none) OR list of found items |
   ```

6. Save the drift report to the output file per report conventions.

7. Present the summary to the user.

#### Step B — Sync Prompt

After presenting the drift report, use the AskUserQuestion tool to ask the user what to do next (if AskUserQuestion is not available, present as a numbered text list), with these options:
- "1. Conceptual-design to metacomm -- align metacomm with the conceptual design"
- "2. Metacomm to conceptual-design -- align conceptual design with the metacomm"
- "3. Bidirectional -- reconcile both (with user confirmation for conflicts)"
- "4. Promote implemented items -- draft ADR-shaped Decision entries for items marked `STATUS: implemented` (Phase 3a of the two-phase promote workflow)"
- "5. No -- skip sync"

If the user chooses **No**, run /post-skill <id> and stop.
If the user chooses **Promote implemented items**, go to Step C (Phase 3a).

#### Step C — Promote Workflow (two-phase, SEJA 2.8.3+)

The promote workflow splits into two phases per advisory-000264 Q4 middle-path design:

- **Phase 3a — Proposal generation** (invocation: `/explain spec-drift --promote`): agent drafts ADR-shaped prose entries for items that have `STATUS: implemented` and writes them to `_output/promote-proposals/promote-proposal-plan-<id>.md`. Agent does NOT modify `product-design-as-intended.md`. Agent creates two paired pending actions: `apply-promote-proposal` (reminds the designer to copy the prose) and `apply-promote-markers` (reminds the designer to flip the STATUS markers after the prose is applied).
- **Phase 3b — Marker flip** (invocation: `/explain spec-drift --promote --apply-markers plan-NNNNNN`, space-separated, 6-digit plan ID): agent verifies that the designer has added the corresponding `### D-NNN:` entries to `product-design-as-intended.md § Decisions` (via a heading-only grep), then runs per-item AskUserQuestion confirmation, then invokes `apply_marker.py` on confirmed items. Post-skill's `check_human_markers_only.py` and `check_changelog_append_only.py` verify the marker flips do not bleed prose.

##### Phase 3a steps (`/explain spec-drift --promote`)

1. Read the as-intended/as-coded registry from `project/conventions.md` (or `template/conventions.md` if absent). Scan the registered `product-design-as-intended.md` (and any other registered Human (markers) files) for `STATUS: implemented` markers that do NOT yet carry an `ESTABLISHED:` stamp.

2. Group candidates by plan ID (from the STATUS marker's plan field). If no candidates are found, inform the user ("No implemented items pending promotion.") and run /post-skill <id>.

3. For each candidate, draft an ADR-shaped entry in the **Nygard shape** (Context / Decision / Consequences / optional Supersedes). Pull the Context from the plan's Agent Interpretation section, the Decision from the plan's chosen approach, and Consequences from the plan's Trade-offs section if present, plus any REQ markers the plan touched.

4. Assign stable `D-NNN` IDs by scanning existing Decision entries in `product-design-as-intended.md § Decisions` and using the next available number. REQ IDs and D-NNN IDs are orthogonal namespaces.

5. Write the proposal to `_output/promote-proposals/promote-proposal-plan-<id>.md` with a header linking back to the source plan and the draft Decision entries each wrapped in a copy-paste-friendly fenced block. The proposal is a designer-owned draft -- the designer may rewrite the prose freely before copying it.

6. **Dedup before adding pending actions** (A3): before invoking `pending.py add`, grep the pending ledger for existing `apply-promote-proposal` / `apply-promote-markers` entries with `source: plan-<id>`.
   - If found with status `pending`, do NOT add duplicates; instead tell the designer: "Proposal already queued. See `_output/promote-proposals/promote-proposal-plan-<id>.md`, or run Phase 3b to continue where you left off."
   - If found only with status `done`, proceed with a fresh pair (re-promotion cycle is a valid workflow).
   - Otherwise, invoke `python .claude/skills/scripts/pending.py add --type apply-promote-proposal --source plan-<id> --description "Copy draft Decision entries from _output/promote-proposals/promote-proposal-plan-<id>.md into product-design-as-intended.md § Decisions"` and `python .claude/skills/scripts/pending.py add --type apply-promote-markers --source plan-<id> --description "Flip STATUS markers via /explain spec-drift --promote --apply-markers plan-<id> after prose is applied"`.

7. Tell the designer: "Phase 3a complete. Drafted N Decision entries in `_output/promote-proposals/promote-proposal-plan-<id>.md`. Review, edit to your voice, copy into `product-design-as-intended.md § Decisions`, save, then run `/explain spec-drift --promote --apply-markers plan-<id>` to flip the STATUS markers."

8. Run /post-skill <id>.

##### Phase 3b steps (`/explain spec-drift --promote --apply-markers plan-NNNNNN`)

1. Read the pending ledger to find the matching `apply-promote-markers` action for this plan ID. If not found, warn and continue anyway (the designer may be running Phase 3b without a prior Phase 3a).

2. Read the proposal report at `_output/promote-proposals/promote-proposal-plan-<id>.md`. Extract the list of drafted `D-NNN` IDs.

3. **Tolerant missing-entries with heading-only grep** (A3, A4): read `_references/project/product-design-as-intended.md`. For each D-NNN ID extracted from the proposal, run a heading-only grep: `^###\s+D-NNN(?::|\s*$)`. **Do NOT match on Decision title text, Context prose, or body content** -- the designer may have rewritten the prose to their own voice (advisory-000264 Q4 middle-path), and matching prose would defeat designer-voice-preservation. Separate results into `present` and `missing` sets.
   - If `present` is empty, abort: "No D-NNN entries from the proposal found in `product-design-as-intended.md`. Copy the draft entries from `_output/promote-proposals/promote-proposal-plan-<id>.md` first, then re-run `/explain spec-drift --promote --apply-markers plan-<id>`."
   - If `present` is non-empty, proceed with the present set; at the end of the phase, report the `missing` set to the designer so they know what is still pending.

4. For each D-NNN that exists in both the proposal and the file, run AskUserQuestion: "Flip STATUS from implemented to established for D-NNN?" with per-item confirmation.

5. For confirmed items, invoke `python .claude/skills/scripts/apply_marker.py --file _references/project/product-design-as-intended.md --id D-<NNN> --marker STATUS --value established --plan plan-<id> --date <today>`. Legacy uppercase markers (`STATUS: IMPLEMENTED`) are detected by the widened regex and REPLACED (not stacked) by the lowercase form.

6. **Precise lifecycle updates to the pending ledger** (A3):
   - If ALL originally-proposed D-NNN entries are in the `present` set AND the designer confirmed-and-flipped every present item, invoke `pending.py done <id>` for BOTH `apply-promote-proposal` and `apply-promote-markers`.
   - If the `present` set is a proper subset of the proposed set (partial copy), leave `apply-promote-proposal` PENDING and emit: "N of M D-NNN entries applied so far; leaving apply-promote-proposal pending. Copy the remaining entries and re-run Phase 3b to finish."
   - If all entries are present but the designer declined some marker flips via AskUserQuestion, leave `apply-promote-markers` PENDING with a message listing the declined items.
   - Mark `apply-promote-markers` done ONLY when every present item was flipped successfully.

7. Run /post-skill <id>.

The Phase 3a+Phase 3b cadence is the middle-path mechanism from advisory-000264 Q4: the designer owns every word in Decision entries, but the framework manages the STATUS lifecycle structurally.

#### Step D — Sync Workflow

If the user chooses to sync (from Step B), perform the following based on the chosen direction.

##### Provenance Tracking

Every entry created or modified by this workflow must carry:
- `source`: one of `human`, `agent (explain)`, `agent (post-skill)`, `agent (plan)`
- `last-synced`: datetime of this sync run (format: `YYYY-MM-DD HH:MM UTC`)

##### Sync Directions

**Direction 1 — conceptual-design -> metacomm**:
For each entity, feature, or UX pattern in `${DESIGN_INTENT}` that lacks a corresponding entry in `${DESIGN_INTENT}`:
- Draft a metacommunication intention describing what the designer communicates to the user through this feature
- Present the draft to the user for confirmation or revision
- If the user revises the draft, record their revision **verbatim** (see `general/shared-definitions.md` § Verbatim rule)
- On confirmation, add the entry to `${DESIGN_INTENT}` with `source: agent (explain)`

**Direction 2 — metacomm -> conceptual-design**:
For each metacommunication intention in `${DESIGN_INTENT}` that implies entities, permissions, or UX patterns not present in `${DESIGN_INTENT}`:
- Propose additions to the conceptual design (new entities, permissions, or UX patterns)
- Present the proposal to the user for confirmation or revision
- On confirmation, add the entry to `${DESIGN_INTENT}` with `source: agent (explain)`

**Direction 3 — bidirectional**:
Run both directions sequentially. Present all gaps and conflicts together for human resolution.

##### Conflict Detection

When the two files disagree (e.g., `${DESIGN_INTENT}` removes an entity but `${DESIGN_INTENT}` still references it):
- Present the conflict with both sides clearly shown
- Ask the user to resolve: keep conceptual-design version, keep metacomm version, or provide a new resolution
- **Never auto-resolve conflicts** — always ask the user

##### Finalization

1. After all changes are confirmed, update the `last-synced` field on all modified entries.
2. Update the "Delta from As-Coded" sections in both as-intended files if the as-coded files exist.
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
