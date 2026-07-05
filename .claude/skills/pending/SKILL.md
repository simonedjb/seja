---
name: pending
description: "List and address outstanding human actions from the pending ledger: verify implementations, flip status markers, run periodic curation, manage deferred work."
argument-hint: "[list|address <id>|add|done|snooze|dismiss] [args]"
compatibility: "Designed for Claude Code with the SEJA harness"
metadata:
  last-updated: 2026-04-27 22:00 UTC
  version: 1.0.0
  category: utility
  context_budget: light
  skip_stages: [pending-check, orphan-check, compaction-check, constitution]
  eager_references: []
  references:
    - general/shared-definitions.md
---

> Overview: see [./SKILL-quickguide.md](./SKILL-quickguide.md)

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| (none, or `list`) | No | List all pending items with per-item recommendation, then stop |
| `address <id>` | No | Run the guided resolution workflow for a specific item (marker flips, confirmation prompts) |
| `add --type <type> --source <id> --description "<text>"` | No | Append a new pending action directly |
| `done <id>` | No | Mark a pending item as done |
| `snooze <id> --until <YYYY-MM-DD>` | No | Snooze an item until a future date |
| `dismiss <id> [--reason <text>]` | No | Dismiss an item without completing it |

# Pending

0. Run /pre-skill "pending" $ARGUMENTS[0] to add general instructions to the context window.

If the argument begins with `add`, `done`, `snooze`, or `dismiss`, forward the arguments to `python .claude/skills/scripts/pending.py <subcommand> <rest>`, capture the exit code, print the output, then run `/post-skill` and stop.

If the argument begins with `address`, go to [Address dispatch](#address-dispatch).

If there is no argument or `list`:

1. Run `python .claude/skills/scripts/pending.py list --status pending --json`. Parse the JSON output.

2a. If empty list: print `No pending actions.` and run `/post-skill` and stop.

2b. If non-empty list: group items by `type`. For each group, print a header with the count (e.g., "**implement** (2)"). For each item in the group, print:

   - `<id>` -- `<type>` -- source: `<source>` -- age: N days
     > `<description>` (omit this line if `description` is empty or null)
     - **How to resolve**:
       1. Render the type-specific resolution steps from the table below, substituting `<id>` and `<source>` with real values.
       2. When `<source>` references a plan (starts with `plan-`), resolve it to the actual file path by globbing `_output/plans/plan-<NNN>-*.md` (exclude `-progress.md` and `-qa-*.md` siblings) and include the path in the instructions.
       3. For `user-defined` items, the `description` field IS the instruction — reproduce it verbatim as the resolution steps (it already contains what to do).
       4. Every resolution block must end with the exact `/pending` subcommand that closes the item.
   <blank line>

   After all groups, print the action footer:

   ```
   --- To act on items ---
     /pending address <id>                     -- run the guided resolution for this item
     /pending done <id>                        -- mark as completed
     /pending snooze <id> --until YYYY-MM-DD   -- defer until a future date
     /pending dismiss <id> --reason "..."      -- dismiss without completing
   ```

3. Run `/post-skill pending` silently (without outputting intermediate actions) and stop.

### Type-specific resolution steps

For each type below, render these steps literally in the output (replacing `<id>`, `<source>`, and `<plan-file>` with actual values). Include the resolved plan file path where indicated.

**`implement`**
1. Open the plan file: `_output/plans/<plan-file>`
2. Run `/implement <source>` to execute the plan
3. The entry auto-closes when the plan's `# DONE | ...` header is written — no manual `/pending done` needed

**`mark-implemented`**
1. Run `/pending address <id>` — this launches the interactive marker-flip workflow
2. It will walk you through each candidate entry, confirming STATUS → implemented flips
3. The item auto-closes when all candidates are addressed

**`test-implementation`**
1. Open the plan file: `_output/plans/<plan-file>`
2. Find the `## Test plan` or `Tests:` section in the plan
3. Execute each test condition described there (manually or via test commands)
4. Run `/pending done <id>` when all tests pass

**`verify-as-coded`**
1. Run `/explain drift` to compare product-design-as-coded.md against product-design-as-intended.md
2. If drift is found, update the as-coded file to reflect current implementation
3. Run `/pending done <id>`

**`update-documentation`**
1. Run `/document --plan <source>` to generate or update docs for this plan
2. Review the generated output in `_output/docs/`
3. Run `/pending done <id>`

**`apply-promote-markers`**
1. Open `_output/promote-proposals/promote-proposal-plan-<source>.md`
2. Review the draft Decision entries; rewrite in your own voice if needed
3. Copy finalized entries into product-design-as-intended.md § Decisions
4. Run `/explain drift --promote --apply-markers <source>` — this flips STATUS markers and auto-closes the pending entry

**`spec-drift-check`**
1. Run `/explain drift` to surface mismatches between design intent and as-coded state
2. If STATUS items are ready for promotion, follow up with `/explain drift --promote`
3. Run `/pending done <id>`

**`periodic-curation`**
1. Run `/pending list` (this invocation) to see all open items
2. Dismiss stale items: `/pending dismiss <id> --reason "..."`
3. Snooze items not yet actionable: `/pending snooze <id> --until YYYY-MM-DD`
4. Run `/pending done <id>` for the curation entry itself when triage is complete

**`incorporate-research-markers`**
1. Run `/pending address <id>` — this launches the interactive INCORPORATED marker-flip workflow
2. It will walk you through each research finding, confirming INCORPORATED flips in the UX research file
3. The item auto-closes when all candidates are addressed

**`review-downstream-plan`**
1. Open the plan files referenced in `<source>` and in the `description`
2. Check whether changes from `<source>` invalidated assumptions in the downstream plan
3. If drifted, revise via `/plan` (or dismiss if the downstream plan is obsolete)
4. Run `/pending done <id>`

**`create-decision-entry`**
1. Draft a `### D-NNN:` entry following the DDR shape (Context, Decision, Rationale, Consequences, Alternatives)
2. Append it to product-design-as-intended.md § Decisions
3. Run `/pending done <id>`

**`check-git-freshness`**
1. Run `/critique freshness` to compare local branches to their upstreams
2. If behind, pull or rebase as appropriate
3. Run `/pending done <id>`

**`reflect-on-practice`**
1. Run `/reflect` to review patterns from recent sessions
2. Run `/pending done <id>`

**`follow-up-plan`**
1. Read the description — it contains the plan scope and rationale
2. Run `/plan` with the described scope to create the follow-up plan
3. Run `/pending done <id>` (the new plan will file its own `implement` entry)

**`user-defined` / unknown**
1. Follow the instructions in the `description` field verbatim — it contains the complete action specification
2. Run `/pending done <id>` when the described action is complete

### Address dispatch

When invoked as `/pending address <id>`:

1. Run `python .claude/skills/scripts/pending.py list --status pending --json`. Find the item matching `<id>`. If not found or not pending, print an error and stop.

2. Dispatch based on the item's `type` field:

   - **mark-implemented**: Parse the `description` and `source` fields to find the target file and candidate entry IDs. For each candidate, run an `AskUserQuestion` confirmation offering `STATUS: implemented` flips. On each confirmation, invoke `python .claude/skills/scripts/apply_marker.py --file <path> --id <entry-id> --marker STATUS --value implemented --plan <source>`. When all candidates are addressed, invoke `pending.py done <id>`.

   - **incorporate-research-markers**: Same marker-flip flow as mark-implemented but with `--marker INCORPORATED`. Target is a ux-research file. Parse candidate entry IDs from description. When all candidates are addressed, invoke `pending.py done <id>`.

   - **All other types**: Print the type-specific resolution steps from the section above, fully substituted with the item's real `<id>`, `<source>`, and resolved `<plan-file>` path. These types resolve via external commands, not via internal dispatch. Include the exact skill commands (with options and arguments) and resolved file paths. Then stop.

3. Run `/post-skill pending` and stop.

## Notes

- The `skip_stages: [pending-check, ...]` in the frontmatter prevents recursion: without it, running `/pending` would trigger `pending-check` in pre-skill, which would run `pending.py status` at the same time this skill is walking the ledger. Critical stages (brief-log, budget-eval, ref-load) still run.
- All state transitions go through `pending.py` subcommands; this skill never writes to `pending.jsonl` directly.
- Marker flips on `Human (markers)` files go through `apply_marker.py`; this skill never calls `Edit` on those files directly.
- **Source-based shortcut**: `pending.py done --source <id> --type <type>` closes all matching open entries in one call. Used when `/implement` writes the `# DONE | ...` header and by post-skill's safety net. Idempotent: no-op when no open entry matches.
- **Uniqueness invariant for implement**: a plan's `implement` entry is filed via `pending.py add --if-absent` so the (source, type) pair is unique under the script's atomicity (no agent-level race). Running `/plan` re-runs or post-skill checkpoint recovery do not duplicate entries.
- **Orphan cleanup for implement**: `pending.py cleanup` (24h-throttled) auto-dismisses `implement` entries whose plan file has been deleted from `_output/plans/`. Leftover `-progress.md` / `-qa-*.md` siblings do not mask a deletion. Dismissal reason: `plan file deleted`.
