# BE-08 Db-path tests + matchmaking regression

**Criterion:** R1/R13 (trafność), R15 (slide evidence).
**PR:** separate, small

## Problem
All API tests override deps with `services/*/mock.py`; no `Db*Service` SQL runs in tests. The demo runs the Db path. Match relevance has no measured number.

## Fix
- Smoke tests against compose Postgres (marked `integration`) for `/match`, `/ideas`, `/threads`, `/admin/reports/*`.
- `scripts/match_regression.py`: runs `documentation/sample-data/sample-matchmaking-queries.md` (+15 Polish queries) against `/match`, prints hit@3. Watches the English-only embedding risk.

## Done when
`make test-integration` green; hit@3 number on a slide.
