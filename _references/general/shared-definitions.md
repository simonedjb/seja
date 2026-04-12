# GENERAL - SHARED DEFINITIONS

## Semiotic Engineering concepts

The **metacommunication message** is a designer-to-user message that is conveyed by the designer (I) to the user (you) throughout the system and the user interface. For the full definition and its application to the project. Semiotic engineering posits that the message can be summarized as: "Here is my understanding of who you are, what I've learned you want or need to do, in which preferred ways, and why. This is the system that I have therefore designed for you, and this is the way you can or should use it in order to fulfill a range of purposes that fall within this vision."

**Phrasing rule (non-negotiable)**: All metacommunication messages — in templates, project files, plans, briefs, per-feature logs, and EMT answers — **must** use first-person "I" for the designer and second-person "you" for the user. Never use "the designer", "the system", "the user" (third-person), passive voice, or imperative mood. This applies to all sections of `project/metacomm-*.md` files: the global summary/vision, every EMT answer, and every per-feature intent. Example: write "I designed a postpone shortcut for you because I know you tend to over-schedule" — not "The designer provides a postpone shortcut" or "Enforce privacy with minimal friction."

**Verbatim rule**: When a user provides a metacommunication message as input — during /design, in a spec, in `project/product-design-as-intended.md`, or as a `--framing metacomm` brief — the agent must record it **exactly as written**, without summarization, editing, or any textual manipulation. The designer's precise wording carries intentional nuance; paraphrasing risks distorting the design intent.

---

## Theoretical Foundations

> SEJA's architecture is grounded in Semiotic Engineering (SemEng), a theory of HCI
> that treats human-computer interaction as a special case of computer-mediated human
> communication. The following table maps SEJA concepts to their SemEng origins.
> This grounding is for reference and intellectual traceability -- SEJA skills and
> agents do not require users to know SemEng terminology.

| SEJA Concept | SemEng Origin | Source |
|---|---|---|
| Metacommunication files (product-design-as-intended § Metacommunication / product-design-as-coded § Metacommunication) | Metacommunication template -- the abstract message every system delivers from designers to users | [SemEng-2005, Ch. 1 & 3] |
| First-person "I/you" phrasing rule | Designer's personal engagement -- designers are communicators, not anonymous producers | [SemEng-2005, Ch. 3 p.84] |
| Extended Metacommunication Template (EMT) | EMT with guiding questions aligned to lifecycle stages (Analysis, Design, Prototype, Evaluation) | [EMT-Ethics-2021, pp.365-368] |
| Spec-drift detection (as-is vs. to-be) | Communicability monitoring -- tracking whether design intent is being communicated | [SemEng-2005, Ch. 4; SemEng-Methods-2009] |
| Constitution (immutable principles) | Value inscription governance -- making implicit values explicit and binding | [SemEng-2005, Ch. 1 pp.9-10] |
| Design -> plan -> implement -> check pipeline | Meaning propagation -- tracking how meanings transform from conception to code | [SigniFYI-2016] |
| Review perspectives (16 lenses) | Communicability evaluation -- segmented analysis from multiple viewpoints | [SemEng-2005, Ch. 4; SemEng-Methods-2009] |
| Council-debate agent | Formalized abductive reasoning with multiple interpretive perspectives | [SemEng-2005, Ch. 2 on abduction] |
| Pre/post-skill pipelines | Reflection in/on action -- structured reflection before and after every action | [SemEng-2005, Ch. 1, citing Schon 1983] |
| Behavior-evolution reconstruction | Reflection on practice -- surfacing and criticizing tacit understandings | [SemEng-2005, Ch. 1, citing Schon 1983] |
| Role families (BLD/SHP/GRD) + expertise levels (L1-L5) | Multi-audience metacommunication -- segmenting the "you" addressee | [SemEng-2005, Ch. 3 & 6] |
| _output/ infrastructure (INDEX, briefs, plans) | SigniFYIng Traces -- capture & access infrastructure for interpretive processes | [SigniFYI-2016] |
| Conventions.md (project signification system) | Signification systems -- conventionalized expression-content associations | [SemEng-2005, Ch. 2, citing Eco 1976] |
| Communicability review questions (UX/DX perspectives) | CEM 13 communicability utterances -- precise taxonomy of communicative breakdowns | [SemEng-2005, Ch. 4 pp.123-138] |
| Sign classification lens (UX perspective) | Three classes of interface signs (static, dynamic, metalinguistic) | [SemEng-2005, Ch. 4; SemEng-Methods-2009] |
| CDN review questions (API/ARCH perspectives) | Cognitive Dimensions of Notations -- 14 dimensions for evaluating notations | [SigniFYI-2016, citing Green & Petre] |

---

## Notation Conventions

### Standards section notation

Cross-references to the unified standards files use the form `standards.md § Backend > 6`, where `§ <Domain>` identifies the H2 section (Backend, Frontend, Testing, i18n for `standards.md`; UX patterns, Graphic / visual design for `design-standards.md`) and `> N` identifies the H3 subsection whose heading begins with `N.`. The original section numbers from the pre-2.8.1 single-topic files are preserved so that legacy citations of the form `backend-standards §6` map to `standards.md § Backend > 6` by direct substitution.

---

## Lifecycle Markers

> Standard inline markers for tracking the lifecycle of to-be items across all registered
> to-be files (see conventions.md To-Be / As-Is Registry). Defined here so all skills
> and agents use a consistent convention when reading or writing markers.
>
> **Agent rules**: agents may read markers and propose new IMPLEMENTED markers (via
> AskUserQuestion in post-skill). Agents must NEVER remove or alter any existing
> IMPLEMENTED or ESTABLISHED marker -- these are audit records.

### STATUS marker (prose sections)

Applied as an inline HTML comment immediately before the section heading -- invisible in
rendered markdown, machine-parseable by agent tooling.

**Legacy scheme (pre-2.8.0, still supported for existing files):** a single uppercase
value `IMPLEMENTED` used as a one-shot marker, typically paired with a separate
`ESTABLISHED` stamp (see below) when the item is later promoted:

```markdown
<!-- STATUS: IMPLEMENTED | plan-NNNNNN | YYYY-MM-DD -->
### Section Title
```

A legacy marker without a plan ID is valid for items implemented outside the plan
workflow: `<!-- STATUS: IMPLEMENTED | manual | YYYY-MM-DD -->`.

**Current scheme (2.8.0+, used by `apply_marker.py` and the middle-path enforcement):**
a lowercase multi-value marker with a documented state machine `proposed -> implemented
-> established -> superseded`. Introduced by advisory-000264 Q3 (middle-path
classification) and enforced by `check_human_markers_only.py` for files classified
`Human (markers)`:

```markdown
<!-- STATUS: proposed | plan-NNNNNN | YYYY-MM-DD -->
### Section Title
```

The plan ID and date fields are optional for `proposed` (the initial state written by
the designer) and required once the item has moved past `proposed`. Transitions are
validated by `apply_marker.py` via `human_markers_registry.ALLOWED_MARKERS["STATUS"]
["allowed_transitions"]`: `proposed -> implemented`, `implemented -> established`,
`established -> superseded`. Regression (e.g., `established -> implemented`) is
rejected.

Both schemes coexist on disk: existing files carrying uppercase `STATUS: IMPLEMENTED`
markers remain valid and match the verifier's allowlist. The widened `_STATUS_MARKER_RE`
in `apply_marker.py` (since SEJA 2.8.3, plan-000268 Amendment A1) detects legacy
uppercase markers so a Phase 3b flip `implemented -> established` REPLACES the legacy
marker (rather than stacking a new lowercase marker above the old one). Files created
or consolidated by follow-up plans use the lowercase multi-value scheme as the primary
form; `project/product-design-as-intended.md` (since SEJA 2.8.3) is the canonical lowercase-primary
Human (markers) file.

### Decision entries (ADR)

Design intent decision entries live in `project/product-design-as-intended.md § Decisions` under
`### D-NNN: Title` headings (ADR shape: Context / Decision / Consequences / optional
Supersedes, per Michael Nygard's Architecture Decision Records). The `D-NNN` namespace
is **orthogonal to the REQ-TYPE-NNN namespace**: they are separate taxonomies, never
intermixed. REQ markers trace individual requirements (entities, permissions, validation
constants, etc.); Decision entries capture the rationale and trade-offs behind larger
architectural choices.

Decision entries carry their own `STATUS` marker (lowercase multi-value scheme) above
the heading:

```markdown
<!-- STATUS: proposed | plan-NNNNNN | YYYY-MM-DD -->
### D-001: Use PostgreSQL as primary datastore

**Context**: ...
**Decision**: ...
**Consequences**: ...
```

The `/explain spec-drift --promote` workflow (Phase 3a) drafts ADR-shaped Decision
entries from plan metadata for items marked `STATUS: implemented`, writing them to
`_output/promote-proposals/promote-proposal-plan-<id>.md`. The designer reviews, edits
to their voice, and copies the entries into `product-design-as-intended.md § Decisions`. Phase 3b
(`/explain spec-drift --promote --apply-markers plan-<id>`) then flips the STATUS
markers from `implemented` to `established` via `apply_marker.py`, using a
heading-only grep (`^###\s+D-NNN(?::|\s*$)`) to verify presence without matching prose
(designer-voice preservation per advisory-000264 Q4).

### IMPLEMENTED marker (table rows)

For structured tables (e.g. journey map steps), add a Status column:

| # | ... | Status |
|---|-----|--------|
| 1 | ... | DONE (plan-000178, 2026-04-02) |
| 2 | ... | - |

### ESTABLISHED stamp

Applied when a human confirms promotion of an IMPLEMENTED item to its established
counterpart file (via `/explain spec-drift --promote` or manual curation):

```markdown
<!-- ESTABLISHED: plan-NNNNNN | YYYY-MM-DD | vX.Y.Z -->
```

The version field (`vX.Y.Z`) is optional -- projects without semver use date only:
`<!-- ESTABLISHED: plan-000178 | 2026-04-02 -->`.

The stamp is appended to the corresponding established file entry. In the to-be file,
the IMPLEMENTED marker is replaced with the ESTABLISHED stamp (or the entry is removed
-- designer's choice, both are valid).

---

## Requirement ID Convention

Stable, machine-parseable identifiers for design-intent requirements, enabling traceability from spec to plan steps. Each marker is an HTML comment placed immediately before the heading, table row, or bullet that defines the requirement.

**Format**: `<!-- REQ-TYPE-NNN -->`

**Type prefix taxonomy**:

| Type Prefix | Design-Intent Section | Classification | Enforcement |
|------------|----------------------|---------------|-------------|
| ENT | 2. Entity Hierarchy | technical | advisory |
| PERM | 4. Permission Model | security | blocking at preflight |
| VAL | 10. Validation Constants | security | blocking at preflight |
| UX | 8. UX Patterns | ux | advisory |
| MC | 14. Per-Feature Metacomm | ux | advisory |
| JM | 15. Designed User Journeys | ux | advisory |
| I18N | 7. Localization | cross-cutting | advisory |
| DELTA | 16-17. Deltas | technical | advisory |

**Classification rule**: Security-classified requirements (PERM, VAL) must be traced by a plan step in the same wave as their parent entity. Advisory-classified requirements produce warnings but do not block.

**Plan step tracing**: Plan steps declare which requirements they satisfy via the `Traces` metadata field (e.g., `- **Traces**: REQ-ENT-001, REQ-PERM-003`). Coverage is verified by `check_plan_coverage.py`.

**Auto-generation**: The `/design` skill auto-assigns REQ IDs during the verification pass. NNN is a zero-padded 3-digit counter per type, starting at 001.

> **Footnote**: The `D-NNN` Decision-entry namespace (see `### Decision entries (ADR)` above) is **orthogonal** to `REQ-TYPE-NNN`. Never interpolate D-NNN into the REQ taxonomy table and never write `REQ-D-NNN` collisions. REQ markers trace requirements; D-NNN entries capture ADR-shaped architectural decisions.

---

## File Maintainer Classification

Four-value scheme applied to all reference files in `_references/` (principally the `project/` subdirectory, which varies by project). Used as the "Maintained by" column in `project/conventions.md` Key Files table, and summarized in `.claude/rules/framework-structure.md`.

| Value | Meaning | Agent rule |
|-------|---------|-----------|
| **Human** | Authored and updated exclusively by humans. | Agents must NOT write to this file. Agents may read it and propose changes via `AskUserQuestion`. |
| **Human (markers)** | Human-authored prose; the agent may write fixed-format structured markers only (e.g., STATUS flags, INCORPORATED stamps, CHANGELOG append lines in a fixed format). | Agents may write only via `apply_marker.py`, and only after explicit `AskUserQuestion` confirmation in the same turn. Agents must never write prose content or modify text outside the allowed marker patterns, even after confirmation. Enforced by `check_human_markers_only.py` during post-skill step 6c. |
| **Agent** | Auto-maintained by agents and skills (e.g., via post-skill). | Agents may read and write. Humans typically do not edit directly. |
| **Human / Agent** | Seeded by an agent (e.g., via /design), then human-owned; both may update. Also applies to framework source files (`general/`, `template/`) maintained by both framework authors and framework tooling. | Agents may write, following the file's own update rules. Humans are the primary curators after initial generation. |

---

## External Specifications

| Spec | Description | SEJA Integration |
|------|-------------|-----------------|
| **agentskills.io** | Universal specification for portable AI agent skill definitions. Defines `name` (1-64 chars, lowercase alphanumeric + hyphens), `description` (1-1024 chars), optional `compatibility` (max 500 chars), and extensible `metadata`. | SKILL.md frontmatter follows the spec. SEJA-specific fields are namespaced under `metadata`. Validated by `check_skill_spec.py`. |

---

## Versioning

The SEJA framework uses three version-bearing files with distinct purposes:

| File | Location | Purpose | Maintained by | When to update |
|------|----------|---------|---------------|----------------|
| `.claude/skills/VERSION` | Framework source | Authoritative framework version (semver) | Manual (developer) | Bump with every release |
| `.claude/CHANGELOG.md` | Framework source | Human-readable release history | Manual (developer) | Add a `## [x.y.z]` heading matching VERSION for every release |
| `.seja-version` | Project root | Per-project migration watermark | Automated (`run_migrations.py`, `/upgrade`) | Written automatically when migrations run; records the version a target project was last migrated to |

**Key distinction**: `.claude/skills/VERSION` tracks what the framework IS. `.seja-version` tracks what a project has been UPGRADED TO. In the framework repo itself, `.seja-version` is dogfooded -- it should match VERSION after each release.

**Validation**: `check_version_changelog_sync.py` validates that VERSION and CHANGELOG are in sync. It runs as part of `/check preflight`. Use `bump_version.py` to update all three files atomically.

---

## Generic Terminology

| Term | Definition | Used In |
|------|-----------|---------|
| **Soft delete** | Records are marked as deleted (`deleted_at` timestamp) rather than physically removed. Queries must filter for non-deleted records. | project/standards.md § Backend > 6 |
| **Double confirmation** | A destructive-action pattern requiring the user to type a confirmation word before the action is enabled. | project/standards.md § Frontend > 11 |
| **Review perspective** | A domain-based evaluation lens (SEC, PERF, DB, etc.) applied to code, plans, or decisions per `general/review-perspectives.md`. | general/review-perspectives.md |
| **Pinned anchor** | A reference file that must survive context compaction events and be re-injected verbatim after any summarization or truncation. The pinned anchors list is defined in `general/constraints.md` under "Pinned Anchors (Non-Compactable Context)". | general/constraints.md |

---

## If stack includes React

| Term | Definition | Used In |
|------|-----------|---------|
| **Orchestrator page** | A page-level component that owns state, effects, and business logic, delegating rendering to sub-components in `features/<domain>/`. | project/standards.md § Frontend > 1, > 2 |
| **Feature co-location** | The practice of placing feature-specific hooks, forms, sub-components, and utils together in `features/<domain>/` rather than scattering them across `hooks/`, `components/`, etc. | project/standards.md § Frontend > 1, > 20 |

## If stack includes Flask/Python

| Term | Definition | Used In |
|------|-----------|---------|
| **Three-layer architecture** | The backend pattern separating API (HTTP), Services (business logic), and Models (data). Services are HTTP-agnostic. | project/standards.md § Backend > 4 |
| **Service layer contract** | The rule that services accept plain arguments, raise error subtypes, and never import framework request/response objects. | project/standards.md § Backend > 19 |
| **Response builder** | Utility functions that produce consistent JSON response envelopes (success, error, paginated). | project/standards.md § Backend > 8 |

## If stack includes CSS/HTML

| Term | Definition | Used In |
|------|-----------|---------|
| **BEM** | Block Element Modifier - the CSS class naming convention used for custom component classes (`block__element--modifier`). | project/standards.md § Frontend > 5 |

## If stack includes a frontend

| Term | Definition | Used In |
|------|-----------|---------|
| **Design tokens** | Centralized style primitives (colors, fonts) consumed by both the CSS framework config and app code. | project/standards.md § Frontend > 5 |
