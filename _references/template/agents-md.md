# Template: AGENTS.md

> Copy this file to the project root as `AGENTS.md` and fill in the placeholders.

---

# ${PROJECT_NAME}

${PROJECT_DESCRIPTION}

## Stack

- **Backend:** ${BACKEND_STACK}
- **Frontend:** ${FRONTEND_STACK}
- **Testing:** ${TESTING_STACK}
- **Deployment:** ${DEPLOYMENT_STACK}

## Build & Run

### Backend

```bash
cd ${BACKEND_DIR}
# Add backend setup and run commands
```

### Frontend

```bash
cd ${FRONTEND_DIR}
# Add frontend setup and run commands
```

### Tests

```bash
# Backend unit tests
cd ${BACKEND_DIR} && ${BACKEND_TEST_CMD}

# Frontend unit tests
cd ${FRONTEND_DIR} && ${FRONTEND_TEST_CMD}

# E2E tests
cd e2e && ${E2E_TEST_CMD}
```

### Database Migrations

```bash
cd ${BACKEND_DIR}
# Add migration commands
```

## Architecture

### Backend

${BACKEND_ARCHITECTURE_SUMMARY}

### Frontend

${FRONTEND_ARCHITECTURE_SUMMARY}

## Key Conventions

- ${CONVENTION_1}
- ${CONVENTION_2}
- ${CONVENTION_3}

## Validation Scripts

Helper scripts in `.codex/skills/scripts/`:

```bash
# List available validation scripts and their purpose
```

## Skills, Agents, and References

This project uses Codex skills (`.codex/skills/`) and reference files (`_references`). Skills can be invoked explicitly via `$skill-name` or triggered automatically from the request. Key skills: `$plan`, `$implement`, `$advise`, `$check review`, and `$check validate`.

@_references/project/conventions.md
@_references/general/constraints.md
@_references/general/permissions.md
