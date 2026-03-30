# Journey: Growing Team -- Existing Product

## Who this is for

A medium-sized team (5-15 people) with specialized roles (frontend, backend, QA, PM, designer) working on an established product that needs continued evolution.

## What you'll accomplish

A shared framework with role-based onboarding, documented architecture, spec-drift detection, and consistent quality across the team.

## Prerequisites

- Claude Code or Codex CLI installed for team members
- Access to the existing *ProjectName* codebase (git repository)
- The foundational SEJA framework available (quickstart kit or repo)
- For teams, the [workspace setup](../recipes/recipe-workspace-setup.md) pattern is recommended so each developer has an independent *ProjectName* workspace

## Step-by-step walkthrough

### Step 1: Map the existing system

Before onboarding anyone, use `/explain architecture` / `$explain architecture` and `/explain data-model` / `$explain data-model` to create documentation of the current system. This becomes the shared understanding that all team members reference.

Expected output: architecture and data model explanations in `_output/`.

### Step 2: Bootstrap with the workspace pattern

For teams, the recommended setup is the workspace pattern: each developer gets their own *ProjectName* workspace (initialized as a git repo) containing the framework files and `_output/`. Run `/quickstart --workspace` / `$quickstart --workspace` from the foundational SEJA framework to create each workspace automatically. This gives each developer version-controlled design history (plans, advisories, briefs) independent of the shared *ProjectName* codebase, which is accessed via `--add-dir`. See the [workspace setup recipe](../recipes/recipe-workspace-setup.md) for details. One person sets up the conventions first, then the team shares `project/conventions.md`.

### Step 3: Onboard team members by role

Run `/onboarding <role> <level>` / `$onboarding <role> <level>` for each team member. The framework supports: Builders (developers, L1-L5), Shapers (designers/PMs, L1-L5), and Guardians (QA/tech leads, L1-L5). Use batch mode for onboarding waves: `/onboarding --batch "builder L2 Alice --area backend; guardian L3 Carlos"` / `$onboarding --batch "builder L2 Alice --area backend; guardian L3 Carlos"`.

Expected output: tailored onboarding plans in `_output/onboarding-plans/`.

### Step 4: Detect spec drift

Run `/explain spec-drift` / `$explain spec-drift` to compare the as-is implementation against the to-be design. This identifies where the product has diverged from intent and helps prioritize what to fix.

Expected output: spec drift analysis with actionable recommendations.

### Step 5: Establish review practices

Use `/check review` / `$check review` for structured code reviews against 16 engineering and design perspectives. The perspective shortcuts by plan prefix (e.g., FEATURE-B gets SEC/DB/API/ARCH/TEST/PERF) ensure domain-appropriate reviews automatically. Use `/check preflight` / `$check preflight` as a pre-commit gate.

### Step 6: Plan evolution

Use `/advise` / `$advise` for migration strategies. Use `/make-plan --roadmap` / `$make-plan --roadmap` to decompose the gap between as-is and to-be into dependency-aware execution waves. Assign plans to team members and execute in parallel where possible.

## What to do next

- [Map an existing codebase](../recipes/recipe-map-existing-codebase.md)
- [Set up a project workspace](../recipes/recipe-workspace-setup.md)
- [Onboard a team member](../recipes/recipe-onboard-team-member.md)
- [Run quality gates](../recipes/recipe-quality-gates.md)
- For the full framework reference, see the onboarding guide: [Claude](../claude-onboarding-guide.md) | [Codex](../codex-onboarding-guide.md)
