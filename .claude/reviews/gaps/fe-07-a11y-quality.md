# FE-07 Accessibility, routes, fallbacks

**Criterion:** R8 (20%), R14 (10%).
**PR:** `chore/a11y-pass`

- **Routes in English:** `/innowacje` → `/innovations`, `/admin/innowacje` → `/admin/innovations`, `/admin/zgloszenia` → `/admin/problem-reports`. Mail links already use `/innovations/{id}`.
- **Silent fallbacks:** `Chat.tsx` answers from `demo-data` on network/5xx; admin views fall back to `admin-mock`. Keep chat fallback but make the "dane przykładowe" label prominent; admin shows an error banner instead of mock data.
- **axe + keyboard-only** on chat, idea form, innovation page, admin: focus after answer, `aria-live` announce, form error summary, 44px targets, high-contrast for admin charts.
- **Plain language:** inline one-liners for "innowacja społeczna", "JST", "Canvas".
- **Originality:** show "mnie też" count / "X gmin ma ten sam problem" on match results.
