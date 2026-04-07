# API — API Design

## Essential

- [P0] Is the endpoint RESTful, consistent with existing routes, and properly documented?
- [P0] Is every public endpoint routed through the API gateway with consistent authentication, throttling, circuit-breaking, and request-tracing policies applied?
- [P0] Is there a versioning strategy (URI path, header, or content negotiation) in place, with a documented deprecation timeline and sunset headers for retired versions?
- [P0] Are authentication tokens validated on every request, and are object-level and field-level authorization checks enforced to prevent BOLA/BFLA vulnerabilities?

## Deep-dive

- [P1] Are error responses localized, structured, and free of internal details?
- [P1] Does the request/response schema use Marshmallow validation?
- [P1] Are rate limit status headers (`X-RateLimit-Remaining`, `X-RateLimit-Reset`) returned to clients?
- [P1] Do resource URIs follow a consistent noun-based hierarchy and avoid verbs, and are HTTP methods used strictly according to their semantics (e.g., PUT for full replacement, PATCH for partial update)?
- [P1] Are query complexity limits, depth restrictions, and field-level authorization enforced to prevent abusive or over-fetching GraphQL operations?
- [P1] Are response shapes stable and predictable enough for generated SDK clients, with nullable fields explicitly marked and envelope structures consistent across endpoints?
- [P1] Are response payloads optimized with pagination, sparse fieldsets, or compression, and are N+1 query patterns eliminated on the server side?
- [P1] Are breaking changes detected automatically via contract tests or schema diff checks in CI, and is there a compatibility policy (e.g., additive-only) that governs schema evolution?
- [P2] Is the OpenAPI spec browsable via a documentation UI (Swagger UI, ReDoc)?
- [P2] Are example request/response payloads included in the API spec?
- [P2] Does every endpoint have a human-readable description, parameter constraints, and at least one success and one error example documented inline in the spec?
- [P2] **Consistency** (CDN): Do similar API operations use similar parameter names, response shapes, and error formats, so that learning one endpoint transfers to others?
- [P2] **Role-expressiveness** (CDN): Can a developer infer the purpose of an endpoint, parameter, or response field from its name and position alone, without reading documentation?
- [P2] **Error-proneness** (CDN): Does the API design invite mistakes -- e.g., easily confused parameter names, missing required field validation, or destructive operations without confirmation?
- [P2] **Hidden dependencies** (CDN): Are relationships between API resources (ordering constraints, cascade effects, required sequences) visible in the API surface or documented, not hidden?
- [P2] **Viscosity** (CDN): How many API calls or configuration changes are needed to make a single logical change? High viscosity discourages legitimate modifications.
- [P2] **Abstraction level** (CDN): Do the API's abstractions match the consumer's mental model -- or must they learn an unfamiliar conceptual framework to use the API correctly?
- [P2] **Closeness of mapping** (CDN): Does the API vocabulary use domain terminology that consumers recognize, or does it impose internal implementation jargon that requires translation?
- [P2] **Intent clarity** (SigniFYIng APIs): Does the API's documentation, naming, and structure clearly communicate what it was designed to do, for whom, and in which contexts -- or must the consumer reverse-engineer design intent from observed behavior?
- [P2] **Effect match** (SigniFYIng APIs): Could a consumer experience the API's behavior as *misused* (wrong assumptions about defaults or context), *misunderstood* (incompatible mental model), or *unexpected* (affordance differs from expectations) -- and would they notice?
- [P2] **Unconscious failure risk** (SigniFYIng APIs): Could a consumer believe they succeeded when they haven't -- e.g., lenient parsing silently converts invalid input, default values are contextually wrong but produce no error, or side effects are invisible?
- [P3] Do error messages, status codes, and pagination patterns feel intuitive and consistent enough that a new developer can integrate without reading supplementary guides?
