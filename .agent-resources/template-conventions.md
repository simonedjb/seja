# TEMPLATE - PROJECT CONVENTIONS

> **How to use this template:** Copy this file to `project-conventions.md` and fill in the values for your project. This is the first file to customize — all other reference files and skills reference variables defined here.
>
> Centralized project-specific definitions. All skills and reference files reference variables from this file instead of hardcoding project-specific values. To adapt the skill system to a different project, edit only this file.

---

## Project Identity

| Variable | Value | Description |
|----------|-------|-------------|
| `PROJECT_NAME` | {{PROJECT_NAME}} | Project display name |

---

## Directory Structure

> **Absolute path support:** Variable values can be absolute paths (e.g., `D:/workspaces/my-project/_output`). Python's `Path` joining treats absolute paths as anchors, overriding relative-to-root resolution. This enables the workspace deployment pattern where output and source directories live outside the framework root.

| Variable | Value | Description |
|----------|-------|-------------|
| `SKILLS_DIR` | `.claude/skills` | Root directory for skill definitions |
| `OUTPUT_DIR` | `_output` | Root directory for all generated artifacts |
| `PLANS_DIR` | `${OUTPUT_DIR}/plans` | Plan output folder |
| `SCRIPTS_DIR` | `${OUTPUT_DIR}/generated-scripts` | Script output folder |
| `ADVISORY_DIR` | `${OUTPUT_DIR}/advisory-logs` | Advisory log output folder |
| `INVENTORIES_DIR` | `${OUTPUT_DIR}/inventories` | Inventory output folder |
| `USER_TESTS_DIR` | `${OUTPUT_DIR}/user-tests` | User test plan output folder |
| `EXPLAINED_BEHAVIORS_DIR` | `${OUTPUT_DIR}/explained-behaviors` | Behavior explanation output folder |
| `EXPLAINED_CODE_DIR` | `${OUTPUT_DIR}/explained-code` | Code explanation output folder |
| `EXPLAINED_DATA_MODEL_DIR` | `${OUTPUT_DIR}/explained-data-model` | Data model explanation output folder |
| `EXPLAINED_ARCHITECTURE_DIR` | `${OUTPUT_DIR}/explained-architecture` | Architecture explanation output folder |
| `BEHAVIOR_EVOLUTION_DIR` | `${OUTPUT_DIR}/behavior-evolution` | Behavior evolution explanation output folder |
| `ONBOARDING_PLANS_DIR` | `${OUTPUT_DIR}/onboarding-plans` | Onboarding plan output folder |
| `COMMUNICATION_DIR` | `${OUTPUT_DIR}/communication` | Communication material output folder |
| `ROADMAP_DIR` | `${OUTPUT_DIR}/roadmaps` | Roadmap output folder |
| `QA_LOGS_DIR` | `${OUTPUT_DIR}/qa-logs` | QA session log output folder |
| `CHECK_LOGS_DIR` | `${OUTPUT_DIR}/check-logs` | Check/preflight/review output folder |
| `TMP_DIR` | `${OUTPUT_DIR}/tmp` | Temporary/helper scripts |

---

## Key Files

| Variable | Value | Description |
|----------|-------|-------------|
| `BRIEFS_FILE` | `${OUTPUT_DIR}/briefs.md` | Execution log of all skill invocations |
| `BRIEFS_INDEX_FILE` | `${OUTPUT_DIR}/briefs-index.md` | Lightweight briefs index (one-line summaries) |
| `ARTIFACT_INDEX_FILE` | `${OUTPUT_DIR}/INDEX.md` | Single global artifact index (no per-folder INDEX.md files) |
| `TESTS_TRACKER_FILE` | `${OUTPUT_DIR}/update-tests-tracker.md` | Test execution tracker for update-tests skill |
| `CONCEPTUAL_DESIGN_AS_IS` | `project-conceptual-design-as-is.md` | As-built conceptual design (in `.agent-resources/`) |
| `CONCEPTUAL_DESIGN_TO_BE` | `project-conceptual-design-to-be.md` | Target conceptual design (in `.agent-resources/`) |
| `METACOMM_AS_IS` | `project-metacomm-as-is.md` | As-built metacommunication record (in `.agent-resources/`) |
| `METACOMM_TO_BE` | `project-metacomm-to-be.md` | Target metacommunication record (in `.agent-resources/`) |
| `UX_DESIGN_STANDARDS` | `project-ux-design-standards.md` | UX design standards (in `.agent-resources/`) |
| `GRAPHIC_UI_DESIGN_STANDARDS` | `project-graphic-ui-design-standards.md` | Graphic/UI design standards (in `.agent-resources/`) |

---

## Source Directories

> Add one row per source directory in your project (e.g., backend, frontend, shared libraries, mobile).

| Variable | Value | Description |
|----------|-------|-------------|
| `BACKEND_DIR` | `{{BACKEND_DIR}}` | Backend source root |
| `FRONTEND_DIR` | `{{FRONTEND_DIR}}` | Frontend source root |

---

## Backend Structure

| Variable | Value | Description |
|----------|-------|-------------|
| `BACKEND_APP_DIR` | `${BACKEND_DIR}/app` | Backend application root |
| `BACKEND_API_DIR` | `${BACKEND_APP_DIR}/api` | API blueprints/routes directory |
| `BACKEND_SCHEMAS_DIR` | `${BACKEND_APP_DIR}/schemas` | Marshmallow/validation schemas |
| `MIGRATIONS_DIR` | `${BACKEND_DIR}/migrations/versions` | Alembic migration files |
| `TRANSLATIONS_DIR` | `${BACKEND_DIR}/translations` | Flask-Babel translation catalogs |

---

## Frontend Structure

| Variable | Value | Description |
|----------|-------|-------------|
| `FRONTEND_SRC_DIR` | `${FRONTEND_DIR}/src` | Frontend source root |
| `FRONTEND_API_DIR` | `${FRONTEND_SRC_DIR}/api` | API client/type definitions |
| `FRONTEND_I18N_DIR` | `${FRONTEND_SRC_DIR}/i18n/locales` | i18n locale JSON files |

---

## i18n Configuration

| Variable                 | Value                       | Description                                                          |
|--------------------------|-----------------------------| ---------------------------------------------------------------------|
| `I18N_FRONTEND_FILES`    | `{{I18N_FRONTEND_FILES}}`   | Comma-separated frontend locale filenames (e.g., `en-US.json,pt-BR.json`)  |
| `I18N_BACKEND_CATALOGS`  | `{{I18N_BACKEND_CATALOGS}}` | Comma-separated backend catalog names (e.g., `en_US,pt_BR`)          |

---

## Test Configuration

| Variable | Value | Description |
|----------|-------|-------------|
| `BACKEND_SUBPACKAGES` | `{{BACKEND_SUBPACKAGES}}` | Comma-separated backend subpackage names for coverage grouping |
| `FRONTEND_SUBPACKAGES` | `{{FRONTEND_SUBPACKAGES}}` | Comma-separated frontend subpackage names for coverage grouping |
| `FRONTEND_ENTRY_POINTS` | `{{FRONTEND_ENTRY_POINTS}}` | Comma-separated entry point filenames to exclude from unused-file checks |

---

## Workspace Deployment

When using the foundational SEJA framework as a companion to an existing codebase, the recommended deployment pattern is:

- The **foundational SEJA framework** is available somewhere (as a cloned repo or quickstart kit) -- it is the single source of truth for all skills, scripts, templates, and references
- The ***ProjectName* workspace** is a standalone git repo containing `.claude/`, `.agent-resources/`, and `_output/` -- created from the foundational framework via `/quickstart --workspace` or `create_workspace.py`
- The ***ProjectName* codebase** is accessed via `claude --add-dir <codebase-path>` -- no framework files are added to it
- `OUTPUT_DIR` points inside the workspace (version-controlled alongside framework config and design decisions)
- `BACKEND_DIR` and `FRONTEND_DIR` point at the codebase via absolute paths
- Setup: `python .claude/skills/scripts/create_workspace.py --from <foundational-framework> --workspace <path> --target <codebase>`
- Update: `python .claude/skills/scripts/upgrade_framework.py --from <foundational-framework> --target <workspace>`
