# FRAMEWORK - FIGMA MAKE INTEGRATION

> Guide for teams using Figma Make alongside the SEJA framework.
> Figma Make is an upstream prototype generator; SEJA is the downstream engineering backbone.
> This file documents the handoff protocol, intake checklist, and integration conventions.

---

## Overview

Figma Make generates React code from natural language prompts and visual designs. It excels at rapid visual prototyping but produces monolithic single-file output with no separation of concerns, no test scaffolds, and no CI/CD awareness.

SEJA manages architecture, testing, review, and deployment. The two tools are complementary when connected by a disciplined one-way handoff.

**Core principle**: Code flows from Figma Make into SEJA-managed code, not the other way around. Figma Make is never the source of truth for production code.

---

## Handoff Protocol

Map the Figma Make handoff onto SEJA's existing design-intent lifecycle:

| Lifecycle stage | Figma Make role | SEJA role |
|----------------|-----------------|-----------|
| `design-intent` (working, `STATUS: proposed`) | Prototypes live here. Exploratory, disposable, not production artifacts. | Records the design intent that the prototype validates in `project/product-design-as-intended.md`. |
| `design-intent` (handoff, `STATUS: implemented`) | Handoff trigger. Prototype is approved for implementation. | `/plan` creates an implementation plan. Generated code is decomposed into modular components. |
| `design-intent § Decisions` (`STATUS: established`) | No role. Prototype is superseded by production code. | Decision entries capture the rationale after `/explain spec-drift --promote` Phase 3a/3b. |
| `as-coded § Conceptual Design` | No role. Figma Make output no longer exists. | Production code managed entirely by SEJA. |

### MCP Server for stakeholder review

The Figma MCP Server's "Code to Canvas" feature can push SEJA-managed production code back to Figma as editable layers for stakeholder review. This is a one-way preview -- Figma is not the source of truth.

---

## Intake Checklist

Before any Figma Make output enters the SEJA-managed codebase, verify:

1. **Architectural decomposition** -- Figma Make produces a single file. Decompose into modular components per project architecture standards (layer boundaries, component structure, separation of concerns).

2. **Design token alignment** -- Verify that tokens used in Make Kits (npm packages, Figma variables/styles) match the production design token set. Flag any drift.

3. **Accessibility audit** -- Figma Make does not guarantee A11Y compliance. Audit the generated markup against WCAG requirements (contrast, keyboard navigation, ARIA attributes, semantic HTML).

4. **Test scaffold creation** -- Define component boundaries and create test stubs. Figma Make output has no test hooks or testable isolation. Establish the test structure before integrating.

---

## Feeding SEJA Conventions into Figma Make

Use Figma Make's Attachments feature to attach SEJA reference files to your prompts. This improves the quality of generated code and reduces the decomposition burden.

Recommended attachments:
- `_references/general/coding-standards.md` -- general coding conventions
- `_references/project/standards.md` -- project-specific engineering standards (Backend, Frontend, Testing, i18n); attach the file and focus on the Frontend section
- Project component templates -- existing component files as examples for Figma Make to follow

Figma Make supports these attachment types: PDF, Markdown, TSX, JS, CSS, CSV, JSON, images, and SVGs.

---

## MCP Server Integration

Treat the Figma MCP Server as an optional convenience layer, not a load-bearing dependency.

**Do**:
- Use it to quickly read Figma designs into Claude Code context
- Use it to push production UI previews back to Figma for stakeholder review
- Build workflows that function without it (manual export/import as fallback)

**Do not**:
- Depend on it for critical workflow steps
- Assume stable availability (rate limits apply; protocol may evolve)
- Use it as a bidirectional sync mechanism for production code

The MCP Server launched in February 2026 and is still maturing. Any integration should degrade gracefully when the server is unavailable or rate-limited.

---

## Token Sync Pipeline

When both Figma Make and the SEJA-managed codebase consume design tokens:

1. **Single source of truth** -- Maintain one canonical token file (e.g., `tokens.json` or a Figma Tokens plugin export) that feeds both systems.

2. **Figma side** -- Import tokens via Make Kits (Figma library styles, variables, and npm packages from the design system).

3. **Code side** -- Import the same token set via CSS custom properties, design token packages, or the project's styling conventions.

4. **Drift monitoring** -- Periodically compare the token values in both systems. Flag discrepancies during code review (VIS perspective) or via automated checks.
