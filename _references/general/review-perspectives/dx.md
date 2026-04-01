# DX — Developer Experience

## Essential

- [P0] Is the code readable, self-documenting, and following project conventions?
- [P0] Are error messages helpful for debugging? Are edge cases handled gracefully?
- [P0] Is there a CI/CD pipeline that runs tests, linting, and type-checking on every commit?
- [P0] Can a developer go from clone to passing tests in under 5 minutes with a single command, and does the pipeline fail fast with clear, actionable error messages?
- [P0] Does the internal developer platform provide self-service environment provisioning, secrets management, and deployment so developers never need to file a ticket to do routine work?
- [P0] Are inline code comments, API docs, and architecture decision records kept up to date and co-located with the code they describe?
- [P0] Will a new contributor understand this without tribal knowledge?

## Deep-dive

- [P1] Is there automated dependency update tooling (Dependabot, Renovate)?
- [P1] Are coverage thresholds enforced, preventing regressions below a minimum?
- [P1] Are code review guidelines documented and enforced consistently, including expectations for review turnaround time, required approvals, and constructive feedback norms?
- [P1] Is there a structured onboarding path (quick-start guide, sample tasks, mentorship pairing) that lets a new team member ship a meaningful change within their first week?
- [P1] Are contribution guidelines, issue templates, and a code of conduct published and maintained so that external or cross-team contributors can participate without friction?
- [P2] Does the project provide editor configurations (`.editorconfig`, recommended extensions, launch configs) so that IDE features like auto-complete, go-to-definition, and debugging work out of the box?
- [P2] Are linting rules, formatting standards, and static analysis checks automated in pre-commit hooks and CI so that style discussions never block code reviews?
- [P2] In a monorepo setup, are build caching, affected-target detection, and dependency graph tooling in place so that developers only build and test what changed?
- [P3] Are developer productivity metrics (build times, CI wait times, deploy frequency, time-to-first-commit) tracked and reviewed regularly to identify bottlenecks?
