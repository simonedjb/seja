# Brownfield collocated how-to

This how-to is for you when you are a solo designer or a team with an existing codebase and you want to introduce SEJA into it without a separate workspace -- the framework files will live inside the same repository as your source code. By the end of it you will have a seeded codebase, an explained snapshot of what the system currently does, a design spec set that captures both as-coded reality and intended target, a first planned improvement, and a clean spec-drift promote cycle that flips a verified item from `proposed` to `implemented`. It takes about 45 minutes.

## Before you start

- An existing codebase you can commit to, initialized as a git repository
- The foundational SEJA framework available locally
- The lifecycle definitions in [concepts.md -- Framework lifecycle chapter](../concepts.md#framework-lifecycle) -- every `**Framework:**` callout below links back there for the shared mechanics

## Step 1: Seed the existing codebase

From the root of the existing codebase, run `/seed .`. Unlike a greenfield project, you are laying the framework over a tree of code that is already under version control.

**Framework:** `/seed` copies `.claude/` and `_references/` into the codebase root without touching any source files that are already there. Even though your codebase already has a commit history, the seed step still runs its full pre-skill to post-skill envelope: `/seed` logs the brief, evaluates the context budget against your existing source tree so the design session that follows knows how large the project is, writes the framework files alongside your code, and then post-skill proposes a commit that shows up as a single reviewable change on top of your existing history. See [concepts.md -- Framework lifecycle chapter](../concepts.md#framework-lifecycle) for the full definition of the pre/post-skill pipeline, pending ledger, marker model, and constitution. `/seed` itself is documented in [framework-reference.md#seed](../reference/framework-reference.md#seed).

## Step 2: Run the design session in brownfield mode

Run `/design`. The design session detects that code already exists and adapts accordingly: it asks you to describe the current system and the intended target state, and it reads the codebase to propose entries for both.

**Framework:** `/design` detects brownfield mode, spawns code-scanning passes to draft `project/product-design-as-coded.md` from the observed codebase, and seeds `project/product-design-as-intended.md` with a draft that you refine into the target state. `project/constitution.md` is still generated from the constitution template and is Human-owned after generation. See [framework-reference.md#design](../reference/framework-reference.md#design).

## Step 3: Explain what the system currently does

Run `/explain architecture`, `/explain data-model`, and `/explain behavior <feature>` for the areas you intend to touch first. These reports become the shared reference you plan against.

**Framework:** each `/explain` subcommand writes an analysis report with diagrams into `_output/explained-<id>/` and leaves the codebase untouched. See [framework-reference.md#explain](../reference/framework-reference.md#explain).

> **Sidebar (solo designer):** Start with one feature end-to-end rather than trying to explain the whole system; the first `/explain behavior` run teaches you how the output is structured and how to read it, and you can scale up from there.

## Step 4: Plan the first improvement

Run `/plan <description>` targeting the highest-priority gap between what the as-coded and as-intended files say. Keep the first plan small -- one entity, one flow, or one refactor.

**Framework:** `/plan` drafts the plan file into `_output/plans/`, optionally spawns the `plan-reviewer` subagent, and records the specific `product-design-as-intended.md` lines the plan intends to address. See [framework-reference.md#plan](../reference/framework-reference.md#plan).

## Step 5: Implement, then draft Decision entries with `/explain spec-drift --promote`

Run `/implement <plan-id>` and let the generator-critic loop land the changes. Then verify in the running codebase that the implemented behavior matches what `project/product-design-as-intended.md` describes. When you are satisfied, run `/explain spec-drift --promote`.

**Framework:** The proposal pass drafts `D-NNN` Decision entries against `project/product-design-as-intended.md` and writes them to `_output/explained-<id>/`. No markers are flipped yet -- the proposal pass is a draft-only operation so that you can review the rationale text before it becomes part of the spec. See [framework-reference.md#explain-spec-drift](../reference/framework-reference.md#explain-spec-drift).

## Step 6: Apply markers with `/explain spec-drift --apply-markers`

Review the draft Decision entries in `_output/explained-<id>/`. If you accept them, run `/explain spec-drift --apply-markers plan-<id>` to flip the marker.

**Framework:** The marker pass invokes `apply_marker.py` to flip `STATUS: proposed` -> `STATUS: implemented` at the line level inside `project/product-design-as-intended.md`. The as-intended file is enforced by `check_human_markers_only.py` -- only marker lines may change in this operation, so prose edits and marker flips stay separated into two distinct audit events. See [framework-reference.md#apply-marker](../reference/framework-reference.md#apply-marker) and [framework-reference.md#check-human-markers-only](../reference/framework-reference.md#check-human-markers-only).

## Step 7: Run `/check` before committing

Run `/check validate` and then `/check review` for a perspective-aware code review.

**Framework:** `/check validate` runs the validator suite; `/check review` invokes the perspective reviewers selected by your plan prefix. See [framework-reference.md#check](../reference/framework-reference.md#check).

## Step 8: Commit the cycle

Commit the implementation changes, the marker flip, and the updated `product-design-as-coded.md` in whatever granularity your git workflow prefers. You now have one feature with a clean audit trail from plan to Decision to `implemented` status.

## What to read next

- [plan-and-execute.md](plan-and-execute.md) -- how to turn design intent into executable plans in depth
- [quality-gates.md](quality-gates.md) -- what `/check` does and when to run each mode
