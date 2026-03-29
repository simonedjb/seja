# Journey: Teaching and Research

## Who this is for

An educator teaching software engineering, HCI, or semiotic engineering, or a researcher studying design processes and AI-assisted development.

## What you'll accomplish

A framework setup that serves as both a pedagogical tool and a research instrument, with the ability to explain system behavior, analyze design decisions, and generate research-oriented material.

## Prerequisites

- Claude Code or Codex CLI installed
- A codebase to analyze (can be a sample project or a real one)
- The foundational SEJA framework extracted into it

## Step-by-step walkthrough

### Step 1: Bootstrap a sample project

Run `/quickstart .` / `$quickstart .` on a sample project (or use an existing one). For teaching, you might prepare a project with intentional design issues for students to discover. For research, use a real project that illustrates the phenomena you want to study.

Expected output: a project with the full framework configured.

### Step 2: Explore explanation capabilities

The `/explain` / `$explain` skill has multiple modes that serve different pedagogical purposes:

- `/explain architecture` / `$explain architecture` -- generates visual diagrams of the system structure (good for teaching system design)
- `/explain data-model` / `$explain data-model` -- maps entity relationships (good for teaching database design)
- `/explain behavior <feature>` / `$explain behavior <feature>` -- traces how a feature works end-to-end (good for teaching code comprehension)
- `/explain spec-drift` / `$explain spec-drift` -- compares design intent with implementation (good for teaching about technical debt and design erosion)

Expected output: explanation reports with diagrams in `_output/explained-*/`.

### Step 3: Use multi-perspective analysis

The `/advise` / `$advise` skill evaluates questions against 16 engineering and design perspectives (SEC, PERF, DB, API, ARCH, UX, A11Y, VIS, etc.). This models structured decision-making for students and provides rich data for researchers. Example:

```
/advise What are the trade-offs of using server-side rendering vs. client-side rendering for this project?   # Claude
$advise What are the trade-offs of using server-side rendering vs. client-side rendering for this project?   # Codex
```

Expected output: advisory reports with perspective-by-perspective analysis.

### Step 4: Study the review process

The `/check review` / `$check review` skill applies the 16 perspectives to code changes. Each perspective has Essential (P0) and Deep-dive (P1-P4) tiers, with conflict resolution rules (SEC wins by default, A11Y is non-negotiable). This structured review process is itself a pedagogical tool for teaching code review practices.

Expected output: a review report organized by perspective and priority tier.

### Step 5: Generate research material

Use `/communication ACD` / `$communication ACD` (academic audience segment) to generate research-oriented material about the project and framework. This includes the theoretical foundation in semiotic engineering, the framework architecture, and the research agenda.

Expected output: academic communication material in the output directory.

## What to do next

- [Map an existing codebase](../recipes/recipe-map-existing-codebase.md) (for analyzing sample projects)
- [Run quality gates](../recipes/recipe-quality-gates.md) (for teaching review practices)
- [Generate stakeholder material](../recipes/recipe-stakeholder-material.md)
- For the full framework reference, see the onboarding guide: [Claude](../claude-onboarding-guide.md) | [Codex](../codex-onboarding-guide.md)
- For the theoretical foundation, see the semiotic engineering concepts in Part 2 of the onboarding guides (section 2.2, References)
