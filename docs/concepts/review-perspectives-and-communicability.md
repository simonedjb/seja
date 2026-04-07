# Review Perspectives and Communicability

## Why multiple perspectives?

A single code review pass tends to focus on whatever the reviewer knows best -- security experts catch vulnerabilities, UX designers catch usability issues, performance engineers catch bottlenecks. But a single person rarely catches everything. SEJA formalizes this insight by defining 16 **review perspectives**, each representing a distinct domain of concern. When reviewing code, plans, or design decisions, the framework evaluates against a relevant subset of these perspectives to ensure nothing critical is missed.

## The 16 perspectives

SEJA organizes its perspectives into two groups:

### Engineering perspectives (11)

| Tag | Name | What it covers |
|-----|------|----------------|
| SEC | Security | Authentication, input validation, secrets management, dependency vulnerabilities |
| PERF | Performance | N+1 queries, unbounded loops, index usage, caching, bundle size |
| DB | Database | Schema migrations, backward compatibility, idempotency, constraints |
| API | API Design | RESTful conventions, route consistency, request/response contracts |
| ARCH | Architecture | Layer boundaries, separation of concerns, dependency direction |
| DX | Developer Experience | Readability, conventions, documentation, error messages for developers |
| I18N | Internationalization | Translation keys, locale support, pluralization, RTL layouts, date/number formats |
| TEST | Testability | Test coverage, new test needs, mocking strategy, test isolation |
| OPS | Operations / DevOps | Environment parity, logging, monitoring, deployment, configuration |
| COMPAT | Compatibility | API contract stability, schema evolution, browser/version support |
| DATA | Data Integrity & Privacy | PII handling, GDPR compliance, validation, audit trails |

### Design perspectives (5)

| Tag | Name | What it covers |
|-----|------|----------------|
| UX | User Experience | User flows, feedback, error handling, navigation, discoverability |
| A11Y | Accessibility | WCAG compliance, contrast, keyboard navigation, screen readers, focus management |
| VIS | Visual Design | Design system consistency, CSS conventions, spacing, typography |
| RESP | Responsive Design | Mobile/tablet/desktop breakpoints, fluid layouts, touch targets |
| MICRO | Microinteractions | Hover/focus/active states, transitions, loading indicators, animations |

## Priority tiers

Each perspective contains questions organized into two tiers:

- **Essential** -- 3 to 7 questions at P0 (critical/blocking) priority. These must always be evaluated when the perspective is selected. They represent the minimum bar.
- **Deep-dive** -- 8 to 12 questions spanning P1 through P4 priority. These are loaded for thorough reviews, when the perspective is the primary focus, or when the context budget allows.

The priority levels are:

| Level | Meaning |
|-------|---------|
| P0 | Critical -- blocking. Must be addressed before merging. |
| P1 | Important -- should be addressed in this iteration. |
| P2 | Desirable -- improves quality but can be deferred. |
| P3 | Informational -- worth noting for future reference. |
| P4 | Nice-to-have -- only if time permits. |

When time or context is constrained, reviewers focus on P0 and P1 questions first.

## Conflict resolution

When two perspectives recommend conflicting approaches, SEJA follows explicit resolution rules rather than leaving it to individual judgment:

1. **SEC wins by default.** Security concerns override performance, convenience, or developer experience unless the user explicitly accepts the risk. For example, if PERF suggests caching sensitive data for speed but SEC advises against it, the security concern takes priority.

2. **A11Y is non-negotiable.** Accessibility requirements are never traded off against visual design, performance, or development convenience. If VIS wants a low-contrast design element but A11Y requires higher contrast, accessibility wins.

3. **Document the trade-off.** When one perspective is deferred in favor of another, both the chosen approach and the deferred concern are recorded with rationale. This creates transparency about what was considered and why.

4. **Ask when unclear.** If two perspectives of equal standing conflict (for example, PERF vs DX), the framework asks the user for guidance rather than making an assumption.

## The connection to communicability

The perspectives are not just checklists -- several of them are grounded in semiotic engineering's analytical tools for evaluating how well software communicates with its users.

### CEM utterances in UX and DX

The UX perspective includes questions derived from the **Communicability Evaluation Method (CEM)**, a research taxonomy of 13 specific communicative breakdown types. Each "utterance" represents something a user might say (or think) when the designer's message fails to get through:

- **Complete failures**: "I give up." (the user abandons the goal entirely) and "Looks fine to me." (the user thinks they succeeded but actually has not -- the most insidious breakdown).
- **Temporary failures from halted sense-making**: "Where is it?" (cannot find the control), "What happened?" (cannot see the outcome), "What now?" (no clear next step).
- **Temporary failures from wrong approach**: "Where am I?" (wrong context or mode), "Oops!" (immediate slip), "I can't do it this way." (abandoning a whole line of reasoning).
- **Clarification-seeking**: "What's this?" (probing an element), "Help!" (invoking explicit help), "Why doesn't it?" (repeating failed steps to understand).

When reviewing a UX flow, these utterances help reviewers move beyond vague "is it usable?" questions to precise diagnostics: "Could a user plausibly face this screen and think 'What now?' because no element suggests a clear next step?"

The DX perspective applies similar reasoning to developer-facing interfaces -- APIs, CLIs, configuration files -- asking whether developers might experience analogous breakdowns.

### Sign classes in UX

The UX perspective also uses the concept of **three classes of interface signs** from semiotic engineering:

- **Static signs** -- elements that are always present and do not change (labels, icons, layout structure). They convey the system's available vocabulary.
- **Dynamic signs** -- elements that change in response to user actions or system events (state transitions, animations, data updates). They convey the system's behavior.
- **Metalinguistic signs** -- elements that explain other signs (tooltips, help text, onboarding tutorials). They convey the designer's explanation of the system.

Reviewing against these categories helps ensure that each type of sign is doing its communicative job. For instance, if a feature relies heavily on dynamic signs (things change when you interact) but has no metalinguistic signs (nothing explains what the changes mean), users may struggle to build an accurate mental model.

### CDN dimensions in API

The API perspective incorporates **Cognitive Dimensions of Notations (CDN)**, a framework for evaluating how well a notation system (like an API) supports the people who use it. Key dimensions include:

- **Consistency** -- do similar operations use similar patterns?
- **Role-expressiveness** -- can a developer infer purpose from names alone?
- **Error-proneness** -- does the design invite mistakes?
- **Hidden dependencies** -- are relationships between resources visible or buried?
- **Viscosity** -- how many changes are needed to make a single logical modification?
- **Closeness of mapping** -- does the API vocabulary match the user's domain language?

These dimensions help API reviewers go beyond "does it work?" to "does it communicate its design intent to the developers who will use it?"

## How perspectives are used in practice

Perspectives appear throughout SEJA's workflow:

- **`/check review`** -- Selects and applies relevant perspectives to code changes, producing a structured review report.
- **`/plan` review phase** -- After generating a plan, the plan-reviewer agent evaluates it against perspectives appropriate to the plan's scope. The framework provides default perspective shortlists based on the plan's prefix (for example, a frontend feature plan defaults to UX, A11Y, VIS, RESP, I18N, TEST, and MICRO).
- **`/advise`** -- When answering architectural or design questions, the advisory-reviewer can draw on perspectives to provide structured analysis.
- **`/check preflight`** -- Runs parallel perspective-based checks before merging.

To keep context usage manageable, perspectives are loaded in two stages: first the compact index (a summary table, under 600 tokens), then only the 4 to 6 perspective files relevant to the current task. See [Context Budget and References](context-budget-and-references.md) for more on this strategy.

For the broader framework motivation and how communicability connects to the design-intent lifecycle, see [What Is SEJA and Why Does It Exist?](what-is-seja.md) and [The Design-Intent Lifecycle](design-intent-lifecycle.md).
