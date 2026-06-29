---
designer_description: "When the reviewer is asked to look at what you built through microinteractions eyes, I'm the checklist that tells it what to watch for -- hover/focus/active states, intermediate loading/skeleton/optimistic/error/empty frames, prefers-reduced-motion support, GPU-composited animations within frame budget, screen-reader-perceivable state changes, and purposeful feedback that matches the weight of the action -- so every interaction feels responsive and deliberate rather than blank or jarring."
tier: Deep-dive
---

# MICRO — Microinteractions

## Essential

- [P0] Are hover, focus, and active states defined for interactive elements?
- [P0] Does `prefers-reduced-motion: reduce` trigger a genuinely usable alternative (e.g., instant state transition, static progress indicator) rather than merely disabling animation?
- [P0] Are all intermediate states (loading, skeleton, optimistic, error, empty, partial) explicitly designed so the UI never shows a blank or broken frame?
- [P0] Are animations GPU-composited (transform/opacity only), avoiding layout thrashing and staying within the frame budget for the target device's refresh rate (16 ms at 60 Hz, 8 ms at 120 Hz)?
- [P0] Do animated or auto-updating elements expose appropriate ARIA live regions so screen-reader users perceive the state changes sighted users see?

## Standard

- [P1] Are transitions and animations purposeful (guiding attention, confirming actions)?
- [P1] Is feedback immediate and proportional to the action (subtle for minor, prominent for destructive)?
- [P1] Are transition durations, easing functions, and animation delays defined as design tokens, and are those tokens used consistently rather than overridden per-component?
- [P1] Do animations follow natural motion principles (ease-in exits, ease-out entrances) and stay within 100-500 ms?
- [P1] Are gesture affordances (swipe, pinch, long-press) discoverable through progressive disclosure or coaching rather than trial-and-error?
- [P1] Are triggers (manual user-initiated and system-generated) for each microinteraction explicitly defined, and do manual triggers have accessible equivalents for keyboard, touch, and pointer inputs (not hover-only)?
- [P1] Are loops and modes defined for each microinteraction — does it reset correctly to its initial state after completion, and is its behavior specified when the trigger fires again before the prior cycle ends (e.g., debounce, queue, cancel-and-restart)?
- [P1] Do auditory cues (click, chime, alert) complement visual feedback without relying on sound alone, and are they mutable without losing information?
- [P2] Are haptic patterns varied by feedback type (light tap for selection, double pulse for error, long press confirmation) rather than a single generic vibration?
- [P2] Is contextual micro-copy (loading button labels, inline validation, toast confirmations) specific to the action rather than generic ("Done", "Error")?
- [P2] Are the conditional rules governing each microinteraction explicitly defined, including behavior during interruption (user re-triggers, navigation change, network failure) and upon re-entry after completion (does the interaction reset, accumulate, or lock)?
- [P2] Do microinteractions close the feedback loop — confirming both the outcome (success, failure, partial) and the resulting system state — in a way that is perceivable without requiring the user to seek additional confirmation?
- [P2] When multiple elements animate together (e.g., list load, modal entry, page transition), are timing relationships (stagger, delay, sequencing) intentionally designed to guide attention and signal hierarchy, rather than defaulting to simultaneous starts?

## Deep

- [P3] Do moments of delight (success animations, empty-state personality) reinforce brand tone, and has their impact on task-completion time been verified to be negligible (within 5% of baseline or validated by user testing)?
- [P3] Are progress indicators, streaks, and reward animations calibrated to motivate without anxiety, and do they degrade gracefully when gamification is disabled?
- [P3] Do animation and transition choices (slide direction, expand/collapse axis, fade vs. transform) encode the correct spatial or hierarchical relationship between source and destination, consistent with the application's navigation model and the user's expected mental model of the information space?
