# Journey: Solo Product Designer -- Existing Product

## Who this is for

A product designer working on an existing product that needs evolution, working solo with an AI agent. The product already has a codebase (the *ProjectName* codebase), possibly built by someone else or by a previous team.

## Why this journey

Existing systems carry implicit design decisions -- patterns that were chosen for reasons that may no longer be documented or even remembered. Before you can improve the product, you need to surface what the current system communicates to users (the as-is state) and articulate what it should communicate instead (the to-be state).

SEJA's three-layer design-intent model (to-be, as-is, established) gives you a structured way to document this gap. The `/explain` skill helps you understand the existing system, while spec-drift detection shows you exactly where implementation has diverged from intent.

For the concepts behind this workflow, see [The Design-Intent Lifecycle](../concepts/design-intent-lifecycle.md) and [Review Perspectives and Communicability](../concepts/review-perspectives-and-communicability.md).

## What you'll accomplish

A documented understanding of the current system (as-is), a clear vision for where it should go (to-be), and a plan for the first improvement.

**Journey time: ~40-50 minutes**

## Prerequisites

- Claude Code installed
- Access to the existing *ProjectName* codebase (git repository)
- The foundational SEJA framework extracted into the codebase (or a *ProjectName* workspace -- see the [workspace setup recipe](../recipes/recipe-workspace-setup.md))

## Step-by-step walkthrough

### Step 1: Understand the existing system (~8 min)

Before changing anything, use `/explain architecture` to get a visual overview of the codebase structure. Then use `/explain data-model` to understand the data entities and relationships. Finally, use `/explain behavior <feature>` for any feature you want to understand in depth.

Expected output: explanation reports with diagrams in `_output/explained-*/`.

Example excerpt from an architecture explanation:

```markdown
## System Layers
┌─────────────────────────────────┐
│  Frontend (React SPA)           │
├─────────────────────────────────┤
│  API Layer (Express REST)       │
├─────────────────────────────────┤
│  Service Layer (business logic) │
├─────────────────────────────────┤
│  Data Layer (PostgreSQL + Redis)│
└─────────────────────────────────┘
```

### Step 2: Catalog what exists (~5 min)

Run `/advise --inventory List all API endpoints and their handlers` or `/advise --inventory List all frontend pages and components` to get a structured view of the codebase. This helps you understand the scope before planning changes.

Expected output: inventory reports in `_output/inventories/`.

### Step 3: Bootstrap the framework (~12 min)

Run `/seed .` then `/design` and walk through the questionnaire. The critical difference from greenfield: fill in the **as-is** conceptual design with what the system currently does, and the **to-be** conceptual design with what you want it to become. This gap between as-is and to-be drives all future planning.

Expected output: `project/*.md` files with the as-is/to-be distinction.

### Step 4: Get migration advice (~3 min)

Use `/advise` to discuss your evolution strategy. Example: `/advise What's the best approach to migrate from the current auth system to JWT?`. The framework evaluates from multiple perspectives (security, architecture, compatibility).

Expected output: advisory report with actionable recommendations.

### Step 5: Plan the first improvement (~3 min)

Use `/plan` targeting the highest-priority gap between as-is and to-be. Start small: pick one entity or one flow to improve. Example: `/plan Refactor the user profile page to match the to-be conceptual design`.

Expected output: a plan file.

### Step 6: Execute and verify (~10-15 min)

Run `/implement <id>`. Then use `/check review` to verify the changes against all relevant perspectives. Use `/explain spec-drift` periodically to check that your implementation stays aligned with the to-be design.

Expected output: working code and a clean review.

## What to do next

- [Map an existing codebase](../recipes/recipe-map-existing-codebase.md) (detailed recipe)
- [Plan and execute a feature](../recipes/recipe-plan-and-execute.md)
- [Run quality gates](../recipes/recipe-quality-gates.md)
- For the full framework reference, see the [onboarding guide](../claude-onboarding-guide.md).
