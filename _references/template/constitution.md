# TEMPLATE - PROJECT CONSTITUTION

> **How to use this template:** Copy this file to `project/constitution.md` and fill in the values for your project. This file declares immutable principles that override all other guidance. Agents must never violate these without explicit user override.
>
> The constitution is loaded first by pre-skill, before conventions or any other reference file. Rules here take precedence over everything else.

---

## Project Identity

{{PROJECT_NAME}} -- {{one-sentence project mission}}.

---

## Non-Negotiable Technical Principles

<!-- List the architectural invariants that must hold across all changes. These are not aspirational -- they are hard rules. -->

| # | Principle | Rationale |
|---|-----------|-----------|
| T1 | {{e.g., All data mutations go through the service layer -- no direct model access from API routes}} | {{e.g., Ensures business logic is testable and HTTP-agnostic}} |
| T2 | {{e.g., Every API endpoint returns a consistent response envelope via response builders}} | {{e.g., Frontend relies on predictable response shape}} |
| T3 | {{e.g., No raw SQL outside of migration files -- all queries go through the ORM}} | {{e.g., Prevents SQL injection and ensures schema consistency}} |

---

## Non-Negotiable Quality Principles

<!-- These are quality gates that cannot be bypassed. -->

| # | Principle | Rationale |
|---|-----------|-----------|
| Q1 | {{e.g., No code ships without automated tests covering the primary path}} | {{e.g., Regression prevention is non-negotiable}} |
| Q2 | {{e.g., All user-facing text must be internationalized -- no hardcoded strings}} | {{e.g., Multi-language support is a core requirement}} |
| Q3 | {{e.g., Accessibility (WCAG AA) is required for all interactive elements}} | {{e.g., Legal compliance and inclusive design}} |

---

## Security Invariants

<!-- Security rules that must never be relaxed without explicit sign-off. -->

| # | Invariant | Rationale |
|---|-----------|-----------|
| S1 | {{e.g., All endpoints require authentication unless explicitly marked public in the route decorator}} | {{e.g., Secure by default}} |
| S2 | {{e.g., PII must be encrypted at rest and masked in non-production environments}} | {{e.g., GDPR/compliance requirement}} |
| S3 | {{e.g., No secrets in source code -- all credentials come from environment variables}} | {{e.g., Prevents credential leaks}} |

---

## Compliance Requirements

<!-- Regulatory or contractual obligations. Leave empty if none apply. -->

| # | Requirement | Regulation/Contract |
|---|-------------|-------------------|
| C1 | {{e.g., User data must not leave the EU region}} | {{e.g., GDPR data residency}} |
| C2 | {{e.g., Audit logs must be retained for 7 years}} | {{e.g., SOC 2 compliance}} |

---

## Enforcement

- These principles are loaded into every agent context via pre-skill.
- `/check validate` verifies conformance against the agent-facing constraints derived from this document.
- Violations discovered during `/check review` or `/check preflight` are classified as **blocking** -- they must be resolved before commit.
- To amend this constitution, the change must be explicitly approved by the project lead and documented in the changelog below.

---

## Changelog

<!-- Record amendments here. The constitution should change rarely. -->

### v1 -- {{YYYY-MM-DD}}
- Initial constitution created via `/design`.
