---
designer_description: "When the reviewer is asked to look at what you built through database eyes, I'm the checklist that tells it what to watch for -- migration safety and reversibility, referential integrity, constraint enforcement, index coverage, connection-pool and replication health, and backup/restore discipline -- so schema changes land without breaking older app versions or losing data on rollback."
tier: Essential
---

# DB — Database

## Essential

- [P0] Are schema changes backward-compatible and migration-safe (idempotent)?
- [P0] Are backup/restore procedures automated with tested recovery, and is RPO/RTO validated via restore drills (point-in-time, cross-region)?
- [P0] Are connection-pool sizes, statement timeouts, and idle-connection reaping tuned for production concurrency and failover?
- [P0] Does the replication topology handle split-brain and convergence (primary/replica lag auto-redirect; multi-master or geo-distributed conflict resolution where applicable), with lag and divergence monitored?
- [P0] Are credentials auto-rotated, network access least-privilege, and sensitive columns encrypted at rest and masked in non-production?
- [P0] Are migrations versioned, reversible, and tested against production-sized data to catch lock contention and long-running ALTERs?
- [P0] Are database transactions scoped to the minimum necessary boundary, with idle-in-transaction and long-running transaction detection configured (e.g., idle_in_transaction_session_timeout or equivalent), so that stale transactions cannot escalate locks, block autovacuum, or exhaust connection slots?

## Standard

- [P1] Are FK constraints, cascades, and soft delete filters correctly applied?
- [P1] Does the health check execute a lightweight test query rather than testing socket connectivity only, correctly reflecting connection pool exhaustion and primary demotion in container readiness probes?
- [P1] Is test environment parity maintained (same DB engine for unit and integration tests)?
- [P1] Do critical queries have covering indexes with guardrails against full-table scans, and does ORM-generated SQL match intended plans with N+1 detection in CI?
- [P1] Is the data model normalized appropriately, with denormalization trade-offs documented and consistency ownership assigned to explicit mechanisms (FK constraints, two-phase commit, sagas, or conflict detection)?
- [P1] Are slow-query logs, lock-wait metrics, and pool saturation surfaced in dashboards with SLO-tied alerts?
- [P1] Are ORM queries efficient (joins, eager/lazy loading)?
- [P2] For time-series, append-heavy, or LSM-tree-backed workloads, are partitioning, retention/rollup, and compaction policies defined to prevent unbounded growth and read amplification?
- [P2] Are database cursors explicitly closed after use — not left dangling across transaction boundaries — to prevent cursor injection and connection exhaustion? (CWE-619)
- [P1] Is the database's consistency model (isolation level for RDBMS; eventual/causal/strong consistency for distributed stores) explicitly documented, with the application's anomaly tolerance validated — i.e., confirming that the chosen level prevents lost updates, dirty reads, or non-repeatable reads that the domain cannot tolerate?
- [P1] Are optimizer statistics refreshed after bulk data loads or significant schema changes, and does CI capture and compare query execution plans (EXPLAIN/EXPLAIN ANALYZE or equivalent) for critical queries across migrations to detect plan regressions before they reach production?
- [P1] For distributed or multi-service deployments using eventual consistency, are domain operations designed to be semantically compatible under concurrent execution — i.e., either using incremental (delta-based) updates that tolerate partial order, or explicit conflict detection/idempotency mechanisms to prevent lost updates?
- [P2] For NoSQL or document-store deployments, is transaction management explicitly configured — including conflict detection strategy (optimistic vs. pessimistic), lock granularity (document vs. field), and retry-backoff parameters — and have abort rates and P99 latency been measured under realistic concurrency levels?

## Deep

- [P3] For complex multi-table join workloads, have cardinality estimation errors been assessed (e.g., via pg_stats, EXPLAIN ANALYZE actuals vs. estimates), and has the team evaluated whether a learned or AI-assisted query optimizer would materially improve plan quality for long-tail queries?
- [P3] Is the schema designed for evolution — using additive change patterns (add columns with defaults rather than renaming, use nullable columns before adding NOT NULL), avoiding breaking changes that require coordinated deploys, and with rollback paths tested explicitly on production-scale data?
