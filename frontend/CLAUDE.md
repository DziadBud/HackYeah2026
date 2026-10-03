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
- `app/page.tsx`: public UI (problem -> matched innovations)
- `app/admin/`: admin UI (behind auth later), one route per area
- `lib/api.ts`: the only place that knows the API shape; typed client
- `app/globals.css`: Tailwind entry + theme tokens

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
