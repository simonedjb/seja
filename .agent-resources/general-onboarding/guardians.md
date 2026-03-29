# GRD — Guardians

> QA engineers, security engineers, tech leads, and engineering managers who ensure quality, alignment, and governance.

## Roles

- QA / Test engineer
- Security engineer
- Tech lead
- Engineering manager
- Release manager
- Compliance officer

## Layer 1 — Role-Specific Onboarding Content

### Essential (all Guardians must cover)

- **Review perspective framework**: The structured review system (`general-review-perspectives.md`) with its 16 perspectives, priority tiers (Essential/Deep-dive), and conflict resolution rules. This is the Guardian's primary tool.
- **Test strategy and coverage**: Unit, integration, e2e boundaries. Coverage thresholds. How to run tests, interpret results, and identify gaps. Validation scripts in `.claude/skills/scripts/`.
- **Security policies**: Authentication/authorization model, input validation rules, secrets management, dependency auditing. Key reference: `general-review-perspectives/sec.md`.
- **Quality gates and CI/CD**: What checks run on every commit, what blocks a merge, deployment approval workflow.
- **Incident response**: How incidents are detected, escalated, and resolved. Postmortem process.
- **Code review process**: Review expectations, turnaround time, required approvals, constructive feedback norms. How to use `/check review` for structured reviews.

### Deep-dive (load for thorough onboarding or when Guardian is the primary role)

- **Compliance requirements**: Regulatory obligations (GDPR, SOC 2, HIPAA, etc.), audit trail expectations, data retention policies.
- **Technical debt inventory**: Known debt areas, severity classification, payoff timelines tied to roadmap.
- **Performance baselines**: Key SLAs/SLOs, load testing results, known bottlenecks, monitoring dashboards.
- **Governance and approval processes**: Who approves what, escalation paths, change advisory board processes.
- **Team health metrics**: Velocity trends, cycle time, deployment frequency, DORA metrics.
- **Cross-team dependencies**: Other teams that depend on or are depended upon, API contracts, SLA agreements.

## Recommended First Tasks by Level

| Level | First Task | Goal |
|-------|-----------|------|
| L1 | Write tests for an untested module | Learn the test framework, codebase structure |
| L2 | Run `/check validate` and triage findings | Understand current quality state, learn validation tools |
| L3 | Conduct a structured code review using `/check review` | Learn the review perspective framework in practice |
| L4 | Audit the security posture of a critical user flow | Map security boundaries, identify gaps |
| L5 | Review and improve the team's development process | Understand team dynamics, propose improvements |

## Key Reference Files

- `general-review-perspectives.md` (review framework index)
- `general-review-perspectives/sec.md` (security perspective)
- `general-review-perspectives/test.md` (testability perspective)
- `general-review-perspectives/dx.md` (developer experience perspective)
- `general-review-perspectives/data.md` (data integrity & privacy perspective)
- `.claude/skills/scripts/` (validation and analysis scripts)
- `.claude/agents/code-reviewer.md` (code review agent prompt)
