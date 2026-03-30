# Recipe: Upgrade the Foundational Framework

## Goal

Upgrade the foundational SEJA framework files in a codebase or project workspace
to a newer version without losing project-specific data.

## Prerequisites

- The foundational SEJA framework already installed in the codebase or workspace
- Clean git state (or a backup)

## Steps

1. **Ensure clean state**
   ```bash
   git status
   ```
   Commit or stash any uncommitted changes before proceeding.

2. **Run the upgrade**
   ```
   /quickstart --upgrade   # Claude
   $quickstart --upgrade   # Codex
   ```
   The skill fetches the latest foundational framework from GitHub and runs
   the upgrade script automatically. No local copy of the framework repo is
   needed.

3. **Review the output**
   The upgrade reports:
   - Version change (e.g., "1.0.0 -> 2.0.0").
   - Whether an old-layout migration was performed.
   - New convention variables that are now available.

4. **Add new convention variables**
   If new variables were reported, add them to your `project/conventions.md`
   with appropriate values for your project.

5. **Accept path migrations if offered**
   If path references changed (for example, from the old `skills/references/` layout to the current `_references/` layout), accept the offered migration to update all references.

6. **Regenerate `CLAUDE.md` / `AGENTS.md` (optional)**
   If the framework structure changed significantly, regenerate the agent
   configuration to reflect the updated layout.

7. **Verify framework integrity**
   ```
   /check health   # Claude
   $check health   # Codex
   ```
   Confirms that all framework components are present and consistent.

## Tips

- The upgrade preserves all `project/*.md` files and `_output/`. Only foundational framework files (skills, scripts,
  general references, templates) are updated.
- Always check the CHANGELOG for breaking changes before upgrading.
- For the workspace pattern, run the upgrade in each project workspace
  separately.

## Related journeys

- [Agency Multi-Project](../journeys/journey-agency-multi-project.md)
  (all client project workspaces need upgrading)
- All other journeys reference this recipe for periodic maintenance.
