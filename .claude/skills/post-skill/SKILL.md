---
name: post-skill
description: "[Internal] Lifecycle hook invoked by other skills for briefs update, QA logging, and git commit. Not intended for direct user invocation."
argument-hint: <id>
user-invocable: false
metadata:
  last-updated: 2026-03-28 12:40:00
  version: 1.1.0
  category: internal
  context_budget: standard
---

# Post skill

## Skill-specific Instructions

0. **Checkpoint recovery**: Check if `${OUTPUT_DIR}/.post-skill-checkpoint` exists. If it does, read it. The format is `<step-number> | <datetime> | <skill-id>`. If the `<skill-id>` matches the current invocation's ID ($ARGUMENTS[0]), resume from the step AFTER the checkpoint step number (skip already-completed steps). If the skill-id does not match, delete the stale checkpoint file and proceed normally.

1. Update the brief related to the execution, prepending it with `DONE | <datetime> | `, where <datetime> is the date and time the execution finished in the format YYYY-MM-DD hh:mm:ss in the UTC timezone (keeping the start time intact). If a plan was generated, append the brief line with `PLAN | <plan id>`.

   Write checkpoint: `1 | <current datetime UTC> | $ARGUMENTS[0]` to `${OUTPUT_DIR}/.post-skill-checkpoint`.

1b. **Telemetry recording** — Prepare a telemetry record (held in context until step 8b writes it to disk). Format:

    ```json
    {"timestamp": "YYYY-MM-DDTHH:MM:SSZ", "skill": "<skill-name>", "id": "<invocation-id>", "duration_seconds": <N|null>, "outcome": "<success|partial|failed>", "brief": "<brief-text>", "prefix_scope": "<PREFIX-SCOPE|null>", "plan_id": "<plan-id|null>", "error_type": "<error-type|null>", "output_file": "<relative-path|null>", "context_budget": "<light|standard|heavy>"}
    ```

    - `timestamp`: current UTC datetime in ISO 8601 format.
    - `skill`: extract the skill name from the brief entry updated in step 1 (the field after the last `|` separator before the brief text, e.g., `advise`, `make-plan`).
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

2. **As-Is alignment** — If the completed skill produced or executed a plan (detectable from the plan ID in $ARGUMENTS[0] or from the brief entry), update the as-is files to reflect changes made by the plan:

   a. Read the plan file to identify what changed: entities added/modified/removed, permissions changed, UX patterns added, metacommunication intents implemented.

   b. If `project-conceptual-design-as-is.md` exists in `.agent-resources/`:
      - For entities/permissions/patterns **added** by the plan: add the corresponding section to the as-is file.
      - For entities/permissions/patterns **modified** by the plan: update the relevant section.
      - For entities/permissions/patterns **removed** by the plan: remove the section.
      - Append a changelog entry to §11:
        ```
        ### vN — YYYY-MM-DD
        - **Added/Changed/Removed**: {{description}}
        - **Source**: agent (post-skill)
        - **Plan**: {{plan-id}}
        ```

   c. If `project-metacomm-as-is.md` exists in `.agent-resources/`:
      - If the plan had metacomm framing: update the per-feature metacomm log (§2) with the implemented intent, setting Implementation Status to "Implemented".
      - For features whose metacomm was modified by the plan: update the Designer Intent and Last Updated columns.
      - Append a changelog entry to §3.
      - Tag all changes with `source: agent (post-skill)`.

   d. Include the updated as-is files in the commit scope (step 8).

3. Run the /qa-log skill with the following caller overrides:
   - **no_commit**: true (post-skill handles the commit in step 8).
   - **filename**: `<prefix>${ARGUMENTS[0]}-qa-<truncated short title slug>.md` where `<prefix>` is the corresponding kind of file (plan-, advisory-, check-, etc) and `<truncated short title slug>` is the truncated short title slug of the previously generated file. If there is no corresponding file, derive the slug from the conversation topic.
   - **output_dir**: the same directory as the previously generated file. If there is no corresponding file, use `${QA_LOGS_DIR}`.
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
     a. If the invocation produced a plan file (detectable from the plan ID argument), read the plan file's "Files" section (Modified + Created lists) to get the expected paths. Also include `project-conceptual-design-as-is.md` and `project-metacomm-as-is.md` from `.agent-resources/` when a plan was executed.
     b. Otherwise, use the calling skill's output directory convention from project-conventions.md (e.g., `/advise` outputs to `${ADVISORY_DIR}`, `/explain` outputs to the appropriate `${EXPLAINED_*_DIR}`).
     c. Always include `${BRIEFS_FILE}`, `${BRIEFS_INDEX_FILE}`, `${ARTIFACT_INDEX_FILE}`, the QA log file, and `${OUTPUT_DIR}/telemetry.jsonl` as expected outputs (post-skill itself produces these; note that `telemetry.jsonl` is written in step 8b after commit).
   - Compare pre-staged files against expected paths. Files under `_loom/` and `.claude/` matching the skill's output convention are always allowed.
   - If there are pre-staged files that are NOT part of the skill's expected output, warn the user, list the unexpected files, and output the commit message for manual use.
   - If there are no unexpected pre-staged files, proceed to stage and commit normally.

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

    - This step is lightweight and must not block subsequent steps. If writing fails (e.g., permission error), log a warning and continue.

9. If there are any manual actions to be taken (db upgrade, environment update or config, restart backend or frontend), append the plan file with the action instructions, separating dev and production environments, and inform the user.

10. Output a link to the generated file within `${OUTPUT_DIR}` (see project-conventions.md).

11. **Contextual next-step suggestions**: Read `.agent-resources/general-skill-graph.md`. Look up the completed skill in the "After" column. If found, display the suggested skill(s) and reason as a tip:

    ```
    Tip: You might want to try next:
    - /suggested-skill — reason from the graph
    ```

    Only show nudges when the completed skill has entries in the graph. If `general-skill-graph.md` does not exist, skip this step silently.
