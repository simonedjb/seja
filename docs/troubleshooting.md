# Troubleshooting

Scan this page when a SEJA session output looks wrong and you need
to pick the right triage move fast. It is a lookup table, not a
tutorial: every row points at the canonical explanation in
[concepts.md](concepts.md#framework-lifecycle) or a specific how-to
step, and you follow the link from there for the full story.

If you want to understand the lifecycle envelope before diagnosing
anything, read [concepts.md -- Framework lifecycle](concepts.md#framework-lifecycle)
first and come back to this page with a mental model of the
`pre-skill -> skill body -> post-skill` pipeline in hand.

## Symptom lookup

Find the row whose symptom matches what you are seeing, follow the
"Where to look" link for the canonical explanation, then take the
"Next step" action.

| Symptom | Likely cause | Where to look | Next step |
|---|---|---|---|
| A skill wrote files outside the directory you expected | Section-boundary violation; the skill body edited a file owned by a different lifecycle stage | [concepts.md -- Section boundaries](concepts.md#section-boundaries) and the post-skill boundary check | Revert the stray writes by hand, then re-run the original skill; if it repeats, file a bug with the pre-skill log attached |
| `product-design-as-intended.md` and `product-design-as-coded.md` disagree after an implementation | Spec drift -- the code landed but intent was not updated, or vice versa | [concepts.md -- product-design-as-intended vs product-design-as-coded](concepts.md#product-design-as-intended-vs-product-design-as-coded) | Run `/explain spec-drift` for a section-by-section drift report, then `/explain spec-drift --promote` to draft D-NNN Decision entries for anything you want to keep |
| A STATUS, ESTABLISHED, or CHANGELOG_APPEND marker appears in the wrong file | Hand-edit bypassed `apply_marker.py`, or the marker was copied instead of applied | [concepts.md -- STATUS, ESTABLISHED, CHANGELOG_APPEND](concepts.md#status-established-changelog-append) | Delete the misplaced marker, re-run the skill that should have written it; markers flow through `apply_marker.py` only, never hand edits |
| The pending ledger has stale, overdue, or duplicated items | Human actions were logged but never verified or flipped | [concepts.md -- Pending ledger](concepts.md#pending-ledger) | Run `/pending` to list outstanding items, verify the ones you have already done, and flip their markers; use `/pending --curate` for the periodic curation pass |
| A review perspective (plan-reviewer, code-reviewer, doc-reviewer) output looks off or missing | Perspective shortlist did not pick up the relevant angle, or a subagent was skipped under Light depth | [concepts.md -- Review perspectives](concepts.md#review-perspectives) | Re-run the skill with `--review deep` (or `--review-depth deep`) to force a full perspective pass |
| You are not sure whether to run `/advise`, `/explain`, or `/communication` | These three skills look similar but answer different intents | The decision table below, and the full matrix at [concepts.md -- /advise vs /explain vs /communication](concepts.md#advise-vs-explain-vs-communication) | Pick the row whose "When to use" phrase matches your sentence, then run that skill |

## /advise vs /explain vs /communication (surface table)

The authoritative matrix with every sub-mode lives in
[concepts.md](concepts.md#advise-vs-explain-vs-communication). Use
this three-row version as a fast first cut when you are triaging
and do not want to read the full chapter.

| Skill | When to use | Writes to | Key output |
|---|---|---|---|
| `/advise` | You have a decision to make and want a recommendation with pros and cons | `${ADVISORY_DIR}` (or `${INVENTORIES_DIR}` with `--inventory`) | Advisory report with logged Q&A pair and a recommendations summary |
| `/explain` | You want to understand existing behavior, code, data, architecture, or spec drift | `${EXPLAINED_*_DIR}` for the chosen mode; `${ADVISORY_DIR}` for `spec-drift` | Analysis report with diagrams, analogies, and (for `spec-drift`) a drift report plus optional D-NNN Decision drafts |
| `/communication` | You need stakeholder-facing material for a specific audience (EVL, CLT, USR, ACD) | `${COMMUNICATION_DIR}/<YYYY-MM-DD>/` | Date-versioned audience-specific files, with an `index.md` when more than one audience is generated the same day |

## Still stuck?

If none of the rows above match your symptom, read
[concepts.md -- Framework lifecycle](concepts.md#framework-lifecycle)
end to end. The lifecycle chapter walks through the
`pre-skill -> skill body -> post-skill` envelope every slash
command runs inside, and understanding that envelope is usually
enough to locate any symptom that does not fit a known row.
