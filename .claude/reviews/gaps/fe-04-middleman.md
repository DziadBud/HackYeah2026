# FE-04 Middleman flow

**Criterion:** R7 (+5%).
**PR:** `feat/frontend-modules` · better with BE-03

## Problem
`POST /middleman` never called. "Jestem z instytucji" only prefills the chat.

## Fix
- Innovation detail: "Dostosuj do mojej instytucji" → institution type + needs → `POST /middleman`.
- Chat action "Jestem z instytucji": after a match, offer the same on each card.
- Render the card printable (print CSS), copy button.
