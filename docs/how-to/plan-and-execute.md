# Plan and execute how-to

This how-to is for you when you have a design intent (captured in `project/product-design-as-intended.md` or in your head) and you want to turn it into executed work with an audit trail. By the end of it you will have a generated plan under `_output/plans/`, an executed implementation with committed code, and your as-coded design file updated to reflect what you just built. Plan on 10-20 minutes for a focused feature; multi-wave work via `--roadmap` takes longer.

## Before you start

- Your project has been seeded and configured via `/seed` + `/design` so the constitution and conventions are in place.
- You have a one-paragraph brief in mind: what you want, and why you want it.
- The lifecycle definitions in [concepts.md -- Framework lifecycle](../concepts.md#framework-lifecycle) -- every `**Framework:**` callout below links back there for its definitions.

## Step 1: Pick your `/plan` mode

We decide up front which mode fits the work. Standard `/plan` is the default for a multi-step feature where we want a full plan with perspective review. `/plan --light` is for a surgical one-to-three-step change where a full review cycle would be overkill. `/plan --roadmap` is for multi-plan work that spans waves and needs dependency ordering across several plans. The mode choice is the single decision that most shapes how the next hour of our work will go, so we make it deliberately rather than defaulting.

**Framework:** See [concepts.md -- Framework lifecycle](../concepts.md#framework-lifecycle) for the full definition of the pre/post-skill pipeline, pending ledger, marker model, and constitution. The pre-skill 8-stage pipeline (help, brief-log, orphan-check, budget-eval, compaction-check, pending-check, ref-load, constitution) runs before the planning body begins, so by the time `/plan` reads our brief it has already loaded our `project/constitution.md` and any pending-ledger items that might constrain the plan. See also [framework-reference.md#plan](../reference/framework-reference.md#plan).

> **Sidebar -- when to use `--light`:** reach for `--light` when we know exactly which file to touch and the change is obvious (a typo fix, a single config bump, a renamed variable). `--light` skips the perspective review and produces a one-page proposal.

> **Sidebar -- when to use `--roadmap`:** reach for `--roadmap` when the work is too large for one plan -- a restructuring that touches many files, a multi-wave refactor, or a bundle of related features. `/plan --roadmap` produces a parent roadmap with child plan stubs that we then flesh out one at a time.

## Step 2: Run `/plan` with our brief

We type the brief in plain language, focused on the what and the why rather than the how. One paragraph is usually enough. Example: "Add a user profile page with avatar upload and bio editing, so returning visitors can personalize what other users see when they arrive on their page." If the intent behind the design matters as much as the feature itself -- for example, when the feature is the embodiment of a designer's metacommunication message -- we add `--framing metacomm` so the plan inherits that framing and drafts any needed `D-NNN` Decision entries against `project/product-design-as-intended.md`.

**Framework:** the complexity gate evaluates our brief and picks an auto review depth (Light, Standard, or Deep) based on step count, file count, and affected perspective surface. If the auto depth is Standard or Deep, `/plan` spawns the `plan-reviewer` subagent in a fresh context window to run the perspective review -- the subagent loads `general/review-perspectives-index.md`, selects four to six relevant perspectives based on the draft plan's content, loads only those perspective files to stay within its context budget, and returns an adopted/deferred/N-A verdict per perspective. Any deferred finding with regression risk is flagged for the pending ledger at post-skill time.

## Step 3: Read the generated plan

We open the saved plan under `_output/plans/plan-NNNNNN-*.md` and read the Steps, the Files list, the Depends-on chain, and the Verify clauses. We check the Review Log to see which perspectives were applied and whether anything was deferred with regression risk. We scan the Step Depends-on graph to confirm the order matches our mental model of the work. This is a human-only step -- we review before we execute, and we are never surprised by what a plan did at implementation time because we already read it here.

## Step 4: Run `/implement <plan-id>`

We invoke `/implement` against the plan ID (visible in the plan file name, for example `plan-000285`). We pick interactive mode when we want to review each step's diff as it completes, or auto mode when we trust the plan and want hands-off execution. The plan ID is short-lived context; the plan file name is the canonical reference.

**Framework:** in auto mode, each plan step is dispatched to a subagent in a fresh context window, so each step starts with a clean budget regardless of how long the plan is. A progress file (`plan-<id>-progress.md`) accumulates cross-iteration learnings so each step benefits from earlier discoveries. After each step, `/implement` runs a generator-critic loop: the `code-reviewer` agent reviews the step's diff against the relevant perspectives, and if it flags critical findings the step re-runs with the findings injected into the generator prompt -- up to 2 retry iterations before the loop gives up and defers the finding to the pending ledger for human review. See also [framework-reference.md#implement](../reference/framework-reference.md#implement).

> **Sidebar -- auto vs interactive:** interactive mode pauses after each step and shows us the diff; we confirm before the next step runs. Auto mode runs the whole plan end to end and reports the result. We pick interactive when the plan touches `project/product-design-as-intended.md` or any other Human-classified file, and auto when the plan is purely Agent-classified output like tests, generated docs, or implementation files.

## Step 5: Let post-skill finish the job

After the last step runs, we let `/implement`'s post-skill pipeline finish before we touch anything else. It is the stage where the audit trail is written, and interrupting it leaves the plan half-committed.

**Framework:** post-skill runs the 13-step pipeline. It updates `project/product-design-as-coded.md` within its H2 section boundaries (`check_section_boundary_writes.py` enforces that no single edit crosses between Conceptual Design, Metacommunication, and Journey Maps -- see the dedicated callout in the quality-gates how-to). It appends to the pending ledger if any step deferred an action with regression risk. It drafts `D-NNN` Decision entries against `project/product-design-as-intended.md` when the plan introduced or changed design intent, leaving the entries under `_output/explained-NNNNNN/` for us to review before they are applied via `apply_marker.py`. It refreshes the briefs and artifact indices, logs a QA transcript under `_output/qa-logs/`, and proposes a single commit covering the whole plan.

## Step 6: Run `/check` before pushing

Once the plan is committed locally, we run the right `/check` mode for the change before we push or merge. The callout that narrates each mode lives in the quality-gates how-to -- we follow the link at the bottom of this page. For a typical plan we run `/check preflight`, which parallelizes validate and review; for a documentation-only plan we run `/check docs`; for a plan that touches telemetry we run `/check telemetry`. The natural flow is `/plan -> /implement -> /check -> git push`, and each arrow in that flow is a deliberate pause, not a reflex.

## What to read next

- [quality-gates.md](quality-gates.md) -- which `/check` mode to run after `/implement` and before pushing.
- [concepts.md -- Framework lifecycle](../concepts.md#framework-lifecycle) -- the canonical definitions the callouts above link back to.
- [team-and-stakeholders.md](team-and-stakeholders.md) -- useful when a `/plan --roadmap` decomposition lands work on a teammate who needs onboarding.
