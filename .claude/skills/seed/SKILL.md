---
name: seed
description: "Copy the SEJA framework into a new or existing project, or create a workspace alongside an existing codebase."
argument-hint: "<target-directory> [--workspace]"
metadata:
  last-updated: 2026-03-31 16:30:00
  version: 1.0.0
  category: utility
  context_budget: light
  references: []
---

## Quick Guide

**What it does**: Copies the SEJA framework files into a target directory. For greenfield projects, creates the directory and initializes git. For existing codebases, embeds the framework alongside existing code. With `--workspace`, creates a separate workspace directory.

**Example**:
> You: /seed /path/to/my-project
> Agent: Detects the scenario (greenfield/existing/workspace), copies all framework files, and tells you to run `/design` next.

**When to use**: You are setting up SEJA in a new or existing project for the first time. Use `/upgrade` instead if the project already has SEJA and you want to update the framework version.

# Seed

> **`/seed`** copies the framework. **`/design`** defines WHAT to build and WHY. **`/make-plan`** defines HOW to build it and WHY those "hows."

## Overview

This skill copies the SEJA framework from the seed repo into a target project directory. It handles only mechanical distribution — no project-specific configuration decisions are made here. After seeding, the user continues from the target project with `/design`.

## Distribution Model

SEJA follows a **copy-and-continue** (seed repo) model:

- **This project is a seed repo** — it is the source of the framework, used for development and distributing updates via GitHub. It is NOT a runtime dependency for target projects.
- **`/seed` copies the framework into the target project**, where all skills, rules, agents, and references become self-contained.
- **After seeding, the user continues working from the target project**, not from this repo. All skills (`/design`, `/make-plan`, `/execute-plan`, `/advise`, etc.) operate on the project they live in.
- **Return to this repo only** to develop framework improvements. To bootstrap a new project, clone the repo and run `/seed`. To upgrade an existing project, use `/upgrade` from the target project or re-seed with "overwrite framework only".

## Steps

1. **Accept target directory**: If not provided as an argument, ask the user for the target path.

2. **Detect scenario**: Inspect the target path to determine the starting point:

   | Scenario | Detection | Action |
   |----------|-----------|--------|
   | **Greenfield** | Target does not exist | Create directory (do NOT `git init` yet — workspace routing in step 2b decides) |
   | **Empty project** | Target exists, is a git repo, no source code | Proceed to copy |
   | **Existing codebase** | Target exists, is a git repo, has source code | Proceed to copy (framework embeds alongside code) |
   | **Not a git repo** | Target exists but is not a git repo | Offer to run `git init`, or abort |

   If a `.claude/` directory already exists in the target, warn the user and offer three options:
   - **Overwrite framework only** (recommended for upgrades) — overwrite skills, `general/` references, `template/` references, scripts, agents, and rules. **Never touch** `project/` references, `settings.json`, `settings.local.json`, the output directory, or `CLAUDE.md`.
   - **Overwrite everything** — full re-seed (destructive, requires confirmation)
   - **Abort**

2b. **Workspace routing** (if `--workspace` flag or user chooses workspace mode):
   - **Greenfield**: Ask for workspace and codebase directory names. Create both as subdirectories. `git init` each. Redirect framework files to workspace dir.
   - **Brownfield**: Ask for workspace directory path. Detect embedded framework files in codebase. Offer to migrate SEJA files to workspace. Create workspace dir and `git init` it.
   - **No separation**: `git init` the target if not already a repo. Proceed with standard in-place setup.
   - Generate launcher scripts (`launch.sh` / `launch.bat`) that invoke `claude --add-dir <codebase-dir>`.

3. **Create directory structure**: Create the following in the target (or workspace) directory:
   ```
   _references/
   _references/general/
   _references/template/
   _references/project/
   .claude/
   .claude/skills/
   .claude/skills/scripts/
   .claude/rules/
   .claude/agents/
   ```

4. **Copy framework files** from this project to the target:
   - All files under `_references/general/` (as-is)
   - All files under `_references/template/` (consumed by `/design`)
   - `template/settings.json`
   - All skill `SKILL.md` files (project-independent)
   - All agent definitions (`.claude/agents/*.md`)
   - All rule definitions (`.claude/rules/*.md`)
   - All validation scripts (`.claude/skills/scripts/*.py`)
   - `.claude/CHANGELOG.md`, `.claude/CHEATSHEET.md`, `.claude/skills/VERSION`

5. **Create output directory**: Create the output directory (default: `_output/`) with:
   - Empty `briefs.md` with header: `# Briefs\n\nExecution log of all skill invocations.\n\n---\n`
   - Subdirectories: `plans/`, `advisory-logs/`, `qa-logs/`, `check-logs/`

6. **Create settings.json**: Copy `template/settings.json` to `.claude/settings.json` in the target, with default path values.

7. **Summary**: Report what was copied (file count by category).

8. **Handoff**:
   > Your project has been seeded at `<target>`. Next steps:
   >
   > 1. Open a new Claude Code session in `<target>` (or workspace directory if separated)
   > 2. Run `/design` to configure the framework for your project
   > 3. This seed repo is no longer needed for day-to-day work — return to it only for framework development
