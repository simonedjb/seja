---
paths:
  - "frontend/src/**"
---

# Frontend Rules

- **TypeScript required** for new files (`.ts`/`.tsx`). Convert existing `.js`/`.jsx` when substantively modified.
- **DOMPurify**: sanitize HTML before `dangerouslySetInnerHTML` — never render user input as raw HTML.
- **Stable useTranslation mock** (critical): return a referentially stable object — new references per call cause hanging tests.

See `project/frontend-standards.md` and `project/testing-standards.md` for full conventions.

## Perspective Alignment

This rule is governed by: **UX** (user experience), **A11Y** (accessibility), **VIS** (visual design), **RESP** (responsive design).
