# TEMPLATE - UX DESIGN STANDARDS REFERENCE

> **How to use this template:** Copy this file to `project-ux-design-standards.md` and customize for your project. Replace `{{placeholders}}` with your project's actual values. Remove sections that don't apply to your product. This template provides sensible defaults for non-technical product designers -- each default includes a rationale so you can make informed decisions even without a UX specialist.

---

## 1. App Type & Default Pattern Set

> Select the app type that best describes your product. This determines the recommended defaults throughout this file.

| App Type | Description | Example | Recommended Navigation | Recommended Form Pattern |
|----------|-------------|---------|----------------------|-------------------------|
| **CRUD Admin** | Data management with lists, forms, and detail views | Project management tool, CMS backend | Sidebar | Inline validation |
| **Content Platform** | Publishing, reading, and discussion of content | Blog platform, knowledge base, wiki | Top nav | Progressive disclosure |
| **Marketplace** | Browse, compare, and transact between parties | E-commerce, freelance marketplace | Top nav + filters | On-submit (checkout flow) |
| **Dashboard** | Data visualization, monitoring, and reporting | Analytics dashboard, admin panel | Sidebar + tabs | Inline validation |
| **Social / Community** | User profiles, feeds, messaging, collaboration | Social network, forum, team chat | Bottom nav (mobile) / Sidebar (desktop) | Inline validation |

**Selected app type:** `{{APP_TYPE}}`

> *Default: CRUD Admin. Rationale: most common app type for new projects; provides a well-understood interaction vocabulary. Example: a project management tool like Trello or Asana.*

---

## 2. Navigation Patterns

> How users move between major sections of your application.

### Primary Navigation

| Pattern | Best For | Pros | Cons |
|---------|----------|------|------|
| **Sidebar** | Admin panels, data-heavy apps with 5+ top-level sections | Always visible, supports deep hierarchy, works with icons + labels | Consumes horizontal space, harder on small screens |
| **Top nav** | Content sites, marketing pages, apps with 3-5 sections | Clean layout, familiar pattern, full-width content area | Limited items, no deep hierarchy, collapses to hamburger on mobile |
| **Bottom nav** | Mobile-first apps, consumer products | Thumb-friendly, always visible on mobile | Max 5 items, no hierarchy, desktop-unfriendly |
| **Hamburger** | Simple apps, mobile-first, secondary navigation | Saves space, hides complexity | Hidden = lower discoverability, extra tap to access |

**Selected pattern:** `{{PRIMARY_NAVIGATION}}`

> *Default: Sidebar. Rationale: accommodates growth (adding sections later), provides persistent wayfinding, and works well for both data-heavy and content-oriented applications. Example: GitHub's left sidebar.*

### Secondary Navigation

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **Tabs** | 2-5 views within a page context | Settings page with General / Security / Notifications tabs |
| **Breadcrumbs** | Hierarchical content deeper than 2 levels | File explorer: Home > Projects > My Project > Settings |
| **Contextual sidebar** | Filters, configuration panels | E-commerce category filters |

**Selected secondary pattern:** `{{SECONDARY_NAVIGATION}}`

> *Default: Tabs + Breadcrumbs (both). Rationale: tabs handle in-page navigation while breadcrumbs handle hierarchical depth -- they serve complementary purposes. Example: AWS Console uses breadcrumbs for hierarchy and tabs within resource pages.*

---

## 3. Form Patterns

> How your application collects and validates user input.

### Validation Strategy

| Strategy | Best For | Pros | Cons |
|----------|----------|------|------|
| **Inline validation** | Most forms, especially data entry | Immediate feedback, fewer submission errors | Can feel aggressive if triggered too early (use on-blur, not on-change) |
| **On-submit** | Checkout flows, multi-step wizards | Less visual noise during entry, batch error display | Users must fix errors after attempting submission |
| **Progressive disclosure** | Complex forms, onboarding | Reduces cognitive load, guides users step by step | Longer perceived flow, users can't see the full picture |

**Selected strategy:** `{{FORM_VALIDATION_STRATEGY}}`

> *Default: Inline validation (on-blur). Rationale: industry standard for web forms since 2015; reduces submission errors by 22% (Baymard Institute, 2024). Trigger validation on field blur, not on every keystroke. Example: GitHub's sign-up form validates username availability on blur.*

### Form Conventions

| Convention | Default | Rationale | Example |
|-----------|---------|-----------|---------|
| Required field indicator | Asterisk (*) after label | Most universally recognized pattern (Nielsen Norman Group) | `Email *` |
| Error message placement | Below the field, in red/danger color | Closest to the error source; color provides secondary signal | `Password must be at least 8 characters` |
| Success feedback | Green checkmark icon on valid fields | Positive reinforcement reduces abandonment | Green checkmark after valid email |
| Disabled submit button | Enabled always; show errors on click | Disabled buttons confuse users about what's wrong | Submit button always clickable; errors appear on click if invalid |
| Auto-save | For long forms (>5 fields) | Prevents data loss on accidental navigation | Draft auto-saved every 30 seconds |
| Form layout | Single column, top-aligned labels | Fastest completion time (Matteo Penzo, 2006); mobile-friendly | Labels above fields, one field per row |

---

## 4. Feedback & Notification Patterns

> How the application communicates status changes, confirmations, and errors to users.

### Feedback Types

| Type | Pattern | When to Use | Duration | Example |
|------|---------|-------------|----------|---------|
| **Success** | Toast notification | After completing an action | 3-5 seconds, auto-dismiss | "Project saved successfully" |
| **Error (recoverable)** | Inline message | Validation errors, failed requests with retry | Persistent until resolved | "Failed to save. [Retry]" |
| **Error (critical)** | Error page or modal | System errors, permission denied, 500 | Persistent | "Something went wrong. Please try again later." |
| **Warning** | Banner or inline alert | Approaching limits, deprecated features | Persistent until dismissed | "You have 2 days left in your trial" |
| **Info** | Inline tip or banner | First-time hints, feature announcements | Dismissible | "Tip: You can drag items to reorder them" |
| **Loading** | Skeleton screen or spinner | Data fetching, processing | Until complete | Skeleton placeholders matching content layout |
| **Confirmation** | Modal dialog | Destructive actions (delete, overwrite) | Until user decides | "Delete this project? This cannot be undone." |

### Feedback Conventions

| Convention | Default | Rationale | Example |
|-----------|---------|-----------|---------|
| Toast position | Top-right | Visible without obstructing content; follows reading direction (LTR) | Toast appears at top-right, stacks downward |
| Toast auto-dismiss | 4 seconds for success, persistent for errors | Success needs acknowledgment, not action; errors need resolution | Success toast fades after 4s; error toast stays with dismiss button |
| Destructive confirmation | Double confirmation (type to confirm) for irreversible actions | Prevents accidental data loss; required for delete-all, account deletion | "Type DELETE to confirm" |
| Optimistic updates | Yes, for low-risk actions (star, bookmark, reorder) | Reduces perceived latency; rollback on failure | Star icon toggles instantly; reverts if API fails |
| Loading skeleton | Match content layout shape | Reduces layout shift (CLS); feels faster than spinners | Card-shaped skeletons while loading a card grid |

---

## 5. Empty States & Zero-Data Design

> What users see when there's no content to display.

### Empty State Strategy

| Strategy | Best For | Pros | Cons |
|----------|----------|------|------|
| **Action prompt** | Primary entities (first project, first task) | Guides users to take their first action; reduces confusion | Requires custom illustration/copy per entity |
| **Illustration + text** | Secondary views (empty search results, no notifications) | Friendly, reduces anxiety about empty screens | Requires design assets |
| **Text-only** | Inline lists, table rows, minor sections | Lightweight, easy to implement | Less engaging |

**Selected strategy:** `{{EMPTY_STATE_STRATEGY}}`

> *Default: Action prompt for primary entities, text-only for secondary. Rationale: first-use experience drives retention; primary entities deserve rich empty states while secondary views can be minimal. Example: Notion's "Get started" page with template suggestions vs. an empty search result showing "No results found."*

### Empty State Checklist

Every empty state must include:

- [ ] Explanation of why it's empty (context-appropriate)
- [ ] Primary action to create content (if applicable)
- [ ] Visual distinction from loading/error states
- [ ] Appropriate tone (encouraging for first-use, neutral for filtered results)

---

## 6. Error Handling UX

> How errors are presented and how users recover from them.

### Error Handling Strategy

| Error Type | Display Pattern | Recovery Path | Example |
|-----------|----------------|---------------|---------|
| **Validation** | Inline, below field | Fix the field and re-submit | "Email format is invalid" |
| **Network** | Toast or inline banner with retry | Automatic retry + manual retry button | "Connection lost. Retrying... [Retry now]" |
| **Permission** | Full-page or section-level message | Request access or contact admin | "You don't have access to this project. [Request access]" |
| **Not found** | Full-page 404 | Navigation to parent or home | "This page doesn't exist. [Go to dashboard]" |
| **Server error** | Full-page 500 | Retry or contact support | "Something went wrong. [Try again] [Contact support]" |
| **Rate limit** | Toast with countdown | Wait and retry | "Too many requests. Try again in 30 seconds." |

### Error UX Conventions

| Convention | Default | Rationale | Example |
|-----------|---------|-----------|---------|
| Error language | Plain language, no codes | Users don't understand HTTP codes or stack traces | "We couldn't save your changes" not "Error 500: Internal Server Error" |
| Preserve user input | Always on form errors | Losing typed data is the #1 frustration (Baymard, 2024) | Form fields retain values after validation error |
| Error boundary | Per-section, not full page | A failing widget shouldn't break the entire page | Sidebar error doesn't crash the main content area |
| Retry mechanism | Automatic (3x, exponential backoff) + manual button | Transient failures often resolve on retry | Auto-retry with "Still trying..." then "Retry" button |

---

## 7. Usability Heuristics Checklist

> Adapted from Jakob Nielsen's 10 Usability Heuristics (1994, revised 2024) for web applications. Use this as a review checklist when designing new features.

| # | Heuristic | Question to Ask | Example |
|---|-----------|----------------|---------|
| 1 | **Visibility of system status** | Does the user always know what's happening? | Loading indicators, progress bars, save confirmations |
| 2 | **Match between system and real world** | Does the UI use the user's language, not developer jargon? | "Remove" not "DELETE", "Sign in" not "Authenticate" |
| 3 | **User control and freedom** | Can users undo, cancel, or go back easily? | Undo toast after delete, Cancel button on every modal |
| 4 | **Consistency and standards** | Does this follow platform conventions and our own patterns? | Same button styles, same form layouts, same terminology |
| 5 | **Error prevention** | Does the design prevent errors before they happen? | Disable unavailable options, confirm destructive actions |
| 6 | **Recognition rather than recall** | Is information visible rather than requiring memory? | Autocomplete, recent items, visible labels (not just icons) |
| 7 | **Flexibility and efficiency** | Can experienced users take shortcuts? | Keyboard shortcuts, bulk actions, search-as-navigation |
| 8 | **Aesthetic and minimalist design** | Is every element necessary? Does it earn its space? | Remove decorative elements that don't serve function |
| 9 | **Help users recognize and recover from errors** | Are error messages clear, specific, and actionable? | "Password must include a number" not "Invalid input" |
| 10 | **Help and documentation** | Is help available in context, not just in a separate docs site? | Tooltips, inline hints, contextual help panels |

---

## 8. Accessibility Workflow

> How your team ensures the application is accessible to all users.

### Target Level

**WCAG target:** `{{WCAG_LEVEL}}`

> *Default: WCAG 2.1 AA. Rationale: industry standard; legally required in many jurisdictions (ADA, EAA 2025); achievable without specialized expertise. AAA is recommended for public/education/government platforms. Example: all text meets 4.5:1 contrast ratio (AA) vs. 7:1 (AAA).*

### Accessibility Audit Cadence

| Cadence | Best For | Pros | Cons |
|---------|----------|------|------|
| **Per-sprint** | Teams with dedicated a11y resources | Catches issues early, prevents debt | Requires tooling and expertise |
| **Per-release** | Most teams | Balances effort and coverage | Issues may accumulate within a release |
| **Quarterly** | Small teams, early-stage products | Low overhead | Issues ship to users before being caught |

**Selected cadence:** `{{A11Y_AUDIT_CADENCE}}`

> *Default: Per-release. Rationale: catches issues before they reach users without requiring per-sprint overhead; automated tools (axe-core, Lighthouse) can run in CI for continuous basic coverage. Example: axe-core in CI catches P0 issues automatically; manual audit before each release catches nuanced issues.*

### Audit Tools & Process

| Tool | Type | When to Run | What It Catches |
|------|------|------------|----------------|
| **axe-core** (or axe-linter) | Automated | CI pipeline, every PR | ~57% of WCAG issues: missing alt text, contrast, ARIA |
| **Lighthouse** | Automated | Pre-release | Performance + a11y scores, best practices |
| **Screen reader testing** | Manual | Per-release | Navigation flow, dynamic content announcements |
| **Keyboard navigation** | Manual | Per-feature | Focus management, tab order, keyboard traps |

### Minimum Accessibility Requirements

| Requirement | Standard | Verify |
|------------|----------|--------|
| Color contrast | >= 4.5:1 (text), >= 3:1 (large text, UI components) | axe-core or contrast checker |
| Keyboard navigation | All interactive elements focusable and operable | Tab through entire flow |
| Focus indicators | Visible focus ring on all interactive elements | Visual inspection |
| Alt text | All informative images have descriptive alt text | axe-core |
| Form labels | All inputs have associated labels | axe-core |
| Error identification | Errors identified by text, not just color | Manual review |
| Skip navigation | Skip-to-main-content link on all pages | Keyboard test |
| ARIA landmarks | Main, nav, aside, footer landmarks present | axe-core |

---

## 9. User Research Artifacts

> How your team maintains understanding of users over time.

### Persona Maintenance

| Artifact | Cadence | Owner | Format |
|----------|---------|-------|--------|
| **Persona documents** | Review quarterly, update after major research | Product designer | Markdown in `.agent-resources/` or design tool |
| **Journey maps** | Update per major feature | Product designer | Diagram (Mermaid, FigJam, or Miro) |
| **Usability test reports** | Per-release (minimum) | Product designer or UX researcher | Markdown report with findings + severity |

> *Default: Quarterly persona review + per-release usability test. Rationale: personas drift as the product evolves; usability tests before release catch the highest-impact issues. Example: a 5-participant usability test using think-aloud protocol on the 3 most critical user flows.*

### Usability Testing Conventions

| Convention | Default | Rationale | Example |
|-----------|---------|-----------|---------|
| Test method | Remote unmoderated (for speed) or moderated (for depth) | Remote unmoderated scales; moderated catches nuance | UserTesting.com or Maze for unmoderated; Zoom for moderated |
| Participants per round | 5 | Finds ~85% of usability issues (Nielsen, 2000) | 5 participants per persona for each test round |
| Severity scale | Critical / Major / Minor / Cosmetic | Prioritizes fixes by user impact | Critical = task failure; Major = significant delay; Minor = noticed but worked around |
| Task success rate target | >= 80% for primary flows | Below 80% indicates a broken flow | "Create a new project" succeeds for 4/5 participants |

---

## 10. Responsive Design Strategy

> How your application adapts across screen sizes and devices.

### Approach

| Strategy | Best For | Pros | Cons |
|----------|----------|------|------|
| **Mobile-first** | Consumer products, content platforms | Forces prioritization, smaller initial CSS | Desktop may feel empty without enhancement |
| **Desktop-first** | Admin panels, data-heavy apps | Easier to design complex layouts first | Mobile often feels cramped as an afterthought |

**Selected approach:** `{{RESPONSIVE_APPROACH}}`

> *Default: Mobile-first. Rationale: forces content prioritization, results in better performance on constrained devices, and progressive enhancement is more robust than graceful degradation. Example: start with a single-column layout, add sidebar and multi-column at larger breakpoints.*

### Breakpoints

| Token | Width | Target | Example |
|-------|-------|--------|---------|
| `sm` | `{{BP_SM}}` | Mobile landscape, large phones | 640px (Tailwind default) |
| `md` | `{{BP_MD}}` | Tablets, small laptops | 768px (Tailwind default) |
| `lg` | `{{BP_LG}}` | Laptops, desktops | 1024px (Tailwind default) |
| `xl` | `{{BP_XL}}` | Large desktops | 1280px (Tailwind default) |

> *Default: Tailwind CSS default breakpoints. Rationale: widely adopted, well-tested across device landscape, and consistent with the recommended CSS framework. Example: sidebar collapses to hamburger below `lg` (1024px).*

### Responsive Conventions

| Convention | Default | Rationale | Example |
|-----------|---------|-----------|---------|
| Touch targets | Minimum 44x44px | WCAG 2.5.8 (AAA) and Apple HIG recommendation | Buttons, links, and interactive elements >= 44px tap area |
| Content reflow | Single column below `md` | Prevents horizontal scrolling on mobile | Two-column layout becomes single column on tablets |
| Image strategy | Responsive images with `srcset` | Serves appropriate resolution per device; saves bandwidth | 1x, 2x, and 3x variants for hero images |
| Font scaling | `clamp()` for fluid typography | Smooth scaling without media query breakpoints | `font-size: clamp(1rem, 2.5vw, 1.5rem)` |

---

## 11. Design System Governance

> How design decisions are documented, maintained, and evolved.

### Token Naming Convention

| Layer | Pattern | Example |
|-------|---------|---------|
| **Primitive** | `color-{hue}-{shade}` | `color-blue-500`, `color-gray-100` |
| **Semantic** | `color-{purpose}` | `color-primary`, `color-danger`, `color-surface` |
| **Component** | `{component}-{property}-{state}` | `button-bg-hover`, `input-border-focus` |

> *Default: Three-layer token architecture (primitive > semantic > component). Rationale: primitives provide a palette, semantic tokens assign meaning, component tokens handle state -- this prevents coupling between visual design and component logic. Example: changing brand color updates `color-primary` (semantic), which cascades to all `button-bg-*` (component) tokens.*

### Component Lifecycle

| Stage | Description | Rule |
|-------|-------------|------|
| **Draft** | Proposed, not yet reviewed | May be used in feature branches only |
| **Active** | Reviewed, documented, in production | Preferred for all new development |
| **Deprecated** | Superseded by a newer pattern | Show console warning; migration deadline set |
| **Removed** | Deleted from codebase | Must be removed from all consumers first |

### Design System Maintenance

| Activity | Cadence | Owner | Example |
|----------|---------|-------|---------|
| Token audit | Per-release | Product designer | Verify all tokens are used; remove orphans |
| Component inventory | Quarterly | Product designer + engineer | List all components, check for duplicates or drift |
| Pattern documentation | Per new pattern | Whoever creates it | Add usage guidelines, do/don't examples |
