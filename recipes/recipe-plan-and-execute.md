# Recipe: Plan and Execute a Change

## Goal

Plan a feature, bug fix, or refactor, then execute it with quality checks.

## Prerequisites

- SEJA framework installed and `/quickstart` / `$quickstart` completed
- A clear idea of what you want to build or fix

## Steps

1. **Write a clear brief**
   Describe what you want in plain language. Focus on the "what" and "why",
   not the "how". One paragraph is usually enough.

2. **Generate a structured plan**
   ```
   /make-plan <brief>   # Claude
   $make-plan <brief>   # Codex
   ```
   For design-driven features where intent and framing matter, use:
   ```
   /make-plan --framing metacomm <brief>   # Claude
   $make-plan --framing metacomm <brief>   # Codex
   ```

3. **Review the generated plan**
   Check the steps, file list, review log, and any deferred concerns. The plan
   lives in `_output/plans/` and is meant to be read before execution.

4. **Execute the plan**
   ```
   /execute-plan <plan-id>   # Claude
   $execute-plan <plan-id>   # Codex
   ```
   The plan ID is shown in the plan file name (e.g., `plan-0042`).

5. **Run quality checks**
   ```
   /check preflight   # Claude
   $check preflight   # Codex
   ```
   This runs validation and review in one pass.

6. **Fix and re-check**
   If preflight surfaces issues, fix them and run `/check preflight` / `$check preflight` again
   until the output is clean.

## Tips

- Always review the plan before running `/execute-plan` / `$execute-plan` -- especially while
  learning, so you can catch issues before changes happen.
- For larger features, use `/make-plan --roadmap` / `$make-plan --roadmap` to decompose into
  dependency-aware implementation waves.
- Keep briefs short and focused -- one feature per plan.

## Related journeys

- [Solo Designer -- Greenfield](../journeys/journey-solo-designer-greenfield.md)
- [Solo Designer -- Brownfield](../journeys/journey-solo-designer-brownfield.md)
- [Solo Developer](../journeys/journey-solo-developer.md)
- [Small Team Kickoff](../journeys/journey-small-team-kickoff.md)
- [Enterprise Evolution](../journeys/journey-enterprise-evolution.md)
