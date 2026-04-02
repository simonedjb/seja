# Recipe: Onboard a New Team Member

Use this recipe when a new person joins the project and needs a structured learning path.

## Goal

Generate a tailored onboarding plan for a new team member joining the project.

## Prerequisites

- The foundational SEJA framework installed (in the codebase or a project workspace) and project configured via `/seed` + `/design`
- Knowledge of the new member's role and experience level

## Steps

1. **Identify the person's role family**
   - **Builder** -- developer, DevOps engineer
   - **Shaper** -- designer, product manager, analyst
   - **Guardian** -- QA engineer, security specialist, tech lead

2. **Assess their expertise level**
   - **L1 Newcomer** -- 0-2 years of experience
   - **L2 Practitioner** -- 2-5 years
   - **L3 Expert** -- 5-10 years
   - **L4 Strategist** -- 10+ years
   - **L5 Leader** -- tech lead or engineering manager

3. **Run the onboarding skill**
   ```
   /onboarding <role> <level> [name] [--area <focus>]
   ```
   Example:
   ```
   /onboarding builder L2 Alice --area backend
   ```

4. **Review the generated plan**
   The plan includes a 30-60-90 day progression, a recommended first task,
   a learning path, and a support structure (buddy, mentor, check-ins).

5. **Share the plan**
   Hand the plan to the new team member and their assigned buddy or mentor.
   The plan references actual project files and paths, so it stays concrete.

## Tips

- Use `--batch` for onboarding waves:
  `/onboarding --batch "builder L2 Alice --area backend; guardian L3 Carlos"`
- Cross-functional roles use `+` notation:
  `/onboarding builder+guardian L3 Dana`
- The onboarding plan references real project files and conventions, so it
  stays actionable rather than generic.

## Related journeys

- [Small Team Kickoff](../journeys/journey-small-team-kickoff.md)
- [Growing Team](../journeys/journey-growing-team.md)
- [Enterprise Evolution](../journeys/journey-enterprise-evolution.md)
