# TEMPLATE - INTERNATIONALIZATION (I18N) STANDARDS REFERENCE

> **How to use this template:** Copy this file to `project-i18n-standards.md` and customize for your project. Replace `{{placeholders}}` with your actual locale codes, file paths, and conventions.

---

## 1. Locale Codes

All layers use **RFC 5646** locale codes consistently:

| Context | Format | Values | Default |
|---------|--------|--------|---------|
| Frontend | RFC 5646 | `{{PRIMARY_LOCALE}}`, `{{SECONDARY_LOCALE}}` | `{{PRIMARY_LOCALE}}` |
| Backend (API responses) | RFC 5646 | `{{PRIMARY_LOCALE}}`, `{{SECONDARY_LOCALE}}` | `{{BACKEND_DEFAULT_LOCALE}}` |
| Database (user preference) | RFC 5646 | `{{PRIMARY_LOCALE}}`, `{{SECONDARY_LOCALE}}` | `{{PRIMARY_LOCALE}}` |

### Backward Compatibility

> If your project accepts legacy locale formats, document the normalization rules:

- Backend `normalize_locale()` accepts 2-letter input and normalizes to RFC 5646.

---

## 2. Frontend i18n

> If stack includes react-i18next:

### Setup

- Framework: i18next + react-i18next
- Single `translation` namespace (no multi-namespace)
- `interpolation.escapeValue: false` (framework handles escaping)
- Resource keys: RFC 5646 codes
- Language loaded from user preferences on startup

> **Security warning:** Because `escapeValue` is disabled, the frontend framework's default escaping is the only protection. This does NOT apply when translations are rendered via `dangerouslySetInnerHTML`. Never interpolate user-supplied values into translation keys that are rendered as raw HTML without sanitization first.

### Translation Files

| File | Purpose |
|------|---------|
| `src/i18n/locales/{{primary}}.json` | Primary locale translations (e.g., `en-US.json`) |
| `src/i18n/locales/{{secondary}}.json` | Secondary locale translations (e.g., `pt-BR.json`) |

Both files must have **identical key structure** — parallel keys, no extras in either file.

### Key Naming Convention

Hierarchical dot notation with camelCase leaf names:

```
"auth.loginPlaceholder"
"{{entity}}.confirmDelete"
"errors.loadFailed"
```

| Segment | Convention | Examples |
|---------|-----------|---------|
| Root | Feature/domain name | `auth`, `errors`, `settings` |
| Leaves | camelCase action/noun | `title`, `confirmDelete`, `loadFailed` |

### Interpolation

```json
{ "confirmDeleteMessage": "Type \"{{name}}\" to confirm deletion..." }
```

Usage: `t("confirmDeleteMessage", { name: entity.title })`

### Usage in Components

```tsx
const { t, i18n } = useTranslation();

// String lookup
<h1>{t("{{section}}.title")}</h1>

// Current language (RFC 5646)
const lang = i18n.language;

// Change language
i18n.changeLanguage("{{locale}}");
```

---

## 3. Backend i18n

> If stack includes Flask-Babel:

### Setup

- **Framework:** Flask-Babel with standard gettext `.po/.pot` catalogs
- **Catalogs:** `{{BACKEND_DIR}}/translations/{locale}/LC_MESSAGES/messages.po`
- **Helpers:** Wrapper functions around `flask_babel.gettext()`
- **Compilation:** `.mo` files built via `pybabel compile -d translations`

### Translation Lookup

```python
locale = get_request_locale()
message = get_common_error('Error message key', locale=locale)
```

### Locale Negotiation

Priority:
1. Query parameter `?lang=...` (normalized)
2. HTTP `Accept-Language` header (first match)
3. Default: `{{BACKEND_DEFAULT_LOCALE}}`

### Interpolation

Uses Python `str.format()` with keyword arguments (applied after gettext lookup):

```python
message = get_common_error('Entity {name} not found', locale=locale, name=name)
```

> **Security warning:** Python's `str.format()` can access object attributes. Never pass user-supplied data as the format string itself. Always use keyword arguments from a trusted template string.

### Adding New Backend Strings

1. Add the `msgid` / `msgstr` pair to all `.po` files
2. Compile: `pybabel compile -d translations`
3. Use helper functions in code
4. To extract markers from source: `pybabel extract -F babel.cfg -o translations/messages.pot .`

---

## 4. Multilingual Domain Entities

> If any entities store translations in the database, document them:

| Entity | Translation Table | Fields |
|--------|------------------|--------|
| {{Entity}} | {{EntityTranslation}} | `name`, `locale` |

### Resolution

```python
name = resolve_translation_name(entity.translations, locales=['{{locale}}'], fallback='{{fallback}}')
```

---

## 5. Rules — Always Follow

### When Creating or Modifying Strings

1. **Update all locale files** — every key in one file must exist in all others.
2. **Mind diacritics** — languages with accented characters require proper encoding.
3. **No hardcoded text** — every user-facing string must use an i18n key (frontend) or helper function (backend).
4. **Backend error messages** — add entries to all `.po` files, then compile.

### Key Sync Checklist

When adding a feature that spans both layers:

- [ ] Frontend: add keys to all locale JSON files
- [ ] Backend: add entries to all `.po` files, then compile
- [ ] Constants: ensure validation limits match between backend and frontend
- [ ] Labels: if adding selectable options, ensure all locale labels are present

### Email Templates

> If your application sends localized emails:

- Email template dictionaries use short language keys (e.g., `'en'`, `'pt'`)
- An adapter function converts RFC 5646 locale codes to template keys

---

## 6. Default Locale Rationale

> Document why your frontend and backend use different default locales (if they do):

- **Frontend default:** `{{PRIMARY_LOCALE}}` — {{rationale}}
- **Backend default:** `{{BACKEND_DEFAULT_LOCALE}}` — {{rationale}}

---

## 7. Known Limitations & Future Improvements

| Limitation | Impact | Future Target |
|------------|--------|---------------|
| {{limitation}} | {{impact}} | {{target}} |
