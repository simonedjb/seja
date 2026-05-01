---
diataxis: reference
freshness: release-bound
last-reviewed: 2026-04-18
---

# Release process reference

This page is the consumer-facing summary of how SEJA releases happen. It is for harness contributors and maintainers — not end-users who only consume SEJA via `/seja-setup` (install and `--upgrade`). If you simply use SEJA in a project, you can skim this page or skip it entirely.

The canonical sources of truth are the harness-private files:

- **Rules**: `tools/release-process.md` in the harness repo (`seja-priv`).
- **Runbook**: `tools/sync-runbook.md` — step-by-step procedure.
- **Dogfooding playbook**: `tools/monthly-dogfood-playbook.md`.

The content below summarizes those and should not drift from them.

## What A2 is

SEJA uses **Option A2** (per advisory-000366): an embedded monorepo where the harness source (`seja-priv`) and its public distribution (`seja-public/` as a git subtree) live in the same tree. Releases are **manual** — no automation pushes to the public `seja` repository. This is a deliberate choice. The decisive constraints were publication-privacy-by-construction (the public face must show only polished evolution) and the decision that SEJA is not open-sourced. Automated sync was evaluated and rejected because it would either leak private iteration history or require a level of sanitization tooling that outweighed the benefit for a small-team release cadence.

The workflow in `.github/workflows/sync-public.yml` is `workflow_dispatch`-only and serves as a fallback, not a routine path.

## Tag convention

- **Format**: `vMAJOR.MINOR.PATCH` (SemVer). Always prefixed with `v`.
- **Starting version**: `v0.1.0`. The leading `0.` signals the harness contract is still evolving; consumers should expect minor-version contract adjustments.
- **Who cuts tags**: any core-team member.
- **Cadence**: manual, when a coherent batch of changes is ready. Target at most ~1 release per week; batch smaller changes together.

## Release workflow (summary)

The full procedure is in `tools/sync-runbook.md`. Summary of the seven steps:

1. Update `seja-public/CHANGELOG.md` "Unreleased" section with the changes to publish.
2. Cut the tag via `python tools/cut_tag.py vX.Y.Z "<message>"`. The script creates an annotated tag and files a `PUBLISH:` entry in the pending ledger.
3. Run `python tools/sync_to_public.py` to regenerate `seja-public/` (strips priv-only sections, excludes `priv/` and `project/` directories).
4. Run `python tools/pre_publish_smoke.py` as a pre-push gate.
5. Inspect `cd seja-public/ && git diff` against the last published state.
6. Push to the public `seja` repository.
7. Resolve the `PUBLISH:` pending ledger entry.

## Drift prevention

Because the release workflow is manual, the harness has a built-in safeguard against "cut tag and forget":

- `cut_tag.py` files a `PUBLISH:` entry in the pending ledger when a tag is cut.
- The `pre-skill` lifecycle hook's `pending-check` stage surfaces this entry on every skill invocation.
- If a `PUBLISH:` entry remains unresolved for **more than 3 days**, the hook escalates: the reminder moves to the top of the output with stronger wording (⚠️ OVERDUE).
- The entry stays in the ledger until the maintainer either completes the sync procedure or explicitly dismisses it.

This is what keeps the manual path reliable. The ledger entry is the forcing function.

## Monthly dogfooding

A consumer-path dogfooding ritual runs monthly in a scratch consumer repository (not in `seja-priv`). See `tools/monthly-dogfood-playbook.md`. The ritual exercises `/seja-setup` (install and `--upgrade`) against a tagged release to surface experiential drift that CI smoke tests cannot catch — things like misleading prompts, stale how-to instructions, or broken cross-links in the consumer-facing docs.

## Hotfix policy

Deferred until the first hotfix case arises. The default rule is: forward-fix on `main` and tag the next patch version. If a consumer is actively blocked on an older version, revisit and decide per-case whether a `release/<minor>.x` branch is warranted.

## Further reading

- `tools/release-process.md` — canonical rules (in the harness tree).
- `tools/sync-runbook.md` — the step-by-step runbook.
- `tools/monthly-dogfood-playbook.md` — the dogfooding ritual.
- `CHANGELOG.md` — release notes.
