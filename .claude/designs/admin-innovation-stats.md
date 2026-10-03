# Admin innovation stats (Panel administratora, R6 + R4 + R2)

**Status:** accepted · **Date:** 2026-10-03

## Goal
ROPS staff open `/admin` and see, for every innovation, whether it reaches people: how often it is proposed, for which problems and where, who wants to test it and how it is rated. The brief asks for a panel to verify and share knowledge (module VI), tester feedback (IV) and needs aggregated into trends visible only to the admin (II).

Non-goals: stored snapshots, page-view analytics, per-user tracking.

## Metrics
A **match** is a problem report whose top 3 (`problem_reports.matched_innovation_ids`) contains the innovation.

| Metric | Definition |
|---|---|
| matches total / last 7 days / previous 7 days | count of matching problem reports by `created_at` |
| matches by week | last 6 weeks, oldest first, zero weeks included |
| people reached | matching problem reports + their `support_count` ("mnie też") |
| by challenge area / by city | `challenge_area` and city of those reports; a city with fewer than 5 is shown as "too few to display" (same rule as the locations report) |
| testers | `test_signups` by status: applied (waiting), accepted, rejected |
| rating | `feedback`: average, count, distribution 1-5, newest comments (improvement proposals) |
| last match, latest problems | newest matching problem reports |

## API
- `GET /admin/reports/innovations?format=json|csv`: one flat row per innovation (drafts included, zeros when never matched), sorted by matches.
- `GET /admin/innovations/{id}/stats`: the same numbers plus breakdowns, ratings and the latest problems.

Both are SQL on read over existing tables, like the other reports. match-api serves them from the mock service until the db-backed services land.

## UI
- `/admin`: summary tiles, filters (search, status, area, sort by matches / 7-day growth / waiting testers / rating / name), a card per innovation with its numbers and "needs attention" hints (draft, testers waiting, rating under 3.5, published but never matched).
- `/admin/innowacje/{id}`: the full breakdown.
- Trend is spelled out with an icon and a signed number, never colour alone.

## Deferred
| Idea | Add when |
|---|---|
| date range picker | ROPS needs more than 6 weeks |
| map of cities | the city list grows past a handful |
| per-innovation CSV with breakdowns | someone asks for it |
