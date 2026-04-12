---
name: implement
description: Execute a previously generated plan to add a feature, fix a bug, or refactor code. Use when user mentions "implement", "execute plan", or "run plan".
argument-hint: "<planned-item-id> [--manual] [--roadmap <roadmap-id>] [--checkpoint wave|plan|none] [--max-iterations N] [--dry-run] [--skip-checks]"
compatibility: "Designed for Claude Code with SEJA framework"
metadata:
  last-updated: 2026-03-27 12:00 UTC
  version: 1.0.0
  plan_format_version: 1
  category: planning
  context_budget: heavy
  eager_references:
    - project/conceptual-design-as-is.md
    - project/design-intent-to-be.md
    - general/report-conventions.md
    - general/coding-standards.md
  references:
    - project/conceptual-design-as-is.md
    - project/design-intent-to-be.md
    - general/report-conventions.md
    - general/coding-standards.md
    - project/frontend-standards.md
    - project/backend-standards.md
    - project/testing-standards.md
    - project/i18n-standards.md
    - project/security-checklists.md
    - general/review-perspectives.md
---

## Quick Guide

**What it does**: Runs a previously approved plan step by step. Nothing changes in your project until you have reviewed and approved the plan first.

**Example**:
> You: /implement 0042
> Agent: Executes each step of Plan 0042 in order — creates files, modifies code, runs verifications. Reports progress and flags any issues encountered.

> You: /implement --roadmap 000316
> Agent: Reads roadmap 000316, identifies 4 plans across 3 waves. Executes Wave 0 plans sequentially, then pauses for review. After approval, executes Wave 1 plans in parallel, pauses again, then Wave 2.

**When to use**: You have reviewed a plan (created by /plan) and are ready to have the agent carry it out. Use `--roadmap` when you want to execute all plans in a roadmap wave-by-wave without manually triggering each one.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<planned-item-id>` | Yes | The 6-digit ID of the plan to execute |
| `--manual` | No | Execute all steps sequentially in the current context instead of using subagents. Default: auto mode |
| `--max-iterations N` | No | Set the iteration cap for auto mode. Default: `20` |
| `--dry-run` | No | Preview what changes would be made without applying them |
| `--roadmap <roadmap-id>` | No | Execute all plans in a roadmap, wave by wave. Mutually exclusive with `<planned-item-id>` |
| `--checkpoint <wave\|plan\|none>` | No | Checkpoint granularity for roadmap mode. Default: `wave` |
| `--skip-checks` | No | Skip the automatic quality checks (`/check validate` + `/check review`) at the end |

# Execute a plan

If no argument was provided, ask the user for the planned item id.

## Definitions

Plan file: Resolve the plan filename by looking up `$ARGUMENTS[0]` in `${OUTPUT_DIR}/INDEX.md` (the global artifact index). The index maps artifact IDs to their titles and status. Use the matched ID to construct the filename `${PLANS_DIR}/plan-<id>-<slug>.md`. If INDEX.md does not exist, run `python .claude/skills/scripts/generate_macro_index.py` to generate it. If the ID is not found in the index, inform the user and abort.

Progress file: `${PLANS_DIR}/plan-<id>-progress.md` — append-only cross-iteration learnings. Created at the start of auto mode, read by each subagent, appended to after each iteration.

## General Instructions
After completing each step (or iteration in auto mode), update the to-do list in the plan file and save it to make it persistent immediately, in case the plan is interrupted.

Before executing, create a rollback branch: `git branch pre-plan-<id>` from the current HEAD. If execution fails and the user wants to undo changes, they can `git checkout pre-plan-<id>`. Inform the user that the rollback branch was created.

## Quality Gate

The quality gate runs validation, code review, and tests. It is referenced from multiple locations in both manual and auto modes. Skipped if `--skip-checks` was passed.

1. Run `/check validate` to run all project validation scripts.
2. Run `/check review` to review all changes in scope.
3. Launch the `test-runner` agent with scope "all" to verify tests pass.
4. If the plan's `smoke` field is `true`, run `/check smoke api`.
5. If any check surfaces **critical** issues (failing tests, security findings, blocking validation errors), fix them before proceeding. For non-critical issues, list them in the plan file summary as deferred items.

### Generator-Critic Loop (Auto Mode Only)

When running in **auto mode**, the quality gate applies a bounded generator-critic retry loop for critical code review findings. In **manual (interactive) mode**, review findings remain advisory — the user decides what to fix.

**Retry logic** (auto mode, after step 2 above):

1. Classify each code-reviewer finding as **critical** (blocking: security, correctness, failing tests) or **advisory** (non-blocking: style, minor improvements).
2. Set `retry_count = 0`.
3. While critical findings exist AND `retry_count < 2`:
   a. Increment `retry_count`.
   b. For each critical finding: construct a fix prompt containing the finding description, affected file(s) and line(s), and the original plan context.
   c. Launch a `general-purpose` subagent to apply the fix.
   d. Re-run `/check review` on the changed files only.
   e. Re-classify findings from the new review.
4. If `retry_count` reaches 2 and critical findings remain, log them as **unresolved** in the plan file summary and continue — do not block the workflow.
5. Append a **Generator-Critic Iterations** section to the quality gate output:
   ```
   ### Generator-Critic Iterations
   - Iteration count: N/2
   - Findings per iteration: [list counts]
   - Resolution status: all resolved / N unresolved critical findings remain
   ```

## Execution Modes

This skill supports three execution modes:

- **Auto** (default): Execute each plan step in a fresh subagent context. Inspired by the Ralph pattern — each iteration gets a clean context window and communicates via disk artifacts. Best for most plans, especially larger ones (>6 steps) where context degradation is a risk.
- **Manual** (`--manual`): Execute all plan steps sequentially in the current context. Best for small plans (≤6 steps) or when interactive confirmation is needed for each step.
- **Roadmap** (`--roadmap <id>`): Execute all plans in a roadmap, wave by wave. Each plan runs via auto mode in a fresh subagent. Pauses between waves for user review (configurable via `--checkpoint`). Best for completing entire roadmaps without manual per-plan invocation.

If `--roadmap` is passed, use roadmap mode. If `--manual` is passed, use manual mode. Otherwise, use auto mode.

`--max-iterations N` sets the iteration cap for auto mode (default: 20). Ignored in manual mode.

`--dry-run` previews the planned changes for each step without applying them. For each step, the agent describes what files would be created/modified and what changes would be made, but does not write any files or run any commands. Useful for reviewing the plan's concrete impact before committing to execution.

`--skip-checks` skips the automatic quality checks (validate, review, tests) at the end of execution. Use for documentation-only or low-risk plans where speed matters more than a full quality review.

---

## Manual Mode — Skill-specific Instructions

1. Run /pre-skill "implement" $ARGUMENTS[0] to add general instructions to the context window.

2. Read the planned item from the plan file.

3. **Load references on demand**: As you execute each step, load lazy references from the "Available references" list based on the step's References field:
   - Load `project/frontend-standards.md` when executing steps that touch frontend files
   - Load `project/backend-standards.md` when executing steps that touch backend files
   - Load `project/testing-standards.md` when writing or updating tests
   - Load `project/i18n-standards.md` when executing i18n-related steps
   - Load `project/security-checklists.md` when executing auth or validation steps
   - Load `general/review-perspectives.md` when running the post-execution quality gate

4. If the plan file does not end with a to-do list, append a to-do list to the plan file and check each item as done after you execute each step.

5. Execute the actions according to the plan. If an affected file has unsaved or uncommitted changes, pause and ask for authorization before proceeding or changing it.

6. Document every file, constant, class, method, and relevant key code fragments you create or modify. Update the to do list in the plan file when this step is done and save it to make it persistent in case the plan is interrupted.

7. **Test generation** (skipped if `--skip-checks` was passed): For each completed step that has a non-N/A `Tests` field, write or update tests following `project/testing-standards.md`. If the step has no `Tests` field (pre-format plans), infer test needs from the modified files. If a bug is found, make and record a new plan to fix it, don't execute it yet, and alert the user when concluding the execution of this skill. Revise or eliminate obsolete tests.

8. Run the [Quality Gate](#quality-gate) (skipped if `--skip-checks` was passed).

9. Mark the resolved issue in the plan file preceding the issue id with `# DONE | <datetime> |`, where <datetime> is the date and time the execution finished in the format YYYY-MM-DD HH:MM UTC. Update the to do list in the plan file when this step is done and save it to make it persistent in case the plan is interrupted. Rename the plan file to reflect the completion of the planned item, changing the prefix from `plan-<id>-` to `plan-<id>-done-` and keeping the rest of the filename unchanged.

10. Append a summary of all changes made to the plan file.

11. If the plan is part of a roadmap, mark the corresponding roadmap item as completed, following the conventions in `project/conventions.md` for roadmap management. Then check whether all roadmap items are now completed. If this was the **last item** in the roadmap, run the [Quality Gate](#quality-gate) with review scope set to all changes since the roadmap's rollback branch (`pre-plan-<first-plan-id>`).

12. Run /post-skill <planned-item-id>.

---

## Auto Mode — Skill-specific Instructions

### Phase 0: Setup

1. Run /pre-skill "implement" $ARGUMENTS[0] to add general instructions to the context window.

2. Read the planned item from the plan file.

3. Parse the Steps section from the plan file. Each step has structured metadata: title, description, Files, References, Depends on, Verify, and a checkbox.

   **Version check**: Before parsing steps, read the plan file's header for `plan_format_version`. If it is present and does not match the expected version (`1`), warn the user and fall back to manual mode. If the field is missing entirely, warn the user and fall back to manual mode — plans without version metadata predate the structured step format. The version check uses exact match. When a future version 2 is introduced, implement must be updated to support both versions or provide a migration path.

4. Create the progress file if it does not exist, with the header:
   ```markdown
   # Progress — Plan <id>

   Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

   ## Codebase Patterns
   <!-- Subagents consolidate reusable patterns here -->

   ## Iteration Log
   ```

5. Determine the list of incomplete steps from the plan file (unchecked `- [ ] Done`). Verify that dependency ordering is respected: a step whose "Depends on" lists incomplete steps cannot be executed yet. Build the execution queue in dependency order.

6. Inform the user: "Auto mode: N steps remaining, max M iterations. Each step runs in a fresh subagent. Use Ctrl+C to stop between iterations."

### Phase 1: Iteration Loop

For each step in the execution queue, up to `--max-iterations` (default 20):

7. **Pick the next step**: Select the next step from the execution queue whose dependencies are all complete. If all steps are done, exit the loop (go to Phase 2). If remaining steps all have unmet dependencies (blocked), pause and ask the user for guidance.

8. **Build the subagent prompt**: Construct a self-contained prompt for a `general-purpose` subagent using the step's structured metadata:
   - The step's full description (title + body — already self-contained per plan conventions)
   - The step's **Files** list — which files to read, create, modify, or delete
   - The step's **Verify** condition — how the subagent knows it succeeded
   - The content of the progress file (cross-iteration learnings from prior steps)
   - Project conventions: instruct the subagent to read `_references/project/conventions.md` and `_references/general/coding-standards.md`
   - The step's **References**: instruct the subagent to read only these specific `_references/` files (e.g., `project/backend-standards.md`). Do not load all 9 references.
   - The step's **Tests** field — what tests to create or update (if non-N/A). If the field is absent (pre-format plans), infer test needs from the modified files.
   - Explicit instructions:
     - Implement the step as described
     - If the step's Tests field is non-N/A, write or update tests as specified. If the Tests field is absent, write or update tests for any code changed.
     - Run the test commands from project/conventions.md to verify the **Verify** condition is met
     - If tests fail, fix the issues (up to 3 retries) before moving on, returning PARTIAL if you can't fully resolve them but made some progress
     - Commit changes with a descriptive message: `plan-<id> step <N>: <step title>`
     - Append learnings to the progress file: what was discovered, gotchas, patterns, useful context for future steps
     - If a reusable pattern was discovered, also add it to the "Codebase Patterns" section at the top of the progress file
     - Report result as: SUCCESS (step completed and verify condition met), PARTIAL (some work done but blocked), or FAILED (could not complete)
     - If PARTIAL or FAILED, describe the blocker clearly in the progress file so the next iteration or the user can address it

9. **Spawn the subagent**: Launch the `general-purpose` agent with the constructed prompt. Wait for it to complete.

10. **Process result**: Read the subagent's response.
    - If SUCCESS: mark the step's checkbox as `- [x] Done` in the plan file. Save the plan file. Continue to next step.
    - If PARTIAL: mark the step's checkbox as `- [~] Partial` in the plan file. Read the progress file for the blocker description. If the blocker is addressable (e.g., a missing file, a test that needs a fixture), attempt the next step anyway — it may unblock later. If 2 consecutive PARTIAL/FAILED results occur, pause and ask the user for guidance.
    - If FAILED: mark the step's checkbox as `- [!] Failed` in the plan file. Read the progress file for the failure description. Pause and ask the user whether to skip this step, retry it, or abort.

11. **Inter-iteration checkpoint**: After each iteration, read the plan file to count remaining items and report progress: "Step N/M complete. Remaining: K steps."

### Phase 2: Wrap-up

12. Run the [Quality Gate](#quality-gate) (skipped if `--skip-checks` was passed). If tests fail, attempt to fix them in the current context since this is a small targeted fix.

13. Mark the resolved issue in the plan file preceding the issue id with `# DONE | <datetime> |`. Update the to-do list. Rename the plan file from `plan-<id>-` to `plan-<id>-done-`.

14. Append a summary of all changes made (aggregated across all iterations) to the plan file. Include:
    - Steps completed vs. total
    - Iterations used
    - Any steps that were partial or failed
    - Key learnings from the progress file

15. If the plan is part of a roadmap, mark the corresponding roadmap item as completed, following the conventions in `project/conventions.md` for roadmap management. Then check whether all roadmap items are now completed. If this was the **last item** in the roadmap, run the [Quality Gate](#quality-gate) with review scope set to all changes since the roadmap's rollback branch (`pre-plan-<first-plan-id>`).

16. Run /post-skill <planned-item-id>.

---

## Roadmap Mode -- Skill-specific Instructions

> This section is used when `--roadmap <id>` is present in the arguments. Skip the Manual Mode and Auto Mode sections above entirely.

### Phase 0: Setup

1. Run /pre-skill "implement" --roadmap $ARGUMENTS to add general instructions to the context window.

2. **Resolve roadmap file**: Look up the roadmap ID in `${OUTPUT_DIR}/INDEX.md`. Read the roadmap file from `${ROADMAP_DIR}/roadmap-<id>-*.md`. If the roadmap is not found, inform the user and abort.

3. **Parse wave summary**: Extract the wave summary tables from the roadmap file. For each work item, capture:
   - Wave number
   - Item ID and title
   - Plan ID (from the Plan column -- skip items with `plan-TBD` or no plan ID)
   - Dependencies (from the Depends on column)
   - Status (from the Status column -- skip items with status "done")

4. **Filter to incomplete items**: Remove items whose status is "done". If no incomplete items remain, inform the user: "All roadmap items are already complete." and exit.

5. **Validate plan availability**: For each incomplete item, verify that its plan file exists in `${PLANS_DIR}`. If any plan file is missing, list the missing plans and ask the user whether to skip those items or abort.

6. **Determine checkpoint mode**: Read the `--checkpoint` flag value (default: `wave`).
   - `wave`: pause between waves for user review (default)
   - `plan`: pause after every plan for user review
   - `none`: no pauses -- full autopilot with progress notes only

7. **Create rollback branches**:
   - Create `git branch pre-roadmap-<id>` from current HEAD as the overall rollback point.
   - Inform the user: "Roadmap mode: N plans remaining across W waves. Checkpoint: <mode>. Rollback branch: pre-roadmap-<id>. Use Ctrl+C to stop between plans."

### Phase 1: Wave Execution Loop

For each wave (Wave 0, Wave 1, ...) that has incomplete plans:

8. **Start wave**: Create a wave rollback branch: `git branch pre-wave-<N>-<roadmap-id>` from current HEAD.

9. **Identify plans in this wave**: Collect all incomplete plans belonging to this wave. Determine parallelism:
   - Plans within the same wave whose Files lists do not overlap can run in parallel.
   - Plans that share files or have intra-wave dependencies must run sequentially.
   - Wave 0 plans always run sequentially (migration chain safety).

10. **Execute plans**: For each plan in the wave (sequentially or in parallel as determined above):
    a. Launch a `general-purpose` subagent with a self-contained prompt:
       - Instruct it to run `/implement <plan-id>` in auto mode
       - Include the plan file path, project conventions path, and coding standards path
       - Instruct it to report result as: SUCCESS, PARTIAL, or FAILED
       - Pass through `--skip-checks` and `--max-iterations` flags if provided
    b. Wait for the subagent to complete.
    c. Read the subagent's result.

11. **Process wave results**: After all plans in the wave complete:
    a. Collect results: count SUCCESS, PARTIAL, FAILED.
    b. Update the roadmap file: mark completed items as "done" in the Status column.
    c. If any plan FAILED: pause regardless of checkpoint mode. Show the failure details and ask the user:
       - **Continue** -- skip the failed plan and proceed to the next wave
       - **Retry** -- re-run the failed plan
       - **Abort** -- stop the roadmap execution (completed plans are preserved)

12. **Inter-wave checkpoint** (based on `--checkpoint` mode):
    - **`wave`** (default): Show wave summary (plans completed, failed, remaining across future waves). List key files modified. Ask the user: "Wave N complete. Continue to Wave N+1?" with options:
      - **Continue** -- proceed to the next wave
      - **Review changes** -- pause so the user can inspect the code before continuing
      - **Abort** -- stop here (completed work is preserved)
    - **`plan`**: The per-plan pause is handled by each `/implement` invocation's post-skill step 11 (which already asks the user what to do next). The roadmap orchestrator reads the plan status after each invocation and proceeds.
    - **`none`**: Emit a one-line progress note: "Wave N complete (K/M plans succeeded). Continuing to Wave N+1..." and proceed automatically. If a plan fails, still pause (failures always get user attention).

### Phase 2: Wrap-up

13. **Final quality gate**: After all waves complete (or user aborts), run the [Quality Gate](#quality-gate) with review scope set to all changes since `pre-roadmap-<id>` branch. This is the cross-plan integration check. Skipped only if `--skip-checks` was passed.

14. **Update roadmap file**: Write final status for all items. If all items are "done", append a completion note:
    ```
    ## Completion
    Roadmap completed at <datetime UTC>. All N plans executed across W waves.
    ```

15. **Report summary**:
    - Total plans executed vs. total in roadmap
    - Waves completed
    - Failures (if any)
    - Total files changed (from `git diff --stat pre-roadmap-<id>..HEAD`)
    - Rollback instructions: "To undo all changes: `git checkout pre-roadmap-<id>`. To undo a specific wave: `git checkout pre-wave-<N>-<roadmap-id>`."

16. Run /post-skill --roadmap <roadmap-id>.

### Constraints

- Each plan runs in auto mode via a fresh subagent. Manual mode is not supported for roadmap execution.
- The `--skip-checks` flag, if passed, applies to all per-plan quality gates. The final roadmap-level quality gate (step 13) is never skipped.
- The `--max-iterations` flag, if passed, applies to each plan's auto mode iteration cap.
- The `--dry-run` flag, if passed, previews all plans without executing any. Each plan's dry-run output is shown sequentially, wave by wave.
- Resumable: running `/implement --roadmap <id>` again on a partially-completed roadmap picks up from the first incomplete item. Completed plans are not re-executed.
