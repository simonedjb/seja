---
designer_description: "When the reviewer is asked to look at what you built through operations eyes, I'm the checklist that tells it what to watch for -- environment parity across dev/staging/production, health-check depth, logging and alerting, deployment and rollback safety, SLO and error-budget impact, secrets handling, and on-call runbook coverage -- so the change survives not just the merge but the next 3 a.m. incident."
tier: Deep-dive
---

# OPS — Operations / DevOps

## Essential

- [P0] Will this work correctly across development, staging, and production environments?
- [P0] Does the health check endpoint verify all critical dependencies (DB, Redis, external services)?
- [P0] Is there a documented disaster recovery and rollback procedure?
- [P0] Are SLIs defined with both a specification (what to measure) and an implementation (how to measure it)? Are error budgets defined, and does this change risk a burn-rate that would breach the SLO window and trigger a deployment freeze?
- [P0] Is there a runbook covering escalation paths, communication templates, and severity classification for on-call?
- [P0] Are all secrets injected at runtime from a centralized vault (not baked into images or env-var literals), with automatic rotation?

## Standard

- [P1] Does this change affect Docker builds, environment variables, or deployment scripts?
- [P1] Are health checks, logging, and monitoring addressed, with a log-aggregation and alerting system in place?
- [P1] Are SLOs/SLAs defined with corresponding monitoring dashboards?
- [P1] Are deployment strategies (blue-green, canary) defined for zero-downtime releases, with automatic abort conditions tied to error-rate or latency thresholds during progressive traffic shifting?
- [P1] Are pod resource requests/limits, HPA thresholds, and disruption budgets correctly configured, and is every infrastructure change in version-controlled IaC with a plan/apply gate (no manual drift)?
- [P1] Is OTel (or equivalent) instrumentation installed and exporting to a collector? Are distributed traces correlated with logs/metrics via W3C Trace Context or equivalent, with dashboards covering the four golden signals?
- [P1] Can the pipeline roll back automatically on health-check failure, with idempotent stages (retries produce no duplicate side effects)?
- [P2] Is cost impact of new or resized resources estimated, with tagging policies enforced for cost attribution?
- [P1] For services with external dependencies, has the service been subjected to failure injection (pod kills, latency spikes, packet loss, DNS failures, dependency outages) to validate graceful degradation and automatic recovery?
- [P1] Are services configured to bind only to the required network interface (not `0.0.0.0`/all interfaces by default), and are admin and debug endpoints bound to loopback or restricted to internal networks only? (CWE-1327)
- [P1] Are deployed file and directory permissions audited so configuration files, keys, and log output are not world-readable, with ownership scoped to the service account rather than root? (CWE-276, CWE-552)
- [P1] Do processes terminate (not hang in a degraded state) when initialization fails, so container orchestrators and process supervisors can restart them rather than serving requests from a broken state? (CWE-455)
- [P2] Are runtime configuration sources (env vars, remote config APIs, feature flag services) controlled and authenticated, preventing external parties from altering system behavior without authorization? (CWE-15)
- [P1] Are alerts configured to fire only on actionable, error-budget-threatening conditions, with tuned thresholds to minimise false positives, full recall of significant events, detection time short enough to contain SLO impact, and automatic reset once the condition clears?
- [P1] Does the runbook include, or does this change update, a postmortem procedure for the failure modes it introduces — including which artifacts to collect (logs, traces, heap/thread dumps), the root-cause analysis template, and the bug-tracking system where findings are recorded?
- [P1] Are all service-to-service network paths enforced with mTLS (or equivalent mutual authentication), with certificate rotation automated and least-privilege network/mesh policies applied so no service can reach endpoints beyond its declared dependencies?
- [P1] For container-orchestrated workloads, are liveness, readiness, and startup probes configured with appropriate thresholds and independently tested — liveness conservative enough to avoid restart loops, readiness strict enough to prevent premature traffic routing, and startup probe set where slow initialisation would otherwise trigger false liveness failures?
- [P2] Are incidents and anomalies triggered by this service filed in a centralised bug-tracking system (rather than communicated informally) with structured problem reports capturing expected vs. actual behaviour, reproduction conditions, and resource context — ensuring a searchable RCA history for future recurrence?
- [P2] Does this change modify workload identity bindings, service account definitions, or RBAC role/cluster-role assignments? If so, are the permissions scoped to the minimum required, have they been reviewed against the existing threat model, and are they version-controlled in IaC?

## Deep

- [P3] Does this change introduce or increase operational toil (manual, repetitive, automatable tasks)? If so, is the toil volume measured, is it within the team's acceptable toil ceiling, and is there a backlog item to automate it?
- [P3] Is the OTel sampler strategy explicitly configured — head-based (TraceIdRatioBased or ParentBased) for low-overhead baseline coverage, or tail-based (via OTel Collector tail-sampling processor) for high-fidelity error and latency outlier capture — with the sampling rate and strategy documented and justified against cost and signal-quality requirements?
