---
diataxis: how-to
freshness: release-bound
last-reviewed: 2026-05-05
---

# Greenfield workspace how-to

This how-to is for you when you are a solo designer or a team starting a brand-new project and you want the SEJA harness files, the design history, and the generated output to live in a separate workspace repository while your source code lives in its own clean repository. By the end of it you will have an independent workspace git repo pointing at a fresh codebase directory, a generated design spec set that reads as workspace-owned, and a first feature implemented into the codebase via an attached working directory. It takes about 35 minutes.

## Before you start

- A path where the new workspace directory will live (e.g. `d:/workspaces/my-project`)
- A separate path for the source codebase (e.g. `d:/git/my-project`), even if it is currently empty
- The foundational SEJA harness available locally
- The lifecycle definitions in [concepts.md -- Harness lifecycle chapter](../concepts.md#harness-lifecycle) -- every `**Harness:**` callout below links back there for the shared mechanics

## Step 1: Seed the workspace

Run `/setup <workspace-path> --workspace` from inside the foundational harness. Answer the prompts that ask for the codebase path; this pins the workspace to a specific source tree without copying anything into it.

**Harness:** `/seja-setup --workspace` creates the workspace directory, initializes it as a git repository, copies `.claude/` and `product-design/` into it, and generates launcher scripts that start the agent with the codebase attached as an additional working directory. The step is one full pre-skill to post-skill envelope running in workspace mode: `/seja-setup` logs its brief, resolves the codebase path you entered into an absolute reference, writes the framework files into the new workspace, and then post-skill proposes a baseline commit inside the workspace git repo rather than inside the codebase repo. The codebase itself is never written to by the setup step. See [concepts.md -- Harness lifecycle chapter](../concepts.md#harness-lifecycle) for the full definition of the pre/post-skill pipeline, pending ledger, marker model, and constitution. `/seja-setup` and the underlying workspace script are documented in [harness-reference.md#seja-setup](../reference/harness-reference.md#seja-setup) and [harness-reference.md#create-workspace](../reference/harness-reference.md#create-workspace).

## Step 2: Run the design session inside the workspace

Change into the workspace directory and run `/design`. The design session runs entirely against the workspace: all generated files land under `product-design/` in the workspace, not in the codebase.

**Harness:** `/design` generates `project/conventions.md`, `project/standards.md`, `project/product-design-as-intended.md`, and `project/constitution.md` inside the workspace. `CODEBASE_DIR` in `conventions.md` is set by absolute path to the codebase root, since the workspace and the codebase are separate git repositories and must be addressed by full path rather than by a relative one. The constitution stays in the workspace's `product-design/` and is marked Human-owned as soon as it is written, so later `/plan` and `/implement` runs read it as a trust boundary that bounds their outputs. Workspace mode changes where the file lives, not what the harness does with it. See [harness-reference.md#design](../reference/harness-reference.md#design).

## Step 3: Read the generated specs

Open each generated file in the workspace's `project/` directory. Adjust wording that does not match your intent before any plan runs against it.

> **Sidebar (small team):** Because the workspace is its own git repo, your co-authors can clone the workspace independently of the codebase, edit the design spec in a branch, and merge before the first plan runs.

## Step 4: Write the first plan

Describe the first feature in plain language, then run `/plan <description>` from the workspace.

**Harness:** `/plan` drafts the plan file into the workspace's `_output/plans/` directory and optionally spawns the `plan-reviewer` subagent when complexity gates fire. The plan references codebase paths via the absolute `CODEBASE_DIR` set in Step 2. See [harness-reference.md#plan](../reference/harness-reference.md#plan).

## Step 5: Execute the plan against the attached codebase

Launch the agent from the workspace with `claude --add-dir <codebase-path>` (or use the generated launcher script), then run `/implement <plan-id>`. The `--add-dir` flag is what gives the agent read and write access to the codebase repo from a session rooted in the workspace.

**Harness:** `/implement` runs the generator-critic loop, writing source-code changes into the attached codebase and writing design-reconciliation updates, brief-log entries, and pending-ledger entries into the workspace. The workspace tracks design decisions, plans, and briefs; the codebase holds source code. See [harness-reference.md#implement](../reference/harness-reference.md#implement).

## Step 6: Run `/critique` and commit both sides

Run `/critique validate` from the workspace. Commit workspace-side changes (plan outputs, pending ledger, design reconciliation) in the workspace repo; commit codebase-side changes in the codebase repo.

**Harness:** `/critique validate` runs the validator suite including `check_human_markers_only.py` and `check_section_boundary_writes.py` against both the workspace files and the attached codebase, so any accidental cross-repo writes across Human-owned marker lines are caught before either commit lands. See [harness-reference.md#check](../reference/harness-reference.md#check).

> **Sidebar (agency):** Each client engagement gets its own workspace repo pointing at the client's own codebase. The audit trail of plans, advisories, and briefs lives entirely inside the per-client workspace and travels with the engagement.

## What to read next

- [plan-and-execute.md](plan-and-execute.md) -- how to turn design intent into executable plans in depth
- [quality-gates.md](quality-gates.md) -- what `/critique` does and when to run each mode
