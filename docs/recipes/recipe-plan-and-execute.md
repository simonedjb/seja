# Recipe: Plan and Execute a Change

Use this recipe when you have a clear idea of what to build and want a structured approach.

## Goal

Plan a feature, bug fix, or refactor, then execute it with quality checks.

**Total time: ~10-20 minutes** (varies with plan complexity)

## Prerequisites

- SEJA framework seeded and project configured via `/seed` + `/design`
- A clear idea of what you want to build or fix

## Steps

1. **Write a clear brief** (~2 min)
   Describe what you want in plain language. Focus on the "what" and "why",
   not the "how". One paragraph is usually enough. For example: "Add a user profile page with avatar upload and bio editing."

2. **Generate a structured plan** (~2 min)
   ```
   /plan <brief>
   ```
   For design-driven features where intent and framing matter, use:
   ```
   /plan --framing metacomm <brief>
   ```

   <details>
   <summary>For designers</summary>

   Focus your brief on describing the user experience -- what the user sees, does, and feels. The framework translates your description into concrete steps. Use `--framing metacomm` when the intent behind the design matters as much as the feature itself.

   </details>

   <details>
   <summary>For developers</summary>

   The generated plan in `_output/plans/` includes file paths, dependency ordering between steps, verification criteria, and traceability references. Each step lists the files to create or modify. Use `--framing metacomm` to include metacommunication context from `project/design-intent-to-be.md`.

   </details>

3. **Review the generated plan** (~2 min)
   Check the steps, file list, review log, and any deferred concerns. The plan
   lives in `_output/plans/` and is meant to be read before execution.

   Example excerpt from a generated plan:

   ```markdown
   ## Steps
   1. Create `src/pages/ProfilePage.tsx` with avatar and bio components
      Files: src/pages/ProfilePage.tsx, src/components/AvatarUpload.tsx
      Traces: REQ-UX-003
   2. Add profile API endpoint for avatar upload
      Files: src/api/routes/profile.ts, src/api/handlers/upload.ts
   3. Write unit tests for profile page and upload handler
      Files: src/__tests__/ProfilePage.test.tsx
   ```

4. **Execute the plan** (~5-15 min)
   ```
   /implement <plan-id>
   ```
   The plan ID is shown in the plan file name (e.g., `plan-0042`).
   Execution automatically runs all quality checks at the end (validate,
   review, tests). Critical issues are fixed before the plan closes;
   non-critical ones are listed as deferred. Use `--skip-checks` to opt out
   for documentation-only or low-risk plans.

   <details>
   <summary>For designers</summary>

   You do not need to do anything during execution. The framework builds what the plan describes and then checks its own work. When it finishes, review the result to confirm it matches your intent.

   </details>

   <details>
   <summary>For developers</summary>

   Before execution, the implement skill creates a `pre-plan-<id>` rollback branch from HEAD. It then executes steps in dependency order, generates tests per step, and runs a quality gate (validate + code review + tests). In auto mode, critical review findings trigger a bounded generator-critic retry loop.

   </details>

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
