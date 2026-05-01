# Post-Skill Reference Data

> This file is loaded by post-skill at step 0 and contains static schemas not requiring per-invocation LLM interpretation.

## Telemetry Schema

Step 1b example record:

```json
{"timestamp": "2026-03-29T14:00:00Z", "skill": "research", "id": "000014", "duration_seconds": 1800, "outcome": "success", "brief": "What other attributes could be incorporated into telemetry?", "prefix_scope": "CHORE-O", "plan_id": null, "error_type": null, "output_file": "_output/research-logs/research-000014-telemetry-attributes-expansion.md", "context_budget": "standard", "git_commit_sha": null, "files_changed": null, "parent_skill": null, "qa_type": "research-follow-up", "user_revised_output": null, "decision_points": [], "advisory_decisions": [], "research_decisions": [], "tokens_used": null}
```

| Field | Type | Source / meaning (fallback) |
|---|---|---|
| `timestamp` | ISO 8601 | Step 1's `date`, ISO-ified. |
| `skill` | string | Brief's skill field (after last `\|`). |
| `id` | string | $ARGUMENTS[0]. |
| `duration_seconds` | int\|null | Now - STARTED (`null` if unparseable). |
| `outcome` | enum | `success` / `partial` / `failed` (default `success`). |
| `brief` | string | STARTED brief text, <=200 chars. |
| `prefix_scope` | string\|null | Parent's prefix-scope (e.g. `"CHORE-O"`) or `null`. |
| `plan_id` | string\|null | From brief's `PLAN \| <id>` suffix, else `null`. |
| `error_type` | enum\|null | `git_conflict` / `permission_error` / `validation_failure` / `timeout` / `context_overflow` / `user_cancelled` / `unknown`. `null` when `outcome=="success"`. |
| `output_file` | string\|null | Relative path to primary artifact, else `null`. |
| `context_budget` | enum | Parent's YAML `context_budget` (`light` / `standard` / `heavy`). |
| `git_commit_sha` | string\|null | Filled at 8b (`null` at 1b). |
| `files_changed` | int\|null | Filled at 8b (`null` at 1b). |
| `parent_skill` | string\|null | Invoking skill from conversation context (`null` at 1b). |
| `qa_type` | enum\|null | Interaction shape -- see table below (default `"single-prompt"`). |
| `user_revised_output` | bool\|null | **Always `null` at 1b and 8b**; `/reflect` populates lazily via `git diff <git_commit_sha>..<next_sha_touching_output_file>`. |
| `decision_points` | list\|null | One `{"prompt": "...", "chosen_option": "...", "rationale_presented": <bool>}` per `AskUserQuestion`. `rationale_presented` = `true` when option descriptions carry the Decision-point rationale payload from `.claude/references/general/constraints.md` (1-2 lines + optional `(more: <link>)`); `false` for bare labels. `[]` if no calls; `null` on capture failure. |
| `advisory_decisions` | list\|null | Dual-key legacy alias; TRANSITION (plan-000468): same payload as `research_decisions`; retired at advisory-000448 Rec 5's 6-month legacy-folder revisit. |
| `research_decisions` | list\|null | `{"topic": "...", "decision": "...", "priority": "high\|medium\|low"}` per HIGH/MEDIUM recommendation; populated by `/research` step 7. `[]` non-research; `null` on capture failure. Canonical forward key. |
| `tokens_used` | int\|null | Total API tokens consumed (input + output) during the skill invocation. `null` when unavailable or capture failed. |

`qa_type` enum:

| Value | Meaning |
|---|---|
| `"single-prompt"` | End-to-end from one prompt, no Q&A or decision points. **Default when uncertain.** |
| `"multi-turn"` | Mid-run follow-ups / clarifications requiring back-and-forth. |
| `"advisory-follow-up"` | Dual-key legacy alias (TRANSITION plan-000468); same meaning as `"research-follow-up"`. |
| `"research-follow-up"` | Research/explain session with follow-ups after the primary report. |
| `"decision-point-accept"` | One `AskUserQuestion`; user picked the recommended option. |
| `"decision-point-revise"` | One `AskUserQuestion`; user picked a non-recommended option. |
| `"decision-point-reject"` | One `AskUserQuestion`; user dismissed or picked "none of these". |
| `null` | Capture failed. |

## QA-Log Directory Mapping

| Prefix | Directory |
|---|---|
| `plan-` / `implement-` | `${PLANS_DIR}` |
| `advisory-` | `${ADVISORY_DIR}` |
| `research-` | `${RESEARCH_DIR}` |
| `check-` | `${CHECK_LOGS_DIR}` |
| `proposal-` | `${PROPOSALS_DIR}` |
| `roadmap-` | `${ROADMAP_DIR}` |
| `onboarding-` | `${ONBOARDING_PLANS_DIR}` |
| `communication-` | `${COMMUNICATION_DIR}` |
| `inventory-` | `${INVENTORIES_DIR}` |
| `reflection-` | `${REFLECTIONS_DIR}` |
| `user-tests-` | `${USER_TESTS_DIR}` |
| `explained-behavior-` / `-code-` / `-data-model-` / `-architecture-` | matching `${EXPLAINED_*_DIR}` (BEHAVIORS, CODE, DATA_MODEL, ARCHITECTURE) |
| `behavior-evolution-` | `${BEHAVIOR_EVOLUTION_DIR}` |
| (unknown) | `${QA_LOGS_DIR}` |

## Telemetry Flush Example

Step 8b enriched record:

```json
{"timestamp": "2026-03-29T14:00:00Z", "skill": "research", "id": "000014", "duration_seconds": 1800, "outcome": "success", "brief": "What other attributes could be incorporated into telemetry?", "prefix_scope": "CHORE-O", "plan_id": null, "error_type": null, "output_file": "_output/research-logs/research-000014-telemetry-attributes-expansion.md", "context_budget": "standard", "git_commit_sha": "9709d91abc123...", "files_changed": 6, "parent_skill": "research", "qa_type": "research-follow-up", "user_revised_output": null, "decision_points": [{"prompt": "Apply markers now?", "chosen_option": "Defer for later review", "rationale_presented": true}], "advisory_decisions": [{"topic": "telemetry-schema", "decision": "Add research_decisions field to capture free-form design decisions", "priority": "high"}], "research_decisions": [{"topic": "telemetry-schema", "decision": "Add research_decisions field to capture free-form design decisions", "priority": "high"}], "tokens_used": null}
```
