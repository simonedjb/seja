---
name: post-skill
description: "[Internal] Lifecycle hook invoked by other skills for briefs update, QA logging, and git commit. Not intended for direct user invocation."
argument-hint: "<id>"
user-invocable: false
compatibility: "Designed for Claude Code with SEJA framework"
metadata:
  last-updated: 2026-04-01 12:59 UTC
  version: 1.2.0
  category: internal
  context_budget: standard
  references: []
---

# Post skill

## Skill-specific Instructions

0. **Checkpoint recovery**: Check if `${OUTPUT_DIR}/.post-skill-checkpoint` exists. If it does, read it. The format is `<step-number> | <datetime> | <skill-id>`. If the `<skill-id>` matches the current invocation's ID ($ARGUMENTS[0]), resume from the step AFTER the checkpoint step number (skip already-completed steps). If the skill-id does not match, delete the stale checkpoint file and proceed normally.

1. Obtain the current UTC time by running `date -u +"%Y-%m-%d %H:%M UTC"` and capturing its output. Use this exact output as `<datetime>` below — do not estimate or guess the time.

   Update the brief related to the execution, prepending it with `DONE | <datetime> | `, where <datetime> is the value obtained from the `date` command above, in the format YYYY-MM-DD HH:MM UTC (keeping the start time intact). If a plan was generated, append the brief line with `PLAN | <plan id>`.

   Write checkpoint: `1 | <current datetime UTC> | $ARGUMENTS[0]` to `${OUTPUT_DIR}/.post-skill-checkpoint`.

1b. **Telemetry recording** — Prepare a telemetry record (held in context until step 8b writes it to disk). Format:

    ```json
    {"timestamp": "YYYY-MM-DDTHH:MM:SSZ", "skill": "<skill-name>", "id": "<invocation-id>", "duration_seconds": <N|null>, "outcome": "<success|partial|failed>", "brief": "<brief-text>", "prefix_scope": "<PREFIX-SCOPE|null>", "plan_id": "<plan-id|null>", "error_type": "<error-type|null>", "output_file": "<relative-path|null>", "context_budget": "<light|standard|heavy>"}
    ```

    - `timestamp`: the UTC datetime obtained from the `date` command in step 1, converted to ISO 8601 format (e.g., `2026-03-19T21:00:00Z`).
    - `skill`: extract the skill name from the brief entry updated in step 1 (the field after the last `|` separator before the brief text, e.g., `advise`, `plan`).
    - `id`: the invocation ID from $ARGUMENTS[0].
    - `duration_seconds`: compute elapsed seconds between the STARTED timestamp and the current time. If timestamps cannot be parsed, set to `null`.
    - `outcome`: `"success"` for normal completions, `"partial"` if any step reported partial completion, `"failed"` if the skill errored.
    - `brief`: one-line brief text from the STARTED entry, truncated to 200 characters max.
    - `prefix_scope`: the report's prefix-scope (e.g., `"CHORE-O"`) from the calling skill's report header, or `null` if not applicable.
    - `plan_id`: associated plan ID from the brief's `PLAN | <id>` suffix, or `null` if no plan was generated.
    - `error_type`: error classification when outcome is not `"success"`. Values: `"git_conflict"`, `"permission_error"`, `"validation_failure"`, `"timeout"`, `"context_overflow"`, `"user_cancelled"`, `"unknown"`. `null` when outcome is `"success"`.
    - `output_file`: relative path to the primary output artifact (e.g., `"_output/advisory-logs/advisory-000014-telemetry-attributes-expansion.md"`), or `null` if no artifact was produced.
    - `context_budget`: the calling skill's `context_budget` from its YAML frontmatter (`"light"`, `"standard"`, or `"heavy"`).

    This step prepares the record in context. The record is written to disk in step 8b after git commit data is available. If any field cannot be determined, set it to `null`.

2. **As-Is alignment** — If the completed skill executed a plan (detectable from the brief entry's skill field being "implement"), update the as-is files to reflect changes made by the plan. Skip when the parent skill is "plan" (no code changes yet):

   a. Read the plan file to identify what changed: entities added/modified/removed, permissions changed, UX patterns added, metacommunication intents implemented.

   b. For `project/conceptual-design-as-is.md` in `_references/`:
      - If the file **does not exist** (greenfield project, first plan execution): instantiate it from `template/conceptual-design-as-is.md`, populating only the sections relevant to what the plan implemented. Leave other sections as template placeholders.
      - If the file **exists**: update it incrementally:
        - For entities/permissions/patterns **added** by the plan: add the corresponding section to the as-is file.
        - For entities/permissions/patterns **modified** by the plan: update the relevant section.
        - For entities/permissions/patterns **removed** by the plan: remove the section.
      - In both cases, append a changelog entry to `${CD_AS_IS_CHANGELOG}` (see project/conventions.md). If the changelog file does not exist, instantiate it from `template/cd-as-is-changelog.md`. Append the entry after the last existing changelog version:
        ```
        ### vN -- YYYY-MM-DD
        - **Added/Changed/Removed**: {{description}}
        - **Source**: agent (post-skill)
        - **Plan**: {{plan-id}}
        ```

   c. For `project/metacomm-as-is.md` in `_references/`:
      - If the file **does not exist** (greenfield project, first plan execution): instantiate it from `template/metacomm-as-is.md`, populating only the sections relevant to what the plan implemented.
      - If the file **exists**: update it incrementally:
        - If the plan had metacomm framing: update the per-feature metacomm log (§2) with the implemented intent, setting Implementation Status to "Implemented".
        - For features whose metacomm was modified by the plan: update the Designer Intent and Last Updated columns.
      - **Phrasing rule**: All metacomm text (global summary, EMT answers, per-feature intents) must use "I" as the designer and "you" as the user — never third-person or passive voice. See `general/shared-definitions.md` § Phrasing rule.
      - In both cases, append a changelog entry to §3.
      - Tag all changes with `source: agent (post-skill)`.

   d. For `project/journey-maps-as-is.md` in `_references/`:
      - If neither `project/journey-maps-as-is.md` nor `project/design-intent-to-be.md §15` exists (project hasn't adopted journey map templates): skip silently.
      - If `project/design-intent-to-be.md` exists with a §15 section (detectable by scanning for `## 15. Designed User Journeys`) but `project/journey-maps-as-is.md` does **not exist** (first plan execution with journey maps): instantiate it from `template/journey-maps-as-is.md`, populating the steps table based on what the plan implemented. For each JM-TB-NNN entry in `project/design-intent-to-be.md §15 (Designed User Journeys)`, check if the plan implemented steps corresponding to that journey and set implementation status accordingly.
      - If `project/journey-maps-as-is.md` **exists**: update incrementally -- for each feature added/modified by the plan, check if it corresponds to a JM-TB-NNN entry in `project/design-intent-to-be.md §15 (Designed User Journeys)` and update the implementation status. For JM-E-NNN entries, cross-reference `project/ux-research-established.md §5 (Discovered User Journeys)`. Update the Delta from To-Be section.
      - In all cases where the file is updated, append a changelog entry.
      - Tag all changes with `source: agent (post-skill)`.

   e. **DONE marker proposal** -- If the plan implemented any user-facing features or journey steps:
      1. Read the to-be/as-is registry from `project/conventions.md` (or `template/conventions.md` if the project file is absent). For each to-be file listed in the registry, check if the file exists in `_references/project/`.
      2. For each existing to-be file, scan for sections (headings) or table rows that correspond to features implemented by this plan -- match against the plan's step descriptions and the Files list (Modified/Created). Ignore sections that already carry a `STATUS: IMPLEMENTED` or `ESTABLISHED` marker.
      3. If candidate items are found, prepare a proposal listing for each:
         - File path (relative to `_references/`)
         - Section heading or table row identifier
         - The marker that would be added: `<!-- STATUS: IMPLEMENTED | plan-NNNNNN | YYYY-MM-DD -->`
      4. Present the proposal via AskUserQuestion: "The following to-be items appear to have been implemented by this plan. Mark them as IMPLEMENTED?" (show the list; include a "None / skip" option).
      5. If the user confirms: apply the markers inline. If the user declines or no candidates are found, skip silently.
      6. Tag all marker changes with `source: agent (post-skill)`.
      > Note: Do NOT apply markers to `ux-research-new.md` or `ux-research-established.md` -- these are research artifacts, not design intent.

   f. Include the updated as-is files and any to-be files with DONE markers in the commit scope (step 8).

   > **Note:** UX research files (`project/ux-research-new.md`, `project/ux-research-established.md`) are human-maintained and are NOT updated by post-skill. The agent can verify consistency between UX research, design intent, and implementation via `/explain spec-drift` or `/check validate`, but does not modify these files.

2c. **Design intent curation reminder** — If the completed skill executed a plan (same condition as step 2):

   Output (text-based, not AskUserQuestion):
   > "Design intent from plan [plan-id] has been implemented. Consider moving processed entries from `design-intent-to-be.md` to `design-intent-established.md` — P0 priority: §4 Permission Model, §11 Global Vision, §13 Solution Representations, §14 Per-Feature Intentions."

   Do **not** perform the move. The designer curates this file manually to preserve their rationale alongside the plan reference. This is informational only.

2b. **Documentation check** — If the completed skill executed a plan (same condition as step 2):

   a. Read the plan file and check for steps with non-N/A `Docs:` fields. Collect all documentation needs into a list. If the plan predates the `Docs:` field (no steps have it), skip this step silently.

   b. Check the plan's prefix: FEATURE and REDESIGN plans always trigger this check. FIX and CHORE plans only trigger if any step has a non-N/A `Docs:` field.

   c. If documentation needs were identified, prompt the user (text-based, not AskUserQuestion):
      > "This change may need documentation updates. The plan identified these documentation needs:
      > - [list each non-N/A Docs: field value]
      >
      > Would you like to update documentation now, or skip?"

   d. If the user says yes, run `/document --plan <plan-id>` to generate documentation based on the plan's Docs: fields. The document skill uses the templates in `_references/template/docs/` and the writing guide (`_references/general/documentation-quality.md`) for structured generation. If the user says skip, continue to step 3.

   e. If no plan was executed (e.g., advisory, explain, check), skip this step silently.

   Include any documentation files updated in the commit scope (step 8).

3. Run the /qa-log skill with the following caller overrides:
   - **no_commit**: true (post-skill handles the commit in step 8).
   - **filename**: `<prefix>${ARGUMENTS[0]}-qa-<truncated short title slug>.md` where `<prefix>` is the corresponding kind of file (plan-, advisory-, check-, etc) and `<truncated short title slug>` is the truncated short title slug of the previously generated file. If there is no corresponding file, derive the slug from the conversation topic.
   - **output_dir**: `${QA_LOGS_DIR}`. All QA logs are centralized, not co-located with the artifact they document.
   The file should include the brief and the full Q&A log.

   Write checkpoint: `3 | <current datetime UTC> | $ARGUMENTS[0]` to `${OUTPUT_DIR}/.post-skill-checkpoint`.

4. Create an appropriate commit message including $ARGUMENTS[0].

5. **Git-state safety check** before committing:
   - Run `git status` to check the repository state.
   - If a rebase is in progress (`rebase-merge` or `rebase-apply` directory exists in `.git/`), or a merge conflict is active (unmerged paths in `git status`), or HEAD is detached: **do not commit**. Instead, inform the user of the git state and output the commit message for manual use.
   - If on `main` or `master` branch: warn the user that they are committing directly to the main branch and ask for confirmation before proceeding.

6. **Commit scope verification** before staging:
   - Run `git diff --cached --name-only` to list any pre-staged files.
   - Determine the skill's expected output paths using these methods, in order of priority:
     a. If the invocation produced a plan file (detectable from the plan ID argument), read the plan file's "Files" section (Modified + Created lists) to get the expected paths. Also include `project/conceptual-design-as-is.md`, `project/metacomm-as-is.md`, and `project/journey-maps-as-is.md` from `_references/` when a plan was executed.
     b. Otherwise, use the calling skill's output directory convention from project/conventions.md (e.g., `/advise` outputs to `${ADVISORY_DIR}`, `/explain` outputs to the appropriate `${EXPLAINED_*_DIR}`).
     c. Always include `${BRIEFS_FILE}`, `${BRIEFS_INDEX_FILE}`, `${ARTIFACT_INDEX_FILE}`, the QA log file, and `${OUTPUT_DIR}/telemetry.jsonl` as expected outputs (post-skill itself produces these; note that `telemetry.jsonl` is written in step 8b after commit).
   - Compare pre-staged files against expected paths. Files under `_loom/` and `.claude/` matching the skill's output convention are always allowed.
   - If there are pre-staged files that are NOT part of the skill's expected output, warn the user, list the unexpected files, and output the commit message for manual use.
   - If there are no unexpected pre-staged files, proceed to stage and commit normally.

6b. **Fast preflight gate** — Run `python .claude/skills/scripts/run_preflight_fast.py` to verify framework integrity before committing.
   - If the script exits 0: proceed silently to step 7.
   - If the script exits non-zero: display the failures and ask the user whether to proceed with the commit anyway or abort. The gate is advisory (not blocking) because post-skill runs after potentially lengthy work and a hard block could lose progress. The pre-commit git hook (`.githooks/pre-commit`) provides the hard block.
   - If the script is not found (e.g., older framework version): skip silently.

7. **Index regeneration:**
   a. Regenerate the briefs index: run `python .claude/skills/scripts/generate_briefs_index.py` to keep `${BRIEFS_INDEX_FILE}` up to date.
   b. Regenerate the global artifact index: run `python .claude/skills/scripts/generate_macro_index.py` to keep `${ARTIFACT_INDEX_FILE}` (`${OUTPUT_DIR}/INDEX.md`) up to date.
   c. **Cross-reference update**: If the produced artifact has a `source: <type>-<id>` header field, open the source artifact file, read its YAML/Markdown header, and append the new artifact's ID to the source's `spawned:` field (comma-separated if `spawned:` already has values; create the field if absent).

   Write checkpoint: `7 | <current datetime UTC> | $ARGUMENTS[0]` to `${OUTPUT_DIR}/.post-skill-checkpoint`.

8. Git stage the affected files (including regenerated index files and any updated as-is files) and commit using the generated message.

   Write checkpoint: `8 | <current datetime UTC> | $ARGUMENTS[0]` to `${OUTPUT_DIR}/.post-skill-checkpoint`.

   Delete `${OUTPUT_DIR}/.post-skill-checkpoint` — post-skill completed successfully.

8b. **Telemetry flush** — Enrich the telemetry record prepared in step 1b with commit metadata and write it to disk:

    - Add 3 fields to the record:
      - `git_commit_sha` (string|null): run `git rev-parse HEAD` after the commit in step 8. If the commit was skipped, set to `null`.
      - `files_changed` (int|null): count of files included in the commit (from `git diff-tree --no-commit-id --name-only -r HEAD`). If the commit was skipped, set to `null`.
      - `parent_skill` (string|null): the name of the skill that invoked post-skill (inferred from the conversation context -- the skill whose workflow called `/post-skill`). `null` if unknown.

    - Append the complete 14-field record as a single JSON line to `${OUTPUT_DIR}/telemetry.jsonl` (create if it does not exist). Example:

      ```json
      {"timestamp": "2026-03-29T14:00:00Z", "skill": "advise", "id": "000014", "duration_seconds": 1800, "outcome": "success", "brief": "What other attributes could be incorporated into telemetry?", "prefix_scope": "CHORE-O", "plan_id": null, "error_type": null, "output_file": "_output/advisory-logs/advisory-000014-telemetry-attributes-expansion.md", "context_budget": "standard", "git_commit_sha": "9709d91abc123...", "files_changed": 6, "parent_skill": "advise"}
      ```

    - After writing, stage `${OUTPUT_DIR}/telemetry.jsonl` and amend the commit from step 8 to include it (`git add ${OUTPUT_DIR}/telemetry.jsonl && git commit --amend --no-edit`). This keeps telemetry co-located with the rest of the skill's output in a single commit. If the amend fails (e.g., commit was skipped), log a warning and continue.
    - This step is lightweight and must not block subsequent steps. If writing fails (e.g., permission error), log a warning and continue.

9. If there are any manual actions to be taken (db upgrade, environment update or config, restart backend or frontend), append the plan file with the action instructions, separating dev and production environments, and inform the user.

10. Output a link to the generated file within `${OUTPUT_DIR}` (see project/conventions.md).

11. **Contextual next-step suggestions**: Read `_references/general/skill-graph.md`. Look up the completed skill in the "After" column. If found, present the suggestions using AskUserQuestion with numbered options (one per suggested skill), so the user can select one to execute directly. Include an option to dismiss. Example question text:

    > "You might want to try next:"

    Options:
    - `/suggested-skill-1` -- reason from the graph
    - `/suggested-skill-2` -- reason from the graph
    - "Skip" -- dismiss suggestions

    If the user selects a skill, execute it. If they select "Skip", end post-skill.

    Only show nudges when the completed skill has entries in the graph. If `general/skill-graph.md` does not exist, skip this step silently.
