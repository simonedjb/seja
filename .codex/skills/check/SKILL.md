---
name: check
description: "Run quality checks: validation, code review, smoke tests, preflight, or framework health."
argument-hint: <validate | review | smoke | preflight | health | test-plan> [scope]
metadata:
  last-updated: 2026-03-29 00:15:00
  version: 1.0.0
  category: analysis
  context_budget: heavy
  references:
    - general/report-conventions.md
    - project/frontend-standards.md
    - project/backend-standards.md
    - project/i18n-standards.md
    - project/security-checklists.md
    - general/review-perspectives.md
    - general/review-log-template.md
---

## Quick Guide

**What it does**: Unified quality gate — runs validation scripts, code reviews, smoke tests, preflight checks, framework health diagnostics, or user test plan generation. One skill for all "is it OK?" questions.

**Example**:
> You: $check preflight
> Agent: Runs all validation scripts and reviews staged changes in one pass. Reports a go/no-go verdict.

> You: $check review staged
> Agent: Reviews staged changes against security, accessibility, performance, and other quality perspectives.

> You: $check smoke api
> Agent: Runs API smoke tests and reports which endpoints pass or fail.

> You: $check test-plan Test the new task filtering feature
> Agent: Produces a structured test plan with scenarios, step-by-step instructions, expected results, and edge cases that testers should verify.

**When to use**: Before committing, after making changes, or when you want to verify code quality, project health, framework integrity, or generate a manual test plan for recent changes.

# Check

If there are no arguments, use the ask the user directly tool to ask which mode to run (if ask the user directly is not available, present as a numbered text list), with these options:
- "validate -- run project validation scripts"
- "review -- structured code review against perspectives"
- "smoke -- runtime smoke tests (API/UI)"
- "preflight -- validate + review in one pass (pre-commit)"
- "health -- framework self-diagnosis"
- "test-plan -- generate manual test plan from recent plans"

## Modes

| Mode | Description | Former skill |
|------|-------------|-------------|
| `validate [scope]` | Run project validation scripts | `/validate` |
| `review [scope]` | Structured code review against perspectives | `/review-code` |
| `smoke [scope]` | Runtime smoke tests (API/UI) | `/smoke-test` |
| `preflight [scope]` | Validate + review in one pass (pre-commit) | `/preflight` |
| `health [flags]` | Framework self-diagnosis | `/health` |
| `test-plan [brief]` | Generate manual test plan from recent plans | `/plan-user-test` |

## Definitions

Output folder: `${CHECK_LOGS_DIR}` (see project/conventions.md)
Filename pattern: `check-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)

Reserve the next global ID by running `python .codex/skills/scripts/reserve_id.py --type check --title '<title>'`. Use the returned 6-digit ID.

## Skill-specific Instructions

1. Run $pre-skill "check" $ARGUMENTS to add general instructions to the context window.

2. Parse the first argument to determine the mode. Remaining arguments are the scope.

---

### Mode: validate

Scope options: `all` (default) | `i18n` | `auth` | `migrations` | `constants` | `po` | `coverage` | `tests`

> **Role boundary:** This skill is the *user-facing orchestrator*. The `standards-checker` agent is the *execution engine*.

1. Determine the validation scope from the argument (default: `all`).

2. Launch the appropriate agent(s):
   - For validation checks: launch the `standards-checker` agent with the scope
   - For `migrations`: launch both the `standards-checker` agent (for chain script) and the `migration-validator` agent (for deep file inspection and idempotency checks)
   - For `tests`: launch the `test-runner` agent with scope "all"
   - For `all`: launch the `standards-checker` agent with "all"; then ask the user whether to also run tests

3. Save the report to the output file, including:
   - *header*: `# Check <id> | CHORE<scope> | <current datetime> | Validation Report`
   - *scope*: what was validated
   - *summary table*: check name, status (PASS/FAIL/INFO), error count, warning count
   - *details*: for each failed check, list the specific issues
   - *overall status*: X/Y checks passed

4. Present the summary to the user, highlighting any failures.

5. Run $post-skill <id>.

---

### Mode: review

Scope options: `staged` (default) | file path | directory path

1. Determine the review scope:
   - If scope is "staged": the scope is `git diff --cached`
   - If scope is a file path: the scope is that file
   - If scope is a directory: the scope is all source files in that directory
   - If no scope: ask the user

2. Launch the `code-reviewer` agent with the scope as input. The agent will:
   - Read the code to review
   - Evaluate against all 16 perspectives from `general/review-perspectives.md`
   - Return a structured report with findings

3. Save the agent's report to the output file, including:
   - *header*: `# Check <id> | REVIEW<scope> | <current datetime> | Code Review: <short description>`
   - *scope*: what was reviewed (files, staged changes, directory)
   - *perspective evaluation*: table with Adopted/Deferred/N/A per perspective
   - *issues found*: prioritized list with severity, perspective, description, and file:line
   - *recommendations*: actionable items

4. Present the findings summary to the user, highlighting any HIGH severity issues.

5. Run $post-skill <id>.

---

### Mode: smoke

Scope options: `all` (default) | `api` | `ui`

> **Role boundary:** This skill is the *user-facing orchestrator*. The scripts are the *execution engines* — `smoke_test_api.py` exercises backend API endpoints, `smoke.spec.ts` walks UI pages via Playwright.

1. Determine the smoke test scope from the argument (default: `all`).

2. Execute the appropriate script(s):

   **For `api` scope:**
   Run `cd backend && python ../.codex/skills/scripts/smoke_test_api.py` via Bash. Capture full stdout output. This runs against an in-memory SQLite database using the Flask test client — no running servers required.

   **For `ui` scope:**
   First check if `e2e/smoke.spec.ts` exists. If not, inform the user: "UI smoke testing requires E2E infrastructure. Generate it via `$quickstart` with `e2e != none`, or create `e2e/smoke.spec.ts` manually."
   If it exists, run `cd e2e && npx playwright test smoke.spec.ts` via Bash. Capture full stdout/stderr output. This requires both backend (port 5000) and frontend (port 3000) to be running.

   **For `all` scope:**
   Run API smoke test first (faster, independent). Then run UI smoke test if `e2e/smoke.spec.ts` exists.

   > **Note:** The API smoke test is driven by `.codex/skills/scripts/smoke_test_registry.json`. To add or modify endpoints, edit the registry JSON. The generic engine lives in `smoke_test_core.py`.

3. Parse the results:
   - **API results**: Extract the summary line (`PASS: N | WARN: N | FAIL: N`) and any FAIL details from stdout.
   - **UI results**: Extract pass/fail status from Playwright output and any runtime error details.

4. Save the report to the output file, including:
   - *header*: `# Check <id> | CHORE-X | <current datetime> | Smoke Test Report`
   - *scope*: what was tested (`api`, `ui`, or `all`)
   - *API results table* (if applicable): per-endpoint status
   - *UI results table* (if applicable): per-page/flow status
   - *captured errors*: full details of any failures
   - *overall verdict*: `PASS` (no errors) or `FAIL` (errors found)

5. Present the summary to the user, highlighting any failures.

6. If failures are found, ask the user whether to investigate and fix, create a plan, or dismiss.

7. Run $post-skill <id>.

---

### Mode: preflight

Scope options: `staged` (default) | `all` | directory path

Combines validate + review into a single pre-merge checkpoint.

1. Determine the scope:
   - `staged` (default): validate all + review staged changes
   - `all`: validate all + review all modified files (staged + unstaged)
   - A directory path: validate all + review files in that directory

2. Launch both checks in parallel:
   - **Validation**: launch the `standards-checker` agent with scope "all"
   - **Code review**: launch the `code-reviewer` agent with the determined review scope

3. Collect results from both agents and save a combined report to the output file, including:
   - *header*: `# Check <id> | CHORE<scope> | <current datetime> | Preflight Check`
   - *validation summary*: table of check name, status (PASS/FAIL/INFO), error count, warning count
   - *code review summary*: perspective evaluation table with Adopted/Deferred/N/A
   - *issues found*: merged list from both checks, prioritized by severity
   - *overall status*: READY / NOT READY (READY only if all validation checks pass and no HIGH severity code review issues)

4. Present the overall status to the user with a clear go/no-go recommendation.

5. Run $post-skill <id>.

---

### Mode: health

Flags: `[--verbose]`

1. Run the following checks and collect results:

   #### Check 1: Skill System Integrity
   Run `python .codex/skills/scripts/check_skill_system.py`. Parse the output for errors and warnings. Report total skills found, errors, and warnings.

   #### Check 2: Orphaned Briefs
   Read `${BRIEFS_FILE}`. Scan for entries with status `STARTED` that have no matching `DONE` entry. Report the count and list each orphaned entry.

   #### Check 3: Stale Plans
   Read `${OUTPUT_DIR}/INDEX.md`. Identify plans with status `OPEN` whose creation date is more than 7 days ago. Report the count and list each stale plan.

   #### Check 4: Reference File Completeness
   Scan all `.codex/skills/*/SKILL.md` files for `metadata.references` entries. For each referenced file, verify it exists in `_references/`. Report any missing references. Distinguish between `general/` references (should always exist) and `project/` references (may not exist in framework-only repos).

   #### Check 5: .codex/.codex Sync Status
   Compare the skill list in `.codex/skills/` with `.codex/skills/`. Report any skills that exist in one but not the other.

   #### Check 6: Conventions Completeness
   Run `python .codex/skills/scripts/check_conventions.py`. Parse the output for errors (undefined variables) and warnings (unused definitions). Report PASS if no errors, WARN if only unused definitions exist, FAIL if any referenced variables are undefined.

2. Compile results into a health report:

   ```
   ## Framework Health Report

   | Check | Status | Details |
   |-------|--------|---------|
   | Skill System Integrity | PASS/WARN/FAIL | N errors, M warnings |
   | Orphaned Briefs | PASS/WARN | N orphaned entries |
   | Stale Plans | PASS/WARN | N stale plans (>7 days) |
   | Reference Completeness | PASS/WARN/FAIL | N missing references |
   | .codex/.codex Sync | PASS/WARN | N out-of-sync skills |
   | Conventions Completeness | PASS/WARN/FAIL | N errors, M warnings |

   Overall: X/6 checks passed
   ```

3. Save the report to the output file per report conventions.

4. Present the summary to the user, highlighting any failures or warnings.

5. Run $post-skill <id>.

---

### Mode: test-plan

Scope: a brief describing what to test. If no brief is provided, ask the user.

Output folder: `${USER_TESTS_DIR}` (see project/conventions.md)
Filename pattern: `usertest-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)

Reserve the next global ID by running `python .codex/skills/scripts/reserve_id.py --type usertest --title '<title>'`. Use the returned 6-digit ID.

As input to apply this mode, use only these folders (see project/conventions.md for paths):
- `${PLANS_DIR}`: these contain the generated plans (use `${OUTPUT_DIR}/INDEX.md` to identify relevant plans instead of scanning the directory)
- `${USER_TESTS_DIR}`: these contain the generated user test plans

1. Read `${OUTPUT_DIR}/INDEX.md` (the global artifact index). If it does not exist, run `python .codex/skills/scripts/generate_macro_index.py` to generate it. Filter for recently executed plans (status DONE) relevant to the brief. Read only the full plan files for the relevant IDs identified from the index.

2. Include the previously unchecked items from the user test plans folder in the analysis, if still applicable (i.e., not superseded by the latest changes) in the new report, so they don't get lost.

3. Phrase each to do item as a command to the user (for example, Navigate to <X>; do <A>, check <B>, do <C>. The expected outcome is <O>).

4. Save the information to a new output file, adopting a format similar to the existing entries, including:
   - *header*: `# User test <id> | <prefix><scope> | <current datetime> | <short title>`
   - *user brief*, *agent interpretation*, *files* -- per _references/general/report-conventions.md
   - *to do*: A brief enumeration of the plan steps

5. Run $post-skill <id>.
