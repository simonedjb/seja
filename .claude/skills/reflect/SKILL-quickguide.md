**What it does**: Helps you reflect on specific work you have done through two explicit lenses — the **product lens** (what you built: does it do what you intended?) and the **practice lens** (how you worked: what patterns emerge in how you designed and built it?). Three modes: **conversational** (default) where you pick artifacts, choose a lens, and write your reflection in your own words; **deep** (`--deep`) for visualization-backed practice evolution narrative; and **telemetry** (`--telemetry`) for statistical pattern mining across weeks of usage data.

In conversational mode, you choose a scope (recent plans, recent research, specific artifact by ID, time window, or free-form), I summarize the artifacts, ask which lens you are reflecting through (product, practice, or both), ask the lens-appropriate open-ended question, and save your reflection to `_output/reflections/reflection-<id>-<slug>.md`. The report records which lens was used.

In deep mode, I read telemetry and briefs within a time window, optionally filtered by a scope keyword, and produce an event matrix visualization (Vega-Lite), a transition graph (Graphviz DOT), and a past-tense practice evolution narrative. This mode is practice-oriented. All output lands in `_output/reflections/` as a markdown report with companion visualization files.

In telemetry mode, I read `telemetry.jsonl` and run 5 analysis primitives: sequence frequency, duration outliers, revision density, stuck-loop detection, and decision-reversal tracking. This mode is also practice-oriented.

**Examples**:
> `/reflect`
> Asks which scope you want (recent plans, recent research, specific ID, time window, or free-form). You pick artifacts, I summarize them, ask whether you are reflecting on the product or your practice, ask the matching question, and write your reflection.

> `/reflect --deep publish`
> Scopes to "publish" topic over the last 30 days. Produces event matrix, transition graph, and practice evolution narrative.

> `/reflect --deep --since 14d`
> All topics, last 14 days. Produces the full deep reflection with visualizations.

> `/reflect --deep semiotic --since 7d`
> Scopes to "semiotic" topic over the last 7 days.

> `/reflect --telemetry`
> Reads the last 30 days of telemetry data, runs all 5 analysis primitives, and writes a statistical reflection report.

> `/reflect --telemetry --since 14d`
> Same as above but scoped to the last 14 days.

> `/reflect --telemetry --skill research`
> Filters telemetry analysis to only `/research` invocations.

> `/reflect --telemetry --dry-run`
> Prints the telemetry report to stdout without writing to disk.

**When to use**: You want to step back and look at specific work you have done. Use the **product lens** when you want to examine what you built — a feature, a design decision, a finished spec — and ask whether it does what you intended. Use the **practice lens** (Schön's reflection-on-practice) when you want to examine how you worked — what patterns emerge, where you hesitated, what you would do differently as a practitioner. Use `--deep` when you want a visual timeline and narrative chronicle of practice evolution across a period. Use `--telemetry` when you want statistical pattern mining instead of narrative reflection.

**Next step**: `/research` for a prescriptive take on any pattern surfaced here, `/design` to turn a surfaced pattern into new design intents, or `/plan` to turn it into new work.

**See also**: `/research` -- prescriptive follow-up for any insight that emerges from your reflection.
