# FRAMEWORK - SKILL RELATIONSHIP GRAPH

> Directed relationships between skills, used by `/post-skill` to suggest contextual next steps.
> Each skill maps to 1-2 suggested follow-up skills with a short reason.
> Maintained as part of the SEJA framework. Regenerate the visual skill map with `generate_skill_map.py`.

## Usage

After a skill completes, `/post-skill` reads this file and looks up the completed skill in the "After" column. If found, it displays the suggested skill(s) and reason as a tip to the user.

## Relationships

### Planning & Execution

| After | Suggest | Reason |
| --- | --- | --- |
| `/plan` | `/implement` | Ready to implement this plan? |
| `/plan --light` | `/implement` | Ready to implement this proposal? |
| `/implement` | `/check validate`, `/check review`, `/check preflight` | All checks run by default unless --skip-checks was used. |
| `/implement` | `/document` | Update documentation for the changes? |
| `/implement` | `/pending` | Review pending actions created by this implementation |
| `/implement` | `/reflect` | Surface patterns across recent skill runs (non-prescriptive) |
| `/plan --roadmap` | `/implement` | Ready to implement items from the roadmap? |
| `/explain spec-drift` | `/plan` | Specs analyzed -- ready to plan next steps? |
| `/explain spec-drift` | `/design` | Drift indicates intent has evolved -- update the project design |
| `/explain spec-drift` | `/pending` | Address pending actions surfaced by the drift check |
| `/pending` | `/explain spec-drift --promote` | Next logical step after addressing pending curation items (generates a Decision proposal for promotion candidates) |
| `/explain spec-drift --promote` | `/explain spec-drift --promote --apply-markers plan-<id>` | Decision proposal drafted -- after you apply the prose, flip the STATUS markers |
| `/pending` | `/implement` | Next logical step after reviewing pending review items |

### Analysis & Review

| After | Suggest | Reason |
| --- | --- | --- |
| `/advise` | `/plan`, `/plan --roadmap` | Want to turn these recommendations into a plan? |
| `/explain` | `/advise` | Have questions about what you just learned? |
| `/check review` | `/plan` | Want to plan fixes for the review findings? |
| `/check validate` | `/plan` | Found issues? Plan and fix them. |
| `/check validate` | `/check health` | Also check framework health? |
| `/check validate` | `/pending` | Check and address outstanding pending actions |
| `/check validate` | `/reflect` | After quality checks, surface patterns across recent runs |
| `/check smoke` | `/plan` | Found failures? Plan and fix them. |
| `/check health` | `/plan` | Found issues? Plan and fix them. |
| `/check preflight` | `/check review` | Want a detailed code review of the changes? |
| `/advise --inventory` | `/explain` | Want a deeper explanation of any of these? |
| `/check telemetry` | `/advise` | Want to discuss usage patterns? |
| `/check telemetry` | `/reflect` | Surface descriptive patterns over the last 30 days? |
| `/reflect` | `/advise` | Want a prescriptive take on any pattern surfaced here? |
| `/reflect` | `/plan` | Want to turn a surfaced pattern into new work? |

### Code & Tests

| After | Suggest | Reason |
| --- | --- | --- |
| `/check test-plan` | `/communication` | Share the test plan with stakeholders? |

### Framework maintenance

| After | Suggest | Reason |
| --- | --- | --- |
| `/upgrade` | `/check health` | Verify framework health after upgrading |
| `/upgrade` | `/explain spec-drift` | Re-run spec drift after framework upgrade to catch changed conventions |

### Utilities

| After | Suggest | Reason |
| --- | --- | --- |
| `/document` | `/check docs` | Validate documentation consistency? |
| `/communication` | `/onboarding` | Need to onboard someone to the project too? |
| `/onboarding` | `/communication` | Want to generate stakeholder material as well? |
| `/help` | `/help --browse` | Browse all available skills? |
| `/help --browse` | `docs/how-to/recipes.md` | See common multi-skill workflow recipes |
| `/seed` | `/design` | New project: configure project design (stack, conventions, domain model) after seeding |
| `/seed` | `general/getting-started.md` | New to SEJA? Follow the getting-started guide |
| `/design` | `/plan --roadmap` | Project configured -- generate a development roadmap |
| `/design` | `/plan` | Plan your first feature against the new project design |
| `/design` | `/pending` | Baseline periodic triggers for the new project |
| `/qa-log` | `/advise` | Have more questions to explore? |
