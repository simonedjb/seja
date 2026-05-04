# SEJA Claude Harness

This repository contains the SEJA agent harness in `.claude/`.

Before editing files that match a rule scope, read the corresponding file in `.claude/rules/`.
When a task benefits from delegation, use the prompt files in `.claude/agents/` as the source of truth for subagent behavior.
For detailed component inventory, see `.claude/rules/harness-structure.md`.

## Conversation trace

After responding to any user message that is NOT within an active skill invocation (no `/skill` running), silently log the exchange to the conversation trace:

1. Run `python .claude/skills/scripts/conversation_trace.py last-evt-id --session-id $CLAUDE_SESSION_ID` to get the preceding evt-id (use the env var value, or `"null"` if unavailable).
2. Append the user's utterance: `python .claude/skills/scripts/conversation_trace.py append --session-id $CLAUDE_SESSION_ID --emitter user --message "<user message>" --type <question|answer|instruction> --preceding-evt-id <last_evt_id>`. Infer `--type` from context (question when the user asks; answer when responding to an agent-initiated prompt; instruction otherwise).
   - If exit code 2 (masking applied): show the masked message to the user and ask for confirmation. On yes, re-run with `--confirm`. On no, do not log either entry.
   - If exit code 0: capture the printed `evt_id` as `<user_evt_id>`.
3. Append the agent's response: `python .claude/skills/scripts/conversation_trace.py append --session-id $CLAUDE_SESSION_ID --emitter claude --message "<1-2 sentence summary of your response>" --type <answer|question|instruction> --preceding-evt-id <user_evt_id>`. Add `--topic-tags` with 1-3 short tags when the topic is clearly identifiable.
   - If exit code 2 (masking applied to agent summary): re-run with `--confirm` to accept the masked version silently.
   - If exit code 0: agent entry appended silently.
4. Do not mention the trace to the user.

`session_id` comes from the `CLAUDE_SESSION_ID` environment variable (`"null"` if unavailable).

## Key workflows

- **Lifecycle at a glance**: the canonical path is `/research` (or `/explain`) > `/design` | `/plan` > `/implement` > `/check` > `/document` | `/communicate` > `/reflect` -- validate before you communicate. On the first iteration, `/seja-setup <target>` hands off to `/design` to configure the project; from iteration 2 onward, start with `/research` (or `/explain`) to investigate what you are about to change, then branch into `/design` when intent needs to change or into `/plan` when it does not. `/explain spec-drift` is the alignment workflow for reconciling design specs with the as-coded state.
- **New project**: run `/seja-setup <target>` to copy the foundational SEJA harness into a new project, or `git clone https://github.com/simonedjb/seja my-project` directly and run `/seja-setup --here` to finalise setup in place. Then run `/design` to configure project-specific files. After setup, review the generated specs and optionally generate a development roadmap.
- **Upgrade**: run `/seja-setup --upgrade` to upgrade a workspace or codebase's harness files to the latest version while preserving project data. (No-arg `/seja-setup` in a finalised project also offers "Upgrade to latest".)
- **Workspace setup**: run `/seja-setup <target> --workspace` to create a project workspace from the foundational SEJA harness for working alongside an existing codebase. The workspace is its own git repo with version-controlled design history.
- **Communication**: run `/communicate <audience>` to generate tailored stakeholder material.
- **Onboarding**: run `/onboard <role> <level>` to generate a tailored onboarding plan for a new team member.
- **Skill help**: run `/help` for an overview, or `/help <skill>` for details. Run `/help --browse` to browse interactively.
- **Quality checks**: run `/check <mode>` for validation, code review, smoke tests, preflight, or harness health.
- **Documentation**: run `/document` after implementation to generate or update user and developer documentation based on plan Docs: fields or auto-detected changes.
- **Spec drift**: run `/explain spec-drift` to compare and align design specs.
- **Release (for maintainers)**: see [`docs/reference/release-process.md`](docs/reference/release-process.md) for the A2 release discipline and sync runbook summary.
