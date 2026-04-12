---
name: design
description: "Define or update project design — stack, conventions, domain model, conceptual design, and standards. Use when user mentions 'design', 'design project', 'configure project', 'update design', or 'project setup'."
argument-hint: "[--generate-spec] [--add-docs] [spec-file-path]"
compatibility: "Designed for Claude Code with SEJA framework"
metadata:
  last-updated: 2026-03-31 16:30 UTC
  version: 1.0.0
  category: planning
  context_budget: standard
  questionnaire_version: 6
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

> **`/design`** defines WHAT to build and WHY. **`/plan`** defines HOW to build it and WHY those tasks are the way they are. Design produces project definitions (`_references/project/`); plans consume them to produce actionable implementation steps.

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
   - If Section metacomm-message (0.1) has been answered, parse it before proceeding: extract project name hint, description, target user type, and primary use case. When the agent reaches questions basic-definitions 1.1, 1.2, and conceptual-design 2.1, 2.10, present the extracted value as: "From your metacomm message, I suggest: [extracted value]. Accept or override?"
   - Start with **Section metacomm-message (0)** (optional but recommended) and **Section basic-definitions (1)** -- 10 minimum questions for a working skeleton
   - For each question, present the options with their pros/cons and a recommendation
   - Record all answers
   - After Section basic-definitions, ask if the user wants to continue with the remaining sections or use defaults

3. **Interruptibility**: At any point, if the user wants to stop:
   - Save all answers collected so far to `specs/design-in-progress.md`
   - Print: "Progress saved. Run `/design` again to resume."

4. **Skip to defaults**: At any point, the user can say "use defaults for everything else":
   - Fill remaining fields from the defaults table (see Field Classification)
   - **Brownfield note**: For brownfield projects, "use defaults" means: use **detected values** (from step 5b) for stack-related fields and **template defaults** (from the Field Classification table) for design-related fields
   - Proceed to template instantiation

5. **Mandatory conceptual design**: Section conceptual-design core questions are **required** for all projects. The agent must not allow the user to skip these by accepting defaults. At minimum, the user must provide:
   - Entity hierarchy (conceptual-design 2.3) — what the system manages
   - Permission levels (conceptual-design 2.6) — who can do what
   - Greenfield/evolving status (conceptual-design 2.9) — determines as-is/to-be population
   The metacommunication message is handled separately in the Final Step (see `template/questionnaire.md`). If Section metacomm-message (0.1) was answered, the Final Step uses it as the default. The verbatim rule applies to the final confirmed answer.

   For **brownfield** projects, additionally require:
   - Existing tech stack (conceptual-design 2.12)
   - Migration constraints (conceptual-design 2.13)

5b. **Brownfield Codebase Scan** (only when question 1.3 or 2.9 confirms brownfield/evolving):

    Before proceeding with remaining questions, scan the codebase to auto-detect stack and structure:

    1. **Detect stack from dependency files**: Read whichever of these exist in `${CODEBASE_DIR}`: `package.json`, `requirements.txt`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, `pom.xml`, `build.gradle`. Map detected dependencies to `conventions.md` variables:
       - `BACKEND_FRAMEWORK`: from main framework dependency (`flask`, `fastapi`, `django`, `express`, `nestjs`, `spring-boot`, `rails`, `actix-web`, `gin`, etc.)
       - `FRONTEND_FRAMEWORK`: from main UI dependency (`react`, `vue`, `angular`, `svelte`, `next`, `nuxt`, etc.)
       - Secondary dependencies: `ORM` (e.g., `sqlalchemy`, `prisma`, `django-orm`, `typeorm`), `VALIDATION` (e.g., `marshmallow`, `pydantic`, `zod`), `AUTH` (e.g., `flask-jwt-extended`, `passport`, `django-allauth`), `CSS` (e.g., `tailwindcss`, `bootstrap`, `styled-components`), `BUILD_TOOL` (e.g., `vite`, `webpack`, `esbuild`), `STATE` (e.g., `redux`, `zustand`, `pinia`), `DATA_FETCHING` (e.g., `tanstack-query`, `swr`, `apollo`), `HTTP_CLIENT` (e.g., `axios`, `ky`), `ROUTER` (e.g., `react-router`, `vue-router`), `BACKEND_TEST` (e.g., `pytest`, `jest`, `mocha`), `FRONTEND_TEST` (e.g., `vitest`, `jest`, `testing-library`)
       - `DATABASE`: infer from ORM config files, `docker-compose.yml` service definitions, `.env` patterns (e.g., `DATABASE_URL`), or migration directory structure (e.g., `alembic/`, `prisma/migrations/`, `django migrations`)

    2. **Detect directory structure**: Scan for `BACKEND_DIR` and `FRONTEND_DIR` by looking for common framework entry points (`app.py`, `manage.py`, `main.py`, `server.ts`, `index.ts`, `App.tsx`, `package.json` in subdirectories). Also detect:
       - `MIGRATIONS_DIR`: from ORM conventions (e.g., `alembic/versions/`, `prisma/migrations/`, `<app>/migrations/`)
       - `MODELS_DIR`: from ORM conventions (e.g., `models/`, `app/models/`, `src/entities/`)

    3. **Present detected values**: Display a summary table of all detected values:
       ```
       | Variable             | Detected Value     | Source                        |
       |----------------------|--------------------|-------------------------------|
       | BACKEND_FRAMEWORK    | flask              | requirements.txt              |
       | FRONTEND_FRAMEWORK   | react              | package.json                  |
       | DATABASE             | PostgreSQL         | docker-compose.yml            |
       | ...                  | ...                | ...                           |
       ```
       Then ask: "I detected the following from your codebase. Accept, override, or correct each value:"

    4. **Pre-fill questionnaire**: Use confirmed detected values as pre-filled defaults for the following questions, converting them from open-ended questions to confirmation prompts:
       - Question 1.4 (Backend framework) — from `BACKEND_FRAMEWORK`
       - Question 1.5 (Frontend framework) — from `FRONTEND_FRAMEWORK`
       - Question 1.6 (Database) — from `DATABASE`
       - Question 1.9 (Testing tools) — from `BACKEND_TEST`, `FRONTEND_TEST`
       - Question 2.12 (Existing tech stack) — from full detected stack summary

    5. **Fallback**: If no dependency files are found, or if detection is ambiguous for a specific field, fall back to standard manual entry for that field. Do not guess — only pre-fill values with high confidence.

5c. **As-Is Pre-population** (brownfield only — runs after 5b when `MODELS_DIR` or schema files were detected):

    Using the codebase scan results from step 5b, extract domain knowledge to pre-populate the `## Conceptual Design` section of `product-design-as-coded.md` instead of copying the empty template.

    1. **Entity extraction**: Scan model/schema files detected in step 5b. The scan location depends on the detected ORM/framework:
       - **SQLAlchemy**: `${MODELS_DIR}` or `models/*.py` — look for classes inheriting `db.Model` or `Base`
       - **Django**: `*/models.py` — look for classes inheriting `models.Model`
       - **Prisma**: `prisma/schema.prisma` — parse `model` blocks
       - **TypeORM**: `entities/` or `src/entities/` — look for `@Entity()` decorated classes
       - **Sequelize**: `models/` — look for `sequelize.define()` or `Model.init()`
       - **ActiveRecord**: `app/models/` — look for classes inheriting `ApplicationRecord`

       For each detected model/table, extract:
       - **Entity name** and its mapped table name (if explicit)
       - **Field names and types** (string, integer, boolean, text, datetime, etc.)
       - **Relationships**: foreign keys (`ForeignKey`, `belongs_to`, `@ManyToOne`), many-to-many (`ManyToManyField`, `@ManyToMany`, HABTM), one-to-many (`has_many`, `@OneToMany`)
       - **Visibility/access rules**: if detectable from model metadata (e.g., `visibility` fields, `is_public` booleans, scoped queries, default manager filters)
       - **Soft delete indicators**: `deleted_at`, `is_deleted`, `paranoid: true`, `acts_as_paranoid`

       Build an entity hierarchy tree for the `### 2. Entity Hierarchy` H3 subsection under `## Conceptual Design` of `product-design-as-coded.md`. Infer parent-child relationships from foreign keys — entities with FKs pointing to another entity are children of that entity in the tree. Root entities are those with no inbound ownership FKs.

    2. **Permission extraction**: Scan route/controller files for permission decorators and middleware:
       - **Python/Flask**: `@login_required`, `@roles_required`, `@jwt_required`, `@permission_required`
       - **Python/Django**: `@login_required`, `@permission_required`, `@user_passes_test`, `permission_classes`
       - **Python/FastAPI**: `Depends()` with auth functions, `Security()` scopes
       - **Node.js/Express**: middleware like `isAuthenticated`, `authorize()`, `requireRole()`
       - **Rails**: `before_action :authenticate_user!`, `authorize`, Pundit policies, CanCanCan abilities

       From the detected decorators, build a permission summary for **Section 4** (Permission Model):
       - Map distinct roles to the System-Level Roles table
       - Map resource-scoped guards to the Resource-Level Access table

    3. **Validation extraction**: Scan validation schema files for field constraints:
       - **Marshmallow**: `Schema` subclasses with `fields.String(validate=Length(...))`, `Required`, etc.
       - **Pydantic**: `BaseModel` subclasses with `Field(min_length=..., max_length=...)`, `constr()`, `conint()`
       - **Zod**: `z.string().min().max()`, `z.number().int().positive()`, etc.
       - **Django Forms/Serializers**: `max_length`, `min_length`, `validators=[...]`
       - **Joi**: `Joi.string().min().max()`, `Joi.number().integer()`

       Map extracted constraints to **Section 10** (Validation Constants) with:
       - Field name, min/max values, and the source file where detected

    4. **Present extracted as-is model**: Before writing anything, display the extracted model to the designer in a structured summary:

       ```
       ## Extracted As-Is Model

       ### Entities (Section 2)
       <entity tree and per-entity details>

       ### Permissions (Section 4)
       <roles table and resource access table>

       ### Validation Constants (Section 10)
       <constraints table>

       ### Sections with no data detected
       Sections 1, 3, 5, 6, 7, 8, 9 — will retain template placeholder text.
       ```

       Ask: "This is what I extracted from your codebase. Confirm, edit, or add details before I save it to `product-design-as-coded.md § Conceptual Design`."

    5. **Populate**: After designer confirmation, write the `## Conceptual Design` H2 section of `project/product-design-as-coded.md` with:
       - Confirmed extracted content populating the `### 2. Entity Hierarchy`, `### 4. Permission Model`, and `### 10. Validation Constants (Domain)` H3 subsections (or whichever sections had data)
       - All other H3 subsections retain the original template placeholder text from `template/product-design-as-coded.md`
       - The `maintained-by: Agent (post-skill)` comment header is preserved
       - The `## Metacommunication` and `## Journey Maps` H2 sections remain as template placeholders (post-skill populates them on first plan execution)

5d. **Brownfield Questionnaire Flow** (only when question 1.3 or 2.9 confirms brownfield/evolving):

    After question 1.3 confirms brownfield mode, the questionnaire diverges from the standard flow into three phases:

    **Phase 1 — Automated scan**: Execute the Brownfield Codebase Scan (step 5b) and As-Is Pre-population (step 5c). Present detected values to the user in the summary table before proceeding.

    **Phase 2 — Confirm detected values**: The following questions become confirmation prompts pre-filled with detected values instead of open-ended questions. For each, present the detected value and its source, and let the user confirm or override:
    - Question 1.4 (Backend framework) — from `BACKEND_FRAMEWORK`
    - Question 1.5 (Frontend framework) — from `FRONTEND_FRAMEWORK`
    - Question 1.6 (Database) — from `DATABASE`
    - Question 1.9 (Testing tools) — from `BACKEND_TEST`, `FRONTEND_TEST`
    - Question 2.12 (Existing tech stack) — from full detected stack summary

    Prompt format: "I detected **[value]** as your [field] [from source]. Correct? (yes / override: ___)"

    If a value was not detected for a given field, fall back to standard manual entry for that question.

    **Phase 3 — Intent-only questions**: Continue with questions that cannot be inferred from the codebase. These require human input regardless of detection:
    - Metacommunication (0.1)
    - Design philosophy (2.2)
    - Entity hierarchy refinement (2.3) — present as: "I detected these entities: [list]. Do you want to refine the hierarchy?"
    - Permission refinement (2.6)
    - Migration constraints (2.13)
    - Pain points (2.15)
    - Design system (2.16)
    - All UX/graphic design sections (3.x, 4.x)

5e. **Validation Cross-check** (brownfield only — runs after 5d, before template instantiation):

    Compare final questionnaire answers against detected values from step 5b. The critical distinction:
    - `conventions.md` variables reflect the **current state** (detected values), because plans execute against the code as it exists today
    - `product-design-as-intended.md` captures the **target state** (questionnaire answers), because it describes where the project is headed
    - `product-design-as-coded.md § Conceptual Design` already reflects the current state (populated by step 5c)

    **Discrepancy detection**: For each field where both a detected value and a questionnaire answer exist, compare them. If they differ, prompt:

    > "You specified **[answer]** but I detected **[detected]** in your codebase. Which is correct — the current state (**[detected]**) for conventions.md, or the target state (**[answer]**) for product-design-as-intended.md? Or are they the same?"

    Fields to cross-check (matching 5b detection targets): `BACKEND_FRAMEWORK`, `FRONTEND_FRAMEWORK`, `DATABASE`, `BACKEND_DIR`, `FRONTEND_DIR`, `MODELS_DIR`, `MIGRATIONS_DIR`, and any other conventions.md variables that were both detected and answered.

    **Dual population** — when current and target states differ (e.g., migrating from Flask to FastAPI):
    - `conventions.md`: set the variable to the **current-state** value (e.g., `BACKEND_FRAMEWORK` = `flask`) so plans and scripts work with existing code
    - `product-design-as-intended.md` Section 0 "Planned Changes": document the migration intent (e.g., "Migrate backend framework from Flask to FastAPI")
    - `product-design-as-coded.md § Conceptual Design`: already reflects the current state from step 5c — no additional action needed

    **No-discrepancy fast path**: If all questionnaire answers match their detected values, skip the cross-check silently and proceed directly to template instantiation.

6. **Codebase scaffolding question**: After stack decisions are made, ask:
   > "Should I create the initial project structure (directories, config files, entry points) for your chosen stack?"
   - If yes, run the project scaffolding tasks (see Project Scaffolding section)
   - If no, skip

7. **Instantiate templates**: Using the questionnaire answers, create project-specific files in `_references/`:
   - Copy `template/conventions.md` to `project/conventions.md`, substituting answers
   - When substituting answers into `project/conventions.md`, set `PROJECT_MODE` from question 2.9 (greenfield -> `greenfield`, evolving -> `brownfield`). Set `CODEBASE_DIR` to `.` for embedded mode (default) or to the absolute codebase path if the project was seeded with workspace separation (detectable from the directory structure -- if `_references/` is not in the codebase root, the codebase is external).
   - Copy `template/constitution.md` to `project/constitution.md` (Required -- always generated for new projects. Content may be customized but file cannot be skipped.)
   - Copy `template/product-design-as-intended.md` to `project/product-design-as-intended.md`. The file is classified `Human (markers)` -- prose (working intent, entity hierarchies, metacomm intentions, §15 Designed User Journeys) remains human-authored, but agents may write `STATUS` markers on to-be items and Decision entries (`### D-NNN:`) via `apply_marker.py` after AskUserQuestion confirmation. The file includes a `## Decisions` section (ADR shape) and a `## CHANGELOG` section. Apply the **I/you phrasing rule** for Part II metacommunication sections.
   - **For evolving (brownfield) projects only**: copy `template/product-design-as-coded.md` to `project/product-design-as-coded.md` (the unified implementation-state file, SEJA 2.8.4; replaces the former three separate as-is files). If step 5c produced pre-populated content for the `## Conceptual Design` section, use that instead of copying the empty section. Also copy `template/product-design-changelog.md` to `project/product-design-changelog.md` (this file is kept separate from `product-design-as-coded.md`; Phase 3 F from advisory-000264 will conditionally embed it in a future release after this plan operates without incidents for one release cycle).
   - **For greenfield projects**: do **not** instantiate `product-design-as-coded.md` (post-skill will create it on first plan execution)
   - Copy `template/standards.md` to `project/standards.md` (unified engineering standards: Backend, Frontend, Testing, i18n sections)
   - Copy `template/design-standards.md` to `project/design-standards.md` (unified design standards: UX patterns, Graphic/visual design sections)
   - Copy `template/security-checklists.md` to `project/security-checklists.md`
   - Copy `template/ux-research-results.md` to `project/ux-research-results.md`, pre-populating persona and user community entries from section conceptual-design (2.10) answers if provided. The file is classified `Human (markers)` -- prose remains human-authored, but agents may write `INCORPORATED` markers and CHANGELOG appends via `apply_marker.py` after AskUserQuestion confirmation.
   > **Registry note:** For each to-be/as-is triple in the To-Be / As-Is Registry (see conventions.md), ensure the to-be and established templates are copied during project setup. As new pairs are added to the registry in future framework versions, add their template copies here.
   - Copy agent YAML templates (`template/agent/constraints.yaml`, `entities.yaml`, `permissions.yaml`, `spec-checks.yaml`) to `project/agent/`
   - Based on Section docs-templates (5) answers: copy selected `template/docs/*.md` files to `project/docs/` in `_references/`. If the user chose "defaults", copy only the 3 recommended templates (readme.md, contextual-help.md, adr.md). If "skip", copy none.
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

11. **Verification pass** (always runs after template instantiation):

    > Status message to display: "Verifying design output..."

    1. Read the original spec input (questionnaire answers) and the 3 critical generated files:
       - `project/product-design-as-intended.md` (Part II — sections 11-15)
       - `project/constitution.md`
       - `project/security-checklists.md`

    2. For each file, evaluate semantic fidelity:
       - **design-intent Part II**: Compare the designer's metacommunication message (from questionnaire section 0.1 or Final Step) against the generated §11 Global Vision. Verify EMT guiding questions (§12) are populated from the spec answers, not left as template placeholders. Check per-feature intentions (§14) include all features mentioned in the spec.
       - **constitution**: Verify all immutable principles from the spec are present and not contradicted.
       - **security-checklists**: Verify all security constraints from the spec (validation constants, auth requirements) are present.

    3. If gaps are found:
       - Fix the gap by updating the generated file with the missing or corrected content
       - Log what was fixed: "Verification: added missing [field] to [file]"
       - Re-run the evaluation once more (bounded to 1 retry)
       - If gaps persist after retry, log a warning: "Verification: [N] semantic gaps remain in [file] after 1 retry. Please review manually."

    4. Output: "Design output verified. [N] files checked, [M] gaps found and fixed."

    5. **Requirement ID assignment**: For each enumerable requirement in the generated `project/product-design-as-intended.md`, assign a sequential REQ ID using HTML comment markers. Use the naming convention `<!-- REQ-TYPE-NNN -->` where TYPE is derived from the section (ENT for section 2, PERM for section 4, VAL for section 10, UX for section 8, MC for section 14, JM for section 15, I18N for section 7, DELTA for sections 16-17) and NNN is a zero-padded 3-digit counter per type, starting at 001. Place each marker on the line immediately before the heading, table row, or bullet that defines the requirement. This enables downstream traceability via `check_plan_coverage.py`.

12. **Secrets check**: Run `python .claude/skills/scripts/check_secrets.py` to verify no secrets are staged.

13. **Clean up**: Remove `specs/design-in-progress.md` if it exists.

14. **Summary**: Output a checklist of everything created and any manual steps needed.

15. **Review & next steps**: Present the generated project specification files and offer review:

    | File | Controls |
    |------|----------|
    | `project/conventions.md` | Directory paths, variable definitions |
    | `project/constitution.md` | Immutable principles, security invariants |
    | `project/product-design-as-intended.md` | Unified working intent (§1-§17), Decision log (## Decisions, ADR shape), and CHANGELOG. Human (markers) classification. |
    | `project/ux-research-results.md` | UX research: personas, problem scenarios, cross-reference map, processing status, discovered user journeys (JM-E-NNN), and CHANGELOG. Human (markers) classification. |
    | `project/standards.md` | Unified engineering standards: Backend, Frontend, Testing, i18n sections |
    | `project/design-standards.md` | Unified design standards: UX patterns, Graphic / visual design sections |
    | `project/security-checklists.md` | Security checklists, validation constants |
    | `project/docs/*.md` | Documentation structure templates |

    **Questionnaire-to-output mapping** (include in summary so the designer knows which answers produced which files):

    | Questionnaire Section | Generated File |
    |---|---|
    | conceptual-design 2.3 Entity hierarchy, 2.6 Permissions | `project/product-design-as-intended.md` |
    | conceptual-design 2.1, 2.10 (product description, user community) | `project/ux-research-results.md` |
    | Final Step metacomm (or metacomm-message 0.1) | `project/product-design-as-intended.md §15` (journey intent seeded in product-design-as-intended.md) |
    | Stack choices (T2) | `project/conventions.md` |
    | Immutable principles (T2) | `project/constitution.md` |
    | Backend patterns (T3) | `project/standards.md § Backend` |
    | Frontend patterns (T3) | `project/standards.md § Frontend` |
    | UX patterns (T1) | `project/design-standards.md § UX patterns` |
    | Visual design (T1) | `project/design-standards.md § Graphic / visual design` |
    | Testing conventions (T3) | `project/standards.md § Testing` |
    | i18n conventions (T3) | `project/standards.md § i18n` |
    | Security constraints (T3) | `project/security-checklists.md` |

    Then offer: 1) Review specs now, 2) Generate roadmap (`/plan --roadmap`), 3) Done for now.

### Mode 2: From Spec File

1. **Locate spec file**: Use the provided path, or look in `specs/`.

2. **Read and parse the spec file**: Same parsing rules as the questionnaire Mode 2.

3. **Version check**: Compare against `questionnaire_version`.

4. **Validate all at once**: Report provided, missing required, missing with defaults, and ambiguous fields.

5. **Targeted Q&A**: Ask for missing required fields. Enforce **mandatory conceptual design** fields.

6. **Offer detailed sections**: Present Sections conceptual-design through security-checklists (2-11) as a numbered multi-select list.

7. **Instantiate templates**: Same as Mode 1, step 7.

8. **Generate CLAUDE.md, rules, smoke tests**: Same as Mode 1, steps 8-10.

9. **Verification pass**: Same as Mode 1, step 11.

10. **Secrets check**: Same as Mode 1, step 12.

11. **Preserve spec**: Copy to `specs/project-spec-YYYY-MM-DD HH.MM UTC.md`.

12. **Summary + Review**: Same as Mode 1, steps 14-15.

### Mode 3: Add Documentation Templates

Triggered when `--add-docs` is passed.

1. **Verify project exists**: Check that `project/conventions.md` exists in `_references/`. If not, abort: "No project design found. Run `/design` first."

2. **Check existing docs**: Check if `project/docs/` already exists in `_references/`. If it does, list the templates already instantiated and ask: "Some documentation templates are already set up. Add more, or replace all?"

3. **Present template checklist**: Read all `template/docs/*.md` files. For each, extract the `recommended` and `depends_on` fields from the YAML frontmatter. Present the list to the user:
   - Mark recommended templates with "(Recommended)"
   - For templates with `depends_on` that matches the project's app type (from `project/design-standards.md § UX patterns` if it exists), add "(Suggested for your app type)"
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

- Entity hierarchy (questionnaire conceptual-design 2.3)
- Permission levels (questionnaire conceptual-design 2.6)
- Greenfield/evolving status (questionnaire conceptual-design 2.9)
- `PROJECT_MODE` — derived from question 2.9 (greenfield -> `greenfield`, evolving -> `brownfield`); must be populated in `project/conventions.md`
- Metacommunication message (questionnaire Final Step, or metacomm-message 0.1)

### Additionally required for brownfield projects

- Existing tech stack (questionnaire conceptual-design 2.12)
- Migration constraints (questionnaire conceptual-design 2.13)

### Required with sensible defaults (inform user of default if missing)

| Field | Default | Inference Rule |
|-------|---------|----------------|
| `CODEBASE_DIR` | `.` | `.` for embedded, absolute path if workspace mode detected |
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
- Conceptual design details beyond conceptual-design 2.3/2.6 (free-form)
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
