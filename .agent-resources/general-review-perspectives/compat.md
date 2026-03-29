# COMPAT — Compatibility

## Essential

- [P0] Does this change break existing API contracts or database schemas?
- [P0] Is backward compatibility preserved, or is a migration path provided?
- [P0] Are API contract changes validated against existing client versions before deployment?
- [P0] Do API changes include a versioning or deprecation strategy that gives consumers a migration window before breaking endpoints are removed?
- [P0] Are database schema changes deployed through reversible migrations, and can the previous application version still operate against the new schema during rollout?

## Deep-dive

- [P1] Are browser compatibility requirements (if frontend) maintained?
- [P1] Are there browser compatibility targets defined and tested (browserslist, cross-browser E2E)?
- [P1] Does this change rely on Web APIs or CSS features absent from any supported browser, and are fallbacks provided?
- [P1] Have touch interactions, viewport constraints, and OS-specific behaviors (iOS Safari, Android WebView) been verified on all supported mobile platforms?
- [P1] Have dependency version constraints been checked for conflicts, and are transitive dependency ranges compatible with the rest of the dependency tree?
- [P1] Is the code free of runtime-specific APIs (e.g., Node-only, Deno-only, Bun-only) that would break execution in any of the targeted JavaScript runtimes?
- [P1] Has integration with legacy systems been validated, ensuring that protocol versions, character encodings, and data formats remain compatible with older upstream/downstream services?
- [P2] Do UI changes maintain equivalent functionality when accessed via assistive technologies across different browser/screen-reader pairings (e.g., NVDA+Firefox, VoiceOver+Safari)?
- [P2] Does the feature degrade gracefully when JavaScript is unavailable or when optional platform capabilities are missing, following a progressive enhancement approach?
- [P2] Are new platform features consumed via feature detection rather than user-agent sniffing, and are polyfills loaded conditionally only when the native API is absent?
