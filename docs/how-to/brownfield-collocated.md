---
diataxis: how-to
freshness: release-bound
last-reviewed: 2026-05-05
---

# Brownfield collocated how-to

This how-to is for you when you are a solo designer or a team with an existing codebase and you want to introduce SEJA into it without a separate workspace -- the harness files will live inside the same repository as your source code. By the end of it you will have a seeded codebase, an explained snapshot of what the system currently does, a design spec set that captures both as-coded reality and intended target, a first planned improvement, and a clean drift promote cycle that flips a verified item from `proposed` to `implemented`. It takes about 45 minutes.

## Before you start

- An existing codebase you can commit to, initialized as a git repository
- The foundational SEJA harness available locally
- The lifecycle definitions in [concepts.md -- Harness lifecycle chapter](../concepts.md#harness-lifecycle) -- every `**Harness:**` callout below links back there for the shared mechanics

## Step 1: Seed the existing codebase

Start by cloning SEJA into your codebase root:

    git clone https://github.com/simonedjb/seja .

Then open Claude Code in that directory and run `/seja-setup --here`. The `--here` flag finalises setup in place without copying harness files (the clone already provided them). Unlike a greenfield project, you are laying the harness over a tree of code that is already under version control.

**Harness:** `/seja-setup --here` runs state detection via `detect_setup_state.py` to confirm this is a fresh download (rather than a SEJA dev repo or an already-finalised project), pins `.seja-version` from the downloaded tag via `git describe --tags --exact-match HEAD`, creates the `_output/` skeleton and empty `product-design/` directory, and prompts you about git history handling (re-init fresh / keep history and add a project remote / leave as-is) and cleanup of harness-dev artefacts (`docs/` moves to `docs/seja/` by default; SEJA's `README.md` and `CHANGELOG.md` are renamed with a `SEJA-` prefix; `tools/` scripts used by framework development are removed). Nothing is silently deleted. See [harness-reference.md#seja-setup](../reference/harness-reference.md#seja-setup).

> The cloned `.git` initially points at upstream SEJA. When `/seja-setup --here` prompts for git history handling, choose *Re-init fresh* if you want your project's history to start here, *Keep history and add a project remote* if you intend to fork and track upstream SEJA updates, or *Leave as-is* for throwaway exploration.

> **Sidebar (version pinning):** `/seja-setup --here` records the downloaded tag in `.seja-version` so future `/seja-setup --upgrade` runs know the baseline. `/seja-setup` accepts `--version <tag>` to pin to a specific public `seja` release in both install and upgrade modes. In brownfield adoption, pinning the first setup is common -- it lets the team agree on a known harness version while they learn SEJA before committing to chasing HEAD. See [upgrade.md -- Pinning to a specific release](upgrade.md#pinning-to-a-specific-release) for the full procedure.

> **Sidebar (`--here` detection and prompts):** The snippet above uses `/seja-setup --here`, which also detects whether the directory is a fresh download, a partial init, or an already-finalised project, and then walks you through the git-history and cleanup prompts before writing any files. That brownfield + clone-into combination is uncommon -- most brownfield adopters already have a SEJA clone elsewhere and run `/seja-setup <target>` pointed at their existing project root instead. If you do go the clone-into route, see [Option B in the greenfield guide](greenfield-collocated.md#option-b-clone-directly-into-the-project-folder) for the full detection-states list, git-history options, and cleanup matrix.

## Step 2: Run the design session in brownfield mode

Run `/design`. The design session detects that code already exists and adapts accordingly: it asks you to describe the current system and the intended target state, and it reads the codebase to propose entries for both.

**Harness:** `/design` detects brownfield mode, spawns code-scanning passes to draft `project/product-design-as-coded.md` from the observed codebase, and seeds `project/product-design-as-intended.md` with a draft that you refine into the target state. `project/constitution.md` is still generated from the constitution template and is Human-owned after generation. See [harness-reference.md#design](../reference/harness-reference.md#design).

## Step 3: Explain what the system currently does

Run `/explain architecture`, `/explain data-model`, and `/explain behavior <feature>` for the areas you intend to touch first. These reports become the shared reference you plan against.

**Harness:** each `/explain` subcommand writes an analysis report with diagrams into `_output/explained-<id>/` and leaves the codebase untouched. See [harness-reference.md#explain](../reference/harness-reference.md#explain).

> **Sidebar (solo designer):** Start with one feature end-to-end rather than trying to explain the whole system; the first `/explain behavior` run teaches you how the output is structured and how to read it, and you can scale up from there.

## Step 4: Plan the first improvement

Run `/plan <description>` targeting the highest-priority gap between what the as-coded and as-intended files say. Keep the first plan small -- one entity, one flow, or one refactor.

**Harness:** `/plan` drafts the plan file into `_output/plans/`, optionally spawns the `plan-reviewer` subagent, and records the specific `product-design-as-intended.md` lines the plan intends to address. See [harness-reference.md#plan](../reference/harness-reference.md#plan).

## Step 5: Implement, then draft Decision entries with `/explain drift --promote`

Run `/implement <plan-id>` and let the generator-critic loop land the changes. Then verify in the running codebase that the implemented behavior matches what `project/product-design-as-intended.md` describes. When you are satisfied, run `/explain drift --promote`.

**Harness:** The proposal pass drafts `D-NNN` Decision entries against `project/product-design-as-intended.md` and writes them to `_output/explained-<id>/`. No markers are flipped yet -- the proposal pass is a draft-only operation so that you can review the rationale text before it becomes part of the spec. See [harness-reference.md#explain-spec-drift](../reference/harness-reference.md#explain-spec-drift).

## Step 6: Apply markers with `/explain drift --apply-markers`

Review the draft Decision entries in `_output/explained-<id>/`. If you accept them, run `/explain drift --apply-markers plan-<id>` to flip the marker.

**Harness:** The marker pass invokes `apply_marker.py` to flip `STATUS: proposed` -> `STATUS: implemented` at the line level inside `project/product-design-as-intended.md`. The as-intended file is enforced by `check_human_markers_only.py` -- only marker lines may change in this operation, so prose edits and marker flips stay separated into two distinct audit events. See [harness-reference.md#apply-marker](../reference/harness-reference.md#apply-marker) and [harness-reference.md#check-human-markers-only](../reference/harness-reference.md#check-human-markers-only).

## Step 7: Run `/critique` before committing

Run `/critique validate` and then `/critique review` for a perspective-aware code review.

**Harness:** `/critique validate` runs the validator suite; `/critique review` invokes the perspective reviewers selected by your plan prefix. See [harness-reference.md#check](../reference/harness-reference.md#check).

## Step 8: Commit the cycle

Commit the implementation changes, the marker flip, and the updated `product-design-as-coded.md` in whatever granularity your git workflow prefers. You now have one feature with a clean audit trail from plan to Decision to `implemented` status.

## What to read next

- [plan-and-execute.md](plan-and-execute.md) -- how to turn design intent into executable plans in depth
- [quality-gates.md](quality-gates.md) -- what `/critique` does and when to run each mode
