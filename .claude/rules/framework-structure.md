# Framework Structure

Detailed inventory of the SEJA Claude framework components. Auto-loaded when working on `.claude/` files.

## Skills

14 skills in `.claude/skills/<name>/SKILL.md` -- 12 user-facing + 2 internal lifecycle hooks (pre-skill, post-skill). Each user-facing skill includes a `## Quick Guide` section with designer-friendly description, example, and usage scenario.

## Agent-Agnostic References

Shared across `.claude` and `.codex` frameworks, located in `.agent-resources/`:

- General references (12 + 16 per-perspective + 8 per-onboarding + 5 per-communication): `general-*.md` files, `general-review-perspectives/` with Essential/Deep-dive tiers (P0-P4) and an auto-generated Essential summary, `general-onboarding/` with role families (BLD/SHP/GRD) and expertise levels (L1-L5), and `general-communication/` with audience segments (EVL/CLT/USR/ACD).
- Template references (32): `template-*.md` and `template-*.json` -- used by `/quickstart` to generate project-specific files.
- Project-specific references: `project-*.md` -- generated per-project by `/quickstart`. Includes conceptual-design and metacomm file pairs (`project-conceptual-design-as-is.md`, `project-conceptual-design-to-be.md`, `project-metacomm-as-is.md`, `project-metacomm-to-be.md`).

## Helper Scripts

28 scripts in `.claude/skills/scripts/` -- validation checks, index generators, conversion utilities, and the central `project_config.py` module that parses `project-conventions.md` to supply all scripts with project-specific paths and settings.

## Subagent Prompts

5 reusable subagent prompts in `.claude/agents/`.

## Path-Scoped Rules

7 rule files in `.claude/rules/` (including this one) -- auto-loaded when Claude works on files matching the rule's scope.
