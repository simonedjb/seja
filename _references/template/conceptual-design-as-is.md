# TEMPLATE — CONCEPTUAL DESIGN AS-IS

<!-- maintained-by: agent (post-skill) -->

> **How to use this template:** This file reflects what the code **currently implements**. Updated automatically by post-skill after plan execution. For the target design, see `project/design-intent-to-be.md`.
>
> For the changelog tracking how this design has evolved, see `project/cd-as-is-changelog.md`.
>
> For implementation details, see `project/backend-standards.md` and `project/frontend-standards.md`.

---

## 1. Platform Purpose

> Describe in 2-3 paragraphs: What does this platform do? Who is it for? What problem does it solve?

### Design Philosophy

> If the platform follows a specific design philosophy or methodology, document it here. This helps ensure all design decisions align with the platform's core intent.

---

## 2. Entity Hierarchy

> Map out the primary entities and their relationships. Use an ASCII tree to show containment/hierarchy:

```
{{TopLevelEntity}}
└── {{ChildEntity}}
    └── {{GrandchildEntity}}
        └── {{LeafEntity}}
```

### {{TopLevelEntity}}

> For each entity, document:
> - What it represents in the domain
> - Visibility/access rules
> - Ownership model
> - Uniqueness constraints
> - Soft delete behavior (if applicable)

### {{ChildEntity}}

> - Scope: Belongs to exactly one {{TopLevelEntity}}
> - Key domain rules

### {{LeafEntity}}

> - The atomic unit of content
> - Threading/nesting behavior (if applicable)
> - Content format (plain text, rich text, etc.)
> - Attachment support (if applicable)

---

## 3. Domain-Specific Concepts

> Document any domain-specific concepts that are unique to this application and not covered by standard CRUD patterns. For each concept:
> - What it is
> - Why it exists
> - How it relates to other entities
> - Any multilingual or localization requirements

---

## 4. Permission Model

> Define the permission levels for your application. Most applications have at least two levels: system-wide roles and resource-level access.

### System-Level Roles

| Role | Level | Capabilities |
|------|-------|-------------|
| {{Role1}} | {{level}} | {{description}} |
| {{Role2}} | {{level}} | {{description}} |
| {{Role3}} | {{level}} | {{description}} |

### Resource-Level Access

> If your application has resource-scoped permissions (e.g., per-group, per-project, per-organization), define them here:

| Access Level | Level | Capabilities |
|-------------|-------|-------------|
| {{Level1}} | {{value}} | {{description}} |
| {{Level2}} | {{value}} | {{description}} |

> **Rationale:** Explain why these specific permission levels exist and how they map to real-world user roles.

---

## 5. Content Authoring & Attribution

> If your application supports content creation, document:
> - How authorship is tracked
> - Whether content can be attributed to non-system users
> - Mention/notification systems
> - Import/export attribution rules

---

## 6. Content Import & Export

> If applicable, document supported formats:

### Import Formats

| Format | Source | Features |
|--------|--------|----------|
| {{format}} | {{source}} | {{features}} |

### Export Formats

| Format | Output | Use Case |
|--------|--------|----------|
| {{format}} | {{output}} | {{use_case}} |

---

## 7. User Community & Localization

### Target Community

> Describe the primary user base: language, geography, domain expertise.

### Localization Design

| Aspect | Primary | Secondary |
|--------|---------|-----------|
| UI default language | {{PRIMARY_LOCALE}} | {{SECONDARY_LOCALE}} |
| Backend error default | {{BACKEND_DEFAULT}} | — |

> Explain why these locale choices were made.

---

## 8. User Experience Patterns (Domain-Driven)

> Document the key UX patterns that are driven by domain requirements rather than generic UI conventions. For each pattern:
> - What the user sees/does
> - Why this pattern was chosen (domain rationale)
> - Any metacommunication intent

---

## 9. Administrative Domain

### Activity Logging

> What operations are logged? What format?

### Backup & Restore

> Any domain-specific backup/restore requirements?

### Terms & Conditions

> Any domain-specific legal/compliance requirements?

---

## 10. Validation Constants (Domain)

> Domain-driven validation limits. These should reflect real-world constraints, not arbitrary technical limits.

| Constant | Value | Domain Rationale |
|----------|-------|-----------------|
| {{field}} length | {{min}}–{{max}} chars | {{why}} |

> **Note:** These constants must be kept in sync between backend and frontend. See `project/security-checklists.md` Quick Reference for the technical mapping.
