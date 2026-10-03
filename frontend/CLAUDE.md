# Frontend

Next.js (App Router) + TypeScript + Tailwind CSS v4. Deps via `npm`, pinned in
`package.json`. Runs in Docker via `../docker-compose.yml` (service `web`, :3000).
Talks only to `match-api` over HTTP; it never touches the DB.

## Commands

- `make install`: install deps
- `make dev`: next dev with hot reload on :3000
- `make build`: production build (standalone output)
- `make lint`: eslint
- `make up` / `make down`: docker compose (just the `web` service)

## Layout

- `app/layout.tsx`: shell, nav, global styles — no feature logic
- `app/page.tsx`: public UI, chat (problem -> matched innovations)
- `app/innowacje/`: innovation library and detail pages
- `app/admin/`: admin UI behind `components/admin/AdminGate.tsx` (login form on 401), one route per area
- `components/`: shared UI (toolbar, header, footer, cards) and feature folders
- `lib/demo-data.ts`, `lib/admin-mock.ts`: fallbacks when the api is unreachable
- `lib/api.ts`: the only place that knows the API shape; typed client
- `app/globals.css`: Tailwind entry + design tokens (documentation/frontend/DESIGN.md)

New features go in new route folders so devs rarely edit the same file.

## Collaboration

- Never push to `main`. Branch per task: `feat/<area>-<what>`, `fix/<area>-<what>`; PR reviewed by a teammate.
- Small PRs, merge often, rebase on `main` first.
- Agree on API contracts before implementing; types in `lib/api.ts` mirror the backend Pydantic schema and are the contract.
- Shared files (`layout.tsx`, `lib/api.ts`, `package.json`, `docker-compose.yml`): small, additive edits only; announce in team chat.
- Commits start with a verb, scope in parens: `feat(match): add results list`. No bare "fix"/"update".
- Never commit `.env`, secrets, `node_modules`, `.next`. New env vars go in `.env.example` (must be `NEXT_PUBLIC_*` to reach the browser).
- New dependency: pin in `package.json`, separate commit, mention in PR.

## Code rules

- TypeScript strict; no `any`. API request/response shapes are typed interfaces in `lib/api.ts`, not inline objects.
- Components stay thin; data access goes through `lib/api.ts`.
- Handle API failure explicitly (loading / error states); never assume the backend is up.
- No hardcoded URLs or secrets; read the API base from `NEXT_PUBLIC_API_URL`.
- Comments only for non-obvious why; lowercase, short.
- Before a PR: `make lint` and `make build` pass.
- No premature abstractions; add a component only on the second use.

## Accessibility (WCAG 2.1 AA is 20% of the score)

- Use the tokens (`text-body-lg`, `bg-primary`, ...), never raw colours or px font sizes: high contrast and A+/A++ depend on them.
- Every boxed surface gets `hc-edge` so it keeps an outline in high contrast.
- Icons via `<Icon name=...>` (always aria-hidden); new glyph -> add to `scripts/fetch-icons.sh` and run it.
- Visible label for every field, min 48 px targets, no text under 14 px, feedback via `role="status"`.
