---
designer_description: "When the reviewer is asked to look at what you built through developer-experience eyes, I'm the checklist that tells it what to watch for -- readability, self-documentation, helpful error messages, CI/CD hygiene, onboarding friction, and the 13 communicability breakdowns that expose where a developer might give up, get stuck, or silently misuse your API -- so the next contributor doesn't need tribal knowledge to ship a change."
tier: Essential
---

# DX — Developer Experience

## Essential

- [P0] Is the code readable and comprehensible in isolation — can a developer unfamiliar with this module hold its logic in working memory without consulting multiple other files?
- [P0] Are error messages helpful for debugging? Are edge cases handled gracefully?
- [P0] Is there CI/CD running tests, linting, and type-checking on every commit?
- [P0] Can a developer go from clone to passing tests in under 5 minutes with a single command, and does the pipeline fail fast with actionable errors?
- [P0] Does the internal developer platform provide self-service environment provisioning, secrets, and deployment -- no tickets for routine work?
- [P0] Are inline comments, API docs, and DDRs up to date and co-located with the code they describe?
- [P0] Will a new contributor understand this without tribal knowledge?
- [P0] Could a developer exhaust docs, examples, and error messages without finding a path to their task? (Ia — "I give up." — developer abandons goal out of knowledge, patience, or time)
- [P0] Could a developer believe their operation succeeded when it didn't — silent failures, swallowed errors, ignored parameters? (Ib — "Looks fine to me." — silent misconfiguration or partial write)

## Standard

- [P1] Is there automated dependency update tooling (Dependabot, Renovate)?
- [P1] Are coverage thresholds enforced, preventing regressions below a minimum?
- [P1] Are code review guidelines documented and enforced (turnaround, approvals, feedback norms)?
- [P1] Is there a structured onboarding path (quick-start, labeled starter tasks, mentorship) with a measurable target: a new member's first meaningful PR merged within one week of joining?
- [P1] Are contribution guidelines, issue templates, and a code of conduct published so external or cross-team contributors can participate without friction?
- [P2] Does the project provide editor configs (`.editorconfig`, recommended extensions, launch configs) so IDE features work out of the box?
- [P2] Are linting, formatting, and static analysis automated in pre-commit hooks and CI so style never blocks reviews?
- [P2] In a monorepo, are build caching, affected-target detection, and dependency graph tooling in place so developers only build and test what changed?
- [P1] Is dead code (unreachable branches, unused variables, commented-out blocks, disabled features with no sunset date) identified via static analysis and removed to prevent it from misleading future contributors? (CWE-561, CWE-563)
- [P1] Do public functions, methods, and CLI entry points carry behavioral summaries documenting inputs, outputs, side effects, thrown exceptions, and concurrency constraints — not just parameter names? (CWE-1117, CWE-1118)
- [P2] Is debug-only code (verbose logging, hardcoded test credentials, active debug endpoints, `console.log`/`print` traces) removed or gated behind build flags before production deployment? (CWE-489, CWE-215)
- [P2] Are source comments verified to accurately describe the code they annotate — with stale or contradictory comments caught in review rather than silently misleading readers? (CWE-1116)
- [P2] Are inner-loop and pipeline metrics — local build time, test re-run latency, CI wait time, deploy frequency — tracked and reviewed at least quarterly, with explicit targets for P50 and P95?
- [P1] Does every code module keep its cognitive load low — short, focused functions with limited nesting, explicit state, and no hidden side effects — so a developer unfamiliar with this module can reason about its behavior without consulting multiple other files?
- [P1] Is the inner-loop feedback latency — the time between saving a code change and seeing a test re-run, hot-reload, or incremental build result — under two minutes for the most common development workflow, so developers can iterate without losing context?
- [P1] Can the developer who wrote a feature access structured observability data for their service in production — searchable structured logs, distributed traces, and real-time error rates — without filing a ticket or waiting for SRE assistance, so the feedback loop from writing to understanding behavior is closed?
- [P2] Are contribution friction-reducers present and visible — issues labeled for first-time contributors, explicit welcoming language in CONTRIBUTING.md, a stated review-turnaround time — so a new contributor knows where to start and can submit an imperfect first PR without fear of an opaque or delayed process?
- [P2] When a developer uses an API, CLI, or configuration option incorrectly, does the system produce immediate, localized feedback — compile-time type error, lint warning, or runtime precondition failure — rather than requiring the developer to discover the mistake at integration test, deploy, or code review?

### Communicability

> 13 utterances from Semiotic Engineering [SemEng-2005, Ch. 4; adapted for developer-facing interfaces per SigniFYI-2016], grounded in the **illocution vs. perlocution discrimination principle**. Each maps 1:1 to a breakdown type between the developer and the tool/API/framework designer's deputy. Use to diagnose how APIs, CLIs, SDKs, config, and docs fail to communicate design intent.

#### Complete Failures (I) -- developer cannot achieve their goal

| Utterance | Code | Breakdown | Diagnostic question |
|-----------|------|-----------|-------------------|
| "I give up." | Ia | Abandons goal -- out of knowledge, patience, or time for the tool/API | Could a developer exhaust docs, examples, and error messages without finding a path to their task? |
| "Looks fine to me." | Ib | Believes API call/config/integration succeeded when it didn't -- silent failures, partial writes, ignored parameters | Could a developer believe their operation succeeded when it didn't (silent failures, swallowed errors, ignored parameters)? |

#### Temporary Failures (II) -- eventual success, but local steps break down

IIa = halted semiosis (sense-making stuck). IIb = wrong illocution (approach is wrong). IIc = clarification-seeking (probing designer intent).

| Utterance | Code | Breakdown | Diagnostic question |
|-----------|------|-----------|-------------------|
| "Where is it?" | IIa1 | Cannot find the endpoint, config option, CLI flag, or API method | Could a developer not find the endpoint, config option, or CLI flag for their action? |
| "What happened?" | IIa2 | Cannot see the outcome of a call/command -- no response, unclear status, missing logs | Does every API call, CLI command, and config change produce clear feedback? |
| "What now?" | IIa3 | Clueless about next step -- docs, errors, and responses give no guidance | After an API response or error, could a developer be left with no next step? |
| "Where am I?" | IIb1 | Using the API/tool in the wrong context or mode | Could a developer confuse which API version, environment, or auth context they're in? |
| "Oops!" | IIb2 | Immediate slip -- wrong endpoint, parameter, or command | Are there parameters, flags, or method names whose similarity could cause an accidental mis-call? |
| "I can't do it this way." | IIb3 | Abandons a whole integration approach after discovering it won't work | Could a developer follow a plausible integration path that doesn't support their use case? |
| "What's this?" | IIc1 | Probes a parameter, return value, or config for meaning -- reads types, explores responses | Are there parameters, response fields, or config options with ambiguous names? |
| "Help!" | IIc2 | Explicitly consults docs, examples, or asks for help | Are docs reachable, contextual, and sufficient to resolve the specific problem? |
| "Why doesn't it?" | IIc3 | Repeats failing calls to understand what's wrong -- experimental debugging | Could a developer repeat the same failing call multiple times, unable to determine why? |

#### Partial Failures (III) -- goal achieved, but not via the intended path

| Utterance | Code | Breakdown | Diagnostic question |
|-----------|------|-----------|-------------------|
| "I can do otherwise." | IIIa | Goal achieved via unintended path (raw SQL not ORM, direct file access not API) without knowing the supported approach | Could a developer achieve their goal via a workaround without discovering the intended approach? |
| "Thanks, but no, thanks." | IIIb | Understands the intended approach but bypasses it -- cumbersome, slow, or over-engineered for their need | Is the intended pattern cumbersome enough that an informed developer would prefer a shortcut? |

## Deep

- [P3] Are high-cognitive-load code sections identified for targeted refactoring — whether via static proxy thresholds (function length, nesting depth, parameter count), IDE cognitive-load visualization tooling, or developer-self-report heatmaps from retrospectives — so the team can prioritize comprehensibility improvements where they matter most?
