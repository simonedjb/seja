---
name: pre-skill
description: "[Internal] Lifecycle hook invoked by other skills to load references and log briefs. Not intended for direct user invocation."
argument-hint: "<skill-name> <brief>"
user-invocable: false
compatibility: "Designed for Claude Code with SEJA framework"
metadata:
  last-updated: 2026-03-28 12:40 UTC
  version: 1.0.0
  category: internal
  context_budget: standard
  references: []
---

## Stage Catalog

Pre-skill executes as a pipeline of 8 composable stages. Each stage is independently skippable (if non-critical) and error-isolated (if non-critical).

| Stage ID | Name | Critical | Description |
|----------|------|----------|-------------|
| `help` | Help interception | No | Checks for --help flag and displays Quick Guide |
| `brief-log` | Brief logging | Yes | Logs skill invocation to briefs file |
| `orphan-check` | Orphaned-brief detection | No | Detects orphaned STARTED entries |
| `budget-eval` | Context budget evaluation | Yes | Determines context budget tier and loads briefs |
| `compaction-check` | Context compaction warning | No | Warns when session has many skill invocations |
| `pending-check` | Pending actions check | No | Surfaces count of outstanding human actions and runs lazy periodic triggers |
| `ref-load` | Reference file loading | Yes | Loads constitution, conventions, permissions, constraints, and skill-specific references |
| `constitution` | Constitution injection | No | Injects project constitution if it exists |

**Skip mechanism -- `metadata.skip_stages`**

Any skill's SKILL.md frontmatter may include `skip_stages` under the `metadata` block to opt out of non-critical stages during pre-skill execution.

- **Field**: `metadata.skip_stages`
- **Format**: YAML list of stage IDs -- `skip_stages: [stage-id, ...]`
- **Default**: empty list `[]` (all stages run)
- **Allowed values**: only non-critical stage IDs may be listed: `help`, `orphan-check`, `compaction-check`, `pending-check`, `constitution`
- **Critical stage protection**: if a critical stage ID (`brief-log`, `budget-eval`, `ref-load`) appears in `skip_stages`, it is silently ignored -- critical stages always run

Example frontmatter usage:

```yaml
metadata:
  skip_stages: [orphan-check, constitution]
```

This would run all critical stages plus `help`, but skip orphan-check and constitution injection.

**Error isolation**: Non-critical stages are wrapped in error isolation. If a non-critical stage fails, a one-line warning is logged and execution continues to the next stage. Critical stages abort pre-skill on failure.

If "$ARGUMENTS" is empty, ask for the skill name and brief.

# Pre-skill

### Stage: help

**Skip guard**: If `help` is in the calling skill's `metadata.skip_stages`, skip this stage.

**Error isolation**: If this stage encounters an error, log a one-line warning: "Warning: help stage failed: <reason>" and continue to the next stage. Do not abort pre-skill.

Before any other processing, check if the calling skill's arguments contain `--help`. If so:
   a. Read the calling skill's SKILL.md file at `.claude/skills/$ARGUMENTS[0]/SKILL.md`.
   b. Extract and display the `## Quick Guide` section (everything between `## Quick Guide` and the next `#` heading).
   c. If no Quick Guide section exists, display the `description` field from the YAML frontmatter.
   d. **Stop here** -- do not proceed with the remaining pre-skill stages or the calling skill's instructions.

### Stage: brief-log

First, obtain the current UTC time by running `date -u +"%Y-%m-%d %H:%M UTC"` and capturing its output. Use this exact output as `<start-datetime UTC>` below — do not estimate or guess the time.

Without asking for authorization, insert into `${BRIEFS_FILE}` (see project/conventions.md) a new entry as the first entry after the `# Briefs Log` header and its following blank line (i.e., newest entries appear first). Format:
- Format: `STARTED | <start-datetime UTC> | <skill-name> | <brief>`
- Example: `STARTED | 2026-03-19 21:00 UTC | plan | Add user profile page`
- The datetime must be in format `YYYY-MM-DD HH:MM UTC` (obtained from the `date` command above)
- The brief should be exactly what the user wrote, except when it is an error log. In this case, summarize the error in one sentence and use that as the brief, prepended by `ERROR: ` (e.g., "ERROR: Database connection timeout error").
- Ensure the briefs are separated by a blank line
- When completed, post-skill prepends `DONE | <end-datetime UTC> |` and appends `| PLAN | <plan-id>` if applicable

Without asking for authorization, save `${BRIEFS_FILE}` before continuing, so the user can see a log of the requests if the system crashes after this.

### Stage: orphan-check

**Skip guard**: If `orphan-check` is in the calling skill's `metadata.skip_stages`, skip this stage.

**Error isolation**: If this stage encounters an error, log a one-line warning: "Warning: orphan-check stage failed: <reason>" and continue to the next stage. Do not abort pre-skill.

Read `${BRIEFS_INDEX_FILE}` (see project/conventions.md). If it does not exist, generate it by running `python .claude/skills/scripts/generate_briefs_index.py`. Scan the index for entries with status `STARTED` (no matching `DONE`). If any orphaned entries are found (excluding the entry just appended in the brief-log stage), emit a warning: "Warning: N orphaned STARTED entries found in briefs index (no matching DONE). These may be from crashed sessions. Consider reviewing them." Then list the 5 most recent orphaned entries (by date, newest first) in a compact format:
   ```
   - <date> | <skill> | <brief (truncated to 80 chars)>
   ```

### Stage: budget-eval

Read the calling skill's SKILL.md file at `.claude/skills/$ARGUMENTS[0]/SKILL.md` and parse its YAML frontmatter. Determine the **context budget** from `metadata.context_budget` (default: `standard` if not specified).

**Context budget tiers:**

**`light`** -- Skip all briefs and reference file loading. Lightweight skills only need the briefs append (brief-log stage) and orphaned-brief check (orphan-check stage). Skip the ref-load and constitution stages.

**`standard`** (default) -- Load the briefs index (`${BRIEFS_INDEX_FILE}`) instead of the full `${BRIEFS_FILE}`. If the index does not exist, generate it by running `python .claude/skills/scripts/generate_briefs_index.py`. Then proceed to the ref-load stage.

**`heavy`** -- Load `${BRIEFS_FILE}` with **recency windowing**: read only the first 50 entries from the file (newest first). Append a summary line for older entries: "N earlier entries from DATE to DATE, not loaded." Also load the plan index (`${PLANS_DIR}/INDEX.md`). Then proceed to the compaction-check stage.

### Stage: compaction-check

**Skip guard**: If `compaction-check` is in the calling skill's `metadata.skip_stages`, skip this stage.

**Error isolation**: If this stage encounters an error, log a one-line warning: "Warning: compaction-check stage failed: <reason>" and continue to the next stage. Do not abort pre-skill.

Check for context bloat by counting recent skill invocations in the current session:

1. Read `${BRIEFS_FILE}` and count STARTED entries (both orphaned and completed) whose timestamp falls within the last 2 hours. This approximates the number of skill invocations in the current session.
2. If the count exceeds the threshold (default: 8 invocations), emit a warning:
   > "Warning: Context may be getting heavy after N skill invocations in this session. Consider starting a fresh conversation for best results, or use the session scratchpad (`${TMP_DIR}/session-notes.md`) to persist key decisions before starting a new session."
3. If the count is below the threshold, proceed silently.

This stage is advisory-only -- it warns but does not block or auto-compact. Future phases may add automatic compaction.

### Stage: pending-check

**Skip guard**: If `pending-check` is in the calling skill's `metadata.skip_stages`, skip this stage.

**Error isolation**: If this stage encounters an error, log a one-line warning: "Warning: pending-check stage failed: `<reason>`" and continue to the next stage. Do not abort pre-skill.

Surface outstanding human actions from the pending ledger and run lazy periodic triggers. Single subprocess call (per plan-000265 amendment A8 -- collapsed from three invocations to one to stay under the <150ms per-skill budget).

1. Run `python .claude/skills/scripts/pending.py status --overdue-days 14 --json` once. The `status` subcommand internally performs conditional cleanup (throttled by a 24h stamp in `${OUTPUT_DIR}/.pending-cleanup-stamp`), conditional periodic-check (throttled by a 1h stamp in `${OUTPUT_DIR}/.pending-periodic-stamp`), and a list reduction. It always exits 0 unless a cleanup or periodic-check write fails (in which case the JSON `warnings` field is populated but exit is still 0).

2. Parse the JSON output: `{"count": N, "overdue_count": M, "top_3": [{"type": ..., "source": ..., "age_days": ..., "description": ...}, ...], "warnings": [...]}`.

3. Emit based on the counts:
   - `count == 0`: silent.
   - `1 <= count <= 5 and overdue_count == 0`: one-line notice `You have N pending actions (run /pending to view).`
   - `count > 5 or overdue_count > 0`: warning block with header `You have N pending actions (M overdue). Top 3 by age:` followed by three indented lines from `top_3`, each showing action type, source artifact, age in days, and description truncated to 80 chars.

4. Never block the skill invocation; this stage is purely informational.

### Stage: ref-load

Load reference files (applies to standard and heavy tiers only):

Always include:
- Read and inject `_references/project/conventions.md`. If it does not exist, read and inject `_references/template/conventions.md` instead.
- Read and inject `_references/general/permissions.md`
- Read and inject `_references/general/constraints.md`

**Dynamic reference loading:**

Pre-skill supports two reference-loading modes: **eager-only** (legacy default) and **demand-pull** (two-tier). The mode is determined by whether the calling skill declares `metadata.eager_references`.

**Mode 1 -- Eager-only (no `eager_references` field):**
If the frontmatter contains a `metadata.references` list but no `metadata.eager_references`, read and inject every file in the `references` list from `_references/`. This is the legacy behavior.
An empty list (`references: []`) is valid -- it means the skill intentionally loads no additional references (e.g., orchestration or utility skills).

**Mode 2 -- Demand-pull (`eager_references` field present):**
When the calling skill's frontmatter contains `metadata.eager_references` (a list of reference paths):
1. **Eager tier** -- read and inject each file listed in `eager_references` from `_references/`. These are always loaded upfront alongside the mandatory refs (conventions, permissions, constraints).
2. **Lazy tier** -- the remaining entries in `metadata.references` that are NOT in `eager_references` become available on demand. Emit an "Available references" block (see below) listing each lazy ref so the skill body can request them when needed. Do NOT read or inject lazy refs at this stage.

An empty `eager_references: []` is valid -- it means all skill-specific references are lazy (only mandatory refs are loaded upfront).

**Available references block (demand-pull mode only):**
After loading eager refs, emit a compact block listing each lazy reference with its path and a trigger hint:

```
--- Available references (load when needed) ---
1. <path> -- load before <trigger hint>
2. <path> -- load before <trigger hint>
...
To load: read and inject the file from _references/<path>.
---
```

Trigger hints are short phrases describing when the reference is useful (e.g., "reviewing security concerns", "writing frontend code"). Derive the hint from the filename and subdirectory (e.g., `project/security-checklists.md` -> "reviewing security concerns", `project/standards.md` -> "writing backend, frontend, testing, or i18n code").

If the calling skill's SKILL.md **does not** contain a `metadata.references` field at all, log a warning: "Skill <name> has no metadata.references -- cannot load skill-specific references." All skills are expected to declare their references in frontmatter.

### Stage: constitution

**Skip guard**: If `constitution` is in the calling skill's `metadata.skip_stages`, skip this stage.

**Error isolation**: If this stage encounters an error, log a one-line warning: "Warning: constitution stage failed: <reason>" and continue to the next stage. Do not abort pre-skill.

Read and inject `_references/project/constitution.md`. If it does not exist, skip silently (constitution is optional for backwards compatibility with projects that haven't generated one yet).

### Util scripts

- When planning, check `${SCRIPTS_DIR}` (see project/conventions.md) for useful scripts.
