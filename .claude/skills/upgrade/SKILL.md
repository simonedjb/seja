---
name: upgrade
description: "Upgrade SEJA framework files from the seed repo without touching project-specific files. Use when user mentions 'upgrade', 'upgrade framework', 'update framework', or 'pull framework updates'."
argument-hint: "[<seed-repo-path>] [--dry-run]"
compatibility: "Designed for Claude Code with SEJA framework"
metadata:
  last-updated: 2026-03-31 16:30 UTC
  version: 1.0.0
  category: utility
  context_budget: light
  references: []
---

## Quick Guide

**What it does**: Upgrades your project's SEJA framework files to the latest version from the seed repo. Preserves all project-specific files (design, conventions, output). Shows a summary of changes before applying.

**Example**:
> You: /upgrade
> Agent: Clones the latest SEJA repo, runs the upgrade script, shows version change and what was updated, offers follow-up actions.

**When to use**: When the SEJA framework has been updated and you want to pull the latest skills, references, scripts, and agents into your project without losing your project-specific configuration.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `[seed-repo-path]` | No | Path to the local seed repo. If omitted, clones the public repo |
| `--dry-run` | No | Preview upgrade changes without applying them |

# Upgrade

> **`/seed`** copies the framework (initial). **`/upgrade`** updates the framework (ongoing). Both preserve project-specific files.

## Overview

This skill upgrades the SEJA framework files in the current project from the seed repo. It runs from the **target project** (not the seed repo). It applies safe updates to project-independent files while preserving all project-specific customizations.

## File Classification

| Category | Files | Safe to overwrite? | Action |
|----------|-------|-------------------|--------|
| **Skills** | `.claude/skills/*/SKILL.md` | Yes — project-independent | Auto-update |
| **General references** | `_references/general/*.md` | Yes — framework standards | Auto-update |
| **Templates** | `_references/template/**` | Yes — consumed by `/design` | Auto-update |
| **Scripts** | `.claude/skills/scripts/*.py` | No — contain hardcoded project paths | Show diff, manual merge |
| **Agents** | `.claude/agents/*.md` | Mostly — may have local tweaks | Show diff, ask per file |
| **Rules** | `.claude/rules/*.md` | No — contain project-specific conventions | Show diff, manual merge |
| **Framework metadata** | `.claude/CHANGELOG.md`, `VERSION`, `CHEATSHEET.md` | Yes | Auto-update |
| **Project definitions** | `_references/project/**` | Never | Skip |
| **Settings** | `.claude/settings.json`, `settings.local.json` | Never | Skip |
| **Output directory** | `_output/` (or configured output dir) | Never | Skip |
| **CLAUDE.md** | `CLAUDE.md` | Never | Skip |

## Steps

1. **Locate seed repo**: If a path is provided as argument, use it. Otherwise, attempt to clone the public SEJA repo: `git clone --depth 1 https://github.com/simonedjb/seja <temp-dir>`. If clone fails, ask the user for a local path.

2. **Validate seed repo**: Check that the seed path contains `.claude/skills/` with skill definitions and `_references/` with reference files.

3. **Read current project conventions**: Read `project/conventions.md` to determine the output directory name and other project-specific paths.

4. **Run the upgrade script**: Execute `python .claude/skills/scripts/upgrade_framework.py --from <seed-path> --target .`. If the user wants a preview first, add `--dry-run`.

5. **Review the summary**: Present the script's output. Highlight:
   - Version change (e.g., "1.0.0 → 2.0.0")
   - Whether old layout migration occurred
   - New convention variables available
   - Files auto-updated vs files needing manual merge

6. **Show diffs for manual-merge files**: For each script, rule, and agent that differs:
   - Show a unified diff
   - For agents: ask "Accept seed version / Keep current / Show diff?" per file
   - For scripts and rules: show the diff and advise on merging

7. **Offer follow-up actions**:
   - If new convention variables were found: "Would you like to add these to your `project/conventions.md`?"
   - If old path references were found: "Would you like me to update the references?"
   - If CLAUDE.md needs refresh: "Would you like to regenerate your CLAUDE.md?"

8. **Clean up**: Remove the temporary clone directory if one was created.

9. **Post-upgrade summary**:
   > Upgrade complete.
   >
   > - N files auto-updated
   > - N files need manual merge (diffs shown above)
   > - N new files added
   >
   > Run `git diff` to review all changes before committing.
