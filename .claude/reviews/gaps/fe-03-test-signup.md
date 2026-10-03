# FE-03 Real test signup

**Criterion:** R4.
**PR:** `feat/frontend-modules` · depends on BE-04

## Problem
`components/innovation/TestSignup.tsx` links to `/?wniosek=1` (idea form), so tester requests land in the ideas inbox.

## Fix
Inline form: email, consent, optional institution type + note → `POST /innovations/{id}/test-signups`. Confirmation text says what happens next.
