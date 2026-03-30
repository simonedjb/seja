# Template: .claude/rules/i18n.md

> Copy to `.claude/rules/i18n.md` and customize for your project.

```yaml
---
paths:
  - "${FRONTEND_DIR}/src/i18n/**"
  - "${BACKEND_DIR}/translations/**"
---
```

# i18n Rules

- **Locale codes**: use RFC 5646 consistently (e.g., `pt-BR`, `en-US`). Never use bare language codes.
- **Key parity**: every key in one locale file must exist in all other locale files. Same structure, same nesting.
- **Diacritics**: translations must use proper accented characters. Never use ASCII approximations.
- **Key naming**: hierarchical dot notation — e.g., `auth.loginPlaceholder`, `groups.confirmDelete`.
- **Backend catalogs**: when adding or modifying backend strings, update all locale catalogs.
- **No hardcoded text**: every user-facing string must use a translation function.
- **Interpolation**: use the framework's interpolation syntax with trusted template strings only.
