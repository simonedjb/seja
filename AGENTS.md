# SEJA Codex Framework

This repository contains two parallel agent frameworks:

- `.claude/`: the original Claude-oriented source framework and upstream source of truth for shared framework behavior.
- `.codex/`: the Codex-oriented equivalent generated from that source.

When working on Codex resources, prefer `.codex/` and keep the same conceptual structure:

- Shared agent-agnostic references live in `_references/` (organized into `general/`, `template/`, and `project/` subdirectories).
- Skills live in `.codex/skills/<name>/SKILL.md`.
- Helper scripts live in `.codex/skills/scripts/`.
- Reusable subagent prompts live in `.codex/agents/`.
- Path-scoped coding guidance lives in `.codex/rules/`.

When the change is Codex-specific documentation or metadata, edit `.codex/` directly.
When the change is shared framework behavior, update `.claude/` first to keep the two toolkits in sync.

Before editing files that match a rule scope, read the corresponding file in `.codex/rules/`.
When a task benefits from delegation, use the prompt files in `.codex/agents/` as the source of truth for subagent behavior.
For detailed component inventory, see `.codex/rules/framework-structure.md`.
