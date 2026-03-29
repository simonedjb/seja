# DATA — Data Integrity & Privacy

## Essential

- [P0] Does this change handle personal data (PII) in compliance with GDPR/privacy requirements?
- [P0] Are cascade deletes, orphan records, and referential integrity properly managed?
- [P0] Are PII fields encrypted at rest, or is the encryption boundary clearly documented?
- [P0] Does every processing activity involving personal data have a documented lawful basis, and is the Records of Processing Activities (ROPA) updated to reflect this change?
- [P0] Are uniqueness constraints, check constraints, and foreign keys enforced at the database level rather than relying solely on application logic?
- [P0] Is user consent captured with granular purpose-scope and version-stamped, and can the system honor consent withdrawal by ceasing processing within the required timeframe?
- [P0] For any cross-border data transfer, is there a valid transfer mechanism in place (e.g., SCCs, adequacy decision, BCRs) and are data residency requirements enforced at the infrastructure level?

## Deep-dive

- [P1] Are data validation rules enforced at both the API boundary and the database level?
- [P1] Are data retention, anonymization, and right-to-deletion considerations addressed?
- [P1] Are data retention policies defined and enforced (auto-purge of old activity logs, soft-deleted records)?
- [P1] Are data pipelines idempotent and schema-versioned so that reprocessing or rollback cannot silently corrupt or duplicate downstream records?
- [P1] Is personal data minimized by default—collected only for an explicit purpose and excluded from logs, caches, and analytics unless a privacy impact assessment approves it?
- [P1] Are data classification labels (public, internal, confidential, restricted) assigned to every new or modified data element, with ownership and stewardship clearly recorded?
- [P1] Is end-to-end data lineage tracked so that the origin, transformations, and downstream consumers of every dataset are discoverable in the data catalog?
- [P1] When personal data is anonymized or replaced with synthetic data for non-production use, is re-identification risk formally assessed and kept below an acceptable threshold?
- [P2] Do audit trails capture who accessed or mutated sensitive data, and are those logs tamper-evident, retained per policy, and available for regulatory examination?
- [P3] Is there a Software Bill of Materials (SBOM) for supply chain transparency?
