# Requirements traceability

Maps each requirement from `documentation/CRITERIA-Wojewodztwo-Malopolskie-HUBMI.md` to the part of [architecture.md](architecture.md) that implements it. M = mandatory, S = extra module (+5% each), X = cross-cutting, D = deliverable.

## R1 Matchmaking spoleczny (M, 10%)
- **Where:** `POST /match` (§3), `innovation` + `chunk` (§6), data from ingest (§2).
- **How:** hybrid retrieval (full-text + trigram + pgvector, rank fusion) over published innovations, top 5 with an LLM-written reason built only from retrieved rows. 3 similar existing problem reports are returned too (same location first, else same challenge area).
- **Done when:** the 8 queries in `documentation/sample-data/sample-matchmaking-queries.md` return the expected id in the top 3.

## R2 Zasobnik wiedzy (S)
- **Where:** public `GET /innovations`, `GET /challenge-areas`; `GET /ask-report`; `/admin/reports/*` (§5).
- **How:** library from `innovation` rows with `video_url`; the 8 challenge areas from the Mapa Wyzwan PDF; reports and Canvas chunked and embedded, "ask the report" answers from retrieved chunks with page references. Admin edits embed inline, so updates are instant. Aggregated needs and trends exist only under `/admin/reports/*` (SQL on request), never public.

## R3 Kreator pomyslow (S)
- **Where:** `POST /ideas`, `idea` and `grant_call` tables, `/admin/grant-calls`.
- **How:** idea card = summary, target group, stage, plus optional Canvas answers in `idea.social_canvas`. The submitter gets an `access_token` link to see status and the admin reply. Grant application generator: while `grant_call.open`, the LLM fills the call's `sections` from the idea card. Assistant and visualisation: stretch.

## R4 Tester innowacji (S)
- **Where:** `POST /innovations/{id}/feedback` (`kind = rating | test_signup`), `feedback` table.
- **How:** star rating, comment and optional "I want to test" flag; admin sees counts per innovation. Thin by design.

## R5 Platforma komunikacji (S)
- **Where:** `admin_reply` on `idea` and `problem_report`, `/admin/ideas/{id}/reply`, `/admin/problem-reports/{id}/reply`.
- **How:** admin answers an idea through the submitter's private link, or answers an problem report once on its public page for everyone who pressed "me too". Mentors are admins. No accounts.

## R6 Panel administratora (S)
- **Where:** `/admin/*` and `/ingest/*` behind the admin session dependency (§4, §5).
- **How:** login, innovation add/edit/publish/unpublish with feedback counts (R4), imports with job status, inbox (new ideas, new and critical problem reports), idea and problem report replies, grant call open/close, reports.

## R7 Middleman innowacji (S)
- **Where:** `POST /middleman` (match-api).
- **How:** input = innovation id + institution type (gmina, CUS, NGO). The LLM drafts a service card (who pays, who decides, channels, partners, fixed vs variable cost) from that innovation's stored fields only; unknown figures are marked "to estimate". One prompt, one card.

## R8 Accessibility, WCAG 2.1 AA (X, 20%)
- **Backend part:** plain-language Polish validation errors, no time limits on public flows, captions/transcripts stored with innovation videos, text answers suitable for read-aloud.
- **Frontend part:** contrast, keyboard navigation, labels, text-size toggle, axe + keyboard-only run (not covered here).

## R9 Scalability (X)
- **Where:** §1, §7.
- **How:** match-api is stateless and scales horizontally; pgvector HNSW index; heavy imports live in a separate service; IP rate limiting protects LLM spend. Next steps are read replicas, then a queue for ingest (§8).

## R10 Integration and automation (X)
- **Where:** admin inbox (§5), email notifier (§4), `grant_call` table.
- **How (MVP):** the inbox surfaces new ideas, new and critical problem reports, plus one optional email to the admin (SMTP from env, BackgroundTasks, no-op if unset) on new ideas and first critical crossing. Grant calls have an open/close switch. Webhooks, outbox and worker (grant DB integration) are deferred (§8) and would be more notifiers on the same events.

## R11 Data security, no real personal data (X)
- **Where:** §4.
- **How:** no public accounts; salted `ip_hash`, raw IPs never stored; per-admin accounts with argon2id hashes, revocable HttpOnly session cookies, login rate limit, secrets from env; location picked from a list; free-text length capped; seed/synthetic data only; user text is data, never instructions.

## R12 Fast admin notification and reply path (jury question)
- **Where:** admin inbox + replies (§5), email notifier and access-token link (§4).
- **How:** every new idea or problem report appears in `GET /admin/inbox?since=`; critical problem reports are flagged there, and an email goes out on new ideas and first critical crossing. The admin replies; the submitter sees it on their link. One problem report reply is stored on the problem report and shown to everyone who created or supported it (whole cluster); no push without accounts.

## R13 Match relevance (jury question)
- **Where:** §3.
- **How:** keyword + semantic retrieval fused, deterministic ranking, LLM only explains. The 8 sample queries plus 15-20 realistic Polish queries are kept as a regression list and slide evidence.

## R14 Originality (X, 10% bonus)
- **Where:** problem reports + support + critical report (§3, §5).
- **How:** every problem becomes a counted problem report. Users see similar problem reports and press "me too" instead of writing again; criticality = problem reports x distinct locations x 7d growth ratio feeds an admin-only radar, and the gaps report shows which innovations ROPS is missing.

## R15 Submission package and running-cost estimate (D)
- **How:** cost sheet from the design: small VM or container + managed Postgres with pgvector, local embeddings (no per-call cost), LLM pay-per-call limited by IP rate limits, ~0.25 FTE content editor, a few hours per week of admin triage, one-off accessibility audit. Demo is `docker compose up`; diagrams from `architecture.md` go on the slides.

## Coverage

| Req | MVP depth |
|---|---|
| R1 | full |
| R2 | library, ask-report, SQL reports |
| R3 | idea card + Canvas answers; generator for one fictional grant call |
| R4, R5, R7 | thin, working end to end |
| R6 | CRUD, imports, inbox, replies, reports |
| R8 | needs frontend work |
| R9-R12 | by design; inbox + one optional email; webhooks and other channels deferred |
| R13, R14 | regression suite; support + critical report |
| R15 | documents |

Gaps: the RULES PDF is unread and may add constraints; innovation data beyond the 8 samples depends on the ROPS answer.
