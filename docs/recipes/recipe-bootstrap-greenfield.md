# Recipe: Bootstrap a Greenfield Project

## Goal

Bootstrap a brand-new project with the foundational SEJA framework from scratch.
In this collocated setup, the framework files live directly inside the codebase
(suitable for solo/greenfield work). For the separated workspace pattern, see
the [workspace setup recipe](recipe-workspace-setup.md) instead.

## Prerequisites

- Git installed
- Claude Code or Codex CLI installed
- The foundational SEJA framework available (cloned repo or downloaded ZIP from GitHub)

## Steps

1. **Create the codebase folder and initialize Git**
   ```bash
   mkdir my-project && cd my-project
   git init
   ```

2. **Copy the foundational SEJA framework into the codebase root**
   Copy `.claude/` (or `.codex/`) and `.agent-resources/` from the SEJA repository into the codebase root.

3. **Verify the structure**
   Confirm that `.claude/` or `.codex/` and `.agent-resources/` directories exist at the
   codebase root. These are the two pillars of the toolkit.

4. **Run `/quickstart .` / `$quickstart .` and choose your mode**
   - **Interactive** -- walk through a guided questionnaire (recommended for
     first-time users).
   - **From spec** -- provide an existing PRD or design document and let the
     framework extract answers automatically.

5. **Walk through the questionnaire -- focus on conceptual design**
   The conceptual design section (as-is and to-be) captures the mental model
   of your system. Spend time here -- it drives every downstream artifact.

6. **Review the generated files**
   Key outputs to inspect:
   - `CLAUDE.md` / `AGENTS.md` -- project-level instructions for the agent.
   - `project-conventions.md` -- paths, naming, tech stack settings.
   - `project-conceptual-design-as-is.md` and `project-conceptual-design-to-be.md`.

7. **Make your first commit**
   ```bash
   git add -A
   git commit -m "Bootstrap codebase with foundational SEJA framework"
   ```

## Tips

- Accept smart defaults if you are unsure about tech choices -- you can always
  change them later.
- The conceptual design is the most important investment during bootstrap.
- You can re-run `/quickstart` / `$quickstart` at any time to regenerate or update files.

## Related journeys

- [Solo Designer Greenfield](../journeys/journey-solo-designer-greenfield.md)
- [Solo Developer](../journeys/journey-solo-developer.md)
- [Small Team Kickoff](../journeys/journey-small-team-kickoff.md)
- [Agency Multi-Project](../journeys/journey-agency-multi-project.md)
