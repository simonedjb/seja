---
diataxis: how-to
freshness: release-bound
last-reviewed: 2026-04-19
---

# Which communicative skill?

Use this page when you want to produce something communicative and are not sure which of `/document`, `/onboard`, `/communicate`, or `/explain` to invoke. Pick the row whose audience matches the person you are writing for; the Skill column names the single command to run.

> Terminology note: `/onboard` and `/communicate` were previously named `/onboarding` and `/communication` before the v0.x harness simplification.

## Decision table

| Audience | Artifact kind | Example question | Skill | Output location |
|----------|---------------|------------------|-------|-----------------|
| Future maintainer (technical) | Project documentation -- README, API reference, DRR, contextual help, help center | "How does this module work, and what were the trade-offs?" | `/document` | `docs/` or `project/` |
| New team member (role family and expertise level) | Tailored onboarding plan with role-conditional reading order and first-week tasks | "What should my first week look like as a BLD L2?" | `/onboard` | `_output/onboarding-plans/` |
| Stakeholder outside the team (non-technical, audience-segment specific) | Tailored material for EVL, CLT, USR, or ACD | "What do I tell the CTO about our architecture and progress?" | `/communicate` | `_output/communication/` |
| Invoking developer (yourself, wanting to understand) | Explanation of behavior, code, data model, architecture, or spec drift | "Why does the pre-skill hook fire twice on first run?" | `/explain` | `_output/explained-behaviors/`, `_output/explained-code/`, `_output/explained-data-model/`, `_output/explained-architecture/` |

## When in doubt

If you are writing for the system itself -- code, diagrams, glossaries, help that ships alongside the UI -- reach for `/document`. If you are writing for a person, pick based on their relationship to the project: a new member joining becomes `/onboard`, someone outside the team becomes `/communicate`, and yourself (wanting to understand something, not produce something for others) becomes `/explain`.

If two rows feel plausible, the audience test breaks the tie: `/document` writes to a future maintainer who will read the docs alongside the code, while `/communicate` writes to a stakeholder who will read the material in isolation from the code. The same architectural fact is shaped very differently for the two audiences, which is why the skills are separate.

## What to read next

- [team-and-stakeholders.md](team-and-stakeholders.md) -- step-by-step walkthroughs for `/onboard` and `/communicate`, with quick-reference workflow sequences.
- [plan-and-execute.md](plan-and-execute.md) -- workflow sequences that chain communicative skills with planning and validation.
- [concepts.md -- Harness lifecycle](../concepts.md#harness-lifecycle) -- where the communicative skills sit in the canonical loop (after `/check`, before `/reflect`).
