---
designer_description: "When the reviewer is asked to look at what you built through responsive-design eyes, I'm the checklist that tells it what to watch for -- mobile-first progressive enhancement, breakpoint behaviour, fluid typography, touch-target sizing, responsive images and tables, container queries, and real-device verification across iOS/Android/non-Chromium browsers -- so the layout holds up from the narrowest phone to the widest desktop without horizontal scroll or hinge-collision."
tier: Deep-dive
---

# RESP — Responsive Design

## Essential

- [P0] Is the viewport meta tag present with `width=device-width, initial-scale=1`, and is `user-scalable=no` / `maximum-scale=1` avoided to preserve user zoom capability?
- [P0] Does the layout behave correctly across a representative set of viewport widths (e.g., 320px, 768px, 1280px, 1920px), including at and between defined breakpoints?
- [P0] Does the layout adapt without horizontal scrolling or content overflow?
- [P0] Does the implementation follow a mobile-first approach, progressively enhancing via min-width media queries rather than overriding desktop layouts?
- [P0] Are all interactive elements (swipe gestures, hover-dependent menus, drag handles) adapted for touch input with fallbacks and pointer-type detection?
- [P0] Are touch targets sized to a minimum 44×44 CSS px interactive area (per WCAG 2.5.5), including invisible hit-area expansion for small visual elements such as icon buttons?

## Standard

- [P2] Are breakpoint behaviors tested in E2E tests or visual regression tests?
- [P1] Are fluid typography scales (clamp()-based font sizes) used for readable text across the viewport continuum without abrupt jumps at breakpoints?
- [P1] Are responsive images served with srcset/sizes or the <picture> element for art direction, ensuring appropriate resolutions per breakpoint?
- [P1] Do data-heavy tables use a responsive pattern (horizontal scroll, card reflow, column prioritisation) that preserves readability on narrow viewports?
- [P1] Has the layout been verified on real or emulated devices covering iOS Safari, Android Chrome, and at least one non-Chromium browser, including viewport behavior with browser chrome visible (not just maximized)?
- [P1] Are container queries used where component-level responsiveness is needed, and is `container-type` (and `container-name` where relevant) correctly declared on the appropriate ancestor element?
- [P2] Are print stylesheets defined for content-heavy pages (discussions, exports)?
- [P2] Do print stylesheets strip non-essential UI (navigation, ads, interactive widgets) and apply appropriate page-break rules for multi-page content?
- [P2] Does the layout account for foldable and dual-screen devices by respecting the viewport segments API (env(viewport-segment-*)) to avoid content on the hinge?
- [P1] Are hover and fine-pointer interactions gated behind `@media (hover: hover) and (pointer: fine)`, with appropriate touch/coarse-pointer alternatives provided via `(hover: none)` or `(pointer: coarse)` media features?
- [P1] Do form controls (`input`, `select`, `textarea`, `button`) remain within their container bounds on narrow viewports, using `max-width: 100%` or equivalent box-sizing rules to prevent overflow?
- [P1] Where layout dimensions must account for retractable browser chrome (address bars, navigation bars), are dynamic viewport units (`dvh`, `svh`, `lvh`) used in preference to static `100vh`?
- [P1] Do responsive layout transitions (drawer animations, sidebar collapses, accordion expansions, page transitions) respect `prefers-reduced-motion: reduce` by disabling or replacing them with instant state changes?
- [P2] For projects with RTL language support, are physical CSS properties (`margin-left`, `padding-right`, directional positioning) replaced with logical properties (`margin-inline-start`, `padding-inline-end`, `inset-inline-*`) so responsive layouts adapt correctly to `dir="rtl"` at all breakpoints?

## Deep

- [P3] For HTML email, does the responsive approach degrade gracefully in clients that ignore media queries (Gmail app, Outlook desktop) via fluid-hybrid or spongy techniques?
- [P3] Are fluid layout widths achieved using intrinsic CSS sizing functions (`clamp()`, `min()`, `max()`, Grid `minmax()` with `fr`) rather than purely percentage-based layouts or breakpoint-multiplied fixed widths?
- [P4] For images that must adapt to OS color scheme, are dark-mode variants served via `<picture>` with `<source media="(prefers-color-scheme: dark)">` rather than relying on CSS filter workarounds?
