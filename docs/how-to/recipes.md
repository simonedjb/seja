# FRAMEWORK - WORKFLOW RECIPES

> A cookbook of common multi-skill workflows. Each recipe chains two or more
> skills into a repeatable sequence you can follow step by step.
>
> For the full skill relationship map and post-skill suggestions, see
> `skill-graph.md` in this directory.

---

### 1. Add a New Feature

**When to use**: You have a feature request or idea and want to go from concept to working code.

**Steps**:
1. `/advise` -- explore the design space; get recommendations on approach and trade-offs
2. `/plan` -- turn the chosen approach into a step-by-step implementation plan
3. `/implement` -- execute the plan to produce working code
4. `/check validate` -- run validations to confirm nothing is broken

**Tip**: For large features, run `/plan --roadmap` first to break work into smaller plans.

---

### 2. Fix a Bug

**When to use**: You have a bug report and need a quick diagnosis-to-fix cycle.

**Steps**:
1. `/advise` -- describe the symptom; get analysis of likely root causes
2. `/plan --light` -- create a lightweight proposal for the fix
3. `/implement` -- apply the fix
4. `/check validate` -- verify the fix and ensure no regressions

**Tip**: If the bug is in test-covered code, `/implement` will automatically generate tests when the plan step has a non-N/A Tests field.

---

### 3. Review and Improve Existing Code

**When to use**: You want to improve code quality, reduce complexity, or refactor a module.

**Steps**:
1. `/check review` -- get a detailed code review with actionable findings
2. `/plan` -- create a plan to address the review findings
3. `/implement` -- execute the improvements

**Tip**: Use `/check review --perspective deep-dive` for a more thorough analysis.

---

### 4. Onboard a New Team Member

**When to use**: Someone is joining the team and needs a structured ramp-up path.

**Steps**:
1. `/onboarding <role> <level>` -- generate a tailored onboarding plan (e.g., `/onboarding BLD L2`)
2. Share the generated plan with the new team member
3. `/communication CLT` -- optionally generate a client-facing intro if the member is client-visible

**Tip**: Role families are BLD (builders), SHP (shapers), and GRD (guardians). Levels range from L1 (novice) to L5 (expert).

---

### 5. Prepare a Stakeholder Update

**When to use**: You need to report progress, metrics, or decisions to a specific audience.

**Steps**:
1. `/check telemetry` -- review recent activity, plan completion, and usage patterns
2. `/communication <audience>` -- generate tailored material (e.g., `/communication EVL` for evaluators)

**Tip**: Audience segments include EVL (evaluators), CLT (clients), USR (users), and ACD (academics).

---

### 6. Upgrade the Framework

**When to use**: A new version of the SEJA framework is available and you want to pull updates.

**Steps**:
1. `/upgrade` -- pull framework file updates while preserving project-specific files
2. `/check health` -- verify framework integrity after the upgrade
3. Review the changes and resolve any conflicts

**Tip**: Run `/explain spec-drift` afterward if you suspect design specs have diverged.

---

### 7. Explain a Confusing Part of the Codebase

**When to use**: You or a teammate need to understand unfamiliar code or architecture.

**Steps**:
1. `/explain code` -- get an explanation of specific code with diagrams and analogies
2. `/explain architecture` -- zoom out to understand how the component fits into the system

**Tip**: Follow up with `/advise` if the explanation raises design questions.

---

### 8. Run a Design Review

**When to use**: You want structured feedback on the current design direction before committing to a roadmap.

**Steps**:
1. `/advise` -- use the council format to get multi-perspective design feedback
2. `/plan --roadmap` -- translate the agreed direction into a prioritized roadmap

**Tip**: Combine with `/explain spec-drift` first if design specs may be out of sync.

---

### 9. Generate and Validate Tests

**When to use**: You want to add or update tests for a module and confirm they pass.

**Steps**:
1. `/plan` -- create a plan with Tests fields specifying what to test
2. `/implement` -- execute the plan; test generation happens automatically per step
3. `/check validate` -- run all checks to make sure the new tests pass

**Tip**: Use `/check review` first to identify which areas most need test coverage.

---

### 10. Check Documentation Freshness

**When to use**: You suspect docs are stale or inconsistent with the codebase.

**Steps**:
1. `/check docs` -- run the documentation consistency checker (path liveness, terminology, etc.)
2. Fix any findings reported by the checker
3. `/check validate` -- confirm fixes did not introduce new issues

**Tip**: Run this recipe after major refactors that rename files or move modules.

---

### 11. Figma Make to Production Code

**When to use**: You have a Figma Make prototype and want to bring it into SEJA-managed production code.

**Steps**:

1. Prototype in Figma Make (design-intent working phase)
2. `/advise` -- evaluate the prototype against project standards and identify decomposition needs
3. `/plan` -- plan the architectural decomposition and integration
4. `/implement` -- execute the plan (includes decomposing monolithic output into modular components)
5. `/check validate` -- verify the integrated code meets all quality standards

**Intake checklist** -- verify these before any Figma Make output enters the SEJA-managed codebase:

1. **Architectural decomposition** -- Figma Make produces a single file. Decompose into modular components per project architecture standards (layer boundaries, component structure, separation of concerns).
2. **Design token alignment** -- Verify that tokens used in Make Kits (npm packages, Figma variables/styles) match the production design token set. Flag any drift.
3. **Accessibility audit** -- Figma Make does not guarantee A11Y compliance. Audit the generated markup against WCAG requirements (contrast, keyboard navigation, ARIA attributes, semantic HTML).
4. **Test scaffold creation** -- Define component boundaries and create test stubs. Figma Make output has no test hooks or testable isolation. Establish the test structure before integrating.

**Feeding SEJA conventions into Figma Make** -- use Figma Make's Attachments feature to attach these SEJA reference files to your prompts, improving initial code quality and reducing the decomposition burden:

- `_references/general/coding-standards.md` -- general coding conventions
- `_references/project/standards.md` -- project-specific engineering standards (focus on the Frontend section)
- Project component templates -- existing component files as examples for Figma Make to follow

Figma Make supports these attachment types: PDF, Markdown, TSX, JS, CSS, CSV, JSON, images, and SVGs.

---

### 12. Deferred Review Workflow

**When to use**: You ran `/implement` on a feature and want to test manually before marking items implemented in `product-design-as-intended.md`. Rather than click through the IMPLEMENTED-marker confirmation immediately, you defer it until you have verified the implementation works.

**Actors**: HUMAN (designer), AGENT (Claude), HELPER (`apply_marker.py`).

**Steps**:

1. HUMAN: `/implement <plan-id>`.
2. AGENT: executes each plan step, runs tests, invokes post-skill.
3. AGENT (post-skill sub-step `e. DONE marker proposal`): presents the candidate list via `AskUserQuestion` with three options: **Apply now**, **Defer for later review**, **Skip**.
4. HUMAN: selects **Defer for later review**.
5. AGENT: for each candidate, invokes `pending.py add --type mark-implemented --source plan-<id> --description "..."`. Also creates `verify-as-coded`, `test-implementation`, and `update-documentation` pending actions from plan metadata (post-skill sub-step `g.`).
6. AGENT (post-skill step 11): contextual suggestion shows "`/pending` - Review pending actions created by this implementation".
7. HUMAN: tests the implementation manually (smoke tests, click through, whatever the domain requires).
8. HUMAN: `/pending`.
9. AGENT: lists pending items grouped by type; presents `AskUserQuestion` to pick one.
10. HUMAN: selects the `mark-implemented` item.
11. AGENT: runs per-entry `AskUserQuestion` confirmations; for each confirmed entry, invokes HELPER (`apply_marker.py --file <path> --id <entry-id> --marker STATUS --value implemented --plan <source>`).
12. HELPER: writes only the marker line; refuses any other edit. Exits 0 on success.
13. AGENT: marks the pending action done via `pending.py done <id>`.
14. HUMAN: addresses remaining items (`verify-as-coded`, `test-implementation`, `update-documentation`) one at a time in the same `/pending` session, or leaves them for a future session.

**Tip**: pre-skill's `pending-check` stage will keep reminding you about outstanding items at the top of every skill invocation until the ledger is empty, so you don't need to hold the list in your head.

---

### 13. Periodic Curation Sweep

**When to use**: It has been 30 days since your last design curation, and the `pending-check` stage surfaces a `periodic-curation` pending action. You want to review your `product-design-as-intended.md` for items ready to promote from `implemented` to `established`.

**Actors**: HUMAN (designer), AGENT (Claude), HELPER (`apply_marker.py`).

**Steps**:

1. HUMAN: runs any skill (e.g., `/advise`).
2. AGENT (pre-skill `pending-check`): emits "You have N pending actions, 1 overdue" based on the `periodic-curation` auto-created by the lazy cron.
3. HUMAN: `/pending`.
4. AGENT: lists items; HUMAN selects `periodic-curation`.
5. AGENT: prints the suggestion "Run `/explain spec-drift` to identify promotion candidates, then `/explain spec-drift --promote` to generate a proposal report. When curation is complete, `/pending done <id>`".
6. HUMAN: `/explain spec-drift`.
7. AGENT: computes drift between `product-design-as-intended.md` and `product-design-as-coded.md`, writes a drift report.
8. HUMAN: `/explain spec-drift --promote`.
9. AGENT (Phase 3a): writes a proposal report to `_output/promote-proposals/promote-proposal-plan-<NNN>.md` with draft `## Decisions` entries in Nygard shape (Context / Decision / Consequences / optional Supersedes), assigns stable `D-NNN` IDs, and creates `apply-promote-proposal` and `apply-promote-markers` pending actions (deduped against any already-pending pair for the same plan).
10. HUMAN: opens the proposal, rewrites draft entries in their own voice, copies accepted entries into `product-design-as-intended.md` under `## Decisions` (each under `### D-NNN: Title`), saves. `product-design-as-intended.md` is classified `Human (markers)` since SEJA 2.8.3 -- prose writes are strictly manual; the classification prevents agent Edit.
11. HUMAN: `/explain spec-drift --promote --apply-markers plan-<NNN>` (Phase 3b).
12. AGENT (Phase 3b): heading-only greps `^###\s+D-NNN(?::|\s*$)` in `product-design-as-intended.md` to find which entries the designer copied; splits into `present` vs `missing`; runs per-item AskUserQuestion confirmation on the `present` set; invokes `apply_marker.py --id D-NNN --marker STATUS --value established --plan plan-<NNN>` for confirmed items. Legacy uppercase `STATUS: IMPLEMENTED` markers are detected by the widened regex and REPLACED (not stacked) by the lowercase form.
13. AGENT (Phase 3b lifecycle): if ALL proposed entries are present and ALL confirmed flips succeeded, marks both `apply-promote-proposal` and `apply-promote-markers` done. If partial copy, leaves `apply-promote-proposal` pending with "N of M entries applied so far" message. If declines, leaves `apply-promote-markers` pending with the declined items listed.
14. HUMAN: `/pending done <id>` on the `periodic-curation` item (the two promote-* entries were handled by Phase 3b).
15. SYSTEM (post-skill `6c`): `check_human_markers_only.py` and `check_changelog_append_only.py` verify no prose mutations slipped into `product-design-as-intended.md` during the curation session.

**Tip**: periodic-curation is one of many pending types. Others include `spec-drift-check` (every 14 days), `verify-as-coded` (per plan), and user-defined items you add via `/pending add`. Cross-references: Recipe 12 (Deferred Review Workflow) covers the defer path that creates many of these items.
