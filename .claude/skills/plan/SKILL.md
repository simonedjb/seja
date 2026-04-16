---
name: plan
description: "Make a plan to add a feature, fix a bug, or refactor code. Supports metacomm framing for design-intent briefs."
argument-hint: "<brief> [--review <light|standard|deep>] [--framing metacomm] [--light] [--plan | --roadmap [--from-spec <path>] [--auto]]"
compatibility: "Designed for Claude Code with SEJA framework"
metadata:
  last-updated: 2026-03-29 00:15 UTC
  version: 1.0.0
  plan_format_version: 1
  category: planning
  context_budget: heavy
  eager_references:
    - project/product-design-as-coded.md
    - project/product-design-as-intended.md
    - general/report-conventions.md
    - general/coding-standards.md
    - general/review-perspectives-index.md
  references:
    - project/product-design-as-coded.md
    - project/product-design-as-intended.md
    - project/conventions.md
    - general/report-conventions.md
    - general/coding-standards.md
    - project/standards.md
    - project/security-checklists.md
    - project/design-standards.md
    - general/review-perspectives.md
    - general/review-perspectives-index.md
    - general/review-log-template.md
---

## Quick Guide

**What it does**: Creates a step-by-step plan for your next feature, bug fix, or improvement. You describe what you want, and the agent produces a detailed plan you can review before anything changes. With `--roadmap`, it generates a full product roadmap with dependency-aware execution waves from your project's design specs.

**Example**:
> You: /plan Add a tagging feature so users can organize their tasks by topic
> Agent: Creates Plan 0042 with 8 steps covering data model, UI components, and search integration. Each step lists files to change, verification criteria, and dependencies. Asks if you want to execute it.

> You: /plan --roadmap --auto
> Agent: Reads project design specs, decomposes into work items, groups into 5 waves (foundation, services/API, frontend, cross-cutting, testing), and generates individual plans for each item.

**When to use**: You have a clear idea of what you want to build or fix and want to see a structured plan before any code changes happen. Use `--framing metacomm` when describing the change from the user's perspective. Use `--roadmap` when you need a high-level view of what to build next, want to organize features into delivery phases, or need to communicate the plan to stakeholders. Use `--plan` to force a single plan when the agent would otherwise suggest a roadmap. If you omit both `--plan` and `--roadmap`, the agent auto-detects the best mode from your brief and asks for confirmation before proceeding.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<brief>` | Yes | Description of the task to plan (feature, bug fix, refactor) |
| `--light` | No | Generate a lightweight proposal instead of a full plan |
| `--plan` | No | Force single-plan mode (skip auto-detection) |
| `--roadmap` | No | Generate a full product roadmap with dependency-aware execution waves |
| `--from-spec <path>` | No | Parse roadmap from a pre-filled spec file. Use with `--roadmap` |
| `--auto` | No | Auto-generate roadmap from project reference files. Use with `--roadmap` |
| `--framing metacomm` | No | Frame the brief as a designer's metacommunication message (I/you phrasing) |
| `--review <level>` | No | Override complexity-gated review depth. Valid: `light`, `standard`, `deep` |

# Make a plan

> **`/design`** defines WHAT to build and WHY. **`/plan`** defines HOW to build it and WHY those "hows." Design produces project definitions (`_references/project/`); plans consume them to produce actionable implementation steps.

## Design Guard

Before planning, verify that minimum project design exists:
- Check if `project/conventions.md` exists in `_references/`
- If **missing**: stop and tell the user: "No project design found. Run `/design` first to define your project's stack, conventions, and domain model."
- If **present**: proceed with planning

If there are no arguments, ask for the brief.

## Mode Detection

Determine which workflow to use based on the arguments and the brief:

1. **Explicit override** — if the argument includes `--light`, use the [Lightweight Proposal Workflow](#lightweight-proposal-workflow). If the argument includes `--roadmap`, use the [Roadmap Workflow](#roadmap-workflow). If the argument includes `--plan`, use the standard planning workflow below. Skip the rest of this section.

2. **Auto-detection** — if neither `--plan` nor `--roadmap` is present, assess the brief against these signals:

   | Signal | Points toward |
   |---|---|
   | Brief mentions ≥3 distinct entities, resources, or features | Roadmap |
   | Brief spans ≥2 architectural layers (e.g., model + API + UI) | Roadmap |
   | Brief mentions multiple pages, screens, or user flows | Roadmap |
   | Brief describes a single bug, fix, or refactor | Single plan |
   | Brief references a specific file, component, or endpoint | Single plan |
   | Brief scope fits comfortably in ≤12 plan steps | Single plan |

   Count the signals. If the majority point toward roadmap, recommend roadmap mode; otherwise recommend single plan.

3. **Confirmation gate** — present the recommendation to the user and ask for confirmation before proceeding (text-based, not AskUserQuestion — this is a quick yes/no with an override option):
   - If recommending roadmap: *"This brief spans multiple entities/layers. I'd recommend generating a **roadmap** with dependency-aware waves rather than a single plan. Proceed with roadmap mode, or force a single plan?"*
   - If recommending single plan: *"This brief looks well-scoped for a **single plan**. Proceed, or would you prefer a full roadmap instead?"*

   Use the user's answer to select the workflow.

## Definitions

Output folder: `${PLANS_DIR}` (see project/conventions.md)
Filename pattern: `plan-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)

Reserve the next global ID by running `python .claude/skills/scripts/reserve_id.py --type plan --title '<short title>'`. Use the returned 6-digit ID.

## Framing

This skill supports two framings:

- **Default** — the brief is a technical description (feature, bug, refactor)
- **Metacomm** — the brief is a designer's metacommunication message, phrased as "I" (designer) speaking to "you" (user). Record the brief **verbatim** in the plan (see `general/shared-definitions.md` § Verbatim rule and § Phrasing rule). Interpret it as the designer telling the user what they can do, how, when (in which context, under which constraints), with what purpose, or why, and ensure the generated plan will make it happen as stated. All metacomm text the agent generates (summaries, intention notes, per-feature intents) must also use I/you phrasing — never third-person or passive voice.

When invoked with `--framing metacomm`, use the metacomm framing. Otherwise, use the default framing.

See [Metacomm framing -- additional context](#metacomm-framing--additional-context) below for details on the `--framing metacomm` option.

## Review Depth Override

This skill supports a `--review <light|standard|deep>` flag to override the complexity-gated review depth for a single invocation. When provided, the effective depth is resolved as `max(auto, floor, flag)` where:
- `auto` = the depth determined by the complexity gate (step 4)
- `floor` = `MINIMUM_REVIEW_DEPTH` from project/conventions.md (default: `light`)
- `flag` = the `--review` value (if provided)

The maximum (deepest) depth from all three sources always wins, using the ordering light < standard < deep.

### Metacomm framing — additional context

When using the metacomm framing:

1. **Read existing metacomm intentions**: If `_references/project/product-design-as-intended.md` exists, read it before generating the plan. This file contains per-feature metacommunication intentions that describe how the designer intends the system to communicate with users.

2. **Contradiction detection**: Compare the new brief against the existing intentions in `project/product-design-as-intended.md`. If the new brief contradicts an existing intention (e.g., the brief says "remove the tagging flow" but an existing intention describes tagging behavior), emit a **⚠ Metacomm contradiction** warning in the plan output, listing:
   - The new brief's directive
   - The conflicting existing intention (quote the relevant line)
   - A recommendation: update the existing intention, or confirm the new brief supersedes it

3. **Append metacomm intention note**: After generating the plan, append a trailing section to the plan file:
   ```markdown
   ## Metacomm Intention
   - **Summary**: <one-sentence summary of the metacommunication message this plan implements>
   - **Source**: agent (metacomm)
   ```
   This note is consumed downstream by `/explain spec-drift` or `/post-skill` to keep `project/product-design-as-intended.md` in sync.

## Skill-specific Instructions

1. Run the /pre-skill "plan" $ARGUMENTS[0] to add general instructions to the context window.

2. **Load references on demand**: Load lazy references from the "Available references" list as needed during planning:
   - Load `project/product-design-as-intended.md` when using `--framing metacomm`
   - Load `project/standards.md` when plan steps touch backend, frontend, testing, or i18n files
   - Load `project/security-checklists.md` when plan involves auth, validation, or sensitive data
   - Load `project/design-standards.md` when plan steps involve UX flows or visual design
   - Load `general/review-perspectives.md` before the review phase (Phase 1)
   - Load `general/review-log-template.md` before writing the review log

3. Following best practices, create a structured, self-contained plan that can be executed independently by an agent, including:
- *header*: `# Plan <id> | <prefix><scope> | <current datetime> | <short title> | Review: <depth>` followed by a metadata line `plan_format_version: 1` on the next line — prefix based on the brief; `<depth>` is Light, Standard, or Deep (set in step 5). If metacomm framing, add `METACOMM |` after the prefix-scope. If invoked from an advisory Q&A flow with a source advisory ID, include `source: advisory-<id>` on the metadata line after `plan_format_version: 1`.
- If default framing: *user brief*, *agent interpretation*, *files* — per _references/general/report-conventions.md
- If metacomm framing: *designer's metacommunication message* (the brief), *agent interpretation*, *files* — per _references/general/report-conventions.md
- *agent interpretation* must consistently cover three elements:
  1. **Problem**: one sentence describing what problem this plan solves or what need it addresses
  2. **Approach**: the chosen approach and why it was selected -- what makes it the right fit
  3. **Alternatives rejected** (for Standard/Deep plans): key alternatives that were considered and why they were not chosen. Omit for Light-depth plans where the approach is self-evident.
- If the prefix is FIX (the brief describes an error or bug), also include:
  - *error log* (optional): if an extensive error log is provided, summarize it and prepend with "summarized error log:". In this case, replace the error log in the user brief with "<error log> (see summary below)"
  - *root cause*: diagnostics of the problem
- *best practices*: used in the plan
- *design decisions* (Standard/Deep plans only; omit for Light): a single section capturing:
  - **User-visible impact**: what changes from the user's perspective (one paragraph)
  - **Trade-offs accepted**: what was gained and what was given up
  - **Metacommunication impact** (when the plan modifies user-facing communication -- error messages, help text, UI copy, CLI output, documentation): what the system will now communicate differently to the user. Use I/you phrasing per shared-definitions.md. Include this line regardless of whether `--framing metacomm` was used -- any plan that changes what users see or read has metacommunication impact.
- *steps*: structured step list (see **Step format** below)
- *review log*: a log of the review iterations, if applicable
- *outcomes*: expected outcomes
- *smoke*: `true` if any step creates or modifies API route files or frontend page/component files; `false` otherwise. This flag is consumed by `/implement` to decide whether to run `/check smoke api` during the quality gate.
- *reflection* (optional, appended post-execution): a `## Reflection` section holding dated bullets appended by post-skill's post-action reflection loop (step 11b) when the user selects "Write a one-line reflection note". Absent by default; the section may be created on first use. Plans without reflection notes are fully valid. See `_references/general/constraints.md` § Decision-point rationale convention and `.claude/skills/post-skill/SKILL.md` step 11b for the reflection loop behavior.
  
   **Step format:**

   Replace the former *actions* + *to do* sections with a unified *steps* section. Each step must be self-contained — executable by a subagent with no shared context from prior steps. Use this format:

   ```markdown
   ## Steps

   ### Step 1: <short imperative title>
   <What to do — a self-contained description that a subagent can execute without reading other steps.
   Include enough context that the step makes sense in isolation: what the code should do, not just which file to edit.>
   - **Files**: <path> (create|modify|delete), <path> (modify), ...
   - **References**: <reference-name>, <reference-name>, ...
   - **Depends on**: none | Step N, Step M
   - **Verify**: <how to know this step succeeded — e.g., "tests pass", "migration runs forward and backward", "endpoint returns 200">
   - **Tests**: <what tests to create or update — e.g., "Add unit tests for new service method", "Update existing API tests for changed response format"> | N/A (no testable code changes)
   - **Docs**: <what documentation to create or update — e.g., "Update API reference for new endpoint", "Add contextual help page for new screen"> | N/A (no documentation impact)
   - **Traces**: REQ-xxx, REQ-yyy | N/A (no design-intent requirements)
   - [ ] Done
   ```

   Guidelines for step decomposition:
   - Each step should be completable in one subagent context window (rule of thumb: touches ≤5 files)
   - If a step would touch >5 files, split it into smaller steps
   - **Files**: list all files the step reads, creates, modifies, or deletes. For new files, the path is a planned location. For existing files, verify they exist during planning.
   - **References**: list only the `_references/` reference files relevant to this step (e.g., `project/standards.md § Backend` for a Python step, `project/standards.md § Frontend` for a React step). Omit irrelevant ones.
   - **Depends on**: list step numbers whose output this step requires. Use `none` if the step is independent. The orchestrator uses this to avoid executing steps before their dependencies complete.
   - **Verify**: a concrete, testable condition. Prefer automated checks ("tests pass", "linter clean") over subjective ones ("looks right").
   - **Tests**: required for steps with prefix FEATURE, FIX, or REFACTOR that create or modify source code files. Set to `N/A` for steps that only modify documentation, configuration, framework files, or other non-testable artifacts. Steps with prefix CHORE, DOCUMENT, or TEST may use N/A. Each step that modifies source code should declare what tests are needed. If the step is too small to warrant its own tests, indicate which step's tests will cover it.
   - **Docs**: required for steps with prefix FEATURE or REDESIGN that create or modify user-facing code or public APIs. Specify what documentation should be created or updated. Set to `N/A` for steps with no documentation impact (internal refactors, test-only changes, configuration). When a step adds a new API endpoint, note "Update API reference"; when adding a new UI screen, note "Add contextual help page".
   - **Traces**: optional field linking the step to design-intent requirements. List comma-separated REQ IDs from `product-design-as-intended.md` that this step implements (e.g., `REQ-ENT-001, REQ-PERM-003`). Set to `N/A` if no REQ markers exist in the project's design-intent file or if the step does not directly implement a design requirement (e.g., test-only steps, infrastructure). When REQ markers exist in the spec, the planning agent should map each plan step to the requirement(s) it satisfies. See `general/shared-definitions.md` for the REQ ID convention.
   - Steps should be ordered so that dependencies flow forward (Step 2 depends on Step 1, not the reverse).

4. Save the plan to the plan file. If not overwriting a file, proceed without asking for authorization.

4b. **Coverage check (advisory)**: If `_references/project/product-design-as-intended.md` exists and contains REQ markers (`<!-- REQ-*-NNN -->`), run `python .claude/skills/scripts/check_plan_coverage.py --mode advisory` and include the coverage summary in the plan file as an informational section after the steps. This helps identify uncovered requirements early. If no REQ markers exist, skip silently.

5. **Review the plan** using a complexity-gated, two-phase process. Use `general/review-log-template.md` for the review log format.

   **Step metadata validation (before perspective review):**
   Before starting the perspective review, validate each step's metadata:
   - Every step has all required fields (Files, References, Depends on, Verify, Tests, Docs, checkbox) and optional fields where applicable (Traces -- required when project has REQ markers)
   - File paths for existing files are verified (the file exists on disk)
   - Dependencies flow forward (no circular dependencies, no backwards references)
   - No step touches >5 files (split if so)
   - Each step description is self-contained (a subagent could execute it without reading other steps)
   Fix any issues found before proceeding to the perspective review.

   **Complexity gate — determine review depth:**
   Assess the plan's complexity to choose the appropriate review depth:
   - **Light** — the plan has ≤6 action steps AND touches ≤4 files. Perform a quick inline scan of the shortlisted perspectives (Phase 1 only, no Phase 2 eligibility). Label the review log `Review: Light`.
   - **Standard** — the plan has 7–12 action steps OR touches 5–8 files. Perform full Phase 1; Phase 2 eligible if needed. Label `Review: Standard`.
   - **Deep** — the plan has >12 action steps OR touches >8 files OR involves migrations, auth, or cross-cutting (X-scope) changes. Perform full Phase 1 + Phase 2 for all Deferred concerns (not just regression-risk ones). Label `Review: Deep`.
   **Depth resolution:**
   After determining the automatic depth, resolve the effective depth:
   1. Read `MINIMUM_REVIEW_DEPTH` from `project/conventions.md` (default: `light` if not set).
   2. If `--review <depth>` flag was provided, include it.
   3. Effective depth = `max(auto, floor, flag)` using ordering `light < standard < deep`.
   4. If the effective depth differs from auto, log in the review: "Review depth overridden: auto=`<auto>`, floor=`<floor>`, flag=`<flag>`, effective=`<effective>`".

   Update the plan header's `Review: <depth>` field to match the effective depth.

   **Phase 1 — Perspective triage and scan (inline, no subagents):**
   Use the two-stage loading protocol (see `general/review-perspectives.md` section "Two-Stage Loading"):
   1. Load `general/review-perspectives-index.md` to see all 16 perspectives at a glance.
   2. Based on the plan's prefix and scope, identify the default shortlist of 3-6 most relevant perspectives using the **Perspective Shortcuts by Plan Prefix** table in `general/review-perspectives.md`.
   3. If the plan's content clearly warrants it, add up to 2 additional perspectives beyond the default shortlist with a one-line justification (e.g., "Added PERF: Step 3 introduces a bulk query not typical for CHORE-O scope").
   4. Load only the selected `review-perspectives/<tag>.md` files. Do not load all 16 files.
   For perspectives not in the final shortlist, mark as N/A in the review log.
   Scan the plan against each shortlisted perspective and record Adopted/Deferred status with a one-line concern for each.
   If the review depth is **Light**, stop here — do not proceed to Phase 2.

   **Phase 2 — Targeted deep-dives:**
   Trigger Phase 2 only for Deferred perspectives where the concern could cause a regression, a production incident, or a standards violation. For **Deep** reviews, also trigger Phase 2 for Deferred concerns that represent additive improvements. Do not trigger Phase 2 for concerns that are purely cosmetic or out of scope.

   **Execution strategy by review depth:**
   - **Standard** — launch the `plan-reviewer` agent (Agent tool, subagent_type=`plan-reviewer`) with the plan text, plan file path, and review depth set to `standard`. The agent performs Phase 1 triage and Phase 2 deep-dives for qualifying perspectives and returns the review log and any plan amendments. Append the agent's output to the plan file.
   - **Deep** — launch the `plan-reviewer` agent (Agent tool, subagent_type=`plan-reviewer`) with the full plan text, plan file path, and review depth set to `deep`. The agent performs all deep-dives, conflict checks, and iterations autonomously and returns the review log and any plan amendments. Append the agent's output to the plan file.

   **Conflict check:**
   After each iteration that produces Phase 2 recommendations, check whether recommendations from different perspectives contradict each other. Resolve conflicts per the priority rules in `general/review-perspectives.md` §Resolving Perspective Conflicts. Log the check in the review log (see template).

   **Iteration and convergence:**
   If Phase 2 produces recommendations that change the plan:
   1. Append a `### Plan Amendment (iteration N)` section to the plan with the change and rationale. Do not modify or delete existing plan text — the amendment is additive (per report conventions).
   2. Update the Steps section to reflect the amended steps (add, modify, or reorder steps as needed). The Steps section is the only section that may be updated in place, since it is a living checklist.
   3. Re-evaluate perspectives whose plan steps were modified (regardless of their prior status), plus any perspective that remains Deferred.
   4. If all Phase 2 findings result in "no change needed," terminate the loop immediately — do not re-iterate.
   5. Otherwise, repeat until all perspectives are either Adopted or Deferred with a clear rationale that no change is needed, or until 3 iterations are reached, or until the deep-dive budget (6) is exhausted — whichever comes first.

   **Execution metrics (mandatory):**
   At the end of the review log, append the Execution Metrics table (see `general/review-log-template.md`). This data is used to tune review thresholds over time.

   Append all review results to the plan file. Do not rewrite the file from scratch — only add the review log and any amendment sections.

6. Output the plan id.

7. Ask the user via AskUserQuestion what to do next. Options (with rationale per the Decision-point rationale convention in `_references/general/constraints.md`):
   - **Implement now** -- commit the plan and run `/implement <id>` to execute the plan steps. Recommended when the plan has been reviewed and you are ready to proceed in this session. NOT recommended when you want to review the plan offline or share it with others first.
   - **Commit plan** -- commit the plan as-is without implementing. The plan can be implemented later via `/implement <id>`. Recommended when you want to review further, implement in a separate session, or share the plan. NOT recommended when the plan is trivially correct and delay adds no value.
   - **Revise plan** -- stop and wait for further instructions. The plan is not committed yet. Recommended when you spotted an issue or want to adjust the approach before committing. NOT recommended when the plan is satisfactory and the revision impulse is perfectionism rather than substance.

8. Based on the user's choice:
   - **Implement now**: run /post-skill <id>, then run /implement <id>.
   - **Commit plan**: run /post-skill <id>.
   - **Revise plan**: do not run /post-skill. Wait for the user's instructions.

---

# Lightweight Proposal Workflow

> This section is used when `--light` is present in the arguments. Skip the standard planning workflow above entirely.

## Overview

Generates a minimal change proposal for small, surgical modifications. No multi-step decomposition, no multi-phase review. Designed for changes that are too small to warrant a full plan but should still be tracked.

## Definitions

Output folder: `${PROPOSALS_DIR}` (see project/conventions.md)
Filename pattern: `proposal-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)

Reserve the next global ID by running `python .claude/skills/scripts/reserve_id.py --type proposal --title '<short title>'`. Use the returned 6-digit ID.

## Steps

1. Run /pre-skill "plan" to add general instructions to the context window.

2. Reserve a global ID via `reserve_id.py --type proposal --title '<title>'`.

3. Generate the proposal in the following format:

   ```markdown
   # Proposal <id> | <prefix><scope> | <datetime> | <short title>
   plan_format_version: 1

   ## What
   <one-paragraph description of the change>

   ## Why
   <motivation -- what problem this solves>

   ## Files
   <list of files to create/modify/delete, with one-line description of each change>

   ## Verify
   <single verification criterion>

   ## Risks
   <potential issues or side effects, or "None identified">

   - [ ] Done
   ```

4. **Quick review**: Perform an inline scan of the 2-3 most relevant perspectives (always include SEC if code changes are involved). Record as a compact review section:

   ```markdown
   ## Review (Light)
   - SEC: <Adopted/N/A -- one line>
   - <perspective>: <Adopted/N/A -- one line>
   ```

5. Save the proposal to `${PROPOSALS_DIR}/proposal-<id>-<slug>.md`.

6. Ask the user: "Execute this proposal now?" If yes, execute the changes inline (no subagent orchestration needed for single-change proposals), then mark the checkbox as done and run /post-skill <id>. If no, run /post-skill <id>.

---

# Roadmap Workflow

> This section is used when `--roadmap` is present in the arguments. Skip the standard planning workflow above entirely.

## Overview

This mode generates a product roadmap by decomposing a project's conceptual design and standards into independent work items, classifying each as technical or design, grouping them into dependency-aware execution waves, and generating plans via the standard plan workflow (with optional `--framing metacomm` for design items). It supports three modes: auto-generate from project references, parse a pre-filled spec file, or generate a blank spec skeleton.

## Definitions

Output folder: `${ROADMAP_DIR}` (see project/conventions.md)
Filename pattern: `roadmap-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)

Reserve the next global ID by running `python .claude/skills/scripts/reserve_id.py --type roadmap --title '<short title>'`. Use the returned 6-digit ID.

## Mode Selection

If no sub-argument or mode flag is provided beyond `--roadmap`, use the AskUserQuestion tool to ask which mode (if AskUserQuestion is not available, present as a numbered text list). Each option carries rationale per the Decision-point rationale convention in `_references/general/constraints.md`:

- **1. Auto-generate** -- I read the project reference files (`product-design-as-intended.md`, `product-design-as-coded.md`, conventions, standards) and decompose the work into dependency-aware waves. Recommended when `/design` has already populated the project references and the roadmap should reflect them. NOT recommended when the references are stale or missing, in which case the roadmap would inherit the gaps.
- **2. From spec file** -- I read a pre-filled `roadmap-spec.md` you provide and compile it into the roadmap structure. Recommended when you already have a manual draft or are working on an existing project where the refs are not yet canonical. NOT recommended when no spec file exists yet -- in that case use option 3 first.
- **3. Generate blank spec** -- I create a `roadmap-spec` skeleton for you to fill out offline, then invoke option 2 on it later. Recommended when you want human-authored control before auto-decomposition. NOT recommended when the project references are already authoritative -- option 1 is faster in that case.

If the argument includes `--auto`, skip the menu and go directly to Mode 1.
If the argument includes `--from-spec <path>`, skip the menu and go directly to Mode 2.

---

## Mode 1: Auto-generate from project references

### Steps

1. **Run /pre-skill "plan"** to load general instructions.

2. **Read project references**: Verify the following files exist in the current project's `_references`. If `project/product-design-as-intended.md` is missing, abort with a message suggesting the user run `/design` first. `project/product-design-as-coded.md` is required for brownfield projects but optional for greenfield. Other files are optional (warn but continue). Read:
   - `project/product-design-as-coded.md` (unified implementation state with three H2 domain sections: `## Conceptual Design`, `## Metacommunication`, `## Journey Maps` -- empty or absent for greenfield)
   - `project/product-design-as-intended.md` (target-state entities, hierarchy, permissions, UX patterns, metacommunication intentions)
   - `project/conventions.md` (directory structure, source paths)
   - `project/standards.md § Backend` (API patterns, service layer)
   - `project/standards.md § Frontend` (pages, components, routing)
   - `project/standards.md § i18n` (locales, translation scope)
   - `project/security-checklists.md` (validation, auth requirements)

2b. **Requirements extraction pass**: If `_references/project/product-design-as-intended.md` contains REQ markers (`<!-- REQ-*-NNN -->`), launch a `general-purpose` agent (Agent tool) with a fresh context to extract a requirements index. The agent should:

   1. Read `_references/project/product-design-as-intended.md` in full
   2. For each REQ marker found, extract: ID, section number, heading/title, classification (derived from type prefix per `general/shared-definitions.md` -- PERM/VAL -> security, UX/MC/JM -> ux, ENT/DELTA -> technical, I18N -> cross-cutting)
   3. Output a flat markdown table:
      ```
      | ID | Section | Title | Classification |
      |---|---|---|---|
      | REQ-ENT-001 | 2 | User entity | technical |
      | REQ-PERM-001 | 4 | Admin role | security |
      ```

   Use this requirements index as the primary input for the decomposition step (step 3), cross-referencing against the index rather than re-reading the full prose. Each generated work item should note which REQ IDs it covers.

   If no REQ markers are found, skip this step and proceed with the existing decomposition approach (step 3 reads the full prose directly).

3. **Decompose into work items**: Compare the as-coded and as-intended conceptual designs to identify work items from the **delta** between them. Use this decomposition strategy:

   **Delta analysis:**
   - Entities, permissions, or UX patterns present in **as-intended but not in as-coded** become **new** work items.
   - Entities, permissions, or UX patterns present in **as-coded but removed in as-intended** become **deprecation** work items (migration to remove, API sunset, UI removal).
   - Entities that exist in both but differ become **modification** work items (migration alter, API update, UI update).
   - If as-coded and as-intended are identical (greenfield), all entities in as-intended are treated as new work items.

   **Layer decomposition** (applied to the delta work items above):

   **Foundation layer (sequential -- migration chain):**
   - One work item per entity cluster (related entities that share FKs)
   - Includes: model, migration, basic service layer, and unit tests
   - These MUST be ordered sequentially due to migration chain dependencies

   **Service + API layer (parallelizable per resource):**
   - One work item per API resource (CRUD endpoints, validation schemas, permissions)
   - Depends on: foundation layer for the relevant entities

   **Frontend layer (parallelizable per page/feature):**
   - One work item per page or major feature
   - Depends on: API layer for the relevant endpoints

   **Cross-cutting (limited parallelism):**
   - i18n setup, auth integration, contextual help, error handling patterns
   - Touches shared files -- limited parallelism

4. **Classify each work item** as:
   - **Technical** -- infrastructure, models, services, API endpoints, migrations, tests. Will be planned via the standard plan workflow.
   - **Design** -- UX flows, page layouts, information hierarchy, empty states, onboarding, feature discoverability. Will be planned via the plan skill with `--framing metacomm`.

   Classification heuristic: if the work item's primary value is in *what the user sees and experiences*, it is design. If the primary value is in *what the system does internally*, it is technical.

5. **Group into execution waves**: Organize items by dependency level:
   - **Wave 0 (sequential)**: Foundation models + migrations (strict order due to migration chain)
   - **Wave 1 (parallel)**: Service + API layer (independent per resource, all depend on Wave 0)
   - **Wave 2 (parallel)**: Frontend pages + features (independent per page, depend on Wave 1 APIs)
   - **Wave 3 (limited parallel)**: Cross-cutting concerns (i18n, auth, help, error handling)
   - **Wave 4 (parallel)**: Testing and polish (E2E tests, accessibility, documentation)

6. **Present draft roadmap for review**: Output the full roadmap as a numbered list grouped by wave, with each item showing:
   - ID (short slug)
   - Title
   - Scope (backend / frontend / fullstack)
   - Size (S / M / L)
   - Classification (technical / design)
   - Dependencies

7. Ask the user to review, add, remove, or reorder items before generating plans.

8. **Save roadmap summary**: Save to `${ROADMAP_DIR}/roadmap-<id>-<slug>.md` with:
   - Header: `# Roadmap <id> | <current datetime> | <short title>`
   - Source: which reference files were used
   - Wave summary table with `plan-TBD` in the Plan column and classifications
   - Execution instructions (which plans can run in parallel)

9. **Plan generation decision point**: Present the user with a decision point (text-based, not AskUserQuestion -- this is a mixed open-ended/closed-set decision point where freeform response is preferred) offering three options:

   - **Create all plans now** -- generates plans for every work item, processing waves sequentially (Wave 0 first, then Wave 1, etc.). Each plan invokes the standard plan workflow inline.
     - Recommended when: the roadmap has 5 or fewer work items and you want to proceed immediately.
     - NOT recommended when: the roadmap has 6+ items, as context budget may degrade plan quality in later waves.
   - **Create plans for Wave 0 only** -- generates plans only for the foundational wave items.
     - Recommended when: the roadmap has 6+ items, or you want to review foundation plans before committing to the full roadmap. Wave 0 items are always needed first and most immediately actionable.
     - NOT recommended when: you already know the full roadmap scope is correct and want to batch-generate everything.
   - **Don't create plans now** -- keep the roadmap as-is with `plan-TBD` entries; create plans manually later via the commands in Execution Instructions.
     - Recommended when: you want to review the roadmap across sessions, share it with others, or are not ready to commit to implementation.
     - NOT recommended when: you have a clear scope and want to start immediately.

   **Context budget guardrail**: If the roadmap has more than 5 work items and the user selects "Create all plans now", emit a note: "This roadmap has N work items. Generating all plans in a single session may impact quality for later waves due to context budget. Consider 'Wave 0 only' if quality is a concern." Do not block -- just inform.

   **Conditional plan generation**: Based on the user's choice, generate plans for the selected work items:
   - If classified as **technical**: invoke the standard plan workflow with the item's description
   - If classified as **design**: invoke the plan skill with `--framing metacomm` and the item's description phrased as a metacommunication message using I/you (e.g., "When you open the home page, I want you to see...")
   - Record the generated plan ID next to each work item by updating the roadmap file's Plan column from `plan-TBD` to the actual plan ID
   - If "Don't create plans now" was selected, skip generation entirely

   **Anti-pattern -- do not pre-reserve plan IDs.** `/plan` reserves its own ID when invoked. Do not call `reserve_id.py --type plan` up front for the downstream work items, and do not embed such a step in the roadmap summary's "Next steps" or resumption prose. Pre-reserving looks tidy but causes drift when the user executes items out of their original order across sessions -- the pre-reserved IDs stop matching the IDs `/plan` actually assigns, and the roadmap's Plan column goes stale. The Plan column should start as `plan-TBD` (or `pending`) for every row and be filled in with the real ID after each `/plan` invocation completes. Note: generating full plans eagerly (via the decision point above) is acceptable -- a generated plan can be revised or discarded without causing the ID drift that empty reservations create.

9b. **Coverage check (advisory)**: After plans are generated (skip if no plans were generated), if `_references/project/product-design-as-intended.md` exists and contains REQ markers, run `python .claude/skills/scripts/check_plan_coverage.py --mode advisory` and include the coverage summary in the roadmap file. This provides an aggregate view of which requirements are covered across all generated plans.

10. **Output execution instructions**: Tell the user how to proceed, adapting the output based on which plans were generated:
    - If all plans were generated: show `/implement <plan-id>` commands with real plan IDs for each wave
    - If only Wave 0 plans were generated: show `/implement <plan-id>` commands for Wave 0 with real IDs, and `/plan <description>` commands for remaining waves
    - If no plans were generated: show `/plan <description>` commands for all waves
    - Include the recommended execution method (multiple Claude Code sessions or worktree-isolated agents) for parallel waves

---

## Mode 2: From spec file

### Steps

1. **Run /pre-skill "plan"** to load general instructions.

2. **Locate spec file**: Use the path from `--from-spec` argument, or ask the user.

3. **Parse the roadmap-spec.md**: Extract themes, work items, constraints, and wave groupings. Parsing rules:
   - Lines starting with `- key:` are key-value pairs (value is everything after the first colon, trimmed)
   - Lines starting with `## ` or `### ` are section/subsection headers
   - Lines inside `<!-- ... -->` are HTML comments (ignored during parsing)
   - Empty values mean "not provided" (use defaults or ask)
   - The `description:` field uses YAML-style `>` for multi-line text

4. **Validate**: Check for:
   - Missing required fields (id, title, scope, description for each work item)
   - Circular dependencies (A depends on B, B depends on A)
   - Items with `depends_on` referencing non-existent IDs
   - Present a validation report before proceeding

5. **Classify items**: Apply the same technical/design classification heuristic as Mode 1. The user can override classification in the spec via the optional `type: technical | design` field per work item.

6. **Present validation report**: Show the parsed items with their classifications and dependency graph. Ask user to confirm or adjust.

7. **Save roadmap summary**: Same as Mode 1, step 8.

8. **Plan generation decision point**: Same as Mode 1, step 9.

9. **Output execution instructions**: Same as Mode 1, step 10.

---

## Mode 3: Generate blank spec

### Steps

1. **Determine target directory**: Use the current working directory or ask the user.

2. **Create specs/ subfolder**: Create `<target>/specs/` if it does not exist.

3. **Generate the spec file**: Copy `template/roadmap-spec.md` (from this project's `_references`) to `<target>/specs/roadmap-spec-YYYY-MM-DD HH.MM UTC.md`. Substitute the `{datetime}` placeholder in the header comment with the current UTC datetime.

4. **Output next steps**:
   > Spec file created at `<path>`.
   >
   > Fill in your choices -- each field has inline comments explaining the options. Required fields per work item: id, title, scope, description. Everything else is optional.
   >
   > When ready, run `/plan --roadmap --from-spec <path>`.

---

## Wave Design Principles

### Migration safety (critical)

The Alembic migration chain is linear -- each migration depends on the previous one. Therefore:
- **Wave 0 must be sequential**: only one plan at a time creates migrations
- If multiple entity clusters need migrations, order them by dependency (entities with FK references to other entities come after the referenced entity)
- Alternative: group all models + migrations into a single large plan

### Parallelism boundaries

| Wave | Parallelizable? | Constraint |
|------|----------------|------------|
| 0 -- Foundation | No (sequential) | Migration chain is linear |
| 1 -- Services/API | Yes, per resource | Each resource is independent once models exist |
| 2 -- Frontend | Yes, per page | Each page is independent once APIs exist |
| 3 -- Cross-cutting | Limited | Shared files (i18n JSONs, auth config, routing) |
| 4 -- Testing/polish | Yes, per suite | E2E, a11y, docs are independent |

### Classification heuristic

| Primary concern | Classification | Planned via | Examples |
|----------------|---------------|-------------|----------|
| What the system does internally | Technical | `/plan` | Models, migrations, services, API endpoints, validation |
| What the user sees and experiences | Design | `/plan --framing metacomm` | Page UX, onboarding, empty states, navigation flow, error feedback |

Design items are phrased as metacommunication messages using I/you: "When you [context], I want you to [experience/action], because I know you [rationale]."

---

## Roadmap Summary File Format

```markdown
# Roadmap <id> | <datetime> | <title>

## Source
- project/product-design-as-coded.md (read)
- project/product-design-as-intended.md (read)
- project/conventions.md (read)
- ... (list all files read)

## Wave Summary

### Wave 0 -- Foundation (sequential)
| # | ID | Title | Scope | Type | Plan | Status |
|---|-----|-------|-------|------|------|--------|
| 1 | user-model | User entity + migration | backend | technical | plan-TBD | pending |
| 2 | group-model | Group entity + migration | backend | technical | plan-TBD | pending |

### Wave 1 -- Services/API (parallel)
| # | ID | Title | Scope | Type | Plan | Depends on | Status |
|---|-----|-------|-------|------|------|-----------|--------|
| 3 | user-api | User CRUD API | backend | technical | plan-TBD | user-model | pending |
| 4 | group-api | Group CRUD API | backend | technical | plan-TBD | group-model | pending |

### Wave 2 -- Frontend (parallel)
| # | ID | Title | Scope | Type | Plan | Depends on | Status |
|---|-----|-------|-------|------|------|-----------|--------|
| 5 | home-page | Home page UX flow | frontend | design | plan-TBD | user-api | pending |

> The `Plan` column starts as `plan-TBD` for every row. Fill in the real ID (e.g., `plan-000042`) **only after** `/plan` has been invoked for that work item and has returned the ID it reserved. Do not pre-reserve IDs up front -- see the anti-pattern note in Mode 1 step 8.

## Execution Instructions

### Wave 0 (sequential)
Execute these plans one at a time, in order:
1. /implement XXXX (user-model)
2. /implement XXXX (group-model)

### Wave 1 (parallel -- 2 plans)
All depend on Wave 0. Execute in parallel via:
- Multiple Claude Code sessions, or
- Worktree-isolated agents from a single session

### Wave 2 (parallel -- 1 plan)
Depends on Wave 1. Execute after Wave 1 completes.
```
