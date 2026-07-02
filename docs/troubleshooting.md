---
diataxis: reference
freshness: release-bound
last-reviewed: 2026-05-05
---

# Troubleshooting

Scan this page when a SEJA session output looks wrong and you need
to pick the right triage move fast. It is a lookup table, not a
tutorial: every row points at the canonical explanation in
[concepts.md](concepts.md#harness-lifecycle) or a specific how-to
step, and you follow the link from there for the full story.

If you want to understand the lifecycle envelope before diagnosing
anything, read [concepts.md -- Harness lifecycle](concepts.md#harness-lifecycle)
first and come back to this page with a mental model of the
`pre-skill -> skill body -> post-skill` pipeline in hand.

## Symptom lookup

Find the row whose symptom matches what you are seeing, follow the
"Where to look" link for the canonical explanation, then take the
"Next step" action.

| Symptom | Likely cause | Where to look | Next step |
|---|---|---|---|
| A skill wrote files outside the directory you expected | Section-boundary violation; the skill body edited a file owned by a different lifecycle stage | [concepts.md -- Section boundaries](concepts.md#section-boundaries) and the post-skill boundary check | Revert the stray writes by hand, then re-run the original skill; if it repeats, file a bug with the pre-skill log attached |
| `product-design-as-intended.md` and `product-design-as-coded.md` disagree after an implementation | Spec drift -- the code landed but intent was not updated, or vice versa | [concepts.md -- product-design-as-intended vs product-design-as-coded](concepts.md#product-design-as-intended-vs-product-design-as-coded) | Run `/explain drift` for a section-by-section drift report, then `/explain drift --promote` to draft D-NNN Decision entries for anything you want to keep |
| A STATUS, ESTABLISHED, or CHANGELOG_APPEND marker appears in the wrong file | Hand-edit bypassed `apply_marker.py`, or the marker was copied instead of applied | [concepts.md -- STATUS, ESTABLISHED, CHANGELOG_APPEND](concepts.md#status-established-changelog-append) | Delete the misplaced marker, re-run the skill that should have written it; markers flow through `apply_marker.py` only, never hand edits |
| The pending ledger has stale, overdue, or duplicated items | Human actions were logged but never verified or flipped | [concepts.md -- Pending ledger](concepts.md#pending-ledger) | Run `/pending` to list outstanding items, verify the ones you have already done, and flip their markers; use `/pending --curate` for the periodic curation pass |
| A review perspective (plan-reviewer, code-reviewer, doc-reviewer) output looks off or missing | Perspective shortlist did not pick up the relevant angle, or a subagent was skipped under Light depth | [concepts.md -- Review perspectives](concepts.md#review-perspectives) | Re-run the skill with `--review deep` (or `--review-depth deep`) to force a full perspective pass |
| You are not sure whether to run `/research`, `/explain`, or `/communicate` | These three skills look similar but answer different intents | The decision table below, and the full matrix at [concepts.md -- /research vs /explain vs /communicate](concepts.md#research-vs-explain-vs-communication) | Pick the row whose "When to use" phrase matches your sentence, then run that skill |
| Pre-skill hangs or takes much longer than expected | `conventions.md` is missing or malformed, causing `ref-load` to fail; or the briefs window is too large for the `budget-eval` stage | [concepts.md -- Pre-skill 6-stage pipeline](concepts.md#pre-skill-pipeline) | Verify `project/conventions.md` exists and parses correctly; if the project was just seeded, run `/design` to generate it |
| "Constitution not found" error at pre-skill | `/design` was not run after `/seja-setup`, so `project/constitution.md` does not exist | [concepts.md -- Constitution](concepts.md#constitution) | Run `/design` to generate the constitution; `/critique health` also validates its presence |
| `apply_marker.py` rejects a STATUS transition | Invalid state transition (e.g., jumping from `proposed` directly to `established` without passing through `implemented`) | [concepts.md -- product-design-as-intended vs product-design-as-coded](concepts.md#product-design-as-intended-vs-as-coded) | Check the current STATUS value in the file and follow the valid transition path: `proposed -> implemented -> established -> superseded` |
| Duplicate `D-NNN` Decision ID in `product-design-as-intended.md` | Manual copy-paste of a Decision entry without changing the ID, or two promote passes that assigned the same ID | [concepts.md -- D-NNN Decision entries](concepts.md#decision-entries) | Renumber the duplicate entry to the next available `D-NNN` ID; `generate_decision_digest.py` will flag duplicates on its next run |
| `/seja-setup --upgrade` reports missing source files | The source harness is incomplete, or the tag passed to `--version` does not exist | [upgrade.md](how-to/upgrade.md) | Verify the source repo is a complete SEJA clone; if using `--version`, confirm the tag exists with `git tag -l` in the source |
| `.seja-version` not found during upgrade | The project predates the `.seja-version` convention (pre-v0.1.0) or was seeded without `/seja-setup --here` | [upgrade.md -- Pinning to a specific release](how-to/upgrade.md) | Run `/seja-setup --here` once to write the version pin, then retry the upgrade |
| Skill output appears truncated or missing sections | The context budget was exhausted; the skill body was too large for the available window | [concepts.md -- Pre-skill 6-stage pipeline](concepts.md#pre-skill-pipeline) (budget-eval stage) | Start a new session to reset the context window; for complex skills, reduce the scope of the request |
| Compaction warning appears at pre-skill | Too many skill invocations in one session; older context is about to be summarized | [concepts.md -- Pre-skill 6-stage pipeline](concepts.md#pre-skill-pipeline) (compaction-check stage) | Start a new session; the brief, QA log, and commit history from the current session will reconstruct context |
| Post-skill did not commit | The preflight gate (step 7) failed, blocking the commit | [concepts.md -- Post-skill 13-step pipeline](concepts.md#post-skill-pipeline) | Read the preflight report in the skill output; fix the flagged issue (often a section-boundary violation or a human-markers write) and re-run |

## /research vs /explain vs /communicate (surface table)

The authoritative matrix with every sub-mode lives in
[concepts.md](concepts.md#research-vs-explain-vs-communication). Use
this three-row version as a fast first cut when you are triaging
and do not want to read the full chapter.

| Skill | When to use | Writes to | Key output |
|---|---|---|---|
| `/research` | You have a decision to make and want a recommendation with pros and cons | `${ADVISORY_DIR}` (or `${INVENTORIES_DIR}` with `--inventory`) | Research report with logged Q&A pair and a recommendations summary |
| `/explain` | You want to understand existing behavior, code, data, architecture, or drift between specs | `${EXPLAINED_*_DIR}` for the chosen mode; `${ADVISORY_DIR}` for `drift` | Analysis report with diagrams, analogies, and (for `drift`) a drift report plus optional D-NNN Decision drafts |
| `/communicate` | You need stakeholder-facing material for a specific audience (EVL, CLT, USR, ACD) | `${COMMUNICATION_DIR}/<YYYY-MM-DD>/` | Date-versioned audience-specific files, with an `index.md` when more than one audience is generated the same day |

## Still stuck?

If none of the rows above match your symptom, read
[concepts.md -- Harness lifecycle](concepts.md#harness-lifecycle)
end to end. The lifecycle chapter walks through the
`pre-skill -> skill body -> post-skill` envelope every slash
command runs inside, and understanding that envelope is usually
enough to locate any symptom that does not fit a known row.
