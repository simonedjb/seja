# Recipe: Run Quality Gates

Use this recipe to catch bugs, standards violations, and regressions before they reach users.

## Goal

Run quality checks to verify code quality, test coverage, and standards
compliance.

**Total time: ~2-5 minutes per check** (preflight combines validate + review)

## Prerequisites

- SEJA framework seeded and project configured via `/seed` + `/design`
- Code changes ready to validate

## Steps

1. **Validate code changes** (~2 min)
   ```
   /check validate
   ```
   Runs validation scripts (i18n (internationalization), auth, migrations, secrets, etc.). Use after
   any code change.

   Example excerpt from a `/check validate` result:

   ```markdown
   ## Validation Results
   ✅ i18n: All strings externalized (42 keys checked)
   ✅ Auth: No unprotected routes found
   ⚠️  Migrations: 1 pending migration detected
   ✅ Secrets: No hardcoded credentials found
   Result: PASS with warnings (1 non-critical)
   ```

2. **Run a structured code review** (~3 min)
   ```
   /check review
   ```
   Reviews code against 16 engineering and design perspectives. Use before
   merging pull requests.

   <details>
   <summary>For designers</summary>

   The review checks your work against 16 perspectives including user experience, accessibility, and communicability. It catches issues like confusing labels, missing error messages, or interaction patterns that do not match your design standards.

   </details>

   <details>
   <summary>For developers</summary>

   The review uses a two-stage perspective loading protocol: it first reads `general/review-perspectives-index.md` to see all 16 perspectives, then selects 4-6 relevant ones based on the change content and loads only those from `general/review-perspectives/`. Review depth is complexity-gated via the `MINIMUM_REVIEW_DEPTH` setting in `project/conventions.md`.

   </details>

3. **Run smoke tests** (~3 min)
   ```
   /check smoke
   ```
   Exercises API endpoints and frontend pages. Use after changes to routes
   or components.

4. **Run preflight (validate + review combined)** (~5 min)
   ```
   /check preflight
   ```
   The all-in-one check before committing. Combines validation and review.

5. **Diagnose framework health** (~1 min)
   ```
   /check health
   ```
   Self-diagnoses framework integrity. Use after upgrading the framework.

6. **Generate a manual test plan** (~2 min)
   ```
   /check test-plan
   ```
   Produces a test plan for edge cases and scenarios that automated checks
   cannot cover. Use before releases.

7. **Check documentation consistency** (~2 min)
   ```
   /check docs
   ```
   Scans documentation for broken links, stale references, and structural
   issues. Use after updating docs or reference files.

8. **Audit telemetry and tracking code** (~2 min)
   ```
   /check telemetry
   ```
   Validates telemetry data integrity and tracking code patterns.

9. **Run semiotic inspection** (~3 min)
   ```
   /check semiotic-inspection
   ```
   Inspects interface messages, labels, and feedback text for
   communicability issues using semiotic engineering criteria.

## Tips

- Make `/check preflight` a habit before every commit.
- Review perspectives are priority-classified (P0 critical through P4
  informational) -- focus on P0-P1 when time is short.
- SEC and A11Y findings should never be deferred.
- For a focused security review, ask Claude to review with a security focus (e.g., "review this change with emphasis on SEC perspective").

## Related journeys

- [Solo Developer](../journeys/journey-solo-developer.md)
- [Small Team Kickoff](../journeys/journey-small-team-kickoff.md)
- [Growing Team](../journeys/journey-growing-team.md)
- [Enterprise Evolution](../journeys/journey-enterprise-evolution.md)
- [Agency Multi-Project](../journeys/journey-agency-multi-project.md)
