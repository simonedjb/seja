# GENERAL - CONSTRAINTS

- All files must be UTF-8 encoded.
- Do not invent data.
- Do not generate agent-dependent or nondeterministic behavior unless explicitly requested.
- Do not use ANSI code in generated code or reports.
- Do not reduce existing test coverage. When modifying code that has tests, update or extend the tests to maintain coverage.
- Do not implement placeholder or simplistic implementations.
- If you come across an opportunity to add a desirable but unessential feature based on similar products or best practices, describe the proposal, provide pros and cons, and ask the user. When working autonomously, as in `auto` or `bypassPermissions` mode, do not add unessential features.
  
## Context Management

- **Session length awareness**: After 8+ skill invocations in a single session, context quality may degrade. Pre-skill's `compaction-check` stage warns when this threshold is reached.
- **When to start a fresh session**: After completing a major workflow (e.g., advisory -> plan -> implement -> check), or when the agent's responses become less accurate or miss previously established context.
- **What to preserve across sessions**: Before starting a fresh session, persist key decisions, plan IDs, open issues, and any unresolved questions to the session scratchpad (`${TMP_DIR}/session-notes.md`). Use timestamped entries with category tags (DECISION, FINDING, TODO, CONTEXT).
- **Pinned anchors**: Certain reference files must never be summarized or dropped during context compaction. See the Pinned Anchors section below for the full list.

### Session Scratchpad Format

The session scratchpad (`${SESSION_NOTES_FILE}`) uses timestamped entries with category tags:

```
## YYYY-MM-DD HH:MM UTC

- DECISION: <what was decided and why>
- FINDING: <what was discovered, with file paths or plan IDs>
- TODO: <what remains to be done, with enough context to resume>
- CONTEXT: <background information needed to continue this work>
```

**When to write**: After making key architectural decisions, discovering important findings, completing major milestones, or before a session is likely to end.

**What to include**: Plan IDs, file paths, unresolved questions, key metrics, dependency relationships between tasks.

**What NOT to include**: Full file contents, verbose logs, conversation history, information already captured in plan files or briefs.

### Pinned Anchors (Non-Compactable Context)

The following reference files must survive any context compaction event. They must be re-injected after summarization or truncation and must never be abbreviated:

1. `project/constitution.md` -- immutable project principles; dropping this allows agents to bypass governance rules
2. `general/permissions.md` -- agent permission boundaries; dropping this removes authorization constraints
3. `general/constraints.md` -- behavioral constraints (this file); dropping this removes quality and safety guardrails
4. Active skill's SKILL.md instructions -- the currently executing skill's full body; dropping this causes the agent to lose its task context
5. Active plan context -- if executing a plan, the plan file content; dropping this causes the agent to lose implementation context
6. Session scratchpad (`${SESSION_NOTES_FILE}`) -- persisted decisions and findings; dropping this negates the purpose of structured note-taking

If a compaction mechanism is implemented in the future, it must treat these files as immutable anchors that are preserved verbatim through every compaction cycle.

## If stack includes TypeScript (frontend)

- New frontend files must be TypeScript (`.ts`/`.tsx`). Existing `.js`/`.jsx` files should be converted when substantively modified.
