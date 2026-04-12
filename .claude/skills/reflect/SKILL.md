---
name: reflect
description: "On-demand reflection anchored on specific plans, advisories, or other artifacts. I summarize the artifacts you choose, ask what stands out, and record your reflection."
argument-hint: "[--telemetry [--since 30d] [--skill <name>] [--dry-run]]"
compatibility: "Designed for Claude Code with SEJA framework"
metadata:
  last-updated: 2026-04-12 02:12 UTC
  version: 2.0.0
  category: analysis
  context_budget: standard
  eager_references:
    - project/conventions.md
    - general/constraints.md
  references:
    - project/conventions.md
    - general/constraints.md
    - general/shared-definitions.md
    - general/skill-graph.md
    - general/coding-standards.md
---

## Quick Guide

**What it does**: I help you reflect on specific work you have done. You pick the artifacts -- plans, advisories, or anything else in `_output/` -- and I summarize them for you. Then I ask one open-ended question, and you write your reflection in your own words. I save it as a `reflection-<id>-*.md` report that links back to the artifacts you chose. Statistical telemetry mining is available via `--telemetry` for pattern analysis across weeks of usage data.

**Example**:
> You: /reflect
> Agent: Asks which scope you want (recent plans, recent advisories, specific ID, time window, or free-form). You pick "Recent plans", select plan-000295 and plan-000303. I summarize them, ask what stands out, and write your reflection to `_output/reflections/reflection-<id>-<slug>.md`.

> You: /reflect --telemetry --since 14d
> Agent: Reads the last 14 days of telemetry, runs 5 analysis primitives, and writes a statistical reflection report.

**When to use**: You want to step back and look at specific work you have done -- what you decided, what surprised you, what you would do differently. The output is your own words anchored on real artifacts, not mechanical telemetry. When you want statistical pattern mining instead, use `--telemetry`.

**See also**: `/advise` -- prescriptive follow-up for any insight that emerges from your reflection.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--telemetry` | No | Switch to statistical telemetry mining mode (legacy V1 flow). |
| `--since <duration>` | No | Time window for `--telemetry` mode. Accepts ISO datetime or `Nd` suffix. Default: `30d`. |
| `--skill <name>` | No | Filter telemetry to a single skill in `--telemetry` mode. |
| `--dry-run` | No | Print report to stdout without writing to disk (applies to `--telemetry` mode). |

# Reflect

Output folder: `${REFLECTIONS_DIR}` (see project/conventions.md)
Filename pattern: `reflection-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)
Header pattern: `# Reflection <id> | <current datetime> | <short title>` (macro-index regex requires this exact shape)

## Mode detection

If `--telemetry` is present in the arguments, route to the [Telemetry workflow](#telemetry-workflow---telemetry) below. Otherwise, run the conversational workflow.

## Conversational workflow (default)

### Skill-specific Instructions

1. Run `/pre-skill "reflect" $ARGUMENTS` to add general instructions to the context window.

2. Reserve the next global ID by running `python .claude/skills/scripts/reserve_id.py --type reflection --title '<short title synthesized from scope>'`. Capture the returned 6-digit ID.

3. **Step A -- Pick scope.** Ask the user via AskUserQuestion which artifacts to reflect on. Each option carries rationale per the Decision-point rationale convention in `_references/general/constraints.md`:

   > "What would you like to reflect on?"

   Options:
   - **Recent plans** -- I list the last 5-10 plans from `${PLANS_DIR}` by mtime and you pick one or more. Recommended when you just finished a block of implementation work and want to step back. NOT recommended when your question is about a *sequence* of decisions rather than a single plan.
   - **Recent advisories** -- I list the last 5-10 advisories from `${ADVISORY_DIR}` by mtime and you pick one or more. Recommended when you want to re-examine a design decision after seeing how it played out. NOT recommended when the advisory has not yet been implemented.
   - **A specific artifact by ID** -- you give me an ID (e.g., `plan-000295`, `advisory-000300`) and I pull it. Recommended when you already know which artifact the reflection is about. NOT recommended when you are casting around for a topic.
   - **A time window** -- you give me a date range; I list all artifacts in that window grouped by type. Recommended when you want to reflect on a *period* (e.g., "last week"). NOT recommended when the period is shorter than a single session.
   - **Free-form** -- no artifact anchor; I give you an empty note. Recommended when the thing you want to reflect on is not yet in any artifact. NOT recommended when there is an artifact you could point at -- anchored reflections are easier to find later.

4. **Resolve the selection to artifact IDs.**

   - **Recent plans / Recent advisories**: List the last 10 files in the corresponding directory by mtime. Present them as a numbered text list (not AskUserQuestion -- the user may want to pick multiple). Capture their selection as a list of artifact IDs.
   - **A specific artifact by ID**: Prompt the user for the ID(s) via plain text. Parse the response into artifact IDs.
   - **A time window**: Prompt for start/end dates via plain text. Glob `${OUTPUT_DIR}/**/*.md`, filter by mtime, group by type, present the list, and let the user pick.
   - **Free-form**: No artifact resolution needed. Skip to Step C with an empty summary.

5. **Step B -- Summarize chosen artifacts.** Run `python .claude/skills/scripts/summarize_artifacts.py <id1> <id2> ...` to produce the narrative summary block. Capture the stdout output. Present it to the user so they can see what they are reflecting on.

6. **Step C -- Reflection prompt.** Ask the user one open-ended question via plain text (NOT AskUserQuestion -- reflection cannot be multiple choice):

   > "What stands out when you look at these now that you did not see when you wrote them?"

   Capture the user's free-text response verbatim.

7. **Step D -- Write the reflection file.** Compose a report at `${REFLECTIONS_DIR}/reflection-<id>-<slug>.md` with:

   ```markdown
   # Reflection <id> | <current datetime> | <short title>

   ## Artifacts reflected on

   <bullet list from summarize_artifacts.py output, with clickable markdown links>

   ## Summary

   <narrative summaries from Step B>

   ## Reflection

   <user's free-text response from Step C, verbatim>

   ## Follow-ups

   <!-- Optional: run /advise with any question that emerged from this reflection -->
   ```

8. Run `/post-skill <reflection-id>` to commit the reflection report.

9. Ask the user with a plain-text prompt (NOT AskUserQuestion):

   > "If any of these insights suggest something you would like to investigate further, run `/advise` with the specific question."

## Strictly non-prescriptive rule

`/reflect` writes observations and the user's own words, not prescriptions. The skill never writes "you should", "consider changing X", "we recommend", or similar. The hand-off to `/advise` is the boundary between retrospective narration and forward-looking recommendation. This convention is enforced by a test in `test_generate_reflection_report.py` that scans the generated report for forbidden substrings.

---

## Telemetry workflow (--telemetry)

> Statistical telemetry mining mode. Reads `${OUTPUT_DIR}/telemetry.jsonl` and surfaces patterns via five analysis primitives. This is the original V1 flow from plan-000295, preserved as an opt-in secondary mode.

### Skill-specific Instructions

1. Run `/pre-skill "reflect" $ARGUMENTS` to add general instructions to the context window.

2. Reserve the next global ID by running `python .claude/skills/scripts/reserve_id.py --type reflection --title '<short title synthesized from the window>'`. Capture the returned 6-digit ID.

3. Parse arguments:
   - Resolve `--since`: accept either an ISO datetime or a relative `Nd` suffix (`30d`, `14d`, `7d`). Default: `30d`.
   - Resolve `--skill`: optional single-skill filter.
   - Resolve `--dry-run`: boolean flag.

4. Load the telemetry window: read `${OUTPUT_DIR}/telemetry.jsonl`, filter by `timestamp >= <resolved since cutoff>`, and optionally filter by `skill == <name>`. Load the corresponding briefs map from `${BRIEFS_FILE}` so the stuck-loops primitive can compute Jaccard similarity over brief text.

5. **V1 note -- `user_revised_output` is not computed in V1**: this field exists on every telemetry record (written as `null` by post-skill) to reserve its shape for a future measurement. V1 does **not** populate the field. The `reflect_revision_rate` primitive reads the window, sees that no record has a non-null value, and degrades gracefully with the documented reason. Leave the window untouched and move on to step 6.

6. Invoke the orchestrator with the reserved ID:

   ```text
   python .claude/skills/scripts/generate_reflection_report.py \
       --since <resolved since> \
       --reflection-id <reserved id> \
       --title "<synthesized title>" \
       [--skill-filter <name>] \
       [--dry-run]
   ```

   - Exit 0 on success; prints the output path on write, or the report body when `--dry-run`.
   - Exit 2 on argument errors.

   Always omit `--out` so the orchestrator writes to `${REFLECTIONS_DIR}/reflection-<id>-<slug>.md` by default.

7. If `--dry-run` was requested, stop here and surface the composed report body to the user without writing to disk or committing.

8. If not `--dry-run`, confirm that the file landed at the expected path. Read the first line back to verify the H1 header matches `# Reflection <id> | <datetime> | <title>`.

9. Ask the user with a plain-text prompt (NOT AskUserQuestion):

   > "Do any of these patterns suggest something you would like to investigate further? If yes, run `/advise` with the specific pattern as your question."

10. Run `/post-skill <reflection-id>` to commit the reflection report.

## V1 analysis primitives

Each primitive lives in `.claude/skills/scripts/` and exposes an `analyze(window, ...)` function. The orchestrator embeds each primitive's observation sentences verbatim into the report body.

- **Sequence mining** -- `reflect_sequence_mining.py`
- **Duration anomalies** -- `reflect_duration_anomalies.py`
- **Revision rate** -- `reflect_revision_rate.py` (V1 always degrades; `user_revised_output` not yet computed)
- **Stuck loops** -- `reflect_stuck_loops.py`
- **Decision reversals** -- `reflect_decision_reversals.py`

## Output location

Reports land at `${REFLECTIONS_DIR}/reflection-<id>-<slug>.md`. `generate_macro_index.py` picks up the new report automatically on post-skill step 8's commit pipeline. The macro-index scanner is anchored on the H1 regex `^#\s+Reflection\s+(\d+)\s*\|\s*([\d\-: UTC]+)\s*\|\s*(.+)`, so the header shape must not be edited.
