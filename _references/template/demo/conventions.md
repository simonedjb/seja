# PROJECT CONVENTIONS -- TaskFlow Demo

> Pre-filled conventions for the TaskFlow demo project (TypeScript + React).

---

## Project Identity

| Variable | Value | Description |
|----------|-------|-------------|
| `PROJECT_NAME` | TaskFlow | Project display name |

---

## Directory Structure

| Variable | Value | Description |
|----------|-------|-------------|
| `SKILLS_DIR` | `.claude/skills` | Root directory for skill definitions |
| `AGENT_SPECS_DIR` | `project/agent` | Agent-facing structured specifications (in `_references/`) |
| `OUTPUT_DIR` | `_output` | Root directory for all generated artifacts |
| `PLANS_DIR` | `${OUTPUT_DIR}/plans` | Plan output folder |
| `SCRIPTS_DIR` | `${OUTPUT_DIR}/generated-scripts` | Script output folder |
| `ADVISORY_DIR` | `${OUTPUT_DIR}/advisory-logs` | Advisory log output folder |
| `PROPOSALS_DIR` | `${OUTPUT_DIR}/proposals` | Lightweight change proposals |
| `CHECK_LOGS_DIR` | `${OUTPUT_DIR}/check-logs` | Check/preflight/review output folder |
| `TMP_DIR` | `${OUTPUT_DIR}/tmp` | Temporary/helper scripts |

---

## Key Files

| Variable | Value | Description |
|----------|-------|-------------|
| `BRIEFS_FILE` | `${OUTPUT_DIR}/briefs.md` | Execution log of all skill invocations |
| `ARTIFACT_INDEX_FILE` | `${OUTPUT_DIR}/INDEX.md` | Single global artifact index |
| `CONSTITUTION_FILE` | `project/constitution.md` | Project constitution (in `_references/`) |
| `DESIGN_INTENT_TO_BE` | `project/design-intent-to-be.md` | Target design intent -- conceptual design + metacommunication (in `_references/`) |
| `DESIGN_INTENT_ESTABLISHED` | `project/design-intent-established.md` | Processed design intent with preserved rationale (human-maintained, never agent-altered) (in `_references/`) |

---

## Review Configuration

| Variable | Value | Description |
|----------|-------|-------------|
| `MINIMUM_REVIEW_DEPTH` | `light` | Minimum review depth floor |

---

## Source Directories

| Variable | Value | Description |
|----------|-------|-------------|
| `FRONTEND_DIR` | `src` | Frontend source root |
| `FRONTEND_FRAMEWORK` | `react` | Frontend framework identifier |

---

## Frontend Structure

| Variable | Value | Description |
|----------|-------|-------------|
| `FRONTEND_SRC_DIR` | `${FRONTEND_DIR}` | Frontend source root |
| `FRONTEND_API_DIR` | `${FRONTEND_SRC_DIR}/api` | API client/type definitions |
| `FRONTEND_UTILS_DIR` | `${FRONTEND_SRC_DIR}/utils` | Frontend utilities directory |
| `FRONTEND_CONSTANTS_FILE` | `constants.ts` | Frontend validation constants filename |
