# BE-02 Per-IP rate limit

**Criterion:** R11; hard req "rate limits on LLM endpoints".
**PR:** `feat/notifier-rate-limit`

## Problem
No rate limit anywhere (`api/public/__init__.py:6` comment says "once it lands"). Traceability R1/R4/R9 claim one. `/support` can be spammed to skew criticality; `/match` stores a row and calls the LLM per request.

## Fix
- In-memory sliding window per IP as a router dependency on the public router; stricter bucket for `/match`, `/middleman`, `/ideas/{id}/grant-application`.
- 429 with Polish message (frontend `Chat.tsx` already handles 429).
- Trade-off: per-process state, wrong with >1 replica → Redis when scaled. One container now.
- Behind a proxy: read `X-Forwarded-For` only when a trusted-proxy setting is on.

## Done when
N+1th request in window → 429; tests for each bucket.

## Docs
`architecture.md` §4, traceability R1/R9/R11.
