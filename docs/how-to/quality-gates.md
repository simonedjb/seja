# Quality gates how-to

This how-to is for you when you are about to commit, push, or merge work and you want to know which quality gate is the right one for the moment. By the end of it you will know which `/check` mode to reach for and when. The matrix covers nine modes; most days we use two or three of them.

## Before you start

- Your working tree has changes ready to verify, or a plan has just finished executing.
- Your project has been seeded and configured so the validator plugins discovered by `check_plugin_registry.json` are in place.
- The lifecycle definitions in [concepts.md -- Framework lifecycle](../concepts.md#framework-lifecycle) -- every `**Framework:**` callout below links back there for its definitions.

## Step 1: Before committing, run `/check validate`

We run `/check validate` as our default first-pass gate after any code change. It is fast and catches the classes of error that should never reach a commit.

**Framework:** See [concepts.md -- Framework lifecycle](../concepts.md#framework-lifecycle) for the full definition of the pre/post-skill pipeline, pending ledger, marker model, and constitution. `/check validate` runs the validator suite discovered by `run_all_checks.py` -- this includes `check_human_markers_only.py`, `check_section_boundary_writes.py`, the `check_docs.py` plugins, and the stack-specific validators declared in `.claude/skills/scripts/check_plugin_registry.json`. See also [framework-reference.md#check](../reference/framework-reference.md#check).

## Step 2: Before reviewing a plan, run `/check review`

When a plan is about to land, we run `/check review` to get a perspective-level critique of the staged diff before we merge.

**Framework:** `/check review` launches the `code-reviewer` agent in advisory mode against the staged diff. The agent selects four to six relevant review perspectives and returns a report organized by perspective with an Adopted / Deferred / N-A verdict per finding.

## Step 3: Before a smoke test, run `/check smoke`

We run `/check smoke` after route or component changes, or after any change that could break a page load.

**Framework:** `/check smoke` runs only the smoke-subset tests -- frontend page loads and API route liveness -- against the running dev server. It is faster than the full test suite and catches the class of regression we care about right before a push.

## Step 4: Before pushing to main, run `/check preflight`

`/check preflight` is our default gate before pushing to main or opening a PR. We prefer it over running validate and review in sequence because it parallelizes them.

**Framework:** `/check preflight` launches validate and review as parallel Agent invocations (per advisory-000188), then synthesizes a unified report that ranks findings by perspective priority.

## Step 5: Periodically, run `/check health` on the framework itself

We run `/check health` after an `/upgrade` or when something feels wrong about the framework layout.

**Framework:** `/check health` runs framework-only checks -- skill spec conformance, agent-count justification against `agent_count_policy.md`, and reference file liveness across the `_references/` tree.

## Step 6: On plan completion, run `/check test-plan`

When a plan is complete and we want to verify that the test plan was actually honored, we run `/check test-plan`.

**Framework:** `/check test-plan` cross-references the plan's Test plan section against the test files that exist in the codebase, flagging any Test plan bullet that has no matching test file.

## Step 7: On documentation changes, run `/check docs`

When we edit files under `seja-public/docs/` or any of the `_references/` reference trees, we run `/check docs`.

**Framework:** `/check docs` runs the `check_docs.py` plugins -- framework-integrity, path-liveness, env-vars, command-refs, terminology, structural-completeness, plus the `framework-reference-coverage` and `lifecycle-fact-uniqueness` plugins.

## Step 8: On telemetry drift, run `/check telemetry`

We run `/check telemetry` when we suspect outcome imbalance in `_output/telemetry.jsonl` -- for example, a run of deferred findings that all went to the same perspective.

**Framework:** `/check telemetry` scans `_output/telemetry.jsonl` for outcome imbalances across perspectives, skills, and review depths.

## Step 9: On user-facing text, run `/check semiotic-inspection`

When we are writing or reviewing copy (labels, error messages, onboarding prose), we run `/check semiotic-inspection`.

**Framework:** `/check semiotic-inspection` runs the semiotic inspection method against copy tone and signage, flagging communicability issues like ambiguous labels or missing feedback messages.

## Section-boundary callout (read this once)

Whenever a `/check validate` run touches `project/product-design-as-coded.md`, `check_section_boundary_writes.py` enforces a strict rule: each contiguous edit region must stay inside one H2 section (`## Conceptual Design`, `## Metacommunication`, or `## Journey Maps`). A single edit that spans two sections is rejected, even if each half would be valid on its own. This is the most common validation failure for plans that refresh the as-coded file; knowing the rule up front saves us a re-plan cycle. If we see the rejection, we split the edit into two writes, one per section.

## What to read next

- [plan-and-execute.md](plan-and-execute.md) -- context on when in the plan/implement flow each gate fits.
- [ci-integration.md](ci-integration.md) -- how to wire SEJA checks into CI/CD pipelines (git hooks, GitHub Actions, GitLab CI).
- [upgrade.md](upgrade.md) -- `/check health` is the natural follow-up after an upgrade.
- [concepts.md -- Framework lifecycle](../concepts.md#framework-lifecycle) -- the canonical definitions the callouts above link back to.
