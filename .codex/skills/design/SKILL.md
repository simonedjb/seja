---
name: design
description: "Define or update project design — stack, conventions, domain model, conceptual design, and standards. Use when user mentions 'design', 'design project', 'configure project', 'update design', or 'project setup'."
argument-hint: "[--generate-spec] [--add-docs] [spec-file-path]"
metadata:
  last-updated: 2026-03-31 16:30:00
  version: 1.0.0
  category: planning
  context_budget: standard
  questionnaire_version: 3
  references:
    - general/report-conventions.md
    - general/review-perspectives.md
    - general/shared-definitions.md
---

## Quick Guide

**What it does**: Configures the SEJA framework for your project. First-time: walks you through a questionnaire (or parses a spec file) to define your stack, domain model, and conventions, then generates all project-specific reference files. Ongoing: lets you update any section of your project design.

**Example**:
> You: /design
> Agent: Detects no project definitions exist, walks you through the questionnaire, generates all `project/` reference files, CLAUDE.md, and rules.

> You: /design (when project already configured)
> Agent: Shows current design summary, offers to update specific sections.

**When to use**: After `/seed` to configure a new project. Or anytime you want to update your project's design foundations (stack, domain model, standards, metacommunication).

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `[spec-file-path]` | No | Path to a pre-filled spec file for automated configuration |
| `--generate-spec` | No | Generate a blank spec skeleton to fill out offline |
| `--add-docs` | No | Jump directly to the Add Documentation Templates mode |

# Design

> **`/design`** defines WHAT to build and WHY. **`/plan`** defines HOW to build it and WHY those "hows." Design produces project definitions (`_references/project/`); plans consume them to produce actionable implementation steps.

## Overview

This skill manages the project's design foundations — the `project/` files in `_references/` that define stack choices, conventions, conceptual design, metacommunication, and standards. It serves both initial configuration (after `/seed`) and ongoing design evolution.

## Detection Logic

On invocation, check whether `project/conventions.md` exists in `_references/`:

- If `--add-docs` is passed, go directly to Mode 3 (Add Documentation Templates)
- **Not found** → Initial design: run the full questionnaire or parse a spec file
- **Found** → Design update: show what's defined, offer to review or update specific sections

---

## Initial Design (no project definitions exist)

### Mode Selection

If no argument is provided, present a usage menu:

1. **Interactive** — walk through questions one by one (best for first-time users)
2. **From spec file** — provide a pre-filled spec file (best for experienced users)
3. **Generate blank spec** — create a skeleton to fill out offline

If the argument includes `--generate-spec`, skip the menu and go directly to Mode 4.
If a spec file path is provided, go directly to Mode 2.

### Mode 1: Interactive Questionnaire

1. **Check for in-progress design**: Look for `specs/design-in-progress.md`. If found, ask: "Resume previous design session or start fresh?"

2. **Run the questionnaire**: Read `template/questionnaire.md` and walk the user through it:
   - If Section metacomm-message (M.1) has been answered, parse it before proceeding: extract project name hint, description, target user type, and primary use case. When the agent reaches questions 0.1, 0.2, 2.1, 2.10, and 2.11, present the extracted value as: "From your metacomm message, I suggest: [extracted value]. Accept or override?"
   - Start with **Section M (metacomm-message)** (optional but recommended) and **Section 0 (quick-start)** -- 10 minimum questions for a working skeleton
   - For each question, present the options with their pros/cons and a recommendation
   - Record all answers
   - After Section quick-start, ask if the user wants to continue with the remaining sections or use defaults

3. **Interruptibility**: At any point, if the user wants to stop:
   - Save all answers collected so far to `specs/design-in-progress.md`
   - Print: "Progress saved. Run `/design` again to resume."

4. **Skip to defaults**: At any point, the user can say "use defaults for everything else":
   - Fill remaining fields from the defaults table (see Field Classification)
   - Proceed to template instantiation

5. **Mandatory conceptual design**: Section conceptual-design (Section 2) core questions are **required** for all projects. The agent must not allow the user to skip these by accepting defaults. At minimum, the user must provide:
   - Entity hierarchy (2.3) — what the system manages
   - Permission levels (2.6) — who can do what
   - Greenfield/evolving status (2.9) — determines as-is/to-be population
   - Metacommunication message (2.10) — what the product communicates to users. Record **verbatim** (see `general/shared-definitions.md` § Verbatim rule).
   If Section metacomm-message (M.1) was answered, use it as the default for 2.10 and present it for confirmation. The verbatim rule applies to the final confirmed answer.

   For **brownfield** projects, additionally require:
   - Existing tech stack (2.13)
   - Migration constraints (2.14)

6. **Codebase scaffolding question**: After stack decisions are made, ask:
   > "Should I create the initial project structure (directories, config files, entry points) for your chosen stack?"
   - If yes, run the project scaffolding tasks (see Project Scaffolding section)
   - If no, skip

7. **Instantiate templates**: Using the questionnaire answers, create project-specific files in `_references/`:
   - Copy `template/conventions.md` to `project/conventions.md`, substituting answers
   - Copy `template/constitution.md` to `project/constitution.md` (Required -- always generated for new projects. Content may be customized but file cannot be skipped.)
   - Copy `template/design-intent-to-be.md` to `project/design-intent-to-be.md` (**I/you phrasing rule** for Part II metacommunication sections)
   - Copy `template/design-intent-established.md` to `project/design-intent-established.md` (empty archive — no entries yet for greenfield; for brownfield projects, note that the designer may populate it manually from their existing design decisions)
   - **For evolving (brownfield) projects only**: also copy as-is templates (including `template/cd-as-is-changelog.md` to `project/cd-as-is-changelog.md`)
   - **For greenfield projects**: do **not** instantiate as-is files (post-skill will create the changelog on first plan execution)
   - Copy `template/backend-standards.md` to `project/backend-standards.md`
   - Copy `template/frontend-standards.md` to `project/frontend-standards.md`
   - Copy `template/i18n-standards.md` to `project/i18n-standards.md`, if i18n is needed
   - Copy `template/security-checklists.md` to `project/security-checklists.md`
   - Copy `template/testing-standards.md` to `project/testing-standards.md`
   - Copy `template/ux-design-standards.md` to `project/ux-design-standards.md`
   - Copy `template/graphic-ui-design-standards.md` to `project/graphic-ui-design-standards.md`
   - Copy `template/user-research-new.md` to `project/user-research-new.md`, pre-populating persona and user community entries from section 2.11 answers if provided
   - Copy `template/journey-maps.md` to `project/journey-maps.md`, seeding the key journey list from the metacommunication intent in section 2.10
   - Copy agent YAML templates (`template/agent/constraints.yaml`, `entities.yaml`, `permissions.yaml`, `spec-checks.yaml`) to `project/agent/`
   - Based on Section docs-templates (Section 10) answers: copy selected `template/docs/*.md` files to `project/docs/` in `_references/`. If the user chose "defaults", copy only the 3 recommended templates (readme.md, contextual-help.md, adr.md). If "skip", copy none.
   - Customize `template/settings.json` to `.claude/settings.json` with actual paths

8. **Generate CLAUDE.md**: Create a `CLAUDE.md` in the codebase root with:
   - Project name, stack summary, build/run commands
   - Architecture overview
   - Key conventions
   - `@` references to the project-specific reference files

9. **Generate rules files**: Create `.claude/rules/` files appropriate for the chosen stack.

10. **Generate smoke test infrastructure** (if backend framework is not "none"):
    - `smoke_test_registry.json` from `template/smoke-test-registry.json`
    - `smoke_test_api.py` — thin runner importing `smoke_test_core`
    - If E2E configured: `e2e/smoke.spec.ts`

11. **Secrets check**: Run `python .claude/skills/scripts/check_secrets.py` to verify no secrets are staged.

12. **Clean up**: Remove `specs/design-in-progress.md` if it exists.

13. **Summary**: Output a checklist of everything created and any manual steps needed.

14. **Review & next steps**: Present the generated project specification files and offer review:

    | File | Controls |
    |------|----------|
    | `project/conventions.md` | Directory paths, variable definitions |
    | `project/constitution.md` | Immutable principles, security invariants |
    | `project/design-intent-to-be.md` | Conceptual design (Part I) + metacommunication (Part II) |
    | `project/design-intent-established.md` | Processed design intent archive (human-maintained) |
    | `project/user-research-new.md` | User personas, goals, and unprocessed research insights |
    | `project/journey-maps.md` | Intended user journeys through key product flows |
    | `project/backend-standards.md` | Backend architecture conventions |
    | `project/frontend-standards.md` | Frontend architecture conventions |
    | `project/ux-design-standards.md` | Interaction patterns, accessibility |
    | `project/graphic-ui-design-standards.md` | Visual identity, colors, typography |
    | `project/testing-standards.md` | Test frameworks and conventions |
    | `project/i18n-standards.md` | Internationalization conventions |
    | `project/security-checklists.md` | Security checklists, validation constants |
    | `project/docs/*.md` | Documentation structure templates |

    **Questionnaire-to-output mapping** (include in summary so the designer knows which answers produced which files):

    | Questionnaire Section | Generated File |
    |---|---|
    | 2.3 Entity hierarchy, 2.6 Permissions, 2.10 Metacomm | `project/design-intent-to-be.md` |
    | 2.1, 2.11 (product description, user community) | `project/user-research-new.md` |
    | 2.10 (metacomm intent) | `project/journey-maps.md` |
    | Stack choices (T2) | `project/conventions.md` |
    | Immutable principles (T2) | `project/constitution.md` |
    | Backend patterns (T3) | `project/backend-standards.md` |
    | Frontend patterns (T3) | `project/frontend-standards.md` |
    | UX patterns (T1) | `project/ux-design-standards.md` |
    | Visual design (T1) | `project/graphic-ui-design-standards.md` |
    | Testing conventions (T3) | `project/testing-standards.md` |
    | i18n conventions (T3) | `project/i18n-standards.md` |
    | Security constraints (T3) | `project/security-checklists.md` |

    Then offer: 1) Review specs now, 2) Generate roadmap (`/plan --roadmap`), 3) Done for now.

### Mode 2: From Spec File

1. **Locate spec file**: Use the provided path, or look in `specs/`.

2. **Read and parse the spec file**: Same parsing rules as the questionnaire Mode 2.

3. **Version check**: Compare against `questionnaire_version`.

4. **Validate all at once**: Report provided, missing required, missing with defaults, and ambiguous fields.

5. **Targeted Q&A**: Ask for missing required fields. Enforce **mandatory conceptual design** fields.

6. **Offer detailed sections**: Present Sections 1-9 as a numbered multi-select list.

7. **Instantiate templates**: Same as Mode 1, step 7.

8. **Generate CLAUDE.md, rules, smoke tests**: Same as Mode 1, steps 8-10.

9. **Secrets check**: Same as Mode 1, step 11.

10. **Preserve spec**: Copy to `specs/project-spec-YYYY-MM-DD HH.MM UTC.md`.

11. **Summary + Review**: Same as Mode 1, steps 13-14.

### Mode 3: Add Documentation Templates

Triggered when `--add-docs` is passed.

1. **Verify project exists**: Check that `project/conventions.md` exists in `_references/`. If not, abort: "No project design found. Run `/design` first."

2. **Check existing docs**: Check if `project/docs/` already exists in `_references/`. If it does, list the templates already instantiated and ask: "Some documentation templates are already set up. Add more, or replace all?"

3. **Present template checklist**: Read all `template/docs/*.md` files. For each, extract the `recommended` and `depends_on` fields from the YAML frontmatter. Present the list to the user:
   - Mark recommended templates with "(Recommended)"
   - For templates with `depends_on` that matches the project's app type (from `project/ux-design-standards.md` if it exists), add "(Suggested for your app type)"
   - Let the user select which templates to instantiate

4. **Instantiate selected templates**: Copy selected `template/docs/*.md` files to `project/docs/` in `_references/`.

5. **Summary**: List the instantiated documentation templates and suggest next steps:
   > "Documentation templates added. To populate them, work through the placeholders in each file. For contextual help, create one help page per UI screen."

### Mode 4: Generate Blank Spec

1. **Create specs/ subfolder** if it does not exist.

2. **Generate the spec file**: Copy `template/project-spec.md` to `specs/project-spec-YYYY-MM-DD HH.MM UTC.md`.

3. **Output next steps**:
   > Spec file created at `<path>`.
   >
   > Fill in your choices — each field has inline comments. Required fields are marked.
   >
   > When ready, run `/design <spec-file-path>` to apply it.

---

## Design Update (project definitions exist)

When `project/conventions.md` already exists:

1. **Show current design summary**: Read `project/conventions.md` and display the current stack choices.

2. **Offer update options**:
   > "Your project design is already configured. What would you like to update?"
   >
   > 1. Stack choices (backend, frontend, database, etc.)
   > 2. Conceptual design (entities, permissions, relationships)
   > 3. Metacommunication (designer intent, feature messaging)
   > 4. Backend standards
   > 5. Frontend standards
   > 6. UX design standards
   > 7. Graphic/UI design standards
   > 8. i18n configuration
   > 9. Security checklists
   > 10. Testing standards
   > 11. Constitution (non-negotiable principles)
   > 12. Full reconfiguration (re-run questionnaire from scratch)

3. **Apply updates**: Read current `project/` file, present current values, walk through changes. Update preserving unmodified sections.

4. **Regenerate dependent files**: If stack choices changed, offer to regenerate CLAUDE.md and rules.

---

## Project Scaffolding

When the user opts into codebase scaffolding, offer the task catalog based on stack choices. See the Backend Package Map, Frontend Package Map, and .env Templates sections below.

Tasks: Create source dirs, Python venv, backend requirements, Node.js init, scaffold frontend, Tailwind config, .env files, migration tool init, E2E test dir, .gitignore.

---

## Field Classification

### Required (agent must ask if missing)

- `name` (Project) — project display name
- `description` (Project) — what the application does
- `framework` (Backend) — or explicit "none" if no backend
- `framework` (Frontend) — or explicit "none" if no frontend

### Required conceptual design (agent must ask if missing)

- Entity hierarchy (questionnaire 2.3)
- Permission levels (questionnaire 2.6)
- Greenfield/evolving status (questionnaire 2.9)
- Metacommunication message (questionnaire 2.10)

### Additionally required for brownfield projects

- Existing tech stack (questionnaire 2.13)
- Migration constraints (questionnaire 2.14)

### Required with sensible defaults (inform user of default if missing)

| Field | Default | Inference Rule |
|-------|---------|----------------|
| `output_dir` | `_output` | Static default |
| `backend` dir | `backend` | Static default |
| `frontend` dir | `frontend` | Static default |
| `orm` | Inferred | SQLAlchemy for Flask/FastAPI, Django ORM for Django, Prisma for Express/NestJS |
| `database` | `PostgreSQL` | Static default |
| `migrations` | Inferred | Alembic for SQLAlchemy, Django Migrations for Django ORM, Prisma Migrate for Prisma |
| `validation` | Inferred | Marshmallow for Flask, Pydantic for FastAPI, Django Forms for Django, Zod for Express/NestJS |
| `auth` | `JWT (HttpOnly cookies)` | Static default |
| `primary_locale` | `en-US` | Static default |
| `build_tool` | `Vite` | Vite for React/Vue/Svelte |
| `css` | `Tailwind CSS` | Static default |
| `state` | `React Context + hooks` | Static default |
| `data_fetching` | `TanStack Query` | Static default |
| `http_client` | `Axios` | Static default |
| `router` | `React Router v7` | For React only |
| `backend_test` | Inferred | pytest for Python, Jest for Node.js |
| `frontend_test` | Inferred | Vitest with Vite, Jest otherwise |
| `e2e` | `Playwright` | Static default |
| `wcag` | `AA` | Static default |

### Optional (omit silently if not provided)

- `rich_text_editor`, `dark_mode`, `primary_color`, `secondary_color`
- `sans_font`, `serif_font`, `context_providers`, `initial_components`
- `secondary_locale`, `backend_default_locale`, `localized_emails`, `translatable_entities`
- `access_token_expiry`, `refresh_token_expiry`, `rate_limit`
- `file_uploads`, `import_export`, `integration_suite`, `e2e_base_url`
- Conceptual design details beyond 2.3/2.6/2.10 (free-form)
- Security validation constants (free-form)

---

## Versioning

- The current questionnaire version is declared in this skill's frontmatter (`questionnaire_version`) and in `template/questionnaire.md`.
- Spec files declare their version via the `version:` field on the first non-comment line.
- When versions differ, consult the Version History table in `template/questionnaire.md`.
- When adding new questions:
  1. Increment `questionnaire_version` in both this skill's frontmatter and `template/questionnaire.md`
  2. Add the new fields to `template/project-spec.md`
  3. Add an entry to the Version History table
  4. Add default values to the Field Classification table above
