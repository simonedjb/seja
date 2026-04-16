---
name: pending
description: "List and address outstanding human actions from the pending ledger: verify implementations, flip status markers, run periodic curation, manage deferred work."
argument-hint: "[list|add|done|snooze|dismiss] [args]"
compatibility: "Designed for Claude Code with SEJA framework"
metadata:
  last-updated: 2026-04-10 10:00 UTC
  version: 1.0.0
  category: utility
  context_budget: light
  skip_stages: [pending-check, orphan-check, compaction-check, constitution]
  eager_references: []
  references:
    - general/shared-definitions.md
---

## Quick Guide

**What it does**: Shows outstanding human actions the framework is tracking for you (items to verify, markers to flip, proposals to apply, periodic curations), and walks you through addressing them one at a time. The ledger lives at `_output/pending.jsonl` and is append-only, so you can snooze, dismiss, or defer items without losing history.

**Example**:
> You: /pending
> Agent: Lists 3 pending items grouped by type, asks which to address first. For "mark-implemented" items, it runs AskUserQuestion per entry and invokes `apply_marker.py` on confirmed items. For "verify-as-coded" items, it suggests `/explain spec-drift` and waits for you to run `/pending done <id>` once verified.

> You: /pending add --type user-defined --description "review CSRF middleware"
> Agent: Appends a user-defined reminder to the ledger. Pre-skill will surface it at the top of every skill invocation until you mark it done.

> You: /pending done pa-000003
> Agent: Marks pa-000003 as done.

**When to use**: After `/implement` if you chose "Defer for later review" at post-skill, when pre-skill tells you there are pending actions, when the periodic curation trigger has fired, or any time you want to review what the framework is tracking for you.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| (none, or `list`) | No | Interactive: list pending items and dispatch one via AskUserQuestion |
| `add --type <type> --source <id> --description "<text>"` | No | Append a new pending action directly |
| `done <id>` | No | Mark a pending item as done |
| `snooze <id> --until <YYYY-MM-DD>` | No | Snooze an item until a future date |
| `dismiss <id> [--reason <text>]` | No | Dismiss an item without completing it |

# Pending

If the argument begins with `add`, `done`, `snooze`, or `dismiss`, forward the arguments to `python .claude/skills/scripts/pending.py <subcommand> <rest>`, capture the exit code, print the output, then run `/post-skill` and stop.

Otherwise (no argument or `list`):

1. Run `python .claude/skills/scripts/pending.py list --status pending --json`. Parse the JSON output.

2. If the list is empty, print `No pending actions.` and run `/post-skill` and stop.

3. Group items by their `type` field. For each group, present a header with the count (e.g., "mark-implemented (2)") and list the items with their id, source, age, and description.

4. Use `AskUserQuestion` to let the designer pick one item to address, offering for each the options: **Address now**, **Snooze**, **Dismiss**, **Skip**. Plus a top-level "Exit" option.

5. On **Address now**, dispatch based on the `type` field:

   - **mark-implemented**: Parse the `description` and `source` fields to find the target file and candidate entry IDs. For each candidate, run an `AskUserQuestion` confirmation offering `STATUS: implemented` flips. On each confirmation, invoke `python .claude/skills/scripts/apply_marker.py --file <path> --id <entry-id> --marker STATUS --value implemented --plan <source>`. When all candidates are addressed, invoke `pending.py done <id>`.

   - **test-implementation**: Read the plan file at `_output/plans/plan-<source>-*.md`. Extract and display the `## Test plan` section. Print `Run the tests, then /pending done <id>` and return to step 4. Do NOT auto-mark done.

   - **verify-as-coded**: Print `Suggest: /explain spec-drift to compare as-coded vs as-intended, then /pending done <id>`. Do NOT auto-mark.

   - **update-documentation**: Print `Suggest: /document --plan <source>, then /pending done <id>`. Do NOT auto-mark.

   - **apply-promote-proposal**: Print the path `_output/promote-proposals/promote-proposal-plan-<source>.md` and the instructions "Open the proposal, rewrite the draft Decision entries in your voice, copy accepted entries into `product-design-as-intended.md § Decisions` (each under `### D-NNN: Title`), save, then run `/explain spec-drift --promote --apply-markers <source>` to flip the STATUS markers (Phase 3b). Phase 3b will mark this entry done automatically when all proposed entries are present and flipped." Do NOT auto-mark.

   - **apply-promote-markers**: Print "Suggest: `/explain spec-drift --promote --apply-markers <source>` (Phase 3b). Phase 3b heading-only greps `product-design-as-intended.md § Decisions` for each proposed D-NNN, runs per-item AskUserQuestion confirmation, invokes `apply_marker.py` on confirmed items to flip STATUS from `implemented` to `established`, and marks this entry done when every present item was flipped successfully. Legacy uppercase `STATUS: IMPLEMENTED` markers are detected by the widened regex and REPLACED (not stacked)." Do NOT auto-mark.

   - **periodic-curation**: Print "Suggest: run /explain spec-drift to identify promotion candidates, then /explain spec-drift --promote to generate a proposal report. When curation is complete, /pending done <id>". Do NOT auto-mark.

   - **spec-drift-check**: Print "Suggest: /explain spec-drift. When the drift check is complete, /pending done <id>". Do NOT auto-mark.

   - **incorporate-research-markers**: Same marker-flip flow as mark-implemented but with `--marker INCORPORATED`. Target is a ux-research file. Parse candidate entry IDs from description.

   - **user-defined**: Display the description and offer `/pending done <id>` on confirmation. Do NOT auto-mark.

6. On **Snooze**, ask for a date via a text input (or default to +7 days) and invoke `pending.py snooze <id> --until <date>`.

7. On **Dismiss**, ask for an optional reason and invoke `pending.py dismiss <id> [--reason <text>]`.

8. On **Skip**, leave the item and return to step 4 with the remaining items.

9. After dispatching one item, re-run step 1 (list) and return to step 4. Continue until the designer selects **Exit** or the list is empty.

10. On exit, run `/post-skill pending`.

## Notes

- The `skip_stages: [pending-check, ...]` in the frontmatter prevents recursion: without it, running `/pending` would trigger `pending-check` in pre-skill, which would run `pending.py status` at the same time this skill is walking the ledger. Critical stages (brief-log, budget-eval, ref-load) still run.
- All state transitions go through `pending.py` subcommands; this skill never writes to `pending.jsonl` directly.
- Marker flips on `Human (markers)` files go through `apply_marker.py`; this skill never calls `Edit` on those files directly.
