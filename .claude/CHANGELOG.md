# SEJA-Claude Changelog

All notable changes to the SEJA-Claude framework are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [2.7.0] -- 2026-04-07 00:22 UTC

### Added
- `check_design_output.py` -- validates design output files (5 scanners: entity-permission alignment, section completeness, cross-file consistency, template conformance, variable resolution)
- `test_check_design_output.py` -- unit tests for design output validation
- `check_plan_coverage.py` -- verifies plan steps trace back to design-intent REQ markers; supports `advisory` (informational) and `blocking` (preflight gate) enforcement modes
- `test_check_plan_coverage.py` -- unit tests for plan coverage check
- `bump_version.py` -- atomic version-bump script updating `.claude/skills/VERSION`, `.seja-version`, and validating CHANGELOG heading; supports `--dry-run`
- `figma-make-integration.md` -- guide for using Figma Make alongside SEJA (handoff protocol, intake checklist, MCP Server conventions, token sync)
- Versioning section in `shared-definitions.md` -- documents the three version files (VERSION, CHANGELOG, .seja-version), their distinct purposes, and maintenance rules
- Requirement ID Convention section in `shared-definitions.md` -- defines `REQ-TYPE-NNN` markers for design-intent traceability (ENT, PERM, VAL, UX, MC, JM, I18N, DELTA prefixes)
- `Traces` field in plan step format -- links plan steps to design-intent requirements (`REQ-xxx` IDs)
- Requirements extraction pass in `/plan --roadmap` workflow -- extracts REQ index from design-intent before decomposition
- Coverage check integration in `/plan` (advisory after steps) and `/plan --roadmap` (aggregate after all plans)
- Design output verification pass in `/design` skill -- runs `check_design_output.py` after file generation
- `check_design_output` and `check_plan_coverage` added to `run_preflight_fast.py` preflight pipeline

### Changed
- Script count increased from 39 to 43 (4 new scripts: check_design_output.py, check_plan_coverage.py, bump_version.py, and their tests)
- `check_version_changelog_sync.py` now validates all CHANGELOG `##` headings for `[x.y.z]` bracket format (warns on bare-date headings)
- `.seja-version` dogfood policy: framework repo's `.seja-version` now tracks the current release version (updated from 2.0.0 to 2.7.0)
- Backfilled bare-date CHANGELOG heading `## 2026-03-30 00:00 UTC` as `## [2.0.1] -- 2026-03-30 00:00 UTC`
- `backend-standards.md` template restructured with improved section organization
- `design-intent-to-be.md` template updated with REQ marker placeholders
- `api.md` review perspective expanded with additional CDN questions
- `getting-started.md` expanded with additional onboarding content
- `recipes.md` expanded with new multi-skill workflow recipes
- `/check` semiotic-inspection mode added -- SIM-based communicability evaluation (5-step analysis of metalinguistic, static, and dynamic signs)

## [2.6.0] -- 2026-04-02 00:00 UTC

### Added
- `compatibility` field in all 15 SKILL.md frontmatter files for agentskills.io spec alignment
- `check_skill_spec.py` -- validates SKILL.md files against agentskills.io spec (name rules, description, compatibility, metadata structure)
- `generate_skill_graph.py` -- generates skill-graph.json from skill-graph.md for programmatic skill-dependency lookup
- `generate_skills_manifest.py` -- generates skills-manifest.json (L1 metadata index for fast skill scanning, ~100 tokens per skill)
- `skills-manifest.json` -- L1 metadata index of 13 user-facing skills (name, description, argument_hint, category, version)
- `compaction-check` stage in pre-skill pipeline (non-critical) -- warns when session has many skill invocations; pipeline now has 7 stages (3 critical + 4 non-critical)
- Generator-critic retry loop in `/implement` auto mode -- bounded loop (max 2 retries) when code-reviewer finds critical findings during quality gate; interactive mode unchanged
- Parallel fan-out for `/check preflight` -- launches validate and review as concurrent Agent invocations, synthesizes unified report
- Meta-skills deferral ADR -- documents prerequisites for runtime skill generation (permission inheritance, constitution injection, template factory pattern)
- agentskills.io Spec Alignment section in `framework-structure.md` governance documentation
- Preflight checks for skills-manifest and skill-spec validation in `run_preflight_fast.py`

### Changed
- Script count increased from 35 to 39 (4 new scripts: check_skill_spec.py, generate_skill_graph.py, generate_skills_manifest.py, check_version_changelog_sync.py)
- Pre-skill pipeline expanded from 6 to 7 composable stages
- `generate_cheatsheet.py` now escapes pipe characters in description and argument_hint fields for correct markdown table rendering
- `/check preflight` rewritten with parallel fan-out pattern and failure isolation

## [2.5.0] -- 2026-04-02 00:00 UTC

### Changed
- Questionnaire sections renumbered sequentially by tier order: M->0, 0->1 (renamed "Basic Definitions", slug `quick-start`->`basic-definitions`), 2->2, 8->3, 9->4, 10->5, 1->6, 3->7, 4->8, 5->9, 6->10, 7->11. All question sub-numbers updated to match new section prefixes.
- `/design` skill references migrated from section numbers to slugs for cross-reference stability; `questionnaire_version` bumped from 3 to 6
- Metacommunication message moved from mandatory conceptual-design field (old 2.10) to the questionnaire Final Step; agent now generates a recommended message from prior answers if Section metacomm-message was skipped
- Post-Questionnaire Checklist now uses slug-based references

### Removed
- `.codex/` framework mirror and all Codex-specific files (`AGENTS.md`, `agents-md.md` template, `codex-onboarding-guide.md`, `migrate_claude_to_codex.py`). The framework is now Claude-only.
- `/check health` Check 5 (.claude/.codex sync) removed; remaining checks renumbered (5=Conventions, 6=Constitution). Health report total reduced from 7 to 6.

### Migration (for existing projects)

- **Questionnaire**: consumed once during `/design`; no migration needed for filled-out projects. Old section numbers remain documented in the Version History table.
- **Framework files**: auto-updated by `/upgrade`. Running `/upgrade` will pull the renumbered questionnaire and slug-aware design skill.
- **Existing plans/advisories referencing old section numbers**: numbers in historical documents remain valid as point-in-time records. Prefer slugs in new documents.

## [2.4.0] -- 2026-04-02 13:04 UTC

### Added
- `## 5. Discovered User Journeys` section in `ux-research-established.md` and `ux-research-new.md` -- absorbs `journey-maps-established.md`; uses JM-E-NNN stable IDs, required research citation, Source column, Processing Log; agent-off-limits rule applies to whole file.
- `## 15. Designed User Journeys` section in `design-intent-to-be.md` and `design-intent-established.md` -- absorbs `journey-maps.md`; uses JM-TB-NNN stable IDs, IMPLEMENTED/ESTABLISHED lifecycle markers; §16 (CD Delta) and §17 (Metacomm Delta) renumbered from §15/§16.
- Section column in the To-Be / As-Is Registry (`conventions.md`) -- enables multi-artifact-type files; tools discriminate artifact types by ID prefix (JM-TB-NNN vs JM-E-NNN).

### Changed
- `user-research-established.md` renamed to `ux-research-established.md`; `user-research-new.md` renamed to `ux-research-new.md` -- reflects broader UX research scope.
- `USER_RESEARCH_NEW` and `USER_RESEARCH_ESTABLISHED` variables in `conventions.md` renamed to `UX_RESEARCH_NEW` and `UX_RESEARCH_ESTABLISHED`; file paths updated accordingly.
- `JOURNEY_MAPS` and `JOURNEY_MAPS_ESTABLISHED` variables removed from `conventions.md` (content absorbed into `DESIGN_INTENT_TO_BE §15` and `UX_RESEARCH_ESTABLISHED §5`).
- post-skill step 2d: reads JM-TB-NNN entries from `design-intent-to-be.md §15`; reads JM-E-NNN entries from `ux-research-established.md §5`.
- `/explain spec-drift --promote`: JM-TB-NNN items promote to `design-intent-established.md §15`; JM-E-NNN items noted as research-grounded with no promotion target.
- `/design` Mode 1: generates `ux-research-established.md` and `ux-research-new.md` (not `user-research-*`); no longer generates standalone `journey-maps.md` or `journey-maps-established.md`.

### Removed
- `_references/template/journey-maps-established.md` -- content absorbed into `ux-research-established.md §5`.
- `_references/template/journey-maps.md` -- content absorbed into `design-intent-to-be.md §15`.

### Migration (for existing projects)

- **No breaking changes to existing project data.** Existing `journey-maps.md` and `journey-maps-established.md` files remain functional until migrated.
- **To adopt**: Move `journey-maps.md` JM-TB-NNN entries to a new `## 15. Designed User Journeys` section in `project/design-intent-to-be.md`. Move `journey-maps-established.md` JM-E-NNN entries to a new `## 5. Discovered User Journeys` section in `project/ux-research-established.md`. Rename `project/user-research-*.md` files to `project/ux-research-*.md`. Update `project/conventions.md` variable names and registry.
- **Upgrade path**: run `/upgrade` to pull updated templates; migrate project-specific files manually or via `/design` (update mode).

## [2.3.0] -- 2026-04-02 11:48 UTC

### Added

- `_references/template/journey-maps-established.md` -- third tier of journey maps: research-grounded, human-only, append-only, never agent-modified. Contains `JM-E-NNN` stable IDs, required research citation (method, date, n-count), optional persona/PS-ID fields, Source column in steps table, and Processing Log.
- `JOURNEY_MAPS_ESTABLISHED` variable in `_references/template/conventions.md` (optional; declared always, absent by default).
- To-Be / As-Is Registry section in `_references/template/conventions.md` -- canonical table of all registered to-be/established/as-is file triples; single source of truth for `/design`, `/explain spec-drift`, and post-skill.
- Lifecycle Markers section in `_references/general/shared-definitions.md` -- defines `STATUS: IMPLEMENTED` (prose and table row variants) and `ESTABLISHED:` stamp convention. Agents may read and apply IMPLEMENTED markers; must never alter existing markers.
- post-skill step 2e: DONE marker proposal -- after as-is update, scans registered to-be files for implemented items and proposes `STATUS: IMPLEMENTED` markers via AskUserQuestion.
- `spec-drift --promote` mode in `/explain` -- scans for IMPLEMENTED items across all registered to-be files and promotes confirmed items to their established counterparts with an optional version stamp.

### Changed

- `_references/template/journey-maps.md` (to-be): added `JM-TB-NNN` stable ID field; updated header to link to established file and state one-directional flow rule.
- `_references/template/journey-maps-as-is.md`: added `JM-TB-NNN` anchors in delta tables; added conditional "Delta from Established" section.
- `/explain spec-drift`: now reads the To-Be / As-Is Registry to iterate all registered file pairs instead of hardcoding the design-intent pair. Drift report now includes a "Pending Promotions" section. Step B menu includes "Promote IMPLEMENTED items" option.
- `/design` Mode 1 step 7: now generates `journey-maps-established.md` and `user-research-established.md` during project setup; includes registry-awareness note.
- post-skill step 2e (former `e`): renamed to `f` (include in commit scope); note extended to cover `journey-maps-established.md` as human-maintained.
- CHANGELOG format: entries now include time component (`YYYY-MM-DD HH:MM UTC`) in addition to date.

### Migration (for existing projects)

- **No breaking changes.** All additions are additive. Existing skills degrade gracefully when `journey-maps-established.md` is absent.
- **To adopt the registry:** add the "To-Be / As-Is Registry" section to your `project/conventions.md` by running `/upgrade` or manually copying the section from `_references/template/conventions.md`.
- **To adopt journey-maps-established.md:** run `/design` (update mode) to generate the new template, or manually copy from `_references/template/journey-maps-established.md`.

## [2.2.0] -- 2026-04-02 00:00 UTC

### Added
- Questionnaire Section M (`metacomm-message`): optional early metacommunication message that seeds suggested defaults across subsequent questions (0.1, 0.2, 2.1, 2.10, 2.11)
- Slug reference table in questionnaire header: stable named identifiers for all sections matching template filenames (e.g., `conceptual-design`, `ux-design-standards`, `quick-start`)
- Slug annotations on all section headers in the questionnaire

### Changed
- Questionnaire sections physically reordered into T1 / T2 / T3 tier blocks. Section M appears first (before Section 0) so metacomm defaults are extracted before quick-start questions. Numbers preserved as stable backward-compatible aliases.
- `/design` skill (Mode 1) updated to extract defaults from Section M metacomm message and to reference sections by slug
- Questionnaire version bumped from 3 to 4
- Onboarding guide updated to reference sections by slug; questionnaire description updated to mention 12 sections

### Migration (for existing projects)
- **Questionnaire**: consumed once during `/design`; no migration needed for filled-out projects.
- **Framework files** (`_references/template/`, `.claude/skills/`): auto-updated by `/upgrade`. Running `/upgrade` will pull the slug-aware questionnaire and design skill.
- **Existing plans/advisories referencing "Section N"**: numbers remain valid aliases -- no action required. Prefer slugs in new documents.

## [2.1.0] -- 2026-04-01 00:00 UTC

### Added
- `project/design-intent-to-be.md` — merged single document combining conceptual design (Part I) and metacommunication intent (Part II), replacing the previous two-file model
- `project/design-intent-established.md` — archive of processed design decisions with preserved rationale (human-maintained, never agent-altered)
- `project/user-research-new.md` — user research file for new/planned product contexts (separate from established-product research)
- `project/journey-maps.md` — journey map template for tracking user journeys through planned features
- `project/journey-maps-as-is.md` — agent-maintained implementation-state companion to journey-maps.md (created by post-skill on first plan execution)
- Solution scenarios and user stories as alternative solution representations in design-intent-to-be.md
- Post-skill step 2d: automatic journey-maps-as-is.md maintenance after plan execution

### Changed
- `/design` now generates `design-intent-to-be.md` + `design-intent-established.md` instead of `conceptual-design-to-be.md` + `metacomm-to-be.md`
- User research model corrected: files are now `established` vs. `new` rather than `as-is` vs. `to-be`
- `/advise`, `/explain`, `/implement`, `/plan` reference the new `design-intent-to-be.md` file
- `/seed --demo` demo files updated to reflect new design-intent model

### Removed
- `project/conceptual-design-to-be.md` (merged into `design-intent-to-be.md`)
- `project/metacomm-to-be.md` (merged into `design-intent-to-be.md`)
- Legacy `template/conceptual-design.md` template

## [2.0.1] -- 2026-03-30 00:00 UTC

- Renamed `_references/` internal structure: files now organized into `general/`, `template/`, and `project/` subdirectories instead of flat files with `general-`, `template-`, `project-` prefixes. Metadata references, scripts, and documentation updated throughout.
- `/implement` quality gate now runs all checks by default (validate, review, test-runner). Previous `--skip-preflight` flag replaced with `--skip-checks`. Roadmap-conclusion gate runs full checks when the last roadmap item completes.
- `/communication` now outputs stakeholder-facing content with dual format: Markdown plus styled HTML, both generated by default (`--format md|html|both`). Next-step recommendations are refined into the content rather than listed. Multi-file subfolder support for audiences with distinct topics. Date-folder index auto-generated when multiple artifacts share the same date.
- `/upgrade` now fetches the foundational SEJA framework directly from GitHub instead of requiring a local copy.
- Skill scanning defaults to codebase root; QA logs centralized in `_output/qa-logs/`.
- Workspace seed resets plan numbering to ensure IDs start at 000001.
- Added Step 14 (Review & next steps) to `/design`: after summary, offers spec review, roadmap generation, or exit. Roadmap auto-derives themes and work items from design intent and metacommunication.
- Updated skill graph: `/design` now suggests `/plan --roadmap` instead of `/help`.
- Removed `/seed --package` (zip packaging). The public repo is now the foundational framework itself. Use GitHub's "Download ZIP" for offline distribution.
- Restructured seja-public/ as a complete foundational framework with docs/ folder.

## [2.0.0] -- 2026-03-29 00:00 UTC

### Added
- Framework upgrade system (`upgrade_framework.py`) for safe project upgrades
- Convention schema diff utility in `project_config.py`
- Semver versioning in VERSION file
- This CHANGELOG
- Upgrade mode in `/quickstart --upgrade`
- Version-bump protocol documentation

### Changed
- References relocated from `.claude/skills/references/` to `_references/` (migration handled by upgrade script)
- VERSION format changed from plain `version: 1` to semver `version: 2.0.0`

### Removed
- Legacy briefs log format parser (`_LEGACY_RE` in `generate_briefs_index.py`)
- Legacy `lightweight` boolean field validation in `check_skill_system.py`
- Legacy plan format fallback in `implement/SKILL.md`

## [1.0.0] -- 2026-03-27 00:00 UTC (retroactive)

### Added
- Initial SEJA-Claude framework: 19 skills, 24 scripts, 5 agents, 6 rules
- References system in `.claude/skills/references/` (later moved to `_references/`)
- Template and general reference files
- Project bootstrapping via `/quickstart`
- Packaging via `/quickstart --package`
