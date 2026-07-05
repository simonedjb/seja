---
diataxis: explanation
freshness: on-structural-change
last-reviewed: 2026-05-05
---

# Concepts

We wrote this file as the "why" companion to the quickstart. Our goal here is to introduce you to the ideas SEJA runs on before you meet the skills that put those ideas to work. In the chapters that follow we cover the sign system we use to classify files and track intent, the profile x pattern picker that tells us how to set SEJA up for your codebase, the role families and expertise levels we tune our output to, the review perspectives we apply when we critique work, the skill portfolio and the decision matrix we use to pick among overlapping skills, and the harness lifecycle we run around every skill invocation. Later how-to guides link back to this file by anchor, so think of it as the reference we point to instead of repeating these definitions inline. For one-line definitions of every term used below, see [docs/reference/glossary.md](reference/glossary.md). For a visual anchor on how the skills connect to each other as a workflow, see [docs/concepts/skill-map.md](concepts/skill-map.md). For quick-reference command sequences, see the workflow sections at the end of each how-to guide.

## Epistemic stance

Before we introduce the sign system, the profile picker, and the rest of the ideas this file is built on, we want to tell you how to read what follows. Everything in this file is our current reading of how SEJA holds together. We have tried to be honest about what we know and what we are hedging on, but our reading is always provisional. When your practice shows us a better reading, we want to hear about it. The `/research` skill is the channel, and concrete counter-readings with artifact paths get further than abstract disagreement.

We ground this stance in the semiotic engineering tradition (de Souza 2005, 2009; SigniFYI 2016; EMT-Ethics 2021) and in Schon's reflective practice (1983). If any of those references feel alien, the short primer at [foundations.md](foundations.md) walks through what we take from each of them, in plain language and without assuming a research background. You do not need to read the primer to use SEJA, but you do need to know that everything here is open to revision.

With that in mind, here is the sign system we use to classify files and track intent.

## Sign system

We treat your project as a communication medium. Every file in it either carries your voice, our voice, or a narrow seam of structured markers through which we are allowed to record lifecycle events on your behalf. The sign system is how we keep those voices from bleeding into each other: four file classifications tell us who may write to a file; three lifecycle markers (STATUS, ESTABLISHED, CHANGELOG_APPEND) track how design intent moves from "proposed" to "established" without anyone having to rewrite prose to reflect the change; and eight requirement-traceability markers (REQ-TYPE-NNN) link individual requirements in your design spec to the plan steps that satisfy them. If you want to know why we treat conventions as a sign system at all -- rather than as arbitrary stylistic rules -- the short primer at [foundations.md](foundations.md) walks through the grounding. The glossary holds the one-line definitions; this chapter narrates the underlying model so you can recognize the signs when you open the repo.

<a id="human-human-markers-agent"></a>
### Human, Human (markers), Agent, Human / Agent

Four classifications. Three are strictly author-scoped; the fourth is jointly owned. **Human** -- File classification for content authored and updated exclusively by humans; agents may read it but must not write to it. We treat Human files as read-only reference. Your `project/constitution.md` is the canonical example: we load it at the start of every skill so we stay inside the principles you committed to, but we never edit a word of it. **Human (markers)** -- File classification for human-authored prose where agents may write only fixed-format structured markers via `apply_marker.py`, and only after explicit confirmation in the same turn. Your `project/product-design-as-intended.md` is the canonical example: you author the design intent in your voice, and we may only stamp STATUS, ESTABLISHED, or CHANGELOG_APPEND markers into it after you have confirmed the edit in the same turn. The guardrail is `check_human_markers_only.py`, which rejects any write that is not a recognized marker pattern. **Agent** -- File classification for content auto-maintained by agents and skills (e.g., via post-skill); humans typically do not edit it directly. `project/product-design-as-coded.md` is the canonical example: we reconstruct and refresh it after implementation, and `check_section_boundary_writes.py` keeps our edits inside its declared H2 sections so we cannot accidentally spill across Conceptual Design, Metacommunication, and Journey Maps. **Human / Agent** -- File classification for files seeded by an agent (e.g., via `/design`) and then jointly maintained; you own the voice and intent, and we update harness-managed sections when they drift from the current harness state. `project/conventions.md` is the canonical example: `/design` generates the initial file keyed to your project's stack and your constitution's principles, but you refine the project-specific rules and we keep sections such as the review-perspectives table in sync.

<a id="status-established-changelog-append"></a>
### STATUS, ESTABLISHED, CHANGELOG_APPEND

Three marker types, one per lifecycle event. **STATUS** -- Inline HTML comment marker above a section heading tracking its lifecycle state through `proposed -> implemented -> established -> superseded`, with plan ID and date. We use STATUS to answer "where is this item on its way from idea to reality?" The state machine is linear: you start an item as `proposed`, a plan flips it to `implemented` once the code lands, you promote it to `established` once you verify the result, and it may later be `superseded` by a newer decision. `apply_marker.py` enforces the allowed transitions; regression is rejected. **ESTABLISHED** -- Inline HTML comment stamp recording that a human has promoted an implemented item to established status, carrying plan ID, date, and optional version. ESTABLISHED is the promotion stamp we write only after you confirm the promotion; it is how we mark that a design decision has crossed from "working" to "committed." **CHANGELOG_APPEND** -- Append-only marker type used to add entries to a CHANGELOG section of a Human (markers) file via `apply_marker.py`. CHANGELOG_APPEND is append-only on purpose: we may add new entries to the CHANGELOG section, but we may never rewrite or remove existing ones, so the audit trail of what happened and when stays intact.

A STATUS marker looks like this above the heading it annotates:

```markdown
<!-- STATUS: proposed | plan-NNNNNN | YYYY-MM-DD -->
### Section Title
```

The comment is invisible in the rendered markdown but machine-parseable by `apply_marker.py` and `check_human_markers_only.py`, which is how the sign system stays out of your way while still giving us something reliable to read and write.

<a id="req-type-nnn"></a>
### REQ-TYPE-NNN

Eight requirement-traceability markers, one per requirement class. Where STATUS, ESTABLISHED, and CHANGELOG_APPEND track lifecycle state, REQ-TYPE-NNN markers do something orthogonal: they tag individual requirements in `product-design-as-intended.md` with stable, machine-parseable IDs so that plan steps can declare which requirements they satisfy and `check_plan_coverage.py` can verify that nothing was silently skipped.

Each marker is an HTML comment placed immediately before the heading, table row, or bullet that defines the requirement:

```markdown
<!-- REQ-PERM-003 -->
| Admin | Can delete any record | ...
```

The eight types, grouped by concern:

| Type | Covers | Classification |
|------|--------|----------------|
| ENT | Entity hierarchy | technical, advisory |
| PERM | Permission model | security, **blocking** |
| VAL | Validation constants | security, **blocking** |
| UX | UX requirements | ux, advisory |
| MC | Metacommunication | ux, advisory |
| JM | Designed user journeys | ux, advisory |
| I18N | Internationalisation | technical, advisory |
| DELTA | Deltas and breaking changes | technical, advisory |

**Blocking vs. advisory.** PERM and VAL are security-classified and blocking at preflight: a plan that touches a permission model or a validation constant must include a step that traces those requirements, or the preflight gate rejects the plan. All other types produce warnings but do not block.

**Plan step tracing.** A plan step declares the requirements it satisfies via the `Traces` metadata field: `- **Traces**: REQ-ENT-001, REQ-PERM-003`. This is the link between a design decision recorded in `product-design-as-intended.md` and the implementation step that brings it to life; `check_plan_coverage.py` walks the plan and verifies every blocking requirement has a trace.

**Orthogonality with D-NNN.** REQ-TYPE-NNN requirement markers and D-NNN Decision entries are separate namespaces and must never be intermixed: a Decision captures the rationale and trade-offs behind a choice; a requirement marker tags the requirement that drove it. One Decision may touch many requirements; one requirement may be shaped by more than one Decision over its lifetime.

Now that you can read the signs, here is how we choose what to do for you next. The profile x pattern chapter is where we describe the two-axis picker we run through at the start of every engagement to decide which how-to guide fits your situation, which deployment layout we should propose, and which skills you should expect to lean on first.

## Profile x pattern

We slice your starting situation along two orthogonal axes before we write a single file for you. The profile axis asks what your codebase already looks like and where SEJA will live relative to it; the pattern axis asks who we are writing for. Together they pick one cell from a small matrix, and that cell tells us which `/seja-setup` variant we run, which how-to guide we open, and how much reconciliation work we should expect before you see value.

<a id="greenfield-brownfield"></a>
### Greenfield and brownfield

The first half of the profile axis is about your code. **greenfield** is the project profile for a brand-new project with no pre-existing codebase: we help you author design intent from scratch, and there is nothing to reconcile against because nothing is built yet. **brownfield** is the project profile for embedding or attaching SEJA to an existing codebase that already has source history: we start by mapping what is actually coded into `product-design-as-coded.md`, then we reconcile that reconstruction against the design intent you author in `product-design-as-intended.md`. Brownfield is the harder axis because drift detection, STATUS marker promotion, and D-NNN Decision drafting only become load-bearing once there is existing code to reconcile. In greenfield those machinery are dormant until the first implementation lands.

<a id="collocated-workspace"></a>
### Collocated and workspace

The second half of the profile axis is about where SEJA's files live. **collocated** is the deployment pattern where harness files (`.claude/`, `product-design/`, `_output/`) live directly inside the product codebase repository: the simplest layout, ideal when one person is doing both design and implementation and there is no reason to version the two streams separately. **workspace** is the deployment pattern where harness files live in a standalone git repository alongside, not inside, the product codebase: design history gets its own git log, multiple people can iterate on specs without touching product code, and the launcher scripts we generate point our session at the product codebase through `claude --add-dir`. We choose workspace when design and code have different review cadences, different contributors, or different release rhythms.

The pattern axis is about the team shape: solo designer working alone, engineering team where several contributors share the harness, or a mixed setup where a designer and a small engineering team collaborate on the same project. The pattern does not change which files we copy, but it does change how we frame `/design`, `/onboard`, and `/communicate` output for you.

The resulting matrix gives us one cell per engagement. Each cell names the `/seja-setup` variant we run and one sentence on what changes in the files we write for that cell:

| Profile / pattern | Solo designer | Engineering team | Mixed |
|---|---|---|---|
| Greenfield collocated | `/seja-setup <target>` (greenfield path, embed in the new repo) -- we author a fresh `constitution.md` and a minimal `product-design-as-intended.md` keyed to one voice, see [greenfield-collocated.md](how-to/greenfield-collocated.md). | `/seja-setup <target>` (greenfield path, embed in the new repo) -- we author the design files with stricter review-perspective defaults and richer `conventions.md` so multiple builders share the same rules, see [greenfield-collocated.md](how-to/greenfield-collocated.md). | `/seja-setup <target>` (greenfield path, embed in the new repo) -- we split `conventions.md` so designers own the standards section while engineers own the path-scoped rules, see [greenfield-collocated.md](how-to/greenfield-collocated.md). |
| Greenfield workspace | `/seja-setup <target> --workspace` (greenfield workspace path) -- we create a standalone workspace repo next to the new product repo and generate launcher scripts so you can run `/design` without touching code, see [greenfield-workspace.md](how-to/greenfield-workspace.md). | `/seja-setup <target> --workspace` (greenfield workspace path) -- we separate the harness repo from the product repo so designers can iterate on specs without blocking engineering PRs, see [greenfield-workspace.md](how-to/greenfield-workspace.md). | `/seja-setup <target> --workspace` (greenfield workspace path) -- we generate launcher scripts that point at the product codebase and set `conventions.md` to split ownership between designers and engineers, see [greenfield-workspace.md](how-to/greenfield-workspace.md). |
| Brownfield collocated | `/seja-setup <target>` (brownfield embed path) -- we detect existing source code, offer to embed the harness in place, and queue `/explain drift` as the first real task so we can reconcile intent against code, see [brownfield-collocated.md](how-to/brownfield-collocated.md). | `/seja-setup <target>` (brownfield embed path) -- we embed the harness alongside existing code and tune `product-design-as-intended.md` to the conventions we reconstructed from the codebase, see [brownfield-collocated.md](how-to/brownfield-collocated.md). | `/seja-setup <target>` (brownfield embed path) -- we embed in place and split drift review between designers and engineers so both voices land in the Decisions log, see [brownfield-collocated.md](how-to/brownfield-collocated.md). |
| Brownfield workspace | `/seja-setup <target> --workspace` (brownfield workspace path) -- we create a companion workspace for the existing codebase, offer to migrate any embedded harness files into it, and keep design history in its own git log, see [brownfield-workspace.md](how-to/brownfield-workspace.md). | `/seja-setup <target> --workspace` (brownfield workspace path) -- we create a companion workspace so designers can run `/explain drift` on the existing code without writing into the product repo, see [brownfield-workspace.md](how-to/brownfield-workspace.md). | `/seja-setup <target> --workspace` (brownfield workspace path) -- we create a companion workspace with launcher scripts and pre-seed `conventions.md` for shared design-plus-engineering ownership, see [brownfield-workspace.md](how-to/brownfield-workspace.md). |

Picking a cell in this matrix is how we interpret "which SEJA are you running" for the rest of our work together.

## Setup modes

Four ways to run `/seja-setup`, all the same verb, none of them implying that SEJA must be copied somewhere else before you use it. The verb is location-agnostic; the mode you pick reflects how the harness files are already arranged when you start, or whether you are refreshing an already-installed project.

- **`/seja-setup <target>`** -- copy the harness into a new or empty project directory. We create the directory if needed, copy skills, rules, and references into place, initialize git, and hand off to `/design`. Use this when the harness source is in a separate clone and your project is a new location.
- **`/seja-setup --here`** -- finalize setup in place in the current directory. We assume the harness files are already present (typically because you ran `git clone https://github.com/simonedjb/seja my-project` into this folder), and we complete the initialization: `_output/` skeleton, `product-design/` placeholder, `.claude/settings.json`, `.seja-version` pin, and an optional cleanup of harness-dev artefacts. Use this when you downloaded SEJA directly into your project folder.
- **`/seja-setup --workspace`** -- create a companion workspace alongside an existing codebase. We keep design and code in separate git repos, generate launcher scripts that point our session at the codebase via `claude --add-dir`, and leave your codebase untouched. Use this when design and code have different review cadences or different contributors.
- **`/seja-setup --upgrade`** -- refresh harness files in an already-installed project to the latest release (or a specific `--version <tag>`). Preserves project-specific files, settings, and output. Use this when a newer version of SEJA has been published and you want to pull it in.

`/seja-setup` with no arguments inspects the current directory and routes to the right mode automatically: install into an empty project, finalise in place inside a fresh download, offer an upgrade inside a finalised project, or refuse when it detects the SEJA development repo itself.

```mermaid
flowchart LR
    start([Starting state]) --> mode{Where are the<br/>harness files?}
    mode -->|"Cloned elsewhere; project is a new dir"| copy["/seja-setup &lt;target&gt;"]
    mode -->|"Cloned directly into my project folder"| here["/seja-setup --here"]
    mode -->|"I want a separate workspace next to my code"| workspace["/seja-setup --workspace"]
    copy --> design[/design]
    here --> design
    workspace --> design
    design --> work[Plan, implement, check, ...]
    work -->|"Later, refresh the harness"| up["/seja-setup --upgrade"]
```

The install branches converge on `/design`. Whichever install mode you take, you end up at the same next step, and `/seja-setup --upgrade` handles harness refreshes from that point on.

## Role families

The same skill surface has to address very different readers. We use role families and expertise levels to tune the tone and depth of what we write for a specific teammate without forking the skills themselves. The pair (role family, expertise level) is the unit `/onboard` plans are cut against, and the role family alone is also how `/communicate` picks which audience framing to apply.

<a id="bld-shp-grd"></a>
### BLD, SHP, GRD

A **role family** in SEJA is one of three coarse groupings that cover everyone a project involves. **BLD (Builders)** is the role family for developers, DevOps engineers, and infrastructure engineers who write, deploy, and maintain code: they read architecture diagrams, coding standards, CI pipelines, and data-model references, and they learn best when we hand them annotated code and convention files. **SHP (Shapers)** is the role family for product managers, UX and UI designers, researchers, and analysts who define what gets built and how: they read `product-design-as-intended.md`, journey maps, metacommunication, and the design system, and they learn best when we narrate a persona's path through a feature without dragging them into source code. **GRD (Guardians)** is the role family for QA engineers, security engineers, tech leads, and engineering managers who ensure quality, alignment, and governance: they read the review-perspective framework, test strategy, security policies, and quality-gate configuration, and they learn best when we hand them the `/critique review` surface and the perspective catalog as their working toolkit. When you run `/onboard bld L2 Alice` or `/communicate clt`, the first token is what we branch on to pick the right reference files.

<a id="expertise-levels"></a>
### Expertise levels L1 through L3

Inside each role family we stratify by expertise so we can scale scaffolding against experience. **L1 Contributor** is the expertise level for junior to mid-level individual contributors (roughly 0-5 years) who need guidance on how, what, and where: newcomers get explicit step-by-step walkthroughs and reviewable first tasks, while mid-level practitioners get project-specific context and convention reference sheets with moderate safety nets. **L2 Expert** is senior expertise (roughly 5-10 years); we produce decision history, architecture deep-dives, trade-off analyses, and mentoring tasks because L2 readers want the "why" behind every pattern and are expected to challenge conventions they find questionable. **L3 Leader** is tech lead, staff engineer, or engineering manager expertise (10+ years or equivalent); we produce team-health dashboards, cross-team dependency maps, governance audits, and process-improvement context so a leader can build trust and pick their first cross-cutting initiative without disrupting what already works.

We combine the role family and the level into a single `(family, level)` tuple when you run `/onboard`. That tuple tells us which reference files under `.claude/references/general/onboarding/` to load and which learning path to cut for the teammate you are onboarding, so the plan we write fits their role and their starting experience at the same time.

## Review perspectives

We never "just review" your work. Every plan we draft and every change we evaluate passes through a fixed catalog of 16 **review perspectives**, each one a named domain lens that asks the same questions every time: what could go wrong here, what would a specialist in this domain insist on, and is the evidence in front of us good enough to answer both. The catalog is split into two tiers: the **Essential tier** holds the perspectives we shortlist first because they catch the highest-frequency issues across most work, and the **Deep-dive tier** holds the more specialized lenses we pull in only when your work's prefix and scope warrant the extra attention. Within each tier the perspectives carry a priority band from P0 through P4 so we know which voice speaks first when two perspectives disagree. For a standalone catalog you can browse independent of this narrative, see [docs/reference/perspectives.md](reference/perspectives.md).

The 16 perspectives:

| Tag | Name | Scope |
|-----|------|-------|
| SEC | Security | Auth, input validation, secrets management, dependency vulnerabilities |
| PERF | Performance | N+1 queries, unbounded loops, indexes, caching, bundle size |
| DB | Database | Schema migrations, backward compatibility, idempotency, constraints |
| API | API Design | RESTful conventions, route consistency, request/response contracts |
| ARCH | Architecture | Layer boundaries, separation of concerns, dependency direction |
| DX | Developer Experience | Readability, conventions, documentation, error messages |
| I18N | Internationalization | i18n keys, locale support, pluralization, RTL, date/number formats |
| TEST | Testability | Test coverage, new test needs, mocking strategy, test isolation |
| OPS | Operations / DevOps | Environment parity, logging, monitoring, deployment, config management |
| COMPAT | Compatibility | API contract stability, schema evolution, browser/version support |
| DATA | Data Integrity & Privacy | PII handling, GDPR compliance, validation, audit trails |
| UX | User Experience | User flows, feedback, error handling, navigation, discoverability |
| A11Y | Accessibility | WCAG AAA, contrast, keyboard nav, screen readers, focus management |
| VIS | Visual Design | Design system consistency, CSS conventions, spacing, typography |
| RESP | Responsive Design | Mobile/tablet/desktop breakpoints, fluid layouts, touch targets |
| MICRO | Microinteractions | Hover/focus/active states, transitions, loading indicators, animations |

Two-stage loading keeps the review focused. We shortlist the 3 to 6 perspectives that match your work's prefix and scope; we load the rest only if we find something that warrants deeper attention. If you want the long form of any perspective, the foundational harness ships per-perspective reference files under its `.claude/references/general/review-perspectives/` directory with the full questionnaire, red flags, and example findings we draw on during a review. That directory is internal to the harness repo rather than part of this public site, so open it locally when you want to study a single lens in depth.

## Skills overview

A **skill** is a `SKILL.md` file under `.claude/skills/<name>/` that defines an agent-invocable capability and is invoked via a slash command. We expose 15 user-facing skills plus 2 internal lifecycle hooks we run on your behalf. For a standalone catalog of every skill with its one-line intent, see [docs/reference/skills.md](reference/skills.md). The 15 user-facing skills group into five purposes:

**Design and planning**

- `/design` configures SEJA for your project: on first run it walks you through a questionnaire (or parses a spec file) to define your stack, domain model, and conventions, then generates the project-specific reference files; on later runs it lets you update any section of your project design.
- `/plan` creates a step-by-step plan for your next feature, bug fix, or improvement that you can review before anything changes; with `--roadmap` it generates a full product roadmap with dependency-aware execution waves drawn from your design specs.
- `/implement` runs a previously approved plan step by step, and nothing changes in your project until you have reviewed and approved the plan first.

**Quality and maintenance**

- `/critique` is the unified quality gate that runs validation scripts, code reviews, smoke tests, preflight checks, harness health diagnostics, or user test plan generation: one skill for all "is it OK?" questions.
- `/explain` gives you a clear explanation of how something works (a feature's behavior, the data model, the overall architecture, or the drift between your design specs) with diagrams and analogies, and its drift mode also offers an interactive sync workflow to realign diverged specs.
- `/document` generates or updates documentation for your project, reading plan `Docs:` fields, detecting changes from git history, or targeting a specific documentation type, and uses project templates plus the documentation-quality writing guide for structured generation.

**Knowledge and communication**

- `/research` answers any question about the project (architecture, design decisions, trade-offs) by researching your codebase, analyzing from multiple perspectives, and giving you actionable recommendations; with `--inventory` it catalogs all codebase elements matching a pattern.
- `/communicate` generates tailored communication material for a specific audience (evaluators, clients, end users, or academics), each in their language and focused on what matters to them.
- `/onboard` creates a personalized onboarding plan based on role and experience level, covering what to learn, in what order, and where to find things, so you can onboard a new teammate or yourself.
- `/reflect` anchors a reflection session on specific artifacts you choose; in its default conversational mode it summarizes the artifacts, asks whether you are reflecting on the **product** (what was built — reflection-on-action on the artifact) or your **practice** (how you worked — Schön's reflection-on-practice), then asks the matching question and records your own words verbatim; it is strictly non-prescriptive, and `/research` is the follow-up skill when you want recommendations on what to change. With `--deep`, it produces an event-matrix heat map, a skill-transition graph, and a practice-evolution narrative across a chosen time window; with `--telemetry`, it mines usage patterns across weeks (sequences, durations, revisions, stuck loops, decision reversals).

**State management**

- `/pending` shows outstanding human actions we are tracking for you (items to verify, markers to flip, proposals to apply, periodic curations) and walks you through addressing them one at a time; the ledger at `_output/pending.jsonl` is append-only so you can snooze, dismiss, or defer items without losing history.
- `/qa-log` saves the current conversation (questions and answers) to a file for future reference, which is useful for documenting decisions and rationale.

**Bootstrap**

- `/seja-setup` copies the SEJA harness files into a target directory: for greenfield projects it creates the directory and initializes git, for existing codebases it embeds the harness alongside existing code, with `--workspace` it creates a separate workspace directory instead, and with `--upgrade` it refreshes harness files in an already-installed project while preserving project-specific data and showing you a summary of changes before applying them.
- `/help` shows you what skills are available and explains what each one does, so you can browse by category to discover skills or get details on a specific one.

Two more skills, `pre-skill` and `post-skill`, run on our behalf around every user-facing skill invocation. You never call them directly, but they are what wraps each slash command with the reflection-in-action and reflection-on-action pipelines that make the harness's behavior consistent and auditable. We cover both in the harness lifecycle chapter below.

<a id="lifecycle-two-paths"></a>
## Lifecycle: canonical path

SEJA runs a single canonical lifecycle path around every engagement, and the one gating invariant is "validate before you communicate": `/critique` always comes before `/document` and `/communicate`, so nothing leaves the envelope until it has been validated. The canonical sequence is:

`/research` (or `/explain`) > `/design` | `/plan` > `/implement` > `/critique` > `/document` | `/communicate` > `/reflect`

Read the `|` as "choose one, depending on intent" and the `>` as "and then." You enter at `/research` when you have a research question or at `/explain` when you want to understand how something works; the answer either flows into `/design` (if intent needs to change) or into `/plan` (if intent is settled and you are ready to build). After `/plan` the build cycle runs through `/implement` and `/critique`, and only once `/critique` has validated the work do you hand off to `/document` or `/communicate` for the reader-facing artifacts. `/reflect` closes the cycle.

| Stage | Skills | Purpose |
|---|---|---|
| **Research** | `/research` or `/explain` | ask a question or understand how something works |
| **Shape the work** | `/design` or `/plan` | change intent (design) or commit to a build (plan) |
| **Build** | `/implement` | execute an approved plan |
| **Validate** | `/critique` | run the quality gate before anything reader-facing ships |
| **Communicate** | `/document` or `/communicate` | write reader-facing artifacts only after validation |
| **Close the cycle** | `/reflect` | record what the turn taught you before the next one starts |

The first iteration of a brand-new project is the only exception to entering at `/research` or `/explain`: on iteration 1 you run `/seja-setup` to copy the harness files into your target and then hand off to `/design` to produce the project-specific reference files. From iteration 2 onward, the canonical path above is your default front door and `/seja-setup` is no longer in the loop as an install -- if you need to refresh harness files on a configured project, `/seja-setup --upgrade` is the right tool because it preserves your project-specific files while pulling the latest harness code. `/explain drift` is the alignment workflow you reach for when intent and code have drifted and you want to reconcile them before re-entering the canonical path.

For a visual rendering of the canonical path, see the Framework Map module in the public tutorial materials, which lays out the skills and their relationships as a single diagram. The auto-generated [skill map](concepts/skill-map.md) flattens the catalog into one graph for reference; use the sequence above as the canonical ordering whenever the two disagree.

## Decision matrix

Three of the skills in the skills overview look deceptively similar at first glance: `/research`, `/explain`, and `/communicate` all accept a question or a request for text output, and all three produce markdown reports. The resemblance is surface-deep. Each answers a different intent: `/research` helps you decide, `/explain` helps you understand, and `/communicate` helps you tell someone else. When you give us an ambiguous prompt, the table below is the decision rule we run in our head before we pick a skill.

<a id="advise-vs-explain-vs-communication"></a>
<a id="research-vs-explain-vs-communication"></a>

### /research vs /explain vs /communicate

| You want to... | Reach for | Because |
|---|---|---|
| Ask an open design question with multiple viable answers | `/research` | We research your codebase, evaluate the question against multiple review perspectives, and hand back an actionable recommendation with pros and cons; the Q&A pair is logged in the research report for later recall. |
| Catalog codebase elements matching a pattern (all endpoints, all models, all form components) | `/research --inventory` | We scan the source and produce a structured inventory of every matching element, its location, and where it is used. |
| Run a high-stakes decision through a structured expert debate | `/research --deep` | We assemble a 5 to 7 member expert council, run a two-round debate, and give you back position statements, cross-examination, and synthesis. |
| Understand how an existing feature behaves in the running product | `/explain behavior` | We read the code, trace a persona's interactions with the feature, and produce an analysis report with diagrams and analogies for the current behavior. |
| Understand the data model, overall architecture, or how code works at a specific location | `/explain data-model`, `/explain architecture`, `/explain code` | We emit a repeatable architectural explainer scoped to the target, aimed at a teammate being onboarded on that slice of the product. |
| Trace how a feature got to its current shape over time | `/explain behavior-evolution` | We mine the plan history, build a chronological timeline of waves, and produce before-and-after narratives for each significant change. |
| Understand architectural rationale and where intent has drifted from code | `/explain drift` | We compare `product-design-as-intended.md` with `product-design-as-coded.md` section by section and surface added, removed, and modified items as a drift report. |
| Generate stakeholder-facing material for a specific audience segment | `/communicate <audience>` | We produce tailored content for EVL, CLT, USR, or ACD audiences, each in the language and framing that audience cares about, emitted as date-versioned files. |
| Produce material for every audience segment in one batch | `/communicate --all` | We launch one generator agent per audience in parallel and write the results into a shared date folder with an index linking them. |
| Understand a confusing part of the codebase | `/explain code` then `/explain architecture` | We start with a local code explanation, then zoom out to see how it fits the system; follow up with `/research` if the explanation raises design questions. |

Output locations follow the project conventions variables. `/research` writes research reports to `${ADVISORY_DIR}` (the directory may appear as `advisory-logs/` or `research-logs/` depending on when the project was created) with the logged Q&A pair and a recommendations summary, and `/research --inventory` writes catalog reports to `${INVENTORIES_DIR}`. `/explain` writes analysis reports to the explained-* directories (`${EXPLAINED_BEHAVIORS_DIR}`, `${BEHAVIOR_EVOLUTION_DIR}`, `${EXPLAINED_CODE_DIR}`, `${EXPLAINED_DATA_MODEL_DIR}`, `${EXPLAINED_ARCHITECTURE_DIR}`), with the drift mode writing into `${ADVISORY_DIR}` because its output is advisory-shaped. `/communicate` writes date-versioned audience-specific files into `${COMMUNICATION_DIR}/<YYYY-MM-DD>/`, with a per-date `index.md` when more than one audience is generated on the same day.

Now that you know which skill to reach for, let us show you the envelope every one of these skills runs inside. The harness lifecycle chapter walks through the reflection-in-action and reflection-on-action pipelines we wrap around every slash command.

## Harness lifecycle

Everything in the previous chapters -- the signs, the profile x pattern picker, the role families and expertise levels, the review perspectives, the skill portfolio, and the decision matrix -- is wrapped in a lifecycle envelope we run on your behalf. Every slash command you invoke flows through a `pre-skill -> skill body -> post-skill` envelope, so the way a skill loads references, logs what it is doing, evaluates context budget, injects your constitution, updates the as-coded files, and proposes a commit is the same across the catalog. When something in this envelope misbehaves -- an orphaned brief, a pending ledger you cannot reconcile, a stuck loop -- see [docs/troubleshooting.md](troubleshooting.md) for common failure modes and their fixes.

This chapter is the canonical home for that envelope. The first three H3s below cover the envelope itself: the overall skill lifecycle, then the pre-skill 6-stage pipeline, then the post-skill pipeline. The next three cover the state the envelope reads from and writes to: the pending ledger, the constitution, and the section boundaries that keep multi-section files safe to edit. The final two cover the reconciliation surface: the two specs files (`product-design-as-intended.md` and `product-design-as-coded.md`) and the D-NNN Decision entries that record the rationale whenever intent and code need to be brought back into alignment. Later how-to guides link back to these anchors instead of redefining the mechanics inline, so if you are reading a how-to and you hit an unfamiliar reference to a pipeline stage, a marker type, or a Decision ID, the link almost always points here.

### Skill lifecycle

Every slash command is wrapped by two internal hooks, and the three-step sequence below is the shape every turn takes:

1. **Pre-skill** runs first. It loads context, logs the brief, evaluates the context budget, loads references, and injects your constitution. Think of it as the reflection-in-action stage: we check our working conditions before we start producing anything.
2. **Skill body** runs next. This is where the slash command you typed actually does its work and produces an artifact under `_output/` (a plan, a research report, an explanation, a communication package, an onboarding plan, and so on).
3. **Post-skill** runs last. It updates the brief from STARTED to DONE, refreshes indices, logs a QA transcript, reconciles the as-coded specs, proposes STATUS marker flips for confirmation, and offers a git commit. Think of it as the reflection-on-action stage: we review and record what just happened so the next turn starts from a clean, auditable state.

The envelope is why two successive `/plan` invocations leave the same audit trail regardless of which skill body ran between them. Whatever skill runs in the middle inherits the same entry and exit conditions, so the surrounding narrative stays uniform across the catalog.

It is also why we can resume a turn in a fresh session without losing the thread: the brief, the QA log, and the commit message together reconstruct what we were doing and why, which is the reflection-in-action and reflection-on-action loop closing on itself.

The specific stages and steps of each hook are covered in the next two sections.

<a id="pre-skill-pipeline"></a>
### Pre-skill 6-stage pipeline

The **pre-skill pipeline** is the six-stage pipeline run before every skill: help, brief-log, budget-eval, pending-check, ref-load, constitution. Three of those stages are **critical** and always run; the other three are **non-critical** and error-isolated, which means a failure in any one of them is logged but does not block the skill body. The stages in order:

1. `help` -- intercepts `--help` and prints the Quick Guide for the calling skill, then exits before the skill body runs.
2. `brief-log` -- records the STARTED entry in the briefs file so you can see what we are doing even if the session crashes mid-turn.
3. `budget-eval` -- picks the light, standard, or heavy context budget tier and loads the recent briefs window sized to that tier; sub-steps within budget-eval include orphan detection (detecting STARTED entries without a matching DONE from a previous crashed turn) and compaction warning (warning when the session has accumulated many skill invocations and may be about to summarize older context).
4. `pending-check` -- surfaces the count of outstanding items from the pending ledger and runs lazy periodic triggers when they come due.
5. `ref-load` -- loads conventions, permissions, constraints, and the skill-specific references the calling skill declares in its SKILL.md metadata.
6. `constitution` -- injects your project constitution into the skill's prompt so trust boundaries are enforced before any generation happens.

`brief-log`, `budget-eval`, and `ref-load` are the three critical stages. A skill may opt out of any non-critical stage by listing the stage ID in `metadata.skip_stages` in its SKILL.md frontmatter; critical stages cannot be skipped.

<a id="post-skill-pipeline"></a>
### Post-skill 13-step pipeline

The **post-skill pipeline** is the lifecycle hook run after every skill for briefs update, QA logging, as-coded updates, marker proposals, and git commit. Its 13 steps group into four bands:

- **Bookkeeping** (steps 1-3: brief-update, telemetry-event, qa-transcript): update the brief entry from STARTED to DONE, record a telemetry event for cost and latency accounting, and log a QA transcript via `/qa-log` so the turn's questions and answers are captured for later recall.
- **As-coded reconciliation** (steps 4-6: as-coded-reconcile, doc-freshness, index-regeneration): when a plan ran, reconcile `project/product-design-as-coded.md` section by section against what actually changed on disk, run the documentation freshness check so stale docs get flagged, and regenerate the `INDEX.md` files under `_output/` so navigation stays in sync with the artifacts the turn produced.
- **Safety and marker proposals** (steps 7-10: preflight-gate, human-markers-verify, pending-append, status-marker-propose): run the fast preflight gate and the human-markers verifier before staging so a bad write never reaches the commit, write any deferred actions into `_output/pending.jsonl`, and propose STATUS marker flips to you through `AskUserQuestion` so any write into a Human (markers) file is confirmed in the same turn.
- **Commit and handoff** (steps 11-13: stage-and-commit, next-step-suggest, contextual-handoff): stage and commit the affected files with a message keyed to the skill and invocation ID for auditability, then surface contextual next-step suggestions through `AskUserQuestion` once the commit lands so the next turn starts from a known good state.

The key artifacts touched every turn are the briefs file (`_output/briefs.md`), the `_output/qa-logs/` directory, the `INDEX.md` files under `_output/`, the pending ledger at `_output/pending.jsonl`, proposed STATUS markers in `project/product-design-as-intended.md`, the reconciled sections of `project/product-design-as-coded.md`, and the git commit itself. Every one of these is addressable after the fact, so you can reconstruct what happened on any turn by reading the brief, the QA log, and the commit diff side by side.

### Pending ledger

The **pending ledger** is the append-only JSONL log at `_output/pending.jsonl` tracking outstanding human actions surfaced by skills. It is where we park actions we cannot finish on our own. Entries fall into four categories:

- **Marker confirmations**: `mark-implemented` (STATUS flip after a plan runs), `apply-promote-markers` (ESTABLISHED flip after curation), `incorporate-research-markers` (research findings to fold into intent), and `create-decision-entry` (D-NNN entries to draft).
- **Implementation follow-ups**: `implement` (filed at `/plan` completion, closed at `/implement`), `test-implementation` (manual test verification), `verify-as-coded` (confirm the as-coded file matches reality), and `update-documentation` (docs that need refreshing after a change).
- **Periodic triggers**: `periodic-curation` (design-intent reviews on a cadence) and `spec-drift-check` (scheduled drift reconciliation).
- **User-defined**: `user-defined` entries you add via `/pending add` for anything not covered above. `PUBLISH:` description-prefixed entries are filed by the release tooling to track outstanding publish work. Post-skill appends entries; pre-skill's `pending-check` stage surfaces their count to you at the start of each turn; `/pending` is the skill that walks you through the ledger one entry at a time so you can resolve, snooze, or dismiss each one. The ledger is append-only on purpose, so snoozing or dismissing an entry leaves a trace you can audit later. JSONL as the storage format is deliberate: every entry is a self-contained JSON object on one line, which makes the ledger trivial to grep, sort, diff, and replay without dragging in a schema migration whenever we want to add a new entry type.

Two workflows illustrate how the ledger fits into practice:

- **Deferred review**: after `/implement` finishes a plan, post-skill offers to apply IMPLEMENTED markers. If you choose **Defer for later review**, pending entries are created (`mark-implemented`, `verify-as-coded`, `test-implementation`, `update-documentation`). You test manually, then run `/pending` to verify and flip markers one at a time. Pre-skill's `pending-check` keeps reminding you about outstanding items until the ledger is empty.
- **Periodic curation**: when a `periodic-curation` entry comes due (typically every 30 days), pre-skill surfaces it. Run `/explain drift` to identify promotion candidates, then `/explain drift --promote` to generate a proposal report with draft `D-NNN` Decision entries. Copy accepted entries into `product-design-as-intended.md`, then run the marker pass (`/explain drift --promote --apply-markers plan-<NNN>`) to flip STATUS markers from `implemented` to `established`. Finally, `/pending done <id>` on the curation item.

### Path-scoped rules

Seven rule files live under `.claude/rules/` and are auto-loaded when Claude edits files matching the rule's path scope. Rules for `backend`, `frontend`, `e2e`, `i18n`, `migrations`, and `tests` point the agent at the review perspectives most relevant to each file type, while the `harness-structure` meta-rule provides the full component inventory when editing `.claude/` files. Rules provide contextual guidance, not permissions -- they do not grant or restrict write access. They are distinct from the project-wide conventions in `project/conventions.md`, which declare paths, variables, and project-level settings rather than file-scoped review guidance.

### Constitution

The **constitution** is the immutable project principles in `project/constitution.md`, never agent-altered, required for new projects. It is copied in by `/seja-setup` from `.claude/references/template/constitution.md`, instantiated by `/design`, and classified Human -- we load it on every turn but we never edit a word of it. We inject its contents into the prompts of generator agents (like `communication-generator`, `onboarding-generator`, and `document-generator`) so their output stays inside the principles you committed to. `/critique health` validates that the constitution is present as one of its checks, and a new project without a constitution is blocked from proceeding past `/design`. The constitution is the one file whose wording is load-bearing for trust boundary enforcement across the catalog.

### Section boundaries

A **section boundary** is an enforcement rule preventing agents from writing outside designated H2 sections of a multi-section file, validated by `check_section_boundary_writes.py`. `project/product-design-as-coded.md` is the canonical example: one file divided into three H2 sections (`## Conceptual Design`, `## Metacommunication`, and `## Journey Maps`), each with different write boundaries and different post-skill logic pointing at it. Section boundaries are the technical mechanism that lets us share write access inside a single file without stepping on each other: we update one section while your prose or your markers stay untouched in the others, and the guardrail catches any accidental spill before it reaches disk. The same idea scales to any multi-section Agent-classified file in your project: declare the H2s, register them as boundaries, and let the guardrail hold the line so one skill's edits cannot corrupt a neighboring section by mistake.

<a id="product-design-as-intended-vs-as-coded"></a>
### product-design-as-intended vs product-design-as-coded

SEJA tracks two design specs, and keeping them legible as distinct artifacts is what makes drift reconciliation possible. The as-intended / as-coded distinction is the heart of the reconciliation model: one file holds intent, the other holds the implementation state, and the skill in between is what tells you where the two disagree.

- **product-design-as-intended**: Unified working-intent file (`project/product-design-as-intended.md`) holding design intent, DDR-shaped Decisions, and CHANGELOG, classified Human (markers). You own the prose and we may only stamp STATUS, ESTABLISHED, and CHANGELOG_APPEND markers into it through `apply_marker.py` after you confirm the edit in the same turn. This file holds your working intent in sections 0 through 17.
- **product-design-as-coded**: Unified implementation-state file (`project/product-design-as-coded.md`) auto-maintained by the agent, with three H2 sections: Conceptual Design, Metacommunication, Journey Maps. We maintain this file via post-skill writes and its three sections mirror the implementation state of the corresponding sections of the intended file.
- `/explain drift` is the skill we run to surface the delta between the two prose files, section by section, so you can see what got added, removed, or modified relative to intent.

<a id="decision-entries"></a>
### D-NNN Decision entries

When the drift between intent and code warrants a recorded rationale, we draft a D-NNN Decision entry. These are DDR-shaped records (short for Design Decision Record) living in the Decisions section of `project/product-design-as-intended.md`, each carrying a stable `D-NNN` ID in a namespace orthogonal to the REQ-TYPE-NNN traceability markers that cover individual requirements. Every Decision entry has four parts:

- **Context** -- one short paragraph on the situation that forced the decision (what code was doing, what intent said, and why the gap mattered enough to record).
- **Decision** -- the option chosen, stated in one sentence so a future reader can grep the Decisions log for "we chose X" without reading every entry in full.
- **Consequences** -- the follow-on effects on intent, code, tests, or other Decisions that the choice locks in, including any requirements promoted or retired as a result.
- **Supersedes** (optional) -- a pointer to any earlier D-NNN this entry replaces, so the chain of rationale stays legible when a past decision is revisited.

Decision entries are promoted through `/explain drift --promote`, which runs in two passes: the proposal pass drafts Decision entry proposals and writes them to the pending ledger for your review, and the marker pass accepts your confirmed proposals and flips the corresponding STATUS markers by running `apply_marker.py` via the `--apply-markers plan-<id>` entry point. The split is what lets you approve the rationale and the marker flips independently, so the audit trail records both your decision and the resulting state change. The orthogonality between D-NNN Decision IDs and REQ-TYPE-NNN requirement IDs is deliberate: a Decision may touch many requirements, and a requirement may be shaped by more than one Decision over its lifetime, so the two namespaces are kept separate to avoid forcing a false one-to-one mapping.

That covers the envelope. Run `/help` for the skill catalog, read [quickstart.md](quickstart.md) if you have not yet, and open the how-to guide whose filename matches your profile-plus-pattern cell for the step-by-step path that fits your engagement.

Each how-to links back to the anchors in this file whenever it needs to refer to a sign, a role, a review perspective, a skill, or a lifecycle concept, so you can always return here for the underlying model. If you find yourself reading a how-to and wondering "why does SEJA do it this way", the answer is almost always in one of the chapters above: the sign system explains who may write where, the profile x pattern picker explains which starting shape you are in, the role families explain who a document is being written for, the review perspectives explain how we judge quality, the skills overview explains the catalog, the decision matrix explains how we disambiguate between overlapping skills, and this chapter explains the envelope every skill runs inside. Keep this file open in a second tab while you work and you will have everything you need to read what we are doing for you and why.
