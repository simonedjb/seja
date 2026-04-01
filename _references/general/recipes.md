# FRAMEWORK - WORKFLOW RECIPES

> A cookbook of common multi-skill workflows. Each recipe chains two or more
> skills into a repeatable sequence you can follow step by step.
>
> For the full skill relationship map and post-skill suggestions, see
> `skill-graph.md` in this directory.

---

### 1. Add a New Feature

**When to use**: You have a feature request or idea and want to go from concept to working code.

**Steps**:
1. `/advise` -- explore the design space; get recommendations on approach and trade-offs
2. `/plan` -- turn the chosen approach into a step-by-step implementation plan
3. `/implement` -- execute the plan to produce working code
4. `/check validate` -- run validations to confirm nothing is broken

**Tip**: For large features, run `/plan --roadmap` first to break work into smaller plans.

---

### 2. Fix a Bug

**When to use**: You have a bug report and need a quick diagnosis-to-fix cycle.

**Steps**:
1. `/advise` -- describe the symptom; get analysis of likely root causes
2. `/plan --light` -- create a lightweight proposal for the fix
3. `/implement` -- apply the fix
4. `/check validate` -- verify the fix and ensure no regressions

**Tip**: If the bug is in test-covered code, `/implement` will automatically generate tests when the plan step has a non-N/A Tests field.

---

### 3. Review and Improve Existing Code

**When to use**: You want to improve code quality, reduce complexity, or refactor a module.

**Steps**:
1. `/check review` -- get a detailed code review with actionable findings
2. `/plan` -- create a plan to address the review findings
3. `/implement` -- execute the improvements

**Tip**: Use `/check review --perspective deep-dive` for a more thorough analysis.

---

### 4. Onboard a New Team Member

**When to use**: Someone is joining the team and needs a structured ramp-up path.

**Steps**:
1. `/onboarding <role> <level>` -- generate a tailored onboarding plan (e.g., `/onboarding BLD L2`)
2. Share the generated plan with the new team member
3. `/communication CLT` -- optionally generate a client-facing intro if the member is client-visible

**Tip**: Role families are BLD (builders), SHP (shapers), and GRD (guardians). Levels range from L1 (novice) to L5 (expert).

---

### 5. Prepare a Stakeholder Update

**When to use**: You need to report progress, metrics, or decisions to a specific audience.

**Steps**:
1. `/check telemetry` -- review recent activity, plan completion, and usage patterns
2. `/communication <audience>` -- generate tailored material (e.g., `/communication EVL` for evaluators)

**Tip**: Audience segments include EVL (evaluators), CLT (clients), USR (users), and ACD (academics).

---

### 6. Upgrade the Framework

**When to use**: A new version of the SEJA framework is available and you want to pull updates.

**Steps**:
1. `/upgrade` -- pull framework file updates while preserving project-specific files
2. `/check health` -- verify framework integrity after the upgrade
3. Review the changes and resolve any conflicts

**Tip**: Run `/explain spec-drift` afterward if you suspect design specs have diverged.

---

### 7. Explain a Confusing Part of the Codebase

**When to use**: You or a teammate need to understand unfamiliar code or architecture.

**Steps**:
1. `/explain code` -- get an explanation of specific code with diagrams and analogies
2. `/explain architecture` -- zoom out to understand how the component fits into the system

**Tip**: Follow up with `/advise` if the explanation raises design questions.

---

### 8. Run a Design Review

**When to use**: You want structured feedback on the current design direction before committing to a roadmap.

**Steps**:
1. `/advise` -- use the council format to get multi-perspective design feedback
2. `/plan --roadmap` -- translate the agreed direction into a prioritized roadmap

**Tip**: Combine with `/explain spec-drift` first if design specs may be out of sync.

---

### 9. Generate and Validate Tests

**When to use**: You want to add or update tests for a module and confirm they pass.

**Steps**:
1. `/plan` -- create a plan with Tests fields specifying what to test
2. `/implement` -- execute the plan; test generation happens automatically per step
3. `/check validate` -- run all checks to make sure the new tests pass

**Tip**: Use `/check review` first to identify which areas most need test coverage.

---

### 10. Check Documentation Freshness

**When to use**: You suspect docs are stale or inconsistent with the codebase.

**Steps**:
1. `/check docs` -- run the documentation consistency checker (path liveness, terminology, etc.)
2. Fix any findings reported by the checker
3. `/check validate` -- confirm fixes did not introduce new issues

**Tip**: Run this recipe after major refactors that rename files or move modules.
