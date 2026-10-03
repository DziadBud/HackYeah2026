# BE-05 Gaps report always empty

**Criterion:** R2 admin trends, R14 originality ("needs with no innovation").
**PR:** `feat/tester-admin`

## Problem
`services/admin/db.py:611-627` selects reports with 0 matches, then filters `if _area(r.challenge_area)`. `challenge_area` is only set from the top match (`public/db.py`), so it is always `None` for those rows → empty list.

## Fix
`GapRow.challenge_area: ChallengeArea | None`, drop the filter. No LLM classification.

## Done when
A `/match` with no hits appears in `GET /admin/reports/gaps`; Db-backed test.
