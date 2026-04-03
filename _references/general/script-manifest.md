# FRAMEWORK -- SCRIPT MANIFEST

> Catalog of all helper scripts in `.claude/skills/scripts/`. Updated manually or via `/advise --inventory`.
> Last updated: 2026-04-01

## Summary

| Type | Count |
|------|-------|
| check | 17 |
| generator | 8 |
| orchestrator | 4 |
| utility | 9 |
| **Total** | **38** |

## Scripts

| Script | Type | Dependencies | Generated |
|--------|------|-------------|-----------|
| `backfill_qa_dates.py` | utility | project_config | no |
| `check_api_auth_decorators.py` | check | project_config | no |
| `check_api_contract_sync.py` | check | project_config | no |
| `check_backend_test_coverage.py` | check | project_config | no |
| `check_conventions.py` | check | project_config | no |
| `check_docs.py` | check | project_config | no |
| `check_frontend_test_coverage.py` | check | project_config | no |
| `check_i18n_keys.py` | check | project_config | no |
| `check_migration_chain.py` | check | project_config | no |
| `check_po_parity.py` | check | project_config | no |
| `check_route_coverage.py` | check | project_config | no |
| `check_secrets.py` | check | -- | no |
| `check_skill_spec.py` | check | -- | no |
| `check_skill_system.py` | check | -- | no |
| `check_spec_conformance.py` | check | project_config | no |
| `check_telemetry.py` | check | project_config | no |
| `check_unused_files.py` | check | project_config | no |
| `check_validation_constants_sync.py` | check | project_config | no |
| `count_loc.py` | utility | project_config | no |
| `create_workspace.py` | utility | upgrade_framework | no |
| `generate_briefs_index.py` | generator | project_config | no |
| `generate_cheatsheet.py` | generator | -- | no |
| `generate_essential_perspectives_summary.py` | generator | -- | no |
| `generate_macro_index.py` | generator | project_config | no |
| `generate_skill_graph.py` | generator | -- | no |
| `generate_skill_map.py` | generator | project_config | no |
| `generate_skills_manifest.py` | generator | -- | no |
| `generate_telemetry_report.py` | generator | project_config | no |
| `md_to_html.py` | utility | project_config | no |
| `migrate_to_global_ids.py` | utility | project_config | no |
| `project_config.py` | utility | -- | no |
| `reserve_id.py` | utility | project_config | no |
| `run_all_checks.py` | orchestrator | project_config | no |
| `run_all_tests.py` | orchestrator | project_config | no |
| `run_migrations.py` | orchestrator | -- | no |
| `run_preflight_fast.py` | orchestrator | -- | no |
| `smoke_test_core.py` | utility | project_config | no |
| `upgrade_framework.py` | utility | project_config, run_migrations | no |
