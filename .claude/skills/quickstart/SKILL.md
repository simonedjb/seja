---
name: quickstart
description: "Bootstrap a new project's .claude directory from templates."
argument-hint: <target-directory> [--generate-spec | --upgrade | --workspace]
metadata:
  last-updated: 2026-03-29 00:15:00
  version: 1.0.0
  category: utility
  context_budget: standard
  questionnaire_version: 1
---

## Quick Guide

**What it does**: Sets up a new project with the SEJA framework. Bootstrap mode creates the directory structure, configuration files, and project-specific references from templates.

**Example**:
> You: /quickstart .
> Agent: Walks you through a questionnaire about your project (tech stack, team structure, goals), then generates all the configuration and reference files you need.

**When to use**: You are starting a brand new project (bootstrap), upgrading an existing project's framework, or creating a workspace alongside an existing codebase.

# Quickstart

## Overview

This skill bootstraps a new project's `.claude/` directory using the template files from this project. It supports three modes: interactive questionnaire, pre-filled spec file, or generating a blank spec skeleton.

## Mode Selection

If no argument is provided, or if the argument is only a target directory, use the AskUserQuestion tool to ask which mode to use (if AskUserQuestion is not available, present as a numbered text list), with these options:
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

1. **Verify target directory**: Check that the target exists and is a git repository (or offer to `git init`). If a `.claude/` directory already exists, warn the user and ask whether to overwrite or merge.

2. **Create directory structure**: Create the following in the target directory:
   ```
   .agent-resources/
   .claude/
   .claude/skills/
   .claude/skills/scripts/
   .claude/rules/
   .claude/agents/
   ```

3. **Copy general (reusable) files** from this project's `.agent-resources/` to the target's `.agent-resources/`:
   - All `general-*.md` reference files (as-is, no modification needed)
   - All `template-*.md` reference files (these will be instantiated in step 6)
   - `template-settings.json` (to be customized in step 6)

4. **Copy skill definitions**: Copy all skill `SKILL.md` files to the target. These are project-independent and work with any project that follows the conventions.

5. **Run the questionnaire**: Read `template-questionnaire.md` and interactively walk the user through it:
   - Start with **Section 0 (Quick Start)** — 8 minimum questions for a skeleton
   - For each question, present the options with their pros/cons and a recommendation
   - Record all answers
   - After Section 0, ask if the user wants to continue with detailed sections (1-7) or use defaults

6. **Instantiate templates**: Using the questionnaire answers, create project-specific files in `.agent-resources/`:
   - Copy `template-conventions.md` to `project-conventions.md`, substituting answers
   - Copy `template-conceptual-design-as-is.md` to `project-conceptual-design-as-is.md`, filling in current-state conceptual design
   - Copy `template-conceptual-design-to-be.md` to `project-conceptual-design-to-be.md`, filling in target-state conceptual design
   - Copy `template-metacomm-as-is.md` to `project-metacomm-as-is.md`, filling in current-state metacommunication
   - Copy `template-metacomm-to-be.md` to `project-metacomm-to-be.md`, filling in target-state metacommunication
   - **Note**: For greenfield projects, populate as-is and to-be identically. For evolving products, populate to-be with the target state and as-is with the current implementation.
   - Copy `template-backend-standards.md` to `project-backend-standards.md`, selecting relevant sections
   - Copy `template-frontend-standards.md` to `project-frontend-standards.md`, selecting relevant sections
   - Copy `template-i18n-standards.md` to `project-i18n-standards.md`, if i18n is needed
   - Copy `template-security-checklists.md` to `project-security-checklists.md`
   - Copy `template-testing-standards.md` to `project-testing-standards.md`
   - Copy `template-ux-design-standards.md` to `project-ux-design-standards.md`, filling in UX design choices
   - Copy `template-graphic-ui-design-standards.md` to `project-graphic-ui-design-standards.md`, filling in visual/UI design choices
   - Customize `template-settings.json` to `.claude/settings.json` with actual paths

7. **Generate CLAUDE.md**: Create a `CLAUDE.md` in the codebase root with:
   - Project name, stack summary, build/run commands
   - Architecture overview
   - Key conventions
   - `@` references to the project-specific reference files

8. **Generate rules files**: Create `.claude/rules/` files appropriate for the chosen stack:
   - Backend rules (if backend exists)
   - Frontend rules (if frontend exists)
   - i18n rules (if i18n is configured)

9. **Copy agents**: Copy agent definitions, adjusting references to use the correct filenames.

10. **Generate smoke test infrastructure** (if backend framework is not "none"):
    1. `smoke_test_core.py` is already copied with the other scripts (step 3/4). No additional action needed — it is framework-agnostic.
    2. Generate `smoke_test_registry.json` from `template-smoke-test-registry.json`:
       - Set `framework` from `backend.framework` (lowercase: "flask", "django", "fastapi", "express")
       - Set `auth.method` from `backend.auth`
       - Set `test_config` based on framework: Flask→"unit_testing", Django→"test", FastAPI→"testing"
       - Set `auth.user_model_path` based on framework conventions (e.g., Flask+SQLAlchemy→"app.models.user.User", Django→"django.contrib.auth.models.User")
       - For each entity listed in the Domain section, generate a CRUD endpoint group with standard REST routes (`POST /api/<plural>`, `GET /api/<plural>`, `GET /api/<plural>/{id}`, `PUT /api/<plural>/{id}`, `DELETE /api/<plural>/{id}`)
       - Include auth setup endpoints (register, login, profile) and destructive auth endpoints (logout, password change) if auth is configured
       - Save to `<target>/.claude/skills/scripts/smoke_test_registry.json`
    3. Generate `smoke_test_api.py` — a thin runner (~80 lines) that imports `smoke_test_core`, loads the registry, and creates a framework-appropriate test client. The template is the same for all Flask projects; adapt the client factory for Django/FastAPI. Save to `<target>/.claude/skills/scripts/smoke_test_api.py`.
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

12b. **Secrets check**: Run `python .claude/skills/scripts/check_secrets.py <target>` to verify no `.env` files or files containing secrets are staged for commit. If the check flags any files, warn the user and list the flagged files. This is a safety net — step 12H already creates `.gitignore` entries, but this catches any files that slipped through.

13. **Summary**: Output a checklist of everything created, including both the `.claude/` framework files (steps 2–11) and any scaffolding tasks performed (step 12). List remaining manual steps only for tasks the user declined or that failed. Typical remaining manual steps:
    - Creating/configuring the database itself (e.g., `createdb <name>`)
    - Running initial migrations (if the migration tool was initialized but the DB does not exist yet)
    - Configuring external services (OAuth providers, email, etc.)
    - Replacing placeholder secrets in `.env` files

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

4. **Version check**: Compare the spec's `version` field against the current `questionnaire_version` (defined in this skill's frontmatter and in `template-questionnaire.md`). If there is a mismatch:
   - Consult the Version History table in `template-questionnaire.md` to identify new, changed, or removed fields between versions
   - Show the user what changed
   - Offer to migrate: apply defaults for new fields, warn about removed fields
   - If the user declines migration, proceed with best-effort parsing

5. **Validate all at once**: Produce a validation report listing:
   - **Provided fields** — with their values (confirmation)
   - **Missing required fields** — must be asked (see Field Classification below)
   - **Missing fields with defaults** — list the defaults that will be used
   - **Ambiguous or conflicting values** — e.g., chose Django ORM with Flask framework, or Prisma with Python backend
   - Present the full report to the user before asking any questions

6. **Targeted Q&A**: For each missing required field or conflict identified in step 5, ask the user. Group related questions when possible (e.g., ask about backend framework and ORM together). Present options with pros/cons from the questionnaire.

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

12. **Generate CLAUDE.md**: Same as Mode 1, step 7.

13. **Generate rules files**: Same as Mode 1, step 8.

14. **Copy agents**: Same as Mode 1, step 9.

15. **Generate initial briefs.md**: Same as Mode 1, step 11.

16. **Project scaffolding**: Same as Mode 1, step 12. Use the combined spec + Q&A answers to determine which tasks to offer.

16b. **Secrets check**: Same as Mode 1 step 12b.

17. **Preserve spec**: Copy the original spec file to `<target>/specs/quickstart-spec-YYYY-MM-DD HH.MM UTC.md` (creating `specs/` if it does not exist). If the spec was already in `specs/`, leave it in place (do not duplicate).

18. **Summary**: Same as Mode 1, step 13. Additionally, note the preserved spec file location.

---

## Mode 3: Generate Blank Spec

Creates a blank spec skeleton for the user to fill out offline.

### Steps

1. **Determine target directory**: Ask for the target directory if not provided as an argument.

2. **Create specs/ subfolder**: Create `<target>/specs/` if it does not exist.

3. **Generate the spec file**: Copy `template-quickstart-spec.md` (from this project's `.agent-resources/`) to `<target>/specs/quickstart-spec-YYYY-MM-DD HH.MM UTC.md`. Substitute the `{datetime}` placeholder in the header comment with the current UTC datetime.

4. **Output next steps**:
   > Spec file created at `<path>`.
   >
   > Fill in your choices — each field has inline comments explaining the options, pros/cons, and recommendations. Required fields are marked; everything else has sensible defaults.
   >
   > When ready, run `/quickstart <target-dir>` and select "From spec file".

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

### Optional (omit silently if not provided)

- `rich_text_editor`, `dark_mode`, `primary_color`, `secondary_color`
- `sans_font`, `serif_font`, `context_providers`, `initial_components`
- `secondary_locale`, `backend_default_locale`, `localized_emails`, `translatable_entities`
- `access_token_expiry`, `refresh_token_expiry`, `rate_limit`
- `file_uploads`, `import_export`, `integration_suite`, `e2e_base_url`
- Conceptual design details (free-form)
- Security validation constants (free-form)

---

## Versioning

- The current questionnaire version is declared in this skill's frontmatter (`questionnaire_version`) and in `template-questionnaire.md`.
- Spec files declare their version via the `version:` field on the first non-comment line.
- When versions differ, consult the Version History table in `template-questionnaire.md` to identify changes and offer migration.
- When adding new questions to the questionnaire:
  1. Increment `questionnaire_version` in both this skill's frontmatter and `template-questionnaire.md`
  2. Add the new fields to `template-quickstart-spec.md`
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

1. `.claude/skills/VERSION` — update the `version:` line
2. `.claude/CHANGELOG.md` — add a new version entry at the top with Added/Changed/Removed sections
3. `questionnaire_version` in `/quickstart` frontmatter and `template-questionnaire.md` — increment only if the questionnaire changed (new questions, removed questions, changed defaults)

### How to verify

Run `/check validate` after bumping to ensure all framework files are consistent.

---

## Mode 4: Upgrade

Upgrades an existing project's framework files to a newer version, preserving project-specific data.

Triggered by `/quickstart --upgrade` or selected from the mode menu.

If the argument includes `--upgrade`, skip the menu and go directly to Mode 4.

### Steps

1. **Locate source framework**: Look for the foundational SEJA framework in `seja-public/`. If not found, ask the user for the path to the source directory.

2. **Run the upgrade script**: Execute `python .claude/skills/scripts/upgrade_framework.py --from <source> --target <target>`. If the user wants a preview first, add `--dry-run`.

3. **Review the summary**: Present the script's output to the user. Highlight:
   - Version change (e.g., "1.0.0 → 2.0.0")
   - Whether old layout migration occurred
   - New convention variables available
   - Any manual steps needed (path reference updates, CLAUDE.md refresh)

4. **Offer follow-up actions**:
   - If new convention variables were found: "Would you like to add these variables to your `project-conventions.md`? I can walk you through the values."
   - If old path references were found in project files: "Would you like me to update the references from `.claude/skills/references/` to `.agent-resources/`?"
   - If CLAUDE.md needs refresh: "Would you like to regenerate your CLAUDE.md with the updated framework structure?"

5. **Summary**: Report the upgrade result and list any remaining manual steps.

---

## Mode 5: Create Workspace

Creates a project workspace from the foundational SEJA framework -- a standalone git repo containing framework files, project-specific references, and output artifacts. The codebase is accessed via `claude --add-dir` and stays completely clean (no framework files in it).

Triggered by `/quickstart --workspace` or selected from the mode menu.

If the argument includes `--workspace`, skip the menu and go directly to Mode 5.

### Steps

1. **Gather paths**: Ask the user for:
   - Framework source path (default: current directory if it has `.claude/`)
   - Workspace directory path (where to create the new workspace)
   - Target codebase path (the existing codebase to work alongside)

2. **Run the workspace creation script**: Execute `python .claude/skills/scripts/create_workspace.py --from <source> --workspace <workspace> --target <target>`. If the user wants a preview first, add `--dry-run`.

3. **Review the summary**: Present the script's output to the user. Highlight:
   - Workspace created at `<path>` (git repo initialized)
   - Output directory at `<workspace>/_output`
   - Conventions configured with absolute paths pointing to the codebase

4. **Offer to continue setup**: Ask the user:
   > "Would you like to run the project questionnaire to customize conventions and design references? This will tailor the framework to your specific project."
   - If yes: instruct the user to `cd` to the workspace and run `/quickstart .` to enter Mode 1 (interactive) or Mode 2 (from-spec)
   - If no: remind the user to edit `.agent-resources/project-conventions.md` manually and run `/quickstart .` in the workspace later

5. **Summary**: Report the workspace setup result and list next steps:
   - Start Claude Code from the workspace: `claude --add-dir <target>`
   - Run `/quickstart .` to complete project-specific setup
   - Use `/quickstart --upgrade` in the workspace when the framework evolves
