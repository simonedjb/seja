# Design Rationale

Key architectural decisions in SEJA, documented with context, trade-offs, and conditions for reconsideration. For the full framework structure, see [Framework File Map](framework-file-map.md).

---

## 1. Monolithic pre/post-skill pipelines

**Decision**: Pre-skill (7 stages) and post-skill (13 steps) are single files rather than decomposed micro-hooks.

**Context**: The skill lifecycle is the most important control flow in the framework. Developers need to read and understand the full pipeline without jumping across dozens of files.

**Rationale**: A single file per pipeline gives a readable, top-to-bottom lifecycle overview. The `skip_stages` mechanism in skill frontmatter handles per-skill overrides without splitting the pipeline into separate files. Decomposing into micro-hooks would add file count and configuration without solving an actual problem.

**Trade-offs**: Harder to test individual stages independently. Stages cannot be versioned or deployed separately. Gained: readability, single-file discoverability, simpler dependency graph.

**Revisit when**: A stage needs independent versioning, or the pipeline grows beyond a size where single-file readability breaks down.

---

## 2. Three context budget tiers

**Decision**: Skills declare one of three tiers -- light, standard, or heavy -- that control how much of the context window is allocated to reference loading.

**Context**: Different skills need different amounts of context. A help lookup needs minimal references; a full design session needs many. Two tiers would force awkward compromises; four or more would add classification overhead without meaningful differentiation.

**Rationale**: Three tiers map to natural usage patterns: light (quick lookups, minimal references), standard (most skills), heavy (design, planning, and review tasks that load many project files). Skills declare their tier upfront in YAML frontmatter, and the pre-skill budget-eval stage enforces the allocation.

**Trade-offs**: Skills must choose a tier at authoring time rather than dynamically scaling. Some skills may sit at the boundary between tiers. Gained: predictable context usage, simple mental model, no runtime negotiation.

**Revisit when**: LLM context windows grow by an order of magnitude (10x), making budget tiers less relevant.

---

## 3. Eager vs demand-pull reference loading

**Decision**: Two reference-loading modes coexist -- eager (load all declared references upfront) and demand-pull (load references on demand during skill execution).

**Context**: The original design loaded all references eagerly. As skills accumulated optional references, eager loading consumed unnecessary context budget. Demand-pull was introduced to let skills load only what they need.

**Rationale**: Backward compatibility required keeping eager mode for existing skills. Demand-pull optimizes context usage for skills with many optional references. Both modes use the same underlying reference resolution logic.

**Trade-offs**: Two code paths to maintain in the pre-skill ref-load stage. Skill authors must understand both modes. Gained: existing skills continue working unchanged; new skills can optimize context usage.

**Revisit when**: All skills migrate to demand-pull, making the eager path dead code.

---

## 4. Checkpoint recovery in post-skill

**Decision**: Post-skill uses idempotent step tracking with a checkpoint file to enable crash recovery.

**Context**: Post-skill is a 13-step pipeline that touches git (commits, branch operations) and updates multiple project files. A crash mid-pipeline would leave partial state -- some files updated, others not, git in an intermediate state.

**Rationale**: Each step records its completion in a checkpoint file. On re-entry after a crash, completed steps are skipped. Steps are designed to be idempotent so re-running a partially completed step produces the same result as running it fresh.

**Trade-offs**: The checkpoint file adds complexity and an additional artifact to manage. Step authors must ensure idempotency. Gained: reliable recovery from crashes without manual intervention or rollback.

**Revisit when**: Post-skill shrinks significantly (fewer than 5 steps), making crash recovery less critical than the overhead of maintaining checkpoints.

---

## 5. Six pinned anchors

**Decision**: Exactly six files are pinned as context anchors that survive compaction and are always available to agents.

**Context**: Agents need persistent access to governance rules, permissions, and task context. Without pinning, compaction could evict critical files, causing agents to violate constraints or lose track of their task.

**Rationale**: The six pinned files contain the constitution, permissions, constraints, conventions, the active plan, and the current brief. These represent the minimum set an agent needs to operate within trust boundaries and maintain task continuity.

**Trade-offs**: Pinning reduces the context budget available for other content. Six anchors consume a fixed portion of the context window regardless of whether all are needed for a given task. Gained: agents never lose access to governance and task state.

**Revisit when**: Compaction is implemented and the anchor set proves too large for the available context budget, or when governance files can be consolidated.

---

## 6. Single global ID namespace

**Decision**: One auto-incrementing counter produces IDs for all artifact types -- plans, advisories, roadmaps, and other numbered artifacts.

**Context**: Multiple ID namespaces (one per artifact type) would require coordination to avoid collisions and would complicate cross-referencing between artifact types.

**Rationale**: A single counter is simple: every new artifact gets the next number, regardless of type. Cross-references are unambiguous because the combination of filename prefix and ID is unique (e.g., `plan-000042` vs `advisory-000042` -- the type is in the prefix, not the ID).

**Trade-offs**: IDs do not encode their type -- you cannot tell from the number alone whether 000042 is a plan or an advisory. The ID space is shared, so heavy use of one artifact type advances the counter for all types. Gained: zero collision risk, trivial implementation, easy cross-referencing.

**Revisit when**: ID space exhaustion becomes a concern, or if the lack of type encoding causes persistent confusion.

---

## 7. Agent single-responsibility

**Decision**: Each agent operates on exactly one type of artifact through one lens. Evaluators review one thing; generators produce one thing.

**Context**: Combining responsibilities in a single agent (e.g., a "super-reviewer" that handles code, plans, and design decisions) would create large, unpredictable prompts with unclear trust boundaries.

**Rationale**: Single-responsibility agents have predictable behavior, testable prompts, and clear trust boundaries. Each agent's prompt is optimized for its specific task. The pattern maps cleanly to the three agent roles: evaluator, generator, executor. (See framework-structure.md -- Governance, Agent Count.)

**Trade-offs**: More agent files to maintain (currently 10). Adding a new review dimension requires a new agent file. Gained: each agent is independently testable, its behavior is predictable, and trust boundaries are explicit.

**Revisit when**: Agent count exceeds 15 and role overlap emerges between agents, suggesting consolidation opportunities.

---

## 8. Generator-critic loops in auto mode

**Decision**: `/implement` auto mode uses a bounded generator-critic loop (max 2 retries) when the code-reviewer finds critical issues. Interactive mode keeps advisory-only review.

**Context**: Auto mode opts out of per-step human oversight. Without automated quality gates, output quality depends entirely on the generator's first attempt. But unbounded retry loops risk runaway token consumption. (advisory-000188)

**Rationale**: Two retries strike a balance -- most fixable issues are resolved within two attempts, while genuinely hard problems are escalated rather than retried indefinitely. Interactive mode does not use the loop because the human is already in the review cycle.

**Trade-offs**: More token consumption per plan step in auto mode (up to 3x if both retries are used). Some issues may not be fixable by retry alone. Gained: measurably better output quality in auto mode without undermining user agency in interactive mode.

**Revisit when**: Retry success rate data shows that retries rarely fix the identified issues, making the extra token cost unjustified.
