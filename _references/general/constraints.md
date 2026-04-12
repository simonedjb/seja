# GENERAL - CONSTRAINTS

- All files must be UTF-8 encoded.
- Do not invent data.
- Do not generate agent-dependent or nondeterministic behavior unless explicitly requested.
- Do not use ANSI code in generated code or reports.
- Do not reduce existing test coverage. When modifying code that has tests, update or extend the tests to maintain coverage.
- Do not implement placeholder or simplistic implementations.
- If you come across an opportunity to add a desirable but unessential feature based on similar products or best practices, describe the proposal, provide pros and cons, and ask the user. When working autonomously, as in `auto` or `bypassPermissions` mode, do not add unessential features.

## Decision-point rationale convention

**Rule.** Every `AskUserQuestion` in SEJA carries explicit rationale for each option. The framework is a proposer; the designer is the decider. No option may be pre-accepted by framing alone.

**Format.** Each option's description contains 1-2 lines: *"Recommended when ..."* (why this option fits) and *"NOT recommended when ..."* (when it would be the wrong choice). An optional `(more: <link>)` footer links to a relevant advisory, plan, or concepts section for substantial rationale. Total description per option: up to 3 lines before the link. Always use "Recommended when" / "NOT recommended when" phrasing — never "Right when" / "Wrong when".

**Recommended-label policy.** The label `(Recommended)` is permitted when and only when the option's description includes the *specific reason* the option is recommended *in this context*. A bare `(Recommended)` without contextual reasoning is a convention violation. When no option has a clear contextual preference, omit the label.

**Rationale for the rationale.** I adopted this convention after advisory-000292 identified that auto-accepting recommendations undermines reflective practice. Reflection-in-action requires the user to pause and consider before clicking; rationale that earns the recommendation is what makes that pause productive. Without this convention, the framework would embody doctrinal delivery rather than reflective collaboration.

**Enforcement.** This convention is currently enforced by author discipline. A `check_docs.py` plugin scanner `decision_point_rationale_compliance` is a candidate follow-up to audit SKILL.md `AskUserQuestion` blocks at CI time.

See advisory-000292 (A3) and plan-000294 for the origin and rationale of this convention.

## Artifact-link convention for decision points

**Rule.** When an `AskUserQuestion` references one or more already-generated artifact files, output a compact **Files for review** block immediately before the question. This lets the user open and review the artifact(s) before answering.

**Format.**

```
**Files for review:**
- [plan-000042-add-tagging.md](_output/plans/plan-000042-add-tagging.md)
- [advisory-000038-auth-middleware.md](_output/advisory-logs/advisory-000038-auth-middleware.md)
```

Each entry is a clickable relative-path link (relative to the project root). List every artifact the user might want to review before making their choice -- the plan they are about to implement, the advisory they are about to act on, the proposal they are about to execute, etc.

**When it applies.** Any `AskUserQuestion` where one or more options reference a specific, already-generated artifact file (plan, advisory, roadmap, proposal, promote-proposal, drift report, pending-action source, etc.). Examples:

- `/plan` step 7 -- the just-generated plan file
- `/plan --light` step 6 -- the just-generated proposal file
- `/advise` step 9b -- the advisory report (and optionally the design-intent file receiving D-NNN entries)
- `/advise` step 10 -- the advisory report
- post-skill step 6e -- the plan file and to-be files with STATUS marker candidates
- post-skill step 11 -- the just-completed artifact
- `/explain spec-drift` Step B -- the drift report
- `/explain spec-drift` Phase 3b step 4 -- the promote-proposal file
- `/pending` step 4 -- the source artifact for the selected pending action

**When it does NOT apply.** `AskUserQuestion` instances that gather input before any artifact exists -- no files to link yet. Examples: roadmap mode selection, onboarding role/level selection, check mode selection, explain type selection, communication audience selection.

**Relationship to Decision-point rationale convention.** Both conventions apply simultaneously. The artifact-link block appears first, then the `AskUserQuestion` with rationale on each option per the Decision-point rationale convention above.

See plan-000341 for the origin and rationale of this convention.

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
