---
name: onboarding
description: "Generate a tailored onboarding plan for a new team member based on their role and expertise level."
argument-hint: "<role-family> <expertise-level> [name] [--area <focus-area>] [--batch <spec-list>]"
metadata:
  last-updated: 2026-03-28 18:45:00
  version: 1.0.0
  category: utility
  context_budget: standard
  references:
    - general/onboarding.md
    - project/conceptual-design-as-is.md
    - general/shared-definitions.md
    - general/report-conventions.md
---

## Quick Guide

**What it does**: Creates a personalized onboarding plan based on role and experience level. Covers what to learn, in what order, and where to find things. Use it to onboard a new teammate — or yourself, if you are new to the toolkit or the project.

**Example (onboarding a new designer)**:
> You: /onboarding shaper L2 Alice --area frontend
> Agent: Generates a 30-60-90 day onboarding plan for a mid-level product designer focused on the frontend. Includes reading lists, key contacts, and milestone checkpoints.

**Example (onboarding yourself as a product designer new to AI-assisted development)**:
> You: /onboarding shaper L1 --area design
> Agent: Generates a starter onboarding plan for a newcomer in a shaper (designer/PM) role, with focus on design workflows and how to use the toolkit effectively.

**When to use**: A new team member is joining and you want a structured, role-appropriate onboarding experience rather than ad-hoc knowledge transfer. Also useful when *you* are the newcomer and want a clear learning path into the project and the toolkit.

# Onboarding

Generate a tailored onboarding plan for a new project team member.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<role-family>` | Yes | Role family: `builder` / `shaper` / `guardian` (or tags `BLD` / `SHP` / `GRD`). Combinations allowed |
| `<expertise-level>` | Yes | Expertise level: `L1`-`L5` or aliases `junior` / `mid` / `senior` / `staff` / `lead` |
| `[name]` | No | Name of the new team member for personalization |
| `--area <focus>` | No | Focus area: `backend`, `frontend`, `api`, `auth`, `payments`, etc. |
| `--batch <specs>` | No | Generate multiple onboarding plans in parallel. Semicolon-separated specs |

If arguments are missing (and not in batch mode), ask the user interactively.

## Definitions

Output folder: `${ONBOARDING_PLANS_DIR}/<YYYY-MM-DD>` where `<YYYY-MM-DD>` is the current UTC date.
Filename pattern: `onboarding-<id>-<name-or-role-slug>.md` (6-digit zero-padded ID)

All plans generated on the same date share the same date folder, regardless of role or level. Plans generated on different dates live in different folders, creating a versioned history of onboarding material.

Example directory structure:
```
${ONBOARDING_PLANS_DIR}/
├── 2026-03-28/
│   ├── onboarding-000012-alice-bld-l2.md
│   ├── onboarding-000013-bob-shp-l3.md
│   └── onboarding-000014-grd-l1.md
├── 2026-04-15/
│   ├── onboarding-000021-carol-bld-l1.md
│   └── onboarding-000022-dave-bld+grd-l4.md
```

The sequential ID is globally unique across all artifact types (6-digit, zero-padded). Reserve it by running `python .claude/skills/scripts/reserve_id.py --type onboarding --title '<name-or-role-slug>'` before writing any content.

## Batch Mode

When `--batch` is provided, generate multiple onboarding plans **in parallel** using the Agent tool.

This mode follows the [Batch Execution Pattern](../../../_references/general/batch-execution-pattern.md). See that reference for the canonical 6-phase orchestration pattern. Below are the skill-specific parameters.

### Batch Spec Format

The spec list is a semicolon-separated list of individual onboarding specs:

```
--batch "builder L2 Alice --area backend; shaper L3 Bob; guardian L1; builder+guardian L4 Carol"
```

Each spec follows the same format as the single-plan arguments: `<role-family> <expertise-level> [name] [--area <focus-area>]`.

### Batch Execution

1. Parse the spec list into individual onboarding specs.
2. Run /pre-skill once for the entire batch.
3. Reserve IDs for all specs upfront: `python .claude/skills/scripts/reserve_id.py --type onboarding --title '<name-or-role-slug>'` once per spec.
4. Compute the date folder path: `${ONBOARDING_PLANS_DIR}/<YYYY-MM-DD>` (UTC). Create the folder if it does not exist.
5. Launch one `onboarding-generator` agent per spec in parallel (using the prompt from `.claude/agents/onboarding-generator.md`). Each agent receives:
   - The resolved role tags and level for its spec
   - Role family file path(s) and expertise level file path
   - Project context file paths (conceptual design, conventions)
   - The assigned ID and output file path
   - Name and area if provided
6. Collect results and verify all files were written. On partial failure, the user can re-run `/onboarding` for just the failed specs individually.
7. Run /post-skill once for the entire batch.

### Batch Interaction

If a batch spec is incomplete (e.g., missing level), resolve all incomplete specs with the user before launching any agents.

## Skill-specific Instructions

1. Run /pre-skill "onboarding" $ARGUMENTS to add general instructions to the context window.

2. **Parse arguments and resolve role/level:**

   Map aliases to canonical tags:
   - Role: `builder` -> BLD, `shaper` -> SHP, `guardian` -> GRD
   - Level: `junior` -> L1, `mid` -> L2, `senior` -> L3, `staff` -> L4, `lead` -> L5

   If the role family is not provided or cannot be inferred, use the AskUserQuestion tool to ask (if AskUserQuestion is not available, present as a numbered text list), with these options:
   - "1. Builder (BLD) -- Developer, DevOps, infra engineer"
   - "2. Shaper (SHP) -- Product designer, product manager, UX researcher, analyst"
   - "3. Guardian (GRD) -- QA, security, tech lead, engineering manager"
   - "4. Builder + Guardian -- Tech lead who codes, security-focused developer"
   - "5. Shaper + Builder -- Designer or PM using AI tools directly (writing prompts, reviewing plans, working alongside code)"

   If the expertise level is not provided or cannot be inferred, use the AskUserQuestion tool to ask (if AskUserQuestion is not available, present as a numbered text list), with these options:
   - "1. L1 Newcomer -- Junior, learning fundamentals (0-2 years)"
   - "2. L2 Practitioner -- Mid-level, independent on familiar tasks (2-5 years)"
   - "3. L3 Expert -- Senior, deep expertise, needs trade-off context (5-10 years)"
   - "4. L4 Strategist -- Staff/Principal, cross-cutting influence (10+ years)"
   - "5. L5 Leader -- Tech lead/Manager, owns process and people"

   If in **batch mode**, skip to the Batch Execution flow above.

3. **Determine output path:**

   Compute the date folder: `${ONBOARDING_PLANS_DIR}/<YYYY-MM-DD>` (current UTC date). Create it if it does not exist.
   Reserve the next global ID by running `python .claude/skills/scripts/reserve_id.py --type onboarding --title '<name-or-role-slug>'`. Use the returned 6-digit ID.

4. **Launch generator agent:**

   Launch the `onboarding-generator` agent (Agent tool, subagent_type=`general-purpose`, using the prompt from `.claude/agents/onboarding-generator.md`) with the following context:
   - `role_tags`: the resolved canonical tag(s) (e.g., "BLD", "BLD+GRD")
   - `level`: the resolved level (L1-L5)
   - `name`: the team member's name (if provided)
   - `area`: the focus area (if `--area` was passed)
   - `role_file_paths`: `_references/general/onboarding/<role>.md` for each role tag
   - `level_file_path`: `_references/general/onboarding/<level>.md`
   - `project_context`: paths to `_references/project/conceptual-design-as-is.md`, `_references/project/conventions.md` (or template fallback)
   - `output_path`: the full path computed in step 3
   - `output_id`: the reserved ID from step 3

   After the agent returns, verify that the expected output file exists. Display a brief result summary to the user (role/level, name, output path).

5. Run /post-skill <id>.
