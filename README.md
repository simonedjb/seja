# SEJA -- Semiotic Engineering Journeys with Agents

SEJA is a human-centered methodology and file-based framework for designing
and building software with AI coding agents. It gives an agent-driven project
a shared memory of intent, conventions, and implementation state, so that
people and agents can reflect on what the system is communicating, decide
together what to change, and keep that decision trail durable. It is for
designers, developers, and small teams who want agent assistance without
losing craft, context, or accountability.

*We (SEJA creators and Claude Code) built this framework to make the communication between people and agents explicit, reviewable, and accountable.*

The framework grew out of work by Clarisse Sieckenius de Souza, Gabriel DJ
Barbosa, and Simone DJ Barbosa on redesigning an academic discussion forum
with agentic tooling. It is grounded in semiotic engineering and in Schon's
concepts of reflection-in-action, reflection-on-action, and reflection-on-
practice.

What you get once SEJA is installed in a project:

- A small set of human-authored design artifacts that capture intent,
  conventions, and the current state of the system.
- Agent-authored artifacts that track implementation state and decisions,
  kept in sync with source through lifecycle markers and quality gates.
- A planning and review loop that turns vague requests into reviewable
  plans, executes them against project conventions, and records the result.

## Pick your path

Two questions decide how you adopt SEJA: are you starting a new product or
working inside an existing one, and do you want the framework files to live
next to the source code or in a separate workspace repo? The matrix below
maps each combination to the right how-to guide.

|                | Collocated                                                                                 | Workspace                                                                                              |
|----------------|--------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| **Greenfield** | New product, framework lives next to source. [Guide](docs/how-to/greenfield-collocated.md) | New product, framework lives in a separate workspace repo. [Guide](docs/how-to/greenfield-workspace.md) |
| **Brownfield** | Existing codebase, framework added in place. [Guide](docs/how-to/brownfield-collocated.md) | Existing codebase, framework kept in a side workspace. [Guide](docs/how-to/brownfield-workspace.md)    |

If you are unsure, skim the quickstart first, then re-read this table. The
collocated pattern is the simplest starting point for solo and small-team
work; the workspace pattern keeps design history in its own repo and is a
better fit for teams who want to add SEJA alongside an existing product
without touching its source tree.

## Read the docs

Three entry points cover everything most readers need. Start at the top and
move down as your questions get more detailed.

- [docs/quickstart.md](docs/quickstart.md) -- 20-minute worked example, read this first. Walks through a tiny project end to end so you can see the framework in motion before committing to a pattern.
- [docs/concepts.md](docs/concepts.md) -- sign system, profile x pattern matrix, and the Framework lifecycle chapter. Read this once the quickstart makes sense and you want to know why each artifact exists.
- [docs/foundations.md](docs/foundations.md) -- theoretical primer on semiotic engineering and reflective practice, the two research traditions SEJA draws on.
- [docs/foundations-assessment.md](docs/foundations-assessment.md) -- correspondence assessment mapping semiotic engineering constructs onto SEJA artifacts and workflows.
- [docs/how-to/](docs/how-to/) -- full how-to set covering the four profile x pattern entry points plus cross-cutting tasks like planning, quality gates, team handoffs, and framework upgrades.
- [docs/troubleshooting.md](docs/troubleshooting.md) -- symptom lookup table for diagnosing common issues when running the framework.

### Advanced / complete framework file list

- [docs/reference/framework-reference.md](docs/reference/framework-reference.md) -- complete inventory of every skill, agent, rule, script, and reference file in the framework. This file is auto-generated from the framework source and is intended as a lookup table, not a tutorial.
- [docs/reference/glossary.md](docs/reference/glossary.md) -- canonical SEJA terminology lookup.
- [docs/reference/perspectives.md](docs/reference/perspectives.md) -- 16 review perspectives catalog.
- [docs/reference/skills.md](docs/reference/skills.md) -- skills catalog organized by category.

## License

Licensed under [CC-BY-NC-4.0](https://creativecommons.org/licenses/by-nc/4.0/) (Creative Commons Attribution-NonCommercial 4.0 International).

You may use, copy, adapt, and share this work for **noncommercial purposes only**, provided that you give appropriate credit and indicate any changes made.

**Commercial use is not permitted under this license.** For commercial licensing inquiries, contact <simonedjb@gmail.com>.

Full terms are in [LICENSE](./LICENSE).

## Attribution

If you reuse or adapt this framework, please credit the original as:

> Based on the SEJA Design and Development Framework by Simone Diniz Junqueira Barbosa

and link back to this repository.

## Trademark notice

The project name, logo, and brand elements are not licensed for general use except as required for factual attribution. See [TRADEMARKS.md](./TRADEMARKS.md).
