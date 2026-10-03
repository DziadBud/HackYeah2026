# FE-05 Grant generator + open-call banner

**Criterion:** R3 (+5%); generator only while a call is open (stated requirement).
**PR:** `feat/frontend-modules` · better with BE-03

## Problem
`GET /grant-calls` and `POST /ideas/{id}/grant-application` never called.

## Fix
- Banner on home when a call is open.
- After idea submit (`IdeaForm`), if a call is open: "Przygotuj wniosek do naboru X" → render sections, copy/print.
- Hidden when no call open.
