# RESP — Responsive Design

## Essential

- [P0] Does this work correctly on mobile, tablet, and desktop breakpoints?
- [P0] Does the layout adapt without horizontal scrolling or content overflow?
- [P0] Does the implementation follow a mobile-first approach, progressively enhancing styles via min-width media queries rather than overriding desktop layouts for smaller screens?
- [P0] Are all interactive elements (swipe gestures, hover-dependent menus, drag handles) adapted for touch input with proper fallbacks and pointer-type detection?

## Deep-dive

- [P1] Are touch targets appropriately sized (min 44x44px)?
- [P1] Are breakpoint behaviors tested in E2E tests or visual regression tests?
- [P1] Are fluid typography scales (e.g., clamp()-based font sizes) used to ensure readable text across the full viewport continuum without abrupt jumps at breakpoints?
- [P1] Are responsive images served with srcset/sizes or the <picture> element for art direction, ensuring appropriate resolutions and crops per breakpoint?
- [P1] Do data-heavy tables use a responsive pattern (horizontal scroll container, card reflow, or column prioritisation) that preserves readability on narrow viewports?
- [P1] Has the layout been verified on real devices (or device-accurate emulators) across iOS Safari, Android Chrome, and at least one non-Chromium desktop browser to catch rendering and viewport-unit discrepancies?
- [P1] Are container queries used where component-level responsiveness is needed, avoiding fragile assumptions about the parent layout's viewport width?
- [P2] Are print stylesheets defined for content-heavy pages (discussions, exports)?
- [P2] Do print stylesheets strip non-essential UI (navigation, ads, interactive widgets) and apply appropriate page-break rules for multi-page content?
- [P2] Does the layout account for foldable and dual-screen devices by respecting the viewport segments API or environmental variables (e.g., env(viewport-segment-*)) to avoid content sitting on the hinge/fold?
- [P3] If the content is delivered via HTML email, does the responsive approach degrade gracefully in clients that ignore media queries (e.g., Gmail app, Outlook desktop) using fluid-hybrid or spongy techniques?
