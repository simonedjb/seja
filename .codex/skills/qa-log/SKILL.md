---
name: qa-log
description: "Log the entire current Q&A session into a file for future reference."
argument-hint: brief or topic
metadata:
  last-updated: 2026-03-27 00:00:00
  version: 1.0.0
  category: utility
  context_budget: light
---

## Quick Guide

**What it does**: Saves the current conversation (questions and answers) to a file for future reference. Useful for documenting decisions and rationale.

**Example**:
> You: $qa-log Design decisions for the notification system
> Agent: Captures the full Q&A exchange from this session and saves it as a timestamped file you can reference later.

**When to use**: You have had a productive conversation with useful decisions or insights and want to preserve it as project documentation.

# Log QA

Logs the entire current Q&A session (all user prompts and agent responses) into `${QA_LOGS_DIR}` (see project/conventions.md).

If an argument is provided, use it as the short title for the log file. If no argument is provided, derive a short title from the conversation topic.

## Definitions

Output folder: `${QA_LOGS_DIR}` (see project/conventions.md)
Filename pattern: `qa-<id>-<truncated short title slug>.md`

The sequential ID is globally unique across all artifact types (6-digit, zero-padded). In standalone mode, reserve it by running `python .codex/skills/scripts/reserve_id.py --type qa --title '<slug>'` before writing any content.

## Caller overrides

When invoked by another skill (e.g., post-skill), the caller may provide overrides for the defaults above. The following overrides are supported:

- **output_dir**: Write the QA file to this directory instead of `${QA_LOGS_DIR}`.
- **filename**: Use this exact filename instead of the default `qa-<id>-<slug>.md` pattern. When provided, skip the ID reservation (step 1) and slug generation (step 2) -- use the filename as-is. The caller is responsible for ensuring the filename uses 6-digit zero-padded IDs derived from the parent artifact (e.g., `advisory-000015-qa-topic.md`).
- **no_commit**: If true, skip the stage-and-commit step (step 6). The caller is responsible for committing.

When no overrides are provided, all defaults apply (standalone behavior).

**Important**: The `<current datetime>` field in the header (step 4) is NEVER overridden -- it must always be present regardless of which overrides are active. This ensures every QA log is indexable by date.

## Skill-specific Instructions

1. Reserve the next global ID by running `python .codex/skills/scripts/reserve_id.py --type qa --title '<slug>'`. Use the returned 6-digit zero-padded ID. *Skip if `filename` override is provided.*

2. Generate a short title slug from the argument or, if no argument was provided, from the main topic of the conversation. *Skip if `filename` override is provided.*

3. Capture the full Q&A session from the current conversation: all user prompts and all agent responses, in chronological order.

4. Save to `<output_dir>/<filename>` (using overrides or defaults) with:
   - **Header** (standalone mode): `# QA <id> | <current datetime> | <short title>` (datetime in `YYYY-MM-DD HH:mm:ss UTC` format)
   - **Header** (with `filename` override): `# QA Log | <parent-type> <parent-id> | <current datetime> | <short title>` (datetime in `YYYY-MM-DD HH:mm:ss UTC` format). The `<parent-type>` and `<parent-id>` are derived from the filename (e.g., `advisory-000058-qa-...` means parent-type is "Advisory" and parent-id is "000058").
   - **Brief**: A one-line summary of what the session was about. If the user provided an argument, use that as the brief. If not, generate a brief based on the conversation topic and make the session title Brief Summary instead of Brief.
   - **Q&A Log**: Numbered exchanges using the format:
     ```
     ## Q1
     <user prompt>

     ## A1
     <agent response summary or full response>

     ## Q2
     ...
     ```
   - For lengthy agent responses (e.g., code generation, plan execution), summarize the action taken rather than reproducing the full output.

5. Output a link to the generated file.

6. Stage and commit the generated file with a message like `Log QA session: <brief or topic>`. *Skip if `no_commit` override is true.*
