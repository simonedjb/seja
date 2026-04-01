# FRAMEWORK -- BATCH EXECUTION PATTERN

> Canonical reference for skills that parallelize work across multiple subagents.
> Used by: `/communication` (batch mode via `--all`), `/onboarding` (batch mode via `--batch`)
> Any skill that needs parallel subagent orchestration should follow this pattern.

## Pattern Overview

Skills that generate multiple independent outputs (e.g., one per audience segment, one per role/level combination) use this 6-phase pattern to avoid duplicating orchestration boilerplate.

## Phases

### Phase 1: Run pre-skill once

Run `/pre-skill` a single time for the entire batch. Do not run it per work item.

### Phase 2: Reserve IDs upfront

Before launching any parallel work, reserve all needed output IDs by running `python .claude/skills/scripts/reserve_id.py --type <artifact-type> --title '<slug>'` once per work item. This prevents ID conflicts when multiple subagents write files concurrently. Each call returns a globally unique 6-digit zero-padded ID.

### Phase 3: Prepare output folder and load shared context

Compute the date-versioned output folder (`<output-dir>/<YYYY-MM-DD>`, UTC) and create it if it does not exist. Then read all shared references and project context (conceptual design, conventions, style config, etc.) into a single context block. Every parallel subagent receives this same context, avoiding redundant file reads.

### Phase 4: Launch N agents in parallel

Spawn one Agent tool call per work item, all in a single message so they execute in parallel. Each agent receives:

- The pre-loaded shared project context from Phase 3
- Its specific work item parameters (audience segment, role, level, name, focus area, etc.)
- The reserved ID and output file path from Phase 2
- The full single-mode skill instructions for the generation and output steps

### Phase 5: Collect, verify, and handle failures

After all agents complete:

- Verify each expected output file exists
- Report completion summary (N succeeded, M failed)
- List any missing or incomplete outputs

**Failure isolation**: each agent runs independently. One agent's failure does not abort the batch. Completed outputs from successful agents are preserved. The user is notified of partial results with the failing items identified, and can re-run the skill for just the failed items individually.

### Phase 6: Run post-skill once

Run `/post-skill` a single time for the entire batch. The hook stages all generated files in a single git commit. Do not run post-skill per work item.

## Key Principle: Bookend Lifecycle Hooks

The pre-skill and post-skill lifecycle hooks wrap the entire batch, not individual items:

```
pre-skill (once)
  -> reserve IDs (N times)
  -> load shared context (once)
  -> launch N agents (parallel)
  -> collect results
post-skill (once)
```

This ensures a single brief entry and a single atomic commit for the whole batch.

## When to Use

Use this pattern when a skill:

- Generates 2+ independent outputs from a single invocation
- Each output can be produced by an agent with no dependency on other outputs
- All outputs should be committed atomically

## When NOT to Use

Do not use this pattern when:

- Outputs depend on each other (use sequential execution instead)
- There is only one output (standard single-agent execution is simpler)
- The work requires interactive user input between items (resolve all interactive prompts before launching the batch)

## Interaction Before Launch

If any work item spec is incomplete (e.g., missing required arguments), do NOT launch agents yet. Present all incomplete specs to the user for resolution first, then launch all agents at once. Interactive prompts must be fully resolved before entering the parallel phase.
