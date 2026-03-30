# FRAMEWORK - COMMUNICATION

> Audience-aware communication framework for generating tailored stakeholder material from project knowledge.
> Designed as a 3-layer content model with audience segments and Diataxis-aligned content types.
> Last revised: 2026-03-28.

---

## How to Use

When generating communication material for a stakeholder audience, determine the **audience segment**, then invoke the `/communication` skill. The skill loads the corresponding audience file, project context, and style configuration to produce tailored content.

### Invocation

```
/communication <audience> [--format md|html] [--all] [--source <file>]
```

| Flag | Description | Default |
|------|-------------|---------|
| `<audience>` | Target audience segment (name or tag). Required unless `--all` is used. | — |
| `--format md\|html` | Output format. `html` generates a styled standalone HTML file alongside the markdown. | `md` |
| `--all` | Generate material for all audience segments in batch (parallel agents). | off |
| `--source <file>` | Path to an existing advisory report or markdown file to reformat for the target audience. | — |

### Audience Segments

Each stakeholder maps to one of five audience segments:

| Tag | Name | File | Core Question | Primary Material Types |
|-----|------|------|---------------|----------------------|
| EVL | Evaluators | [evaluators.md](communication/evaluators.md) | "Should we adopt this? What's the ROI?" | Executive overview, architecture overview, comparison guide, proof of value |
| ADO | Adopters | *(cross-ref: [general/onboarding.md](onboarding.md))* | "How do I get started and become productive?" | Onboarding plans, tutorials, quickstart guides |
| CLT | Clients | [clients.md](communication/clients.md) | "Is the product I commissioned delivering the outcomes I need?" | Product vision alignment, delivery status, outcome evidence, metacommunication summary |
| USR | End Users | [end-users.md](communication/end-users.md) | "Does the software serve my needs well?" | Quality manifesto, feedback channels, accessibility statement |
| ACD | Academics | [academics.md](communication/academics.md) | "What's the theoretical contribution? How can I build on this?" | Theoretical foundation, research agenda, extension guide |

**Note on A2 Adopters**: This segment is served by the `/onboarding` skill and its `general/onboarding.md` framework. The `/communication` skill does not duplicate adopter material — instead, it cross-references onboarding output when adopter-facing content is needed.

**Note on CLT role variants**: The Clients segment includes two role variants: CLT-D (Decision-maker, who shapes product design intent) and CLT-F (Funder, who provides financial backing). A single stakeholder may fill both roles. See [clients.md](communication/clients.md) for details.

---

## Content Layers

Material is organized in 3 progressive layers. Each layer adds specificity to the output:

| Layer | Name | Source | Purpose |
|-------|------|--------|---------|
| **0** | Universal Foundation | `project/conceptual-design-as-is.md`, `project/conventions.md` | Project identity, value proposition, key differentiators — shared across all audiences |
| **1** | Audience-Specific Content | `general/communication/<audience>.md` | Tone guidance, content sections (Essential + Deep-dive), Diataxis mapping — tailored per audience segment |
| **2** | Format-Specific Presentation | `project/communication-style.md` | CSS styling, header/footer templates, per-audience tone overrides, HTML conversion settings |

### Layer 0 — Universal Foundation

Every communication artifact includes:

- **Project identity**: Name, tagline, mission statement (from conceptual design)
- **Value proposition**: What problem the project solves and for whom
- **Key differentiators**: What sets the project apart from alternatives
- **Current state**: Phase, maturity, key metrics (from project conventions and recent output)

### Layer 1 — Audience-Specific Content

Each audience file defines:

- **Essential sections**: Core content that every artifact for this audience must include
- **Deep-dive sections**: Extended content for when more depth is needed
- **Tone guidance**: Formality, technical depth, and framing appropriate for the audience
- **Diataxis mapping**: Which content types (Tutorial, How-to, Explanation, Reference) are relevant

### Layer 2 — Format-Specific Presentation

When `--format html` is selected:

- CSS styling from `project/communication-style.md` (or template defaults)
- Header and footer HTML templates with project branding
- Inline styles for standalone, dependency-free HTML output
- Per-audience tone and depth overrides

---

## Diataxis Integration

Each audience segment maps differently to the four Diataxis content types. Not every audience needs every type:

| Audience | Tutorial | How-to | Explanation | Reference |
|----------|----------|--------|-------------|-----------|
| **EVL** Evaluators | "Try the framework in 30 min" | Adoption guide, migration path | Architecture overview, design rationale | Skills catalog, feature matrix |
| **ADO** Adopters | *(via /onboarding)* | *(via /onboarding)* | *(via /onboarding)* | *(via /onboarding)* |
| **CLT** Clients | — | Status reporting template | Product vision, metacommunication summary | KPI definitions, outcome metrics |
| **USR** End Users | — | Feedback guide, getting help | Quality manifesto, transparency note | — |
| **ACD** Academics | "Extend the framework" workshop | Skill authoring guide | Theoretical foundation, semiotic engineering basis | Extension API, taxonomy reference |

The full Diataxis mapping with priorities and target lengths lives in [diataxis-mapping.md](communication/diataxis-mapping.md).

---

## Loading Strategy

For a given invocation, the skill loads files in this order:

### Single audience (`/communication evaluators`)

1. `general/communication.md` — this file (framework overview, audience resolution)
2. `general/communication/evaluators.md` — audience-specific content template and tone
3. `project/conceptual-design-as-is.md` — project identity and context (Layer 0)
4. `project/communication-style.md` — style and tone overrides (Layer 2, if `--format html` or if the file exists)
5. `general/report-conventions.md` — output file naming and encoding rules

### Source reformatting (`/communication clients --source advisory-0002.md`)

Same as above, plus:

6. The source file — content to be reformatted for the target audience

### Batch mode (`/communication --all`)

Launches parallel agents, one per active audience (EVL, CLT, USR, ACD). Each agent follows the single-audience loading strategy independently.

---

## Output Structure

Communication material is saved in date-versioned folders under `${COMMUNICATION_DIR}/`:

```
${COMMUNICATION_DIR}/
├── 2026-03-28/
│   ├── communication-0001-evaluators.md
│   ├── communication-0001-evaluators.html
│   ├── communication-0002-clients.md
│   └── communication-0003-end-users.md
├── 2026-04-15/
│   ├── communication-0004-academics.md
│   └── communication-0005-evaluators.md
```

- **Date folder** (`YYYY-MM-DD` UTC): Groups all material generated on the same date. Regenerating on a new date creates a new version without overwriting.
- **Sequential ID**: Global across all date folders (not reset per folder).
- **Audience slug**: Lowercase audience name (e.g., `evaluators`, `clients`, `end-users`, `academics`).
- **Extension**: `.md` for markdown, `.html` for HTML. When both formats are generated, both files share the same ID and slug.
- **Batch generation**: Use `--all` to generate material for all active audiences in parallel via concurrent agents.

---

## Relationship to Other Framework Components

- **Onboarding** (`general/onboarding.md`, `/onboarding`): The A2 Adopters audience segment is entirely served by the onboarding framework. Communication material may cross-reference onboarding plans when addressing adopter needs.
- **Advisory** (`/advise`): Advisory reports can be reformatted for specific audiences using `--source <advisory-file>`. This transforms technical advisory content into audience-appropriate communication.
- **Review perspectives** (`general/review-perspectives.md`): The UX perspective's focus on audience-appropriate communication is directly addressed by this framework's per-audience tone guidance.
- **Conceptual design** (`project/conceptual-design-as-is.md`): Layer 0 universal content draws project identity and value proposition from the conceptual design files.
- **Metacommunication** (`project/metacomm-as-is.md`): The designer's intent documented in metacommunication files informs how the project's story is told to each audience.
- **Style template** (`template/communication-style.md` / `project/communication-style.md`): Controls visual presentation and tone overrides. Instantiated per-project by `/quickstart`.
- **Skills system** (`.claude/skills/communication/SKILL.md`): The communication skill orchestrates all of the above.
