---
designer_description: "When the reviewer is asked to look at what you built through performance eyes, I'm the checklist that tells it what to watch for -- N+1 queries, unbounded loops, missing indexes, cache strategy, bundle weight, and how the change holds up under realistic concurrency and peak load -- so you hear back where the code will slow down before users do."
tier: Deep-dive
---

# PERF — Performance

## Essential

- [P0] Are there N+1 queries or unbounded loops in the change?
- [P0] Will this degrade under realistic load (concurrent users, large datasets)?
- [P0] Are queries using appropriate indexes, with slow-query logs reviewed for full scans or lock contention?
- [P0] Has the system been profiled under sustained peak load to identify throughput ceilings and graceful degradation paths?
- [P0] Are shared-state access patterns free of lock contention, with thread pools / async queues sized to avoid saturation?
- [P0] Does a performance baseline (profiling trace, benchmark results, or load test snapshot) exist for the specific code path being changed, and has the change been measured against it to confirm no throughput or latency regression?

## Standard

- [P1] Are expensive operations cached, paginated, or deferred appropriately?
- [P1] Are HTTP cache headers (`Cache-Control`, `ETag`, `Last-Modified`) set on read-heavy endpoints, and is app-level caching (Redis, in-memory) used for expensive queries?
- [P1] Are critical-path resources minimized, with LCP ≤ 2.5s, CLS ≤ 0.1, and INP ≤ 200ms measured at the p75 field-data level?
- [P1] Are cacheable assets served from edge locations, with invalidation scoped to avoid stale content?
- [P1] Are object lifetimes and allocations reviewed for GC pressure, leaks, or unbounded growth in long-lived collections?
- [P1] Are round-trips minimized via request batching? Is connection reuse enabled (keep-alive / HTTP/2 multiplexing)? Is payload compressed (gzip/Brotli)?
- [P1] Are mobile constraints addressed (CPU/GPU budgets, battery, 3G/LTE variability)?
- [P1] Are frontend bundle sizes enforced against a performance budget in CI (e.g., ≤ 150 KB JS transferred), with prefetch/preload hints used for predictable navigation?
- [P1] Are latency percentiles (p50, p95, p99) tracked per endpoint, with SLO-breach alerts rather than averages?
- [P2] Is there a capacity model mapping traffic growth to resources, validated against real historical traffic distributions, with auto-scaling load-tested at projected peak?
- [P1] Are regular expressions reviewed for catastrophic backtracking (ReDoS), with polynomial-complexity patterns bounded by length guards, timeouts, or replacement with linear-time automata? (CWE-1333)
- [P1] Is blocking I/O (synchronous filesystem, DNS, or database calls) avoided in single-threaded non-blocking runtimes (Node.js event loop, Python asyncio, reactive streams), with all I/O performed via non-blocking equivalents? (CWE-1322)
- [P2] Are all resource acquisitions (file handles, sockets, database cursors, thread-pool slots) bounded by explicit limits and released deterministically via `finally`, `with`, or RAII — not relying on GC collection? (CWE-770, CWE-772)
- [P1] Is the cache eviction policy explicitly chosen and appropriate for the access-pattern distribution (e.g., LRU for recency-skewed workloads, score-based or LFU for value/size-heterogeneous caches), and is the choice documented with rationale?
- [P1] Are cache TTL values matched to data freshness requirements, with stale-on-expiry behavior explicitly handled (e.g., background refresh, stale-while-revalidate) and cache volatility on restart documented as a known constraint for in-memory caches?
- [P2] Is cache effectiveness measured via hit ratio telemetry (per-cache-level, not just aggregate), with a defined SLO threshold (e.g., hit ratio ≥ 80%) and an alert that fires when sustained hit-ratio degradation is detected?
- [P1] Is the algorithmic complexity of new or changed logic documented and appropriate for expected input sizes, with any O(n²) or worse complexity explicitly justified or refactored when input scale warrants it?

## Deep

- [P3] Have profiling flame graphs (or equivalent hotspot traces) been generated for the hot path(s) affected by this change, reviewed to confirm that CPU time distribution matches architectural expectations, and attached to the review artifact?
- [P3] For systems where cache hit ratio is a primary performance constraint, has the deployed eviction strategy been benchmarked against a theoretical optimum (e.g., Belady's bound or 2D-knapsack approximation) to quantify the efficiency gap and confirm it is within acceptable margins?
