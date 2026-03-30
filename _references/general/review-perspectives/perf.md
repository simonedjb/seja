# PERF — Performance

## Essential

- [P0] Are there N+1 queries, unbounded loops, or missing database indexes?
- [P0] Will this degrade under realistic load (concurrent users, large datasets)?
- [P0] Are queries using appropriate indexes, and have slow-query logs been reviewed for full table scans or lock contention under write-heavy workloads?
- [P0] Has the system been profiled under sustained peak load to identify throughput ceilings, and are graceful degradation paths in place?
- [P0] Are shared-state access patterns free of lock contention, and are thread pools / async task queues sized to avoid saturation or starvation?

## Deep-dive

- [P1] Are expensive operations cached, paginated, or deferred appropriately?
- [P1] Are HTTP cache headers (`Cache-Control`, `ETag`, `Last-Modified`) set on read-heavy endpoints?
- [P1] Is application-level caching (Redis, in-memory) used for expensive queries or computed data?
- [P1] Are critical rendering path resources minimized, and are layout shifts (CLS) and largest contentful paint (LCP) within acceptable thresholds?
- [P1] Are cacheable assets served from edge locations, and are cache invalidation strategies correctly scoped to avoid serving stale content?
- [P1] Are object lifetimes and allocation patterns reviewed for excessive GC pressure, memory leaks, or unbounded growth in long-lived collections?
- [P1] Are round-trips minimized through request batching, connection reuse (keep-alive, HTTP/2 multiplexing), and strategic payload compression?
- [P1] Are mobile-specific constraints addressed, including reduced CPU/GPU budgets, battery impact of background work, and network variability (3G/LTE transitions)?
- [P2] Are frontend bundle sizes monitored, and is there a performance budget?
- [P2] Are prefetch/preload hints used for predictable navigation paths?
- [P2] Are latency percentiles (p50, p95, p99) tracked per endpoint, and are alerts configured for SLO breaches rather than only averages?
- [P2] Is there a capacity model that maps expected traffic growth to resource requirements, and are auto-scaling policies validated against realistic demand curves?
