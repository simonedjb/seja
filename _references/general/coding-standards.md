# GENERAL - CODING STANDARDS

## Universal Principles

- **Small, focused functions**: prefer functions of ~20 lines or fewer. If a function does more than one thing, extract the parts.
- **Descriptive naming**: use intention-revealing names for variables, functions, and classes. Avoid abbreviations unless they are universally understood (e.g., `id`, `url`, `db`).
- **Error handling**: fail fast. Validate inputs at boundaries and provide context in error messages (what failed, why, and how to fix it).
- **Logging**: log at appropriate levels (DEBUG for development tracing, INFO for key operations, WARNING for recoverable issues, ERROR for failures). Prefer structured logging over ad-hoc print statements.
- **Rule of Three**: extract shared logic only when it is used 3+ times. Three similar lines of code are better than a premature abstraction.
- **Comments**: explain *why*, not *what*. Code should be self-documenting through clear naming and structure. Comment non-obvious decisions, workarounds, and constraints.

## Review Integration

- For every code to be created or altered, evaluate against the applicable engineering and design perspectives in `general/review-perspectives.md`, recording each perspective as adopted, deferred (with reason), or N/A on the plan. If a best practice is deferred only because it is out of scope, ask the user whether it should be included in the plan.
- If at any point in the execution a helper script is generated that can be useful for future plans, write it into `${TMP_DIR}` (see project/conventions.md) with a header describing its purpose, usage, and other information that may be useful to support future prompt executions.
- For detailed frontend conventions, see `project/frontend-standards.md`. For backend conventions, see `project/backend-standards.md`. For testing conventions, see `project/testing-standards.md`.

## Git commit messages

Template for a good commit message:

```
<type>[optional scope]: <description>
[optional body]
[optional footer(s)]
```

The commit type can be

- feat: Commits, which adds a new feature
- fix: Commits, that fixes a bug
- refactor: refactored code that neither fixes a bug nor adds a - feature but rewrites/restructures your code.
- chore : Changes that do not relate to a fix or feature and don’t modify src or test files basically miscellaneous commits (for example, updating dependencies or modifying .gitignore file)
- perf : Commits are special refactor commits, geared towards improving performance.
- ci : Continuous integration related.
- ops : Commits, that affect operational components like infrastructure, deployment, backup , recovery …
- build : Changes that affect the build system build tool, ci pipeline, dependencies, project version, …
- docs : Commits, that affect documentation, such as the README.
- style : changes that do not affect the meaning of the code, likely related to code formatting such as white-space, missing semi-colons, etc.
- revert: reverts a previous commit.
- test:commits that add missing tests or correct existing tests

Rules for creating a great commit message

- Limit the subject line to 50 characters
- Capitalize the subject/description line
- Do not end the subject line with a period
- Separate the subject from the body with a blank line
- Wrap the body at 72 characters
- Use the body to explain what and why
- Use the imperative mood in the subject line let it seem like you’re giving a command eg “feat: Add unit tests for user authentication”. Using the imperative mood in commit messages makes them more consistent and commands-like, which is helpful in understanding the actions taken.


## If stack includes i18n

- If strings are created or altered, ensure all affected i18n entries are updated. Mind the diacritics and accented characters.

## If stack includes a frontend

- If any frontend files were changed or added, update the corresponding contextual help and user docs.

## If stack includes Alembic/PostgreSQL

- Ensure that any Alembic migrations created or modified are idempotent and consider Postgres syntax.

## If stack includes TypeScript

- Frontend source files use TypeScript (`.ts`/`.tsx`). New files must be TypeScript; existing `.js`/`.jsx` files should be converted when modified. See `project/frontend-standards.md` §21 for type system conventions.

## If stack includes Python

- Backend source files use Python 3. See `project/backend-standards.md` for architectural conventions.
