# Backend review — 2026-10-03

HEAD `6888234`. Three parallel passes: requirements coverage, public surface, admin/auth/upload.
Tests: 140 public + 112 admin/services pass — **but every API test overrides deps with `mock.py`; no `Db*Service` SQL is exercised.**
rag/ treated as frozen; all fixes below are backend/compose/docs side.

Legend: ✅ verified (reproduced or confirmed in code by me), ◐ plausible (read, not run).

## P0 — demo breaks

| # | Finding | Where | Fix |
|---|---|---|---|
| 1 ✅ | `api` container has no `DATABASE_URL`; `.env` is dockerignored → falls back to `localhost:5432` (the api container itself). Every DB route 500s after `make up`; `/health` still green. | `docker-compose.yml:40-58`, `app/config.py:10`, `backend/.dockerignore` | add `DATABASE_URL: postgresql+psycopg://…@db:5432/…` (must be `+psycopg`) |
| 2 ✅ | Backend `sql/*.sql` not in `docker/postgres/init/`; fresh volume has no `problem_reports`, `ideas`, `threads`… until someone runs `make migrate`. | `docker/postgres/init/` | copy backend SQL into init (after rag files), or apply idempotent SQL on api startup |
| 3 ✅ | `docker/postgres/init/02-rag_chunks.sql` drifted from `rag/sql/001` — missing `innovations.content`, which rag selects/inserts. | init dir vs `rag/app/services/vector_store.py:63,104` | re-copy rag SQL into init |
| 4 ✅ | rag `/query` SQL references `feedback.kind`; backend `feedback` has no `kind`. Postgres fails at parse time → every `/query` errors once wired. | `backend/sql/006_feedback.sql`, `rag/.../vector_store.py:233` | add `kind text` to backend `feedback` (new migration) |

## P1 — requirements / judging

| # | Finding | Where |
|---|---|---|
| 5 ✅ | `/match` never calls rag: word-overlap ranking over all published rows; "why it fits" is a template. `GeminiClient` is unused. Mandatory relevance criterion is unmet; docs claim R1 "full". | `services/public/db.py:71-80`, `drafts.py:12-24`, `clients/rag.py` (only `embed_pdf`) |
| 6 ✅ | Gaps report is always empty: `gaps()` selects reports with 0 matches, but `challenge_area` is only set from a top match → always `None` → filtered by `if _area(...)`. | `admin/db.py:625-641`, `public/db.py:86-88` |
| 7 ◐ | No admin thread moderation; public threads/replies stay `pending` forever → community module shows nothing. | `api/admin/__init__.py` |
| 8 ◐ | No `/admin/test-signups` status endpoints; signups only created and counted. | — |
| 9 ◐ | No notifier (SMTP/Mailpit/`ADMIN_NOTIFY_EMAIL`); inbox lacks signups/threads. "Admin notified → replies → author gets it" ends at a DB column. | `config.py`, `schemas/admin/inbox.py` |
| 10 ◐ | Grant generator and Middleman card are templates (`[uzupełnij]`), not LLM. Accepting an idea doesn't create a draft innovation. | `drafts.py:27-43`, `admin/db.py:405-410` |

## P1 — security (demo exposure)

| # | Finding | Where | Fix |
|---|---|---|---|
| 11 ✅ | Compose defaults `DEBUG=true` + `ADMIN_AUTH_DISABLED=true`: `/admin/*` open to anyone on the venue wifi, `/docs` served, and `FastAPI(debug=True)` returns tracebacks on 500. Fallback password `1234`. | `docker-compose.yml:44-49`, `main.py:12`, `auth.py:45` | default auth on; `FastAPI(debug=False)`, keep `settings.debug` only for docs |
| 12 ✅ | CSV exports don't escape formulas; citizen `text`/`location` like `=HYPERLINK(...)` executes in Excel. | `services/admin/csv_export.py:15` | prefix `'` to cells starting `= + - @ \t \r` |
| 13 ◐ | Login lockout keyed on username only, checked before password → anyone can lock out the single admin; `_attempts` never pruned/reset. | `services/admin/auth.py:57-59`, `auth_store.py:42` | key on username+IP, reset on success |
| 14 ◐ | No rate limit anywhere (docs claim one). `/support` can be spammed to skew criticality; `/match` stores a row per call. | `api/public/__init__.py:6` | small in-memory per-IP dependency on public router |
| 15 ◐ | Problem-report text shown publicly (`similar_reports`, `GET /problem-reports/{id}`) with no moderation — profanity/PII from live demo leaks to next user. | `public/db.py:122-140` | only show replied/approved reports |
| 16 ◐ | Trends have no small-count suppression (per week×area×city), bypassing the `<5` rule used elsewhere. | `admin/db.py:552-576` | apply `MIN_LOCATION_PROBLEM_REPORTS` or drop `city` |

## P2 — upload path (rag `/embed/pdf`)

| # | Finding | Where | Fix |
|---|---|---|---|
| 17 ◐ | Embed failure only logged; draft stays `draft` forever, no failure state, no retry. Docs promise `POST /admin/innovations/{id}/pdf` + `indexed` filter — neither exists. | `innovation_upload.py:89-96` | add `/{id}/pdf` re-embed from saved file (idempotent on rag side) |
| 18 ◐ | Re-upload mints a new id each time → duplicates in `/match` if both embed. | `innovation_upload.py:76` | resolved by #17 |
| 19 ◐ | `uploads` volume declared but not mounted on `api` → PDFs lost on recreate, re-embed impossible. | `docker-compose.yml` | mount volume at `/data/uploads` |
| 20 ◐ | Status race: manual `/publish` works on never-embedded drafts; background `publish()` overrides an admin's `unpublish`. | `admin/db.py:140-144`, `innovation_upload.py:94` | `UPDATE … WHERE status='draft'` |
| 21 ◐ | `RagClient` 300s timeout applies to connect too; httpx errors not mapped. | `clients/rag.py:11-15` | `httpx.Timeout(300, connect=5)`; map to 502/503 |
| 22 ◐ | rag `/embed/pdf` is `async def` doing sync work → blocks rag's loop (incl. `/query`, healthcheck) during an upload. rag is frozen → operational: upload demo content before the demo. | `rag/app/main.py:156-177` | — |

## P3 — correctness, low

- ✅ NUL bytes accepted by Pydantic, rejected by Postgres → 500 on any text write (+ traceback via #11). Shared validator or map `DataError` → 422.
- ✅ Mock vs Db divergence on feedback `test_signup_id`: Db 404s malformed id, mock returns 201. Map to 422; make mock validate.
- ◐ `is_critical` is per-area but stamped on every report in the area → `?is_critical=true` / inbox lists hundreds. Inbox critical ignores `since`.
- ◐ `/match?test_signup=true` with zero matches returns 200, nothing stored.
- ◐ Library pagination orders by `title` only → add `id` tiebreak. `ilike` without escaping `%`/`_`.
- ◐ Admin problem-report list includes `hidden` rows but schema doesn't expose `hidden`.
- ◐ `read(max+1)` runs after Starlette spooled the whole body → no real request-size cap.
- ◐ `date_trunc('week')` in DB tz vs `this_week` in UTC (fine on default image).
- `map_domain_errors` doesn't cover `OperationalError` (DB down → 500 instead of 503).

## Docs drift (fix in same PR per project rule)

- `requirements-traceability.md` rates R1 full; R10/R12 notifier, Mailpit, rate limit, `/admin/threads*`, `/admin/test-signups*`, `/admin/generated-documents`, `/{id}/pdf`, `/problem-reports/{id}/hide`, `indexed` filter — documented, not implemented.
- `architecture.md` still describes rag tag filtering (removed in e65b973); shows Ollama, code has Gemini; "accepting idea creates draft" false; challenge area from "LLM classification" is actually top-match; "city spellings rejected" but `city` is free `str`; stale English-only embedding risk.
- `rabbitmq` still in compose, unused.

## Test gap

No test runs `Db*Service` against Postgres. One `pytest` fixture with a throwaway Postgres (compose `db` or testcontainers) applying `sql/*.sql` would have caught #1-4, #6, and the mock divergences. Highest-ROI test investment.

## Recommended order

1. #1-4 (one compose/init PR) — makes `docker compose up` actually work.
2. #11, #12 — 10-minute security fixes.
3. #5 + #4 — wire `/match` to rag `/query` and use its `answer`; this is the mandatory criterion.
4. #6 gaps fix, #7 thread moderation, #17/#19 re-embed.
5. Docs truth pass — cut claims that won't ship.
