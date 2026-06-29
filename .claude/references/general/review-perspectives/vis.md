---
designer_description: "When the reviewer is asked to look at what you built through visual-design eyes, I'm the checklist that tells it what to watch for -- design-system consistency, spacing and typographic scale, semantic color tokens for light and dark themes, grid alignment, icon-family coherence, and pixel-perfect rendering across densities -- so the surface you ship feels like one designed product instead of a stitched-together patchwork."
tier: Deep-dive
---

# VIS -- Visual Design

## Essential

- [P0] Is the visual treatment consistent with the project's design system and CSS conventions?
- [P0] Does every visual element (logo usage, palette, typeface) align with brand guidelines, with deviations explicitly approved?
- [P0] Does the dark mode implementation use semantic color tokens (not hard-coded values), declare `color-scheme: light dark` on `:root`, and pass contrast checks independently from the light theme?
- [P0] Is the layout built on a consistent grid with defined columns, gutters, and breakpoint behavior preventing alignment drift?

## Standard

- [P1] Are spacing, typography, and color usage following established patterns?
- [P1] Does it maintain visual hierarchy and readability?
- [P1] Is there a documented design token inventory (colors, spacing, typography) beyond the CSS framework config?
- [P1] Are icon sizes, weights, and spacing consistent across the application?
- [P1] Are typographic scales fluid across breakpoints (using `clamp()` or equivalent), with line heights, letter-spacing, optical sizing, and font fallbacks defined systematically?
- [P1] Do color combinations meet WCAG contrast, and is the palette built on a perceptually uniform model (OKLCH/CIELAB) to avoid hue shifts at different lightness levels?
- [P1] Are design tokens structured in layers (global -> alias -> component) with a single source of truth feeding both design tools and code?
- [P1] Does the component library follow a deliberate atomic hierarchy (atoms as smallest functional units, molecules as simple functional groups, organisms as discrete sections) with no collapsed or inverted levels that would make components monolithic or non-reusable?
- [P1] Does a machine-readable token source file (e.g., conforming to the W3C Design Tokens Format 2025.10) exist as the single canonical artifact, enabling automated consumption by CI pipelines, design tools, and code generators without manual re-entry?
- [P2] Are icons drawn on a uniform pixel grid with consistent stroke widths and optical sizing so they read as one family?
- [P2] Do transitions and animations follow a unified easing/duration set, restrict movement to compositor-friendly properties (`opacity`, `transform`), avoid triggering reflow, and respect `prefers-reduced-motion`?
- [P2] Have final renders been compared pixel-for-pixel against design specs at 1x/2x densities with sub-pixel rounding and asset crispness verified?
- [P2] Do data visualizations use colorblind-safe palettes, legible labels, appropriate chart types, and consistent visual encoding across all charts?
- [P2] Is the pattern library actively synchronized with the production codebase (not a snapshot or manual export), and does it document pattern lineage -- which sub-patterns compose each component and where each component is employed -- so that changes propagate predictably?

## Deep

- [P3] Have perceptual uniformity assumptions been validated across the full lightness range used by alias tokens (not just at defined swatch values), ensuring that hover states, disabled states, and gradient steps do not produce visually jarring jumps despite using a nominally uniform color model?
- [P3] Has the design system been stress-tested with extreme content variations -- very long strings, missing images, zero-item states, and maximum-item counts -- at every atomic level (atom, molecule, organism, template), and do all visual properties (alignment, overflow, truncation, spacing) degrade gracefully?
- [P4] Does the icon system document optical sizing corrections -- separate path variants or compensation tables for each canonical size (e.g., 16px, 24px, 48px) with adjusted stroke weights and simplified geometry -- rather than relying solely on mathematical scaling of a single master icon?
