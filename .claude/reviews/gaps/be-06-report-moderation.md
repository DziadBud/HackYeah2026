# BE-06 Public problem-report text is unmoderated

**Criterion:** R11 (data security, no personal data).
**PR:** `feat/tester-admin`

## Problem
Any `/match` text is shown to other users in `similar_reports` and `GET /problem-reports/{id}`. Profanity or PII typed during the demo leaks to the next user.

## Fix
Show publicly only reports that have an `admin_reply` and are not `hidden`. Similar-report count ("X osób zgłosiło podobny problem") can still use all rows.

## Done when
Fresh report not visible in another user's `similar_reports` until the admin replies.

## Docs
`architecture.md` §3, traceability R11/R14.
