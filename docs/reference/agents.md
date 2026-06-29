---
diataxis: reference
freshness: on-structural-change
last-reviewed: 2026-05-05
---

# SEJA agents catalog

Agents are subagent prompts under `.claude/agents/` that execute a single role on one artifact type. Skills invoke agents; you never invoke them directly. Each agent operates in an isolated context window with a defined set of tools, receives its inputs from the calling skill, and returns a structured artifact.

Agents follow the single-responsibility principle across three roles: evaluators review artifacts through a quality lens, generators produce self-contained artifacts from well-defined inputs, and executors (not listed here) are constructed dynamically by `/implement` auto mode from plan step metadata.

## Evaluator agents

Evaluator agents review artifacts against quality perspectives and return structured findings.

| Name | Purpose | Invoked by | What it produces |
|---|---|---|---|
| `code-reviewer` | Review code diffs against 16 engineering and design perspectives with depth-gating (deep evaluates all 16; standard/light use a shortlisted subset). | `/critique review`, `/critique preflight`, `/implement` auto mode (generator-critic loop) | Structured report with perspective evaluation table (Adopted/Deferred/N/A per perspective), issues by severity, and recommendations |
| `council-debate` | Run a structured expert debate with five fixed archetypes plus 0-2 brief-specific experts to surface trade-offs, tensions, and insights. | `/research --deep` | Debate transcript: Round 1 position statements, Round 2 cross-examination, synthesis with consensus areas, unresolved tensions, and recommended path |
| `harness-health-evaluator` | Run 9 built-in harness self-diagnosis checks: skill system, briefs hygiene, plans hygiene, references, conventions, constitution, spec compliance, pending ledger, harness drift. | `/critique health` | Harness Health Report: 9-row status table (PASS/WARN/FAIL per check) with overall tally and per-check detail |
| `migration-validator` | Validate Alembic migration chain integrity, check for idempotency issues, PostgreSQL syntax problems, and common migration pitfalls. | `/critique` (migration scope) | Migration Validation Report: chain status, critical/warning/info issues by file, summary tally |
| `plan-reviewer` | Review a plan against engineering and design perspectives using a complexity-gated two-phase process (Phase 1 scan, Phase 2 deep-dives). | `/plan` (standard mode, post-generation) | Review log: Phase 1 perspective triage table, Phase 2 deep-dive findings, conflict checks, plan amendments |
| `research-reviewer` | Evaluate design decisions, open-ended questions, and trade-offs against engineering and design perspectives. | `/research` (optional final pass) | Research review: perspective evaluation table, key findings, recommendations ordered by impact, trade-off analysis |
| `semiotic-inspector` | Conduct a Semiotic Inspection Method (SIM) evaluation of interface communicability across metalinguistic, static, and dynamic sign classes. | `/critique semiotic-inspection` | SIM Report: per-sign-class analysis, contrastive analysis with 4 quality dimensions, communicability judgment, sign inventory table |
| `standards-checker` | Run all project validation scripts and aggregate results into a unified compliance report. | `/critique validate` | Standards Compliance Report: summary table (check name, PASS/FAIL, error/warning counts), details for failures and warnings, overall tally |
| `test-runner` | Run backend (pytest) and frontend (vitest) test suites, parse output, and classify failures with context. | `/critique` (test scope) | Test Results: passed/failed/skipped counts, failures with classification (test bug, source bug, environment, flaky) and suggested fixes |

## Generator agents

Generator agents produce self-contained artifacts from well-defined inputs. They receive the project constitution in their prompt for trust boundary enforcement.

| Name | Purpose | Invoked by | What it produces |
|---|---|---|---|
| `architecture-explainer` | Survey system structure, map boundaries and communication patterns, surface key design decisions for onboarding developers. | `/explain architecture` | Architecture explanation report with system overview, diagrams, component inventory, design decisions, data flow, and cross-cutting concerns |
| `communication-generator` | Generate tailored stakeholder-facing material for a specific audience segment (EVL, CLT, USR, ACD). | `/communicate` | Markdown and/or HTML output files with audience-specific content, Diataxis classification, and project context |
| `document-generator` | Generate or update project documentation for a specific type (readme, contextual-help, api-reference, drr, help-center, changelog). | `/document` | Markdown files per documentation type in project-specific locations |
| `evolution-explainer` | Mine plan history to trace how a feature reached its current state, building a chronological timeline of waves and design rationale. | `/explain behavior-evolution` | Behavior evolution report with current snapshot, timeline table, before/after narratives per wave, and cumulative rule ledger |
| `explanation-generator` | Generate explanation reports for behavior, code, or data-model modes with visual diagrams and analogies. | `/explain behavior`, `/explain code`, `/explain data-model` | Explanation report (behavior, dev-onboarding, or data-model) with analogies, diagrams, walk-throughs, and gotchas |
| `onboarding-generator` | Generate a personalized onboarding plan for a new team member based on role family (BLD/SHP/GRD) and expertise level (L1-L3). | `/onboard` | Onboarding plan with welcome, universal foundation, role-specific context, level-specific depth, 30-60-90 timeline, and reading list |
| `test-plan-generator` | Generate a structured manual test plan from a brief and the most recent DONE plans, carrying forward unchecked items. | `/critique test-plan` | User-test artifact with test to-do list phrased as imperative commands with expected outcomes |
