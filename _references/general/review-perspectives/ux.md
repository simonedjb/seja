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

## Communicability

> The 13 communicability utterances below are a precise analytical taxonomy from Semiotic Engineering [SemEng-2005, Ch. 4 pp.123-138], grounded in the **discrimination principle of illocution vs. perlocution**. Each utterance maps 1:1 to a specific communicative breakdown type between the user and the designer's deputy (the system speaking on the designer's behalf). Reviewers use these to diagnose specific breakdown types by looking for interface patterns that could trigger each category.

### Complete Failures (I) -- global intent does not match global outcome

| Utterance | Code | Breakdown | Diagnostic question |
|-----------|------|-----------|-------------------|
| "I give up." | Ia | User consciously abandons the goal -- has run out of knowledge, skill, time, or patience | Could a user plausibly exhaust all apparent paths to their goal and have no visible way forward? |
| "Looks fine to me." | Ib | User believes they succeeded but actually hasn't -- the system state does not match their intent, and they cannot tell | Could the UI lead a user to believe an action completed successfully when it didn't (silent failures, missing confirmation, invisible side effects)? |

### Temporary Failures (II) -- global intent will be achieved, but local steps break down

**Halted semiosis (IIa)** -- the user's sense-making is momentarily stuck:

| Utterance | Code | Breakdown | Diagnostic question |
|-----------|------|-----------|-------------------|
| "Where is it?" | IIa1 | User knows what they want to do but cannot find the control for it among the visible signs | Could a user plausibly not find the control for this action among the visible interface elements? |
| "What happened?" | IIa2 | User performed an action but cannot see or perceive the outcome -- feedback is absent or unnoticed | Does every user action produce visible, timely feedback? Could a state change go unnoticed? |
| "What now?" | IIa3 | User is clueless about what to do next -- no sign means anything to them in context | At any point in this flow, could a user face a screen where no element suggests a clear next step? |

**Wrong illocution (IIb)** -- the user realizes their approach is wrong:

| Utterance | Code | Breakdown | Diagnostic question |
|-----------|------|-----------|-------------------|
| "Where am I?" | IIb1 | User is acting in the wrong context/mode -- their action would be valid elsewhere | Could a user confuse which mode, section, or state they are in and attempt actions valid only in another context? |
| "Oops!" | IIb2 | User immediately realizes a momentary slip and backtracks -- an isolated wrong expression | Are there controls whose proximity, appearance, or labels could cause a quick mis-click that the user would instantly regret? |
| "I can't do it this way." | IIb3 | User abandons a whole line of reasoning (a multi-step plan) after realizing it won't achieve the goal | Could a user follow a plausible multi-step path that appears productive but ultimately leads nowhere? |

**Clarification-seeking (IIc)** -- the user tries to understand the designer's message:

| Utterance | Code | Breakdown | Diagnostic question |
|-----------|------|-----------|-------------------|
| "What's this?" | IIc1 | User probes an interface element for meaning (hovering, opening menus) -- implicit metacommunication | Are there interface elements whose meaning isn't self-evident and that lack tooltips, labels, or contextual cues? |
| "Help!" | IIc2 | User explicitly invokes help (F1, help page, documentation, asking someone) -- explicit metacommunication | Is the help content reachable, contextual, and sufficient to resolve the specific breakdown the user is experiencing? |
| "Why doesn't it?" | IIc3 | User repeats previously unsuccessful steps to understand what went wrong -- autonomous sense-making | Could a user repeat the same failing action multiple times, unable to determine why it doesn't produce the expected result? |

### Partial Failures (III) -- goal is achieved, but not through the intended path

| Utterance | Code | Breakdown | Diagnostic question |
|-----------|------|-----------|-------------------|
| "I can do otherwise." | IIIa | User achieves the goal through an unintended path without understanding the designed solution -- potential residual misconception | Could a user achieve their goal via a workaround without ever discovering the intended (better-supported) approach? |
| "Thanks, but no, thanks." | IIIb | User understands the designed solution but deliberately chooses an alternative -- mismatch between the designer's model of the user and who they actually are | Is the intended interaction path cumbersome enough that an informed user would prefer a shortcut, even at some cost? |

### Sign Classification (optional analytical lens)

> Segmented analysis by sign class -- analyzing each independently, then comparing -- mirrors the Semiotic Inspection Method [SemEng-Methods-2009] and can catch inconsistencies that cross-cutting reviews miss.

- [P2] **Metalinguistic signs**: Are help text, error messages, tooltips, and documentation consistent with the interactive behavior they describe?
- [P2] **Static signs**: Do labels, icons, layout structure, and visual hierarchy communicate the available actions and their relationships clearly in a single-moment snapshot?
- [P2] **Dynamic signs**: Do state transitions, animations, and interaction feedback confirm or clarify the user's understanding of what happened and what to do next?
