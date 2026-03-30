---
name: execute-plan
description: Execute a previously generated plan to add a feature, fix a bug, or refactor code. Use when user mentions "execute plan".
argument-hint: <planned-item-id> [--manual] [--max-iterations N] [--dry-run] [--skip-checks]
metadata:
  last-updated: 2026-03-27 12:00:00
  version: 1.0.0
  plan_format_version: 1
  category: planning
  context_budget: heavy
  references:
    - project/conceptual-design-as-is.md
    - project/conceptual-design-to-be.md
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
> You: /execute-plan 0042
> Agent: Executes each step of Plan 0042 in order — creates files, modifies code, runs verifications. Reports progress and flags any issues encountered.

**When to use**: You have reviewed a plan (created by $make-plan) and are ready to have the agent carry it out.

# Execute a plan

If no argument was provided, ask the user for the planned item id.

## Definitions

Plan file: Resolve the plan filename by looking up `$ARGUMENTS[0]` in `${OUTPUT_DIR}/INDEX.md` (the global artifact index). The index maps artifact IDs to their titles and status. Use the matched ID to construct the filename `${PLANS_DIR}/plan-<id>-<slug>.md`. If INDEX.md does not exist, run `python .codex/skills/scripts/generate_macro_index.py` to generate it. If the ID is not found in the index, inform the user and abort.

Progress file: `${PLANS_DIR}/plan-<id>-progress.md` — append-only cross-iteration learnings. Created at the start of auto mode, read by each subagent, appended to after each iteration.

## General Instructions
After completing each step (or iteration in auto mode), update the to-do list in the plan file and save it to make it persistent immediately, in case the plan is interrupted.

Before executing, create a rollback branch: `git branch pre-plan-<id>` from the current HEAD. If execution fails and the user wants to undo changes, they can `git checkout pre-plan-<id>`. Inform the user that the rollback branch was created.

## Execution Modes

This skill supports two execution modes:

- **Auto** (default): Execute each plan step in a fresh subagent context. Inspired by the Ralph pattern — each iteration gets a clean context window and communicates via disk artifacts. Best for most plans, especially larger ones (>6 steps) where context degradation is a risk.
- **Manual** (`--manual`): Execute all plan steps sequentially in the current context. Best for small plans (≤6 steps) or when interactive confirmation is needed for each step.

If `--manual` is passed, use manual mode. Otherwise, use auto mode.

`--max-iterations N` sets the iteration cap for auto mode (default: 20). Ignored in manual mode.

`--dry-run` previews the planned changes for each step without applying them. For each step, the agent describes what files would be created/modified and what changes would be made, but does not write any files or run any commands. Useful for reviewing the plan's concrete impact before committing to execution.

`--skip-checks` skips the automatic quality checks (validate, review, tests) at the end of execution. Use for documentation-only or low-risk plans where speed matters more than a full quality review.

---

## Manual Mode — Skill-specific Instructions

1. Run $pre-skill "execute-plan" $ARGUMENTS[0] to add general instructions to the context window.

2. Read the planned item from the plan file.

3. If the plan file does not end with a to-do list, append a to-do list to the plan file and check each item as done after you execute each step.

4. Execute the actions according to the plan. If an affected file has unsaved or uncommitted changes, pause and ask for authorization before proceeding or changing it.

5. Document every file, constant, class, method, and relevant key code fragments you create or modify. Update the to do list in the plan file when this step is done and save it to make it persistent in case the plan is interrupted.

6. If the codebase was modified, create, adapt, and revise automated backend and frontend tests if and as needed to achieve broad coverage. If a bug is found, make and record a new plan to fix it, don't execute it yet, and alert the user when concluding the execution of this skill. Revise or eliminate obsolete tests. Use the $update-tests skill.

7. **Post-execution quality gate** (skipped if `--skip-checks` was passed):
    - Run `$check validate` to run all project validation scripts.
    - Run `$check review` to review all changes made by this plan.
    - Launch the `test-runner` agent with scope "all" to verify that existing tests still pass.
    - If the plan's `smoke` field is `true`, run `$check smoke api` to verify that API endpoints and pages still respond correctly.
    - If any check surfaces **critical** issues (failing tests, security findings, blocking validation errors), fix them before proceeding. For non-critical issues, list them in the plan file summary as deferred items.

8. Mark the resolved issue in the plan file preceding the issue id with `# DONE | <datetime> |`, where <datetime> is the date and time the execution finished in the format YYYY-MM-DD hh:mm:ss in the UTC timezone. Update the to do list in the plan file when this step is done and save it to make it persistent in case the plan is interrupted. Rename the plan file to reflect the completion of the planned item, changing the prefix from `plan-<id>-` to `plan-<id>-done-` and keeping the rest of the filename unchanged.

9. Append a summary of all changes made to the plan file.

10. If the plan is part of a roadmap, mark the corresponding roadmap item as completed, following the conventions in `project/conventions.md` for roadmap management. Then check whether all roadmap items are now completed. If this was the **last item** in the roadmap, run the roadmap-conclusion quality gate before proceeding:
    - Run `$check validate` to run all project validation scripts.
    - Run `$check review` to review all changes since the roadmap's rollback branch (`pre-plan-<first-plan-id>`).
    - Launch the `test-runner` agent with scope "all" for a full test pass.
    - If any check surfaces **critical** issues (failing tests, security findings, blocking validation errors), fix them before proceeding. For non-critical issues, list them in the plan file summary as deferred items.

11. Run $post-skill <planned-item-id>.

---

## Auto Mode — Skill-specific Instructions

### Phase 0: Setup

1. Run $pre-skill "execute-plan" $ARGUMENTS[0] to add general instructions to the context window.

2. Read the planned item from the plan file.

3. Parse the Steps section from the plan file. Each step has structured metadata: title, description, Files, References, Depends on, Verify, and a checkbox.

   **Version check**: Before parsing steps, read the plan file's header for `plan_format_version`. If it is present and does not match the expected version (`1`), warn the user and fall back to manual mode. If the field is missing entirely, warn the user and fall back to manual mode — plans without version metadata predate the structured step format. The version check uses exact match. When a future version 2 is introduced, execute-plan must be updated to support both versions or provide a migration path.

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
   - The step's full description (title + body — already self-contained per make-plan conventions)
   - The step's **Files** list — which files to read, create, modify, or delete
   - The step's **Verify** condition — how the subagent knows it succeeded
   - The content of the progress file (cross-iteration learnings from prior steps)
   - Project conventions: instruct the subagent to read `_references/project/conventions.md` and `_references/general/coding-standards.md`
   - The step's **References**: instruct the subagent to read only these specific `_references/` files (e.g., `project/backend-standards.md`). Do not load all 9 references.
   - Explicit instructions:
     - Implement the step as described
     - Write or update tests for any code changed
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

12. **Quality gate** (skipped if `--skip-checks` was passed):
    - Run `$check validate` to run all project validation scripts.
    - Run `$check review` to review all changes made by this plan.
    - Launch the `test-runner` agent with scope "all" for a final cross-step verification. If tests fail, attempt to fix them (in the current context, since this is a small targeted fix).
    - If the plan's `smoke` field is `true`, run `$check smoke api`.
    - If any check surfaces **critical** issues (failing tests, security findings, blocking validation errors), fix them before proceeding. For non-critical issues, list them in the plan file summary as deferred items.

13. Mark the resolved issue in the plan file preceding the issue id with `# DONE | <datetime> |`. Update the to-do list. Rename the plan file from `plan-<id>-` to `plan-<id>-done-`.

14. Append a summary of all changes made (aggregated across all iterations) to the plan file. Include:
    - Steps completed vs. total
    - Iterations used
    - Any steps that were partial or failed
    - Key learnings from the progress file

15. If the plan is part of a roadmap, mark the corresponding roadmap item as completed, following the conventions in `project/conventions.md` for roadmap management. Then check whether all roadmap items are now completed. If this was the **last item** in the roadmap, run the roadmap-conclusion quality gate before proceeding:
    - Run `$check validate` to run all project validation scripts.
    - Run `$check review` to review all changes since the roadmap's rollback branch (`pre-plan-<first-plan-id>`).
    - Launch the `test-runner` agent with scope "all" for a full test pass.
    - If any check surfaces **critical** issues (failing tests, security findings, blocking validation errors), fix them before proceeding. For non-critical issues, list them in the plan file summary as deferred items.

16. Run $post-skill <planned-item-id>.
