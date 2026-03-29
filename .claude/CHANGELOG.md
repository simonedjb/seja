# SEJA-Claude Changelog

All notable changes to the SEJA-Claude framework are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## 2026-03-30

- Removed `/quickstart --package` (zip packaging). The public repo is now the foundational framework itself. Use GitHub's "Download ZIP" for offline distribution.
- Restructured seja-public/ as a complete foundational framework with docs/ folder.

## [2.0.0] — 2026-03-29

### Added
- Framework upgrade system (`upgrade_framework.py`) for safe project upgrades
- Convention schema diff utility in `project_config.py`
- Semver versioning in VERSION file
- This CHANGELOG
- Upgrade mode in `/quickstart --upgrade`
- Version-bump protocol documentation

### Changed
- References relocated from `.claude/skills/references/` to `.agent-resources/` (migration handled by upgrade script)
- VERSION format changed from plain `version: 1` to semver `version: 2.0.0`

### Removed
- Legacy briefs log format parser (`_LEGACY_RE` in `generate_briefs_index.py`)
- Legacy `lightweight` boolean field validation in `check_skill_system.py`
- Legacy plan format fallback in `execute-plan/SKILL.md`

## [1.0.0] — 2026-03-27 (retroactive)

### Added
- Initial SEJA-Claude framework: 19 skills, 24 scripts, 5 agents, 6 rules
- References system in `.claude/skills/references/` (later moved to `.agent-resources/`)
- Template and general reference files
- Project bootstrapping via `/quickstart`
- Packaging via `/quickstart --package`
