---
diataxis: how-to
freshness: release-bound
last-reviewed: 2026-07-02
---

# How to generate a Structured Product Overview (SPO)

The Structured Product Overview is an interactive HTML diagram that shows your product's complete value chain — from business goals at the top down to data infrastructure at the bottom — as a layered, interconnected graph. It answers: *what does this product do, for whom, why, and how is it built?*

## What the SPO looks like

The generated `_output/docs/spo.html` file opens in any browser and includes:

- **Layered cards** organized into layers (5 by default; add `obstacles` / `intelligent-components` for problem-space or AI-heavy products)
- **SVG arrows** tracing how lower-layer cards enable upper-layer cards
- **Persona filter** — click a persona chip to highlight their card relationships
- **Facet bar** — extra filter axes (e.g. Subsystem, Channels) declared in `meta.facets`; chips highlight matching cards, and combine with persona/quality filters
- **Quality Criteria panel** — highlight which cards satisfy specific quality dimensions
- **Traceability chips** — when `meta.tracker_type: seja`, each card shows its `req_ids` / `decision_ids` / `journey_ids`
- **Deep-links** — a card's `source_ref` renders a ↗ link back to its design source
- **Analyses panel** — press **A** for computed structure analyses: coverage gaps, orphans, hub nodes, longest value chains, unaddressed quality criteria, and cross-version dependency risk
- **Language toggle** — when `meta.languages` lists more than one locale, switch label languages in place
- **Roadmap columns** — switch to V1 / V2 / V3 view to see what is in each release bucket
- **Compact / full toggle** — shrink cards to title-only for a high-level overview
- **Gap badges** — cards with no enabler from the layer below get a `⚠` warning

## The data file: `product-overview.yaml`

The SPO is generated from `product-overview.yaml` in your project root (alongside `product-design-as-intended.md`). It captures:

```yaml
meta:
  title: "My Project — Product Overview"
  version_labels: {V1: "V1 · MVP", V2: "V2 · Next Release", V3: "V3 · Roadmap"}

layers:      # ordered bottom-up; add/remove layers here
personas:    # referenced by card IDs
quality_criteria:  # organized by layer
cards:       # the graph nodes — each with id, layer, enables, depends, status
```

The file is populated incrementally during normal skill usage:

| Skill | What it writes to the SPO |
|---|---|
| `/design` | Initial `layers`, `personas`, and `goals`/`tasks` card stubs |
| `/plan` | New `features` or `services` cards (status: `proposed`) |
| `/implement` | Status transitions: `proposed → implementing → done` |
| `/research` | Optional obstacle cards and quality criteria |
| `/explain drift` | Batch status proposals for implemented-but-proposed cards |

The `enables` and `depends` graph edges — the arrows between cards — are the only fields you fill in manually. They require intentional structural thinking about which parts of the product support which others.

### Facets, traceability, deep-links, and languages

`meta` and each card support optional fields for richer overviews:

```yaml
meta:
  tracker_type: seja        # render req_ids / decision_ids / journey_ids as chips
  locale: en-US
  languages: [en-US, pt-BR] # >1 language adds an in-page language toggle
  facets:                   # extra filter axes beyond personas
    - {id: subsystem, label: Subsystem, field: subsystem}
    - {id: channels,  label: Channels,  field: channels}

cards:
  - id: F-01
    # ...
    subsystem: ui                     # drives the `subsystem` facet
    channels: [WhatsApp, Google]      # drives the `channels` facet
    req_ids: [REQ-UX-001]             # SEJA traceability chips (tracker_type: seja)
    decision_ids: [D-001]
    journey_ids: [JM-TB-001]
    source_ref: "product-design/product-design-as-intended.md#8-user-experience-patterns"
```

- **Bilingual labels:** any label (`meta.title`, layer `name`/`subtitle`, card `title`, quality-criteria `label`, persona `name`/`role`, version labels) may be a plain string OR a `{locale: string}` map.
- **Facets** read a card field (string or list); the generator derives the distinct values into a chip row automatically.
- **`source_ref`** is relative to the repo root; the generator resolves it from wherever the HTML is written.

## Generating the SPO

Once `product-overview.yaml` exists:

```
/document --type spo
```

Output: `_output/docs/spo.html`

### Show drift between intended and coded state

```
/document --type spo --drift
```

Dims non-`done` cards and shows a "N done / M total" count per layer, making the gap between what is designed and what is built immediately visible.

### Customize the output path

```
/document --type spo --output docs/product-overview.html
```

## Card lifecycle: `status` field

Each card has a `status` field that tracks its implementation state:

| Status | Visual | Meaning |
|---|---|---|
| `proposed` | dashed outline | Designed; not yet started |
| `implementing` | solid outline, muted fill | In progress (plan active) |
| `done` | fully styled | Implemented and verified |
| `deferred` | grayed out, 40% opacity | Out of scope for now |

Update status via:
- **Manual edit**: change `status` directly in `product-overview.yaml`
- **`/explain drift`**: the drift skill can propose batch status flips when plan evidence shows features are complete

## Default 5-layer model

| Layer | ID | What it captures |
|---|---|---|
| Business Goals | `goals` | Strategic rationale — why this product exists |
| User Tasks | `tasks` | What each persona needs to accomplish |
| Features & Modules | `features` | What the system delivers |
| Services & Integrations | `services` | Processing engines, external APIs |
| Data & Infrastructure | `data` | Persistence, pipelines, foundations |

To add layers (e.g. an `obstacles` layer between `goals` and `tasks`, or an `intelligent-components` layer for AI/ML capabilities), add entries to the `layers` array in `product-overview.yaml`. Use card ID prefixes consistently: `G-NNN` (goals), `T-NNN` (tasks), `F-NNN` (features), `S-NNN` (services), `D-NNN` (data).

## When to re-generate

The SPO is not regenerated on every `/implement` cycle. Re-run `/document --type spo` when:

- After `/design` completes initial project setup
- Before a stakeholder presentation
- After significant product structure changes (new layers, major feature additions)
- Before cutting a release

## See also

- `/explain drift` — reconcile design specs with as-coded state
- `/communicate` — generate stakeholder materials from the same design layer
- `product-overview.yaml` template in `.claude/references/template/product-overview.yaml`
