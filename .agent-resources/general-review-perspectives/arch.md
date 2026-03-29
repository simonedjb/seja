# ARCH — Architecture

## Essential

- [P0] Does this follow the established layer boundaries (API / service / model)?
- [P0] Does it avoid circular dependencies and maintain separation of concerns?
- [P0] Are bounded contexts explicitly defined, and does this change respect aggregate boundaries without leaking domain concepts across contexts? *(DDD practitioner)*
- [P0] Under network partitions or partial failures, does the system preserve its consistency/availability guarantees as defined by its CAP/PACELC trade-off choices? *(Distributed systems engineer)*

## Deep-dive

- [P1] Is the solution the simplest that meets the requirement?
- [P1] Is there a feature flag mechanism for safe incremental rollouts?
- [P1] Are error tracking and failure categorization centralized (e.g., Sentry, custom aggregation)?
- [P1] Does the service boundary align with a single business capability, and are inter-service contracts versioned to allow independent deployability? *(Microservices architect)*
- [P1] Are state-changing operations captured as domain events, and is there a clear strategy for event ordering, idempotency, and schema evolution? *(Event-driven systems specialist)*
- [P1] Are infrastructure concerns (networking, storage, compute scaling) decoupled from application logic through well-defined platform abstractions? *(Platform/infrastructure architect)*
- [P1] Are module boundaries enforced at build time (e.g., visibility rules, dependency constraints), and does the dependency graph remain acyclic after this change? *(Modularity/dependency management expert)*
- [P1] Has the failure mode been tested under adverse conditions (dependency outage, resource exhaustion, clock skew), and are circuit breakers, bulkheads, or retry budgets in place? *(Resilience/chaos engineering advocate)*
- [P2] Is the caching strategy documented — what is cached, TTL, invalidation triggers?
- [P2] Has the technical debt introduced (or resolved) by this change been catalogued, and is there a payoff timeline tied to upcoming roadmap items? *(Technical debt strategist)*
- [P2] If this change touches legacy components, is there a strangler-fig or anti-corruption layer strategy in place to isolate new code from legacy coupling? *(Legacy modernization specialist)*
- [P3] Can the core design be explained in terms of fundamental trade-offs (latency vs. throughput, consistency vs. availability, coupling vs. autonomy) with explicit justification for each choice? *(System design interviewer / first-principles thinker)*
