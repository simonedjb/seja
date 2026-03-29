# Recipe: Run Quality Gates

## Goal

Run quality checks to verify code quality, test coverage, and standards
compliance.

## Prerequisites

- SEJA framework installed and `/quickstart` / `$quickstart` completed
- Code changes ready to validate

## Steps

1. **Validate code changes**
   ```
   /check validate   # Claude
   $check validate   # Codex
   ```
   Runs validation scripts (i18n, auth, migrations, secrets, etc.). Use after
   any code change.

2. **Run a structured code review**
   ```
   /check review   # Claude
   $check review   # Codex
   ```
   Reviews code against 16 engineering and design perspectives. Use before
   merging pull requests.

3. **Run smoke tests**
   ```
   /check smoke   # Claude
   $check smoke   # Codex
   ```
   Exercises API endpoints and frontend pages. Use after changes to routes
   or components.

4. **Run preflight (validate + review combined)**
   ```
   /check preflight   # Claude
   $check preflight   # Codex
   ```
   The all-in-one check before committing. Combines validation and review.

5. **Diagnose framework health**
   ```
   /check health   # Claude
   $check health   # Codex
   ```
   Self-diagnoses framework integrity. Use after upgrading the framework.

6. **Generate a manual test plan**
   ```
   /check test-plan   # Claude
   $check test-plan   # Codex
   ```
   Produces a test plan for edge cases and scenarios that automated checks
   cannot cover. Use before releases.

## Tips

- Make `/check preflight` / `$check preflight` a habit before every commit.
- Review perspectives are priority-classified (P0 critical through P4
  informational) -- focus on P0-P1 when time is short.
- SEC and A11Y findings should never be deferred.
- Use `/check review --perspective SEC` / `$check review --perspective SEC` to run a focused security review.

## Related journeys

- [Solo Developer](../journeys/journey-solo-developer.md)
- [Small Team Kickoff](../journeys/journey-small-team-kickoff.md)
- [Growing Team](../journeys/journey-growing-team.md)
- [Enterprise Evolution](../journeys/journey-enterprise-evolution.md)
- [Agency Multi-Project](../journeys/journey-agency-multi-project.md)
