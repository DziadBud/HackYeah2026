# Staff review: gaps vs. HubMI requirements — 2026-10-04

HEAD `2e099d8`. Supersedes the open items of `backend-review.md`; per-gap files in `gaps/` (their P0 compose/SQL items are fixed).

## Verdict

Matchmaking (R1) and the admin panel (R6) work end to end. Every other module has a backend that the **frontend never calls**, or a backend that is a template, not AI. Points are lost on "+5% per *working* module", not on missing tables.

| Module | Backend | Frontend | Jury sees it working? |
|---|---|---|---|
| R1 Matchmaking | rag `/query`, ranked, LLM answer | chat, wired | yes |
| R2 Zasobnik | library + PDF | library list/detail | yes (no reports/films/education) |
| R3 Kreator | idea card, grant-application = **template `[uzupełnij]`** | idea form only; no grant generator, no open-call view | half |
| R4 Tester | signups created, **no admin status endpoints**, feedback POST exists | "Zgłoś się do testowania" opens idea form; **no rating form** | no |
| R5 Komunikacja | threads + moderation, admin replies | threads shown; **no admin moderation UI** | no (threads stay `pending`) |
| R6 Admin | full | dashboard, innovations, reports | yes |
| R7 Middleman | `POST /middleman` = **template** | **not called** ("Jestem z instytucji" just prefills chat) | no |
| R10/R12 notify → reply | **no notifier**; inbox lacks threads/signups | — | no: the explicit jury question has no demoable answer |

## Backend — must do (ordered by points per hour)

1. **Notifier + Mailpit (R10, R12).** `SmtpNotifier` on stdlib `smtplib`, sent from `BackgroundTasks` after commit.
   - at-most-once: a lost mail is acceptable because the inbox is the source of truth. Outbox + worker (at-least-once) only if mails must not be lost — not now.
   - triggers: new idea / problem report / pending thread → `ADMIN_NOTIFY_EMAIL`; reply / status / published thread → author; grant call opened → idea authors with consent.
   - inbox: add `pending_threads`, `new_test_signups`.
   - this is the scripted answer to "how is the admin notified and how does the reply reach the author".
2. **Rate limit (R11, hard requirement).** Per-IP sliding window as a dependency on the public router (`/match`, `/middleman`, grant-application, all public writes), 429 with Polish text (frontend already handles 429).
   - in-memory = per-replica; Redis when >1 replica. One container now, so in-memory.
3. **LLM for grant generator (R3) and Middleman (R7).** `GeminiClient` exists and is unused. Replace `drafts.grant_draft` / `drafts.middleman_card` with one grounded prompt each (input: idea card / innovation row + its rag chunks; output: sections; unknown numbers → "do oszacowania"). Keep the template as fallback on `LlmError` so the demo never breaks.
   - recommendation: Gemini Flash (better Polish, cents per call, rate-limited by #2); Ollama remains the no-key fallback. Put the per-call cost in the cost sheet.
4. **Tester admin side (R4).** `GET /admin/test-signups?innovation_id=&status=`, `POST /admin/test-signups/{id}/status`; email on change; the accepted mail carries `{WEB_URL}/innovations/{id}?test_signup={signup_id}` (uuid = token) for the rating form.
5. **Gaps report always empty (R2/R14).** `admin/db.py:611-627` filters out every row because `challenge_area` is only set from a top match. Make `GapRow.challenge_area` optional and drop the `if _area(...)` filter. The "needs with no innovation" radar is our originality pitch — currently blank.
6. **Public problem-report text unmoderated (R11).** Shown in `similar_reports` and `GET /problem-reports/{id}`. A jury member typing profanity/PII leaks to the next user. Show only reports that are replied or older than N minutes and not `hidden`; cheapest: only replied ones.

## Backend — should do

- CSV formula injection: prefix `'` on cells starting with `= + - @ \t \r` (`csv_export.py:15`). 5 minutes.
- Login lockout keyed on username only → anyone can lock out the single admin. Key on username+IP, reset on success.
- Mount `uploads` volume on `api` at `/data/uploads` (declared, not mounted) so PDFs survive recreate.
- Compose defaults `ADMIN_AUTH_DISABLED=true`, password `1234`: fine on a laptop, not on venue wifi. Default auth on for the hosted demo URL.
- Drop RabbitMQ from compose: nothing uses it, it costs RAM and a line in the cost sheet (R15 "simple maintenance").
- Tests only exercise `mock.py`; add one smoke test per `Db*Service` against the compose Postgres for `/match`, `/ideas`, `/threads`. The demo runs the Db path, not the mock.
- Matchmaking regression: script that runs the 8 sample queries (+15 Polish) against `/match` and prints hit@3. It's slide evidence for "trafność" and catches the English-only embedding risk (R13).

## Backend — defer (state cost)

- Ask-a-report / page citations (R2 depth): rag is frozen; costs R2 depth only.
- Accept idea → draft innovation: needs a PDF anyway; remove the claim from docs.
- Admin sessions in Postgres (multi-replica): talking point for scalability slide, not code.

## Frontend — wire what exists (highest value)

1. **Admin moderation + tester queue.** Add to `AdminPanel`: pending threads/replies (publish/hide), test signups (accept/reject/complete), inbox counters. Without it R4/R5 are invisible.
2. **Rating form on the innovation page.** `POST /innovations/{id}/feedback` (stars + comment, improvement proposal). Read `?test_signup=` and send `test_signup_id`.
3. **Tester signup for real.** Replace `TestSignup.tsx` redirect-to-idea-form with: email + consent → `POST /match?test_signup=true` (or a small dedicated endpoint if we want sign-up without a problem text — recommend adding `POST /innovations/{id}/test-signups` server-side, one row, no fake problem report).
4. **Middleman flow.** "Jestem z instytucji" → institution type + needs + chosen innovation → `POST /middleman` → printable service card. On innovation detail: "Dostosuj do mojej instytucji".
5. **Grant generator.** `GET /grant-calls` banner when a call is open; after idea submit offer "Przygotuj wniosek" → `POST /ideas/{id}/grant-application`, render sections, copy/print. Hidden when no call is open (that conditionality is a stated requirement).
6. **Public problem-report page** `/problem-reports/[id]`: text, "mnie też" count, ROPS reply. It is the reply path for authors without email.

## Frontend — quality / accessibility (20%)

- Routes in English per agreed convention: `/innowacje` → `/innovations`, `/admin/zgloszenia` → `/admin/problem-reports`; mail links already use `/innovations/{id}`.
- Silent demo fallback: on network/5xx `Chat` answers from `demo-data` (marked `demo`). Keep for resilience, but make the label prominent and log it; otherwise a broken backend in the demo looks "fine" until a jury member reads an off answer.
- Admin panels fall back to `admin-mock` on error — same risk; show an error banner instead in non-demo builds.
- Run axe + keyboard-only pass on chat, idea form, innovation page, admin; check focus after chat answer (announce via `aria-live`), form error summaries, 44px targets, high-contrast mode in admin charts.
- Plain-language pass: "innowacja społeczna", "JST", "Canvas" need a one-line explanation inline for seniors.
- Originality: surface the "mnie też" counter and "X gmin ma ten sam problem" on the match result — it's our differentiator and is barely visible.

## Docs to update with the code

`architecture.md` (notifier, rate limit, new endpoints), `requirements-traceability.md` (R4/R5/R7 depth, remove "per-IP rate limit guards" until it exists — the doc currently claims it), `documentation/frontend/architecture.md`, `.claude/designs/innovation-testing.md`.

## Suggested PRs

1. `feat/notifier-rate-limit` — backend 1, 2, inbox fields, CSV, lockout, uploads mount.
2. `feat/llm-drafts` — backend 3 (Gemini + template fallback).
3. `feat/tester-admin` — backend 4 + direct test-signup endpoint, gaps fix (5), report moderation (6).
4. `feat/frontend-modules` — frontend 1-6.
5. `chore/a11y-pass` — accessibility + routes + fallback banners.
