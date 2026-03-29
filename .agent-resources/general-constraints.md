# GENERAL - CONSTRAINTS

- All files must be UTF-8 encoded.
- Do not invent data.
- Do not generate agent-dependent or nondeterministic behavior unless explicitly requested.
- Do not use ANSI code in generated code or reports.
- Do not reduce existing test coverage. When modifying code that has tests, update or extend the tests to maintain coverage.
- Do not implement placeholder or simplistic implementations.
- If you come across an opportunity to add a desirable but unessential feature based on similar products or best practices, describe the proposal, provide pros and cons, and ask the user. When working autonomously, as in `auto` or `bypassPermissions` mode, do not add unessential features.
  
## If stack includes TypeScript (frontend)

- New frontend files must be TypeScript (`.ts`/`.tsx`). Existing `.js`/`.jsx` files should be converted when substantively modified.
