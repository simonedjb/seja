**What it does**: Helps you reflect on specific work you have done. Two modes: **conversational** (default) where you pick artifacts and write your reflection in your own words, and **telemetry** (`--telemetry`) for statistical pattern mining across weeks of usage data.

In conversational mode, you choose a scope (recent plans, recent research, specific artifact by ID, time window, or free-form), I summarize the artifacts, ask one open-ended question, and save your reflection to `_output/reflections/reflection-<id>-<slug>.md`.

In telemetry mode, I read `telemetry.jsonl` and run 5 analysis primitives: sequence frequency, duration outliers, revision density, stuck-loop detection, and decision-reversal tracking.

**Examples**:
> `/reflect`
> Asks which scope you want (recent plans, recent research, specific ID, time window, or free-form). You pick artifacts, I summarize them, ask what stands out, and write your reflection.

> `/reflect --telemetry`
> Reads the last 30 days of telemetry data, runs all 5 analysis primitives, and writes a statistical reflection report.

> `/reflect --telemetry --since 14d`
> Same as above but scoped to the last 14 days.

> `/reflect --telemetry --skill research`
> Filters telemetry analysis to only `/research` invocations.

> `/reflect --telemetry --dry-run`
> Prints the telemetry report to stdout without writing to disk.

**When to use**: You want to step back and look at specific work you have done -- what you decided, what surprised you, what you would do differently. The conversational output is your own words anchored on real artifacts. Use `--telemetry` when you want statistical pattern mining instead of narrative reflection.

**Next step**: `/research` for a prescriptive take on any pattern surfaced here, `/design` to turn a surfaced pattern into new design intents, or `/plan` to turn it into new work.

**See also**: `/research` -- prescriptive follow-up for any insight that emerges from your reflection.
