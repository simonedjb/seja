# SEJA -- Semiotic Engineering Journeys with Agents

A public framework for agentic design and development.

---

## Start here

- [Codex onboarding guide](seja-codex-onboarding-guide.md) -- the main end-to-end guide for a product designer new to AI-assisted development
- [Quickstart kits](quickstart-kits/) -- downloadable framework exports, including `seja-codex-quickstart-kit.zip`
- [Journeys](journeys/) -- scenario-based starting points for solo work, teams, agencies, and regulated environments
- [Recipes](recipes/) -- short task-focused how-to guides

---

## Key concepts

| Term | Meaning |
|------|---------|
| **Foundational SEJA framework** | The reusable source of truth for skills, scripts, templates, agents, and guidance files. |
| ***ProjectName* workspace** | A standalone git repository that holds the framework files (`.codex/`, `.agent-resources/`), project guidance, and generated artifacts under `_output/`. |
| ***ProjectName* codebase** | The product source code itself. In the workspace pattern, the framework points at this codebase without copying framework files into it. |

The workspace pattern is best when you want to keep framework artifacts and design history separate from product source code. The collocated pattern is best for solo or greenfield work when you want everything in one repository.

---

## Which toolkit?

This repository still contains **two parallel toolkits**:

- `.codex/`: the Codex-native toolkit, driven by `AGENTS.md`
- `.claude/`: the original Claude-oriented source toolkit, retained as the upstream source of truth for shared framework behavior

If you are choosing where to start, use the Codex toolkit unless you specifically need the Claude-oriented flow. The public docs and quickstart packaging here are maintained around the Codex path.

---

## Shared recommendations

1. Run `$quickstart` early so the project guidance exists before implementation work starts.
2. Treat the conceptual design and project conventions as first-class artifacts, not setup boilerplate.
3. Always review the plan before running `$execute-plan` until the codebase and workflow feel familiar.
4. Use `$check validate`, `$check review`, and `$check preflight` as routine safety rails.
5. Keep `AGENTS.md` and the `project-*.md` files current as the product evolves.
6. Break larger work into small, reviewable steps.
7. Never defer SEC or A11Y findings without an explicit decision.
8. Use metacommunication framing when the main challenge is what the interface should communicate.
9. Review plans and diffs before accepting changes.
10. Capture longer-term reasoning with roadmap, advisory, and Q&A artifacts.

---

## Choose a path

### Solo

- [Product designer, new product](journeys/journey-solo-designer-greenfield.md)
- [Product designer, existing product](journeys/journey-solo-designer-brownfield.md)
- [Developer, side project](journeys/journey-solo-developer.md)

### Team

- [Small team kickoff](journeys/journey-small-team-kickoff.md)
- [Growing team, existing product](journeys/journey-growing-team.md)

### Multi-project / special contexts

- [Agency or consultancy](journeys/journey-agency-multi-project.md)
- [Enterprise / regulated system](journeys/journey-enterprise-evolution.md)
- [Teaching or research](journeys/journey-teaching-research.md)

---

## Core recipes

- [Bootstrap a greenfield project](recipes/recipe-bootstrap-greenfield.md)
- [Map an existing codebase](recipes/recipe-map-existing-codebase.md)
- [Plan and execute a feature](recipes/recipe-plan-and-execute.md)
- [Set up a project workspace](recipes/recipe-workspace-setup.md)
- [Onboard a team member](recipes/recipe-onboard-team-member.md)
- [Run quality gates](recipes/recipe-quality-gates.md)
- [Generate stakeholder material](recipes/recipe-stakeholder-material.md)
- [Upgrade the foundational framework](recipes/recipe-upgrade-framework.md)

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
