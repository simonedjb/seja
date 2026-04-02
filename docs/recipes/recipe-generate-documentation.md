# Recipe: Generate Project Documentation

Use this recipe after implementing a feature to generate or update project documentation.

## Goal

Generate or update user-facing and developer documentation after implementing a feature or making significant changes.

## Prerequisites

- SEJA framework seeded and project configured via `/seed` + `/design`
- A recently completed plan (with `Docs:` field) or recent code changes. This field is set automatically when you create a plan with `/plan` -- each step declares what documentation it affects.

## Steps

1. **After implementing a plan**
   If the plan includes a `Docs:` field, run `/document` to generate the documentation types specified in the plan:
   ```
   /document
   ```
   The skill reads the most recent plan's `Docs:` field and generates the appropriate documentation.

2. **Auto-detect what needs documenting**
   If there is no recent plan, or you want to check what documentation might need updating:
   ```
   /document
   ```
   The skill scans recent changes and proposes which documentation types to generate or update.

3. **Generate a specific documentation type**
   To generate a specific type directly:
   ```
   /document --type readme        # Project README
   /document --type api-reference  # API reference docs
   /document --type changelog      # Changelog entry
   /document --type contextual-help # In-app help content
   /document --type adr            # Architecture decision record
   /document --type help-center    # Help center article
   ```

4. **Review the generated documentation**
   Documentation is written to project source locations (not `_output/`). Review the generated files for accuracy and completeness before committing.

## Tips

- The post-skill lifecycle hook suggests running `/document` when a plan includes documentation tasks -- follow the suggestion.
- For architecture decisions explored via `/advise`, use `/document --type adr` to formalize the decision as an ADR.
- Documentation templates include freshness metadata and Diataxis classification, so generated docs follow a consistent quality standard.

## Related recipes

- [Plan and Execute a Change](recipe-plan-and-execute.md) -- the typical workflow before documentation
- [Run Quality Gates](recipe-quality-gates.md) -- validation checks that include documentation consistency
