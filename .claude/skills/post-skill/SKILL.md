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
    {"timestamp": "2026-03-29T14:00:00Z", "skill": "advise", "id": "000014", "duration_seconds": 1800, "outcome": "success", "brief": "What other attributes could be incorporated into telemetry?", "prefix_scope": "CHORE-O", "plan_id": null, "error_type": null, "output_file": "_output/advisory-logs/advisory-000014-telemetry-attributes-expansion.md", "context_budget": "standard", "git_commit_sha": null, "files_changed": null, "parent_skill": null, "qa_type": "advisory-follow-up", "user_revised_output": null, "decision_points": [], "advisory_decisions": []}
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
    - `git_commit_sha`, `files_changed`, `parent_skill`: populated in step 8b after the commit completes. At this point (step 1b), set all three to `null` — they will be filled in before flush.
    - `qa_type` (string enum | null): shape of the interaction the skill had with the user. Allowed values: `"single-prompt"`, `"multi-turn"`, `"advisory-follow-up"`, `"decision-point-accept"`, `"decision-point-revise"`, `"decision-point-reject"`, or `null`. Determined during the skill run by observing the interaction shape:
      - `"single-prompt"` — skill ran end-to-end from one user prompt with no Q&A or decision points. **Default fallback when uncertain.** Skills that do not involve Q&A or decision points should set this value.
      - `"multi-turn"` — the user asked follow-up questions or provided clarifications mid-run that required back-and-forth dialogue (not just acceptance of a proposal).
      - `"advisory-follow-up"` — an advisory or explain-style skill whose session included follow-up questions from the user after the primary report.
      - `"decision-point-accept"` — the skill's main interaction was a single `AskUserQuestion` decision and the user picked the recommended option.
      - `"decision-point-revise"` — same as above but the user picked a non-recommended option and proceeded.
      - `"decision-point-reject"` — same as above but the user dismissed the decision or chose "none of these".
      - `null` — telemetry capture of this field failed.
    - `user_revised_output` (bool | null): whether the user modified the primary output artifact between this skill's commit and the next commit on that file. **Post-skill always writes `null` at step 1b and step 8b — it cannot know the future.** The `/reflect` skill computes this lazily when it later analyzes the telemetry stream via `git diff <git_commit_sha>..<next_sha_touching_output_file>`. Document explicitly as `null` here; `/reflect` is the sole consumer that populates it retroactively.
    - `decision_points` (list | null): list of objects, each of shape `{"prompt": "<question text>", "chosen_option": "<option label>", "rationale_presented": <bool>}`. Populated during the skill run by observing every `AskUserQuestion` invocation:
      - For each `AskUserQuestion` call, record the prompt text, the option the user chose, and whether that invocation's option descriptions carried the "Decision-point rationale convention" payload defined in `_references/general/constraints.md` (1-2 lines explaining *why this option might be right* and optionally *when it would be wrong*, optionally a `(more: <link>)` footer).
      - `rationale_presented` is `true` when the option descriptions include that rationale payload, `false` otherwise. A bare option label with no rationale fails this check.
      - Set to `[]` (empty list) if the skill issued no `AskUserQuestion` calls.
      - Set to `null` only if telemetry capture of decision points failed. `/reflect` audits rationale compliance over time using this field.
    - `advisory_decisions` (list | null): list of objects, each of shape `{"topic": "<short topic>", "decision": "<one-line decision statement>", "priority": "high|medium|low"}`. Populated by the `/advise` skill during recommendation synthesis (step 7). Each HIGH or MEDIUM recommendation becomes one entry. Set to `[]` for non-advisory skills. Set to `null` if telemetry capture failed. This field captures the substance of free-form design decisions that `decision_points` misses (since `decision_points` only records `AskUserQuestion` interactions).

    This step prepares the record in context. The record is written to disk in step 8b after git commit data is available. If any field cannot be determined, set it to `null` (or `"single-prompt"` for `qa_type`, `[]` for `decision_points`, `[]` for `advisory_decisions`, per the fallbacks above).

    > **Backwards compatibility (additive).** The four new fields (`qa_type`, `user_revised_output`, `decision_points`, `advisory_decisions`) are additive. Any telemetry reader that expected the previous 14-field record continues to work because JSON object field order is non-significant and unknown fields are ignored by well-behaved readers. The 17-to-18 expansion follows the same pattern as the 14-to-17 expansion (plan-000295).

2. **As-Coded alignment** — If the completed skill executed a plan (detectable from the brief entry's skill field being "implement"), update the as-coded files to reflect changes made by the plan. Skip when the parent skill is "plan" (no code changes yet):

   a. Read the plan file to identify what changed: entities added/modified/removed, permissions changed, UX patterns added, metacommunication intents implemented.

   b. **Conceptual design updates — `project/product-design-as-coded.md § Conceptual Design`** (three-branch discriminator, SEJA 2.8.4):

      1. **If `project/product-design-as-coded.md` exists**: update the `## Conceptual Design` H2 section incrementally using anchor-based `Edit` with `old_string` containing the H3 heading text. Add/modify/remove H3 subsections under the Conceptual Design H2:
         - For entities/permissions/patterns **added** by the plan: add the corresponding H3 subsection under `## Conceptual Design`.
         - For entities/permissions/patterns **modified** by the plan: update the relevant H3 subsection.
         - For entities/permissions/patterns **removed** by the plan: remove the H3 subsection.

      2. **If `project/product-design-as-coded.md` does not exist AND none of `project/conceptual-design-as-is.md`, `project/metacomm-as-is.md`, `project/journey-maps-as-is.md` exist on disk** (greenfield / fresh brownfield path): instantiate from `template/product-design-as-coded.md`, populating `## Conceptual Design` with plan-relevant content and leaving `## Metacommunication` and `## Journey Maps` as template placeholders. Steps 2c and 2d will populate their respective H2 sections below.

      3. **If `project/product-design-as-coded.md` does not exist AND any of the three legacy files exist on disk** (option-3 migration path from CHANGELOG 2.8.4): emit the warning:

         ```
         WARNING: legacy as-is layout detected (one or more of
         conceptual-design-as-is.md, metacomm-as-is.md, journey-maps-as-is.md
         present) but project/product-design-as-coded.md is missing. Skipping as-coded alignment
         for this plan. Migrate per CHANGELOG 2.8.4 Migration Option 1 or 2,
         or run /upgrade. This warning repeats on every post-skill invocation
         until migrated.
         ```

         Then return from the as-coded alignment step. Steps 2b, 2c, and 2d all become no-ops for this plan. Do not create `product-design-as-coded.md`, do not edit any legacy file. Continue to append changelog entries to `${CD_AS_IS_CHANGELOG}` as normal (that file is unchanged in this plan; Phase 3 F from advisory-000264 handles its conditional embedding later).

      After branch 1 or 2 completes, append a changelog entry to `${CD_AS_IS_CHANGELOG}` (see project/conventions.md). If the changelog file does not exist, instantiate it from `template/product-design-changelog.md`. Append the entry after the last existing changelog version:

      ```
      ### vN -- YYYY-MM-DD
      - **Added/Changed/Removed**: {{description}}
      - **Source**: agent (post-skill)
      - **Plan**: {{plan-id}}
      ```

   c. **Metacommunication updates — `project/product-design-as-coded.md § Metacommunication`**:

      Steps 2c and 2d inherit the branch decision from step 2b. If 2b took branch 3 (legacy warning), 2c is a no-op. If 2b took branch 2 (fresh instantiation), 2c populates `## Metacommunication`. If 2b took branch 1 (incremental edit), 2c updates `## Metacommunication` incrementally.

      - If the plan had metacomm framing: update the per-feature metacomm log (the H3 subsection `### 4. Per-Feature Metacommunication Log` under `## Metacommunication`) with the implemented intent, setting Implementation Status to "Implemented".
      - For features whose metacomm was modified by the plan: update the Designer Intent and Last Updated columns.
      - **Phrasing rule**: All metacomm text (global summary, EMT answers, per-feature intents) must use "I" as the designer and "you" as the user — never third-person or passive voice. See `general/shared-definitions.md` § Phrasing rule.
      - Append a changelog entry to the `### 5. Changelog` H3 subsection under `## Metacommunication`.
      - Tag all changes with `source: agent (post-skill)`.
      - Use anchor-based `Edit` with `old_string` containing the H3 heading text. All edits must stay within the `## Metacommunication` H2 section (see the section boundary discipline note at the end of step 2d).

   d. **Journey map updates — `project/product-design-as-coded.md § Journey Maps`**:

      Steps 2c and 2d inherit the branch decision from step 2b. If 2b took branch 3 (legacy warning), 2d is a no-op.

      - If `project/product-design-as-coded.md § Journey Maps` section is missing (e.g., the file was created by branch 2 above but the Journey Maps section is still a template placeholder) or `project/product-design-as-intended.md §15` does not exist, skip silently.
      - If `project/product-design-as-intended.md` exists with a §15 section (detectable by scanning for `## 15. Designed User Journeys`) and `## Journey Maps` is populated: update incrementally. For each feature added/modified by the plan, check if it corresponds to a JM-TB-NNN entry in `project/product-design-as-intended.md §15 (Designed User Journeys)` and update the implementation status under the appropriate H3 subsection (`### JM-TB-NNN: ...`). For JM-E-NNN entries, cross-reference `project/ux-research-results.md §5 (Discovered User Journeys)`. Update the `### Delta from As-Intended` H3 subsection.
      - Append a changelog entry to the `### Changelog` H3 subsection under `## Journey Maps`.
      - Tag all changes with `source: agent (post-skill)`.

   **Section boundary discipline** (SEJA 2.8.4): post-skill writes to `project/product-design-as-coded.md` must stay within one H2 domain section per `Edit` call. The `check_section_boundary_writes.py` validator at preflight step 6c rejects any single contiguous write region that spans two or more H2 sections. Use anchor-based `Edit` with `old_string` containing the H3 heading text (not line numbers). If a single logical update requires changes in multiple sections, issue multiple Edit calls, one per section.

   e. **DONE marker proposal** -- If the plan implemented any user-facing features or journey steps:
      1. Read the as-intended/as-coded registry from `project/conventions.md` (or `template/conventions.md` if the project file is absent). For each as-intended file listed in the registry, check if the file exists in `_references/project/`.
      2. For each existing as-intended file, scan for sections (headings) or table rows that correspond to features implemented by this plan -- match against the plan's step descriptions and the Files list (Modified/Created). Ignore sections that already carry a `STATUS: implemented` (or legacy `STATUS: IMPLEMENTED`) or `ESTABLISHED` marker.
      3. If candidate items are found, prepare a proposal listing for each:
         - File path (relative to `_references/`)
         - Section heading or table row identifier
         - The marker that would be added: `<!-- STATUS: implemented | plan-NNNNNN | YYYY-MM-DD -->`
      4. Present the proposal via AskUserQuestion: "The following as-intended items appear to have been implemented by this plan. Apply markers now, defer for later review, or skip?" Show the candidate list with three options, each carrying rationale per the Decision-point rationale convention in `_references/general/constraints.md`:
         - **Apply now** -- I flip STATUS markers to `implemented` now, while the mapping between plan steps and as-intended items is fresh in context. Recommended when the implementation has been verified in the working session. NOT recommended when you are unsure whether every candidate item actually matches what shipped.
         - **Defer for later review** -- I add each candidate to the pending ledger so you can review them against the real codebase later, without losing the mapping. Recommended when the implementation looks right but you want a cool-down period before committing to markers. NOT recommended when the candidates are trivially correct and deferring is pure procrastination.
         - **Skip** -- I do nothing. Recommended when the plan did not actually implement any as-intended items (e.g., refactor, tooling, docs). NOT recommended when there are real candidates I would lose if we skip.
      5. On **Apply now**: route the markers through `python .claude/skills/scripts/apply_marker.py` for any file in the Human (markers) registry (`HUMAN_MARKERS_FILES` in `human_markers_registry.py`). For files classified Human or Human/Agent not in the registry, the existing inline HTML-comment insertion continues to work.
      6. On **Defer for later review**: for each candidate item, invoke `python .claude/skills/scripts/pending.py add --type mark-implemented --source plan-<id> --description "Flip STATUS markers on <file> for <entry-id> after verification"`. Do not apply markers inline. Log silently on success; log a one-line warning on failure and continue.
      7. On **Skip**: do nothing (same as the previous "None / skip" behavior).
      8. Tag all marker changes with `source: agent (post-skill)`.
      > Note: Markers on `project/ux-research-results.md` and `project/product-design-as-intended.md` must go through `python .claude/skills/scripts/apply_marker.py` because both files are classified Human (markers). Prose content remains human-authored; agents may write only STATUS (on D-NNN Decision entries and §15 journey entries), ESTABLISHED (legacy), INCORPORATED, and CHANGELOG_APPEND lines after AskUserQuestion confirmation. Enforced by `check_human_markers_only.py` and `check_changelog_append_only.py` during step 6c.

   f. Include the updated as-coded files and any as-intended files with DONE markers in the commit scope (step 8).

   g. **Pending action creation from plan metadata** -- If the completed skill executed a plan (same condition as step 2), auto-create pending actions based on the plan's metadata:
      i. Read the plan file's Files section. Count entries (both Modified and Created). If the count is >= the `Verify-as-coded file threshold` from `## Periodic Triggers` in conventions.md (default 5), invoke `python .claude/skills/scripts/pending.py add --type verify-as-coded --source plan-<id> --description "Review _references/project/product-design-as-coded.md against the real implementation of plan-<id>"`. Log silently on success.
      ii. If the plan has a non-empty `## Test plan` or `## Test Plan` section, invoke `python .claude/skills/scripts/pending.py add --type test-implementation --source plan-<id> --description "Run manual tests per plan-<id>'s Test plan section"`.
      iii. If step 2b's documentation prompt was answered "skip" (the user did not proceed with `/document`) and the plan has any step with a non-N/A `Docs:` field, invoke `python .claude/skills/scripts/pending.py add --type update-documentation --source plan-<id> --description "Run /document --plan plan-<id>"`.
      Each invocation must be silent on success and log a one-line warning on failure (`Warning: could not create pending action <type>: <reason>`). Do not block on failures.

   > **Note:** UX research (`project/ux-research-results.md`) and design intent (`project/product-design-as-intended.md`) are classified `Human (markers)` since SEJA 2.8.2 and 2.8.3 respectively. Prose content (personas, scenarios, journey observations, working intent, Decision entry rationale) remains human-authored only. Agents may write `STATUS`, `ESTABLISHED`, `INCORPORATED` markers, and append `CHANGELOG` entries via `apply_marker.py` after AskUserQuestion confirmation (see step 2e and step 6c).

2c. **Design intent curation reminder** — If the completed skill executed a plan (same condition as step 2):

   Output (text-based, not AskUserQuestion):
   > "Design intent from plan [plan-id] has been implemented. Consider promoting items to `established` status via `/explain spec-drift --promote` (Phase 3a generates a draft Decision entry proposal; Phase 3b flips the STATUS markers after you apply the prose). P0 priority items: §4 Permission Model, §11 Global Vision, §13 Solution Representations, §14 Per-Feature Intentions."

   Do **not** perform the promotion. The designer owns every word of Decision entries; the framework only manages the STATUS marker lifecycle structurally. This is informational only.

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
   - **output_dir**: Resolve to the parent artifact's directory by extracting the filename prefix (the portion before the first digit group) from the `filename` override and mapping it via this table:

     | Prefix | Directory variable |
     |--------|---------------------|
     | `plan-` | `${PLANS_DIR}` |
     | `implement-` | `${PLANS_DIR}` |
     | `advisory-` | `${ADVISORY_DIR}` |
     | `check-` | `${CHECK_LOGS_DIR}` |
     | `proposal-` | `${PROPOSALS_DIR}` |
     | `roadmap-` | `${ROADMAP_DIR}` |
     | `onboarding-` | `${ONBOARDING_PLANS_DIR}` |
     | `communication-` | `${COMMUNICATION_DIR}` |
     | `inventory-` | `${INVENTORIES_DIR}` |
     | `reflection-` | `${REFLECTIONS_DIR}` |
     | `user-tests-` | `${USER_TESTS_DIR}` |
     | `explained-behavior-` | `${EXPLAINED_BEHAVIORS_DIR}` |
     | `explained-code-` | `${EXPLAINED_CODE_DIR}` |
     | `explained-data-model-` | `${EXPLAINED_DATA_MODEL_DIR}` |
     | `explained-architecture-` | `${EXPLAINED_ARCHITECTURE_DIR}` |
     | `behavior-evolution-` | `${BEHAVIOR_EVOLUTION_DIR}` |
     | (no known prefix / free-form) | `${QA_LOGS_DIR}` (fallback) |

     QA logs are collocated with the artifact they document. `${QA_LOGS_DIR}` is reserved for user-invoked `/qa-log` sessions without a parent artifact. The `implement-` prefix maps to `${PLANS_DIR}` because `/implement` lifecycle logs carry a plan ID and belong with their parent plan.
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
     a. If the invocation produced a plan file (detectable from the plan ID argument), read the plan file's "Files" section (Modified + Created lists) to get the expected paths. Also include `project/product-design-as-coded.md` from `_references/` when a plan was executed.
     b. Otherwise, use the calling skill's output directory convention from project/conventions.md (e.g., `/advise` outputs to `${ADVISORY_DIR}`, `/explain` outputs to the appropriate `${EXPLAINED_*_DIR}`).
     c. Always include `${BRIEFS_FILE}`, `${BRIEFS_INDEX_FILE}`, `${ARTIFACT_INDEX_FILE}`, the QA log file, and `${OUTPUT_DIR}/telemetry.jsonl` as expected outputs (post-skill itself produces these; note that `telemetry.jsonl` is written in step 8b after commit). The QA log path is the parent-collocated path computed in step 3 (i.e., the parent artifact's directory, not `${QA_LOGS_DIR}`), so the commit scope check treats it as an expected output of the parent skill's directory.
   - Compare pre-staged files against expected paths. Files under `_loom/` and `.claude/` matching the skill's output convention are always allowed.
   - If there are pre-staged files that are NOT part of the skill's expected output, warn the user, list the unexpected files, and output the commit message for manual use.
   - If there are no unexpected pre-staged files, proceed to stage and commit normally.

6b. **Fast preflight gate** — Run `python .claude/skills/scripts/run_preflight_fast.py` to verify framework integrity before committing.
   - If the script exits 0: proceed silently to step 7.
   - If the script exits non-zero: display the failures and ask the user whether to proceed with the commit anyway or abort. The gate is advisory (not blocking) because post-skill runs after potentially lengthy work and a hard block could lose progress. The pre-commit git hook (`.githooks/pre-commit`) provides the hard block.
   - If the script is not found (e.g., older framework version): skip silently.

6c. **Human markers verifier** — Run `python .claude/skills/scripts/check_human_markers_only.py --staged` to verify no prose mutations slipped into `Human (markers)`-classified files.
   - If the script exits 0: proceed silently to step 7.
   - If the script exits 1 (prose mutation detected in a Human (markers) file): display the violation report and ask via AskUserQuestion whether to abort the commit or proceed anyway. The default recommendation is to abort because a `Human (markers)` file has received an unauthorized edit that should go through `apply_marker.py`.
   - If the script is not found (e.g., older framework version): skip silently.

7. **Index regeneration:**
   a. Regenerate the briefs index: run `python .claude/skills/scripts/generate_briefs_index.py` to keep `${BRIEFS_INDEX_FILE}` up to date.
   b. Regenerate the global artifact index: run `python .claude/skills/scripts/generate_macro_index.py` to keep `${ARTIFACT_INDEX_FILE}` (`${OUTPUT_DIR}/INDEX.md`) up to date.
   c. **Cross-reference update**: If the produced artifact has a `source: <type>-<id>` header field, open the source artifact file, read its YAML/Markdown header, and append the new artifact's ID to the source's `spawned:` field (comma-separated if `spawned:` already has values; create the field if absent).
   d. **Decision digest regeneration** (conditional): If the completed skill was `/advise` and the advisory had HIGH or MEDIUM recommendations, OR if a plan applied DECISION_APPEND markers, run `python .claude/skills/scripts/generate_decision_digest.py` to regenerate `${DECISION_DIGEST_FILE}` (`${OUTPUT_DIR}/decision-digest.jsonl`). Include the output file in the commit scope. Skip silently if the script is not found (e.g., older framework version).

   Write checkpoint: `7 | <current datetime UTC> | $ARGUMENTS[0]` to `${OUTPUT_DIR}/.post-skill-checkpoint`.

8. Git stage the affected files (including regenerated index files and any updated as-coded files) and commit using the generated message.

   Write checkpoint: `8 | <current datetime UTC> | $ARGUMENTS[0]` to `${OUTPUT_DIR}/.post-skill-checkpoint`.

   Delete `${OUTPUT_DIR}/.post-skill-checkpoint` — post-skill completed successfully.

8b. **Telemetry flush** — Enrich the telemetry record prepared in step 1b with commit metadata and write it to disk:

    - Populate the 3 commit-dependent fields that step 1b left as `null`:
      - `git_commit_sha` (string|null): run `git rev-parse HEAD` after the commit in step 8. If the commit was skipped, leave as `null`.
      - `files_changed` (int|null): count of files included in the commit (from `git diff-tree --no-commit-id --name-only -r HEAD`). If the commit was skipped, leave as `null`.
      - `parent_skill` (string|null): the name of the skill that invoked post-skill (inferred from the conversation context -- the skill whose workflow called `/post-skill`). `null` if unknown.

    - Carry forward the three captured-during-run fields from step 1b unchanged: `qa_type`, `user_revised_output` (always `null` at write time — `/reflect` populates it lazily), and `decision_points`.

    - Append the complete 17-field record as a single JSON line to `${OUTPUT_DIR}/telemetry.jsonl` (create if it does not exist). Example:

      ```json
      {"timestamp": "2026-03-29T14:00:00Z", "skill": "advise", "id": "000014", "duration_seconds": 1800, "outcome": "success", "brief": "What other attributes could be incorporated into telemetry?", "prefix_scope": "CHORE-O", "plan_id": null, "error_type": null, "output_file": "_output/advisory-logs/advisory-000014-telemetry-attributes-expansion.md", "context_budget": "standard", "git_commit_sha": "9709d91abc123...", "files_changed": 6, "parent_skill": "advise", "qa_type": "advisory-follow-up", "user_revised_output": null, "decision_points": [{"prompt": "Apply markers now?", "chosen_option": "Defer for later review", "rationale_presented": true}], "advisory_decisions": [{"topic": "telemetry-schema", "decision": "Add advisory_decisions field to capture free-form design decisions", "priority": "high"}]}
      ```

    - After writing, stage `${OUTPUT_DIR}/telemetry.jsonl` and amend the commit from step 8 to include it (`git add ${OUTPUT_DIR}/telemetry.jsonl && git commit --amend --no-edit`). This keeps telemetry co-located with the rest of the skill's output in a single commit. If the amend fails (e.g., commit was skipped), log a warning and continue.
    - This step is lightweight and must not block subsequent steps. If writing fails (e.g., permission error), log a warning and continue.

    > **Backwards compatibility (additive).** The four new fields added since the original 14-field schema (`qa_type`, `user_revised_output`, `decision_points`, `advisory_decisions`) are additive. Readers that only knew the old 14 fields continue to parse each record as a JSON object and can safely ignore the new keys. No existing field was renamed, removed, or retyped. The 17-to-18 expansion (plan-000321) follows the same pattern as the 14-to-17 expansion (plan-000295).

9. If there are any manual actions to be taken (db upgrade, environment update or config, restart backend or frontend), append the plan file with the action instructions, separating dev and production environments, and inform the user.

10. Output a link to the generated file within `${OUTPUT_DIR}` (see project/conventions.md).

11. **Contextual next-step suggestions**: Read `_references/general/skill-graph.md`. Look up the completed skill in the "After" column. If found, present the suggestions using AskUserQuestion with numbered options (one per suggested skill), so the user can select one to execute directly. Include an option to dismiss. Example question text:

    > "You might want to try next:"

    When emitting the AskUserQuestion, populate each option's description with the skill-graph reason verbatim plus one line on *when the suggestion would be wrong*, per the Decision-point rationale convention in `_references/general/constraints.md`. If the skill-graph entry does not include a "when wrong" note, derive one from the skill's failure modes documented in its SKILL.md (typical sources: the Quick Guide "When to use" section and the argument-hint field).

    Options (shape):
    - `/suggested-skill-1` -- *Recommended when*: <reason from the graph>. *NOT recommended when*: <derived from the skill's failure mode>.
    - `/suggested-skill-2` -- *Recommended when*: <reason from the graph>. *NOT recommended when*: <derived from the skill's failure mode>.
    - "Skip" -- *Recommended when*: the current workflow is complete and you want to stop here. *NOT recommended when*: you are skipping because the choices feel like friction, in which case one of the suggestions probably earns its place.

    If the user selects a skill, execute it. If they select "Skip", end post-skill.

    Only show nudges when the completed skill has entries in the graph. If `general/skill-graph.md` does not exist, skip this step silently.

