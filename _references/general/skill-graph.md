# FRAMEWORK - SKILL RELATIONSHIP GRAPH

> Directed relationships between skills, used by `/post-skill` to suggest contextual next steps.
> Each skill maps to 1-2 suggested follow-up skills with a short reason.
> Last revised: 2026-03-28 (consolidated skills: /inventory->/advise, /roadmap->/plan, /plan-user-test->/check, /spec->/explain)

## Usage

After a skill completes, `/post-skill` reads this file and looks up the completed skill in the "After" column. If found, it displays the suggested skill(s) and reason as a tip to the user.

## Relationships

### Planning & Execution

| After | Suggest | Reason |
| --- | --- | --- |
| `/plan` | `/implement` | Ready to execute this plan? |
| `/plan --light` | `/implement` | Ready to execute this proposal? |
| `/implement` | `/check validate`, `/check review` | All checks run by default unless --skip-checks was used. |
| `/plan --roadmap` | `/implement` | Ready to execute items from the roadmap? |
| `/explain spec-drift` | `/plan` | Specs analyzed — ready to plan next steps? |

### Analysis & Review

| After | Suggest | Reason |
| --- | --- | --- |
| `/advise` | `/plan` | Want to turn these recommendations into a plan? |
| `/explain` | `/advise` | Have questions about what you just learned? |
| `/check review` | `/update-tests` | Want to add tests for the reviewed code? |
| `/check validate` | `/plan` | Found issues? Plan and fix them. |
| `/check validate` | `/check health` | Also check framework health? |
| `/check smoke` | `/plan` | Found failures? Plan and fix them. |
| `/check health` | `/plan` | Found issues? Plan and fix them. |
| `/check preflight` | `/check review` | Want a detailed code review of the changes? |
| `/advise --inventory` | `/explain` | Want a deeper explanation of any of these? |
| `/check telemetry` | `/advise` | Want to discuss usage patterns? |

### Code & Tests

| After | Suggest | Reason |
| --- | --- | --- |
| `/generate-script` | `/check validate` | Run validations to check the new script? |
| `/generate-script` | `/help --browse` | Regenerate the skill map to include the new script? |
| `/update-tests` | `/check validate` | Run all checks to make sure tests pass? |
| `/check test-plan` | `/communication` | Share the test plan with stakeholders? |

### Utilities

| After | Suggest | Reason |
| --- | --- | --- |
| `/communication` | `/onboarding` | Need to onboard someone to the project too? |
| `/onboarding` | `/communication` | Want to generate stakeholder material as well? |
| `/help` | `/help --browse` | Browse all available skills? |
| `/help --browse` | `general/recipes.md` | See common multi-skill workflow recipes |
| `/seed` | `general/getting-started.md` | New to SEJA? Follow the getting-started guide |
| `/design` | `/plan --roadmap` | Project configured — generate a development roadmap? |
| `/qa-log` | `/advise` | Have more questions to explore? |
