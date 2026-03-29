# OPS — Operations / DevOps

## Essential

- [P0] Will this work correctly across development, staging, and production environments?
- [P0] Does the health check endpoint verify all critical dependencies (DB, Redis, external services)?
- [P0] Is there a documented disaster recovery and rollback procedure?
- [P0] Are error budgets defined, and does this change risk breaching any SLO target that would trigger a deployment freeze? *(SRE)*
- [P0] Is there a runbook for this service covering escalation paths, communication templates, and severity classification criteria for on-call responders? *(Incident management / on-call lead)*
- [P0] Are all secrets injected at runtime from a centralized vault rather than baked into images or stored in environment variable literals, with automatic rotation enabled? *(Secrets management specialist)*

## Deep-dive

- [P1] Does this change affect Docker builds, environment variables, or deployment scripts?
- [P1] Are health checks, logging, and monitoring considerations addressed?
- [P1] Is there a log aggregation and alerting system in place?
- [P1] Are there defined SLOs/SLAs with corresponding monitoring dashboards?
- [P1] Are deployment strategies (blue-green, canary) defined for zero-downtime releases?
- [P1] Are pod resource requests/limits, horizontal pod autoscaler thresholds, and disruption budgets correctly configured for this workload? *(Kubernetes/container orchestration specialist)*
- [P1] Is every infrastructure change captured in version-controlled IaC modules with a plan/apply review gate, and are there no manual drift-prone modifications? *(Infrastructure-as-code engineer)*
- [P1] Are distributed traces correlated with logs and metrics using consistent identifiers, and do dashboards cover the four golden signals (latency, traffic, errors, saturation)? *(Observability platform architect)*
- [P1] Can the deployment pipeline roll back automatically on health-check failure, and are pipeline stages idempotent so a retry never produces duplicate side effects? *(CI/CD pipeline reliability engineer)*
- [P2] Has the cost impact of new or resized resources been estimated, and are tagging policies enforced to enable accurate cost attribution? *(Cost optimization analyst / FinOps)*
- [P2] Are service-to-service communication paths secured with mutual TLS, and are network policies or service mesh traffic rules scoped to least-privilege? *(Network/service mesh engineer)*
- [P2] Has this service been subjected to controlled failure injection (e.g., pod kills, latency spikes, dependency outages) to validate graceful degradation and recovery? *(Chaos engineering practitioner)*
