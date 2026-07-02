**What it does**: Generate or update documentation for your project. Four invocation modes: plan-driven (reads Docs: fields from a plan), auto-detect (scans recent git changes), type-targeted (you pick the doc type), or bare scope (you name a file/module/feature). Uses project templates and the documentation-quality writing guide for structured generation. Supports 7 documentation types: readme, contextual-help, api-reference, ddr, help-center, changelog, and spo.

**Examples**:
> `/document --plan 000130`
> Reads the plan's Docs: fields and generates the appropriate documentation for each identified need.

> `/document --auto-detect`
> Analyzes recent git changes using 6 heuristic patterns (new API routes, changed models, new UI components, config changes, architectural shifts, breaking changes) and generates matching documentation types.

> `/document --auto-detect --since 2026-04-01`
> Same as above but bounds the git scan to changes since a specific date.

> `/document --auto-detect --since last`
> Scans only changes since the last `/document` run of any kind.

> `/document --auto-detect --full-history`
> Ignores per-doc-type bounding windows and scans the full recent git history.

> `/document --type readme`
> Generates or updates the project README.

> `/document --type api-reference`
> Generates API reference documentation from your routes and handlers.

> `/document --type changelog`
> Generates a changelog entry from recent changes.


> `/document --type spo`
> Generates `_output/docs/spo.html` — an interactive layered product overview from `product-overview.yaml`. Shows the full value chain (goals → tasks → features → services → data) with persona filters, quality criteria panel, and roadmap version columns.

> `/document --type spo --drift`
> Same as above, but dims non-`done` cards to highlight the gap between as-intended and as-coded state.


> `/document --type ddr`
> Creates a Design Decision Record for a recent decision.

> `/document --type contextual-help`
> Generates contextual help content for UI features.

> `/document --type help-center`
> Generates help-center articles for end users.

> `/document src/auth`
> Documents the auth module -- infers the most appropriate doc type from the scope content.

**When to use**: After implementing a feature or fix that affects user-facing behavior, API contracts, or architectural decisions. Automatically suggested by post-skill for FEATURE and REDESIGN plans and plans with non-N/A Docs: fields. Use `--plan` when documentation needs are already specified in a plan; use `--auto-detect` for a broad scan of what changed; use `--type` when you know exactly which doc type you need; use bare scope for ad-hoc documentation of a specific area. Use `--type spo` after design is established, before a stakeholder presentation, or when the product structure changes significantly (new layers, major feature additions).

**Not for**: stakeholder updates (use `/communicate`) or personalized onboarding plans (use `/onboard`). See `docs/how-to/which-communicative-skill.md` for the audience routing table.

**Next step**: `/critique docs` to validate documentation consistency.

**See also**: `/explain` -- understand existing system behavior, architecture, data model, or design spec drift.
