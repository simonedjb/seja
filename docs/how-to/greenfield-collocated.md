# Greenfield collocated how-to

This how-to is for you when you are a solo designer or a small team starting a brand-new project from scratch and you want the SEJA framework files to live alongside your source code in the same repository. By the end of it you will have a seeded codebase, a generated design spec set, your first plan, your first implemented feature, and a clean `/check` run. It takes about 30 minutes.

## Before you start

- An empty or near-empty project directory, initialized as a git repository
- The foundational SEJA framework available locally (cloned repo or extracted download)
- The lifecycle definitions in [concepts.md -- Framework lifecycle chapter](../concepts.md#framework-lifecycle) -- every `**Framework:**` callout below links back there for the shared mechanics

## Step 1: Seed the project

From inside the project directory, run `/seed .` (or `/seed <project-path>` from outside). This is the one-shot copy of the foundational framework into your codebase.

**Framework:** `/seed` copies `.claude/` and `_references/` into the target directory, leaving your source tree otherwise untouched. Under the hood this is the first pre-skill to post-skill envelope you will see: `/seed` runs its brief-log stage, its context-budget stage, its reference-loading stage, and then writes the framework files on your behalf before post-skill proposes a baseline commit for you to accept or adjust. The seeded framework is now ready for the design session described in Step 2. See [concepts.md -- Framework lifecycle chapter](../concepts.md#framework-lifecycle) for the full definition of the pre/post-skill pipeline, pending ledger, marker model, and constitution. `/seed` itself is documented in [framework-reference.md#seed](../reference/framework-reference.md#seed).

> **Sidebar (solo designer):** If you have not yet run `git init`, do so before `/seed` so the first real commit after design captures every generated file in one clean baseline.

## Step 2: Run the design session

Run `/design` and walk through the interactive prompts. Focus on the conceptual design answers first -- describe who your users are, what they need to do, and why. Accept smart defaults for technical choices where you are unsure.

**Framework:** `/design` populates `project/conventions.md`, `project/standards.md`, and the initial `project/product-design-as-intended.md` from the templates in `_references/template/`, and it generates `project/constitution.md` from `_references/template/constitution.md` plus your answers. From this point on, `project/constitution.md` is Human-owned and is injected into every generator-agent prompt as a trust boundary, which is why later `/plan` and `/implement` runs are bounded by the decisions you make here. See [framework-reference.md#design](../reference/framework-reference.md#design).

## Step 3: Read what was generated

Open each generated file under `project/` and read it end to end. Adjust wording that does not match your intent. This is the cheapest time to fix an entity name, a role label, or a permission rule -- before any plan has been written against it.

> **Sidebar (small team):** Share the generated `project/product-design-as-intended.md` with your co-authors and land their edits in the same commit as the design output, so the first plan review starts from an agreed baseline.

## Step 4: Write the first plan

Describe the first feature you want in plain language, then run `/plan <description>`. Read the generated plan before moving on: look at the step sequence, the files the plan intends to touch, and any perspectives it has flagged for review.

**Framework:** `/plan` drives the plan-authoring pipeline, drafts the plan file into `_output/plans/`, and optionally spawns the `plan-reviewer` subagent when complexity gates fire. See [framework-reference.md#plan](../reference/framework-reference.md#plan) and [framework-reference.md#plan-reviewer](../reference/framework-reference.md#plan-reviewer).

## Step 5: Execute the plan

Run `/implement <plan-id>`. In auto mode the framework runs the full generator-critic loop without interruption; in interactive mode it pauses for confirmation between steps.

**Framework:** `/implement` drives the generator-critic loop step by step and then runs its post-skill pipeline, which updates `project/product-design-as-coded.md` within its section boundaries, refreshes the pending ledger with any deferred actions, and proposes marker flips or a commit message for you to confirm. See [framework-reference.md#implement](../reference/framework-reference.md#implement).

## Step 6: Run `/check` before committing

Run `/check validate` on the modified tree before you commit. Fix anything the validator flags.

**Framework:** `/check validate` runs the validator suite including `check_human_markers_only.py` and `check_section_boundary_writes.py`, so any accidental writes across Human-owned marker lines or across a section boundary in a multi-owner file are caught before the commit lands. See [framework-reference.md#check](../reference/framework-reference.md#check).

## Step 7: Commit and continue

Commit the generated framework scaffold and the first implemented feature in whatever granularity your git workflow prefers. You now have a live SEJA project you can keep extending with `/plan` and `/implement` cycles.

## What to read next

- [plan-and-execute.md](plan-and-execute.md) -- how to turn design intent into executable plans in depth
- [quality-gates.md](quality-gates.md) -- what `/check` does and when to run each mode
