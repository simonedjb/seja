**What it does**: Unified quality gate -- runs validation scripts, code reviews, smoke tests, preflight checks, harness health diagnostics, documentation consistency scans, git freshness checks, telemetry analysis, test plan generation, or semiotic inspection. One skill for all "is it OK?" questions. Ten modes, one at a time.

**Examples**:
> `/critique validate`
> Runs all project validation scripts and reports pass/fail with details.

> `/critique validate i18n`
> Runs only the i18n-related validation scripts.

> `/critique review staged`
> Reviews staged changes against security, accessibility, performance, and other quality perspectives.

> `/critique review src/components --depth deep`
> Deep review of all files in a directory, evaluating all 16 quality perspectives.

> `/critique smoke api`
> Runs API smoke tests and reports which endpoints pass or fail.

> `/critique preflight`
> Combined validate + review in one pass. Go/no-go verdict for merging.

> `/critique preflight --depth light`
> Lightweight preflight -- faster pass with fewer perspectives.

> `/critique health`
> Harness self-diagnosis across 8 built-in checks (skill system, briefs hygiene, plans hygiene, references, conventions, constitution, spec compliance, pending ledger).

> `/critique health --verbose`
> Same checks with detailed output per check.

> `/critique test-plan Test the new task filtering feature`
> Produces a structured manual test plan with scenarios, step-by-step instructions, expected results, and edge cases.

> `/critique docs`
> Runs 6 documentation consistency scanners (harness integrity, path liveness, env vars, command refs, terminology, structural-completeness).

> `/critique docs --plugins terminology,structural-completeness --filter src/`
> Runs only the named scanners, filtered to a directory.

> `/critique freshness`
> Compares local branches to upstreams for configured repos, reports ahead/behind counts. Never pulls automatically.

> `/critique telemetry`
> Reads `telemetry.jsonl` and reports skill invocation statistics and usage patterns. Read-only; does not write a check log.

> `/critique semiotic-inspection task-filtering`
> Conducts a 5-step Semiotic Inspection Method (SIM) evaluation of the feature's communicability. Analyzes metalinguistic, static, and dynamic signs, then collates the three metacommunication messages.

Advanced: `--depth <light|standard|deep>` overrides review depth for `review` and `preflight` modes.

**When to use**: Before committing, after making changes, or when you want to verify code quality, project health, harness integrity, documentation consistency, git freshness, usage patterns, or interface communicability. Generate a manual test plan when you need structured QA scenarios.

**Related**: `/pending` manages the pending-actions ledger. `/critique` and `/pending` are intentionally separate -- `/critique` is heavy-budget and produces diagnostic reports; `/pending` is light-budget and drives interactive ledger curation. `/critique health` Check 9 surfaces the pending-ledger count as a diagnostic signal; any mutation (add/done/snooze/dismiss) still flows through `/pending`. See advisory-000442.

**Next step**:
- After `validate`: `/plan` to fix findings, `/critique health` for harness diagnostics, `/pending` for outstanding actions, or `/reflect` on a clean pass.
- After `review`: `/plan` to address review findings.
- After `smoke`: `/plan` to fix failing endpoints.
- After `health`: `/plan` to fix harness issues.
- After `preflight`: `/critique review` for a deeper review, or `/onboard` to onboard someone.
- After `telemetry`: `/research` to discuss usage patterns, or `/reflect` for pattern mining.
- After `test-plan`: `/communicate` to share the test plan with stakeholders.
- After `docs`, `freshness`, `semiotic-inspection`: `/reflect` on a clean pass; `/plan` when findings need fixing.
