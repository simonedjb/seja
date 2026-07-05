---
designer_description: "I'm the demo conventions file /seja-setup --demo writes into your scratch project -- project identity, directory layout, key-file paths, review floor, and frontend structure already filled in for a TypeScript plus React task app, so you can see exactly what /design produces from a real questionnaire pass instead of starting from empty placeholders."
---

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
| `AGENT_SPECS_DIR` | `product-design/agent` | Agent-facing structured specifications |
| `OUTPUT_DIR` | `_output` | Root directory for all generated artifacts |
| `PLANS_DIR` | `${OUTPUT_DIR}/plans` | Plan output folder |
| `SCRIPTS_DIR` | `${OUTPUT_DIR}/generated-scripts` | Script output folder |
| `ADVISORY_DIR` | `${OUTPUT_DIR}/advisory-logs` | Advisory log output folder |
| `PROPOSALS_DIR` | `${OUTPUT_DIR}/proposals` | Lightweight change proposals |
| `CRITIQUE_LOGS_DIR` | `${OUTPUT_DIR}/critique-logs` | Critique/preflight/review output folder |
| `TMP_DIR` | `${OUTPUT_DIR}/tmp` | Temporary/helper scripts |

---

## Key Files

| Variable | Value | Description |
|----------|-------|-------------|
| `BRIEFS_FILE` | `${OUTPUT_DIR}/briefs.md` | Execution log of all skill invocations |
| `ARTIFACT_INDEX_FILE` | `${OUTPUT_DIR}/INDEX.md` | Single global artifact index |
| `CONSTITUTION_FILE` | `product-design/constitution.md` | Project constitution |
| `DESIGN_INTENT` | `product-design/product-design-as-intended.md` | Unified working intent + Decisions + CHANGELOG |
| `UX_RESEARCH` | `product-design/ux-research-results.md` | UX research: personas, problem scenarios, journeys, CHANGELOG |
| `AS_CODED` | `product-design/product-design-as-coded.md` | Unified implementation state: Conceptual Design, Metacommunication, Journey Maps |

---

## As-Intended / As-Coded Registry

> Registered as-intended/as-coded file pairs for the TaskFlow demo.

| As-Intended file | Section | As-Coded counterpart |
| ---------------- | ------- | -------------------- |
| `${DESIGN_INTENT}` | §0-§17 design intent + Decisions + CHANGELOG | `${AS_CODED}` |
| `${DESIGN_INTENT}` | §15 designed journeys | `${AS_CODED} § Journey Maps` |

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
