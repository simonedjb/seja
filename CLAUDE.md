# SEJA Claude Framework

This repository contains two parallel agent frameworks: `.claude/` (source) and `.codex/` (generated mirror). Prefer `.claude/` when working on framework resources.

Before editing files that match a rule scope, read the corresponding file in `.claude/rules/`.
When a task benefits from delegation, use the prompt files in `.claude/agents/` as the source of truth for subagent behavior.
For detailed component inventory, see `.claude/rules/framework-structure.md`.

## Key workflows

- **New project**: extract the foundational SEJA framework (clone or download the public repo), then run `/quickstart .` to generate project-specific files.
- **Upgrade**: run `/quickstart --upgrade` to upgrade a workspace or codebase's framework files to the latest version while preserving project data.
- **Workspace setup**: run `/quickstart --workspace` to create a project workspace from the foundational SEJA framework for working alongside an existing codebase. The workspace is its own git repo with version-controlled design history.
- **Communication**: run `/communication <audience>` to generate tailored stakeholder material.
- **Onboarding**: run `/onboarding <role> <level>` to generate a tailored onboarding plan for a new team member.
- **Skill help**: run `/help` for an overview, or `/help <skill>` for details. Run `/help --browse` to browse interactively.
- **Quality checks**: run `/check <mode>` for validation, code review, smoke tests, preflight, or framework health.
- **Spec drift**: run `/explain spec-drift` to compare and align design specs.
