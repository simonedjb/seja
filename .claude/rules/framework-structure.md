---
paths:
  - ".claude/**"
---
# Framework Structure

Detailed inventory of the SEJA Claude framework components. Auto-loaded when working on `.claude/` files.

## Skills

15 skills in `.claude/skills/<name>/SKILL.md` -- 13 user-facing + 2 internal lifecycle hooks (pre-skill, post-skill). The `/document` skill generates and updates project documentation based on plan Docs: fields or auto-detected changes. Each user-facing skill includes a `## Quick Guide` section with designer-friendly description, example, and usage scenario. The `/plan` skill supports three modes: standard planning, `--light` (lightweight proposals), and `--roadmap` (full product roadmap). Pre-skill executes as a pipeline of 7 composable stages (help, brief-log, orphan-check, budget-eval, ref-load, constitution) -- 3 critical (always run) and 4 non-critical (error-isolated, skippable). Skills can declare `skip_stages: [stage-id, ...]` in their YAML frontmatter (`metadata.skip_stages`) to opt out of non-critical stages.

## Agent-Agnostic References

Shared reference files located in `_references/`:

- General references (20 + 16 per-perspective + 8 per-onboarding + 5 per-communication): `general/*.md` files (including `general/threat-model.md` -- framework threat model with STRIDE-lite vectors, trust boundaries, and mitigation status; `general/getting-started.md` -- step-by-step onboarding guide for new SEJA users; `general/recipes.md` -- common multi-skill workflow recipes; `general/documentation-quality.md` -- documentation quality standard with Diataxis classification, freshness policy, and structural-completeness rules; `general/batch-execution-pattern.md`, `general/ci-integration.md`, `general/coding-standards.md`, `general/constraints.md`, `general/permissions.md`, `general/progress-file-pattern.md`, `general/script-manifest.md`, `general/skill-graph.md`), `general/review-perspectives/` with Essential/Deep-dive tiers (P0-P4) and an auto-generated Essential summary, `general/onboarding/` with role families (BLD/SHP/GRD) and expertise levels (L1-L5), and `general/communication/` with audience segments (EVL/CLT/USR/ACD).
- Template references (51): `template/*.md`, `template/*.json`, `template/agent/*.yaml`, `template/ci/`, `template/demo/`, and `template/docs/` -- used by `/design` to generate project-specific files. Includes `template/constitution.md` for immutable project principles (copied by `/seed`, instantiated by `/design`), `template/cd-as-is-changelog.md` for the separated conceptual design changelog, `template/agent/` for agent-facing structured specifications (constraints, entities, permissions, spec-checks), `template/demo/` (5 files: pre-filled conventions, constitution, conceptual design, metacomm, and walkthrough for the `/seed --demo` hello-world experience), and `template/docs/` (6 documentation templates with `freshness` and `diataxis` classification metadata; the contextual-help template documents the expanded 6-section pattern).
- Project-specific references: `project/*.md` and `project/agent/*.yaml` -- generated per-project by `/design`. Includes `project/constitution.md` (immutable principles -- required for new projects; `/check health` validates its presence as Check 7; existing projects without it remain functional), `project/agent/` (agent-facing structured specs for automated validation), conceptual-design files (`project/conceptual-design-as-is.md`, `project/cd-as-is-changelog.md`), design-intent artifacts (three-layer model: `project/design-intent-to-be.md` -- fresh intent, human-maintained working document; `project/design-intent-established.md` -- processed intent with preserved rationale, human-maintained, never agent-altered; `project/conceptual-design-as-is.md` + `project/metacomm-as-is.md` -- implementation state, agent-maintained via post-skill), metacomm as-is (`project/metacomm-as-is.md`), and journey map files: `project/journey-maps-as-is.md` -- implemented journeys, agent-maintained (standalone); JM-TB-NNN designed journeys now live in `project/design-intent-to-be.md §15` (working) and `project/design-intent-established.md §15` (validated promotion archive); JM-E-NNN discovered journeys now live in `project/ux-research-new.md` (unprocessed) and `project/ux-research-established.md §5` (processed, human-only, append-only, agents must NOT modify). UX research files renamed from `user-research-*` to `ux-research-*` to reflect broader scope. The To-Be / As-Is Registry in `conventions.md` declares all registered to-be/established/as-is file triples with a Section column (enabling multi-artifact-type files; tools discriminate artifact types by ID prefix -- JM-TB-NNN vs JM-E-NNN) and is the single source of truth for `/design`, `/explain spec-drift`, and post-skill DONE marker proposals. Lifecycle markers (`STATUS: IMPLEMENTED`, `ESTABLISHED:`) defined in `general/shared-definitions.md` track the lifecycle of individual to-be items; agents may read and apply IMPLEMENTED markers but must never alter existing markers.

## Helper Scripts

39 scripts in `.claude/skills/scripts/` -- validation checks, index generators, conversion utilities, the central `project_config.py` module that parses `project/conventions.md` to supply all scripts with project-specific paths and settings, `run_all_checks.py` (CI-independent validation orchestrator that discovers and runs all check scripts with unified exit codes and JUnit XML output), and `check_docs.py` (plugin-based documentation consistency checker with 6 scanners: framework integrity, path liveness, env vars, command refs, terminology, structural-completeness).

## Subagent Prompts

10 subagent prompts in `.claude/agents/`, organized by role:

- **Evaluator agents** (7): review artifacts against quality perspectives -- advisory-reviewer, code-reviewer, council-debate, migration-validator, plan-reviewer, standards-checker, test-runner.
- **Generator agents** (3): produce self-contained artifacts from well-defined inputs -- communication-generator, onboarding-generator, document-generator. Invoked by thin-skill wrappers that handle argument parsing, interactive prompts, and lifecycle hooks. Generator agents must receive the project constitution as part of their prompt for trust boundary enforcement.
- **Executor agents** (pattern): execute plan steps in isolated context windows. Used by `/implement` auto mode. Not standalone prompt files -- the implement skill constructs their prompts dynamically from plan step metadata.

## Path-Scoped Rules

7 rule files in `.claude/rules/` (including this one) -- auto-loaded when Claude works on files matching the rule's scope.

## Governance

### Skill Count
New skills must justify that their functionality cannot be a mode of an existing skill. The `/check` consolidation (8 modes in one skill) is the model to follow for skills that share a common execution pattern. Skills serving distinct communicative purposes may justify independent existence when they meet 3 or more of these 4 criteria: (a) distinct user intent and mental model, (b) disjoint reference sets, (c) incompatible execution topology, (d) different output strategy. Current count: 15 skills (13 user-facing + 2 internal lifecycle hooks).

### Agent Count
New agents must justify that their domain is distinct from existing agents. Agents follow single-responsibility principle across three roles:
- **Evaluator**: each reviews one type of artifact through one lens (code diffs, plans, design decisions, debates, validation scripts, test suites, migrations).
- **Generator**: each produces one type of artifact from well-defined inputs (communication material, onboarding plans, documentation). Invoked by thin-skill wrappers, not directly by users.
- **Executor**: dynamically constructed by `/implement` auto mode (not standalone prompt files).
Current count: 10 agents (7 evaluator + 3 generator).

### agentskills.io Spec Alignment
SEJA SKILL.md frontmatter follows the [agentskills.io](https://agentskills.io) universal specification. Top-level fields (`name`, `description`, `compatibility`) conform to the spec; SEJA-specific fields (`context_budget`, `eager_references`, `references`, `skip_stages`, `plan_format_version`, `questionnaire_version`) are namespaced under `metadata` to avoid conflicts with future spec fields. New skills must validate against the agentskills.io spec (enforced by `check_skill_spec.py`).

### Architectural Decisions

**Pre/post-skill monolithic pipelines**: Pre-skill (6 stages) and post-skill (13 steps) are intentionally monolithic. The full lifecycle is readable in a single file. Decomposing into micro-hooks would add file count and configuration without solving an actual problem. The `skip_stages` mechanism handles per-skill overrides. Revisit only if a stage needs independent versioning.

**Explain/document separation**: `/explain` (epistemic -- understanding existing system) and `/document` (productive -- generating documentation artifacts) remain separate skills. They have different user intents, different output topologies (`_output/explained-*` vs. project source locations), disjoint reference sets (design specs vs. doc templates), and incompatible interaction patterns (ID-reserved analysis reports vs. template-based generation). The spec-drift mode's interactive sync workflow has no analogue in any document mode. Revisit if the two skills develop shared output conventions, shared references, or if user feedback shows intent confusion. (advisory-000153)

**Onboarding/document separation**: `/onboarding` (person-centric onboarding plans) and `/document` (artifact-centric project documentation) remain separate skills. Onboarding has interactive argument resolution, role-conditional project scanning, batch mode with parallel subagents, date-versioned output, and zero reference overlap with document. Onboarding implements a pedagogical framework (Dreyfus-aligned levels, role families, progressive disclosure layers), not a document template. Revisit if onboarding loses its interactive/batch capabilities or if reference sets converge. (advisory-000156)

**Agent single-responsibility**: Each agent operates on one type of artifact through one lens. Evaluators: `code-reviewer` reviews diffs, `plan-reviewer` reviews plans, `advisory-reviewer` reviews design decisions, `council-debate` runs structured debates, `standards-checker` aggregates script results, `test-runner` runs test suites, `migration-validator` validates migrations. Generators: `communication-generator` produces stakeholder material, `onboarding-generator` produces onboarding plans, `document-generator` produces project documentation. Do not merge agents or add cross-cutting responsibilities to existing agents.

**Generator-critic loops in auto mode**: `/implement` auto mode uses a bounded generator-critic loop (max 2 retries) when the code-reviewer identifies critical findings during the quality gate. Interactive (manual) mode retains advisory-only review — the user decides what to fix. Rationale: auto mode has already opted out of per-step human oversight, so automated fix attempts improve output quality without undermining user agency. The 2-iteration cap prevents runaway token consumption.

**Parallel fan-out for preflight checks**: `/check preflight` launches independent sub-checks (validate and review) as parallel Agent invocations, then synthesizes their results into a unified report. Each check writes to a unique output section to avoid conflicts. If one check fails, the other still produces results. Rationale: reduces wall-clock time for preflight checks without sacrificing completeness. The pattern applies to any future check modes that are independent and stateless.

**Meta-skills deferral**: Runtime skill generation (agents creating new SKILL.md files at runtime, per the ADK "Skill Factory" pattern) is deferred. Prerequisites for adoption: (1) agentskills.io spec compliance is enforced via automated validation (plan-000196 -- done); (2) a permission inheritance model is defined -- generated skills must inherit the permission ceiling of their parent skill; (3) constitution injection is mandatory for generated skills (cannot bypass); (4) generated skills cannot declare new file-write permissions beyond their parent's scope; (5) a "skill template" factory pattern (constrained parameters, pre-approved templates) is designed as the safe middle ground between full generation and prohibition. Revisit when prerequisites 1-4 are met. Reference: advisory-000188, council debate synthesis.

## Reference File Maintainer Summary

Quick-reference guide for agents: which files can be written to, which are read-only.
Classification values are defined in `_references/general/shared-definitions.md` -- File Maintainer Classification.

### Group A -- Project-specific files (`project/`)

| File | Maintained by | Notes |
|------|---------------|-------|
| `project/constitution.md` | Human | Never agent-altered |
| `project/design-intent-to-be.md` | Human | §15 Designed User Journeys (JM-TB-NNN working); agents may propose changes via AskUserQuestion only |
| `project/design-intent-established.md` | Human | §15 Designed User Journeys (validated JM-TB-NNN archive); never agent-altered |
| `project/ux-research-new.md` | Human | Includes §5 Discovered User Journeys (unprocessed JM-E-NNN) |
| `project/ux-research-established.md` | Human | §5 Discovered User Journeys: append-only; agents must NOT modify |
| `project/conceptual-design-as-is.md` | Agent | Auto-updated by post-skill |
| `project/metacomm-as-is.md` | Agent | Auto-updated by post-skill |
| `project/journey-maps-as-is.md` | Agent | Auto-updated by post-skill |
| `project/conventions.md` | Human / Agent | Seeded by /design; primary human configuration file |
| Standards files (backend, frontend, testing, etc.) | Human / Agent | Seeded by /design; human-owned after generation |

### Group B -- Framework source files (`general/`, `template/`)

Both framework authors and framework tooling (e.g., skills that generate index or summary files) may update these files.

| Path | Maintained by | Notes |
|------|---------------|-------|
| `general/*.md` | Human / Agent | Framework guidance; most files human-authored, some updated by agents |
| `template/*.md` | Human / Agent | Templates; human-authored framework source, may be updated by framework tooling |
