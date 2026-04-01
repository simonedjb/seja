# Progress File Pattern

Cross-iteration learnings file for subagent communication during multi-step plan execution.

## Purpose

The progress file is an append-only shared artifact that enables subagents running in separate context windows to communicate findings, patterns, and blockers across iterations. Each subagent reads the file at start and appends its discoveries at end, building a cumulative knowledge base that prevents repeated mistakes and surfaces reusable patterns.

## When to Create

Create a progress file at the start of any workflow that spawns multiple subagents sequentially, where later subagents benefit from earlier subagents' discoveries. The canonical use case is `/implement` in auto mode, where each plan step runs in a fresh context.

## File Location

`${PLANS_DIR}/plan-<id>-progress.md` -- colocated with the plan file it supports.

## File Structure

```markdown
# Progress -- Plan <id>

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->

## Iteration Log
```

### Codebase Patterns section

A curated collection of reusable patterns discovered during execution. Subagents add entries here when they discover something that future steps (or future plans) will benefit from -- naming conventions, file layout patterns, API idioms, test fixtures, etc. This section is meant to be read top-down as a reference.

### Iteration Log section

Chronological append-only log. Each subagent appends an entry after completing its step, including:

- Which step was executed and its outcome (SUCCESS / PARTIAL / FAILED)
- What was discovered or changed
- Gotchas encountered
- Blockers (for PARTIAL / FAILED outcomes) described clearly enough for the next subagent or the user to address

## How Subagents Use It

1. **Read at start**: The orchestrator includes the progress file content in the subagent prompt, giving it full visibility into prior iterations.
2. **Append at end**: The subagent appends its learnings to the Iteration Log. If a reusable pattern was discovered, it also adds an entry to the Codebase Patterns section.
3. **Report blockers**: If the subagent cannot complete its step, it describes the blocker in the progress file so the orchestrator (or the next subagent) can address it.

## When to Reference This Pattern

- Any skill or workflow that spawns multiple subagents needing shared context
- When designing new auto-mode execution loops
- When extending the `/implement` skill's iteration protocol
