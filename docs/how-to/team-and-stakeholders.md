# Team and stakeholders how-to

This how-to is for you when you are bringing a new teammate into your project, or when you need to produce material about your project for a stakeholder outside your team. These are two related but distinct flows; pick the one that matches your situation. Both flows generate tailored output by running a generator agent against your project constitution, so the result respects the principles you committed to without us having to reread the reference manually.

## Before you start

- Your project has been seeded and configured via `/seed` + `/design` so the constitution and conceptual design files are in place.
- You know who the output is for -- a teammate joining the project, or a stakeholder outside it.
- The lifecycle definitions in [concepts.md -- Framework lifecycle](../concepts.md#framework-lifecycle) -- every `**Framework:**` callout below links back there for its definitions.

## Onboarding a new teammate with `/onboarding`

### Step 1: Pick a role family and an expertise level

We identify the new teammate's role family and expertise level before we invoke the skill. Role families are `BLD` (builder -- developer, DevOps engineer), `SHP` (shaper -- designer, product manager, analyst), and `GRD` (guardian -- QA engineer, security specialist, tech lead). Expertise levels run `L1` through `L5`, from newcomer to leader. The role family selects which project files the generator treats as primary reading; the level selects the pace and the depth of the suggested first tasks.

**Framework:** See [concepts.md -- Framework lifecycle](../concepts.md#framework-lifecycle) for the full definition of the pre/post-skill pipeline, pending ledger, marker model, and constitution. `/onboarding` generates a role-and-level-tailored onboarding plan via the `onboarding-generator` agent, which is invoked with the project constitution in its prompt so the plan stays inside the trust boundaries we committed to and so the generated first-week tasks respect our principles. See also [framework-reference.md#onboarding](../reference/framework-reference.md#onboarding).

### Step 2: Run `/onboarding <role> <level>`

We invoke the skill with the role family and level we picked, optionally with a name and a focus area: `/onboarding BLD L2 Alice --area backend`. For cross-functional roles we use a plus notation (`BLD+GRD`) so the generator produces a plan that covers both surfaces. For onboarding waves where several people join in the same week, we use `--batch` with a semicolon-separated list of role/level pairs.

**Framework:** the skill interactively resolves role-conditional project scanning (a `BLD` plan reads the codebase tree and conventions; a `SHP` plan reads the conceptual design and journey maps; a `GRD` plan reads the validator suite and review perspectives), writes a date-versioned plan to `_output/onboarding-plans/`, and cross-links into the profile-and-pattern how-tos so the new teammate can start reading with the how-to that matches their workflow instead of the generic README.

### Step 3: Hand off the generated plan

We share the generated plan with the new teammate and their assigned buddy or mentor. The plan references real project files and paths, so it stays actionable rather than generic -- a `BLD L2` plan names actual routes, schemas, and test files; a `SHP L3` plan names actual conceptual design anchors and journey map steps. This is a human-only step, and it is the one that turns a generated artifact into a real onboarding conversation.

## Producing stakeholder material with `/communication`

### Step 1: Pick an audience segment

We identify the audience segment for the material we need to produce. Segments are `EVL` (evaluator -- CTO, tech lead, architect), `CLT` (client -- VP, budget owner, executive), `USR` (end user -- product user, support team), and `ACD` (academic -- researcher, educator). The segment choice determines the tone, the level of technical detail, the mix of outcome versus architecture, and the default length of the generated artifact.

**Framework:** `/communication` generates material tailored to the chosen segment via the `communication-generator` agent, which is also invoked with the project constitution so the generated prose respects our voice, our metacommunication intent, and the principles we committed to. See also [framework-reference.md#communication](../reference/framework-reference.md#communication).

### Step 2: Run `/communication <audience>`

We invoke the skill with the segment code: `/communication EVL`. To generate material for every segment in one pass, we use `/communication --all`. For deeper technical sections (architecture details, research foundation, development roadmap), we add `--deep` -- this is the flag we reach for when the audience is an evaluator or an academic who needs comprehensive context.

**Framework:** the skill writes a tailored markdown artifact and a styled HTML version to `_output/communication/`, ready for internal review and external sharing. Each segment gets fundamentally different content -- evaluators see architecture and ROI, clients see outcomes and cost, end users see quality commitment, and academics see theoretical foundation -- so the four segments are not just four tones on the same content, they are four different selections of project facts.

### Step 3: Review and deliver

We read the generated material, edit any passages we want to refine (the generator's voice is a draft of ours, not a replacement for it), and send it to the stakeholder. This is a human-only step.

## What to read next

- [plan-and-execute.md](plan-and-execute.md) -- the first how-to a new teammate should read after their onboarding plan lands, so they know how to turn intent into executed work.
- [concepts.md -- Framework lifecycle](../concepts.md#framework-lifecycle) -- the canonical definitions the callouts above link back to.
