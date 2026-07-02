---
diataxis: how-to
freshness: release-bound
last-reviewed: 2026-05-05
---

# Brownfield workspace how-to

This how-to is for you when you are a growing team or an enterprise introducing SEJA alongside an existing codebase, and you want the harness files, the design decisions, and the audit trail to live in a workspace repository that never writes into the codebase. By the end of it you will have an independent workspace repo pointing at the existing codebase, a design spec set that reads both the as-coded reality and the intended target state, a clean drift promote cycle, and a documented upgrade path for when the foundational framework changes. It takes about 50 minutes.

## Before you start

- Access to the existing codebase as a git repository you can read (and, during implement, write to via an attached working directory)
- A path for the new workspace directory, separate from the codebase
- The foundational SEJA harness available locally
- The lifecycle definitions in [concepts.md -- Harness lifecycle chapter](../concepts.md#harness-lifecycle) -- every `**Harness:**` callout below links back there for the shared mechanics

## Step 1: Create the workspace from the foundational harness

Run `python .claude/skills/scripts/create_workspace.py --from <foundational-harness> --workspace <path> --target <codebase>` from inside the foundational harness checkout. This is the scripted path that pins a new workspace to a specific existing codebase in one command.

**Harness:** `create_workspace.py` copies `.claude/` and `product-design/` into the new workspace directory, runs `git init` inside it, sets `CODEBASE_DIR` in the workspace's `project/conventions.md` to the absolute path of the codebase, and writes launcher scripts that start the agent with the codebase attached as an additional directory. The codebase itself is not touched -- the script only reads from it to validate that the path exists, never writes into it, so this is the step where the separation between the two repositories first becomes concrete. See [concepts.md -- Harness lifecycle chapter](../concepts.md#harness-lifecycle) for the full definition of the pre/post-skill pipeline, pending ledger, marker model, and constitution. The workspace script is documented in [harness-reference.md#create-workspace](../reference/harness-reference.md#create-workspace).

## Step 2: Run the design session inside the workspace

Change into the workspace and run `/design`. Because this is brownfield, the session reads the attached codebase to draft both the as-coded and the intended spec files -- but the writes land entirely in the workspace.

**Harness:** `/design` reads codebase files through the `CODEBASE_DIR` absolute path set in Step 1, drafts `project/product-design-as-coded.md` from the observed code, seeds `project/product-design-as-intended.md` with a draft for you to refine, and generates `project/constitution.md` from the constitution template. All generated files land in the workspace's `product-design/` directory; the codebase stays clean. As in every other how-to, the constitution becomes Human-owned the moment it is written, and downstream `/plan` and `/implement` runs read it as a trust boundary that bounds their outputs against the codebase. See [harness-reference.md#design](../reference/harness-reference.md#design).

> **Sidebar (growing team):** Share design decisions by pushing the workspace repo to a shared remote and having teammates pull, not by copy-pasting specs across machines; the workspace git history is your decision audit trail.

## Step 3: Explain what the codebase currently does

Run `/explain architecture`, `/explain data-model`, and `/explain behavior <feature>` from inside the workspace against the attached codebase.

**Harness:** `/explain` writes diagrams and analysis reports into the workspace's `_output/explained-<id>/` directories. The codebase is read-only during these passes. See [harness-reference.md#explain](../reference/harness-reference.md#explain).

## Step 4: Plan the first improvement

Run `/plan <description>` from the workspace targeting a specific gap between as-coded and as-intended.

**Harness:** `/plan` drafts the plan file into the workspace's `_output/plans/` directory and optionally spawns the `plan-reviewer` subagent. All codebase references inside the plan resolve via the absolute `CODEBASE_DIR`. See [harness-reference.md#plan](../reference/harness-reference.md#plan).

## Step 5: Implement, then draft Decision entries with `/explain drift --promote`

Launch the agent from the workspace with the codebase attached via `claude --add-dir <codebase-path>`, then run `/implement <plan-id>`. Verify the implemented behavior in the running codebase. When satisfied, run `/explain drift --promote`.

**Harness:** The proposal pass drafts `D-NNN` Decision entries against `project/product-design-as-intended.md` and writes them to the workspace's `_output/explained-<id>/` directory. No markers are flipped yet; the Decision text is a draft for review. Source-code writes from `/implement` land in the attached codebase, while design-reconciliation writes land in the workspace, preserving the separation between the two repositories. See [harness-reference.md#explain-spec-drift](../reference/harness-reference.md#explain-spec-drift).

## Step 6: Apply markers with `/explain drift --apply-markers`

Review the draft Decision entries in the workspace. If you accept them, run `/explain drift --apply-markers plan-<id>`.

**Harness:** The marker pass invokes `apply_marker.py` to flip `STATUS: proposed` -> `STATUS: implemented` at the line level inside the workspace copy of `project/product-design-as-intended.md`. `check_human_markers_only.py` enforces that only marker lines change in this operation, so the Decision prose and the marker flip remain two distinct audit events inside the workspace git history. See [harness-reference.md#apply-marker](../reference/harness-reference.md#apply-marker) and [harness-reference.md#check-human-markers-only](../reference/harness-reference.md#check-human-markers-only).

## Step 7: Upgrade the workspace when the foundational harness changes

Periodically run `python .claude/skills/scripts/upgrade_harness.py --from <foundational-harness> --target <workspace>` from inside the foundational harness checkout. This refreshes harness files inside the workspace without touching your project-specific design files.

**Harness:** `upgrade_harness.py` refreshes `.claude/` and the non-project parts of `product-design/` in the workspace while preserving everything under `product-design/` and everything under `_output/`. The workspace git history shows the upgrade as a single reviewable commit. See [harness-reference.md#upgrade-framework](../reference/harness-reference.md#upgrade-framework).

> **Sidebar (enterprise):** The workspace's version-control history -- plans, advisories, briefs, Decision entries, marker flips, and upgrade commits -- is the compliance-ready audit trail. Push the workspace repo to a governed remote so that SEC and DATA reviewers can inspect the same commits that drove the codebase changes.

## What to read next

- [plan-and-execute.md](plan-and-execute.md) -- how to turn design intent into executable plans in depth
- [quality-gates.md](quality-gates.md) -- what `/critique` does and when to run each mode
