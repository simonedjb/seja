# FRAMEWORK - ONBOARDING

> Role- and level-aware onboarding framework ensuring structured, progressive knowledge transfer for new project team members.
> Designed as a 4-layer progressive disclosure model with role families and expertise tiers.
> Last revised: 2026-03-28.

---

## How to Use

When onboarding a new team member, determine their **role family** and **expertise level**, then load the corresponding files to generate a tailored onboarding plan. The `/onboarding` skill automates this process.

### Determining Role Family

Each team member belongs to one (or occasionally two) role families:

| Tag | Name | File | Description |
|-----|------|------|-------------|
| BLD | Builders | [builders.md](onboarding/builders.md) | Write, deploy, and maintain code — developers, DevOps, infra engineers |
| SHP | Shapers | [shapers.md](onboarding/shapers.md) | Define what gets built and how — product managers, designers, data analysts |
| GRD | Guardians | [guardians.md](onboarding/guardians.md) | Ensure quality and alignment — QA, security engineers, tech leads, engineering managers |

Cross-functional roles (e.g., a tech lead who also codes) should load both applicable files.

### Determining Expertise Level

Each team member maps to one of three expertise levels. These levels consolidate the original 5-level Dreyfus-aligned taxonomy into three actionable bands: guided contributor, independent expert, and organizational leader.

| Tag | Name | File | Characteristics |
|-----|------|------|-----------------|
| L1 | Contributor | [l1-contributor.md](onboarding/l1-contributor.md) | Junior to mid-level IC (0-5 years); needs guidance on *how*, *what*, and *where* |
| L2 | Expert | [l2-expert.md](onboarding/l2-expert.md) | Senior (5-10 years); needs context on *why* and *trade-offs* |
| L3 | Leader | [l3-leader.md](onboarding/l3-leader.md) | Staff/Principal/Manager (10+ years); needs *organizational context* and *team dynamics* |

### Onboarding Layers

Material is organized in 4 progressive layers. All layers reference content from role and level files:

| Layer | Name | Audience | Timing |
|-------|------|----------|--------|
| **0** | Universal Foundation | All roles, all levels | Day 1 |
| **1** | Role-Specific Context | By role family | Week 1 |
| **2** | Level-Specific Depth | By expertise level | Weeks 1-4 |
| **3** | Living Knowledge | All roles (ongoing) | 30-60-90 days and beyond |

### Loading Strategy

For a given team member:

1. Always load **Layer 0** content (embedded in the skill, not a separate file).
2. Load the **role family file(s)** matching the member's role (Layer 1).
3. Load the **expertise level file** matching the member's seniority (Layer 2).
4. Layer 3 is generated dynamically from project state (briefs, ADRs, plans).

### Role-Level Shortcuts

Common combinations for quick reference:

| Scenario | Role | Level | Key Focus |
|----------|------|-------|-----------|
| Junior frontend dev | BLD | L1 | Guided tutorial, pair programming, code review receiving |
| Mid-level backend dev | BLD | L1 | Project conventions, architecture boundaries, independent features |
| Senior backend dev | BLD | L2 | Architecture decisions, system design rationale, technical debt |
| New product manager | SHP | L1 | Domain context, user research, roadmap, metrics |
| New QA engineer | GRD | L1 | Test strategy, coverage expectations, review perspective framework |
| Tech lead joining | BLD+GRD | L3 | Team dynamics, process ownership, cross-team dependencies |
| Designer with AI tools | SHP+BLD | L1 | Conceptual design, AI-assisted workflow, metacommunication |

---

## Onboarding KPIs

Track onboarding effectiveness with these metrics (aligned with DX perspective P1/P3):

| Metric | Target | Measured At |
|--------|--------|-------------|
| Time-to-environment-setup | < 30 minutes | Day 1 |
| Time-to-first-commit | < 1 week | Week 1 |
| Time-to-first-review | < 2 weeks | Week 2 |
| Time-to-independent-contribution | < 30 days | Month 1 |
| Onboarding satisfaction score | >= 4/5 | Day 30 |

---

## Output Structure

Onboarding plans are saved in date-versioned folders under `${ONBOARDING_PLANS_DIR}/`:

```
${ONBOARDING_PLANS_DIR}/
├── 2026-03-28/
│   ├── onboarding-0001-alice-bld-l1.md
│   ├── onboarding-0002-bob-shp-l2.md
│   └── onboarding-0003-grd-l1.md
├── 2026-04-15/
│   ├── onboarding-0004-carol-bld-l1.md
│   └── onboarding-0005-dave-bld+grd-l3.md
```

- **Date folder** (`YYYY-MM-DD` UTC): Groups all plans generated on the same date. When the team evolves or the project changes, regenerating plans on a new date creates a new version without overwriting the old ones.
- **Sequential ID**: Global across all date folders (not reset per folder).
- **Batch generation**: Use `--all` to generate all 9 combinations (3 roles x 3 levels), `--all-levels <role>` for all levels of one role, `--all-roles <level>` for all roles at one level, or `--batch` for custom spec lists. See the `/onboarding` skill for details.

---

## Relationship to Other Framework Components

- **Review perspectives** (`general/review-perspectives.md`): The DX perspective's P1 question on structured onboarding paths is directly addressed by this framework.
- **Conceptual design** (`project/conceptual-design-*.md`): Shapers onboarding draws heavily from these files.
- **Metacommunication** (`project/metacomm-*.md`): Shapers and Guardians need to understand the designer's intent.
- **Coding standards** (`project/standards.md §§ Backend and Frontend`): Builders onboarding references these.
- **Skills system** (`.claude/skills/`): The onboarding skill orchestrates all of the above.
