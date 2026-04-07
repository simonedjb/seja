# Context Strategy

SEJA actively manages context window usage to balance thoroughness against token efficiency. This page documents the mechanisms that control how much information is loaded, when it is loaded, and how session health is monitored.

For a conceptual introduction to the context system, see [Skills, Agents, and the Pipeline](../concepts/skills-agents-pipeline.md).

---

## Context Budget Tiers

Every skill declares a `metadata.context_budget` in its YAML frontmatter. The pre-skill pipeline's `budget-eval` stage reads this value and adjusts reference loading accordingly. Three tiers are available.

### light

Skips all briefs loading and reference file loading. The only pre-skill stages that run are `brief-log` (to record the invocation) and `orphan-check` (to detect crashed sessions). The `ref-load` and `constitution` stages are skipped entirely.

Use `light` for skills that need minimal context -- for example, `/help` and `/qa-log`, which operate on their own inputs rather than project state.

### standard (default)

Loads the **briefs index** (`briefs-index.md`) instead of the full briefs file. The index contains one-line summaries of each invocation, providing session awareness at low token cost. If the index does not exist, it is generated on the fly by running `generate_briefs_index.py`.

After loading the index, proceeds to `ref-load`, which injects the mandatory references (conventions, permissions, constraints) plus any skill-specific references declared in the skill's frontmatter.

Most skills use `standard`. It provides enough context for informed decision-making without loading the full history.

### heavy

Loads the **full briefs file** with **recency windowing**: reads only the first 50 entries (newest first), then appends a summary line for older entries ("N earlier entries from DATE to DATE, not loaded"). Also loads the **plan index** (`_output/plans/INDEX.md`) to provide awareness of all existing plans.

After loading briefs and the plan index, proceeds through all remaining stages including `compaction-check`.

Use `heavy` for skills that need deep project awareness -- for example, `/plan` and `/implement`, which must understand prior work to avoid duplication and maintain consistency.

---

## Reference Loading Modes

Skills declare their reference dependencies in YAML frontmatter. Two loading modes are available, determined by whether the skill declares `metadata.eager_references`.

### Eager-Only (Legacy)

When a skill declares `metadata.references` but no `metadata.eager_references`, all listed references are loaded upfront during the `ref-load` stage. This is the simpler, original behavior.

```yaml
metadata:
  references:
    - general/coding-standards.md
    - project/backend-standards.md
```

Both files above would be read and injected into context immediately. An empty list (`references: []`) is valid -- it means the skill intentionally loads no additional references beyond the mandatory set.

### Demand-Pull (Two-Tier)

When a skill declares `metadata.eager_references`, the loading splits into two tiers:

1. **Eager tier** -- files listed in `eager_references` are loaded upfront alongside the mandatory refs (conventions, permissions, constraints). These are references the skill always needs.
2. **Lazy tier** -- the remaining entries in `references` that are not in `eager_references` become available on demand. Pre-skill emits an "Available references" block listing each lazy ref with a trigger hint derived from the filename:

```
--- Available references (load when needed) ---
1. project/security-checklists.md -- load before reviewing security concerns
2. project/frontend-standards.md -- load before writing frontend code
...
To load: read and inject the file from _references/<path>.
---
```

The skill body can then request specific lazy refs when needed, paying the context cost only for references actually used during that invocation.

An empty `eager_references: []` is valid -- it means all skill-specific references are lazy and only the mandatory refs are loaded upfront.

---

## Two-Stage Perspective Loading

The review perspective system uses its own loading optimization to avoid injecting all 16 perspective files (which would consume significant context). The protocol works in two stages:

### Stage 1: Load the Index

Read `general/review-perspectives-index.md`, a compact table under 600 tokens that lists all 16 perspectives with their tags, names, and scope descriptions.

### Stage 2: Select and Load

Based on the change type, plan prefix, or review scope, select 4-6 relevant perspectives from the index. Default shortlists are defined per plan prefix (e.g., `FEATURE-B` defaults to SEC, DB, API, ARCH, TEST, PERF). Up to 2 additional perspectives may be added if the content warrants it.

Only the selected perspective files (`general/review-perspectives/<tag>.md`) are loaded. Each file contains two tiers:

- **Essential** -- 3-7 P0 (critical/blocking) questions that must always be evaluated.
- **Deep-dive** -- 8-12 P1-P4 questions for thorough reviews, loaded for heavy context budget or explicit deep-dive requests.

### Conflict Resolution

When two perspectives recommend conflicting approaches:

- **SEC wins by default** -- security concerns override performance or convenience unless the user explicitly accepts the risk.
- **A11Y is non-negotiable** -- accessibility requirements are not traded off.
- For other conflicts, the trade-off is documented and the user is asked for guidance.

---

## Session Management

### Compaction Warning

The pre-skill `compaction-check` stage monitors session health by counting STARTED entries in the briefs file whose timestamps fall within the last 2 hours. If the count exceeds 8, it emits an advisory warning:

> "Warning: Context may be getting heavy after N skill invocations in this session. Consider starting a fresh conversation for best results, or use the session scratchpad to persist key decisions before starting a new session."

This is advisory-only -- it does not block or auto-compact. The threshold of 8 invocations is based on typical context window degradation patterns.

### Session Scratchpad

The session scratchpad (`_output/tmp/session-notes.md`) provides structured persistence for decisions that need to survive across sessions. Entries use timestamped category tags:

- **DECISION** -- what was decided and why
- **FINDING** -- what was discovered, with file paths or plan IDs
- **TODO** -- what remains to be done, with enough context to resume
- **CONTEXT** -- background information needed to continue the work

The scratchpad is meant for key decisions, plan IDs, and unresolved questions -- not for full file contents or conversation history.

### Pinned Anchors

Six reference files are designated as **pinned anchors** -- they must survive any context compaction event and be re-injected after summarization or truncation. These files are never abbreviated:

1. `project/constitution.md` -- immutable project principles. Dropping this allows agents to bypass governance rules.
2. `general/permissions.md` -- agent permission boundaries. Dropping this removes authorization constraints.
3. `general/constraints.md` -- behavioral constraints. Dropping this removes quality and safety guardrails.
4. The active skill's `SKILL.md` instructions -- the currently executing skill's full body. Dropping this causes the agent to lose its task context.
5. The active plan context -- if executing a plan, the plan file content. Dropping this causes the agent to lose implementation context.
6. The session scratchpad -- persisted decisions and findings. Dropping this negates the purpose of structured note-taking.

These anchors define the minimum viable context that must be preserved at all times. Any future compaction mechanism must treat them as immutable through every compaction cycle.
