# Journey: Solo Product Designer -- New Product

## Who this is for

A product designer (not necessarily technical) starting a brand-new product, working solo with an AI agent as the development partner.

## Why this journey

Starting a new product from scratch is the ideal time to establish clear design intent. When there is no existing code, you shape the metacommunication -- the message your interface sends to users -- from day one, without the constraints of legacy decisions.

SEJA helps you capture that intent in structured files (`design-intent-to-be.md`) before any code is written. This means your vision is documented, reviewable, and directly used by the agent when planning and implementing features. The result is code that reflects your design decisions rather than ad-hoc technical choices.

For the concepts behind this workflow, see [What Is SEJA](../concepts/what-is-seja.md) and [The Design-Intent Lifecycle](../concepts/design-intent-lifecycle.md).

## What you'll accomplish

A bootstrapped project with conventions, conceptual design, and your first feature planned and executed.

**Journey time: ~30-40 minutes**

## Prerequisites

- Claude Code installed
- A git-initialized codebase folder
- The foundational SEJA framework extracted into it (see Part 0 of the [onboarding guide](../claude-onboarding-guide.md))

## Step-by-step walkthrough

### Step 1: Bootstrap your project with `/seed` + `/design` (~12 min)

Run `/seed .` then `/design` and walk through the interactive questionnaire. Focus on Section 0 (Quick Start) first, accept smart defaults for technical choices. The key investment is the conceptual design: describe who your users are, what they need to do, and why.

Expected output: `project/conventions.md`, `project/conceptual-design-*.md`, and other `project/*.md` files generated in `_references/`.

Example excerpt from the generated conceptual design (`design-intent-to-be.md`):

```markdown
## 1. Platform Purpose
TaskFlow is a lightweight task management tool for solo
creators. It helps users organize daily work into focused
sessions with clear start/end points.

## 2. Entity Hierarchy
Workspace
└── Project
    └── Task
        └── Session
```

### Step 2: Review what was generated (~3 min)

Read through `CLAUDE.md` (your project's identity card) and the conceptual design files. These are the foundation everything else builds on. If something doesn't look right, edit the files directly or re-run `/design`.

### Step 3: Plan your first feature with `/plan` (~3 min)

Describe what you want to build in plain language. Always review the plan before executing. Example:

```
/plan Add a home page that shows the user's recent activity
```

Review the generated plan before proceeding.

Expected output: a plan file in `_output/plans/`.

### Step 4: Execute the plan with `/implement` (~10-15 min)

Run `/implement <plan-id>` to implement the plan step by step. The agent creates code, tests, and verifies each step.

Expected output: working code committed to your project.

### Step 5: Review and share (~5 min)

Quality checks (validation, review, tests) run automatically at the end of `/implement`. Before sharing or deploying, review the quality report in the plan summary. For additional manual checks, use `/check preflight`.

## What to do next

- [Plan and execute a feature](../recipes/recipe-plan-and-execute.md)
- [Generate stakeholder material](../recipes/recipe-stakeholder-material.md) for investors or early users
- [Run quality gates](../recipes/recipe-quality-gates.md) to set up pre-commit checks
- For the full framework reference, see the [onboarding guide](../claude-onboarding-guide.md).
