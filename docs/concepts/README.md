# Concepts

These pages explain the ideas and design decisions behind SEJA. They answer *why* questions: why the framework exists, why it works the way it does, and why certain trade-offs were made.

New to SEJA? Start with [What Is SEJA](what-is-seja.md) for the motivation, then pick the pages most relevant to your role.

## For everyone

These pages cover the foundational ideas that matter regardless of whether you work primarily in design or development:

- [What Is SEJA and Why Does It Exist?](what-is-seja.md) -- The semiotic engineering motivation, the problem SEJA solves, and how it differs from generic coding assistants.
- [The Design-Intent Lifecycle](design-intent-lifecycle.md) -- The three-layer model (to-be, as-is, established) for tracking how design intent flows from vision to validated implementation.
- [Review Perspectives and Communicability](review-perspectives-and-communicability.md) -- The 16 review perspectives, priority tiers, conflict resolution, and the connection to communicability evaluation.

## Developer-primary

These pages go deeper into the framework's technical architecture:

- [Skills, Agents, and the Execution Pipeline](skills-agents-pipeline.md) -- What skills and agents are, and the full pre-skill / execution / post-skill pipeline that governs every invocation.
- [Context Budget and References](context-budget-and-references.md) -- How SEJA manages LLM context limits with budget tiers, eager/lazy loading, and two-stage perspective loading.
- [Extending the Framework](extending-the-framework.md) -- Extension points for custom skills, perspectives, agents, and rules, plus governance requirements.
