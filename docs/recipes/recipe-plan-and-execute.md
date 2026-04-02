# Recipe: Plan and Execute a Change

Use this recipe when you have a clear idea of what to build and want a structured approach.

## Goal

Plan a feature, bug fix, or refactor, then execute it with quality checks.

## Prerequisites

- SEJA framework seeded and project configured via `/seed` + `/design`
- A clear idea of what you want to build or fix

## Steps

1. **Write a clear brief**
   Describe what you want in plain language. Focus on the "what" and "why",
   not the "how". One paragraph is usually enough. For example: "Add a user profile page with avatar upload and bio editing."

2. **Generate a structured plan**
   ```
   /plan <brief>
   ```
   For design-driven features where intent and framing matter, use:
   ```
   /plan --framing metacomm <brief>
   ```

3. **Review the generated plan**
   Check the steps, file list, review log, and any deferred concerns. The plan
   lives in `_output/plans/` and is meant to be read before execution.

4. **Execute the plan**
   ```
   /implement <plan-id>
   ```
   The plan ID is shown in the plan file name (e.g., `plan-0042`).
   Execution automatically runs all quality checks at the end (validate,
   review, tests). Critical issues are fixed before the plan closes;
   non-critical ones are listed as deferred. Use `--skip-checks` to opt out
   for documentation-only or low-risk plans.

## Tips

- Always review the plan before running `/implement` -- especially while
  learning, so you can catch issues before changes happen.
- For larger features, use `/plan --roadmap` to decompose into
  dependency-aware implementation waves.
- Keep briefs short and focused -- one feature per plan.

## Related journeys

- [Solo Designer -- Greenfield](../journeys/journey-solo-designer-greenfield.md)
- [Solo Designer -- Brownfield](../journeys/journey-solo-designer-brownfield.md)
- [Solo Developer](../journeys/journey-solo-developer.md)
- [Small Team Kickoff](../journeys/journey-small-team-kickoff.md)
- [Enterprise Evolution](../journeys/journey-enterprise-evolution.md)
