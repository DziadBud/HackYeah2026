# FE-06 Public problem-report page

**Criterion:** R5, R12 (reply path for authors without email), R14.
**PR:** `feat/frontend-modules` · respects BE-06

## Problem
`GET /problem-reports/{id}` has no page; the ROPS reply is unreachable for authors without email.

## Fix
`/problem-reports/[id]`: text, "mnie też" count + button, ROPS reply. Chat shows the link after a match ("Sprawdź odpowiedź ROPS tutaj").
