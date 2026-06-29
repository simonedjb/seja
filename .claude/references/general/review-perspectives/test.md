---
designer_description: "When the reviewer is asked to look at what you built through testability eyes, I'm the checklist that tells it what to watch for -- whether existing tests still cover the change, where new tests are needed for success and error paths, contract coverage between services, mocking strategy, test isolation, and reproducibility of the test environment -- so the suite keeps earning its right to gate merges."
tier: Essential
---

# TEST — Testability

## Essential

- [P0] Is this change covered by existing tests, or are new tests needed?
- [P0] Are success path, error paths, and edge cases tested?
- [P0] Are API contract tests catching frontend/backend schema drift?
- [P0] Are SAST (static analysis security tests) integrated into the pipeline?
- [P0] Do consumer-driven contract tests let services deploy independently?

## Standard

- [P1] Has isolation been achieved, and where it proved difficult, was the coupling addressed as a design signal rather than accepted as fixed?
- [P1] Are DAST (dynamic analysis security tests) integrated into the pipeline?
- [P1] Are E2E tests executed automatically in the CI pipeline on every PR or merge — not only runnable locally by individual developers?
- [P1] Does the test suite follow a layered pyramid (many unit tests, fewer integration tests, few E2E tests) with defined ratios and explicit team ownership of each layer?
- [P1] Is mutation testing run against the suite, with the score reported and weak-assertion clusters investigated — noting that raw scores may overstate quality for property-specific subsystems?
- [P1] Are performance/load tests defined for critical paths with baselines and regression thresholds?
- [P1] Is test infrastructure reproducible (containerised runners, pinned dependencies, cached layers) for deterministic results?
- [P1] Do tests verify observable behavior (outputs, side effects, state transitions) rather than implementation details (call counts, private method returns, internal variable values), ensuring the suite survives behavioral-preserving refactors?
- [P1] Are test assertions strong enough to distinguish correct from incorrect outputs — specifically, do they assert exact values, preconditions, and postconditions rather than trivially-satisfied proxies such as null checks or type checks?
- [P2] Is there a flaky test detection/quarantine mechanism?
- [P2] Do property-based or generative tests cover invariants example-based tests miss?
- [P2] Is test data managed via deterministic factories/fixtures, are seed/teardown sequences idempotent, and are they safe under parallel test execution?
- [P2] Is there a structured exploratory testing charter to complement automated coverage?
- [P2] For each previously discovered security vulnerability, is there a regression test that would have caught the original bug and will catch re-introduction of the same weakness class? (CWE-89, CWE-79, CWE-502)
- [P2] Are race conditions and TOCTOU vulnerabilities specifically exercised under concurrent load (multiple goroutines, threads, or async tasks executing the same critical section simultaneously)? (CWE-366, CWE-367)
- [P2] Are fuzzing tests integrated into the pipeline for security-relevant or protocol-parsing code?
- [P2] For suites exceeding 10 minutes of serial execution, is there a sharding or parallelism strategy (by file, class, or historical duration) that keeps CI feedback under a defined threshold?

## Deep

- [P3] Are visual regression snapshots stored in VCS, compared automatically on every PR, routed to a named approver, and is the approval gate enforced before merge?
- [P3] For subsystems validated against formal properties (temporal logic, contracts, SLA assertions), is property-based mutation testing (PBMT) used to measure φ-mutation score — counting only mutants whose faults propagate to a property violation, not merely to any output difference?
