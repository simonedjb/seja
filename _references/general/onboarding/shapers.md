# SHP — Shapers

> Product managers, UX/UI designers, data analysts, and others who define what gets built and how.

## Roles

- Product manager / Product owner
- UX designer
- UI designer
- UX researcher
- Data analyst / Business analyst
- Content strategist

## Layer 1 — Role-Specific Onboarding Content

### Essential (all Shapers must cover)

- **Conceptual design and metacommunication**: The unified as-coded implementation state and the design intent documents (`project/product-design-as-coded.md` with `## Conceptual Design` and `## Metacommunication` H2 sections, `project/product-design-as-intended.md`). These capture the system's entity model, user roles, permissions, interaction patterns, and the designer's intent as expressed through the system -- who the user is, what they need, and why the system works this way.
- **User personas and journey maps**: Who uses the system, what their goals are, and how they move through key workflows.
- **Design system and component library**: Visual language, design tokens, reusable components, interaction patterns.
- **Product roadmap and priorities**: Current and upcoming work, strategic goals, how features are prioritized. Use `/plan --roadmap` output if available.
- **AI-assisted design workflow**: How to use AI tools (like Claude Code with the skill system) to explore the codebase, validate design decisions, and generate explanations without needing to read code directly.

### Deep-dive (load for thorough onboarding or when Shaper is the primary role)

- **Analytics and metrics**: Key performance indicators, how they're tracked, dashboards for monitoring user behavior.
- **User research findings**: Past usability studies, survey results, support ticket patterns, A/B test outcomes.
- **Accessibility requirements**: WCAG compliance level, assistive technology support, accessibility review process.
- **Internationalization**: Supported locales, translation workflow, cultural considerations.
- **Competitive landscape**: How the product positions itself, key differentiators, known gaps.
- **Stakeholder map**: Who influences product decisions, approval workflows, escalation paths.

## Recommended First Tasks by Level

| Level | First Task | Goal |
|-------|-----------|------|
| L1 Contributor | Conduct a heuristic evaluation (newcomer) or write a feature brief (practitioner) | Learn the product through a critical lens |
| L2 Expert | Review and critique the conceptual design document | Understand design intent, propose refinements |
| L3 Leader | Map cross-feature dependencies (Strategist) or lead a design review session (Manager) | Identify systemic design issues or understand team norms |

## Key Reference Files

- `project/product-design-as-coded.md § Conceptual Design` (current system design)
- `project/product-design-as-intended.md` (unified working intent, Decisions log, and metacommunication; Human (markers) classification)
- `project/product-design-as-coded.md § Metacommunication` (current metacommunication record)
- `general/shared-definitions.md` (project terminology)
- `general/review-perspectives/ux.md` (UX review standards)
- `general/review-perspectives/a11y.md` (accessibility standards)
- `general/review-perspectives/vis.md` (visual design standards)
