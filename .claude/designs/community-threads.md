# Community threads (Platforma aktywnej komunikacji, R5)

**Status:** accepted · **Date:** 2026-10-03

## Goal
Each published innovation has an open discussion space: residents, NGOs, JSTs and mentors ask questions, share deployment tips and get answers. The brief's module V asks for direct dialogue and cross-sector partnerships; the innovation detail UI already shows threads. Hackathon scope: flat threads per innovation, no accounts, ROPS moderation.

Non-goals:
- nested reply trees
- user profiles or private DMs
- per-user like tables (a counter is enough, same as "mnie też")

## Design

### Flow
```
public:  GET  /innovations/{id}/threads          -> published threads + published replies
         POST /innovations/{id}/threads {title, body, author_label, email?}
              -> status pending; admin notified
         POST /threads/{id}/replies {body, author_label, email?}  (always practitioner)
              -> status pending (admin/mentor replies may be published immediately)
admin:   inbox shows pending threads / replies
         GET  /admin/threads?status=&innovation_id=
         POST /admin/threads/{id}/status {published|hidden}
         POST /admin/threads/replies/{id}/status {published|hidden}
```

No public accounts: the author is a free-text `author_label` (e.g. "Jan Kowalski (OPS Zakliczyn)") plus an optional `email` for moderation and "your thread was published" mail. Mentors and ROPS staff answer as `kind = mentor|admin` from the admin panel (or as a normal reply marked admin).

### Data model
```sql
threads(
  id uuid pk,
  innovation_id text fk innovations,
  title text,
  body text,
  author_label text,
  email text null,
  status text,           -- pending | published | hidden
  helpful_count int default 0,
  created_at, updated_at
)

thread_replies(
  id uuid pk,
  thread_id uuid fk threads,
  body text,
  author_label text,
  email text null,
  kind text,             -- practitioner | expert | mentor | admin
  status text,           -- pending | published | hidden
  created_at
)
```

## Failure modes
| Failure | Mitigation |
|---|---|
| spam threads / replies | per-IP rate limit, length caps, default `pending` |
| PII pasted into body | admin can `hidden`; seed data stays synthetic |
| email send fails on publish | logged; the public page is the source of truth |

## Rollout
1. Tables + public list/create + admin publish/hide.
2. Wire `frontend/components/innovation/Community.tsx` to the API (drop local-only state for persistence).
3. Inbox badge for pending items + optional notify email.

## Deferred
Nested replies, reactions beyond `helpful_count`, and moderated edit history: add when one flat list is not enough (architecture §8).
