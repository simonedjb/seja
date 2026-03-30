---
name: update-tests
description: "Write or update unit tests (frontend vitest or backend pytest) following project conventions."
argument-hint: <file or module to test>
metadata:
  last-updated: 2026-03-25 22:15:00
  version: 1.0.0
  category: code
  context_budget: standard
  references:
    - project/frontend-standards.md
    - project/backend-standards.md
    - project/testing-standards.md
---

## Quick Guide

**What it does**: Writes or updates automated tests for a specific file or module. Ensures your code has safety nets that catch regressions when things change.

**Example**:
> You: /update-tests backend/app/services/task_service.py
> Agent: Analyzes the service, identifies untested paths, and writes pytest tests covering the key behaviors. Follows project testing conventions.

**When to use**: You have added or modified code and need tests to cover it, or you want to improve test coverage for an existing module.

# Update Tests

If there are no arguments, ask which file or module needs tests.

## Scope Detection

Determine the test scope from the argument:
- If the file/module is under `${FRONTEND_DIR}` or has a `.js`/`.jsx`/`.ts`/`.tsx` extension: use **frontend** conventions (vitest, below)
- If the file/module is under `${BACKEND_DIR}` or has a `.py` extension: use **backend** conventions (pytest, below)
- If the argument is `frontend` or `backend`: scope to that entire side
- If ambiguous, ask the user

## Execution Tracker

The file `${TESTS_TRACKER_FILE}` (see project/conventions.md) records the last git commit hash and scope for each execution of this skill. This enables faster planning on subsequent runs by diffing only what changed since the last tracked commit.

### Reading the tracker (planning phase)

1. Read `${TESTS_TRACKER_FILE}`. If the file does not exist, treat all source files as candidates.
2. Determine the **scope** for this execution:
   - `frontend` — only `frontend/src/` files
   - `backend` — only `backend/` files (Python tests)
   - `all` — both frontend and backend
3. Look up the most recent tracker entry that matches the current scope (or `all`).
4. If a matching entry exists, run `git diff --name-only <tracked-commit> HEAD` filtered to the scope paths. Use this diff to identify which source files changed and therefore which tests may need updating. Inform the user of the narrowed scope.
5. If no matching entry exists, fall back to the full analysis (read the source file provided by the user or scan the scope).

## Skill-specific Instructions

1. Run /pre-skill "update-tests" $ARGUMENTS[0] to add general instructions to the context window.

2. Read the source file to understand its exports, props, dependencies, and behavior.
3. Check if a co-located test file already exists. If yes, read it and extend it. If no, create one.
4. Write or update the test file following every convention below exactly.
5. Run the appropriate test command to verify all tests pass:
   - **Frontend**: `npx vitest run <test-file>` from `frontend/`
   - **Backend**: `python -m pytest <test-file> --tb=short -v` from `backend/`
6. If any test fails, fix it and re-run until green. Use progressive diagnostics: retry 1 re-reads the source file, retry 2 checks imports and dependencies, retry 3 asks the user for guidance. Maximum 3 retries before escalating.

### Writing the tracker (after completion)

7. After all tests pass, append a new entry to `${TESTS_TRACKER_FILE}` with:
   ```
   | <current datetime UTC YYYY-MM-DD HH:mm:ss> | <scope> | <current HEAD commit hash (short)> | <brief summary of what was tested/updated> |
   ```
   If the file does not exist, create it with the header:
   ```markdown
   # Update-Tests Tracker

   Records the last git commit and scope for each execution of the update-tests skill.

   | Date (UTC) | Scope | Commit | Summary |
   |---|---|---|---|
   ```

## Test Conventions

Read the project's testing standards for all test conventions (runner, file placement, imports, mocking patterns, assertion style, what NOT to do):
- **Frontend**: read `project/testing-standards.md` (loaded via metadata.references). If it does not exist, read `template/testing-standards.md` from `_references/` as fallback.
- **Backend**: read `project/testing-standards.md` (loaded via metadata.references). If it does not exist, read `template/testing-standards.md` from `_references/` as fallback.

Do NOT hardcode test conventions in this skill — always defer to the standards file so that conventions stay in sync across all skills that write tests.
