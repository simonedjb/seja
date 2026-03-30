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

- **Conceptual design**: The as-is and to-be conceptual design documents (`project/conceptual-design-as-is.md`, `project/conceptual-design-to-be.md`). These capture the system's entity model, user roles, permissions, and interaction patterns.
- **Metacommunication message**: The designer's intent as expressed through the system (`project/metacomm-as-is.md`, `project/metacomm-to-be.md`). Understanding who the user is, what they need, and why the system works this way.
- **User personas and journey maps**: Who uses the system, what their goals are, and how they move through key workflows.
- **Design system and component library**: Visual language, design tokens, reusable components, interaction patterns.
- **Product roadmap and priorities**: Current and upcoming work, strategic goals, how features are prioritized. Use `/make-plan --roadmap` output if available.
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
| L1 | Conduct a heuristic evaluation of one user flow | Learn the product through a critical lens |
| L2 | Write a feature brief for an upcoming item | Learn the product language, priorities, and constraints |
| L3 | Review and critique the conceptual design document | Understand design intent, propose refinements |
| L4 | Map cross-feature dependencies and conflicts | Identify systemic design issues |
| L5 | Lead a design review session | Understand team norms, decision-making process |

## Key Reference Files

- `project/conceptual-design-as-is.md` (current system design)
- `project/conceptual-design-to-be.md` (target system design)
- `project/metacomm-as-is.md` (current metacommunication record)
- `project/metacomm-to-be.md` (target metacommunication record)
- `general/shared-definitions.md` (project terminology)
- `general/review-perspectives/ux.md` (UX review standards)
- `general/review-perspectives/a11y.md` (accessibility standards)
- `general/review-perspectives/vis.md` (visual design standards)
