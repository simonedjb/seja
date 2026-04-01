# Journey: Solo Developer -- Side Project

## Who this is for

An experienced developer using the framework to accelerate a personal project, with emphasis on code quality and architecture rather than design documentation.

## What you'll accomplish

A well-structured project with conventions, architecture decisions documented, tests in place, and quality gates configured.

## Prerequisites

- Claude Code or Codex CLI installed
- A git-initialized codebase folder
- The foundational SEJA framework extracted into it
- Familiarity with your chosen tech stack

## Step-by-step walkthrough

### Step 1: Bootstrap with seed + design

Run `/seed .` / `$seed .` to copy the framework, then run `/design` / `$design` to configure your project. If you already know your stack, you can provide a pre-filled spec file to `/design` for faster, non-interactive setup.

Expected output: all `project/*.md` files generated.

### Step 2: Get architecture advice with `/advise` / `$advise`

Ask the agent for recommendations on architecture decisions. Example:

```
/advise Should I use a monorepo or separate repos for backend and frontend?   # Claude
$advise Should I use a monorepo or separate repos for backend and frontend?   # Codex
```

The multi-perspective analysis (SEC, PERF, ARCH, DB, etc.) catches trade-offs you might miss.

Expected output: an advisory report in `_output/advisory-logs/`.

### Step 3: Plan and execute features

Use `/plan` / `$plan` for features, then review the plan and run `/implement <id>` / `$implement <id>` to apply the changes.

Expected output: plan files and committed code.

### Step 4: Add tests with `/update-tests` / `$update-tests`

After implementing features, run `/update-tests` / `$update-tests` to generate or update unit tests following your project's conventions.

Expected output: test files with good coverage.

### Step 5: Run quality gates

Quality checks (validation, review, tests) run automatically at the end of `/implement` / `$implement`. For standalone checks before a commit, use `/check preflight` / `$check preflight`. For deeper review, use `/check review` / `$check review` which evaluates against all 16 engineering and design perspectives.

Expected output: clean quality report.

## What to do next

- [Bootstrap a greenfield project](../recipes/recipe-bootstrap-greenfield.md)
- [Plan and execute a feature](../recipes/recipe-plan-and-execute.md)
- [Run quality gates](../recipes/recipe-quality-gates.md)
- For the full framework reference, see the onboarding guide: [Claude](../claude-onboarding-guide.md) | [Codex](../codex-onboarding-guide.md)
