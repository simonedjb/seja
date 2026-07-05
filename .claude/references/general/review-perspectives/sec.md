---
designer_description: "When the reviewer is asked to look at what you built through security eyes, I'm the checklist that tells it what to watch for -- attack surfaces, input validation, secret handling, auth and session integrity, least-privilege authorization, and dependency or supply-chain exposure -- so the findings that come back separate the things that would block a release from the ones you can safely defer."
tier: Essential
---

# SEC — Security

## Essential

- [P0] Does this introduce or widen an attack surface (injection, XSS, CSRF, auth bypass)?
- [P0] Are inputs validated at the boundary? Outputs sanitized before rendering?
- [P0] Are secrets, tokens, and credentials handled per product-design/security-checklists.md?
- [P0] Can user-controlled input reach OS commands, SQL queries, or template engines without parameterization or sandboxing?
- [P0] Are auth/session flows resistant to token leakage, fixation, and replay, and is authorization enforced server-side for every state-changing op (incl. horizontal escalation between tenants)?

## Standard

- [P1] Are rate limits applied per authenticated user (not just IP), with lockout on repeated auth failures?
- [P1] Are dependency vulnerability audits automated in CI with findings at or above a configurable severity threshold blocking the build, not run as a manual pre-deployment step?
- [P1] Are cryptographic primitives current (no MD5/SHA-1 for integrity, no ECB), keys rotated on schedule, random values from a CSPRNG?
- [P1] Are cloud permissions scoped to least privilege, with buckets, queues, and endpoints protected against public exposure or IAM misconfig?
- [P1] Are dependencies pinned to exact versions with verified checksums, and is CI/CD protected against dependency confusion and compromised build tooling?
- [P1] Is there a current artifact (DFD, architecture diagram, or annotated design doc) that shows data flows across trust boundaries, and has it been reviewed to enumerate new threats introduced by this change?
- [P1] Is personal/sensitive data minimized at collection, encrypted at rest and in transit, and purgeable within GDPR Art. 17 / CCPA 1798.105 SLAs?
- [P1] Are audit-log completeness (who, what, when, from-where per SOC 2 CC7/CC8, ISO 27001 A.12.4) and detection signals (structured logs, alerts, correlation IDs) sufficient to triage exploitation within SLA?
- [P1] Is deserialized data from untrusted sources (JSON, XML, pickle, Java serialization, YAML) validated against an explicit allowlist of safe types before use? (CWE-502)
- [P1] Are file upload endpoints restricted by content type (magic-byte MIME detection, not just Content-Type header), file extension denylist, maximum size, and path — with uploaded files stored outside the web root and never executed? (CWE-434, CWE-22)
- [P1] Is multi-factor authentication required for all privileged or sensitive operations (admin access, credential changes, high-value transactions), not just initial login? (CWE-308)
- [P1] Do server-side sessions expire after a configurable idle timeout, and are session tokens invalidated on logout, privilege change, and password reset? (CWE-613)
- [P1] Is log output neutralized to prevent CRLF injection (log forging) and to strip or escape control characters before writing to logs or HTTP response headers? (CWE-93, CWE-117)
- [P1] Are all security-sensitive checks (authorization, input validation, access control) performed on canonicalized, fully decoded input — not raw strings — to prevent bypass via double-encoding, unicode normalization, or path traversal equivalence? (CWE-551, CWE-179, CWE-22)
- [P2] Is there account enumeration protection on login/register/reset endpoints?
- [P2] Are constant-time comparison functions used for secret-bearing comparisons (HMAC verification, token equality) to prevent timing side-channel attacks? (CWE-208)
- [P2] Do URL redirects validate the target against an allowlist of trusted domains, preventing open redirect abuse in phishing and OAuth flows? (CWE-601)
- [P2] Are all web responses served with `X-Frame-Options: DENY` or an equivalent `Content-Security-Policy: frame-ancestors` directive to prevent clickjacking? (CWE-1021)
- [P2] Are temporary files created with secure permissions (not world-readable) in a private directory, and cleaned up deterministically on process exit? (CWE-378, CWE-379)
- [P1] Does user-controlled input reach URL fetch, DNS resolution, or outbound network requests without strict allowlist validation of scheme, host, and port — preventing SSRF attacks against cloud metadata endpoints, internal services, and localhost? (OWASP A10:2021)
- [P1] Is infrastructure-as-code (Terraform, Helm, Kubernetes manifests, CloudFormation) scanned for security misconfigurations (open ingress rules, privileged containers, public storage buckets) by an automated tool (Checkov, tfsec, kube-score) as a CI gate before deployment? (OWASP A05:2021, NIST CM-6)
- [P2] Are alerting rules or anomaly detection thresholds wired to the security-relevant events introduced by this change (new auth flows, sensitive data access, privilege escalation paths), such that an exploitation attempt would produce a detectable signal within the incident response SLA? (NIST SI-4, SOC 2 CC7.2)
- [P2] Is data collected under a stated purpose technically restricted from flowing into systems, analytics pipelines, or processes serving a different purpose — through API scopes, access policies, or data-flow boundaries — preventing silent purpose creep? (GDPR Art. 5(1)(b), NIST PT-2)

## Deep

- [P3] Has a STRIDE analysis been performed for each new or modified trust boundary crossing in the current DFD or architecture artifact, with threats enumerated, rated, and either mitigated or formally accepted in the threat model record?
- [P3] Are parser-heavy or format-conversion codepaths (XML, JSON, image, PDF, archive) covered by a fuzzing harness, property-based test suite, or chaos-style input mutation campaign targeting malformed and adversarially crafted inputs? (CWE-20, NIST SA-11(8))
