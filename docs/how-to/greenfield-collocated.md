---
diataxis: how-to
freshness: release-bound
last-reviewed: 2026-04-18
---

# Greenfield collocated how-to

This how-to is for you when you are a solo designer or a small team starting a brand-new project from scratch and you want the SEJA harness files to live alongside your source code in the same repository. By the end of it you will have a seeded codebase, a generated design spec set, your first plan, your first implemented feature, and a clean `/check` run. It takes about 30 minutes.

## Before you start

- An empty or near-empty project directory, initialized as a git repository
- The foundational SEJA harness available locally (cloned repo or extracted download)
- The lifecycle definitions in [concepts.md -- Harness lifecycle chapter](../concepts.md#harness-lifecycle) -- every `**Harness:**` callout below links back there for the shared mechanics

## Step 1: Seed the project

Two paths lead to the same finalised project. Pick the one that matches whether you already have a local SEJA clone.

### Option A: `/seja-setup <target>` from an existing SEJA clone

Choose this path when you already have a SEJA clone on disk and want to copy the harness into a fresh target directory.

From your existing SEJA clone, run:

    /seja-setup <project-path>

`/seja-setup` copies harness files into `<project-path>`, writes `.seja-version` (pinned to the resolved public tag, or HEAD with a warning if no tag resolves), and scaffolds `_output/` and `project-design/` for `/design` to populate. Pass `--version <tag>` to pin to a specific public `seja` release (see [upgrade.md -- Pinning to a specific release](upgrade.md#pinning-to-a-specific-release) for the full procedure).

**Harness:** `/seja-setup <target>` resolves the target version via `resolve_seja_version.py` (latest SemVer tag by default, or the value passed to `--version`), copies harness files to the target, and writes `.seja-version` for future `/seja-setup --upgrade` runs to use as the baseline. See [harness-reference.md#seja-setup](../reference/harness-reference.md#seja-setup).

> **Sidebar (solo designer):** Run `git init` in `<project-path>` before `/seja-setup` so the first real commit after design captures every generated file in one clean baseline.

### Option B: clone directly into the project folder

Choose this path when you do not have a local SEJA clone, when you want to explore SEJA and decide later whether to keep it, or when you are starting fresh in an empty directory.

#### Version-pin first (recommended)

Pin to a specific public `seja` release at clone time so `/seja-setup --here` can capture an exact-match tag:

    git clone --branch v0.1.0 --depth 1 https://github.com/simonedjb/seja my-project

If you instead clone `main`, `/seja-setup --here` will record the literal string `HEAD` in `.seja-version` and print a warning; `/seja-setup --upgrade` will still work from that baseline but may not resolve relative deltas cleanly. See [upgrade.md -- Pinning to a specific release](upgrade.md#pinning-to-a-specific-release) for the full pinning procedure.

#### Baseline command

    git clone https://github.com/simonedjb/seja my-project && cd my-project && /seja-setup --here

Open Claude Code in `my-project/` and run `/seja-setup --here`. The `--here` flag finalises setup in place without copying harness files (the clone already provided them).

#### Detection step

`/seja-setup --here` first inspects the current directory and classifies it into one of six states. The routing decides whether to proceed, prompt for confirmation, or hard-abort:

- **`dev-repo-refuse`** -- the directory looks like the SEJA harness dev repo (e.g. `seja-public/` subtree, `tools/sync_to_public.py`). Hard-abort with signals listed; no mutation.
- **`public-clone-soft-confirm`** -- clean public `seja` clone at the default branch. Prompts "Yes, continue" / "No, cancel" before proceeding.
- **`finalised`** -- already-seeded project (`.claude/`, project conventions, non-empty `_output/`). Prompts "Upgrade instead" / "Re-seed anyway" / "Cancel".
- **`fresh-download`** -- harness files present, no project state yet. Proceeds directly.
- **`partial-init`** -- harness files plus partial project state. Proceeds directly with reconciliation semantics (pre-existing files are logged and skipped).
- **`no-harness`** -- no `setup/SKILL.md` found. Aborts; you are not in a SEJA download.

The Option B baseline command lands you in `fresh-download`.

#### Git-history prompt

`/seja-setup --here` asks how to handle SEJA's git history. No default is preselected -- you must pick:

- **Re-init fresh** -- Recommended when you want the project's history to start here -- SEJA's history is not yours. NOT recommended when you intended to fork and track upstream SEJA changes. A second free-text confirmation is required: type `confirm` to proceed, or cancel. Only then does `/seja-setup --here` run `rm -rf .git && git init`.
- **Keep history and add a project remote** -- Recommended when you intend to fork and track upstream SEJA changes. NOT recommended when you do not want SEJA's history in your project repo. `/seja-setup --here` prompts for your project's git remote URL and runs `git remote rename origin upstream && git remote add origin <url>`.
- **Leave as-is** -- Recommended for throwaway exploration where you will not push this to a remote. NOT recommended when you are setting up a long-lived project. No git action.

> **Warning:** The "Re-init fresh" option permanently deletes SEJA's git history. The second free-text confirmation prevents muscle-memory click-through; `/seja-setup --here` never auto-deletes `.git`.

#### Cleanup prompt

`/seja-setup --here` then asks which harness-dev artefacts to clean up. Only artefacts that exist in the current directory appear as rows; you can accept all defaults in one click or customise per row. Nothing is silently deleted -- you must submit the prompt to confirm the batch.

| Artefact | Default action | Alternatives |
| --- | --- | --- |
| `docs/` | Move to `docs/seja/` | Keep in place / Remove |
| SEJA's `README.md` | Rename to `SEJA-README.md` | Keep as-is / Remove |
| SEJA's `CHANGELOG.md` | Rename to `SEJA-CHANGELOG.md` | Keep as-is / Remove |
| `LICENSE`, `TRADEMARKS.md` | Keep in place | Remove (warns about attribution) |
| Harness-dev tools: `tools/sync_to_public.py`, `tools/cut_tag.py`, `tools/pre_publish_smoke.py`, `tools/sync-runbook.md`, `tools/monthly-dogfood-playbook.md` | Remove (not useful to consumers) | Keep (opt-in) |
| `.github/workflows/sync-public.yml` | Remove | Keep |
| `.githooks/` | Remove | Keep |

The `docs/` rename frees `docs/` for your project's own documentation while preserving SEJA attribution. README and CHANGELOG renames keep attribution while freeing those paths for your own content. Removing `LICENSE` or `TRADEMARKS.md` may violate SEJA's license terms -- the prompt warns you.

#### Version capture

Before any mutation, `/seja-setup --here` runs `git describe --tags --exact-match HEAD`. If HEAD is at an exact-match tag (e.g. `v0.1.0`), that value is written to `.seja-version`. If not, the literal string `HEAD` is written and a warning is printed. `/seja-setup --upgrade` reads `.seja-version` as the baseline for future harness refreshes.

#### Initial commit

After cleanup, `/seja-setup --here` runs `git add . && git commit -m "chore: finalise SEJA setup in place (plan-000392)"` in the current directory. If the commit fails (git not configured, or "Re-init fresh" already produced an initial commit), you will see a warning and the skill continues to the handoff.

#### Handoff

Run `/design` next to populate `project/conventions.md`, `project/standards.md`, `project/product-design-as-intended.md`, and `project/constitution.md` (see Step 2 below). The handoff message also surfaces your pinned version: "`.seja-version` is pinned to `<version>` -- `/seja-setup --upgrade` will use this as the baseline next time you want to refresh harness files."

**Harness:** `/seja-setup --here` runs state detection via `detect_setup_state.py` to confirm this is a fresh download (rather than a SEJA dev repo or an already-finalised project), pins `.seja-version` from the downloaded tag via `git describe --tags --exact-match HEAD`, creates the `_output/` skeleton and empty `project-design/` directory, and prompts you about git history handling and cleanup of harness-dev artefacts. Nothing is silently deleted. See [harness-reference.md#seja-setup](../reference/harness-reference.md#seja-setup).

> **Warning:** `--here` cannot be combined with `--workspace` or `--demo`. Use it alone to finalise SEJA setup in the current directory.

## Step 2: Run the design session

Run `/design` and walk through the interactive prompts. Focus on the conceptual design answers first -- describe who your users are, what they need to do, and why. Accept smart defaults for technical choices where you are unsure.

**Harness:** `/design` populates `project/conventions.md`, `project/standards.md`, and the initial `project/product-design-as-intended.md` from the templates in `.claude/references/template/`, and it generates `project/constitution.md` from `.claude/references/template/constitution.md` plus your answers. From this point on, `project/constitution.md` is Human-owned and is injected into every generator-agent prompt as a trust boundary, which is why later `/plan` and `/implement` runs are bounded by the decisions you make here. See [harness-reference.md#design](../reference/harness-reference.md#design).

## Step 3: Read what was generated

Open each generated file under `project/` and read it end to end. Adjust wording that does not match your intent. This is the cheapest time to fix an entity name, a role label, or a permission rule -- before any plan has been written against it.

> **Sidebar (small team):** Share the generated `project/product-design-as-intended.md` with your co-authors and land their edits in the same commit as the design output, so the first plan review starts from an agreed baseline.

## Step 4: Write the first plan

Describe the first feature you want in plain language, then run `/plan <description>`. Read the generated plan before moving on: look at the step sequence, the files the plan intends to touch, and any perspectives it has flagged for review.

**Harness:** `/plan` drives the plan-authoring pipeline, drafts the plan file into `_output/plans/`, and optionally spawns the `plan-reviewer` subagent when complexity gates fire. See [harness-reference.md#plan](../reference/harness-reference.md#plan) and [harness-reference.md#plan-reviewer](../reference/harness-reference.md#plan-reviewer).

## Step 5: Execute the plan

Run `/implement <plan-id>`. In auto mode the harness runs the full generator-critic loop without interruption; in interactive mode it pauses for confirmation between steps.

**Harness:** `/implement` drives the generator-critic loop step by step and then runs its post-skill pipeline, which updates `project/product-design-as-coded.md` within its section boundaries, refreshes the pending ledger with any deferred actions, and proposes marker flips or a commit message for you to confirm. See [harness-reference.md#implement](../reference/harness-reference.md#implement).

## Step 6: Run `/check` before committing

Run `/check validate` on the modified tree before you commit. Fix anything the validator flags.

**Harness:** `/check validate` runs the validator suite including `check_human_markers_only.py` and `check_section_boundary_writes.py`, so any accidental writes across Human-owned marker lines or across a section boundary in a multi-owner file are caught before the commit lands. See [harness-reference.md#check](../reference/harness-reference.md#check).

## Step 7: Commit and continue

Commit the generated harness scaffold and the first implemented feature in whatever granularity your git workflow prefers. You now have a live SEJA project you can keep extending with `/plan` and `/implement` cycles.

## What to read next

- [plan-and-execute.md](plan-and-execute.md) -- how to turn design intent into executable plans in depth
- [quality-gates.md](quality-gates.md) -- what `/check` does and when to run each mode
