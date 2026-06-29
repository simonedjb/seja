---
designer_description: "When the reviewer is asked to look at what you built through API-design eyes, I'm the checklist that tells it what to watch for -- RESTful conventions, route and naming consistency, request/response contracts, versioning and deprecation discipline, object-level authorization, and how the API communicates its intent to consumers -- so the surface you ship feels predictable to integrate against."
tier: Deep-dive
---

# API — API Design

## Essential

- [P0] Is the endpoint RESTful, consistent with existing routes, and properly documented?
- [P0] Is every public endpoint routed through the API gateway with consistent authentication, throttling, circuit-breaking, and request-tracing policies applied?
- [P0] Is there a versioning strategy (URI path, header, or content negotiation) in place, with a documented deprecation timeline and sunset headers for retired versions?
- [P0] Are authentication tokens validated on every request — including `aud` and `scope` claim verification — and are object-level and field-level authorization checks enforced to prevent BOLA/BFLA vulnerabilities?

## Standard

- [P1] Are error responses structured (consistent envelope), free of internal stack traces or implementation details, and validated against a published error schema?
- [P1] Are rate-limit headers (`X-RateLimit-Remaining`, `X-RateLimit-Reset`) returned, and is `Retry-After` included on `429 Too Many Requests` responses per RFC 9110 §10.2.1?
- [P1] Do resource URIs follow a consistent noun-based hierarchy, with HTTP methods used per their semantics (PUT=full replacement, PATCH=partial)?
- [P1] Are query complexity limits, depth restrictions, and field-level authorization enforced for GraphQL, and is introspection disabled in production environments?
- [P1] Are response shapes stable for generated SDK clients, with nullable fields marked and envelope structures consistent?
- [P1] Are payloads optimized (pagination, sparse fieldsets, compression) and N+1 query patterns eliminated server-side?
- [P1] Are breaking changes detected via contract tests or schema diff in CI, under a documented compatibility policy (e.g., additive-only)?
- [P1] For POST operations that must not be repeated on retry (payments, order submissions, notifications), is an idempotency key mechanism (`Idempotency-Key` header or equivalent) required, validated server-side, and documented in the API spec?
- [P1] Does the API implement content negotiation per RFC 9110 §12 — parsing `Accept` and `Content-Type` headers, returning `406 Not Acceptable` when the requested media type cannot be served, and setting `Vary` correctly on responses whose representation varies by negotiation?
- [P1] Are inputs canonicalized and decoded (percent-decoding, Unicode normalization, path normalization) *before* validation, not after, so canonicalized-equivalent values cannot bypass input checks? (CWE-551, CWE-179)
- [P1] Does the API apply server-side file upload validation (content-type verification via magic bytes, size limits, extension denylist) independent of any client-side enforcement? (CWE-434)
- [P1] Do API responses return identical status codes and response times for "resource not found" vs. "access forbidden" cases, preventing authenticated enumeration of IDs, usernames, and resource existence? (CWE-204, CWE-205)
- [P2] Is the OpenAPI spec browsable via a documentation UI (Swagger UI, ReDoc), with example request/response payloads included?
- [P2] Does every endpoint have a human-readable description, parameter constraints, and at least one success and one error example documented inline?
- [P2] **Consistency** (CDN): Do similar API operations use similar parameter names, response shapes, and error formats?
- [P2] **Role-expressiveness** (CDN): Can a developer infer the purpose of an endpoint, parameter, or response field from its name alone?
- [P2] **Error-proneness** (CDN): Does the API design invite mistakes (confusable parameter names, missing validation, destructive operations without confirmation)?
- [P2] **Hidden dependencies** (CDN): Are relationships between resources (ordering, cascade effects, required sequences) visible or documented?
- [P2] **Viscosity** (CDN): How many API calls or config changes are needed for a single logical change?
- [P2] **Abstraction level** (CDN): Do the API's abstractions match the consumer's mental model, or impose an unfamiliar conceptual framework?
- [P2] **Closeness of mapping** (CDN): Does the vocabulary use domain terminology consumers recognize, or internal implementation jargon?
- [P2] **Intent clarity** (SigniFYIng APIs): Does documentation, naming, and structure communicate what the API was designed to do, for whom, and in which contexts?
- [P2] **Effect match & unconscious failure risk** (SigniFYIng APIs): Could a consumer experience the API as *misused*, *misunderstood*, or *unexpected*, and could they believe they succeeded when they haven't (lenient parsing, contextually wrong defaults, invisible side effects)?
- [P2] Do API responses include appropriate `Cache-Control` directives and `ETag` or `Last-Modified` validators, and do read endpoints support conditional GET (`If-None-Match`, `If-Modified-Since`) to return `304 Not Modified` when the resource has not changed?
- [P2] Are OpenAPI `operationId` values present on every operation, unique across the entire spec, and following a stable naming convention (e.g., `{verb}{Resource}`) such that SDK generators produce predictable, non-colliding client method names that do not change when route paths are reorganized?

## Deep

- [P3] Do error messages, status codes, and pagination patterns feel intuitive and consistent enough that a new developer can integrate without reading supplementary guides?
- [P3] Do API responses include hypermedia controls — `Link` headers per RFC 8288, or embedded link objects (`_links`, `links`) — that enable clients to discover and navigate valid next states without requiring out-of-band knowledge of URI structure or calling sequences?
