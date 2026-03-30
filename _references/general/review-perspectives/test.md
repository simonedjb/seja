# TEST — Testability

## Essential

- [P0] Is this change covered by existing tests, or do new tests need to be written?
- [P0] Are the success path, common error paths, and edge cases tested?
- [P0] Are API contract tests in place to catch frontend/backend schema drift?
- [P0] Are security-focused tests (SAST rules, DAST scans, fuzzing) integrated into the pipeline to catch vulnerabilities before deployment?
- [P0] Are consumer-driven contract tests validating integration boundaries so services can deploy independently without breaking each other?

## Deep-dive

- [P1] Can this be tested in isolation without complex setup?
- [P1] Are E2E tests automated in a pipeline, not just available locally?
- [P1] Is there mutation testing to validate test suite effectiveness?
- [P1] Is the test automation architecture layered (unit/integration/E2E) with clear ownership boundaries and appropriate ratios across layers?
- [P1] Have performance and load tests been defined for critical paths, with measurable baselines and regression thresholds?
- [P1] Has the mutation testing score been measured, and are there gaps where mutants survive indicating weak assertions?
- [P1] Is the test infrastructure reproducible (containerised runners, pinned dependencies, cached layers) so results are deterministic across environments?
- [P2] Is there a flaky test detection/quarantine mechanism?
- [P2] Are property-based or generative tests used to cover invariants and discover edge cases that example-based tests miss?
- [P2] Is test data managed through deterministic factories or fixtures rather than shared mutable state that couples tests together?
- [P2] Is there a structured exploratory testing charter or session-based approach to complement automated coverage for new features?
- [P3] Are visual regression snapshots captured for UI components, with an automated diffing and approval workflow?
