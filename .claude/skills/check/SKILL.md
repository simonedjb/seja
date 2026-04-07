---
name: check
description: "Run quality checks: validation, code review, smoke tests, preflight, or framework health."
argument-hint: "<validate | review | smoke | preflight | health | test-plan | docs | telemetry | semiotic-inspection> [--depth <light|standard|deep>] [scope]"
compatibility: "Designed for Claude Code with SEJA framework"
metadata:
  last-updated: 2026-03-29 00:15:00
  version: 1.0.0
  category: analysis
  context_budget: heavy
  references:
    - general/report-conventions.md
    - project/frontend-standards.md
    - project/backend-standards.md
    - project/i18n-standards.md
    - project/security-checklists.md
    - general/review-perspectives.md
    - general/review-perspectives-index.md
    - general/review-log-template.md
---

## Quick Guide

**What it does**: Unified quality gate — runs validation scripts, code reviews, smoke tests, preflight checks, framework health diagnostics, or user test plan generation. One skill for all "is it OK?" questions.

**Example**:
> You: /check preflight
> Agent: Runs all validation scripts and reviews staged changes in one pass. Reports a go/no-go verdict.

> You: /check review staged
> Agent: Reviews staged changes against security, accessibility, performance, and other quality perspectives.

> You: /check smoke api
> Agent: Runs API smoke tests and reports which endpoints pass or fail.

> You: /check test-plan Test the new task filtering feature
> Agent: Produces a structured test plan with scenarios, step-by-step instructions, expected results, and edge cases that testers should verify.

> You: /check semiotic-inspection task-filtering
> Agent: Conducts a 5-step Semiotic Inspection Method (SIM) evaluation of the task-filtering feature's communicability. Analyzes metalinguistic, static, and dynamic signs independently, then collates and compares the three metacommunication messages to identify communicative problems.

**When to use**: Before committing, after making changes, or when you want to verify code quality, project health, framework integrity, generate a manual test plan, or evaluate interface communicability.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `validate [scope]` | -- | Run project validation scripts. Scope: `all`, `i18n`, `auth`, `migrations`, `constants`, `po`, `coverage`, `tests`, `spec` |
| `review [scope]` | -- | Structured code review against quality perspectives. Scope: `staged`, file path, or directory path |
| `smoke [scope]` | -- | Runtime smoke tests. Scope: `all`, `api`, `ui` |
| `preflight [scope]` | -- | Combined validate + review in one pass. Scope: `staged`, `all`, or directory path |
| `health` | -- | Framework self-diagnosis and integrity check. Supports `--verbose` |
| `test-plan [brief]` | -- | Generate a structured manual test plan for the given brief |
| `docs [--plugins LIST]` | -- | Documentation consistency check. Supports `--plugins`, `--verbose`, `--filter` |
| `telemetry` | -- | Usage analytics and skill invocation statistics |
| `--depth <level>` | No | Override review depth. Valid: `light`, `standard`, `deep` |

> One mode is required. Modes are mutually exclusive.

## Stack Filtering

Validate and preflight modes use stack-based filtering to run only the check scripts relevant to the project's technology stack.

**How it works:**

1. Read `BACKEND_FRAMEWORK` and `FRONTEND_FRAMEWORK` from `_references/project/conventions.md` (use `project_config.py` to parse the values).
2. Load `.claude/skills/scripts/check_plugin_registry.json` -- an array of plugin entries, each with a `stack.backend` and `stack.frontend` list.
3. For each plugin entry, include it if:
   - Its `stack.backend` list is empty (matches any backend) OR contains the project's `BACKEND_FRAMEWORK` value, **AND**
   - Its `stack.frontend` list is empty (matches any frontend) OR contains the project's `FRONTEND_FRAMEWORK` value.
4. Run only the matching scripts. Skip non-matching scripts silently.

**Fallback (legacy projects):** If `conventions.md` has no `BACKEND_FRAMEWORK` or `FRONTEND_FRAMEWORK` variables, run all scripts and log this warning if the BACKEND_FRAMEWORK or FRONTEND_FRAMEWORK variables cannot be inferred from the codebase:

> Warning: No stack framework variables found in conventions.md. Running all check scripts. Add BACKEND_FRAMEWORK and FRONTEND_FRAMEWORK to conventions.md to enable stack filtering.

## Adding a Check Plugin

To add a new check plugin to the system, follow these three steps:

1. **Create the script.** Add a new `check_<name>.py` in `.claude/skills/scripts/`. Include a `CHECK_PLUGIN_MANIFEST` YAML block in the module docstring declaring the plugin's metadata:

   ```python
   """
   Description of what this check does.

   CHECK_PLUGIN_MANIFEST:
     name: <human-readable name>
     stack:
       backend: [flask]   # or [any] for stack-agnostic
       frontend: [react]  # or [any] for stack-agnostic
     scope: <validate scope keyword, e.g. auth, i18n, constants>
     critical: true       # true if failure should block preflight
   """
   ```

2. **Register in the plugin registry.** Add a corresponding entry to `.claude/skills/scripts/check_plugin_registry.json` with `script`, `name`, `stack` (containing `backend` and `frontend` arrays), `scope`, and `critical` fields. These must match the values in the manifest.

3. **Automatic pickup.** No further wiring is needed. The check skill orchestrator reads the plugin registry at runtime and includes new scripts automatically when running validate or preflight modes for projects whose stack matches the plugin's declared requirements.

# Check

If there are no arguments, use the AskUserQuestion tool to ask which mode to run (if AskUserQuestion is not available, present as a numbered text list), with these options:
- "1. validate -- run project validation scripts (scope: all, i18n, auth, migrations, constants, po, coverage, tests, spec)"
- "2. review -- structured code review against quality perspectives (scope: staged, file, or directory)"
- "3. smoke -- runtime smoke tests against API endpoints or UI pages (scope: all, api, ui)"
- "4. preflight -- validate + review in one pass as a pre-merge checkpoint (scope: staged, all, or directory)"
- "5. health -- framework self-diagnosis and integrity check (7 built-in checks)"
- "6. test-plan -- generate a structured manual test plan from a brief or recent plans"
- "7. docs -- documentation consistency check via plugin-based scanners (paths, env vars, terminology)"
- "8. telemetry -- usage analytics and skill invocation statistics from telemetry.jsonl"
- "9. semiotic-inspection -- Semiotic Inspection Method (SIM) evaluation of interface communicability (scope: feature, page, flow)"

## Modes

| Mode | Description | Former skill |
|------|-------------|-------------|
| `validate [scope]` | Run project validation scripts | `/validate` |
| `review [scope]` | Structured code review against perspectives | `/review-code` |
| `smoke [scope]` | Runtime smoke tests (API/UI) | `/smoke-test` |
| `preflight [scope]` | Validate + review in one pass (pre-commit) | `/preflight` |
| `health [flags]` | Framework self-diagnosis | `/health` |
| `test-plan [brief]` | Generate manual test plan from recent plans | `/plan-user-test` |
| `docs [--plugins LIST]` | Documentation consistency check | -- |
| `telemetry` | Usage analytics from telemetry.jsonl | -- |
| `semiotic-inspection [scope]` | SIM-based communicability evaluation | -- |

## Definitions

Output folder: `${CHECK_LOGS_DIR}` (see project/conventions.md)
Filename pattern: `check-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)

Reserve the next global ID by running `python .claude/skills/scripts/reserve_id.py --type check --title '<title>'`. Use the returned 6-digit ID.

## Skill-specific Instructions

1. Run /pre-skill "check" $ARGUMENTS to add general instructions to the context window.

2. Parse the first argument to determine the mode. Remaining arguments are the scope.

---

### Mode: validate

Scope options: `all` (default) | `i18n` | `auth` | `migrations` | `constants` | `po` | `coverage` | `tests` | `spec`

> **Role boundary:** This skill is the *user-facing orchestrator*. The `standards-checker` agent is the *execution engine*.

1. Determine the validation scope from the argument (default: `all`).

2. **Apply stack filtering** (see [Stack Filtering](#stack-filtering) above). Before launching any agent, resolve the set of applicable scripts from the plugin registry. Pass only the matching script list to the `standards-checker` agent. If the project has no stack variables (legacy fallback), pass all scripts and include the warning in the report output.

3. Launch the appropriate agent(s):
   - For validation checks: launch the `standards-checker` agent with the scope
   - For `migrations`: launch both the `standards-checker` agent (for chain script) and the `migration-validator` agent (for deep file inspection and idempotency checks)
   - For `tests`: launch the `test-runner` agent with scope "all"
   - For `spec`: run `python .claude/skills/scripts/check_spec_conformance.py` directly (no agent needed)
   - For `all`: launch the `standards-checker` agent with "all"; also run `check_spec_conformance.py`; then ask the user whether to also run tests

4. Save the report to the output file, including:
   - *header*: `# Check <id> | CHORE<scope> | <current datetime> | Validation Report`
   - *scope*: what was validated
   - *summary table*: check name, status (PASS/FAIL/INFO), error count, warning count
   - *details*: for each failed check, list the specific issues
   - *overall status*: X/Y checks passed

5. Present the summary to the user, highlighting any failures.

6. Run /post-skill <id>.

---

### Mode: review

Scope options: `staged` (default) | file path | directory path

1. Determine the review scope:
   - If scope is "staged": the scope is `git diff --cached`
   - If scope is a file path: the scope is that file
   - If scope is a directory: the scope is all source files in that directory
   - If no scope: ask the user

   **Review depth:**
   If `--depth <light|standard|deep>` is provided, resolve the effective depth as `max(floor, flag)` where `floor` = `MINIMUM_REVIEW_DEPTH` from project/conventions.md (default: `light`). Pass the effective depth to the code-reviewer agent. If no `--depth` flag is provided, the code-reviewer evaluates all 16 perspectives (current behavior, equivalent to `deep`).

2. Launch the `code-reviewer` agent with the scope and review depth as input. The agent should use the two-stage loading protocol (see `general/review-perspectives.md` section "Two-Stage Loading"):
   - Load `general/review-perspectives-index.md` to see all 16 perspectives at a glance
   - Select 4-6 relevant perspectives based on the change content and scope
   - Load only the selected `review-perspectives/<tag>.md` files (not all 16)
   - For **deep** depth or when explicitly requested, load all perspective files instead
   - Evaluate selected perspectives and return a structured report with findings

3. Save the agent's report to the output file, including:
   - *header*: `# Check <id> | REVIEW<scope> | <current datetime> | Code Review: <short description>`
   - *scope*: what was reviewed (files, staged changes, directory)
   - *perspective evaluation*: table with Adopted/Deferred/N/A per perspective
   - *issues found*: prioritized list with severity, perspective, description, and file:line
   - *recommendations*: actionable items

4. Present the findings summary to the user, highlighting any HIGH severity issues.

5. Run /post-skill <id>.

---

### Mode: smoke

Scope options: `all` (default) | `api` | `ui`

> **Role boundary:** This skill is the *user-facing orchestrator*. The scripts are the *execution engines* — `smoke_test_api.py` exercises backend API endpoints, `smoke.spec.ts` walks UI pages via Playwright.

1. Determine the smoke test scope from the argument (default: `all`).

2. Execute the appropriate script(s):

   **For `api` scope:**
   Run `cd backend && python ../.claude/skills/scripts/smoke_test_api.py` via Bash. Capture full stdout output. This runs against an in-memory SQLite database using the Flask test client — no running servers required.

   **For `ui` scope:**
   First check if `e2e/smoke.spec.ts` exists. If not, inform the user: "UI smoke testing requires E2E infrastructure. Generate it via `/design` with `e2e != none`, or create `e2e/smoke.spec.ts` manually."
   If it exists, run `cd e2e && npx playwright test smoke.spec.ts` via Bash. Capture full stdout/stderr output. This requires both backend (port 5000) and frontend (port 3000) to be running.

   **For `all` scope:**
   Run API smoke test first (faster, independent). Then run UI smoke test if `e2e/smoke.spec.ts` exists.

   > **Note:** The API smoke test is driven by `.claude/skills/scripts/smoke_test_registry.json`. To add or modify endpoints, edit the registry JSON. The generic engine lives in `smoke_test_core.py`.

3. Parse the results:
   - **API results**: Extract the summary line (`PASS: N | WARN: N | FAIL: N`) and any FAIL details from stdout.
   - **UI results**: Extract pass/fail status from Playwright output and any runtime error details.

4. Save the report to the output file, including:
   - *header*: `# Check <id> | CHORE-X | <current datetime> | Smoke Test Report`
   - *scope*: what was tested (`api`, `ui`, or `all`)
   - *API results table* (if applicable): per-endpoint status
   - *UI results table* (if applicable): per-page/flow status
   - *captured errors*: full details of any failures
   - *overall verdict*: `PASS` (no errors) or `FAIL` (errors found)

5. Present the summary to the user, highlighting any failures.

6. If failures are found, ask the user whether to investigate and fix, create a plan, or dismiss.

7. Run /post-skill <id>.

---

### Mode: preflight

Scope options: `staged` (default) | `all` | directory path

Combines validate + review into a single pre-merge checkpoint.

1. Determine the scope:
   - `staged` (default): validate all + review staged changes
   - `all`: validate all + review all modified files (staged + unstaged)
   - A directory path: validate all + review files in that directory

2. **Apply stack filtering** (see [Stack Filtering](#stack-filtering) above). Resolve the set of applicable scripts from the plugin registry before launching validation. If the project has no stack variables (legacy fallback), pass all scripts and include the warning in the report output.

3. **Parallel fan-out**: Launch independent checks as concurrent Agent invocations (multiple Agent tool calls in a single message). Each check writes to a unique output section to avoid conflicts:
   - **Validation**: launch the `standards-checker` agent with scope "all" and the filtered script list
   - **Code review**: launch the `code-reviewer` agent with the determined review scope
   - **Smoke** (if plan's `smoke` field is `true`): launch smoke test in parallel with the above

   If any individual check fails (agent error, timeout), the other checks still produce results — do not abort the entire preflight.

4. **Gather and synthesize**: Collect results from all agents and save a combined report to the output file, including:
   - *header*: `# Check <id> | CHORE<scope> | <current datetime> | Preflight Check`
   - *validation summary*: table of check name, status (PASS/FAIL/INFO), error count, warning count
   - *code review summary*: perspective evaluation table with Adopted/Deferred/N/A
   - *issues found*: merged list from both checks, prioritized by severity
   - *overall status*: READY / NOT READY (READY only if all validation checks pass and no HIGH severity code review issues)

5. Present the overall status to the user with a clear go/no-go recommendation.

6. Run /post-skill <id>.

---

### Mode: health

Flags: `[--verbose]`

1. Run the following checks and collect results:

   #### Check 1: Skill System Integrity
   Run `python .claude/skills/scripts/check_skill_system.py`. Parse the output for errors and warnings. Report total skills found, errors, and warnings.

   #### Check 2: Orphaned Briefs
   Read `${BRIEFS_FILE}`. Scan for entries with status `STARTED` that have no matching `DONE` entry. Report the count and list each orphaned entry.

   #### Check 3: Stale Plans
   Read `${OUTPUT_DIR}/INDEX.md`. Identify plans with status `OPEN` whose creation date is more than 7 days ago. Report the count and list each stale plan.

   #### Check 4: Reference File Completeness
   Scan all `.claude/skills/*/SKILL.md` files for `metadata.references` entries. For each referenced file, verify it exists in `_references/`. Report any missing references. Distinguish between `general/` references (should always exist) and `project/` references (may not exist in framework-only repos).

   #### Check 5: Conventions Completeness
   Run `python .claude/skills/scripts/check_conventions.py`. Parse the output for errors (undefined variables) and warnings (unused definitions). Report PASS if no errors, WARN if only unused definitions exist, FAIL if any referenced variables are undefined.

   #### Check 7: Constitution Presence
   Check whether `_references/project/constitution.md` exists. If missing, report WARN status with message: "No project constitution found. Run `/design` to generate `project/constitution.md` with your project's immutable principles." If present, report PASS.

   #### Check 8: Skill Spec Compliance
   Run `python .claude/skills/scripts/check_skill_spec.py`. This validates all SKILL.md files against the agentskills.io specification (name format, description length, directory name match, optional fields). Report PASS if exit code 0, FAIL if exit code 1 with violation details.

2. Compile results into a health report:

   ```
   ## Framework Health Report

   | Check | Status | Details |
   |-------|--------|---------|
   | Skill System Integrity | PASS/WARN/FAIL | N errors, M warnings |
   | Orphaned Briefs | PASS/WARN | N orphaned entries |
   | Stale Plans | PASS/WARN | N stale plans (>7 days) |
   | Reference Completeness | PASS/WARN/FAIL | N missing references |
   | Conventions Completeness | PASS/WARN/FAIL | N errors, M warnings |
   | Constitution Presence | PASS/WARN | Present or missing |
   | Skill Spec Compliance | PASS/FAIL | N violations |

   Overall: X/7 checks passed
   ```

3. Save the report to the output file per report conventions.

4. Present the summary to the user, highlighting any failures or warnings.

5. Run /post-skill <id>.

---

### Mode: test-plan

Scope: a brief describing what to test. If no brief is provided, ask the user.

Output folder: `${USER_TESTS_DIR}` (see project/conventions.md)
Filename pattern: `usertest-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)

Reserve the next global ID by running `python .claude/skills/scripts/reserve_id.py --type usertest --title '<title>'`. Use the returned 6-digit ID.

As input to apply this mode, use only these folders (see project/conventions.md for paths):
- `${PLANS_DIR}`: these contain the generated plans (use `${OUTPUT_DIR}/INDEX.md` to identify relevant plans instead of scanning the directory)
- `${USER_TESTS_DIR}`: these contain the generated user test plans

1. Read `${OUTPUT_DIR}/INDEX.md` (the global artifact index). If it does not exist, run `python .claude/skills/scripts/generate_macro_index.py` to generate it. Filter for recently executed plans (status DONE) relevant to the brief. Read only the full plan files for the relevant IDs identified from the index.

2. Include the previously unchecked items from the user test plans folder in the analysis, if still applicable (i.e., not superseded by the latest changes) in the new report, so they don't get lost.

3. Phrase each to do item as a command to the user (for example, Navigate to <X>; do <A>, check <B>, do <C>. The expected outcome is <O>).

4. Save the information to a new output file, adopting a format similar to the existing entries, including:
   - *header*: `# User test <id> | <prefix><scope> | <current datetime> | <short title>`
   - *user brief*, *agent interpretation*, *files* -- per _references/general/report-conventions.md
   - *to do*: A brief enumeration of the plan steps

5. Run /post-skill <id>.

---

### Mode: docs

Flags: `[--plugins LIST] [--verbose] [--filter SEVERITY]`

Documentation consistency checker powered by `check_docs.py` with plugin-based scanners.

1. Run `python .claude/skills/scripts/check_docs.py` with any flags passed through:
   - `--plugins LIST`: Comma-separated plugin names to run (default: all)
   - `--verbose`: Show passing checks and extra detail
   - `--filter SEVERITY`: Minimum severity to report: `error`, `warning`, `info` (default: `info`)

   **Available plugins:**

   | Plugin | Description | Stack |
   |--------|-------------|-------|
   | `framework-integrity` | Validate CLAUDE.md skill/agent references exist on disk, Quick Guide presence | all |
   | `path-liveness` | Verify relative paths in .md files resolve to existing files | all |
   | `env-vars` | Cross-check documented vs referenced environment variables | django, node, next |
   | `command-refs` | Cross-check documented CLI commands against build targets | django, node, next |
   | `terminology` | Check for variant spellings against shared-definitions.md | all |

2. Parse the script output. Exit code 0 means no issues; exit code 1 means issues found; exit code 2 means script error.

3. Save the report to the output file, including:
   - *header*: `# Check <id> | CHORE-docs | <current datetime> | Documentation Consistency Report`
   - *summary*: error/warning/info counts
   - *per-plugin findings*: grouped by plugin name with severity, location, and message
   - *overall status*: PASS / ISSUES FOUND

4. Present the summary to the user, highlighting any errors or warnings.

5. Run /post-skill <id>.

---

### Mode: telemetry

Informational usage analytics. No check-log file is written.

1. Run `python .claude/skills/scripts/generate_telemetry_report.py` via Bash. Capture stdout.

2. Display the markdown output directly to the user.

---

### Mode: semiotic-inspection

Conducts a Semiotic Inspection Method (SIM) evaluation [SIM-2006; SemEng-Methods-2009, pp.26-33] of a project's interface communicability. SIM reconstructs the designer's metacommunication message by examining three classes of interface signs independently (segmented analysis), then collating and comparing them (synthesis). The agent acts as **evaluator-as-user-advocate** [SIM-2006, p.151] -- representing users' interests through HCI knowledge, not replacing them.

SIM evaluates the **emission** of metacommunication (what the designer's deputy communicates). It is complementary to CEM (which evaluates reception via observed breakdowns -- see the Communicability sub-sections in UX/DX review perspectives).

**Scope**: the user specifies what to inspect -- a feature name, page, user flow, or `all` for a broad inspection. The agent selects the portions of the artifact to inspect based on this scope.

#### Preparation

1. **Identify inspection context**: Read the project's metacommunication files to establish the designer's intended message:
   - `project/metacomm-as-is.md` or `project/design-intent-to-be.md` (who the users are, what they need, the design vision)
   - `project/conceptual-design-as-is.md` (entities, permissions, UX patterns)
   - `project/journey-maps-as-is.md` or `project/design-intent-to-be.md §15` (user flows and journeys)
   - `project/ux-design-standards.md` (if it exists)

2. **Establish focus of analysis**: Based on the scope argument, identify:
   - (i) Who are the intended users of the system (from metacomm files, user profiles, role families)
   - (ii) What are the top-level goals and activities that the system supports (from journey maps, conceptual design)

3. **Elaborate inspection scenarios**: Construct 1-3 inspection scenarios [SemEng-Methods-2009, p.28] that project the evaluation question onto the territory of possible interactions. Each scenario defines:
   - A user persona (from the project's role families or metacomm user profile)
   - A goal-directed activity (from journey maps or user flows)
   - The context and constraints of the activity

   Inspection scenarios are necessary because aimless interaction cannot provide the appropriate communicative intent for analysis.

#### SIM Step 1: Analysis of metalinguistic signs

Examine signs that **explicitly inform, illustrate, or explain** the meaning of other signs: help text, documentation, error messages, tooltips, tutorials, onboarding text, contextual help pages, confirmation dialogs.

For each inspection scenario:
- Read the project's help/documentation content related to the scenario's scope (contextual help files, error message definitions, onboarding flows)
- Read the frontend code for metalinguistic elements: error messages, validation messages, empty state text, helper text, modal explanations, toast notifications
- Fill out the **metacommunication template** based on what metalinguistic signs communicate:
  > "Here is my understanding of who you are [from metalinguistic signs], what I've learned you want or need to do [from metalinguistic signs], in which preferred ways, and why. This is the system that I have therefore designed for you, and this is the way you can or should use it in order to fulfill a range of purposes that fall within this vision."
- Record the metacommunication message X (metalinguistic)

#### SIM Step 2: Analysis of static signs

Examine signs whose meaning is interpreted independently of temporal and causal relations -- a **single-moment snapshot**: labels, icons, form fields, layout structure, menu options, navigation hierarchy, button text, visual grouping, typography choices.

For each inspection scenario:
- Read the frontend code for static interface elements: component structure, layout, labels, icons, navigation, form fields
- Analyze what these signs communicate about available actions, their relationships, and the designer's model of the user
- Fill out the metacommunication template again **independently** (do not reference step 1 findings)
- Record the metacommunication message Y (static)
- Note any mismatches or elaborations compared to what metalinguistic signs communicated

#### SIM Step 3: Analysis of dynamic signs

Examine signs bound to temporal and causal aspects -- signs that **emerge through interaction**: state transitions, animations, loading states, form validation feedback, hover/focus states, progressive disclosure, navigation transitions.

For each inspection scenario:
- Read the frontend code for dynamic behavior: event handlers, state transitions, conditional rendering, animation triggers, validation flows, loading states
- Analyze what these signs communicate about system behavior, cause-and-effect relationships, and the consequences of user actions
- Fill out the metacommunication template again **independently**
- Record the metacommunication message Z (dynamic)

#### SIM Step 4: Collate and compare metacommunication messages

Compare messages X, Y, and Z. Apply the **5 scaffold questions** [SIM-2006, p.153]:

1. Would the user plausibly be able to interpret this sign differently? How? Why?
2. Would this interpretation still be consistent with the design intent?
3. Does the current interpretive path remind of other interpretive paths identified in the inspection? Which? Why?
4. Can classes of static and dynamic signs be drawn from the semiotic analysis? Which?
5. Are there static or dynamic signs that are apparently misclassified according to the classes identified? Can this affect communication?

Evaluate the metacommunication quality across sign classes using the four SigniFYIng Interaction dimensions [de Souza et al., 2016, Ch.3 pp.70-71]:

1. **Consistency**: Do all three sign classes (metalinguistic, static, dynamic) convey the same message about each feature? Where they diverge, which class is authoritative and which is misleading?
2. **Completeness**: Is every aspect of the designer's metacommunication message conveyed by at least one sign class? Are there fields in the metacommunication template that no sign class addresses?
3. **Redundancy**: Are critical messages reinforced across multiple sign classes (positive redundancy)? Are there contradictory redundancies where sign classes actively conflict?
4. **Distribution**: Is metacommunication over-reliant on one sign class? For example, if all meaning resides in metalinguistic signs (help text, documentation) but static signs (layout, labels) and dynamic signs (feedback, transitions) are silent, users who don't read help will miss the message entirely.

For each dimension, record specific findings with sign evidence. Flag any dimension rated "poor" as a communicability risk.

#### SIM Step 5: Final evaluation of communicability

Produce a conclusive appreciation [SIM-2006, pp.153-154] containing:

i. A brief description of SIM and how it was applied
ii. The criteria for selecting which portions of the artifact were inspected
iii. For each sign class (metalinguistic, static, dynamic):
   - Relevant signs identified (with justification)
   - Sign systems and sign classes in use
   - The reconstructed metacommunication message for that class
iv. A substantiated judgment of communicative problems (actual or potential) that may prevent users from getting the designer's message and interacting productively

#### Output

Save the report to `${CHECK_LOGS_DIR}/check-<id>-semiotic-inspection-<scope-slug>.md` with:
- *header*: `# Check <id> | CHORE-O | <current datetime> | Semiotic Inspection: <scope>`
- *inspection context*: user profiles, goals, scenarios
- *per-sign-class analysis*: metalinguistic (X), static (Y), dynamic (Z) -- each with relevant signs, sign classification, and reconstructed metacommunication message
- *contrastive analysis*: scaffold questions applied, then the 4 quality dimensions (consistency, completeness, redundancy, distribution) with per-dimension findings and risk flags
- *communicability judgment*: substantiated assessment with specific recommendations
- *sign inventory*: table of all significant signs identified, their class, and their communicative role

Run /post-skill <id>.

3. Do **not** reserve an ID, write a check-log file, or run /post-skill. This mode is read-only and informational.
