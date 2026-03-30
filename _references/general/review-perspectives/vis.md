# VIS — Visual Design

## Essential

- [P0] Is the visual treatment consistent with the project's design system and CSS conventions?
- [P0] Does every visual element (logo usage, color palette, typeface selection) align with the brand guidelines, and are deviations explicitly approved? *(Brand identity designer)*
- [P0] Does the dark mode implementation use semantic color tokens (not hard-coded values) and pass contrast checks independently from the light theme? *(Dark mode / theming specialist)*

## Deep-dive

- [P1] Are spacing, typography, and color usage following established patterns?
- [P1] Does it maintain visual hierarchy and readability?
- [P1] Is there a documented design token inventory (colors, spacing, typography) beyond the CSS framework config?
- [P1] Are icon sizes, weights, and spacing consistent across the application?
- [P1] Are typographic scales, line heights, letter-spacing, and font fallback stacks defined systematically to ensure readability and hierarchy across all breakpoints? *(Typography specialist)*
- [P1] Do color combinations meet WCAG contrast requirements, and is the palette built on a perceptually uniform model (e.g., OKLCH/CIELAB) to avoid hue shifts at different lightness levels? *(Color theory / palette designer)*
- [P1] Is the layout built on a consistent grid or spacing system with clearly defined columns, gutters, and breakpoint behavior that prevents alignment drift? *(Layout / grid systems expert)*
- [P1] Are design tokens structured in layers (global → alias → component) with clear naming conventions and a single source of truth that feeds both design tools and code? *(Design token architect)*
- [P2] Are icons drawn on a uniform pixel grid with consistent stroke widths, optical sizing, and metaphor clarity so they read as a single family? *(Iconography designer)*
- [P2] Do transitions and animations follow a unified easing and duration curve set, avoid layout thrashing, and respect the `prefers-reduced-motion` media query? *(Motion / animation designer)*
- [P2] Have final renders been compared pixel-for-pixel against design specs at 1x and 2x densities, with sub-pixel rounding, anti-aliasing, and asset crispness verified? *(Visual QA / pixel-perfection engineer)*
- [P2] Do data visualizations use colorblind-safe palettes, legible axis labels, appropriate chart types for the data shape, and consistent visual encoding across all charts? *(Data visualization designer)*
