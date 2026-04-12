# TEMPLATE - PROJECT CONVENTIONS

> **How to use this template:** Copy this file to `project/conventions.md` and fill in the values for your project. This is the first file to customize — all other reference files and skills reference variables defined here.
>
> Centralized project-specific definitions. All skills and reference files reference variables from this file instead of hardcoding project-specific values. To adapt the skill system to a different project, edit only this file.

---

## Project Identity

| Variable | Value | Description |
|----------|-------|-------------|
| `PROJECT_NAME` | {{PROJECT_NAME}} | Project display name |
| `PROJECT_DESCRIPTION` | {{PROJECT_DESCRIPTION}} | One-line project description |
| `PROJECT_MODE` | {{PROJECT_MODE}} | Project mode: greenfield (new project) or brownfield (existing codebase) |

---

## Directory Structure

> **Absolute path support:** Variable values can be absolute paths (e.g., `D:/workspaces/my-project/_output`). Python's `Path` joining treats absolute paths as anchors, overriding relative-to-root resolution. This enables the workspace deployment pattern where output and source directories live outside the framework root.

| Variable | Value | Description |
|----------|-------|-------------|
| `SKILLS_DIR` | `.claude/skills` | Root directory for skill definitions |
| `AGENT_SPECS_DIR` | `project/agent` | Agent-facing structured specifications in YAML (in `_references/`) |
| `OUTPUT_DIR` | `_output` | Root directory for all generated artifacts |
| `PLANS_DIR` | `${OUTPUT_DIR}/plans` | Plan output folder |
| `SCRIPTS_DIR` | `${OUTPUT_DIR}/generated-scripts` | Script output folder |
| `ADVISORY_DIR` | `${OUTPUT_DIR}/advisory-logs` | Advisory log output folder |
| `PROPOSALS_DIR` | `${OUTPUT_DIR}/proposals` | Lightweight change proposals |
| `INVENTORIES_DIR` | `${OUTPUT_DIR}/inventories` | Inventory output folder |
| `USER_TESTS_DIR` | `${OUTPUT_DIR}/user-tests` | User test plan output folder |
| `EXPLAINED_BEHAVIORS_DIR` | `${OUTPUT_DIR}/explained-behaviors` | Behavior explanation output folder |
| `EXPLAINED_CODE_DIR` | `${OUTPUT_DIR}/explained-code` | Code explanation output folder |
| `EXPLAINED_DATA_MODEL_DIR` | `${OUTPUT_DIR}/explained-data-model` | Data model explanation output folder |
| `EXPLAINED_ARCHITECTURE_DIR` | `${OUTPUT_DIR}/explained-architecture` | Architecture explanation output folder |
| `BEHAVIOR_EVOLUTION_DIR` | `${OUTPUT_DIR}/behavior-evolution` | Behavior evolution explanation output folder |
| `REFLECTIONS_DIR` | `${OUTPUT_DIR}/reflections` | Reflection report output folder |
| `ONBOARDING_PLANS_DIR` | `${OUTPUT_DIR}/onboarding-plans` | Onboarding plan output folder |
| `COMMUNICATION_DIR` | `${OUTPUT_DIR}/communication` | Communication material output folder |
| `ROADMAP_DIR` | `${OUTPUT_DIR}/roadmaps` | Roadmap output folder |
| `QA_LOGS_DIR` | `${OUTPUT_DIR}/qa-logs` | QA session log output folder |
| `CHECK_LOGS_DIR` | `${OUTPUT_DIR}/check-logs` | Check/preflight/review output folder |
| `TMP_DIR` | `${OUTPUT_DIR}/tmp` | Temporary/helper scripts |
| `CODEBASE_DIR` | {{CODEBASE_DIR}} | Root directory of the project codebase (`.` for embedded, absolute path for workspace mode) |

---

## Key Files

| Variable | Value | Description | Maintained by |
|----------|-------|-------------|-------------- |
| `BRIEFS_FILE` | `${OUTPUT_DIR}/briefs.md` | Execution log of all skill invocations | Agent |
| `BRIEFS_INDEX_FILE` | `${OUTPUT_DIR}/briefs-index.md` | Lightweight briefs index (one-line summaries) | Agent |
| `ARTIFACT_INDEX_FILE` | `${OUTPUT_DIR}/INDEX.md` | Single global artifact index (no per-folder INDEX.md files) | Agent |
| `CONSTITUTION_FILE` | `project/constitution.md` | Project constitution -- immutable principles (in `_references/`) | Human |
| `AS_CODED` | `project/product-design-as-coded.md` | Unified implementation state: Conceptual Design, Metacommunication, Journey Maps (in `_references/`) | Agent |
| `CD_AS_IS_CHANGELOG` | `project/product-design-changelog.md` | As-built conceptual design changelog (in `_references/`) | Agent |
| `DESIGN_INTENT` | `project/product-design-as-intended.md` | Unified working intent (§0-§17) + ADR Decision log (## Decisions) + CHANGELOG (in `_references/`) | Human (markers) |
| `DESIGN_INTENT_TO_BE` | `project/product-design-as-intended.md` | Legacy alias for `DESIGN_INTENT` (workspace-mode backward compat; see plan-000268 Amendment A6) | Human (markers) |
| `UX_RESEARCH` | `project/ux-research-results.md` | UX research: personas, problem scenarios, journeys, processing status, CHANGELOG (in `_references/`) | Human (markers) |
| `STANDARDS` | `project/standards.md` | Unified engineering standards: Backend, Frontend, Testing, i18n (in `_references/`) | Human / Agent |
| `DESIGN_STANDARDS` | `project/design-standards.md` | Unified design standards: UX patterns and graphic/visual design (in `_references/`) | Human / Agent |
| `SESSION_NOTES_FILE` | `${TMP_DIR}/session-notes.md` | Session-scoped working memory for structured note-taking | Agent |
| `DECISION_DIGEST_FILE` | `${OUTPUT_DIR}/decision-digest.jsonl` | Machine-readable decision index (one JSON line per design decision) | Agent |

---

## To-Be / As-Is Registry

> Canonical list of all to-be / established / as-is file triples in this project.
> Read by `/design` (template generation), `/explain spec-drift` (drift checking),
> and post-skill (DONE marking proposals). Add a row when a new to-be/as-is pair
> is introduced. `established` and `as-is` are optional -- set to `-` if not applicable.
> The Section column identifies which portion of a file corresponds to each registry row when a file hosts multiple artifact types. Tools that scan for drift use the ID prefix (JM-TB-NNN for designed journeys, JM-E-NNN for discovered journeys) to discriminate artifact types within the same file.

| To-be file | Section | Established counterpart | Section | As-is counterpart |
| ---------- | ------- | ---------------------- | ------- | ----------------- |
| `${DESIGN_INTENT}` | §0-§17 design intent + Decisions + CHANGELOG | `-` | `-` | `${AS_CODED}` |
| `${DESIGN_INTENT}` | §15 designed journeys | `-` | `-` | `${AS_CODED} § Journey Maps` |
| `${UX_RESEARCH}` | all (personas, scenarios, journeys, CHANGELOG) | `-` | `-` | `-` |

---

## Review Configuration

| Variable | Value | Description |
|----------|-------|-------------|
| `MINIMUM_REVIEW_DEPTH` | `{{MINIMUM_REVIEW_DEPTH}}` | Minimum review depth floor. Valid values: `light`, `standard`, `deep`. The automatic complexity gate and per-call flags can only raise the depth above this floor, never lower it. Depth ordering: light < standard < deep. Default: `light`. |

---

## Periodic Triggers

> Configurable intervals for the `pending-check` pre-skill stage's lazy periodic-action creation. Read by `pending.py periodic-check` at skill invocation time. Empty or missing intervals disable the corresponding trigger.

| Trigger | Interval (days) | Action type | Description |
|---------|-----------------|-------------|-------------|
| Periodic curation | 30 | `periodic-curation` | Review `product-design-as-intended.md` for items ready to promote from `implemented` to `established` |
| Spec-drift check | 14 | `spec-drift-check` | Run `/explain spec-drift` to surface drift between design intent and as-coded state |

| Threshold | Value | Description |
|-----------|-------|-------------|
| Verify-as-coded file threshold | 5 | Minimum number of files changed by a plan before post-skill auto-creates a `verify-as-coded` pending action |
| Pending age escalation | 14 | Days before a pending action is flagged "overdue" in pre-skill notices |
| Pending auto-dismiss | 90 | Days after which unaddressed pending actions are auto-dismissed by `pending.py cleanup` |

---

## Source Directories

> Add one row per source directory in your project (e.g., backend, frontend, shared libraries, mobile).

| Variable | Value | Description |
|----------|-------|-------------|
| `BACKEND_DIR` | `{{BACKEND_DIR}}` | Backend source root |
| `FRONTEND_DIR` | `{{FRONTEND_DIR}}` | Frontend source root |
| `BACKEND_FRAMEWORK` | `{{BACKEND_FRAMEWORK}}` | Backend framework identifier (e.g., `flask`, `fastapi`, `django`, `express`, `none`) |
| `FRONTEND_FRAMEWORK` | `{{FRONTEND_FRAMEWORK}}` | Frontend framework identifier (e.g., `react`, `vue`, `angular`, `none`) |

---

## Stack Description

| Variable | Value | Description |
|----------|-------|-------------|
| `BACKEND_STACK` | {{BACKEND_STACK}} | Backend technology summary (e.g., "Flask + SQLAlchemy + PostgreSQL") |
| `FRONTEND_STACK` | {{FRONTEND_STACK}} | Frontend technology summary (e.g., "React + TypeScript + Vite") |
| `TESTING_STACK` | {{TESTING_STACK}} | Testing technology summary (e.g., "pytest + Vitest + Playwright") |
| `DEPLOYMENT_STACK` | {{DEPLOYMENT_STACK}} | Deployment technology summary (e.g., "Docker + Caddy") |

---

## Architecture Description

| Variable | Value | Description |
|----------|-------|-------------|
| `ARCHITECTURE_DESCRIPTION` | {{ARCHITECTURE_DESCRIPTION}} | High-level architecture description |
| `ARCHITECTURE_PATTERN` | {{ARCHITECTURE_PATTERN}} | Architecture pattern (e.g., "3-layer: API / Service / Model") |
| `BACKEND_ARCHITECTURE_SUMMARY` | {{BACKEND_ARCHITECTURE_SUMMARY}} | Backend architecture summary for CLAUDE.md |
| `FRONTEND_ARCHITECTURE_SUMMARY` | {{FRONTEND_ARCHITECTURE_SUMMARY}} | Frontend architecture summary for CLAUDE.md |
| `MODELS_DIR` | `${BACKEND_DIR}/app/models` | Database models directory |
| `CONVENTION_1` | {{CONVENTION_1}} | Key project convention #1 for CLAUDE.md |
| `CONVENTION_2` | {{CONVENTION_2}} | Key project convention #2 for CLAUDE.md |
| `CONVENTION_3` | {{CONVENTION_3}} | Key project convention #3 for CLAUDE.md |

---

## Backend Structure

| Variable | Value | Description |
|----------|-------|-------------|
| `BACKEND_APP_DIR` | `${BACKEND_DIR}/app` | Backend application root |
| `BACKEND_API_DIR` | `${BACKEND_APP_DIR}/api` | API blueprints/routes directory |
| `BACKEND_SCHEMAS_DIR` | `${BACKEND_APP_DIR}/schemas` | Marshmallow/validation schemas |
| `BACKEND_UTILS_DIR` | `${BACKEND_APP_DIR}/utils` | Backend utilities directory |
| `BACKEND_CONSTANTS_FILE` | `validation_constants.py` | Backend validation constants filename (resolved under BACKEND_UTILS_DIR) |
| `MIGRATIONS_DIR` | `${BACKEND_DIR}/migrations/versions` | Alembic migration files |
| `TRANSLATIONS_DIR` | `${BACKEND_DIR}/translations` | Flask-Babel translation catalogs |

---

## Frontend Structure

| Variable | Value | Description |
|----------|-------|-------------|
| `FRONTEND_SRC_DIR` | `${FRONTEND_DIR}/src` | Frontend source root |
| `FRONTEND_API_DIR` | `${FRONTEND_SRC_DIR}/api` | API client/type definitions |
| `FRONTEND_UTILS_DIR` | `${FRONTEND_SRC_DIR}/utils` | Frontend utilities directory |
| `FRONTEND_CONSTANTS_FILE` | `constants.ts` | Frontend validation constants filename (resolved under FRONTEND_UTILS_DIR) |
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

## Secret Scanning

| Variable | Value | Description |
|----------|-------|-------------|
| `SECRETS_EXTRA_SKIP_PATTERNS` | `{{SECRETS_EXTRA_SKIP_PATTERNS}}` | Additional filename substrings to skip during secret scanning (comma-separated) |
| `SECRETS_EXTRA_SKIP_DIRS` | `{{SECRETS_EXTRA_SKIP_DIRS}}` | Additional directory names to skip during secret scanning (comma-separated) |
| `SECRETS_EXTRA_SKIP_EXTENSIONS` | `{{SECRETS_EXTRA_SKIP_EXTENSIONS}}` | Additional file extensions to skip during secret scanning (comma-separated, with dots) |
| `SECRETS_EXTRA_FALSE_POSITIVES` | `{{SECRETS_EXTRA_FALSE_POSITIVES}}` | Additional false-positive regex patterns (comma-separated, case-insensitive) |
| `SECRETS_EXTRA_PATTERNS` | `{{SECRETS_EXTRA_PATTERNS}}` | Additional secret-detection regex patterns (comma-separated, case-insensitive, auto-named) |

---

## Build & Test Commands

| Variable | Value | Description |
|----------|-------|-------------|
| `ALL_TESTS_CMD` | {{ALL_TESTS_CMD}} | Command to run all tests |
| `BACKEND_TEST_CMD` | {{BACKEND_TEST_CMD}} | Command to run backend tests |
| `BACKEND_INTEGRATION_TEST_CMD` | {{BACKEND_INTEGRATION_TEST_CMD}} | Command to run backend integration tests |
| `BACKEND_TEST_FILE_CMD` | {{BACKEND_TEST_FILE_CMD}} | Command to run a single backend test file |
| `FRONTEND_TEST_CMD` | {{FRONTEND_TEST_CMD}} | Command to run frontend tests |
| `FRONTEND_TEST_FILE_CMD` | {{FRONTEND_TEST_FILE_CMD}} | Command to run a single frontend test file |
| `E2E_TEST_CMD` | {{E2E_TEST_CMD}} | Command to run E2E tests |
| `MIGRATION_CHAIN_SCRIPT` | {{MIGRATION_CHAIN_SCRIPT}} | Script to check migration chain integrity |

---

## Workspace Deployment

When using the foundational SEJA framework as a companion to an existing codebase, the recommended deployment pattern is:

- The **foundational SEJA framework** is available somewhere (as a cloned repo) -- it is the single source of truth for all skills, scripts, templates, and references
- The ***ProjectName* workspace** is a standalone git repo containing `.claude/`, `_references/`, and `_output/` -- created from the foundational framework via `/seed --workspace` or `create_workspace.py`
- The ***ProjectName* codebase** is accessed via `claude --add-dir <codebase-path>` -- no framework files are added to it
- `OUTPUT_DIR` points inside the workspace (version-controlled alongside framework config and design decisions)
- `BACKEND_DIR` and `FRONTEND_DIR` point at the codebase via absolute paths
- Setup: `python .claude/skills/scripts/create_workspace.py --from <foundational-framework> --workspace <path> --target <codebase>`
- Update: `python .claude/skills/scripts/upgrade_framework.py --from <foundational-framework> --target <workspace>`
