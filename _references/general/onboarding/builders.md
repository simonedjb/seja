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
- **Coding conventions and standards**: Language-specific standards from `project/standards.md §§ Backend and Frontend`. Path-scoped rules from `.claude/rules/`.
- **Development environment setup**: Repository clone, dependency install, environment variables, database setup, first test run. Target: clone-to-passing-tests in under 5 minutes.
- **CI/CD pipeline**: Build, test, lint, deploy stages. How to trigger, how to read failures, how to deploy.
- **Branching and PR workflow**: Branch naming, commit message conventions, PR template, review expectations.
- **AI-assisted development workflow**: Sanctioned AI tools, how to use them effectively, how to review AI-generated code, when AI output needs human judgment.

### Deep-dive (load for thorough onboarding or when Builder is the primary role)

- **Dependency map**: Key third-party libraries, internal shared packages, integration points with external services.
- **Data model**: Entity relationships, naming conventions, migration workflow. Use `/explain data-model` to generate if not available.
- **Testing strategy**: Unit, integration, e2e test boundaries. Coverage expectations. How to write and run tests. See `project/standards.md § Testing` for conventions.
- **Error handling patterns**: How errors propagate through layers, logging conventions, error response formats.
- **Performance constraints**: Known bottlenecks, caching strategy, query optimization patterns.
- **Security boundaries**: Authentication/authorization flow, input validation expectations, secrets management.

## Recommended First Tasks by Level

| Level | First Task | Goal |
|-------|-----------|------|
| L1 Contributor | Fix a well-scoped bug (newcomer) or implement a small feature (practitioner) | Build confidence, learn conventions and PR workflow |
| L2 Expert | Review and improve an existing module | Understand design decisions, propose improvements |
| L3 Leader | Audit a cross-cutting concern (Strategist) or lead a planning session (Manager) | Map system-wide patterns or understand team dynamics |

## Key Reference Files

- `project/standards.md § Backend` (if backend role)
- `project/standards.md § Frontend` (if frontend role)
- `.claude/rules/backend.md`, `.claude/rules/frontend.md` (path-scoped rules)
- `project/product-design-as-coded.md § Conceptual Design` (current system design)
- `general/review-perspectives/dx.md` (developer experience standards)
