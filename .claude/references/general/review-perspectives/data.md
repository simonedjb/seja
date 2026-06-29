---
designer_description: "When the reviewer is asked to look at what you built through data-integrity-and-privacy eyes, I'm the checklist that tells it what to watch for -- PII handling under GDPR/CCPA, encryption at rest, cascade and referential-integrity rules, consent capture and withdrawal, retention and right-to-deletion, cross-border transfer controls, and audit-log completeness -- so the data your feature touches stays lawful, classified, and traceable end-to-end."
tier: Deep-dive
---

# DATA — Data Integrity & Privacy

## Essential

- [P0] Does this change handle personal data (PII) in compliance with GDPR/privacy requirements?
- [P0] Are cascade deletes and referential integrity changes privacy-safe — do they preserve, not silently destroy, consent records, audit trails, and lineage entries?
- [P0] Are PII fields encrypted at rest, or is the encryption boundary clearly documented?
- [P0] Does every processing activity involving personal data have a documented lawful basis, with ROPA updated to reflect this change?
- [P0] Are uniqueness constraints, check constraints, and foreign keys enforced at the database level rather than in application logic alone?
- [P0] Is user consent captured with granular purpose-scope and version-stamped, with withdrawal honored within the required timeframe?
- [P0] For cross-border transfers, is a valid mechanism in place (SCCs, adequacy decision, BCRs) with data residency enforced at the infrastructure level?

## Standard

- [P1] Are data validation rules enforced at both the API boundary and the database level?
- [P1] Are retention policies defined and enforced (auto-purge of old activity logs, soft-deleted records)?
- [P1] Are data pipelines idempotent and schema-versioned so reprocessing or rollback cannot silently corrupt or duplicate downstream records?
- [P1] Is personal data minimized by default -- collected only for an explicit purpose and excluded from logs, caches, and analytics unless a PIA approves it?
- [P1] Are data classification labels (public, internal, confidential, restricted) assigned to every new or modified data element with ownership recorded — prerequisite for answering the [P0] PII compliance question?
- [P1] Is end-to-end data lineage tracked so origin, transformations, and downstream consumers are discoverable in the data catalog?
- [P1] When personal data is anonymized, synthesized, or aggregated — including for non-production use, analytics dashboards, and ML training datasets — is re-identification risk formally assessed using a specified methodology (k-anonymity minimum) against a documented acceptable threshold?
- [P1] Do audit trails capture who accessed or mutated sensitive data, are they tamper-evident and cryptographically integrity-protected, and are they retained per the documented retention policy for regulatory examination?
- [P1] Is sensitive data (tokens, PII, passwords) excluded from URLs (query strings), HTTP `Referer` headers, redirect parameters, and request logs — routed only via request body or secure headers? (CWE-201)
- [P1] Do responses containing sensitive data set `Cache-Control: no-store, no-cache` and `Pragma: no-cache` to prevent caching by browsers, CDN edge nodes, and intermediate proxies? (CWE-524)
- [P2] Are file metadata, document properties (EXIF, PDF author/producer, Office `lastModifiedBy`), and embedded thumbnails stripped before publishing artifacts that may reveal author identity, internal paths, or software version? (CWE-1230)
- [P1] Does this change introduce or modify a relationship with a third-party data processor, and if so, is a compliant GDPR Art. 28 Data Processing Agreement (DPA) in place that covers the new or changed processing activity, with purpose limitation and sub-processor clauses documented?
- [P1] Is there a documented incident response and breach notification procedure that covers this feature's personal data elements, confirms the 72-hour supervisory authority notification window (GDPR Art. 33) is operationally achievable, and specifies the data-subject notification threshold (GDPR Art. 34 / CCPA § 1798.150)?
- [P1] Where feasible, is pseudonymization applied as a privacy-by-design technical measure to reduce the direct linkability of personal data to data subjects, and is pseudonymized data clearly distinguished from anonymized data in the data model documentation — with pseudonymized data still treated as personal data under GDPR Recital 26?
- [P1] Does this change involve processing likely to result in high risk to data subjects (profiling at scale, sensitive data categories, systematic monitoring, new technologies per GDPR Art. 35(1))? If yes, has a Data Protection Impact Assessment (DPIA) been conducted, documented, and approved by the Data Protection Officer (or equivalent) before processing begins?
- [P1] For personal data introduced or modified by this change, are the data subject rights of access (Art. 15), rectification (Art. 16), erasure (Art. 17), restriction (Art. 18), portability (Art. 20), and objection (Art. 21) operationally supportable — meaning the data can be located, exported in a structured machine-readable format, corrected, restricted, and deleted within the statutory deadlines without requiring architectural redesign?
- [P2] Is the storage mode of personal data documented — specifying whether data at rest is stored in a form inaccessible to the service provider (encrypted under a key held exclusively by the data subject or a trusted third party, i.e., "hidden" per Ta 2018) or accessible to the service provider (provider-held key, "unhidden")? If unhidden, is the service-provider access need justified by a legitimate service or accountability purpose?

## Deep

- [P3] For high-risk or architecturally complex processing, has formal or semi-formal policy-to-architecture conformance been verified — confirming that the system's data access, storage-mode, deletion-delay, and forwarding behaviors match the declared data protection policy (privacy conformance ⊳_priv, DPR conformance ⊳_dpr, and functional conformance ⊳_func as defined in Ta 2018), or that deviations are documented with risk acceptance?
- [P3] For statistical outputs, aggregate analytics dashboards, and ML model outputs derived from personal data, are formal re-identification risk bounds documented — specifying the methodology used (k-anonymity, l-diversity, differential privacy budget ε), the auxiliary information considered in the adversary model, and confirmation that the bounds meet the documented acceptable threshold?
