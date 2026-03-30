---
name: onboarding
description: "Generate a tailored onboarding plan for a new team member based on their role and expertise level."
argument-hint: <role-family> <expertise-level> [name] [--area <focus-area>] [--batch <spec-list>]
metadata:
  last-updated: 2026-03-28 18:45:00
  version: 1.0.0
  category: utility
  context_budget: standard
  references:
    - general-onboarding.md
    - project-conceptual-design-as-is.md
    - general-shared-definitions.md
    - general-report-conventions.md
---

## Quick Guide

**What it does**: Creates a personalized onboarding plan for a new team member based on their role and experience level. Covers what to learn, in what order, and where to find things.

**Example**:
> You: $onboarding shaper L2 Alice --area frontend
> Agent: Generates a 30-60-90 day onboarding plan tailored for a mid-level product designer, with focus on the frontend. Includes reading lists, key contacts, and milestone checkpoints.

**When to use**: A new team member is joining and you want a structured, role-appropriate onboarding experience rather than ad-hoc knowledge transfer.

# Onboarding

Generate a tailored onboarding plan for a new project team member.

## Arguments

- `<role-family>`: One of `builder`, `shaper`, `guardian`, or a combination (e.g., `builder+guardian` for a tech lead who codes). Maps to role family tags: BLD, SHP, GRD.
- `<expertise-level>`: One of `L1` (Newcomer/Junior), `L2` (Practitioner/Mid), `L3` (Expert/Senior), `L4` (Strategist/Staff), `L5` (Leader/Manager). Also accepts aliases: `junior`, `mid`, `senior`, `staff`, `lead`.
- `[name]`: Optional name of the new team member (for personalizing the plan).
- `[--area <focus-area>]`: Optional focus area within the project (e.g., `backend`, `frontend`, `api`, `auth`, `payments`).
- `[--batch <spec-list>]`: Generate multiple onboarding plans in parallel. See **Batch Mode** below.

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

The sequential ID is globally unique across all artifact types (6-digit, zero-padded). Reserve it by running `python .codex/skills/scripts/reserve_id.py --type onboarding --title '<name-or-role-slug>'` before writing any content.

## Batch Mode

When `--batch` is provided, generate multiple onboarding plans **in parallel** using the `spawn_agent`.

### Batch Spec Format

The spec list is a semicolon-separated list of individual onboarding specs:

```
--batch "builder L2 Alice --area backend; shaper L3 Bob; guardian L1; builder+guardian L4 Carol"
```

Each spec follows the same format as the single-plan arguments: `<role-family> <expertise-level> [name] [--area <focus-area>]`.

### Batch Execution

1. Parse the spec list into individual onboarding specs.
2. Run $pre-skill once for the entire batch (step 1 of single mode).
3. Reserve sequential IDs for all specs upfront by running `python .codex/skills/scripts/reserve_id.py --type onboarding --title '<name-or-role-slug>'` once per spec.
4. Compute the date folder path: `${ONBOARDING_PLANS_DIR}/<YYYY-MM-DD>` (UTC). Create the folder if it does not exist.
5. Load shared context once: project state (step 4 of single mode) is read once in the parent context and passed to each agent via the prompt.
6. Launch one Agent per spec **in parallel** (all in a single message with multiple `spawn_agent` calls). Each agent receives:
   - The resolved role/level for its spec
   - The pre-loaded shared project context (conceptual design, conventions, etc.)
   - The assigned ID and output file path
   - The full skill instructions for steps 3-5 of single mode (load role/level files, generate plan, save)
7. After all agents complete, collect results and verify all files were written.
8. Run $post-skill once for the entire batch, staging all generated files in a single commit.

### Batch Interaction

If a batch spec is incomplete (e.g., missing level), do NOT launch agents yet. Instead, present all incomplete specs to the user for resolution, then launch all agents at once.

## Skill-specific Instructions

1. Run $pre-skill "onboarding" $ARGUMENTS to add general instructions to the context window.

2. **Parse arguments and resolve role/level:**

   Map aliases to canonical tags:
   - Role: `builder` -> BLD, `shaper` -> SHP, `guardian` -> GRD
   - Level: `junior` -> L1, `mid` -> L2, `senior` -> L3, `staff` -> L4, `lead` -> L5

   If the role family is not provided or cannot be inferred, use the ask the user directly tool to ask (if ask the user directly is not available, present as a numbered text list), with these options:
   - "Builder (BLD) -- Developer, DevOps, infra engineer"
   - "Shaper (SHP) -- Product manager, designer, analyst"
   - "Guardian (GRD) -- QA, security, tech lead, engineering manager"
   - "Builder + Guardian -- Tech lead who codes, security-focused developer"
   - "Shaper + Builder -- Designer using AI tools, full-stack PM"

   If the expertise level is not provided or cannot be inferred, use the ask the user directly tool to ask (if ask the user directly is not available, present as a numbered text list), with these options:
   - "L1 Newcomer -- Junior, learning fundamentals (0-2 years)"
   - "L2 Practitioner -- Mid-level, independent on familiar tasks (2-5 years)"
   - "L3 Expert -- Senior, deep expertise, needs trade-off context (5-10 years)"
   - "L4 Strategist -- Staff/Principal, cross-cutting influence (10+ years)"
   - "L5 Leader -- Tech lead/Manager, owns process and people"

   If in **batch mode**, skip to the Batch Execution flow above.

3. **Determine output path:**

   Compute the date folder: `${ONBOARDING_PLANS_DIR}/<YYYY-MM-DD>` (current UTC date). Create it if it does not exist.
   Reserve the next global ID by running `python .codex/skills/scripts/reserve_id.py --type onboarding --title '<name-or-role-slug>'`. Use the returned 6-digit ID.

4. **Load onboarding content:**

   Based on the resolved role and level:
   a. Load the role family file(s) from `general-onboarding/<role>.md`
   b. Load the expertise level file from `general-onboarding/<level>.md`
   c. If `--area` is provided, scan the codebase for the relevant area to provide concrete file references and examples.

5. **Read project state:**

   To make the onboarding plan concrete and project-specific, **default to the codebase** (i.e., `${BACKEND_DIR}` / `${FRONTEND_DIR}` from conventions) as the scan target — not the workspace root. In workspace deployments these point to the actual source code via absolute paths.

   a. Read `project-conceptual-design-as-is.md` for current system overview.
   b. Read `project-conventions.md` for directory structure and key variables.
   c. If Builder role: scan codebase source directories (`${BACKEND_DIR}`, `${FRONTEND_DIR}`), read relevant coding standards and rules.
   d. If Shaper role: read metacommunication files and conceptual design files.
   e. If Guardian role: read review perspectives and validation scripts inventory.
   f. Check for existing architecture explanations (`${EXPLAINED_ARCHITECTURE_DIR}`), data model explanations (`${EXPLAINED_DATA_MODEL_DIR}`), and behavior explanations (`${EXPLAINED_BEHAVIORS_DIR}`) that can be referenced.

6. **Generate the onboarding plan:**

   The plan must include the following sections:

   ### Header
   `# Onboarding <id> | <role-tag> L<level> | <current datetime> | <name or role description>`

   ### Welcome
   A brief, warm welcome paragraph that:
   - Names the person (if provided)
   - Describes their role in the context of this project
   - Sets expectations for their first weeks

   ### Layer 0 — Universal Foundation (Day 1)
   Project-specific content covering:
   - Project mission and current phase (from conceptual design)
   - Team structure and communication norms (ask user to fill in if not available)
   - Environment setup instructions (concrete steps, not abstract)
   - Project glossary (from `general-shared-definitions.md` + project-specific terms)
   - AI tooling policy and sanctioned tools

   ### Layer 1 — Role-Specific Context (Week 1)
   Drawn from the loaded role family file(s), made concrete with:
   - Actual file paths and references from this project
   - Specific skills and tools relevant to this project's stack
   - Links to existing explanations (from `$explain` outputs) where available

   ### Layer 2 — Level-Specific Depth (Weeks 1-4)
   Drawn from the loaded expertise level file, including:
   - Specific support structure recommendations
   - Concrete first task suggestion based on the project's current state
   - Learning path with project-specific milestones
   - AI-assisted development guidance calibrated to the level

   ### Layer 3 — Living Knowledge (30-60-90 days)
   Pointers to ongoing knowledge sources:
   - Briefs file and plan history for decision context
   - Review perspectives framework for quality standards
   - How to use the skill system for self-service learning (`$explain`, `$advise`, `$advise --inventory`)

   ### 30-60-90 Day Plan
   A concrete timeline with:
   - Specific milestones for each period
   - Checkpoints and who conducts them
   - Success criteria for each milestone

   ### Recommended Reading List
   A curated, prioritized list of files to read, ordered by importance:
   - **Read first** (Day 1): 3-5 essential files
   - **Read this week** (Week 1): 5-10 contextual files
   - **Read this month** (Month 1): Additional deep-dive files

   ### Appendix: Key Contacts
   A placeholder table for team contacts:
   | Role | Name | Contact | Topics |
   |------|------|---------|--------|
   | Buddy/Mentor | _TBD_ | | Day-to-day questions |
   | Tech Lead | _TBD_ | | Architecture, design decisions |
   | Product Owner | _TBD_ | | Requirements, priorities |
   | QA Lead | _TBD_ | | Testing strategy, quality gates |

7. Save the onboarding plan to the date-versioned output folder determined in step 3.

8. Run $post-skill <id>.
