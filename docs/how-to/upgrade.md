# Upgrade how-to

This how-to is for you when you want to pull framework updates into your project or workspace without touching your project data. By the end of it you will have a refreshed `.claude/` and `_references/` tree, a regenerated `framework-reference.md`, and a clean `/check health` report. Plan on a few minutes for the upgrade itself, plus whatever time you need to read the CHANGELOG.

## Before you start

- Your working tree is clean, or pending changes are stashed.
- You know whether the target is an in-project install or a workspace alongside an existing codebase -- the command is the same, but the workspace path uses the script form.
- The lifecycle definitions in [concepts.md -- Framework lifecycle](../concepts.md#framework-lifecycle) -- every `**Framework:**` callout below links back there for its definitions.

## Step 1: Ensure a clean working tree

We commit or stash any pending work before we upgrade. An upgrade can overwrite framework files, and a clean tree makes it easy to diff what changed and to roll back if anything looks wrong after the fact. We run `git status` to confirm there are no unstaged modifications to framework files, and if there are, we decide whether to commit them, stash them, or abandon them before we proceed. This is a human-only step.

## Step 2: Run `/upgrade`

We invoke `/upgrade` from the project root. For workspace installs that live alongside a codebase, we can also call the script directly: `python .claude/skills/scripts/upgrade_framework.py --from <foundational-framework> --target <project-or-workspace>`. The slash form is the one we reach for in day-to-day work; the script form is what we use when we want to script an upgrade across several workspaces in one pass.

**Framework:** See [concepts.md -- Framework lifecycle](../concepts.md#framework-lifecycle) for the full definition of the pre/post-skill pipeline, pending ledger, marker model, and constitution. `upgrade_framework.py` copies framework files from the source-of-truth framework repo into the target, explicitly skipping `_references/project/`, `_output/`, and any files classified as Human or Human (markers) in the reference-file maintainer summary. Your `project/constitution.md`, `project/product-design-as-intended.md`, and `project/product-design-as-coded.md` are never touched. See also [framework-reference.md#upgrade](../reference/framework-reference.md#upgrade).

> **Sidebar -- workspace vs in-project:** a workspace install is a separate repo that sits next to an existing codebase and drives it through SEJA without modifying it. In workspace mode we run the upgrade inside the workspace repo, not inside the codebase it drives. If we maintain several workspaces (for example, one per client project), we upgrade each one independently -- there is no fan-out mode, and each workspace's `project/` tree is its own island.

## Step 3: Let post-skill regenerate `framework-reference.md`

After the copy finishes, we let the post-skill pipeline run to completion before we touch anything else. This is the stage where the reference docs are kept honest.

**Framework:** `/upgrade`'s post-skill invokes `generate_framework_reference.py` against the refreshed framework state and writes the result to `seja-public/docs/reference/framework-reference.md` (or the configured public-docs root). This keeps the reference file in sync with the framework source every time we upgrade, so we never have to wonder whether the row for a given skill or script has drifted from what the skill actually does. If the generator detects a breaking rename (a skill renamed, a script moved), it logs the rename in `_output/upgrade-reports/` so we can update any prose that referred to the old name.

## Step 4: Run `/check health`

We run `/check health` to verify the upgrade left everything coherent. A clean `/check health` report is our green light that the upgrade landed cleanly.

**Framework:** `/check health` validates skill spec conformance, agent count justifications against `agent_count_policy.md`, and reference file liveness across the refreshed `_references/` tree. If anything is missing or inconsistent -- a skill whose spec does not match the catalog, a reference file that no longer exists on disk, an agent file whose line count exceeds the policy -- it reports the gap before we start using the new framework for real work.

## Step 5: Review the CHANGELOG

We read `CHANGELOG.md` in the foundational framework repo to see what changed since our last upgrade -- new skills, renamed artifacts, new conventions, breaking changes, removed features. If a convention variable was added, we copy it into our `project/conventions.md` with a value that matches our project; if a convention was renamed, we update any references inside `project/` to the new name. This is a human-only step, but it is the one that closes the upgrade cycle and tells us whether our next `/plan` run will behave differently from our last one.

## What to read next

- [quality-gates.md](quality-gates.md) -- detail on `/check health` and the other gates we may want to run after the upgrade.
- [concepts.md -- Framework lifecycle](../concepts.md#framework-lifecycle) -- the canonical definitions the callouts above link back to.
