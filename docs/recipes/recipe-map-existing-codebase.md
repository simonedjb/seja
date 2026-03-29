# Recipe: Map an Existing Codebase

## Goal

Understand an existing codebase before making changes to it.

## Prerequisites

- The foundational SEJA framework installed in the codebase (or a project
  workspace -- see the [workspace setup recipe](recipe-workspace-setup.md))
- Access to the codebase you want to map

## Steps

1. **Get a visual architecture overview**
   ```
   /explain architecture   # Claude
   $explain architecture   # Codex
   ```
   This produces a high-level diagram of the system structure, layers, and
   key dependencies.

2. **Understand entities and relationships**
   ```
   /explain data-model   # Claude
   $explain data-model   # Codex
   ```
   Generates an entity-relationship view of your domain objects.

3. **Dive into specific features**
   ```
   /explain behavior <feature>   # Claude
   $explain behavior <feature>   # Codex
   ```
   Replace `<feature>` with the name of a flow you need to understand (e.g.,
   "user-registration", "payment-checkout").

4. **Catalog codebase elements**
   ```
   /advise --inventory List all API endpoints   # Claude
   $advise --inventory List all API endpoints   # Codex
   ```
   Also try: "List all components", "List all database models", "List all
   background jobs". Each produces a structured inventory.

5. **Review the generated reports**
   - Architecture and behavior reports land in `_output/explained-*/`.
   - Inventories land in `_output/inventories/`.

6. **Feed findings into the conceptual design**
   Use the reports to fill in the as-is conceptual design when running
   `/quickstart` / `$quickstart`. This closes the loop between discovery and project setup.

## Tips

- Start broad (architecture), then narrow (specific features).
- The `--inventory` mode is especially useful for large codebases with many
  endpoints or components.
- Keep the explanation reports -- they serve as living documentation that you
  can regenerate as the codebase evolves.

## Related journeys

- [Solo Designer Brownfield](../journeys/journey-solo-designer-brownfield.md)
- [Growing Team](../journeys/journey-growing-team.md)
- [Enterprise Evolution](../journeys/journey-enterprise-evolution.md)
- [Teaching/Research](../journeys/journey-teaching-research.md)
