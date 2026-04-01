# Framework Structure

Detailed inventory of the SEJA Codex framework components. Auto-loaded when working on `.codex/` files.

## Skills

16 skills in `.codex/skills/<name>/SKILL.md` -- 14 user-facing + 2 internal lifecycle hooks (pre-skill, post-skill). Each user-facing skill includes a `## Quick Guide` section with designer-friendly description, example, and usage scenario. The `/plan` skill supports three modes: standard planning, `--light` (lightweight proposals), and `--roadmap` (full product roadmap). Pre-skill executes as a pipeline of 6 composable stages (help, brief-log, orphan-check, budget-eval, ref-load, constitution) -- 3 critical (always run) and 3 non-critical (error-isolated, skippable). Skills can declare `skip_stages: [stage-id, ...]` in their YAML frontmatter (`metadata.skip_stages`) to opt out of non-critical stages.

## Agent-Agnostic References

Shared across `.claude` and `.codex` frameworks, located in `_references/`:

- General references (15 + 16 per-perspective + 8 per-onboarding + 5 per-communication): `general/*.md` files (including `general/threat-model.md` -- framework threat model with STRIDE-lite vectors, trust boundaries, and mitigation status; `general/getting-started.md` -- step-by-step onboarding guide for new SEJA users; `general/recipes.md` -- common multi-skill workflow recipes), `general/review-perspectives/` with Essential/Deep-dive tiers (P0-P4) and an auto-generated Essential summary, `general/onboarding/` with role families (BLD/SHP/GRD) and expertise levels (L1-L5), and `general/communication/` with audience segments (EVL/CLT/USR/ACD).
- Template references (43): `template/*.md`, `template/*.json`, `template/agent/*.yaml`, and `template/demo/` -- used by `/design` to generate project-specific files. Includes `template/constitution.md` for immutable project principles (copied by `/seed`, instantiated by `/design`), `template/cd-as-is-changelog.md` for the separated conceptual design changelog, `template/agent/` for agent-facing structured specifications (constraints, entities, permissions, spec-checks), and `template/demo/` (5 files: pre-filled conventions, constitution, conceptual design, metacomm, and walkthrough for the `/seed --demo` hello-world experience).
- Project-specific references: `project/*.md` and `project/agent/*.yaml` -- generated per-project by `/design`. Includes `project/constitution.md` (immutable principles -- required for new projects; `/check health` validates its presence as Check 7; existing projects without it remain functional), `project/agent/` (agent-facing structured specs for automated validation), conceptual-design files (`project/conceptual-design-as-is.md`, `project/cd-as-is-changelog.md`, `project/conceptual-design-to-be.md`), and metacomm file pairs (`project/metacomm-as-is.md`, `project/metacomm-to-be.md`).

## Helper Scripts

35 scripts in `.codex/skills/scripts/` -- validation checks, index generators, conversion utilities, the central `project_config.py` module that parses `project/conventions.md` to supply all scripts with project-specific paths and settings, `run_all_checks.py` (CI-independent validation orchestrator that discovers and runs all check scripts with unified exit codes and JUnit XML output), and `check_docs.py` (plugin-based documentation consistency checker with 5 scanners: framework integrity, path liveness, env vars, command refs, terminology).

## Subagent Prompts

5 reusable subagent prompts in `.codex/agents/`.

## Path-Scoped Rules

7 rule files in `.codex/rules/` (including this one) -- auto-loaded when Codex works on files matching the rule's scope.
