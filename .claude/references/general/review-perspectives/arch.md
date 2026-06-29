---
designer_description: "When the reviewer is asked to look at what you built through architecture eyes, I'm the checklist that tells it what to watch for -- layer boundaries, separation of concerns, dependency direction, bounded-context respect, failure-mode resilience, and whether the shape you chose is the simplest that meets the requirement -- so structural erosion gets caught at review time instead of at the next refactor."
tier: Essential
---

# ARCH — Architecture

## Essential

- [P0] Does this follow established layer boundaries (API / service / model), avoiding circular dependencies and preserving separation of concerns?
- [P0] Are bounded contexts explicitly defined, with aggregate boundaries respected and no domain leakage across contexts?
- [P0] Under partitions or partial failures, does the system preserve its documented consistency/availability guarantees per its CAP/PACELC trade-offs, and does it degrade gracefully (returning partial results or cached data) rather than failing hard when a dependency becomes unavailable?

## Standard

- [P1] Is the solution the simplest that meets the requirement?
- [P2] Are feature flags available for safe incremental rollouts of this change?
- [P1] Does the service boundary align with a single business capability, with versioned inter-service contracts for independent deployability?
- [P1] Are state-changing operations captured as domain events, with a strategy for ordering, idempotency, and schema evolution?
- [P1] Are infrastructure concerns (networking, storage, compute scaling) decoupled from application logic through platform abstractions?
- [P1] Are module boundaries enforced at build time (visibility rules, dependency constraints), and is the dependency graph acyclic after this change?
- [P1] Are timeout policies, retry budgets, and backpressure mechanisms explicitly documented at each service interface boundary, and are circuit breakers and bulkheads configured to isolate failure blast radius?
- [P2] Is the caching strategy documented -- what is cached, TTL, invalidation triggers?
- [P2] Has technical debt introduced or resolved been catalogued, with a payoff timeline tied to roadmap items?
- [P2] If this touches legacy components, is there a strangler-fig or anti-corruption layer isolating new code from legacy coupling?
- [P2] **Consistency** (CDN): Do similar architectural patterns (error handling, DI, config) use similar structures across modules?
- [P2] **Role-expressiveness** (CDN): Can a developer infer a module's responsibility from its name, location, and public interface?
- [P2] **Error-proneness** (CDN): Does the architecture invite structural mistakes (wrong-layer logic, easy cycles)?
- [P2] **Hidden dependencies** (CDN): Are cross-module dependencies, shared state, and implicit contracts visible or documented?
- [P2] **Viscosity** (CDN): How much effort to make a change that respects the architecture vs. taking a shortcut?
- [P2] Are cyclomatic complexity and cognitive complexity scores tracked per module, with hard limits triggering refactor obligations to prevent untestable and maintenance-hostile control flow growth? (CWE-1121, CWE-1122)
- [P2] Are cross-cutting concerns (logging, auth, serialization, retry logic) implemented as transverse components or shared infrastructure, rather than duplicated across layers or assigned to a single horizontal layer that forces skip-calls from all other layers? (CWE-1092, CWE-1054)
- [P2] Are module-level cohesion scores (LCOM-family metrics or equivalent tooling such as ArchUnit's `noClasses().should().bePubliclyAccessible()` responsibility rules) tracked alongside coupling metrics (Ce, Ca, CBO), with documented split obligations triggered when a module's responsibility set is detected as disjoint?
- [P2] Are architectural structural invariants (layer boundaries, dependency direction, module visibility rules, acyclic dependency constraints) enforced automatically at build time via fitness functions or dependency-constraint tools (e.g., ArchUnit, Lattix, Structure101), so that violations surface as build failures rather than being discovered at review or post-incident?
- [P2] Are significant architectural decisions made in this change captured as Architecture Decision Records (ADRs) with explicit context, decision text, considered alternatives, consequences, and current status, enabling future reviewers to understand why the current structure exists without requiring access to the original decision-makers?
- [P2] Does the service or module boundary align with the ownership boundary of a single team, such that routine feature delivery within this service does not require cross-team coordination, and changes to internal implementation do not force interface negotiations with other teams?

## Deep

- [P3] Can the core design be explained via fundamental trade-offs (latency vs. throughput, consistency vs. availability, coupling vs. autonomy) with explicit justification?
- [P3] Are omnipresent concerns (logging, security enforcement, telemetry, internationalisation) assigned to a transverse vertical component (sidecar pattern) rather than to a horizontal layer, so that all other layers access them via adjacent-layer calls rather than generating ILD-violating skip-calls across the abstraction stack?
- [P3] Has each layer's public interface been explicitly documented with a stability contract (versioning, deprecation policy, or change-notification obligations), such that internal implementation changes do not propagate to client layers and consumers can rely on interface stability across releases?
