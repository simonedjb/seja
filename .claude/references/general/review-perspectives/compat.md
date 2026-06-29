---
designer_description: "When the reviewer is asked to look at what you built through compatibility eyes, I'm the checklist that tells it what to watch for -- API contract stability, schema-evolution safety, browser and runtime support, graceful degradation, dependency-range conflicts, and whether older clients can still talk to your new service during rollout -- so breaking changes either get a migration window or get caught before they ship."
tier: Deep-dive
---

# COMPAT — Compatibility

## Essential

- [P0] Does this change break existing API contracts or database schemas?
- [P0] Is backward compatibility preserved, or is a migration path provided?
- [P0] Are API contract changes validated against existing client versions before deployment?
- [P0] Do API changes include a versioning or deprecation strategy giving consumers a migration window before breaking endpoints are removed?
- [P0] Are schema changes deployed via reversible migrations, with the previous application version still able to operate against the new schema during rollout?

## Standard

- [P1] Are browser compatibility targets defined and tested (browserslist, cross-browser E2E)?
- [P1] Does this change rely on Web APIs or CSS features (Grid subgrid, container queries, `:has()`, etc.) absent from any supported browser without fallbacks or polyfills?
- [P1] Have touch interactions, viewport constraints, and OS-specific behaviors (iOS Safari, Android WebView) been verified on supported mobile platforms?
- [P1] Have dependency version constraints been checked for conflicts across transitive ranges?
- [P1] Is the code free of runtime-specific APIs (Node-only, Deno-only, Bun-only, Cloudflare Workers-only, edge-runtime-only) that would break in any targeted JavaScript runtime or edge execution environment?
- [P1] Has legacy-system integration been validated so protocol versions, encodings, and data formats remain compatible with older upstream/downstream services?
- [P1] Does the feature degrade gracefully when JavaScript is unavailable or optional platform capabilities are missing (progressive enhancement)?
- [P1] Has this change been formally classified as MAJOR (backward-incompatible public API change), MINOR (backward-compatible new functionality), or PATCH (backward-compatible bug fix) per SemVer 2.0.0, and does the version bump recorded in the package manifest match that classification?
- [P1] Are wire-protocol and serialization schema changes (new JSON fields, Protobuf message definitions, Avro schemas, GraphQL type extensions, event payload shapes) strictly additive, with new fields carrying default values and unknown-field tolerance verified on both the producing and consuming sides before the rollout proceeds?
- [P1] Is the project's public API surface explicitly declared (in code, OpenAPI spec, TypeDoc, CLI help text, or equivalent) so that downstream consumers can independently determine whether a given change is breaking, non-breaking, or internal-only?
- [P2] Are new platform features consumed via feature detection (detecting the specific API, not a proxy capability) rather than UA sniffing, with polyfills loaded only when the native API is absent and removed when the browserslist support floor makes them unnecessary?
- [P2] Are behavioral changes introduced by library or framework version upgrades explicitly documented and regression-tested before the upgrade is promoted, so consumers are not silently broken by transitive dependency updates? (CWE-439)
- [P2] Are platform-dependent third-party components (native binaries, OS-specific SDKs, architecture-tied libraries) flagged in the dependency manifest, with portability verified for each target platform in CI? (CWE-1103)
- [P2] Are previously deprecated APIs, endpoints, or configuration keys tracked in a deprecation log or issue tracker, and have those reaching end-of-window been removed (or is their removal scheduled and unblocked) rather than left indefinitely to accumulate technical debt?
- [P2] When dependency version conflicts are resolved via pinned versions, `overrides`, or `resolutions` fields, is the resolution recorded in the manifest with a brief rationale explaining which conflicting range triggered it, so future dependency updates do not silently revert the fix?

## Deep

- [P3] Is there a compatibility test matrix covering all declared target environments (OS versions, Node/Deno/Bun/edge runtimes, browsers per browserslist config, screen-reader/browser pairings), and is the matrix run in CI on a scheduled basis — not just on PRs — so that upstream environment changes are caught before reaching production?
- [P3] Are environment variable changes (new required vars without defaults, renamed vars, removed vars) backward-compatible with currently running deployments, or is an operator migration guide provided that is gated into the same release notes as the code change?
- [P4] For long-lived libraries or platforms, is a formal support commitment (LTS window, EOL dates, support matrix covering runtime and OS targets) published and kept current, so that downstream consumers can plan upgrades with confidence that the previous MAJOR version will receive security patches for a defined period?
