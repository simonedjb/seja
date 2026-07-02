---
diataxis: how-to
freshness: release-bound
last-reviewed: 2026-05-05
---

# Plan and execute how-to

This how-to is for you when you have a design intent (captured in `project/product-design-as-intended.md` or in your head) and you want to turn it into executed work with an audit trail. By the end of it you will have a generated plan under `_output/plans/`, an executed implementation with committed code, and your as-coded design file updated to reflect what you just built. Plan on 10-20 minutes for a focused feature; multi-wave work via `--roadmap` takes longer.

## Before you start

- Your project has been seeded and configured via `/seja-setup` + `/design` so the constitution and conventions are in place.
- You have a one-paragraph brief in mind: what you want, and why you want it.
- The lifecycle definitions in [concepts.md -- Harness lifecycle](../concepts.md#harness-lifecycle) -- every `**Harness:**` callout below links back there for its definitions.

## Step 1: Pick your `/plan` mode

We decide up front which mode fits the work. Standard `/plan` is the default for a multi-step feature where we want a full plan with perspective review. `/plan --light` is for a surgical one-to-three-step change where a full review cycle would be overkill. `/plan --roadmap` is for multi-plan work that spans waves and needs dependency ordering across several plans. The mode choice is the single decision that most shapes how the next hour of our work will go, so we make it deliberately rather than defaulting.

**Harness:** See [concepts.md -- Harness lifecycle](../concepts.md#harness-lifecycle) for the full definition of the pre/post-skill pipeline, pending ledger, marker model, and constitution. The pre-skill 6-stage pipeline (help, brief-log, budget-eval, pending-check, ref-load, constitution) runs before the planning body begins, so by the time `/plan` reads our brief it has already loaded our `project/constitution.md` and any pending-ledger items that might constrain the plan. See also [harness-reference.md#plan](../reference/harness-reference.md#plan).

> **Sidebar -- when to use `--light`:** reach for `--light` when we know exactly which file to touch and the change is obvious (a typo fix, a single config bump, a renamed variable). `--light` skips the `plan-reviewer` subagent and produces a one-page proposal without a perspective review cycle.

> **Sidebar -- when to use `--roadmap`:** reach for `--roadmap` when the work is too large for one plan -- a restructuring that touches many files, a multi-wave refactor, or a bundle of related features. `/plan --roadmap` produces a parent roadmap with child plan stubs that we then flesh out one at a time. Use `--from-spec <path>` to seed the roadmap from a design spec file, and `--auto` for non-interactive generation.

**Which mode?**

| Situation | Mode | Why |
|---|---|---|
| Quick fix, single file, obvious change | `--light` | Skip review overhead; 1-3 step proposal |
| Standard feature or multi-file refactor | (default) | Full perspective review; complete audit trail |
| Multi-phase initiative or feature bundle | `--roadmap` | Dependency ordering across waves; child plan stubs |

## Step 2: Run `/plan` with our brief

We type the brief in plain language, focused on the what and the why rather than the how. One paragraph is usually enough. Example: "Add a user profile page with avatar upload and bio editing, so returning visitors can personalize what other users see when they arrive on their page." If the intent behind the design matters as much as the feature itself -- for example, when the feature is the embodiment of a designer's metacommunication message -- we add `--framing metacomm` so the plan inherits that framing and drafts any needed `D-NNN` Decision entries against `project/product-design-as-intended.md`.

**Harness:** the complexity gate evaluates our brief and picks an auto review depth (Light, Standard, or Deep) based on step count, file count, and affected perspective surface. If the auto depth is Standard or Deep, `/plan` spawns the `plan-reviewer` subagent in a fresh context window to run the perspective review -- the subagent loads `general/review-perspectives-index.md`, selects four to six relevant perspectives based on the draft plan's content, loads only those perspective files to stay within its context budget, and returns an adopted/deferred/N-A verdict per perspective. Any deferred finding with regression risk is flagged for the pending ledger at post-skill time.

## Step 3: Read the generated plan

We open the saved plan under `_output/plans/plan-NNNNNN-*.md` and read the Steps, the Files list, the Depends-on chain, and the Verify clauses. We check the Review Log to see which perspectives were applied and whether anything was deferred with regression risk. We scan the Step Depends-on graph to confirm the order matches our mental model of the work. This is a human-only step -- we review before we execute, and we are never surprised by what a plan did at implementation time because we already read it here.

## Step 4: Run `/implement <plan-id>`

We invoke `/implement` against the plan ID (visible in the plan file name, for example `plan-000285`). We pick interactive mode when we want to review each step's diff as it completes, or auto mode when we trust the plan and want hands-off execution. The plan ID is short-lived context; the plan file name is the canonical reference.

**Harness:** in auto mode, each plan step is dispatched to a subagent in a fresh context window, so each step starts with a clean budget regardless of how long the plan is. A progress file (`plan-<id>-progress.md`) accumulates cross-iteration learnings so each step benefits from earlier discoveries. After each step, `/implement` runs a generator-critic loop: the `code-reviewer` agent reviews the step's diff against the relevant perspectives, and if it flags critical findings the step re-runs with the findings injected into the generator prompt -- up to 2 retry iterations before the loop gives up and defers the finding to the pending ledger for human review. See also [harness-reference.md#implement](../reference/harness-reference.md#implement).

> **Sidebar -- auto vs interactive:** interactive mode pauses after each step and shows us the diff; we confirm before the next step runs. Auto mode runs the whole plan end to end and reports the result. We pick interactive when the plan touches `project/product-design-as-intended.md` or any other Human-classified file, and auto when the plan is purely Agent-classified output like tests, generated docs, or implementation files.

## Step 5: Let post-skill finish the job

After the last step runs, we let `/implement`'s post-skill pipeline finish before we touch anything else. It is the stage where the audit trail is written, and interrupting it leaves the plan half-committed.

**Harness:** post-skill runs the 13-step pipeline. It updates `project/product-design-as-coded.md` within its H2 section boundaries (`check_section_boundary_writes.py` enforces that no single edit crosses between Conceptual Design, Metacommunication, and Journey Maps -- see the dedicated callout in the quality-gates how-to). It appends to the pending ledger if any step deferred an action with regression risk. It drafts `D-NNN` Decision entries against `project/product-design-as-intended.md` when the plan introduced or changed design intent, leaving the entries under `_output/explained-NNNNNN/` for us to review before they are applied via `apply_marker.py`. It refreshes the briefs and artifact indices, logs a QA transcript under `_output/qa-logs/`, and proposes a single commit covering the whole plan.

## Step 6: Run `/critique` before pushing

Once the plan is committed locally, we run the right `/critique` mode for the change before we push or merge. The callout that narrates each mode lives in the quality-gates how-to -- we follow the link at the bottom of this page. For a typical plan we run `/critique preflight`, which parallelizes validate and review; for a documentation-only plan we run `/critique docs`; for a plan that touches telemetry we run `/critique telemetry`. The natural flow is `/plan -> /implement -> /critique -> git push`, and each arrow in that flow is a deliberate pause, not a reflex.

## Quick-reference workflows

Compact command sequences for common planning scenarios. Each links back to the steps above for the full explanation.

### Add a new feature

`/research` (explore the design space) -> `/plan` (turn the approach into a step-by-step plan) -> `/implement` (execute the plan) -> `/critique validate` (confirm nothing is broken).

> **Tip:** For large features, run `/plan --roadmap` first to break work into smaller plans.

### Fix a bug

`/research` (describe the symptom; get root cause analysis) -> `/plan --light` (create a lightweight fix proposal) -> `/implement` (apply the fix) -> `/critique validate` (verify the fix and ensure no regressions).

> **Tip:** If the bug is in test-covered code, `/implement` automatically generates tests when the plan step has a non-N/A Tests field.

### Review and improve existing code

`/critique review` (get a detailed code review with actionable findings) -> `/plan` (create a plan to address the findings) -> `/implement` (execute the improvements).

> **Tip:** Use `/critique review` with deep depth for a more thorough analysis.

### Run a design review

`/research --deep` (use the council format to get multi-perspective design feedback) -> `/plan --roadmap` (translate the agreed direction into a prioritized roadmap).

> **Tip:** Combine with `/explain drift` first if design specs may be out of sync.

### Figma Make to production code

When you have a Figma Make prototype and want to bring it into SEJA-managed production code:

1. Prototype in Figma Make (design-intent working phase).
2. `/research` -- evaluate the prototype against project standards and identify decomposition needs.
3. `/plan` -- plan the architectural decomposition and integration.
4. `/implement` -- execute the plan (includes decomposing monolithic output into modular components).
5. `/critique validate` -- verify the integrated code meets all quality standards.

**Intake checklist** -- verify these before any Figma Make output enters the codebase:

- **Architectural decomposition** -- Figma Make produces a single file. Decompose into modular components per project architecture standards.
- **Design token alignment** -- Verify that tokens used in Make Kits match the production design token set. Flag any drift.
- **Accessibility audit** -- Figma Make does not guarantee A11Y compliance. Audit the generated markup against WCAG requirements.
- **Test scaffold creation** -- Define component boundaries and create test stubs before integrating.

**Feeding SEJA conventions into Figma Make** -- use Figma Make's Attachments feature to attach these reference files to your prompts: `.claude/references/general/coding-standards.md`, `product-design/standards.md` (focus on the Frontend section), and existing component files as examples.

## What to read next

- [quality-gates.md](quality-gates.md) -- which `/critique` mode to run after `/implement` and before pushing.
- [concepts.md -- Harness lifecycle](../concepts.md#harness-lifecycle) -- the canonical definitions the callouts above link back to.
- [team-and-stakeholders.md](team-and-stakeholders.md) -- useful when a `/plan --roadmap` decomposition lands work on a teammate who needs onboarding.
