# Recipe: Bootstrap a Greenfield Project

Use this recipe when starting a brand-new project from scratch with no existing codebase.

## Goal

Bootstrap a brand-new project with the foundational SEJA framework from scratch.
In this collocated setup, the framework files live directly inside the codebase
(suitable for solo/greenfield work). For the separated workspace pattern, see
the [workspace setup recipe](recipe-workspace-setup.md) instead.

**Total time: ~20 minutes** (less if you accept defaults)

## Prerequisites

- Git installed
- Claude Code installed
- The foundational SEJA framework available (cloned repo or downloaded ZIP from GitHub)

## Steps

1. **Create the codebase folder and initialize Git** (~1 min)
   ```bash
   mkdir my-project && cd my-project
   git init
   ```

2. **Copy the foundational SEJA framework into the codebase root** (~1 min)
   Copy `.claude/` and `_references/` from the SEJA repository you cloned in the prerequisites into the codebase root.

3. **Verify the structure** (~1 min)
   Confirm that `.claude/` and `_references/` directories exist at the
   codebase root. These are the two pillars of the toolkit.

4. **Run `/seed .` then `/design` and choose your mode** (~1 min)
   - **Interactive** -- walk through a guided questionnaire (recommended for
     first-time users).
   - **From spec** -- provide an existing PRD or design document and let the
     framework extract answers automatically.

   <details>
   <summary>For designers</summary>

   The questionnaire asks about your product vision, who your users are, and how they interact with the system. Your answers become the foundation for every design decision the framework makes later. Focus on describing the experience you want users to have.

   </details>

   <details>
   <summary>For developers</summary>

   The questionnaire populates `_references/project/` files: `conventions.md` (stack, paths, naming), `design-intent-to-be.md` (domain model, entity hierarchy), and standards files for backend, frontend, testing, security, and i18n. These files are consumed by every downstream skill.

   </details>

5. **Walk through the questionnaire -- focus on conceptual design** (~10 min)
   The conceptual design section (as-is and to-be) captures the mental model
   of your system. Spend time here -- it drives every downstream artifact.

6. **Review the generated specs** (~3 min)

   <details>
   <summary>For designers</summary>

   Check that the generated files reflect your product vision. Look at the conceptual design (entity hierarchy, user roles) and the UX and visual design standards. If something does not match your intent, this is the cheapest time to correct it -- before any code is written.

   </details>

   <details>
   <summary>For developers</summary>

   Verify `project/conventions.md` for correct directory paths and stack settings. Check `project/design-intent-to-be.md` for the entity hierarchy and permission model. Review `project/backend-standards.md`, `project/frontend-standards.md`, and `project/testing-standards.md` for framework and pattern choices.

   </details>

   After the summary, the design skill offers three options:
   - **Review specs now** -- walk through each `project/*` file to verify and adjust.
   - **Generate roadmap** -- auto-derive a development roadmap from your specs.
   - **Done for now** -- review offline, generate roadmap later.

   Key outputs to inspect:
   - `CLAUDE.md` -- project-level instructions for the agent.
   - `project/conventions.md` -- paths, naming, tech stack settings.
   - `project/conceptual-design-as-is.md` and `project/design-intent-to-be.md`.
   - `project/ux-design-standards.md` and `project/graphic-ui-design-standards.md`.

   Example excerpt from `conventions.md` after generation:

   ```markdown
   ## Project Identity
   | Variable       | Value     | Description            |
   |----------------|-----------|------------------------|
   | `PROJECT_NAME` | TaskFlow  | Project display name   |

   ## Directory Structure
   | Variable     | Value     | Description                        |
   |--------------|-----------|-------------------------------------|
   | `SKILLS_DIR` | `.claude/skills` | Root directory for skill definitions |
   | `OUTPUT_DIR`  | `_output` | Root directory for generated artifacts |
   ```

   Example excerpt from `design-intent-to-be.md`:

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

7. **Generate a roadmap** (~2 min, optional but recommended)
   If you chose "Generate roadmap" in step 6, the design skill creates a roadmap spec
   in `_output/roadmaps/` with themes derived from your conceptual design and
   metacommunication. You can then run `/plan --roadmap`
   to turn it into executable plans.

8. **Make your first commit** (~1 min)
   ```bash
   git add -A
   git commit -m "Bootstrap codebase with foundational SEJA framework"
   ```

   <details>
   <summary>For designers</summary>

   This saves a snapshot of your project setup. If anything goes wrong later, you can always return to this clean starting point. Think of it as a save point in a game.

   </details>

   <details>
   <summary>For developers</summary>

   This commit captures the framework scaffold (`.claude/`, `_references/`) and all generated `project/` files. It establishes the baseline for `git diff` during future plan execution and quality checks. The implement skill creates a `pre-plan-<id>` rollback branch from HEAD before each plan runs.

   </details>

## Tips

- Accept smart defaults if you are unsure about tech choices -- you can always
  change them later.
- The conceptual design is the most important investment during bootstrap.
- Review specs before generating a roadmap -- changes are cheapest at the spec level.
- You can re-run `/design` at any time to regenerate or update files.

## Related journeys

- [Solo Designer Greenfield](../journeys/journey-solo-designer-greenfield.md)
- [Solo Developer](../journeys/journey-solo-developer.md)
- [Small Team Kickoff](../journeys/journey-small-team-kickoff.md)
- [Agency Multi-Project](../journeys/journey-agency-multi-project.md)
