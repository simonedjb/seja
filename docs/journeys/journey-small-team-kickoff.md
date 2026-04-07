# Journey: Small Team -- New Project Kickoff

## Who this is for

A small cross-functional team (2-5 people: designer + developers, possibly a PM) starting a new project together.

## Why this journey

When multiple people work on the same product, design intent can fragment -- each person builds with slightly different assumptions about what the interface should communicate and how. SEJA provides shared conventions and a shared design-intent file that align the team around a single metacommunication vision.

The onboarding system (role families and expertise levels) ensures each team member gets guidance tailored to their background. The review perspectives provide a common vocabulary for discussing trade-offs in code reviews and planning sessions.

For the concepts behind this workflow, see [What Is SEJA](../concepts/what-is-seja.md) and [Extending the Framework](../concepts/extending-the-framework.md).

## What you'll accomplish

A shared project with conventions aligned across the team, role-based onboarding plans for each member, and a roadmap of features organized into execution waves.

## Prerequisites

- Claude Code installed for each team member
- A shared *ProjectName* codebase (git repository)
- The foundational SEJA framework extracted into it
- Agreement on the product vision

## Step-by-step walkthrough

### Step 1: Bootstrap the project together

One team member runs `/seed .` then `/design` and walks through the interactive questionnaire with the team. The conceptual design section is especially important -- it captures the shared understanding of who the users are and what the product should do. Commit the generated files so everyone shares the same conventions.

### Step 2: Onboard each team member

Run `/onboarding <role> <level>` for each person. The framework supports three role families: Builder (developers), Shaper (designers, PMs), and Guardian (QA, tech leads). Each gets a tailored 30-60-90 day plan.

For batch generation:

```
/onboarding --batch "builder L2 Alice --area backend; shaper L3 Bob"
```

Expected output: onboarding plans in `_output/onboarding-plans/`.

### Step 3: Generate a product roadmap

Run `/plan --roadmap` to decompose the conceptual design into work items organized by dependency waves. Wave 0 is foundation (models, migrations), Wave 1 is services/API, Wave 2 is frontend, etc. Review and adjust the roadmap with the team.

Expected output: a roadmap file with individual plans for each work item.

### Step 4: Execute the roadmap

Start with Wave 0 (sequential due to migration dependencies). Then execute Wave 1+ in parallel -- each developer can work on independent plans simultaneously. Use `/implement <id>` for each.

### Step 5: Establish quality rituals

Set up `/check preflight` as a pre-commit habit. Use `/check review` for code reviews. The 16 review perspectives ensure consistent quality regardless of who reviews.

### Step 6: Keep conventions alive

As the project evolves, update `project/*.md` files to reflect new decisions. Use `/advise` to document architecture decisions, and `/explain spec-drift` to detect when implementation diverges from design intent.

## What to do next

- [Bootstrap a greenfield project](../recipes/recipe-bootstrap-greenfield.md)
- [Onboard a team member](../recipes/recipe-onboard-team-member.md)
- [Plan and execute a feature](../recipes/recipe-plan-and-execute.md)
- [Run quality gates](../recipes/recipe-quality-gates.md)
- For the full framework reference, see the [onboarding guide](../claude-onboarding-guide.md).
