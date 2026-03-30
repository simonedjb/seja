# Journey: Solo Product Designer -- New Product

## Who this is for

A product designer (not necessarily technical) starting a brand-new product, working solo with an AI agent as the development partner.

## What you'll accomplish

A bootstrapped project with conventions, conceptual design, and your first feature planned and executed.

## Prerequisites

- Claude Code or Codex CLI installed
- A git-initialized codebase folder
- The foundational SEJA framework extracted into it (see Part 0 of the onboarding guide: [Claude](../claude-onboarding-guide.md) | [Codex](../codex-onboarding-guide.md))

## Step-by-step walkthrough

### Step 1: Bootstrap your project with `/quickstart` / `$quickstart`

Run `/quickstart .` / `$quickstart .` and walk through the interactive questionnaire. Focus on Section 0 (Quick Start) first, accept smart defaults for technical choices. The key investment is the conceptual design: describe who your users are, what they need to do, and why.

Expected output: `project-conventions.md`, `project-conceptual-design-*.md`, and other `project-*.md` files generated in `.agent-resources/`.

### Step 2: Review what was generated

Read through `CLAUDE.md` / `AGENTS.md` (your project's identity card) and the conceptual design files. These are the foundation everything else builds on. If something doesn't look right, edit the files directly or re-run `/quickstart` / `$quickstart`.

### Step 3: Plan your first feature with `/make-plan` / `$make-plan`

Describe what you want to build in plain language. Always review the plan before executing. Example:

```
/make-plan Add a home page that shows the user's recent activity   # Claude
$make-plan Add a home page that shows the user's recent activity   # Codex
```

Review the generated plan before proceeding.

Expected output: a plan file in `_output/plans/`.

### Step 4: Execute the plan with `/execute-plan` / `$execute-plan`

Run `/execute-plan <plan-id>` / `$execute-plan <plan-id>` to implement the plan step by step. The agent creates code, tests, and verifies each step.

Expected output: working code committed to your project.

### Step 5: Review and share

Quality checks (validation, review, tests) run automatically at the end of `/execute-plan` / `$execute-plan`. Before sharing or deploying, review the quality report in the plan summary. For additional manual checks, use `/check preflight` / `$check preflight`.

## What to do next

- [Bootstrap a greenfield project](../recipes/recipe-bootstrap-greenfield.md) (detailed recipe)
- [Plan and execute a feature](../recipes/recipe-plan-and-execute.md)
- [Generate stakeholder material](../recipes/recipe-stakeholder-material.md) for investors or early users
- For the full framework reference, see the onboarding guide: [Claude](../claude-onboarding-guide.md) | [Codex](../codex-onboarding-guide.md)
