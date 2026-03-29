# UX — User Experience

## Essential

- [P0] Is the user flow intuitive, with clear feedback for actions and errors?
- [P0] Do user research findings (personas, journey maps, usability studies) directly inform the design decisions made here, and are there unvalidated assumptions that need testing?
- [P0] Has the flow been validated with real users across key task scenarios, and are there identified usability issues above a severity threshold that remain unresolved?
- [P0] When an error occurs, does the UI explain what happened in plain language, preserve user input, and offer a clear recovery path or undo option?

## Deep-dive

- [P1] Does the interaction follow established UX patterns in the project?
- [P1] Are loading states, empty states, and error states handled?
- [P1] Are offline or degraded-network states handled gracefully (retry, queue, feedback)?
- [P1] Is the information architecture logically structured so users can form accurate mental models and find content through multiple navigation paths?
- [P1] Are micro-interactions (transitions, hover states, affordances) consistent and purposeful, reinforcing cause-and-effect relationships rather than adding visual noise?
- [P1] Are dark patterns absent, and does the design respect user autonomy by making opt-outs as easy as opt-ins and avoiding manipulative urgency or social proof?
- [P1] Do all components adhere to the design system's token and pattern contracts, and are any deviations documented with rationale and tracked for backport?
- [P1] Does the onboarding flow progressively disclose complexity, provide meaningful quick wins, and allow users to skip or revisit steps without losing progress?
- [P1] Are analytics events instrumented at each decision point so that drop-off rates, task completion times, and variant performance can be measured and acted upon?
- [P2] Are optimistic updates used where appropriate to reduce perceived latency?
- [P2] Is there a consistent skeleton/shimmer loading pattern across all data-dependent views?
- [P2] Is the copy concise, scannable, and action-oriented, with terminology consistent across the product and aligned with the vocabulary users actually use?
