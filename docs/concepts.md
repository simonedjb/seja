# Concepts

We wrote this file as the "why" companion to the quickstart. Our goal here is to introduce you to the ideas SEJA runs on before you meet the skills that put those ideas to work. In the chapters that follow we cover the sign system we use to classify files and track intent, the profile x pattern picker that tells us how to set SEJA up for your codebase, the role families and expertise levels we tune our output to, the review perspectives we apply when we critique work, the skill portfolio and the decision matrix we use to pick among overlapping skills, and the framework lifecycle we run around every skill invocation. Later how-to guides link back to this file by anchor, so think of it as the reference we point to instead of repeating these definitions inline. For one-line definitions of every term used below, see [docs/reference/glossary.md](reference/glossary.md). For a visual anchor on how the skills connect to each other as a workflow, see [docs/concepts/skill-map.md](concepts/skill-map.md). For a cookbook of common multi-skill workflows you can follow step by step, see [docs/how-to/recipes.md](how-to/recipes.md).

## Epistemic stance

Before we introduce the sign system, the profile picker, and the rest of the ideas this file is built on, we want to tell you how to read what follows. Everything in this file is our current reading of how SEJA holds together. We have tried to be honest about what we know and what we are hedging on, but our reading is always provisional. When your practice shows us a better reading, we want to hear about it. The `/advise` skill is the channel, and concrete counter-readings with artifact paths get further than abstract disagreement.

We ground this stance in the semiotic engineering tradition (de Souza 2005, 2009; SigniFYI 2016; EMT-Ethics 2021) and in Schon's reflective practice (1983). If any of those references feel alien, the short primer at [foundations.md](foundations.md) walks through what we take from each of them, in plain language and without assuming a research background. You do not need to read the primer to use SEJA, but you do need to know that everything here is open to revision.

With that in mind, here is the sign system we use to classify files and track intent.

## Sign system

We treat your project as a communication medium. Every file in it either carries your voice, our voice, or a narrow seam of structured markers through which we are allowed to record lifecycle events on your behalf. The sign system is how we keep those voices from bleeding into each other: three file classifications tell us who may write to a file, and three marker types track how design intent moves from "proposed" to "established" without anyone having to rewrite prose to reflect the change. If you want to know why we treat conventions as a sign system at all -- rather than as arbitrary stylistic rules -- the short primer at [foundations.md](foundations.md) walks through the grounding. The glossary holds the one-line definitions; this chapter narrates the underlying model so you can recognize the signs when you open the repo.

<a id="human-human-markers-agent"></a>
### Human, Human (markers), Agent

Three classifications, one per author. **Human** -- File classification for content authored and updated exclusively by humans; agents may read it but must not write to it. We treat Human files as read-only reference. Your `project/constitution.md` is the canonical example: we load it at the start of every skill so we stay inside the principles you committed to, but we never edit a word of it. **Human (markers)** -- File classification for human-authored prose where agents may write only fixed-format structured markers via `apply_marker.py`, and only after explicit confirmation in the same turn. Your `project/product-design-as-intended.md` is the canonical example: you author the design intent in your voice, and we may only stamp STATUS, ESTABLISHED, or CHANGELOG_APPEND markers into it after you have confirmed the edit in the same turn. The guardrail is `check_human_markers_only.py`, which rejects any write that is not a recognized marker pattern. **Agent** -- File classification for content auto-maintained by agents and skills (e.g., via post-skill); humans typically do not edit it directly. `project/product-design-as-coded.md` is the canonical example: we reconstruct and refresh it after implementation, and `check_section_boundary_writes.py` keeps our edits inside its declared H2 sections so we cannot accidentally spill across Conceptual Design, Metacommunication, and Journey Maps.

<a id="status-established-changelog-append"></a>
### STATUS, ESTABLISHED, CHANGELOG_APPEND

Three marker types, one per lifecycle event. **STATUS** -- Inline HTML comment marker above a section heading tracking its lifecycle state through `proposed -> implemented -> established -> superseded`, with plan ID and date. We use STATUS to answer "where is this item on its way from idea to reality?" The state machine is linear: you start an item as `proposed`, a plan flips it to `implemented` once the code lands, you promote it to `established` once you verify the result, and it may later be `superseded` by a newer decision. `apply_marker.py` enforces the allowed transitions; regression is rejected. **ESTABLISHED** -- Inline HTML comment stamp recording that a human has promoted an implemented item to established status, carrying plan ID, date, and optional version. ESTABLISHED is the promotion stamp we write only after you confirm the promotion; it is how we mark that a design decision has crossed from "working" to "committed." **CHANGELOG_APPEND** -- Append-only marker type used to add entries to a CHANGELOG section of a Human (markers) file via `apply_marker.py`. CHANGELOG_APPEND is append-only on purpose: we may add new entries to the CHANGELOG section, but we may never rewrite or remove existing ones, so the audit trail of what happened and when stays intact.

A STATUS marker looks like this above the heading it annotates:

```markdown
<!-- STATUS: proposed | plan-NNNNNN | YYYY-MM-DD -->
### Section Title
```

The comment is invisible in the rendered markdown but machine-parseable by `apply_marker.py` and `check_human_markers_only.py`, which is how the sign system stays out of your way while still giving us something reliable to read and write.

Now that you can read the signs, here is how we choose what to do for you next. The profile x pattern chapter is where we describe the two-axis picker we run through at the start of every engagement to decide which how-to guide fits your situation, which deployment layout we should propose, and which skills you should expect to lean on first.

## Profile x pattern

We slice your starting situation along two orthogonal axes before we write a single file for you. The profile axis asks what your codebase already looks like and where SEJA will live relative to it; the pattern axis asks who we are writing for. Together they pick one cell from a small matrix, and that cell tells us which `/seed` variant we run, which how-to guide we open, and how much reconciliation work we should expect before you see value.

<a id="greenfield-brownfield"></a>
### Greenfield and brownfield

The first half of the profile axis is about your code. **greenfield** is the project profile for a brand-new project with no pre-existing codebase: we help you author design intent from scratch, and there is nothing to reconcile against because nothing is built yet. **brownfield** is the project profile for embedding or attaching SEJA to an existing codebase that already has source history: we start by mapping what is actually coded into `product-design-as-coded.md`, then we reconcile that reconstruction against the design intent you author in `product-design-as-intended.md`. Brownfield is the harder axis because spec-drift detection, STATUS marker promotion, and D-NNN Decision drafting only become load-bearing once there is existing code to reconcile. In greenfield those machinery are dormant until the first implementation lands.

<a id="collocated-workspace"></a>
### Collocated and workspace

The second half of the profile axis is about where SEJA's files live. **collocated** is the deployment pattern where framework files (`.claude/`, `_references/`, `_output/`) live directly inside the product codebase repository: the simplest layout, ideal when one person is doing both design and implementation and there is no reason to version the two streams separately. **workspace** is the deployment pattern where framework files live in a standalone git repository alongside, not inside, the product codebase: design history gets its own git log, multiple people can iterate on specs without touching product code, and the launcher scripts we generate point our session at the product codebase through `claude --add-dir`. We choose workspace when design and code have different review cadences, different contributors, or different release rhythms.

The pattern axis is about the team shape: solo designer working alone, engineering team where several contributors share the framework, or a mixed setup where a designer and a small engineering team collaborate on the same project. The pattern does not change which files we copy, but it does change how we frame `/design`, `/onboarding`, and `/communication` output for you.

The resulting matrix gives us one cell per engagement. Each cell names the `/seed` variant we run and one sentence on what changes in the files we write for that cell:

| Profile / pattern | Solo designer | Engineering team | Mixed |
|---|---|---|---|
| Greenfield collocated | `/seed <target>` (greenfield path, embed in the new repo) -- we author a fresh `constitution.md` and a minimal `product-design-as-intended.md` keyed to one voice, see [greenfield-collocated.md](how-to/greenfield-collocated.md). | `/seed <target>` (greenfield path, embed in the new repo) -- we author the design files with stricter review-perspective defaults and richer `conventions.md` so multiple builders share the same rules, see [greenfield-collocated.md](how-to/greenfield-collocated.md). | `/seed <target>` (greenfield path, embed in the new repo) -- we split `conventions.md` so designers own the standards section while engineers own the path-scoped rules, see [greenfield-collocated.md](how-to/greenfield-collocated.md). |
| Greenfield workspace | `/seed <target> --workspace` (greenfield workspace path) -- we create a standalone workspace repo next to the new product repo and generate launcher scripts so you can run `/design` without touching code, see [greenfield-workspace.md](how-to/greenfield-workspace.md). | `/seed <target> --workspace` (greenfield workspace path) -- we separate the framework repo from the product repo so designers can iterate on specs without blocking engineering PRs, see [greenfield-workspace.md](how-to/greenfield-workspace.md). | `/seed <target> --workspace` (greenfield workspace path) -- we generate launcher scripts that point at the product codebase and set `conventions.md` to split ownership between designers and engineers, see [greenfield-workspace.md](how-to/greenfield-workspace.md). |
| Brownfield collocated | `/seed <target>` (brownfield embed path) -- we detect existing source code, offer to embed the framework in place, and queue `/explain spec-drift` as the first real task so we can reconcile intent against code, see [brownfield-collocated.md](how-to/brownfield-collocated.md). | `/seed <target>` (brownfield embed path) -- we embed the framework alongside existing code and tune `product-design-as-intended.md` to the conventions we reconstructed from the codebase, see [brownfield-collocated.md](how-to/brownfield-collocated.md). | `/seed <target>` (brownfield embed path) -- we embed in place and split spec-drift review between designers and engineers so both voices land in the Decisions log, see [brownfield-collocated.md](how-to/brownfield-collocated.md). |
| Brownfield workspace | `/seed <target> --workspace` (brownfield workspace path) -- we create a companion workspace for the existing codebase, offer to migrate any embedded framework files into it, and keep design history in its own git log, see [brownfield-workspace.md](how-to/brownfield-workspace.md). | `/seed <target> --workspace` (brownfield workspace path) -- we create a companion workspace so designers can run `/explain spec-drift` on the existing code without writing into the product repo, see [brownfield-workspace.md](how-to/brownfield-workspace.md). | `/seed <target> --workspace` (brownfield workspace path) -- we create a companion workspace with launcher scripts and pre-seed `conventions.md` for shared design-plus-engineering ownership, see [brownfield-workspace.md](how-to/brownfield-workspace.md). |

Picking a cell in this matrix is how we interpret "which SEJA are you running" for the rest of our work together.

## Role families

The same skill surface has to address very different readers. We use role families and expertise levels to tune the tone and depth of what we write for a specific teammate without forking the skills themselves. The pair (role family, expertise level) is the unit `/onboarding` plans are cut against, and the role family alone is also how `/communication` picks which audience framing to apply.

<a id="bld-shp-grd"></a>
### BLD, SHP, GRD

A **role family** in SEJA is one of three coarse groupings that cover everyone a project involves. **BLD (Builders)** is the role family for developers, DevOps engineers, and infrastructure engineers who write, deploy, and maintain code: they read architecture diagrams, coding standards, CI pipelines, and data-model references, and they learn best when we hand them annotated code and convention files. **SHP (Shapers)** is the role family for product managers, UX and UI designers, researchers, and analysts who define what gets built and how: they read `product-design-as-intended.md`, journey maps, metacommunication, and the design system, and they learn best when we narrate a persona's path through a feature without dragging them into source code. **GRD (Guardians)** is the role family for QA engineers, security engineers, tech leads, and engineering managers who ensure quality, alignment, and governance: they read the review-perspective framework, test strategy, security policies, and quality-gate configuration, and they learn best when we hand them the `/check review` surface and the perspective catalog as their working toolkit. When you run `/onboarding bld L2 Alice` or `/communication clt`, the first token is what we branch on to pick the right reference files.

<a id="expertise-levels"></a>
### Expertise levels L1 through L5

Inside each role family we stratify by expertise so we can scale scaffolding against experience. **L1 Newcomer** is the expertise level for team members learning fundamentals and needing explicit step-by-step guidance: we produce guided walkthroughs, pair-work schedules, and reviewable first tasks. **L2 Practitioner** is mid-level expertise; we produce architecture overviews, convention reference sheets, and independent feature work with moderate safety nets. **L3 Expert** is senior expertise; we produce decision history, trade-off analyses, and mentoring tasks because L3 readers want the "why" behind every pattern. **L4 Strategist** is staff or principal expertise; we produce cross-team dependency maps, technical-debt inventories with business impact, and failed-initiative postmortems so a strategist can pick their first cross-cutting initiative. **L5 Leader** is tech lead or engineering manager expertise; we produce team-health dashboards, process audits, retrospective summaries, and governance questions so a leader can build trust before changing anything.

We combine the role family and the level into a single `(family, level)` tuple when you run `/onboarding`. That tuple tells us which reference files under `_references/general/onboarding/` to load and which learning path to cut for the teammate you are onboarding, so the plan we write fits their role and their starting experience at the same time.

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

Two-stage loading keeps the review focused. We shortlist the 3 to 6 perspectives that match your work's prefix and scope; we load the rest only if we find something that warrants deeper attention. If you want the long form of any perspective, the foundational framework ships per-perspective reference files under its `_references/general/review-perspectives/` directory with the full questionnaire, red flags, and example findings we draw on during a review. That directory is internal to the framework repo rather than part of this public site, so open it locally when you want to study a single lens in depth.

## Skills overview

A **skill** is a `SKILL.md` file under `.claude/skills/<name>/` that defines an agent-invocable capability and is invoked via a slash command. We expose 15 user-facing skills plus 2 internal lifecycle hooks we run on your behalf. For a standalone catalog of every skill with its one-line intent, see [docs/reference/skills.md](reference/skills.md). The 15 user-facing skills group into five purposes:

**Design and planning**

- `/design` configures SEJA for your project: on first run it walks you through a questionnaire (or parses a spec file) to define your stack, domain model, and conventions, then generates the project-specific reference files; on later runs it lets you update any section of your project design.
- `/plan` creates a step-by-step plan for your next feature, bug fix, or improvement that you can review before anything changes; with `--roadmap` it generates a full product roadmap with dependency-aware execution waves drawn from your design specs.
- `/implement` runs a previously approved plan step by step, and nothing changes in your project until you have reviewed and approved the plan first.

**Quality and maintenance**

- `/check` is the unified quality gate that runs validation scripts, code reviews, smoke tests, preflight checks, framework health diagnostics, or user test plan generation: one skill for all "is it OK?" questions.
- `/explain` gives you a clear explanation of how something works (a feature's behavior, the data model, the overall architecture, or the drift between your design specs) with diagrams and analogies, and its spec-drift mode also offers an interactive sync workflow to realign diverged specs.
- `/upgrade` upgrades your project's SEJA framework files to the latest version from the seed repo, preserves all project-specific files, and shows you a summary of changes before applying them.
- `/document` generates or updates documentation for your project, reading plan `Docs:` fields, detecting changes from git history, or targeting a specific documentation type, and uses project templates plus the documentation-quality writing guide for structured generation.

**Knowledge and communication**

- `/advise` answers any question about the project (architecture, design decisions, trade-offs) by researching your codebase, analyzing from multiple perspectives, and giving you actionable recommendations; with `--inventory` it catalogs all codebase elements matching a pattern.
- `/communication` generates tailored communication material for a specific audience (evaluators, clients, end users, or academics), each in their language and focused on what matters to them.
- `/onboarding` creates a personalized onboarding plan based on role and experience level, covering what to learn, in what order, and where to find things, so you can onboard a new teammate or yourself.
- `/reflect` surfaces descriptive patterns across weeks of telemetry, such as skill sequences, durations, revisions, and stuck loops, so you can see how your practice has actually been running; it is strictly non-prescriptive, and `/advise` is the follow-up skill when you want recommendations on what to change.

**State management**

- `/pending` shows outstanding human actions we are tracking for you (items to verify, markers to flip, proposals to apply, periodic curations) and walks you through addressing them one at a time; the ledger at `_output/pending.jsonl` is append-only so you can snooze, dismiss, or defer items without losing history.
- `/qa-log` saves the current conversation (questions and answers) to a file for future reference, which is useful for documenting decisions and rationale.

**Bootstrap**

- `/seed` copies the SEJA framework files into a target directory: for greenfield projects it creates the directory and initializes git, for existing codebases it embeds the framework alongside existing code, and with `--workspace` it creates a separate workspace directory instead.
- `/help` shows you what skills are available and explains what each one does, so you can browse by category to discover skills or get details on a specific one.

Two more skills, `pre-skill` and `post-skill`, run on our behalf around every user-facing skill invocation. You never call them directly, but they are what wraps each slash command with the reflection-in-action and reflection-on-action pipelines that make the framework's behavior consistent and auditable. We cover both in the framework lifecycle chapter below.

## Decision matrix

Three of the skills in the skills overview look deceptively similar at first glance: `/advise`, `/explain`, and `/communication` all accept a question or a request for text output, and all three produce markdown reports. The resemblance is surface-deep. Each answers a different intent: `/advise` helps you decide, `/explain` helps you understand, and `/communication` helps you tell someone else. When you give us an ambiguous prompt, the table below is the decision rule we run in our head before we pick a skill.

### /advise vs /explain vs /communication

| You want to... | Reach for | Because |
|---|---|---|
| Ask an open design question with multiple viable answers | `/advise` | We research your codebase, evaluate the question against multiple review perspectives, and hand back an actionable recommendation with pros and cons; the Q&A pair is logged in the advisory report for later recall. |
| Catalog codebase elements matching a pattern (all endpoints, all models, all form components) | `/advise --inventory` | We scan the source and produce a structured inventory of every matching element, its location, and where it is used. |
| Run a high-stakes decision through a structured expert debate | `/advise --deep` | We assemble a 5 to 7 member expert council, run a two-round debate, and give you back position statements, cross-examination, and synthesis. |
| Understand how an existing feature behaves in the running product | `/explain behavior` | We read the code, trace a persona's interactions with the feature, and produce an analysis report with diagrams and analogies for the current behavior. |
| Understand the data model, overall architecture, or how code works at a specific location | `/explain data-model`, `/explain architecture`, `/explain code` | We emit a repeatable architectural explainer scoped to the target, aimed at a teammate being onboarded on that slice of the product. |
| Trace how a feature got to its current shape over time | `/explain behavior-evolution` | We mine the plan history, build a chronological timeline of waves, and produce before-and-after narratives for each significant change. |
| Understand architectural rationale and where intent has drifted from code | `/explain spec-drift` | We compare `product-design-as-intended.md` with `product-design-as-coded.md` section by section and surface added, removed, and modified items as a drift report. |
| Generate stakeholder-facing material for a specific audience segment | `/communication <audience>` | We produce tailored content for EVL, CLT, USR, or ACD audiences, each in the language and framing that audience cares about, emitted as date-versioned files. |
| Produce material for every audience segment in one batch | `/communication --all` | We launch one generator agent per audience in parallel and write the results into a shared date folder with an index linking them. |

Output locations follow the project conventions variables. `/advise` writes advisory reports to `${ADVISORY_DIR}` with the logged Q&A pair and a recommendations summary, and `/advise --inventory` writes catalog reports to `${INVENTORIES_DIR}`. `/explain` writes analysis reports to the explained-* directories (`${EXPLAINED_BEHAVIORS_DIR}`, `${BEHAVIOR_EVOLUTION_DIR}`, `${EXPLAINED_CODE_DIR}`, `${EXPLAINED_DATA_MODEL_DIR}`, `${EXPLAINED_ARCHITECTURE_DIR}`), with the spec-drift mode writing into `${ADVISORY_DIR}` because its output is advisory-shaped. `/communication` writes date-versioned audience-specific files into `${COMMUNICATION_DIR}/<YYYY-MM-DD>/`, with a per-date `index.md` when more than one audience is generated on the same day.

Now that you know which skill to reach for, let us show you the envelope every one of these skills runs inside. The framework lifecycle chapter walks through the reflection-in-action and reflection-on-action pipelines we wrap around every slash command.

## Framework lifecycle

Everything in the previous chapters -- the signs, the profile x pattern picker, the role families and expertise levels, the review perspectives, the skill portfolio, and the decision matrix -- is wrapped in a lifecycle envelope we run on your behalf. Every slash command you invoke flows through a `pre-skill -> skill body -> post-skill` envelope, so the way a skill loads references, logs what it is doing, evaluates context budget, injects your constitution, updates the as-coded files, and proposes a commit is the same across the catalog. When something in this envelope misbehaves -- an orphaned brief, a pending ledger you cannot reconcile, a stuck loop -- see [docs/troubleshooting.md](troubleshooting.md) for common failure modes and their fixes.

This chapter is the canonical home for that envelope. The first three H3s below cover the envelope itself: the overall skill lifecycle, then the pre-skill 8-stage pipeline, then the post-skill 13-step pipeline. The next three cover the state the envelope reads from and writes to: the pending ledger, the constitution, and the section boundaries that keep multi-section files safe to edit. The final two cover the reconciliation surface: the two specs files (`product-design-as-intended.md` and `product-design-as-coded.md`) and the D-NNN Decision entries that record the rationale whenever intent and code need to be brought back into alignment. Later how-to guides link back to these anchors instead of redefining the mechanics inline, so if you are reading a how-to and you hit an unfamiliar reference to a pipeline stage, a marker type, or a Decision ID, the link almost always points here.

### Skill lifecycle

Every slash command is wrapped by two internal hooks, and the three-step sequence below is the shape every turn takes:

1. **Pre-skill** runs first. It loads context, logs the brief, evaluates the context budget, loads references, and injects your constitution. Think of it as the reflection-in-action stage: we check our working conditions before we start producing anything.
2. **Skill body** runs next. This is where the slash command you typed actually does its work and produces an artifact under `_output/` (a plan, an advisory report, an explanation, a communication package, an onboarding plan, and so on).
3. **Post-skill** runs last. It updates the brief from STARTED to DONE, refreshes indices, logs a QA transcript, reconciles the as-coded specs, proposes STATUS marker flips for confirmation, and offers a git commit. Think of it as the reflection-on-action stage: we review and record what just happened so the next turn starts from a clean, auditable state.

The envelope is why two successive `/plan` invocations leave the same audit trail regardless of which skill body ran between them. Whatever skill runs in the middle inherits the same entry and exit conditions, so the surrounding narrative stays uniform across the catalog.

It is also why we can resume a turn in a fresh session without losing the thread: the brief, the QA log, and the commit message together reconstruct what we were doing and why, which is the reflection-in-action and reflection-on-action loop closing on itself.

The specific stages and steps of each hook are covered in the next two sections.

<a id="pre-skill-pipeline"></a>
### Pre-skill 8-stage pipeline

The **pre-skill pipeline** is the eight-stage pipeline run before every skill: help, brief-log, orphan-check, budget-eval, compaction-check, pending-check, ref-load, constitution. Three of those stages are **critical** and always run; the other five are **non-critical** and error-isolated, which means a failure in any one of them is logged but does not block the skill body. The stages in order:

1. `help` -- intercepts `--help` and prints the Quick Guide for the calling skill, then exits before the skill body runs.
2. `brief-log` -- records the STARTED entry in the briefs file so you can see what we are doing even if the session crashes mid-turn.
3. `orphan-check` -- detects STARTED entries without a matching DONE from a previous crashed turn and offers to clean them up.
4. `budget-eval` -- picks the light, standard, or heavy context budget tier and loads the recent briefs window sized to that tier.
5. `compaction-check` -- warns when the session has accumulated many skill invocations and may be about to summarize older context.
6. `pending-check` -- surfaces the count of outstanding items from the pending ledger and runs lazy periodic triggers when they come due.
7. `ref-load` -- loads conventions, permissions, constraints, and the skill-specific references the calling skill declares in its SKILL.md metadata.
8. `constitution` -- injects your project constitution into the skill's prompt so trust boundaries are enforced before any generation happens.

`brief-log`, `budget-eval`, and `ref-load` are the three critical stages. A skill may opt out of any non-critical stage by listing the stage ID in `metadata.skip_stages` in its SKILL.md frontmatter; critical stages cannot be skipped.

<a id="post-skill-pipeline"></a>
### Post-skill 13-step pipeline

The **post-skill pipeline** is the lifecycle hook run after every skill for briefs update, QA logging, as-coded updates, marker proposals, and git commit. Its 13 steps group into four bands:

- **Bookkeeping**: update the brief entry from STARTED to DONE, record a telemetry event for cost and latency accounting, and log a QA transcript via `/qa-log` so the turn's questions and answers are captured for later recall.
- **As-coded reconciliation**: when a plan ran, reconcile `project/product-design-as-coded.md` section by section against what actually changed on disk, run the documentation freshness check so stale docs get flagged, and regenerate the `INDEX.md` files under `_output/` so navigation stays in sync with the artifacts the turn produced.
- **Safety and marker proposals**: run the fast preflight gate and the human-markers verifier before staging so a bad write never reaches the commit, write any deferred actions into `_output/pending.jsonl`, and propose STATUS marker flips to you through `AskUserQuestion` so any write into a Human (markers) file is confirmed in the same turn.
- **Commit and handoff**: stage and commit the affected files with a message keyed to the skill and invocation ID for auditability, then surface contextual next-step suggestions through `AskUserQuestion` once the commit lands so the next turn starts from a known good state.

The key artifacts touched every turn are the briefs file (`_output/briefs/*.md`), the `_output/qa-logs/` directory, the `INDEX.md` files under `_output/`, the pending ledger at `_output/pending.jsonl`, proposed STATUS markers in `project/product-design-as-intended.md`, the reconciled sections of `project/product-design-as-coded.md`, and the git commit itself. Every one of these is addressable after the fact, so you can reconstruct what happened on any turn by reading the brief, the QA log, and the commit diff side by side.

### Pending ledger

The **pending ledger** is the append-only JSONL log at `_output/pending.jsonl` tracking outstanding human actions surfaced by skills. It is where we park actions we cannot finish on our own, and it holds four kinds of entries: human confirmations we need before we may write a marker, stuck retries waiting for a rerun, spec-drift reconciliations that need your judgment, and periodic curation items (design-intent reviews, orphan-brief sweeps) that come due on a cadence. Post-skill appends entries; pre-skill's `pending-check` stage surfaces their count to you at the start of each turn; `/pending` is the skill that walks you through the ledger one entry at a time so you can resolve, snooze, or dismiss each one. The ledger is append-only on purpose, so snoozing or dismissing an entry leaves a trace you can audit later. JSONL as the storage format is deliberate: every entry is a self-contained JSON object on one line, which makes the ledger trivial to grep, sort, diff, and replay without dragging in a schema migration whenever we want to add a new entry type.

### Constitution

The **constitution** is the immutable project principles in `project/constitution.md`, never agent-altered, required for new projects. It is copied in by `/seed` from `_references/template/constitution.md`, instantiated by `/design`, and classified Human -- we load it on every turn but we never edit a word of it. We inject its contents into the prompts of generator agents (like `communication-generator`, `onboarding-generator`, and `document-generator`) so their output stays inside the principles you committed to. `/check health` validates that the constitution is present as one of its checks, and a new project without a constitution is blocked from proceeding past `/design`. The constitution is the one file whose wording is load-bearing for trust boundary enforcement across the catalog.

### Section boundaries

A **section boundary** is an enforcement rule preventing agents from writing outside designated H2 sections of a multi-section file, validated by `check_section_boundary_writes.py`. `project/product-design-as-coded.md` is the canonical example: one file divided into three H2 sections (`## Conceptual Design`, `## Metacommunication`, and `## Journey Maps`), each with different write boundaries and different post-skill logic pointing at it. Section boundaries are the technical mechanism that lets us share write access inside a single file without stepping on each other: we update one section while your prose or your markers stay untouched in the others, and the guardrail catches any accidental spill before it reaches disk. The same idea scales to any multi-section Agent-classified file in your project: declare the H2s, register them as boundaries, and let the guardrail hold the line so one skill's edits cannot corrupt a neighboring section by mistake.

<a id="product-design-as-intended-vs-as-coded"></a>
### product-design-as-intended vs product-design-as-coded

SEJA tracks two design specs, and keeping them legible as distinct artifacts is what makes spec-drift reconciliation possible. The as-intended / as-coded distinction is the heart of the reconciliation model: one file holds intent, the other holds the implementation state, and the skill in between is what tells you where the two disagree.

- **product-design-as-intended**: Unified working-intent file (`project/product-design-as-intended.md`) holding design intent, ADR-shaped Decisions, and CHANGELOG, classified Human (markers). You own the prose and we may only stamp STATUS, ESTABLISHED, and CHANGELOG_APPEND markers into it through `apply_marker.py` after you confirm the edit in the same turn. This file holds your working intent in sections 0 through 17.
- **product-design-as-coded**: Unified implementation-state file (`project/product-design-as-coded.md`) auto-maintained by the agent, with three H2 sections: Conceptual Design, Metacommunication, Journey Maps. We maintain this file via post-skill writes and its three sections mirror the implementation state of the corresponding sections of the intended file.
- `/explain spec-drift` is the skill we run to surface the delta between the two files, section by section, so you can see what got added, removed, or modified relative to intent.

<a id="decision-entries"></a>
### D-NNN Decision entries

When the drift between intent and code warrants a recorded rationale, we draft a D-NNN Decision entry. These are ADR-shaped records (short for Architecture Decision Record) living in the Decisions section of `project/product-design-as-intended.md`, each carrying a stable `D-NNN` ID in a namespace orthogonal to the REQ-TYPE-NNN traceability markers that cover individual requirements. Every Decision entry has four parts:

- **Context** -- one short paragraph on the situation that forced the decision (what code was doing, what intent said, and why the gap mattered enough to record).
- **Decision** -- the option chosen, stated in one sentence so a future reader can grep the Decisions log for "we chose X" without reading every entry in full.
- **Consequences** -- the follow-on effects on intent, code, tests, or other Decisions that the choice locks in, including any requirements promoted or retired as a result.
- **Supersedes** (optional) -- a pointer to any earlier D-NNN this entry replaces, so the chain of rationale stays legible when a past decision is revisited.

Decision entries are promoted through `/explain spec-drift --promote`, which runs in two passes: the proposal pass drafts Decision entry proposals and writes them to the pending ledger for your review, and the marker pass accepts your confirmed proposals and flips the corresponding STATUS markers by running `apply_marker.py` via the `--apply-markers plan-<id>` entry point. The split is what lets you approve the rationale and the marker flips independently, so the audit trail records both your decision and the resulting state change. The orthogonality between D-NNN Decision IDs and REQ-TYPE-NNN requirement IDs is deliberate: a Decision may touch many requirements, and a requirement may be shaped by more than one Decision over its lifetime, so the two namespaces are kept separate to avoid forcing a false one-to-one mapping.

That covers the envelope. Run `/help` for the skill catalog, read [quickstart.md](quickstart.md) if you have not yet, and open the how-to guide whose filename matches your profile-plus-pattern cell for the step-by-step path that fits your engagement.

Each how-to links back to the anchors in this file whenever it needs to refer to a sign, a role, a review perspective, a skill, or a lifecycle concept, so you can always return here for the underlying model. If you find yourself reading a how-to and wondering "why does SEJA do it this way", the answer is almost always in one of the chapters above: the sign system explains who may write where, the profile x pattern picker explains which starting shape you are in, the role families explain who a document is being written for, the review perspectives explain how we judge quality, the skills overview explains the catalog, the decision matrix explains how we disambiguate between overlapping skills, and this chapter explains the envelope every skill runs inside. Keep this file open in a second tab while you work and you will have everything you need to read what we are doing for you and why.
