# DX — Developer Experience

## Essential

- [P0] Is the code readable, self-documenting, and following project conventions?
- [P0] Are error messages helpful for debugging? Are edge cases handled gracefully?
- [P0] Is there a CI/CD pipeline that runs tests, linting, and type-checking on every commit?
- [P0] Can a developer go from clone to passing tests in under 5 minutes with a single command, and does the pipeline fail fast with clear, actionable error messages?
- [P0] Does the internal developer platform provide self-service environment provisioning, secrets management, and deployment so developers never need to file a ticket to do routine work?
- [P0] Are inline code comments, API docs, and architecture decision records kept up to date and co-located with the code they describe?
- [P0] Will a new contributor understand this without tribal knowledge?

## Deep-dive

- [P1] Is there automated dependency update tooling (Dependabot, Renovate)?
- [P1] Are coverage thresholds enforced, preventing regressions below a minimum?
- [P1] Are code review guidelines documented and enforced consistently, including expectations for review turnaround time, required approvals, and constructive feedback norms?
- [P1] Is there a structured onboarding path (quick-start guide, sample tasks, mentorship pairing) that lets a new team member ship a meaningful change within their first week?
- [P1] Are contribution guidelines, issue templates, and a code of conduct published and maintained so that external or cross-team contributors can participate without friction?
- [P2] Does the project provide editor configurations (`.editorconfig`, recommended extensions, launch configs) so that IDE features like auto-complete, go-to-definition, and debugging work out of the box?
- [P2] Are linting rules, formatting standards, and static analysis checks automated in pre-commit hooks and CI so that style discussions never block code reviews?
- [P2] In a monorepo setup, are build caching, affected-target detection, and dependency graph tooling in place so that developers only build and test what changed?
- [P3] Are developer productivity metrics (build times, CI wait times, deploy frequency, time-to-first-commit) tracked and reviewed regularly to identify bottlenecks?

## Communicability

> The 13 communicability utterances below are a precise analytical taxonomy from Semiotic Engineering [SemEng-2005, Ch. 4; adapted for developer-facing interfaces per SigniFYI-2016], grounded in the **discrimination principle of illocution vs. perlocution**. Each maps 1:1 to a specific communicative breakdown type between the developer and the tool/API/framework designer's deputy. Use these to diagnose how developer-facing interfaces (APIs, CLIs, SDKs, config, documentation) fail to communicate their design intent.

### Complete Failures (I) -- developer cannot achieve their goal

| Utterance | Code | Breakdown | Diagnostic question |
|-----------|------|-----------|-------------------|
| "I give up." | Ia | Developer consciously abandons the goal -- has run out of knowledge, patience, or time to figure out the tool/API | Could a developer exhaust all apparent documentation, examples, and error messages without finding a way to accomplish their task? |
| "Looks fine to me." | Ib | Developer believes their API call, config change, or integration succeeded when it actually didn't -- silent failures, partial writes, ignored parameters | Could a developer believe their operation succeeded when it actually didn't (silent failures, swallowed errors, ignored parameters, partial state changes)? |

### Temporary Failures (II) -- developer will eventually succeed, but local steps break down

**Halted semiosis (IIa)** -- the developer's sense-making is momentarily stuck:

| Utterance | Code | Breakdown | Diagnostic question |
|-----------|------|-----------|-------------------|
| "Where is it?" | IIa1 | Developer knows what they want to do but cannot find the endpoint, config option, CLI flag, or API method | Could a developer plausibly not find the API endpoint, config option, or CLI flag for their intended action? |
| "What happened?" | IIa2 | Developer performed an API call or command but cannot see the outcome -- no response, unclear status, missing logs | Does every API call, CLI command, and config change produce clear feedback? Could a state change go unnoticed in logs or responses? |
| "What now?" | IIa3 | Developer is clueless about the next step -- documentation, error messages, and API responses provide no guidance | After receiving an API response or error, could a developer be left with no indication of what to do next? |

**Wrong illocution (IIb)** -- the developer realizes their approach is wrong:

| Utterance | Code | Breakdown | Diagnostic question |
|-----------|------|-----------|-------------------|
| "Where am I?" | IIb1 | Developer is using the API/tool in the wrong context or mode -- their call would be valid in a different state or configuration | Could a developer confuse which API version, environment, or authentication context they're operating in? |
| "Oops!" | IIb2 | Developer immediately realizes a slip -- called the wrong endpoint, passed wrong parameter, ran the wrong command | Are there API parameters, CLI flags, or method names whose similarity could cause an accidental mis-call with immediate consequences? |
| "I can't do it this way." | IIb3 | Developer abandons a whole integration approach after discovering it won't work as expected | Could a developer follow a plausible integration path (documented or inferred) that ultimately doesn't support their use case? |

**Clarification-seeking (IIc)** -- the developer tries to understand the designer's intent:

| Utterance | Code | Breakdown | Diagnostic question |
|-----------|------|-----------|-------------------|
| "What's this?" | IIc1 | Developer probes a parameter, return value, or config option for meaning -- reads type hints, explores responses | Are there API parameters, response fields, or config options whose names are ambiguous without reading documentation? |
| "Help!" | IIc2 | Developer explicitly consults documentation, examples, or asks for help | Is the documentation reachable, contextual, and sufficient to resolve the specific integration problem the developer is experiencing? |
| "Why doesn't it?" | IIc3 | Developer repeats previously failing calls to understand what's wrong -- experimental debugging | Could a developer repeat the same failing API call or command multiple times, unable to determine why it doesn't produce the expected result? |

### Partial Failures (III) -- goal is achieved, but not through the intended path

| Utterance | Code | Breakdown | Diagnostic question |
|-----------|------|-----------|-------------------|
| "I can do otherwise." | IIIa | Developer achieves the goal through an unintended path (raw SQL instead of ORM, direct file access instead of API) without knowing the supported approach exists | Could a developer achieve their goal via a workaround (bypassing the API, using internal interfaces, copy-pasting) without discovering the intended approach? |
| "Thanks, but no, thanks." | IIIb | Developer understands the intended approach but deliberately bypasses it because it's cumbersome, slow, or over-engineered for their need | Is the intended usage pattern cumbersome enough that an informed developer would prefer a shortcut, even at some cost (e.g., skipping validation, using raw queries)? |
