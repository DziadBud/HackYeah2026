# FE-01 Admin: thread moderation + test signups + inbox counters

**Criterion:** R4, R5, R6.
**PR:** `feat/frontend-modules` · depends on BE-01, BE-04

## Problem
`AdminPanel.tsx` has problem reports, ideas, reports, grant calls. No UI for `GET /admin/threads?status=pending`, thread/reply status, test signups. Threads stay `pending` → community looks empty.

## Fix
- Moderation queue: thread/reply with publish / hide.
- Test signups table per innovation: accept / reject / complete.
- Inbox counters incl. `pending_threads`, `new_test_signups`.
