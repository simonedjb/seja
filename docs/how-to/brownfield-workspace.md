# Brownfield workspace how-to

This how-to is for you when you are a growing team or an enterprise introducing SEJA alongside an existing codebase, and you want the framework files, the design decisions, and the audit trail to live in a workspace repository that never writes into the codebase. By the end of it you will have an independent workspace repo pointing at the existing codebase, a design spec set that reads both the as-coded reality and the intended target state, a clean spec-drift promote cycle, and a documented upgrade path for when the foundational framework changes. It takes about 50 minutes.

## Before you start

- Access to the existing codebase as a git repository you can read (and, during implement, write to via an attached working directory)
- A path for the new workspace directory, separate from the codebase
- The foundational SEJA framework available locally
- The lifecycle definitions in [concepts.md -- Framework lifecycle chapter](../concepts.md#framework-lifecycle) -- every `**Framework:**` callout below links back there for the shared mechanics

## Step 1: Create the workspace from the foundational framework

Run `python .claude/skills/scripts/create_workspace.py --from <foundational-framework> --workspace <path> --target <codebase>` from inside the foundational framework checkout. This is the scripted path that pins a new workspace to a specific existing codebase in one command.

**Framework:** `create_workspace.py` copies `.claude/` and `_references/` into the new workspace directory, runs `git init` inside it, sets `CODEBASE_DIR` in the workspace's `project/conventions.md` to the absolute path of the codebase, and writes launcher scripts that start the agent with the codebase attached as an additional directory. The codebase itself is not touched -- the script only reads from it to validate that the path exists, never writes into it, so this is the step where the separation between the two repositories first becomes concrete. See [concepts.md -- Framework lifecycle chapter](../concepts.md#framework-lifecycle) for the full definition of the pre/post-skill pipeline, pending ledger, marker model, and constitution. The workspace script is documented in [framework-reference.md#create-workspace](../reference/framework-reference.md#create-workspace).

## Step 2: Run the design session inside the workspace

Change into the workspace and run `/design`. Because this is brownfield, the session reads the attached codebase to draft both the as-coded and the intended spec files -- but the writes land entirely in the workspace.

**Framework:** `/design` reads codebase files through the `CODEBASE_DIR` absolute path set in Step 1, drafts `project/product-design-as-coded.md` from the observed code, seeds `project/product-design-as-intended.md` with a draft for you to refine, and generates `project/constitution.md` from the constitution template. All generated files land in the workspace's `_references/project/` directory; the codebase stays clean. As in every other how-to, the constitution becomes Human-owned the moment it is written, and downstream `/plan` and `/implement` runs read it as a trust boundary that bounds their outputs against the codebase. See [framework-reference.md#design](../reference/framework-reference.md#design).

> **Sidebar (growing team):** Share design decisions by pushing the workspace repo to a shared remote and having teammates pull, not by copy-pasting specs across machines; the workspace git history is your decision audit trail.

## Step 3: Explain what the codebase currently does

Run `/explain architecture`, `/explain data-model`, and `/explain behavior <feature>` from inside the workspace against the attached codebase.

**Framework:** `/explain` writes diagrams and analysis reports into the workspace's `_output/explained-<id>/` directories. The codebase is read-only during these passes. See [framework-reference.md#explain](../reference/framework-reference.md#explain).

## Step 4: Plan the first improvement

Run `/plan <description>` from the workspace targeting a specific gap between as-coded and as-intended.

**Framework:** `/plan` drafts the plan file into the workspace's `_output/plans/` directory and optionally spawns the `plan-reviewer` subagent. All codebase references inside the plan resolve via the absolute `CODEBASE_DIR`. See [framework-reference.md#plan](../reference/framework-reference.md#plan).

## Step 5: Implement, then draft Decision entries with `/explain spec-drift --promote`

Launch the agent from the workspace with the codebase attached via `claude --add-dir <codebase-path>`, then run `/implement <plan-id>`. Verify the implemented behavior in the running codebase. When satisfied, run `/explain spec-drift --promote`.

**Framework:** The proposal pass drafts `D-NNN` Decision entries against `project/product-design-as-intended.md` and writes them to the workspace's `_output/explained-<id>/` directory. No markers are flipped yet; the Decision text is a draft for review. Source-code writes from `/implement` land in the attached codebase, while design-reconciliation writes land in the workspace, preserving the separation between the two repositories. See [framework-reference.md#explain-spec-drift](../reference/framework-reference.md#explain-spec-drift).

## Step 6: Apply markers with `/explain spec-drift --apply-markers`

Review the draft Decision entries in the workspace. If you accept them, run `/explain spec-drift --apply-markers plan-<id>`.

**Framework:** The marker pass invokes `apply_marker.py` to flip `STATUS: to-be` -> `STATUS: implemented` at the line level inside the workspace copy of `project/product-design-as-intended.md`. `check_human_markers_only.py` enforces that only marker lines change in this operation, so the Decision prose and the marker flip remain two distinct audit events inside the workspace git history. See [framework-reference.md#apply-marker](../reference/framework-reference.md#apply-marker) and [framework-reference.md#check-human-markers-only](../reference/framework-reference.md#check-human-markers-only).

## Step 7: Upgrade the workspace when the foundational framework changes

Periodically run `python .claude/skills/scripts/upgrade_framework.py --from <foundational-framework> --target <workspace>` from inside the foundational framework checkout. This refreshes framework files inside the workspace without touching your project-specific design files.

**Framework:** `upgrade_framework.py` refreshes `.claude/` and the non-project parts of `_references/` in the workspace while preserving everything under `_references/project/` and everything under `_output/`. The workspace git history shows the upgrade as a single reviewable commit. See [framework-reference.md#upgrade-framework](../reference/framework-reference.md#upgrade-framework).

> **Sidebar (enterprise):** The workspace's version-control history -- plans, advisories, briefs, Decision entries, marker flips, and upgrade commits -- is the compliance-ready audit trail. Push the workspace repo to a governed remote so that SEC and DATA reviewers can inspect the same commits that drove the codebase changes.

## What to read next

- [plan-and-execute.md](plan-and-execute.md) -- how to turn design intent into executable plans in depth
- [quality-gates.md](quality-gates.md) -- what `/check` does and when to run each mode
