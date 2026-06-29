---
diataxis: how-to
freshness: release-bound
last-reviewed: 2026-05-05
---

# Upgrade how-to

This how-to is for you when you want to pull harness updates into your project or workspace without touching your project data. By the end of it you will have a refreshed `.claude/` and `product-design/` tree, a regenerated `harness-reference.md`, and a clean `/critique health` report. Plan on a few minutes for the upgrade itself, plus whatever time you need to read the CHANGELOG.

## Before you start

- Your working tree is clean, or pending changes are stashed.
- You know whether the target is an in-project install or a workspace alongside an existing codebase -- the command is the same, but the workspace path uses the script form.
- The lifecycle definitions in [concepts.md -- Harness lifecycle](../concepts.md#harness-lifecycle) -- every `**Harness:**` callout below links back there for its definitions.

## Step 1: Ensure a clean working tree

We commit or stash any pending work before we upgrade. An upgrade can overwrite harness files, and a clean tree makes it easy to diff what changed and to roll back if anything looks wrong after the fact. We run `git status` to confirm there are no unstaged modifications to harness files, and if there are, we decide whether to commit them, stash them, or abandon them before we proceed. This is a human-only step.

## Step 2: Run `/seja-setup --upgrade`

We invoke `/seja-setup --upgrade` from the project root. For workspace installs that live alongside a codebase, we can also call the script directly: `python .claude/skills/scripts/upgrade_harness.py --from <foundational-framework> --target <project-or-workspace>`. The slash form is the one we reach for in day-to-day work; the script form is what we use when we want to script an upgrade across several workspaces in one pass.

**Harness:** See [concepts.md -- Harness lifecycle](../concepts.md#harness-lifecycle) for the full definition of the pre/post-skill pipeline, pending ledger, marker model, and constitution. `upgrade_harness.py` copies harness files from the source-of-truth harness repo into the target, explicitly skipping `product-design/`, `_output/`, and any files classified as Human or Human (markers) in the reference-file maintainer summary. Your `project/constitution.md`, `project/product-design-as-intended.md`, and `project/product-design-as-coded.md` are never touched. See also [harness-reference.md#upgrade](../reference/harness-reference.md#upgrade).

> **Sidebar -- workspace vs in-project:** a workspace install is a separate repo that sits next to an existing codebase and drives it through SEJA without modifying it. In workspace mode we run the upgrade inside the workspace repo, not inside the codebase it drives. If we maintain several workspaces (for example, one per client project), we upgrade each one independently -- there is no fan-out mode, and each workspace's `project/` tree is its own island.

## Step 3: Let post-skill regenerate `harness-reference.md`

After the copy finishes, we let the post-skill pipeline run to completion before we touch anything else. This is the stage where the reference docs are kept honest.

**Harness:** `/seja-setup --upgrade`'s post-skill invokes `generate_harness_reference.py` against the refreshed harness state and writes the result to `seja-public/docs/reference/harness-reference.md` (or the configured public-docs root). This keeps the reference file in sync with the harness source every time we upgrade, so we never have to wonder whether the row for a given skill or script has drifted from what the skill actually does. If the generator detects a breaking rename (a skill renamed, a script moved), it logs the rename in `_output/upgrade-reports/` so we can update any prose that referred to the old name.

## Step 4: Run `/critique health`

We run `/critique health` to verify the upgrade left everything coherent. A clean `/critique health` report is our green light that the upgrade landed cleanly.

**Harness:** `/critique health` validates skill spec conformance, agent count justifications against `agent_count_policy.md`, and reference file liveness across the refreshed `product-design/` tree. If anything is missing or inconsistent -- a skill whose spec does not match the catalog, a reference file that no longer exists on disk, an agent file whose line count exceeds the policy -- it reports the gap before we start using the new harness for real work.

## Step 5: Review the CHANGELOG

We read `CHANGELOG.md` in the foundational harness repo to see what changed since our last upgrade -- new skills, renamed artifacts, new conventions, breaking changes, removed features. If a convention variable was added, we copy it into our `project/conventions.md` with a value that matches our project; if a convention was renamed, we update any references inside `project/` to the new name. This is a human-only step, but it is the one that closes the upgrade cycle and tells us whether our next `/plan` run will behave differently from our last one.

## Pinning to a specific release

By default, `/seja-setup --upgrade` pulls the latest SemVer tag from public `seja` (e.g. `v0.1.0`). If we want deterministic upgrades -- locking a project to a known-good release, coordinating a team's upgrade cadence, or reproducing a past harness state -- we pass `--version <tag>`:

```bash
/seja-setup --upgrade --version v0.1.0
```

The resolved tag is recorded in a one-line file at the project root called `.seja-version`. The next `/seja-setup --upgrade` reads this file as its baseline so it can tell you which harness version you are coming from. Projects bootstrapped before `.seja-version` existed are treated as `unknown -> <target-tag>` on the first upgrade; the file is written on that run, and subsequent upgrades have a proper baseline. If we ever want to pin from the start, we can also pass `--version` at install time with `/seja-setup <target> --version <tag>`.

**When to pin vs. track HEAD:** pin when reproducibility matters (CI pipelines, team lock-in, audit trails). Track HEAD (the default) when we want early access to harness improvements and we are willing to read the CHANGELOG between upgrades. Mixed strategies are fine -- pin a production workspace while a dogfooding workspace follows HEAD.

Implementation detail: the resolution logic lives in `.claude/skills/scripts/resolve_seja_version.py`, which queries remote tags and validates the requested version. If the remote has no SemVer tags yet (pre-`v0.1.0` state), the skill warns and falls back to HEAD.

## Harness migrations

<a id="harness-migrations"></a>

When SEJA releases a new version, some updates require more than copying files over: they need to move, rename, or reformat harness data that already exists in your project. Those structural changes are packaged as **harness migration scripts** under `.claude/migrations/` in the foundational harness repo.

When `/seja-setup --upgrade` runs, `upgrade_harness.py` calls `run_migrations.py`, which discovers every migration script whose sequence number is higher than the one last applied and runs them in order. Each migration script is idempotent: running it twice has the same effect as running it once, so an interrupted upgrade can be retried safely.

Migrations are project-data–safe by design: they update harness mechanics (file layout, script APIs, reference structure) without touching your `project/`, `_output/`, or product source files. The files classified as Human or Human (markers) -- your `constitution.md`, your `product-design-as-intended.md`, your authored conventions -- are explicitly excluded from every migration's write paths.

If a migration makes a change you want to inspect, the upgrade report written to `_output/upgrade-reports/` by `upgrade_harness.py` itemises what each migration did and whether any manual follow-up is needed.

## Quick-reference workflow

`/seja-setup --upgrade` (pull harness file updates) -> `/critique health` (verify harness integrity) -> review the CHANGELOG and resolve any conflicts.

> **Tip:** Run `/explain spec-drift` afterward if you suspect design specs have diverged during the time between upgrades.

## What to read next

- [quality-gates.md](quality-gates.md) -- detail on `/critique health` and the other gates we may want to run after the upgrade.
- [concepts.md -- Harness lifecycle](../concepts.md#harness-lifecycle) -- the canonical definitions the callouts above link back to.
