---
diataxis: how-to
freshness: release-bound
last-reviewed: 2026-05-05
---

# Quality gates how-to

This how-to is for you when you are about to commit, push, or merge work and you want to know which quality gate is the right one for the moment. By the end of it you will know which `/critique` mode to reach for and when. The matrix covers ten modes; most days we use two or three of them.

**Quick reference:**

| Mode | Purpose | Typical timing |
|---|---|---|
| `validate` | Run project validation scripts | After any code change |
| `review` | Perspective-level code review | Before merging a plan |
| `smoke` | Frontend page loads and API liveness | After route/component changes |
| `preflight` | Parallel validate + review | Before pushing to main |
| `health` | Framework self-diagnosis | After upgrades |
| `test-plan` | Cross-reference plan test spec against test files | After plan completion |
| `docs` | Documentation consistency | After doc edits |
| `freshness` | Git upstream comparison | When returning to the project |
| `telemetry` | Usage analytics and outcome balance | When suspecting outcome drift |
| `semiotic-inspection` | Communicability evaluation | When writing user-facing copy |

## Before you start

- Your working tree has changes ready to verify, or a plan has just finished executing.
- Your project has been seeded and configured so the validator plugins discovered by `check_plugin_registry.json` are in place.
- The lifecycle definitions in [concepts.md -- Harness lifecycle](../concepts.md#harness-lifecycle) -- every `**Harness:**` callout below links back there for its definitions.

## Step 1: Before committing, run `/critique validate`

We run `/critique validate` as our default first-pass gate after any code change. It is fast and catches the classes of error that should never reach a commit.

**Harness:** See [concepts.md -- Harness lifecycle](../concepts.md#harness-lifecycle) for the full definition of the pre/post-skill pipeline, pending ledger, marker model, and constitution. `/critique validate` runs the validator suite discovered by `run_all_checks.py` -- this includes `check_human_markers_only.py`, `check_section_boundary_writes.py`, the `check_docs.py` plugins, and the stack-specific validators declared in `.claude/skills/scripts/critique_plugin_registry.json`. See also [harness-reference.md#check](../reference/harness-reference.md#check).

## Step 2: Before reviewing a plan, run `/critique review`

When a plan is about to land, we run `/critique review` to get a perspective-level critique of the staged diff before we merge.

**Harness:** `/critique review` launches the `code-reviewer` agent in advisory mode against the staged diff. The agent selects four to six relevant review perspectives and returns a report organized by perspective with an Adopted / Deferred / N-A verdict per finding.

## Step 3: Before a smoke test, run `/critique smoke`

We run `/critique smoke` after route or component changes, or after any change that could break a page load.

**Harness:** `/critique smoke` runs only the smoke-subset tests -- frontend page loads and API route liveness -- against the running dev server. It is faster than the full test suite and catches the class of regression we care about right before a push.

## Step 4: Before pushing to main, run `/critique preflight`

`/critique preflight` is our default gate before pushing to main or opening a PR. We prefer it over running validate and review in sequence because it parallelizes them.

**Harness:** `/critique preflight` launches validate and review as parallel Agent invocations, then synthesizes a unified report that ranks findings by perspective priority.

## Step 5: Periodically, run `/critique health` on the harness itself

We run `/critique health` after a `/seja-setup --upgrade` or when something feels wrong about the harness layout.

**Harness:** `/critique health` runs harness-only checks -- skill spec conformance, agent-count justification against `agent_count_policy.md`, and reference file liveness across the `product-design/` tree.

## Step 6: On plan completion, run `/critique test-plan`

When a plan is complete and we want to verify that the test plan was actually honored, we run `/critique test-plan`.

**Harness:** `/critique test-plan` cross-references the plan's Test plan section against the test files that exist in the codebase, flagging any Test plan bullet that has no matching test file.

## Step 7: On documentation changes, run `/critique docs`

When we edit files under `seja-public/docs/` or any of the `product-design/` reference trees, we run `/critique docs`.

**Harness:** `/critique docs` runs the `check_docs.py` plugins -- harness-integrity, path-liveness, env-vars, command-refs, terminology, structural-completeness, plus the `harness-reference-coverage` and `lifecycle-fact-uniqueness` plugins.

## Step 8: When returning to the project, run `/critique freshness`

We run `/critique freshness` when we return to a project after time away and want to know whether local branches have fallen behind their upstreams.

**Harness:** `/critique freshness` runs `check_git_freshness.py` against the workspace and companion codebase (when distinct). It compares local branches to their upstreams and reports ahead/behind counts. It never pulls -- it only reports, so it is safe to run at any time. The `check-git-freshness` periodic trigger in `project/conventions.md` also files a pending-ledger entry at the configured interval so the check surfaces automatically.

## Step 9: On telemetry drift, run `/critique telemetry`

We run `/critique telemetry` when we suspect outcome imbalance in `_output/telemetry.jsonl` -- for example, a run of deferred findings that all went to the same perspective.

**Harness:** `/critique telemetry` scans `_output/telemetry.jsonl` for outcome imbalances across perspectives, skills, and review depths.

## Step 10: On user-facing text, run `/critique semiotic-inspection`

When we are writing or reviewing copy (labels, error messages, onboarding prose), we run `/critique semiotic-inspection`.

**Harness:** `/critique semiotic-inspection` runs the semiotic inspection method against copy tone and signage, flagging communicability issues like ambiguous labels or missing feedback messages.

## Section-boundary callout (read this once)

Whenever a `/critique validate` run touches `project/product-design-as-coded.md`, `check_section_boundary_writes.py` enforces a strict rule: each contiguous edit region must stay inside one H2 section (`## Conceptual Design`, `## Metacommunication`, or `## Journey Maps`). A single edit that spans two sections is rejected, even if each half would be valid on its own. This is the most common validation failure for plans that refresh the as-coded file; knowing the rule up front saves us a re-plan cycle. If we see the rejection, we split the edit into two writes, one per section.

## Quick-reference workflows

### Generate and validate tests

`/plan` (create a plan with Tests fields specifying what to test) -> `/implement` (execute the plan; test generation happens automatically per step) -> `/critique validate` (run all checks to make sure the new tests pass).

> **Tip:** Use `/critique review` first to identify which areas most need test coverage.

### Check documentation freshness

`/critique docs` (run the documentation consistency checker) -> fix any findings reported by the checker -> `/critique validate` (confirm fixes did not introduce new issues).

> **Tip:** Run this after major refactors that rename files or move modules.

## What to read next

- [plan-and-execute.md](plan-and-execute.md) -- context on when in the plan/implement flow each gate fits.
- [ci-integration.md](ci-integration.md) -- how to wire SEJA checks into CI/CD pipelines (git hooks, GitHub Actions, GitLab CI).
- [upgrade.md](upgrade.md) -- `/critique health` is the natural follow-up after an upgrade.
- [concepts.md -- Harness lifecycle](../concepts.md#harness-lifecycle) -- the canonical definitions the callouts above link back to.
