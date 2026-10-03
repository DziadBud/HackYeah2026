# Requirements traceability

Maps each requirement from `documentation/knowledge-base/CRITERIA-Wojewodztwo-Malopolskie-HUBMI.md` to the part of [architecture.md](architecture.md) that implements it. M = mandatory, S = extra module (+5% each), X = cross-cutting, D = deliverable.

## R1 Matchmaking spoleczny (M, 10%)
- **Where:** `POST /match` (§3) calling rag `POST /query`; `innovations` + `innovation_chunks` (§6).
- **How:**
  - rag retrieval over published rows, top 3 in rag's order, plus rag's one LLM-written `answer` for the whole result (no per-innovation reason)
  - 3 similar problem reports are returned too (pg_trgm, same city first)
  - a per-IP rate limit guards LLM spend
- **Done when:** the 8 queries in `documentation/sample-data/sample-matchmaking-queries.md` return the expected id in the top 3.

## R2 Zasobnik wiedzy (S)
- **Where:** public `GET /innovations`, `GET /innovations/{id}`; `/admin/reports/*` (§5).
- **How:**
  - the library lists `innovations` rows tagged `type:innovation`; films are linked through `page_url`
  - ROPS reports and the Mapa Wyzwan are `type:report` rows embedded with `/embed/pdf`; "ask the report" over their chunks is deferred until they are embedded
  - the admin uploads a PDF per innovation; match-api sends it to rag `/embed/pdf` in a background task and publishes the innovation once indexed
  - aggregated needs and trends exist only under `/admin/reports/*`
- **Gap:** `/embed/pdf` stores no page numbers, so report answers can't cite pages.

## R3 Kreator pomyslow (S)
- **Where:** `POST /ideas`, `ideas` and `grant_calls` tables, `/admin/ideas`, `/admin/grant-calls`, `generated_documents`.
- **How:**
  - idea card = summary, essence, target group, stage, plus optional Canvas answers in `ideas.social_canvas`
  - an optional email gets the status change and the `admin_reply`
  - an accepted idea becomes a draft innovation; it is matchable once the admin uploads its PDF and rag embeds it
  - grant application generator: while a `grant_calls` row is open, the LLM fills that call's `sections` from the idea card and stores the draft in `generated_documents` (`kind = grant_application`)
  - assistant and visualisation: stretch

## R4 Tester innowacji (S)
- **Where:** `POST /match?test_signup=true`, `test_signups`, `feedback` ([.claude/designs/innovation-testing.md](../../.claude/designs/innovation-testing.md)).
- **How:**
  - testing is part of matching: with `?test_signup=true` and an email, the user volunteers to test the innovations matched for their problem (one `test_signups` row each, linked to the problem report); the admin accepts, rejects or marks `completed`, and the applicant is emailed
  - ratings and comments go to `feedback` (per-IP rate limited); improvement proposals are comments; optional `test_signup_id` marks feedback from a real tester
  - the admin sees the rating average, count, star distribution, comments and signups by status per innovation (`GET /admin/innovations/{id}/stats`)

## R5 Platforma komunikacji (S)
- **Where:** `admin_reply` on `problem_reports` and `ideas`; `threads` + `thread_replies` on each innovation ([.claude/designs/community-threads.md](../../.claude/designs/community-threads.md)); the email notifier (§4).
- **How:**
  - the admin answers an idea (emailed if it has an email), or answers a problem report once on its public page
  - per-innovation community threads: public create starts as `pending`, ROPS moderates to `published` / `hidden` (`GET /admin/threads?status=pending`, `POST /admin/threads/{id}/status`, `POST /admin/threads/replies/{id}/status`); flat replies with role `kind` (public replies are always practitioner; expert / mentor / admin set by ROPS)
  - mentors are admins (or reply with `kind = mentor`)
  - no public accounts

## R6 Panel administratora (S)
- **Where:** `/admin/*` behind the admin session (§4, §5).
- **How:**
  - login
  - innovation create from a PDF (file saved, draft row, background call to rag `/embed/pdf`, published on success), metadata edit (`title`, `summary`, `challenge_areas`, `city`, `page_url`), publish/unpublish, feedback counts
  - innovation list with stats per innovation: matches (total, 7d trend, by week, area and city), people reached, testers, ratings, matched problems (`/admin/reports/innovations`, `/admin/innovations/{id}/stats`)
  - inbox: new ideas, problem reports, critical problem reports, signups, pending threads / replies
  - replies, idea status, test signup status, thread moderation, grant call open/close, generated-document list, reports with CSV

## R7 Middleman innowacji (S)
- **Where:** `POST /middleman` (match-api), `generated_documents` (`kind = middleman`).
- **How:** input = innovation id + institution type + its needs. The LLM drafts a service card from that innovation's row and chunks only; unknown figures are marked "to estimate". The draft is stored so the institution and the admin can reopen it.

## R8 Accessibility, WCAG 2.1 AA (X, 20%)
- **Backend part:** plain-language Polish validation errors, no time limits on public flows, text answers suitable for read-aloud.
- **Frontend part:** contrast, keyboard navigation, labels, text-size toggle, axe + keyboard-only run (not covered here).

## R9 Scalability (X)
- **Where:** §1, §7.
- **How:**
  - match-api is stateless apart from admin sessions held in memory
  - retrieval and embedding live in rag; pgvector HNSW index
  - the per-IP rate limit protects LLM spend
- **Next steps:** admin sessions in Postgres for more than one replica, then read replicas (§8).

## R10 Integration and automation (X)
- **Where:** admin inbox (§5), email notifier (§4), `grant_calls`.
- **How:** the inbox surfaces new items (ideas, problem reports, signups, pending threads). The optional email notifier (background task after commit, at-most-once, Mailpit in the demo) emails the admin on new ideas, problem reports and pending threads, and authors on replies, status changes and published threads. Grant calls have an open/close switch. An outbox and webhooks for the grant DB are deferred (§8).

## R11 Data security, no real personal data (X)
- **Where:** §4, §6.
- **How:**
  - no public accounts or passwords, no IP stored
  - an email only when given with consent, stored on the item / thread
  - one shared admin login from env (argon2id-hashed at startup), revocable HttpOnly session cookies, login rate limit, secrets from env
  - city picked from a list, free text length-capped, synthetic demo data only
  - problem reports and threads can be `hidden` by an admin
  - user text is data, never instructions

## R12 Fast admin notification and reply path (jury question)
- **Where:** inbox + replies (§5), threads moderation, email notifier (§4).
- **How:**
  1. Every new idea, problem report or pending thread appears in `GET /admin/inbox?since=`, and the admin gets an email.
  2. The admin sets `admin_reply`, or publishes / hides a thread.
  3. An author with an email gets it by email; a problem report reply is also on its public page for everyone who pressed "mnie też".

## R13 Match relevance (jury question)
- **Where:** §3.
- **How:** rag retrieval with deterministic ranking; the LLM only explains. The 8 sample queries plus 15-20 realistic Polish queries are kept as a regression list and slide evidence.
- **Risk:** the English-only embedding model (§11).

## R14 Originality (X, 10% bonus)
- **Where:** problem reports + support + critical report (§3, §5).
- **How:**
  - every problem becomes a counted problem report
  - users press "mnie też" on similar reports instead of writing again
  - criticality = problem reports x distinct cities x 7d growth ratio feeds an admin-only radar
  - the gaps report shows needs with no matching innovation

## R15 Submission package and running-cost estimate (D)
- **How:**
  - cost sheet: small VM or container + managed Postgres with pgvector, local embeddings (no per-call cost), LLM pay-per-call limited by rate limits, SMTP relay (free tier), ~0.25 FTE content editor, a one-off accessibility audit
  - demo is `docker compose up`; diagrams from `architecture.md` go on the slides

## Coverage

| Req | MVP depth |
|---|---|
| R1 | full |
| R2 | library, SQL reports; ask-report deferred until report PDFs are embedded |
| R3 | idea card + Canvas answers; generator for one fictional grant call (stored) |
| R4, R5, R7 | thin, working end to end (threads moderated; Middleman stored) |
| R6 | CRUD, inbox, replies, thread moderation, reports, per-innovation stats |
| R8 | needs frontend work |
| R9-R12 | by design; inbox + optional email notifier |
| R13, R14 | regression suite; support + critical report |
| R15 | documents |

Gaps: the RULES PDF is unread and may add constraints; innovation data beyond the 8 samples depends on the ROPS answer; no page citations for reports.
