---
diataxis: reference
freshness: release-bound
last-reviewed: 2026-05-05
---

# SEJA Glossary

Canonical reference for SEJA terminology. This is a lookup, not a tutorial: scan the category you need and read the matching entry. Definitions are pinned to their authoritative source in the foundational harness and must not be paraphrased in a way that drifts from that source.

## Sign system

- **Agent** -- File classification for content auto-maintained by agents and skills (e.g., via post-skill); humans typically do not edit it directly.
- **Human** -- File classification for content authored and updated exclusively by humans; agents may read it but must not write to it.
- **Human (markers)** -- File classification for human-authored prose where agents may write only fixed-format structured markers via `apply_marker.py`, and only after explicit confirmation in the same turn.
- **Human / Agent** -- File classification seeded by an agent (e.g., via `/design`), then human-owned; both may update it following the file's own rules. See `docs/concepts.md § Sign system`.

## Markers

- **CHANGELOG_APPEND** -- Append-only marker type used to add entries to a CHANGELOG section of a Human (markers) file via `apply_marker.py`.
- **D-NNN** -- DDR-shaped Decision entry ID (Context / Decision / Consequences) living in `project/product-design-as-intended.md § Decisions`, orthogonal to the REQ namespace.
- **ESTABLISHED** -- Inline HTML comment stamp recording that a human has promoted an implemented item to established status, carrying plan ID, date, and optional version.
- **PUBLISH pending entry** -- Pending-ledger entry subtype filed by `cut_tag.py` at tag-cut to track outstanding publish-to-public work; surfaced by the pre-skill hook and escalated after 3 days overdue. See `docs/reference/release-process.md § Drift prevention`.
- **REQ-TYPE-NNN** -- Stable machine-parseable requirement ID (ENT, PERM, VAL, UX, MC, JM, I18N, DELTA) placed as an HTML comment before the heading, row, or bullet that defines the requirement. See `docs/concepts.md § REQ-TYPE-NNN`.
- **STATUS** -- Inline HTML comment marker above a section heading tracking its lifecycle state through `proposed -> implemented -> established -> superseded`, with plan ID and date.

## Profiles and patterns

- **brownfield** -- Project profile for embedding or attaching SEJA to an existing codebase that already has source history.
- **collocated** -- Deployment pattern where harness files (`.claude/`, `product-design/`, `_output/`) live directly inside the product codebase repository.
- **greenfield** -- Project profile for a brand-new project with no pre-existing codebase.
- **workspace** -- Deployment pattern where harness files live in a standalone git repository alongside, not inside, the product codebase.

## Roles and levels

- **BLD (Builders)** -- Role family for developers, DevOps engineers, and infrastructure engineers who write, deploy, and maintain code.
- **GRD (Guardians)** -- Role family for QA engineers, security engineers, tech leads, and engineering managers who ensure quality, alignment, and governance.
- **L1 Contributor** -- Junior to mid-level expertise (0-5 years); needs guidance on how, what, and where; learns via walkthroughs and reviewable first tasks.
- **L2 Expert** -- Senior expertise (5-10 years); makes independent judgment calls, mentors others, and wants the "why" behind patterns.
- **L3 Leader** -- Tech lead, staff engineer, or engineering manager expertise (10+ years); aligns teams, governance, and organizational outcomes.
- **SHP (Shapers)** -- Role family for product managers, UX and UI designers, researchers, and analysts who define what gets built and how.

## Review perspectives

- **A11Y** (Accessibility) -- WCAG conformance, contrast, keyboard navigation, screen readers, focus management.
- **API** (API Design) -- RESTful conventions, route consistency, request/response contracts.
- **ARCH** (Architecture) -- Layer boundaries, separation of concerns, dependency direction.
- **COMPAT** (Compatibility) -- API contract stability, schema evolution, browser and version support.
- **DATA** (Data Integrity and Privacy) -- PII handling, GDPR compliance, validation, audit trails.
- **DB** (Database) -- Schema migrations, backward compatibility, idempotency, constraints.
- **DX** (Developer Experience) -- Readability, conventions, documentation, error messages.
- **I18N** (Internationalization) -- i18n keys, locale support, pluralization, RTL, date and number formats.
- **MICRO** (Microinteractions) -- Hover, focus, active states, transitions, loading indicators, animations.
- **OPS** (Operations / DevOps) -- Environment parity, logging, monitoring, deployment, config management.
- **PERF** (Performance) -- N+1 queries, unbounded loops, indexes, caching, bundle size.
- **RESP** (Responsive Design) -- Mobile, tablet, and desktop breakpoints, fluid layouts, touch targets.
- **SEC** (Security) -- Auth, input validation, secrets management, dependency vulnerabilities.
- **TEST** (Testability) -- Test coverage, new test needs, mocking strategy, test isolation.
- **UX** (User Experience) -- User flows, feedback, error handling, navigation, discoverability.
- **VIS** (Visual Design) -- Design system consistency, CSS conventions, spacing, typography.

## Harness artifacts

- **harness** -- The SEJA agent harness: the collection of skills, agents, rules, references, scripts, and lifecycle pipelines under `.claude/` that govern how the AI agent operates on a project. The harness wraps every skill invocation in a pre-skill / post-skill envelope, enforces trust boundaries via the constitution, and maintains the sign system that tracks design intent. "Harness files" refers to the on-disk artifacts (`.claude/`, `product-design/`, `_output/`) that the harness reads and writes.
- **agent** -- Subagent prompt under `.claude/agents/` executing a single role (evaluator, generator, or executor) on one artifact type.
- **constitution** -- Immutable project principles in `project/constitution.md`, never agent-altered, required for new projects.
- **migration** -- Upgrade script under `.claude/migrations/` that moves a target project's harness files between SEJA versions. See `docs/how-to/upgrade.md § Harness migrations`.
- **pending ledger** -- Append-only JSONL log at `_output/pending.jsonl` tracking outstanding human actions surfaced by skills.
- **post-skill pipeline** -- Lifecycle hook run after every skill for briefs update, QA logging, as-coded updates, marker proposals, and git commit.
- **pre-skill pipeline** -- Eight-stage pipeline run before every skill: help, brief-log, orphan-check, budget-eval, compaction-check, pending-check, ref-load, constitution.
- **product-design-as-coded** -- Unified implementation-state file (`project/product-design-as-coded.md`) auto-maintained by the agent, with three H2 sections: Conceptual Design, Metacommunication, Journey Maps.
- **product-design-as-intended** -- Unified working-intent file (`project/product-design-as-intended.md`) holding design intent, DDR-shaped Decisions, and CHANGELOG, classified Human (markers).
- **rule** -- Path-scoped guidance file under `.claude/rules/` auto-loaded when Claude edits files matching the rule's scope.
- **script** -- Helper script under `.claude/skills/scripts/` performing validation, index generation, conversion, or orchestration tasks.
- **section boundary** -- Enforcement rule preventing agents from writing outside designated H2 sections of a multi-section file, validated by `check_section_boundary_writes.py`.
- **`.seja-version`** -- Per-project pin file written by `/seja-setup --here` recording the harness tag (or literal `HEAD`) the project was seeded from; read by `/seja-setup --upgrade` to compute the upgrade baseline. See `docs/how-to/upgrade.md § Pinning to a specific release`.
- **skill** -- A `SKILL.md` file under `.claude/skills/<name>/` defining an agent-invocable capability and invoked via a slash command.

## Processes

- **A2 release process** -- Manual release discipline for cutting SemVer-tagged releases of SEJA to public `seja`, with pending-ledger drift prevention and monthly dogfooding. See `docs/reference/release-process.md`.
- **Two-path lifecycle** -- The two entry paths to `/design`: first-iteration (one-shot, via `/seja-setup`) and iteration-2+ (recurring, via `/research` or `/explain` into `/design` or `/plan`). See `docs/concepts.md § Lifecycle: canonical path`.

## Flags

- **`--version`** -- Flag on `/seja-setup` (install and `--upgrade` modes) pinning the harness to an exact tag (or `HEAD`) at seed time or upgrade time. See `docs/how-to/upgrade.md § Pinning to a specific release`.
- **`/seja-setup --here`** -- Flag variant of `/seja-setup` that finalises setup in place inside a freshly cloned seed repo rather than copying to a new target directory; writes `.seja-version`. See `docs/how-to/greenfield-collocated.md § Option B: clone directly into the project folder`.
