# Context Budget and References

## The challenge

Large language models have finite context windows -- a hard limit on how much text they can process at once. A mature SEJA project might have dozens of reference files: conventions, standards, design intent documents, review perspectives, threat models, and more. Loading all of them into every skill invocation would quickly exhaust the available context, leaving little room for the actual work.

SEJA solves this with a **context budget system** that controls how much reference material is loaded based on what each skill actually needs.

## Three context budget tiers

Every skill declares a context budget tier in its YAML frontmatter. The tier determines how much background material the pre-skill pipeline loads before the skill begins its work.

### Light

The lightest tier. Skips all reference file loading and briefs loading. The pre-skill pipeline only logs the invocation (brief-log stage) and checks for orphaned sessions.

This tier is used by utility skills that do not need project context -- for example, `/help` only needs to display information about other skills, not load the full project design.

### Standard (default)

The balanced tier, used by most skills. Loads:

- The **briefs index** -- a compact summary of recent skill invocations, rather than the full briefs log. If the index does not exist, the pipeline generates it automatically.
- **Mandatory references** -- the project's conventions, permissions, and constraints files.
- **Skill-specific references** -- additional files declared in the skill's frontmatter (see eager vs lazy loading below).
- The **project constitution** -- immutable design principles, if one exists.

### Heavy

The most thorough tier, used by skills that need extensive context -- like `/plan` in roadmap mode or `/implement` in auto mode. Loads everything in the standard tier, plus:

- The **full briefs log** with recency windowing (the 50 most recent entries, with a summary of older ones).
- The **plan index** -- a directory of all plans generated for the project.
- All skill-specific references (no lazy loading -- everything is loaded upfront).

## Eager vs lazy reference loading

Within the standard tier, skills can fine-tune which references are loaded immediately and which are available on demand.

**Eager references** are loaded upfront during the pre-skill pipeline. These are files the skill will definitely need -- for example, `/plan` eagerly loads the design-intent-to-be document because every planning session needs to consider the designer's intent.

**Lazy references** are listed in the skill's metadata but not loaded until the skill explicitly requests them. The pre-skill pipeline emits an "Available references" block listing each lazy reference with a short description of when it is useful (for example, "load before reviewing security concerns"). The skill body can then request specific files as needed during execution.

This two-tier approach is declared in the skill's YAML frontmatter:

- `metadata.eager_references` lists files to load immediately.
- `metadata.references` lists all available files (both eager and lazy). Files in `references` that are not in `eager_references` become lazy.

If a skill only has a `references` list (no `eager_references`), all references are loaded upfront -- this is the legacy behavior for older skills.

## Two-stage perspective loading

The 16 review perspectives (see [Review Perspectives and Communicability](review-perspectives-and-communicability.md)) present a specific context budget challenge. Each perspective file contains detailed questions across two tiers (Essential and Deep-dive). Loading all 16 files at once would consume significant context for little benefit -- most reviews only need 4 to 6 perspectives.

SEJA handles this with a **two-stage select-then-load** protocol:

1. **Load the index.** The compact perspective index is a summary table -- under 600 tokens -- listing all 16 perspectives with their tags, names, and scope descriptions.
2. **Select relevant perspectives.** Based on the type of change being reviewed, the framework selects 4 to 6 perspectives. Default shortlists are provided for each plan prefix (for example, a frontend feature defaults to UX, A11Y, VIS, RESP, I18N, TEST, MICRO).
3. **Load only selected files.** Only the chosen perspective files are read. The rest are skipped entirely.

This protocol replaces the earlier approach of loading all perspective files and is used by skills like `/plan`, `/check review`, and `/advise`.

## Session length management

Even with careful budget management, long sessions accumulate context. SEJA includes two mechanisms to help:

**Compaction check.** The pre-skill pipeline counts how many skill invocations have occurred in the last 2 hours. If the count exceeds 8, it warns:

> "Context may be getting heavy after N skill invocations in this session. Consider starting a fresh conversation for best results."

This is advisory only -- it does not block execution. But it signals that accuracy and quality may degrade as the context fills up.

**Session scratchpad.** For decisions and context that need to persist across sessions, SEJA provides a session scratchpad file. Before starting a fresh conversation, you can write key decisions and findings to this file, then pick them up in the new session. This avoids the common problem of losing important context when you follow the compaction warning and start over.

## Why this matters

Context budget management is not just a technical optimization. It directly affects the quality of SEJA's output. When too much irrelevant material is loaded, the model may lose focus on what matters. When too little is loaded, the model lacks the context needed to make good decisions.

The budget system ensures that each skill gets the context it needs -- no more, no less. Light skills stay fast. Standard skills get enough context for informed work. Heavy skills get the full picture when thorough analysis justifies the cost.

For more on how the pre-skill pipeline loads context, see [Skills, Agents, and the Execution Pipeline](skills-agents-pipeline.md). For the perspectives that benefit from two-stage loading, see [Review Perspectives and Communicability](review-perspectives-and-communicability.md).
