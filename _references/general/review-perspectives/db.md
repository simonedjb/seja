# DB — Database

## Essential

- [P0] Are schema changes backward-compatible and migration-safe (idempotent)?
- [P0] Are backup/restore procedures automated with tested recovery?
- [P0] Are connection pool sizes, statement timeouts, and idle-connection reaping tuned for production concurrency and failover scenarios?
- [P0] Does the replication topology handle split-brain scenarios, and are read-replica lag thresholds monitored with automatic traffic redirection on excessive lag?
- [P0] Are database credentials rotated automatically, is network access restricted to least-privilege, and are sensitive columns encrypted at rest and masked in non-production environments?
- [P0] Is the backup RPO/RTO documented and validated through periodic restore drills, including point-in-time recovery and cross-region restore?

## Deep-dive

- [P1] Are FK constraints, cascades, and soft delete filters correctly applied?
- [P1] Does the health check endpoint verify database responsiveness (not just return a static status)?
- [P1] Is test environment parity maintained (same DB engine for unit and integration tests)?
- [P1] Do critical queries have covering indexes, and are there guardrails against full-table scans on large tables (e.g., missing WHERE clauses, implicit type casts that prevent index use)?
- [P1] Is the data model normalized appropriately, and are denormalization trade-offs explicitly documented with clear ownership of consistency guarantees?
- [P1] Are migrations versioned, reversible, and tested against a production-sized dataset to catch lock contention and long-running ALTER TABLE issues?
- [P1] Does the ORM-generated SQL match intended query plans, and are N+1 query patterns detected in CI (e.g., via query-count assertions or log analysis)?
- [P1] Are slow-query logs, lock-wait metrics, and connection-pool saturation surfaced in dashboards with alerting thresholds tied to SLOs?
- [P2] Are queries using the ORM efficiently (joins, eager/lazy loading)?
- [P2] For time-series or append-heavy workloads, are partitioning strategies and retention/rollup policies defined to prevent unbounded table growth?
