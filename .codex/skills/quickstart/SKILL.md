---
name: quickstart
description: "Bootstrap a new project's .codex directory from templates."
argument-hint: <target-directory> [--generate-spec | --upgrade | --workspace]
metadata:
  last-updated: 2026-03-29 00:15:00
  version: 1.0.0
  category: utility
  context_budget: standard
  questionnaire_version: 2
---

## Quick Guide

**What it does**: Sets up a new project with the SEJA framework. Bootstrap mode creates the directory structure, configuration files, and project-specific references from templates.

**Example**:
> You: $quickstart .
> Agent: Walks you through a questionnaire about your project (tech stack, team structure, goals), then generates all the configuration and reference files you need.

**When to use**: You are starting a brand new project (bootstrap), upgrading an existing project's framework, or creating a workspace alongside an existing codebase.

# Quickstart

## Overview

This skill bootstraps a new project's `.codex/` directory using the template files from this project. It supports three modes: interactive questionnaire, pre-filled spec file, or generating a blank spec skeleton. Codex workspace permissions are managed outside the repo, so this workflow generates guidance files and prompts rather than a local settings manifest.

## Mode Selection

If no argument is provided, or if the argument is only a target directory, use the ask the user directly tool to ask which mode to use (if ask the user directly is not available, present as a numbered text list), with these options:
- "Interactive -- walk through questions one by one (best for first-time users)"
- "From spec file -- provide a pre-filled quickstart-spec.md (best for experienced users)"
- "Generate blank spec -- create a skeleton to fill out offline"
- "Upgrade -- update an existing project's framework to a newer version"
- "Create workspace -- set up a project workspace from the foundational SEJA framework for working alongside an existing codebase"

Then ask for the target codebase directory (if not already provided as an argument).

If the argument includes `--generate-spec`, skip the menu and go directly to Mode 3.
If the argument includes `--upgrade`, skip the menu and go directly to Mode 4.
If the argument includes `--workspace`, skip the menu and go directly to Mode 5.

---

## Mode 1: Interactive

The original interactive flow. Walk the user through the questionnaire to gather project-specific information, then instantiate templates.

### Steps

1. **Verify target directory**: Check that the target exists. If a `.codex/` directory already exists, warn the user and ask whether to overwrite or merge. **Do NOT `git init` or create any git repository at this point** — the workspace/codebase separation question in step 5 determines which directories get `git init`. Initializing the target now would create nested repos if the user later chooses separation. Git initialization happens in step 5 (after the separation decision) or, if the user chooses no separation, after step 5 completes.

2. **Create directory structure**: Create the following in the target directory:
   ```
   _references/
   .codex/
   .codex/skills/
   .codex/skills/scripts/
   .codex/rules/
   .codex/agents/
   ```

3. **Copy general (reusable) files** from this project's `_references/` to the target's `_references/`:
   - All files under `general/` (as-is, no modification needed)
   - All files under `template/` (these will be instantiated in step 6)

4. **Copy skill definitions**: Copy all skill `SKILL.md` files to the target. These are project-independent and work with any project that follows the conventions.

5. **Run the questionnaire**: Read `template/questionnaire.md` and interactively walk the user through it:
   - Start with **Section 0 (Quick Start)** — 8 minimum questions for a skeleton
   - For each question, present the options with their pros/cons and a recommendation
   - Record all answers
   - **Workspace routing** — After question 0.3, regardless of greenfield or brownfield, offer workspace/codebase separation:
     - **Greenfield framing**: *"For greenfield projects, the SEJA framework recommends separating the workspace (framework files, design artifacts) from the codebase (source code). This keeps the codebase clean and the design history version-controlled independently. Would you like to create separate workspace and codebase folders?"*
     - **Brownfield framing**: *"The SEJA framework can either install directly into your existing codebase, or create a separate workspace alongside it. A separate workspace keeps your codebase clean — no `.codex/` or `_references/` folders in your repo. Would you like to create a separate workspace?"*
     - If **yes (greenfield)**: Ask for the workspace directory name (default: `<project-name>-workspace`) and codebase directory name (default: `<project-name>`). Both will be created as subdirectories of the target directory. Then:
        - Create `<target>/<workspace-dir>/` and `git init` it
        - Create `<target>/<codebase-dir>/` and `git init` it
        - Redirect all framework file creation (steps 2-4, 6-11) to `<target>/<workspace-dir>/`
        - Set `BACKEND_DIR` and `FRONTEND_DIR` in `project/conventions.md` to **absolute paths** pointing into `<target>/<codebase-dir>/`
        - Set `OUTPUT_DIR` to `<target>/<workspace-dir>/_output`
        - Generate launcher scripts (`launch.sh` / `launch.bat`) in `<target>/<workspace-dir>/` that invoke `codex --add-dir <codebase-dir>`
        - Redirect scaffolding tasks (step 12, tasks A-K) to `<target>/<codebase-dir>/`
     - If **yes (brownfield)**: Ask for the workspace directory path (default: `<target>-workspace` as a sibling directory). Then:
        - **Detect embedded framework** — Check whether the codebase already contains SEJA framework files (`.claude/`, `.codex/`, `_references/`, `_output/` or custom output dir). If any are found:
          1. **Inventory before touching anything.** The codebase's `.claude/` (or `.codex/`) and `_references/` may contain a mix of SEJA framework files and custom (non-SEJA) additions. Classify each item into three categories:
             - **SEJA framework** → move to workspace: files whose names match known SEJA skill names (from the foundational framework's skill list), known rule filenames (`backend.md`, `frontend.md`, `i18n.md`, `migrations.md`, `tests.md`, `e2e.md`, `framework-structure.md`), known agent filenames, `CHANGELOG.md`, `CHEATSHEET.md`, `VERSION`, and the `scripts/` directory. In `_references/`: the `general/` and `template/` subdirectories.
             - **SEJA project data** (files in `_references/project/`) → move to workspace: these are SEJA-generated references (conventions, conceptual design, metacomm, standards) that belong with the framework, not in the codebase.
             - **Custom (non-SEJA)** → stay in codebase: any skill, rule, agent, or config file that does NOT match a known SEJA name. Also `settings.json` and `settings.local.json` (may contain project-specific hooks and permissions).
          2. Report the classification: *"I found SEJA framework files, SEJA project data, and custom (non-SEJA) files in your codebase. SEJA files (N items) and project data (P items) will be migrated to the workspace. Custom files (M items) will stay in the codebase. Here's the breakdown: ..."*
          3. If **yes (migrate)**: Move SEJA framework files and `project/` data to `<workspace-dir>/`. **Leave custom (non-SEJA) skills, rules, agents, and config in the codebase.** Update path references in migrated `project/conventions.md` to use absolute paths. If an `AGENTS.md` exists at the codebase root referencing framework files, update its paths or note it as a manual step.
          4. If **no (fresh start)**: Ignore the embedded files and proceed with a clean workspace. Warn: *"The old framework files will remain in your codebase. You may want to remove them manually after verifying the workspace setup."*
        - **Reconcile `project/` files** — After migration (or when setting up a brownfield project that never had SEJA), compare any existing `project/` files against the current `template/` files to identify missing or outdated references. For each `template/` file:
          - If the corresponding `project/` file **does not exist** → flag it for creation during template instantiation (step 6). The agent will use the mandatory conceptual design answers (Section 2) plus codebase inspection to populate it.
          - If the corresponding `project/` file **exists but is from an older template version** (missing sections, deprecated fields, or structural differences vs. the current template) → show the user what changed and offer to regenerate it. Preserve any user-authored content by reading the existing file first and carrying forward relevant values into the new template structure. Present a before/after summary so the user can confirm.
          - If the corresponding `project/` file **exists and is current** → keep as-is, no action needed.
        - Create `<workspace-dir>/` and `git init` it
        - Redirect all framework file creation (steps 2-4, 6-11) to `<workspace-dir>/`
        - Set `BACKEND_DIR` and `FRONTEND_DIR` in `project/conventions.md` to **absolute paths** pointing into the existing codebase at `<target>/`
        - Set `OUTPUT_DIR` to `<workspace-dir>/_output`
        - Generate launcher scripts (`launch.sh` / `launch.bat`) in `<workspace-dir>/` that invoke `codex --add-dir <target>`
        - Skip scaffolding tasks that create source directories (task A) — the codebase already exists
     - If **no**: Initialize the target as a git repository (`git init`) if it is not already one. Proceed with the standard in-place setup (all files in the target directory). For brownfield projects, still run the **Reconcile `project/` files** step against any existing `_references/` in the codebase.
   - After Section 0, ask if the user wants to continue with detailed sections (1-9) or use defaults
   - **Mandatory conceptual design** — Section 2 core questions are **required** for all projects, not optional. The agent must not allow the user to skip these by accepting defaults. Without a conceptual model, the framework cannot produce meaningful plans or design references. At minimum, the user must provide:
     - Entity hierarchy (2.3) — what the system manages
     - Permission levels (2.6) — who can do what
     - Greenfield/evolving status (2.9) — determines whether as-is and to-be are populated identically or differently
     - Metacommunication message (2.10) — what the product communicates to users
     If the user tries to skip Section 2, remind them: *"The conceptual model is the foundation for all planning and code generation. Without it, the framework cannot produce meaningful plans or design references. Please describe at least your entities, permissions, and what the product communicates to users."*
     For **brownfield** projects, additionally require:
     - Existing tech stack (2.13) — what is already in place
     - Migration constraints (2.14) — what cannot change

6. **Instantiate templates**: Using the questionnaire answers, create project-specific files in `_references/`:
   - Copy `template/conventions.md` to `project/conventions.md`, substituting answers
   - Copy `template/conceptual-design-as-is.md` to `project/conceptual-design-as-is.md`, filling in current-state conceptual design
   - Copy `template/conceptual-design-to-be.md` to `project/conceptual-design-to-be.md`, filling in target-state conceptual design
   - Copy `template/metacomm-as-is.md` to `project/metacomm-as-is.md`, filling in current-state metacommunication
   - Copy `template/metacomm-to-be.md` to `project/metacomm-to-be.md`, filling in target-state metacommunication
   - **Note**: For greenfield projects, populate as-is and to-be identically. For evolving products, populate to-be with the target state and as-is with the current implementation.
   - Copy `template/backend-standards.md` to `project/backend-standards.md`, selecting relevant sections
   - Copy `template/frontend-standards.md` to `project/frontend-standards.md`, selecting relevant sections
   - Copy `template/i18n-standards.md` to `project/i18n-standards.md`, if i18n is needed
   - Copy `template/security-checklists.md` to `project/security-checklists.md`
   - Copy `template/testing-standards.md` to `project/testing-standards.md`
   - Copy `template/ux-design-standards.md` to `project/ux-design-standards.md`, filling in UX design choices
   - Copy `template/graphic-ui-design-standards.md` to `project/graphic-ui-design-standards.md`, filling in visual/UI design choices
   - Copy `template/agents-md.md` to `AGENTS.md` and substitute the stack-specific placeholders

7. **Generate AGENTS.md**: Create an `AGENTS.md` in the codebase root with:
   - Project name, stack summary, build/run commands
   - Architecture overview
   - Key conventions
   - `@` references to the project-specific reference files

8. **Generate rules files**: Create `.codex/rules/` files appropriate for the chosen stack:
   - Backend rules (if backend exists)
   - Frontend rules (if frontend exists)
   - i18n rules (if i18n is configured)

9. **Copy agents**: Copy agent definitions, adjusting references to use the correct filenames.

10. **Generate smoke test infrastructure** (if backend framework is not "none"):
    1. `smoke_test_core.py` is already copied with the other scripts (step 3/4). No additional action needed — it is framework-agnostic.
    2. Generate `smoke_test_registry.json` from `template/smoke-test-registry.json`:
       - Set `framework` from `backend.framework` (lowercase: "flask", "django", "fastapi", "express")
       - Set `auth.method` from `backend.auth`
       - Set `test_config` based on framework: Flask→"unit_testing", Django→"test", FastAPI→"testing"
       - Set `auth.user_model_path` based on framework conventions (e.g., Flask+SQLAlchemy→"app.models.user.User", Django→"django.contrib.auth.models.User")
       - For each entity listed in the Domain section, generate a CRUD endpoint group with standard REST routes (`POST /api/<plural>`, `GET /api/<plural>`, `GET /api/<plural>/{id}`, `PUT /api/<plural>/{id}`, `DELETE /api/<plural>/{id}`)
       - Include auth setup endpoints (register, login, profile) and destructive auth endpoints (logout, password change) if auth is configured
       - Save to `<target>/.codex/skills/scripts/smoke_test_registry.json`
    3. Generate `smoke_test_api.py` — a thin runner (~80 lines) that imports `smoke_test_core`, loads the registry, and creates a framework-appropriate test client. The template is the same for all Flask projects; adapt the client factory for Django/FastAPI. Save to `<target>/.codex/skills/scripts/smoke_test_api.py`.
    4. If `testing.e2e` is not "none", generate `<target>/e2e/smoke.spec.ts` — a Playwright spec with:
       - Error collectors (console.error, pageerror, requestfailed)
       - A test for each major page route from the conceptual design
       - Uses pre-authenticated fixtures if auth is configured
       - If `testing.e2e == "none"`, skip this file entirely.

11. **Generate initial briefs.md**: Create an empty briefs file in the output directory.

12. **Project scaffolding**: Offer to perform environment setup tasks that would otherwise be manual. Present the applicable tasks as a numbered checklist (based on the questionnaire answers) and ask the user which ones to execute. Execute selected tasks sequentially, reporting progress after each.

    **Task catalog** (include only tasks whose preconditions are met):

    | # | Task | Precondition | Actions |
    |---|------|-------------|---------|
    | A | **Create source directories** | Always | Create `<target>/<backend_dir>/` and `<target>/<frontend_dir>/` (and any additional source dirs from Section 1). Create `<target>/<output_dir>/`. |
    | B | **Create Python virtual environment** | Backend is Python (Flask / FastAPI / Django) | Run `python -m venv <target>/<backend_dir>/venv`. |
    | C | **Generate and install backend requirements** | Backend is Python AND task B was selected | Generate `<target>/<backend_dir>/requirements.txt` with packages matching the chosen stack (see Backend Package Map below). Run `<target>/<backend_dir>/venv/Scripts/pip install -r <target>/<backend_dir>/requirements.txt` (Windows) or `<target>/<backend_dir>/venv/bin/pip install -r ...` (Unix). |
    | D | **Initialize backend package** | Backend is Node.js (Express / NestJS) | Run `npm init -y` inside `<target>/<backend_dir>/`. Run `npm install` with the packages from the Backend Package Map. |
    | E | **Scaffold frontend project** | Frontend is not "none" | Run the appropriate scaffolding command inside `<target>/`: Vite → `npm create vite@latest <frontend_dir> -- --template react-ts` (adjust template for Vue/Svelte); Next.js → `npx create-next-app@latest <frontend_dir> --typescript --tailwind --app`. |
    | F | **Install additional frontend dependencies** | Task E was selected | Inside `<target>/<frontend_dir>/`, run `npm install` with the packages from the Frontend Package Map. |
    | G | **Configure Tailwind CSS** | `css` is Tailwind AND task E was selected | Inside `<target>/<frontend_dir>/`, run `npx tailwindcss init -p`. Update `tailwind.config.js` content paths to include `./src/**/*.{js,ts,jsx,tsx}`. Add Tailwind directives to the main CSS file. |
    | H | **Create .env files** | Always | Generate `<target>/<backend_dir>/.env` and `<target>/<frontend_dir>/.env` with stack-appropriate variables (see .env Templates below). Generate a matching `.env.example` alongside each `.env` (with placeholder values instead of secrets). Add `.env` to `<target>/.gitignore` (create the file if it does not exist). |
    | I | **Initialize migration tool** | Backend has a migration tool configured | Alembic → run `<venv>/bin/alembic init <target>/<backend_dir>/migrations` and patch `alembic.ini` to read `sqlalchemy.url` from the `.env` `DATABASE_URL`. Django → `python manage.py migrate` is a manual step (skip — just note in summary). Prisma → run `npx prisma init` inside `<target>/<backend_dir>/`. |
    | J | **Initialize E2E test directory** | `e2e` is not "none" | Create `<target>/e2e/`. Playwright → run `npm init -y && npm install -D @playwright/test && npx playwright install` inside `<target>/e2e/`. Cypress → run `npm init -y && npm install -D cypress` inside `<target>/e2e/`. |
    | K | **Create initial .gitignore** | Always | Generate `<target>/.gitignore` (or append to it if it exists) with entries for the chosen stack: Python (`__pycache__/`, `*.pyc`, `venv/`), Node (`node_modules/`, `dist/`, `.next/`), environment (`.env`), IDE (`.vscode/`, `.idea/`), OS (`.DS_Store`, `Thumbs.db`). |

    **Backend Package Map** (derive from questionnaire answers):

    | Stack Choice | Python packages | Node.js packages |
    |-------------|----------------|-----------------|
    | Flask | `flask` | — |
    | FastAPI | `fastapi`, `uvicorn[standard]` | — |
    | Django | `django`, `djangorestframework` | — |
    | Express | — | `express`, `cors`, `dotenv` |
    | NestJS | — | `@nestjs/cli`, `@nestjs/core`, `@nestjs/common` |
    | SQLAlchemy | `sqlalchemy`, `psycopg2-binary` (for PostgreSQL), `pymysql` (for MySQL) | — |
    | Django ORM | (included with Django) | — |
    | Prisma | — | `prisma`, `@prisma/client` |
    | Alembic | `alembic` | — |
    | Marshmallow | `marshmallow`, `flask-marshmallow`, `marshmallow-sqlalchemy` | — |
    | Pydantic | `pydantic` (included with FastAPI) | — |
    | JWT auth | `pyjwt`, `flask-jwt-extended` (Flask) or `python-jose` (FastAPI) | `jsonwebtoken`, `cookie-parser` |
    | pytest | `pytest`, `pytest-cov` | — |
    | Jest | — | `jest`, `ts-jest`, `@types/jest` |
    | Rate limiting | `flask-limiter` (Flask), `slowapi` (FastAPI) | `express-rate-limit` |
    | CORS | `flask-cors` (Flask) | `cors` |
    | i18n | `flask-babel` (Flask), `django-modeltranslation` (Django) | `i18next` |
    | `python-dotenv` | Always for Python backends | — |

    **Frontend Package Map** (derive from questionnaire answers):

    | Stack Choice | Packages |
    |-------------|----------|
    | React Router v7 | `react-router-dom` |
    | TanStack Router | `@tanstack/react-router` |
    | TanStack Query | `@tanstack/react-query`, `@tanstack/react-query-devtools` |
    | SWR | `swr` |
    | Axios | `axios` |
    | Tailwind CSS | `tailwindcss`, `postcss`, `autoprefixer` |
    | Zustand | `zustand` |
    | Redux Toolkit | `@reduxjs/toolkit`, `react-redux` |
    | Lexical | `lexical`, `@lexical/react` |
    | TipTap | `@tiptap/react`, `@tiptap/starter-kit` |
    | Vitest | `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom` |
    | Jest | `jest`, `@testing-library/react`, `@testing-library/jest-dom` |

    **.env Templates** (populate based on stack):

    Backend `.env`:
    ```
    FLASK_APP=app                     # Flask only
    FLASK_ENV=development             # Flask only
    DJANGO_SETTINGS_MODULE=config.settings  # Django only
    DATABASE_URL=postgresql://localhost:5432/<project_name_snake_case>
    SECRET_KEY=change-me-in-production
    JWT_SECRET_KEY=change-me-in-production   # if JWT auth
    CORS_ORIGINS=http://localhost:5173       # Vite default port
    ```

    Frontend `.env`:
    ```
    VITE_API_BASE_URL=http://localhost:5000/api   # Vite
    NEXT_PUBLIC_API_BASE_URL=http://localhost:5000/api  # Next.js
    ```

    **Execution rules**:
    - Before executing, confirm the list with the user. They may deselect tasks or reorder.
    - If a task fails, report the error and continue with the remaining tasks. Do not abort the entire sequence.
    - After all selected tasks complete, collect any that failed and list them in the summary (step 13) as manual steps still needed.
    - Use the platform-appropriate commands (detect via `$OSTYPE` or Node's `process.platform`): forward slashes, `venv/Scripts/` on Windows vs `venv/bin/` on Unix, etc.

12b. **Secrets check**: Run `python .codex/skills/scripts/check_secrets.py <target>` to verify no `.env` files or files containing secrets are staged for commit. If the check flags any files, warn the user and list the flagged files. This is a safety net — step 12H already creates `.gitignore` entries, but this catches any files that slipped through.

13. **Summary**: Output a checklist of everything created, including both the `.codex/` framework files (steps 2–11) and any scaffolding tasks performed (step 12). If workspace/codebase separation was chosen (greenfield routing in step 5), clearly show the two-directory layout and how to launch Codex from the workspace. List remaining manual steps only for tasks the user declined or that failed. Typical remaining manual steps:
    - Creating/configuring the database itself (e.g., `createdb <name>`)
    - Running initial migrations (if the migration tool was initialized but the DB does not exist yet)
    - Configuring external services (OAuth providers, email, etc.)
    - Replacing placeholder secrets in `.env` files
    - (If workspace pattern) Start Codex from the workspace: `codex --add-dir <codebase-dir>`

14. **Review & next steps**: After the summary, present the generated project specification files and offer the user a chance to review them before moving on. This is the last opportunity to correct design decisions before they propagate into plans and code.

    **Present the review checklist:**
    > *"I've generated the following project specification files from your answers. I recommend reviewing them before generating a roadmap — these are the foundation for all planning and code generation."*

    List the `project/` files with a one-line description of what each controls:

    | File | Controls | Key things to verify |
    |------|----------|---------------------|
    | `project/conventions.md` | Directory paths, variable definitions | Paths are correct, especially for workspace pattern |
    | `project/conceptual-design-as-is.md` | Entity hierarchy, permissions, domain concepts | Entities and their relationships match your mental model |
    | `project/conceptual-design-to-be.md` | Target design (same as as-is for greenfield) | Greenfield: should be identical to as-is |
    | `project/metacomm-as-is.md` | Current metacommunication record | Designer intent per feature is accurate |
    | `project/metacomm-to-be.md` | Target metacommunication with full EMT | Global vision and per-feature intentions are complete |
    | `project/backend-standards.md` | Backend architecture conventions | Framework, ORM, auth patterns match your stack |
    | `project/frontend-standards.md` | Frontend architecture conventions | Components, routing, state management patterns |
    | `project/ux-design-standards.md` | Interaction patterns, accessibility, responsive | Navigation, forms, keyboard shortcuts, WCAG level |
    | `project/graphic-ui-design-standards.md` | Visual identity, colors, typography, motion | Brand colors, font, spacing, icon set |
    | `project/testing-standards.md` | Test frameworks and conventions | Test patterns match your stack |
    | `project/i18n-standards.md` | Internationalization conventions | Locales, translation approach |
    | `project/security-checklists.md` | Security checklists, validation constants | Field limits, auth constants |

    **Then offer next steps:**
    > *"What would you like to do next?"*

    Present as a numbered list:
    1. **Review specs now** — *"I'll walk you through each file so you can verify and adjust. Changes are easiest to make now, before any code is generated."*
    2. **Generate roadmap** — *"I'll generate a development roadmap from your specs and offer to turn it into executable plans via `$make-plan --roadmap`."*
    3. **Done for now** — *"You can review the files at your own pace and run `$make-plan --roadmap` when ready."*

    **If the user chooses "Review specs now" (option 1):**
    - Walk through each `project/` file, presenting a brief summary of the key decisions captured.
    - For each file, ask: *"Does this look right, or would you like to change anything?"*
    - If the user requests changes, edit the file in place.
    - After the review, return to the next-steps menu (offer options 2 and 3).

    **If the user chooses "Generate roadmap" (option 2):**
    1. Read `template/roadmap-spec.md` for the spec format.
    2. Derive themes and work items from the conceptual design (entities, permissions, domain concepts, import/export, i18n) and the metacommunication message (features the designer committed to).
    3. Structure the roadmap as follows:
       - **Theme: Foundation** (P0) — data models, database setup, app factory, auth endpoints. One work item per entity (User + auth, then each domain entity). These are `technical` type, `backend` scope.
       - **Theme: Core UI** (P0) — frontend shell (routing, layout, auth pages), then one work item per entity's CRUD UI. These are `design` type, `fullstack` scope.
       - **Theme: Domain Features** (P1) — one work item per domain-specific concept from Section 2.5 / the metacomm (e.g., priorities, alerts, postpone, recurring tasks, keyboard shortcuts). Classify as `design` if user-facing, `technical` if internal.
       - **Theme: Collaboration & Sharing** (P1) — sharing, permissions, mentions, notifications. These are `design` type, `fullstack` scope.
       - **Theme: Data & Integration** (P2) — import/export, localization polish, backup/restore. These are `technical` type.
    4. Set dependency chains: auth before CRUD, backend before frontend for each entity, foundation before domain features.
    5. Fill in the Parallel Execution Strategy section with waves derived from the dependency graph.
    6. Set the Product Vision from the questionnaire's description + metacomm summary.
    7. Set the Roadmap Horizon to a reasonable default based on project scope (e.g., "Initial MVP — 4-6 weeks" for a small project, "Phase 1 — Q2 2026" for larger ones).
    8. Add a Constraints section reflecting the project's stack and design decisions (e.g., "WCAG AAA compliance on all UI", "All strings must be i18n-ready").
    9. Save to `<output_dir>/roadmaps/roadmap-spec-YYYY-MM-DD HH.MM UTC.md`.
    10. Present the roadmap to the user for review.
    11. Offer: *"Would you like to run `$make-plan --roadmap` to generate executable plans from this roadmap?"*
    12. If the user declines, note: *"You can run `$make-plan --roadmap --from-spec <path>` later to generate plans."*

    **If the user chooses "Done for now" (option 3):**
    - Remind: *"You can review the spec files in `_references/` at any time. When ready, run `$make-plan --roadmap` to generate a development roadmap and executable plans."*

---

## Mode 2: From Spec File

For experienced users who pre-fill a spec file with their stack choices. The agent parses the spec, validates it, asks targeted questions for gaps, and proceeds with template instantiation.

### Steps

1. **Verify target directory**: Same as Mode 1, step 1.

2. **Locate spec file**: Ask the user for the path to their spec file. Look in the target's `specs/` subfolder first if no path is given.

3. **Read and parse the spec file**: Extract all key-value pairs and free-form sections. Parsing rules:
   - Lines starting with `- key:` are key-value pairs (value is everything after the first colon, trimmed)
   - Lines starting with `## ` are section headers
   - Lines inside `<!-- ... -->` are HTML comments (ignored during parsing)
   - Lines starting with `version:` (no dash prefix) are the version field
   - Empty values mean "not provided" (use default or ask)
   - Free-form sections (Domain, Security) capture all non-comment, non-key-value text as prose

4. **Version check**: Compare the spec's `version` field against the current `questionnaire_version` (defined in this skill's frontmatter and in `template/questionnaire.md`). If there is a mismatch:
   - Consult the Version History table in `template/questionnaire.md` to identify new, changed, or removed fields between versions
   - Show the user what changed
   - Offer to migrate: apply defaults for new fields, warn about removed fields
   - If the user declines migration, proceed with best-effort parsing

5. **Validate all at once**: Produce a validation report listing:
   - **Provided fields** — with their values (confirmation)
   - **Missing required fields** — must be asked (see Field Classification below)
   - **Missing fields with defaults** — list the defaults that will be used
   - **Ambiguous or conflicting values** — e.g., chose Django ORM with Flask framework, or Prisma with Python backend
   - Present the full report to the user before asking any questions

6. **Targeted Q&A**: For each missing required field or conflict identified in step 5, ask the user. Group related questions when possible (e.g., ask about backend framework and ORM together). Present options with pros/cons from the questionnaire. Apply the **Workspace routing** logic from Mode 1, step 5 — offer workspace/codebase separation before proceeding to directory creation. Enforce the **Mandatory conceptual design** fields regardless of project mode (greenfield or brownfield).

7. **Offer detailed sections**: After resolving core fields, present:
   > "Your spec covers the core stack decisions. The following detailed sections can refine the generated files. Which would you like to explore?"

   Present Sections 1-7 as a numbered multi-select list:
   1. Project Conventions (directory paths, additional source dirs)
   2. Conceptual Design (entities, permissions, authoring, import/export)
   3. Frontend Standards (design choices, contexts, components)
   4. Backend Standards (extensions, file uploads, import/export)
   5. Testing Standards (integration suite, E2E base URL)
   6. i18n Standards (locale rationale, localized emails, translatable entities)
   7. Security Checklists (validation constants, applicable checklists)

   Walk through selected sections interactively. Skip unselected sections (use defaults).

8. **Create directory structure**: Same as Mode 1, step 2.

9. **Copy general files**: Same as Mode 1, step 3.

10. **Copy skill definitions**: Same as Mode 1, step 4.

11. **Instantiate templates**: Using the combined spec + Q&A answers. Same as Mode 1, step 6.

12. **Generate AGENTS.md**: Same as Mode 1, step 7.

13. **Generate rules files**: Same as Mode 1, step 8.

14. **Copy agents**: Same as Mode 1, step 9.

15. **Generate initial briefs.md**: Same as Mode 1, step 11.

16. **Project scaffolding**: Same as Mode 1, step 12. Use the combined spec + Q&A answers to determine which tasks to offer.

16b. **Secrets check**: Same as Mode 1 step 12b.

17. **Preserve spec**: Copy the original spec file to `<target>/specs/quickstart-spec-YYYY-MM-DD HH.MM UTC.md` (creating `specs/` if it does not exist). If the spec was already in `specs/`, leave it in place (do not duplicate).

18. **Summary**: Same as Mode 1, step 13. Additionally, note the preserved spec file location.

19. **Review & next steps**: Same as Mode 1, step 14. Use the combined spec + Q&A answers for the review and roadmap generation.

---

## Mode 3: Generate Blank Spec

Creates a blank spec skeleton for the user to fill out offline.

### Steps

1. **Determine target directory**: Ask for the target directory if not provided as an argument.

2. **Create specs/ subfolder**: Create `<target>/specs/` if it does not exist.

3. **Generate the spec file**: Copy `template/quickstart-spec.md` (from this project's `_references/`) to `<target>/specs/quickstart-spec-YYYY-MM-DD HH.MM UTC.md`. Substitute the `{datetime}` placeholder in the header comment with the current UTC datetime.

4. **Output next steps**:
   > Spec file created at `<path>`.
   >
   > Fill in your choices — each field has inline comments explaining the options, pros/cons, and recommendations. Required fields are marked; everything else has sensible defaults.
   >
   > When ready, run `$quickstart <target-dir>` and select "From spec file".

---

## Field Classification

Used during Mode 2 validation (step 5) to determine which fields are required, defaultable, or optional.

### Required (agent must ask if missing)

- `name` (Project) — project display name
- `description` (Project) — what the application does
- `framework` (Backend) — or explicit "none" if no backend
- `framework` (Frontend) — or explicit "none" if no frontend

### Required with sensible defaults (inform user of default if missing)

| Field | Default | Inference Rule |
|-------|---------|----------------|
| `output_dir` | `_output` | Static default. This is the directory where all generated artifacts (plans, advisory logs, scripts, etc.) are stored. The name is configurable — e.g., `_loom` in the Dialogos project. Choose a name prefixed with `_` so it sorts to the top and is clearly distinct from source code. |
| `backend` dir | `backend` | Static default |
| `frontend` dir | `frontend` | Static default |
| `orm` | Inferred | SQLAlchemy for Flask/FastAPI, Django ORM for Django, Prisma for Express/NestJS |
| `database` | `PostgreSQL` | Static default |
| `migrations` | Inferred | Alembic for SQLAlchemy, Django Migrations for Django ORM, Prisma Migrate for Prisma |
| `validation` | Inferred | Marshmallow for Flask, Pydantic for FastAPI, Django Forms for Django, Zod for Express/NestJS |
| `auth` | `JWT (HttpOnly cookies)` | Static default |
| `primary_locale` | `en-US` | Static default |
| `build_tool` | `Vite` | Vite for React/Vue/Svelte; Next.js only if explicitly chosen |
| `css` | `Tailwind CSS` | Static default |
| `state` | `React Context + hooks` | Static default |
| `data_fetching` | `TanStack Query` | Static default |
| `http_client` | `Axios` | Static default |
| `router` | `React Router v7` | For React only |
| `backend_test` | Inferred | pytest for Python, Jest for Node.js |
| `frontend_test` | Inferred | Vitest with Vite, Jest otherwise |
| `e2e` | `Playwright` | Static default |
| `wcag` | `AA` | Static default |

### Required conceptual design (agent must ask if missing, regardless of project mode)

- Entity hierarchy (questionnaire 2.3) — what the system manages
- Permission levels (questionnaire 2.6) — who can do what
- Greenfield/evolving status (questionnaire 2.9) — determines as-is/to-be population
- Metacommunication message (questionnaire 2.10) — what the product communicates to users

### Additionally required for brownfield projects

- Existing tech stack (questionnaire 2.13)
- Migration constraints (questionnaire 2.14)

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
- When versions differ, consult the Version History table in `template/questionnaire.md` to identify changes and offer migration.
- When adding new questions to the questionnaire:
  1. Increment `questionnaire_version` in both this skill's frontmatter and `template/questionnaire.md`
  2. Add the new fields to `template/quickstart-spec.md`
  3. Add an entry to the Version History table describing the changes
  4. Add default values for the new fields to the Field Classification table above

---

## Version Bump Protocol

When releasing a new framework version, follow this procedure:

### When to bump

| Change type | Version bump | Examples |
|-------------|-------------|----------|
| Breaking schema changes | **Major** (X.0.0) | Renamed/removed convention variables, changed SKILL.md frontmatter schema, restructured directories |
| New skills, variables, or features | **Minor** (x.Y.0) | Added new skill, added convention variables with defaults, new script |
| Bug fixes, documentation | **Patch** (x.y.Z) | Fixed script bug, updated SKILL.md instructions, corrected template |

### What to update

1. `.codex/skills/VERSION` — update the `version:` line
2. `.codex/CHANGELOG.md` — add a new version entry at the top with Added/Changed/Removed sections
3. `questionnaire_version` in `$quickstart` frontmatter and `template/questionnaire.md` — increment only if the questionnaire changed (new questions, removed questions, changed defaults)

### How to verify

Run `$check validate` after bumping to ensure all framework files are consistent.

---

## Mode 4: Upgrade

Upgrades an existing project's framework files to a newer version, preserving project-specific data.

Triggered by `$quickstart --upgrade` or selected from the mode menu.

If the argument includes `--upgrade`, skip the menu and go directly to Mode 4.

### Steps

1. **Fetch latest framework**: Clone the public SEJA framework from `https://github.com/simonedjb/seja` into a temporary directory using `git clone --depth 1 https://github.com/simonedjb/seja <temp-dir>`. If git clone fails (e.g., network issues), fall back to asking the user for a local path to the source directory.

2. **Run the upgrade script**: Execute `python .codex/skills/scripts/upgrade_framework.py --from <temp-dir> --target <target>`. If the user wants a preview first, add `--dry-run`. After the script completes (whether dry-run or actual), clean up the temporary directory.

3. **Review the summary**: Present the script's output to the user. Highlight:
   - Version change (e.g., "1.0.0 → 2.0.0")
   - Whether old layout migration occurred
   - New convention variables available
   - Any manual steps needed (path reference updates, AGENTS.md refresh)

4. **Offer follow-up actions**:
   - If new convention variables were found: "Would you like to add these variables to your `project/conventions.md`? I can walk you through the values."
   - If old path references were found in project files: "Would you like me to update the references from `.codex/skills/references/` to `_references/`?"
   - If AGENTS.md needs refresh: "Would you like to regenerate your AGENTS.md with the updated framework structure?"

5. **Summary**: Report the upgrade result and list any remaining manual steps.

---

## Mode 5: Create Workspace

Creates a project workspace from the foundational SEJA framework -- a standalone git repo containing framework files, project-specific references, and output artifacts. The codebase is accessed via `codex --add-dir` and stays completely clean (no framework files in it).

Triggered by `$quickstart --workspace` or selected from the mode menu.

If the argument includes `--workspace`, skip the menu and go directly to Mode 5.

### Steps

1. **Gather paths**: Ask the user for:
   - Framework source path (default: current directory if it has `.codex/`)
   - Workspace directory path (where to create the new workspace)
   - Target codebase path (the existing codebase to work alongside)

2. **Run the workspace creation script**: Execute `python .codex/skills/scripts/create_workspace.py --from <source> --workspace <workspace> --target <target>`. If the user wants a preview first, add `--dry-run`.

3. **Review the summary**: Present the script's output to the user. Highlight:
   - Workspace created at `<path>` (git repo initialized)
   - Output directory at `<workspace>/_output`
   - Conventions configured with absolute paths pointing to the codebase

4. **Offer to continue setup**: Ask the user:
   > "Would you like to run the project questionnaire to customize conventions and design references? This will tailor the framework to your specific project."
   - If yes: instruct the user to `cd` to the workspace and run `$quickstart .` to enter Mode 1 (interactive) or Mode 2 (from-spec)
   - If no: remind the user to edit `_references/project/conventions.md` manually and run `$quickstart .` in the workspace later

5. **Summary**: Report the workspace setup result and list next steps:
   - Start Codex from the workspace: `codex --add-dir <target>`
   - Run `$quickstart .` to complete project-specific setup
   - Use `$quickstart --upgrade` in the workspace when the framework evolves
