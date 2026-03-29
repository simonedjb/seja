---
name: help
description: "Show contextual help, browse skills by category, or get details on a specific skill."
argument-hint: "[skill-name | --browse] [--details]"
metadata:
  last-updated: 2026-03-29 00:15:00
  version: 1.0.0
  category: utility
  context_budget: light
  references: []
---

## Quick Guide

**What it does**: Shows what skills are available and explains what each one does. Browse by category to discover skills, or get details on a specific one.

**Example**:
> You: $help advise
> Agent: Displays a plain-language summary of what $advise does, with an example interaction and when to use it.

> You: $help --browse
> Agent: Shows skill categories (Planning, Analysis, Code, Utilities) with counts. You pick a category, then a skill, and the agent runs it.

**When to use**: You want to know what the framework can do, need details about a specific skill, or want to browse and pick a skill interactively.

# Help

## Skill-specific Instructions

This skill provides four layers of progressive disclosure depending on the arguments provided.

### Layer 1: No argument - Overview

When invoked without arguments (`$help`), display a curated overview of all user-facing skills organized by designer workflow. Present the categories to the user and let them pick one to explore further.

**Categories and skills:**

- **Getting started** - `$quickstart`, `$help`
- **Design & plan** - `$advise`, `$make-plan`, `$execute-plan`
- **Understand the system** - `$explain`
- **Quality & review** - `$check`
- **Communicate** - `$communication`, `$onboarding`
- **Code & tests** - `$generate-script`, `$update-tests`
- **Housekeeping** - `$qa-log`

For each category, show the skill names and a one-sentence summary. After displaying the overview, ask: "Want details on a specific skill? Just say its name."

### Layer 2: With skill name - Quick Guide

When invoked with a skill name (`$help advise`):

1. Read the target skill's SKILL.md file at `.codex/skills/<skill-name>/SKILL.md`.
2. Extract and display the `## Quick Guide` section (What it does, Example, When to use).
3. If no Quick Guide section exists, fall back to the `description` field from the YAML frontmatter.
4. After displaying, ask: "Want more details? Say `$help <skill-name> --details`."

### Layer 3: With --details flag - Full details

When invoked with `--details` (`$help advise --details`):

1. Display the Quick Guide (same as Layer 2).
2. Additionally show:
   - **Arguments**: The full argument syntax from the `argument-hint` field in frontmatter.
   - **Category**: The skill's `metadata.category` value.
   - **Related skills**: Look up the skill in `.agent-resources/general-skill-graph.md` and show which skills are suggested after this one, and which skills suggest this one as a follow-up.
3. After displaying, ask: "Ready to use this skill? Just type the command."

### Layer 4: With --browse flag - Interactive Browse

When invoked with `--browse` (`$help --browse`), or when the user says "pick prompt", "pick skill", or "prompt menu":

1. Scan the `.codex/skills/` directory for all subdirectories containing a `SKILL.md` file. For each, read the `name` and `description` fields from the YAML frontmatter. Exclude internal lifecycle hooks (`pre-skill`, `post-skill`) from the menu. If a SKILL.md cannot be parsed, log a warning and skip it.

2. Group the discovered skills by their `metadata.category` field:

   | Category value | Display label |
   |---------------|---------------|
   | `planning` | Planning & Execution |
   | `analysis` | Analysis & Review |
   | `code` | Code & Tests |
   | `utility` | Utilities |

   Exclude skills with `category: internal` from the menu. If a skill has no `category` field, place it in **Utilities** as a fallback.

3. If an argument is provided (other than `--browse`), attempt to match it to one of the available skills. If you find up to 4 matches, present the options to the user and let them choose what to execute.

4. Otherwise, show ONE question with the category options (with a count of skills in each). Then show the skills in the chosen category with their descriptions.

5. After the user picks a specific skill, ask what arguments to pass (if the skill has an `argument-hint`), then execute the corresponding skill command.
