---
name: generate-script
description: "Generate a helper Python script according to the brief."
argument-hint: <brief>
metadata:
  last-updated: 2026-03-25 22:15:00
  version: 1.0.0
  category: code
  context_budget: standard
  references:
    - general-report-conventions.md
    - general-coding-standards.md
---

## Quick Guide

**What it does**: Creates a helper Python script based on your description. Useful for one-off tasks like data migration, report generation, or automating a repetitive step.

**Example**:
> You: /generate-script Create a script that reads all plan files and generates a summary table with plan ID, title, date, and status
> Agent: Writes a Python script with argument parsing, file reading logic, and formatted output. Saves it to the scripts directory.

**When to use**: You need a utility script for a specific task — data processing, file generation, validation, or any repetitive operation you want to automate.

# Generate script

If there are no arguments, ask for a user brief.

## Definitions

Output folder: `${SCRIPTS_DIR}` (see project-conventions.md)
Filename pattern: `<descriptive-slug>.py` (scripts use descriptive names, not sequential IDs)

The sequential ID is globally unique across all artifact types (6-digit, zero-padded). Reserve it by running `python .claude/skills/scripts/reserve_id.py --type script --title '<descriptive-slug>'` before writing any content. The ID is used in the script's header comment and in the global artifact index, not in the filename.

## Skill-specific Instructions

1. Run /pre-skill "generate-script" $ARGUMENTS[0] to add general instructions to the context window.

2. Reserve a global ID by running `python .claude/skills/scripts/reserve_id.py --type script --title '<descriptive-slug>'`. Use the returned 6-digit ID in the script's header documentation.

3. Write a deterministic script according to the brief. If it cannot be deterministic (i.e., depends on agents), inform why and stop.

4. Document the script with *id*, *current datetime*, *user brief*, *agent interpretation* -- per .agent-resources/general-report-conventions.md.

5. Run /post-skill <id>.