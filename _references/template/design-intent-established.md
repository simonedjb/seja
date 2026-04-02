# TEMPLATE -- DESIGN INTENT ESTABLISHED

<!-- maintained-by: human (designer) — agents must NOT modify this file -->

> **How to use this template:** Copy this file to `project/design-intent-established.md`. This is the human-maintained archive for design intent that has been processed through plans and implementations. It preserves the designer's reasoning alongside a reference to the plan that implemented it — filling the gap between "what was built" (as-is files) and "why the designer chose it" (this file).
>
> **When to add entries:** After a plan has been executed and post-skill has updated the as-is files, move the processed portions of `design-intent-to-be.md` into a new entry block here. Use the preservation priorities below as your guide.
>
> **Preservation priorities** (from `project/design-intent-to-be.md`):
> | Priority | Sections | Guidance |
> |----------|----------|----------|
> | P0 — must move | §4 Permission Model, §11 Global Vision, §13 Solution Representations, §14 Per-Feature Intentions | Core rationale and semiotic engineering intent — always preserve |
> | P1 — should move | §1 Platform Purpose, §2 Entity Hierarchy, §3 Domain Concepts, §8 UX Patterns, §12 EMT | Architectural and analytical framing — preserve when non-trivial |
> | P2 — optional | §5 Content Authoring, §6 Import/Export, §7 Community/L10n, §9 Admin, §10 Validation | Supporting decisions — preserve if rationale is not obvious from code |
>
> **Rules:**
> - Append only — never edit or delete prior entries; history is the value.
> - Each entry covers one plan's worth of processed intent.
> - Sections §0 (Planned Changes), §15 (CD Delta), and §16 (Metacomm Delta) are ephemeral and do **not** belong here — they live in `design-intent-to-be.md` until processed.
> - Agents must not write to this file. If post-skill reminds you to curate — that reminder is informational only.
>
> **Related files:**
> - `project/design-intent-to-be.md` — active working document for fresh design intent (human-maintained)
> - `project/conceptual-design-as-is.md` — what is currently implemented (agent-maintained)
> - `project/metacomm-as-is.md` — what the system currently communicates (agent-maintained)
> - `project/cd-as-is-changelog.md` — versioned change history of the as-built design

---

<!--
  ENTRY PATTERN — copy this block for each plan's worth of processed intent
  =========================================================================

  ## Entry: {{YYYY-MM-DD}} | Plan {{plan-id}} | Template v{{template-version}}

  > Summary of what design intent this entry captures and which plan implemented it.

  [Paste the relevant sections from design-intent-to-be.md below, using the section structure from Part I and Part II. Include only the sections that were processed — skip sections with no content for this entry.]

  =========================================================================
-->

<!-- ============================================================ -->
<!-- PART I — CONCEPTUAL DESIGN                                    -->
<!-- ============================================================ -->

## 1. Platform Purpose
<!-- P1: should move to established -->

> *Archive the platform purpose and design philosophy as it was understood when the implementing plan was executed. Copy from §1 of design-intent-to-be.md.*

---

## 2. Entity Hierarchy
<!-- P1: should move to established -->

> *Archive the entity hierarchy and per-entity domain rules as they were designed for this plan. Copy from §2 of design-intent-to-be.md.*

---

## 3. Domain-Specific Concepts
<!-- P1: should move to established -->

> *Archive any domain-specific concepts that were introduced or clarified by this plan. Copy from §3 of design-intent-to-be.md.*

---

## 4. Permission Model
<!-- P0: must move to established — permission rationale -->

> *Archive the permission model and its rationale as designed for this plan. The "why" behind permission levels underpins security decisions and must be preserved. Copy from §4 of design-intent-to-be.md.*

---

## 5. Content Authoring & Attribution
<!-- P2: optional move to established -->

> *Archive content authoring and attribution decisions if the rationale is not obvious from code. Copy from §5 of design-intent-to-be.md.*

---

## 6. Content Import & Export
<!-- P2: optional move to established -->

> *Archive import/export format decisions if the rationale is not obvious from code. Copy from §6 of design-intent-to-be.md.*

---

## 7. User Community & Localization
<!-- P2: optional move to established -->

> *Archive target community and localization decisions. Copy from §7 of design-intent-to-be.md.*

---

## 8. User Experience Patterns (Domain-Driven)
<!-- P1: should move to established -->

> *Archive domain-driven UX patterns and their rationale. Copy from §8 of design-intent-to-be.md.*

---

## 9. Administrative Domain
<!-- P2: optional move to established -->

> *Archive administrative domain constraints if non-obvious. Copy from §9 of design-intent-to-be.md.*

---

## 10. Validation Constants (Domain)
<!-- P2: optional move to established -->

> *Archive domain validation constants. These are also recorded in the as-is files; preserve here only if the rationale is worth keeping alongside the value. Copy from §10 of design-intent-to-be.md.*

---

<!-- ============================================================ -->
<!-- PART II — METACOMMUNICATION                                   -->
<!-- ============================================================ -->

## 11. Global Metacommunication Vision
<!-- P0: must move to established — core metacomm vision -->

> *Archive the designer-to-user metacommunication message as it was intended at the time of this entry. Phrasing rule: use "I" as the designer and "you" as the user — never third-person or passive voice (see `general/shared-definitions.md` Phrasing rule). Copy from §11 of design-intent-to-be.md.*

---

## 12. Extended Metacommunication Template Guiding Questions
<!-- P1: should move to established -->

> *Archive the EMT answers that informed this plan's design decisions. Copy from §12 of design-intent-to-be.md.*

---

## 13. Solution Representations
<!-- P0: must move to established — solution representations -->

> *Archive the solution scenarios or user stories that were designed and implemented in this plan. These represent the designer's intended user experience — preserving them alongside the plan ID keeps the "why this flow?" answer accessible. Copy from §13 of design-intent-to-be.md.*

---

## 14. Per-Feature Metacommunication Intentions
<!-- P0: must move to established — per-feature intents -->

> *Archive the per-feature metacommunication intentions that were implemented by this plan. Use I/you phrasing. Copy from §14 of design-intent-to-be.md, filtered to the features implemented in this plan.*

| Feature / Flow | Designer Intent | Priority | Plan ID | Date |
|---|---|---|---|---|
| {{feature}} | {{intent}} | {{P0 / P1 / P2}} | {{plan-id}} | {{YYYY-MM-DD}} |

---

## Changelog

| Date | Plan ID | Summary | Sections moved |
|------|---------|---------|----------------|
| {{YYYY-MM-DD}} | {{plan-id}} | {{one-line summary of what design intent this entry captures}} | {{e.g., §1, §4, §11, §13, §14}} |
