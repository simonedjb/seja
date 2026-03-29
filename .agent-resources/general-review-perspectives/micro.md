# MICRO — Microinteractions

## Essential

- [P0] Are hover, focus, and active states defined for interactive elements?
- [P0] Is there a `prefers-reduced-motion` media query check to disable animations for users who need it?
- [P0] Are all intermediate states (loading, skeleton, optimistic update, error, empty, partial) explicitly designed so the UI never shows a blank or broken frame during transitions?
- [P0] Are animations GPU-composited (transform/opacity only) and do they avoid layout thrashing, staying under 16 ms per frame on target low-end devices?
- [P0] Do animated or auto-updating elements expose appropriate ARIA live regions, and can screen-reader users perceive state changes that sighted users see through animation?

## Deep-dive

- [P1] Are transitions and animations purposeful (guiding attention, confirming actions)?
- [P1] Is feedback immediate and proportional to the action (e.g., subtle for minor, prominent for destructive)?
- [P1] Are transition durations and easing functions defined as design tokens for consistency?
- [P1] Do animations follow natural motion principles (ease-in for exits, ease-out for entrances) and stay within 100–500 ms to feel responsive without causing delay?
- [P1] Are gesture affordances (swipe, pinch, long-press) discoverable through progressive disclosure or coaching overlays rather than hidden behind trial-and-error?
- [P2] Are haptic patterns varied by feedback type (e.g., light tap for selection, double pulse for error, long press confirmation) rather than using a single generic vibration?
- [P2] Do auditory cues (click, chime, alert) complement visual feedback without relying on sound alone, and are they mutable without losing information?
- [P2] Is contextual micro-copy (button labels during loading, inline validation messages, toast confirmations) specific to the action performed rather than generic ("Done", "Error")?
- [P3] Do microinteractions include moments of delight (playful success animations, personality in empty states) that reinforce brand tone without slowing task completion?
- [P3] Are progress indicators, streaks, and reward animations calibrated so they motivate without creating anxiety, and do they degrade gracefully when gamification features are disabled?
