# FE-02 Rating form on innovation page

**Criterion:** R4.
**PR:** `feat/frontend-modules`

## Problem
`POST /innovations/{id}/feedback` exists; `lib/api.ts` has no call; page only shows `rating_avg`.

## Fix
- Stars (radio group, keyboard accessible) + comment + "co poprawić" field.
- Read `?test_signup=` and send `test_signup_id`; show "Ocena testera" note.
