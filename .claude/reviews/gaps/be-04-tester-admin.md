# BE-04 Tester admin side + direct signup

**Status:** admin list + status endpoints, tester mails and one-click rating from the mail (`/ratings/{signup_id}`) done on `feat/notifier`. Open: direct `POST /innovations/{id}/test-signups`.

**Criterion:** R4 (+5%).
**PR:** `feat/tester-admin`

## Problem
`test_signups` rows are created via `/match?test_signup=true` but no admin endpoint lists or changes them. Public UI can't sign up without writing a problem text.

## Fix
- `GET /admin/test-signups?innovation_id=&status=`
- `POST /admin/test-signups/{id}/status {accepted|rejected|completed}` → email (BE-01).
- Accepted mail carries `{WEB_URL}/innovations/{innovation_id}?test_signup={signup_id}`; uuid acts as token for the rating form (`feedback.test_signup_id`).
- `POST /innovations/{id}/test-signups {email, consent, institution_type?, note?}` — one row, no fake problem report. `test_signups.problem_report_id` must be nullable (check `004_test_signups.sql`; new migration if not).

## Done when
Sign up from innovation page → admin sees it → accept → tester gets link → rating stored with `kind='test_signup'`.

## Docs
`.claude/designs/innovation-testing.md`, `architecture.md`, traceability R4.
