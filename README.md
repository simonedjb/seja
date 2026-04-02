# SEJA -- Semiotic Engineering Journeys with Agents

A public framework for agentic design and development.

This project began with explorations conducted by Clarisse Sieckenius de Souza (PUC-Rio), Gabriel DJ Barbosa (PUC-Rio and Datamint), and Simone DJ Barbosa (PUC-Rio) on redesigning and redeveloping the academic discussion forum Dialogos.

Our goal is to design a human-centered computing methodology based on semiotic engineering for agentic software design and development in a way that supports Schön's concepts of reflection-in-action, reflection-on-action, and reflection-on-practice.

## Start here

- **New to the framework?** Start with the [onboarding guide](docs/claude-onboarding-guide.md) -- an end-to-end walkthrough for product designers new to AI-assisted development
- Clone this repository or download it as ZIP from GitHub to get started
- [Journeys](docs/journeys/) -- scenario-based starting points for solo work, teams, agencies, and regulated environments
- [Recipes](docs/recipes/) -- short task-focused how-to guides

---

## Key concepts

| Term | Meaning |
|------|---------|
| **Foundational SEJA framework** | The reusable source of truth for skills, scripts, templates, agents, and guidance files. |
| ***ProjectName* workspace** | A standalone git repository that holds the framework files (`.claude/` plus `_references/`), project guidance, and generated artifacts under `_output/`. |
| ***ProjectName* codebase** | The product source code itself. In the workspace pattern, the framework points at this codebase without copying framework files into it. |

The workspace pattern is best when you want to keep framework artifacts and design history separate from product source code. The collocated pattern is best for solo or greenfield work when you want everything in one repository.

---

## Toolkit

The framework lives in `.claude/` and is configured via `CLAUDE.md` and `/slash` commands. It includes:

- **15 skills** (13 user-facing + 2 internal lifecycle hooks): `/plan`, `/implement`, `/advise`, `/check`, `/explain`, `/document`, and more
- **10 specialized agents** for code review, plan review, testing, migrations, communication, onboarding, and documentation
- **7 path-scoped rules** that activate automatically when editing matching files
- **35 validation scripts** for quality checks, analysis, and smoke testing
- **51 reference templates** in `_references/` for generating project-specific standards

---

## Recommendations

1. Run `/seed` to copy the framework, then `/design` to configure project-specific files early, so the project guidance exists before implementation work starts.
2. Treat the conceptual design and project conventions as first-class artifacts, not setup boilerplate.
3. Always review the plan before running `/implement` until the codebase and workflow feel familiar.
4. Use `/check` (validate, review, preflight) as routine safety rails.
5. Keep `CLAUDE.md` and the `project/*.md` files current as the product evolves.
6. Break larger work into small, reviewable steps.
7. Never defer security (SEC) or accessibility (A11Y) findings without an explicit decision.
8. Use metacommunication framing when the main challenge is what the interface should communicate.
9. Review plans and diffs before accepting changes.
10. Capture longer-term reasoning with roadmap, advisory, and Q&A artifacts.

---

## Choose a path

### Solo

- [Product designer, new product](docs/journeys/journey-solo-designer-greenfield.md)
- [Product designer, existing product](docs/journeys/journey-solo-designer-brownfield.md)
- [Developer, side project](docs/journeys/journey-solo-developer.md)

### Team

- [Small team kickoff](docs/journeys/journey-small-team-kickoff.md)
- [Growing team, existing product](docs/journeys/journey-growing-team.md)

### Multi-project / special contexts

- [Agency or consultancy](docs/journeys/journey-agency-multi-project.md)
- [Enterprise / regulated system](docs/journeys/journey-enterprise-evolution.md)
- [Teaching or research](docs/journeys/journey-teaching-research.md)

---

## Core recipes

- [Bootstrap a greenfield project](docs/recipes/recipe-bootstrap-greenfield.md)
- [Map an existing codebase](docs/recipes/recipe-map-existing-codebase.md)
- [Plan and execute a feature](docs/recipes/recipe-plan-and-execute.md)
- [Set up a project workspace](docs/recipes/recipe-workspace-setup.md)
- [Onboard a team member](docs/recipes/recipe-onboard-team-member.md)
- [Run quality gates](docs/recipes/recipe-quality-gates.md)
- [Generate project documentation](docs/recipes/recipe-generate-documentation.md)
- [Generate stakeholder material](docs/recipes/recipe-stakeholder-material.md)
- [Upgrade the foundational framework](docs/recipes/recipe-upgrade-framework.md)

---

## License

Licensed under [CC-BY-NC-4.0](https://creativecommons.org/licenses/by-nc/4.0/) (Creative Commons Attribution-NonCommercial 4.0 International).

You may use, copy, adapt, and share this work for **noncommercial purposes only**, provided that you give appropriate credit and indicate any changes made.

**Commercial use is not permitted under this license.** For commercial licensing inquiries, contact <simonedjb@gmail.com>.

Full terms are in [LICENSE](./LICENSE).

## Attribution

If you reuse or adapt this framework, please credit the original as:

> Based on the SEJA Design and Development Framework by Simone Diniz Junqueira Barbosa

and link back to this repository.

## Trademark notice

The project name, logo, and brand elements are not licensed for general use except as required for factual attribution. See [TRADEMARKS.md](./TRADEMARKS.md).
