# SEC — Security

## Essential

- [P0] Does this change introduce or widen an attack surface (injection, XSS, CSRF, auth bypass)?
- [P0] Are inputs validated at the boundary? Are outputs sanitized before rendering?
- [P0] Are secrets, tokens, and credentials handled according to project-security-checklists.md?
- [P0] Can any user-controlled input reach OS commands, SQL queries, or template engines without parameterization or sandboxing? *(Penetration tester)*
- [P0] Are authentication and session management flows resistant to token leakage, session fixation, and replay attacks? *(Application security engineer)*
- [P0] Is the authorization model enforced server-side for every state-changing operation, including horizontal privilege escalation between tenants or resource owners? *(Identity/access management expert)*

## Deep-dive

- [P1] Are rate limits applied per authenticated user (not just IP), and are lockout mechanisms in place for repeated auth failures?
- [P1] Are dependencies audited for known vulnerabilities (`pip audit`, `npm audit`) before deployment?
- [P1] Are cryptographic primitives current (no MD5/SHA-1 for integrity, no ECB mode), keys rotated on schedule, and random values sourced from a CSPRNG? *(Cryptography specialist)*
- [P1] Are cloud resource permissions scoped to least privilege, and are storage buckets, queues, and endpoints protected against public exposure or misconfigured IAM policies? *(Cloud security architect)*
- [P1] Are third-party dependencies pinned to exact versions with verified checksums, and is the CI/CD pipeline protected against dependency confusion and compromised build tooling? *(Supply chain security analyst)*
- [P1] Has a threat model been updated to reflect new trust boundaries, data flows, or elevated-privilege components introduced by this change? *(Threat modeler)*
- [P1] Is personal or sensitive data minimized at collection, encrypted at rest and in transit, and purgeable within retention/deletion SLAs required by GDPR Art. 17 and CCPA sec. 1798.105? *(Privacy engineer)*
- [P2] Is there account enumeration protection on login/register/reset endpoints?
- [P2] Does the change maintain audit-log completeness (who, what, when, from-where) required by SOC 2 CC7/CC8 and ISO 27001 A.12.4 controls? *(Security compliance officer)*
- [P2] Are sufficient detection signals (structured logs, alerts, correlation IDs) in place so that exploitation of this code path would be identified and triaged within the defined SLA? *(Incident response lead)*
- [P3] Are API versioning or deprecation headers in place to prevent clients from using stale, insecure endpoints?
