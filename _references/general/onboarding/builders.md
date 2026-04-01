# BLD — Builders

> Developers, DevOps engineers, and infrastructure engineers who write, deploy, and maintain code.

## Roles

- Frontend developer
- Backend developer
- Full-stack developer
- Mobile developer
- DevOps / Infrastructure engineer
- Data engineer / ML engineer

## Layer 1 — Role-Specific Onboarding Content

### Essential (all Builders must cover)

- **Architecture overview**: System layers, component boundaries, data flow, deployment topology. Use `/explain architecture` to generate if not available.
- **Coding conventions and standards**: Language-specific standards from `project/backend-standards.md` and/or `project/frontend-standards.md`. Path-scoped rules from `.claude/rules/`.
- **Development environment setup**: Repository clone, dependency install, environment variables, database setup, first test run. Target: clone-to-passing-tests in under 5 minutes.
- **CI/CD pipeline**: Build, test, lint, deploy stages. How to trigger, how to read failures, how to deploy.
- **Branching and PR workflow**: Branch naming, commit message conventions, PR template, review expectations.
- **AI-assisted development workflow**: Sanctioned AI tools, how to use them effectively, how to review AI-generated code, when AI output needs human judgment.

### Deep-dive (load for thorough onboarding or when Builder is the primary role)

- **Dependency map**: Key third-party libraries, internal shared packages, integration points with external services.
- **Data model**: Entity relationships, naming conventions, migration workflow. Use `/explain data-model` to generate if not available.
- **Testing strategy**: Unit, integration, e2e test boundaries. Coverage expectations. How to write and run tests. See `project/testing-standards.md` for conventions.
- **Error handling patterns**: How errors propagate through layers, logging conventions, error response formats.
- **Performance constraints**: Known bottlenecks, caching strategy, query optimization patterns.
- **Security boundaries**: Authentication/authorization flow, input validation expectations, secrets management.

## Recommended First Tasks by Level

| Level | First Task | Goal |
|-------|-----------|------|
| L1 | Fix a well-scoped bug with a failing test | Build confidence, learn PR workflow |
| L2 | Implement a small, well-defined feature | Learn conventions, architecture boundaries |
| L3 | Review and improve an existing module | Understand design decisions, propose improvements |
| L4 | Audit a cross-cutting concern (logging, auth, caching) | Map system-wide patterns, identify debt |
| L5 | Lead a planning session for an upcoming feature | Understand team dynamics, process, priorities |

## Key Reference Files

- `project/backend-standards.md` (if backend role)
- `project/frontend-standards.md` (if frontend role)
- `.claude/rules/backend.md`, `.claude/rules/frontend.md` (path-scoped rules)
- `project/conceptual-design-as-is.md` (current system design)
- `general/review-perspectives/dx.md` (developer experience standards)
