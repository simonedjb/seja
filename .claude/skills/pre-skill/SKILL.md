---
name: pre-skill
description: "[Internal] Lifecycle hook invoked by other skills to load references and log briefs. Not intended for direct user invocation."
argument-hint: <skill-name> <brief>
user-invocable: false
metadata:
  last-updated: 2026-03-28 12:40:00
  version: 1.0.0
  category: internal
  context_budget: standard
---

If "$ARGUMENTS" is empty, ask for the skill name and brief.

# Pre-skill

0. **`--help` interception**: Before any other processing, check if the calling skill's arguments contain `--help`. If so:
   a. Read the calling skill's SKILL.md file at `.claude/skills/$ARGUMENTS[0]/SKILL.md`.
   b. Extract and display the `## Quick Guide` section (everything between `## Quick Guide` and the next `#` heading).
   c. If no Quick Guide section exists, display the `description` field from the YAML frontmatter.
   d. **Stop here** — do not proceed with the remaining pre-skill steps or the calling skill's instructions.

1. Without asking for authorization, insert into `${BRIEFS_FILE}` (see project-conventions.md) a new entry as the first entry after the `# Briefs Log` header and its following blank line (i.e., newest entries appear first). Format:
- Format: `STARTED | <start-datetime UTC> | <skill-name> | <brief>`
- Example: `STARTED | 2026-03-19 21:00:00 UTC | make-plan | Add user profile page`
- The datetime must be in format `YYYY-MM-DD HH:mm:ss UTC`
- The brief should be exactly what the user wrote, except when it is an error log. In this case, summarize the error in one sentence and use that as the brief, prepended by `ERROR: ` (e.g., "ERROR: Database connection timeout error").
- Ensure the briefs are separated by a blank line
- When completed, post-skill prepends `DONE | <end-datetime UTC> |` and appends `| PLAN | <plan-id>` if applicable

2. Without asking for authorization, save `${BRIEFS_FILE}` before continuing, so the user can see a log of the requests if the system crashes after this.

3. **Orphaned-brief detection**: Read `${BRIEFS_INDEX_FILE}` (see project-conventions.md). If it does not exist, generate it by running `python .claude/skills/scripts/generate_briefs_index.py`. Scan the index for entries with status `STARTED` (no matching `DONE`). If any orphaned entries are found (excluding the entry just appended in step 1), emit a warning: "Warning: N orphaned STARTED entries found in briefs index (no matching DONE). These may be from crashed sessions. Consider reviewing them." Then list the 5 most recent orphaned entries (by date, newest first) in a compact format:
   ```
   - <date> | <skill> | <brief (truncated to 80 chars)>
   ```

4. Read the calling skill's SKILL.md file at `.claude/skills/$ARGUMENTS[0]/SKILL.md` and parse its YAML frontmatter. Determine the **context budget** from `metadata.context_budget` (default: `standard` if not specified).

   **Context budget tiers:**

   **`light`** — Skip all briefs and reference file loading. Lightweight skills only need the briefs append (step 1) and orphaned-brief check (step 3). Proceed directly to step 5.

   **`standard`** (default) — Load the briefs index (`${BRIEFS_INDEX_FILE}`) instead of the full `${BRIEFS_FILE}`. If the index does not exist, generate it by running `python .claude/skills/scripts/generate_briefs_index.py`. Then load reference files (see below).

   **`heavy`** — Load `${BRIEFS_FILE}` with **recency windowing**: read only the first 50 entries from the file (newest first). Append a summary line for older entries: "N earlier entries from DATE to DATE, not loaded." Also load the plan index (`${PLANS_DIR}/INDEX.md`). Then load reference files (see below).

   **Reference file loading (standard and heavy tiers):**

   Always include:
   - Read and inject `.agent-resources/project-conventions.md`. If it does not exist, read and inject `.agent-resources/template-conventions.md` instead.
   - Read and inject `.agent-resources/general-permissions.md`
   - Read and inject `.agent-resources/general-constraints.md`

   **Dynamic reference loading:**
   If the frontmatter contains a `metadata.references` list, read and inject each listed file. Resolve each filename using the following lookup order:
   1. If the filename starts with `general-`, read from `.agent-resources/`
   2. Otherwise, read from `.agent-resources`
   This is the primary mechanism for loading skill-specific references. An empty list (`references: []`) is valid — it means the skill intentionally loads no additional references (e.g., orchestration or utility skills).

   If the calling skill's SKILL.md **does not** contain a `metadata.references` field at all, log a warning: "Skill <name> has no metadata.references — cannot load skill-specific references." All skills are expected to declare their references in frontmatter.

### Util scripts

- When planning, check `${SCRIPTS_DIR}` (see project-conventions.md) for useful scripts.
