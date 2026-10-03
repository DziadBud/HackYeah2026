# Notifications without accounts

**Status:** draft · **Date:** 2026-10-03 · public accounts rejected (users must not need to register)

## Goal
Know who to inform when something changes, with no accounts and no passwords:
- an admin replies to a problem report
- an idea changes status
- a test round opens
- a test signup is accepted

At the same time, drop IP logic that doesn't earn its keep.

Non-goals:
- login for residents
- in-app inboxes
- user-visible history across devices

## Approach: optional email contact, linked to actions
Each follow-up action form gets one optional field: **"Podaj e-mail, jeśli chcesz dostać odpowiedź"**, plus a consent checkbox. If it is filled in, we upsert a `contact` row by email and link the action to it. No email means the action still works and nobody is notified.

Every email carries a link to the contact's **profile page**, `/profile/{token}`. It needs no login and shows:
- what they follow
- their ideas and test signups with status
- interests ("powiadom mnie o testach z obszaru X / w mojej gminie")
- "usuń moje dane"

Trade-off: contacts are unverified, so someone can type another person's email. That is acceptable: the worst case is unwanted emails, and each one has an unsubscribe and delete link. Verification (double opt-in) is the first thing to add after the demo.

## What it replaces
| Before | After |
|---|---|
| `ip_hash` on problem_report, support, signups, ratings + salt + IP middleware | removed |
| dedupe of "mnie też" by `(problem_report_id, ip_hash)` | soft: browser remembers the click (localStorage); with an email, unique `(problem_report_id, contact_id)` |
| per-item `access_token` links for ideas and test signups | kept only as a fallback for users who give no email (shown once on screen); with an email, the profile link covers everything |
| spam protection by stored ip_hash | in-process per-IP rate limit on public writes and `/match`, nothing stored |
| admin login limit keyed by email **and** ip_hash | email only; `client_ip_hash`, `ip_hash_salt` and `session.ip_hash` removed from admin auth |

## Data model
```sql
contact(
  id uuid pk, email citext unique, consent_at timestamptz,
  profile_token_hash bytea unique,     -- the token is sent only by email, never shown on the site
  location text null,                  -- gmina, optional, for targeting test rounds
  created_at
)
contact_interest(contact_id fk, challenge_area text, pk(contact_id, challenge_area))
```

Changes to existing tables:
| Table | Change |
|---|---|
| `problem_report` | `+ contact_id null`, `- ip_hash` |
| `problem_report_support` | `+ contact_id null`, `- ip_hash`, partial unique `(problem_report_id, contact_id) where contact_id is not null` |
| `idea` | `+ contact_id null` |
| `test_signup` | `+ contact_id null`; `contact_email`, `ip_hash` and the per-round purge go away, because data lives in one place |

## Who gets informed
| Event | Recipients (contacts with consent) |
|---|---|
| reply to a problem report | author + supporters with `contact_id` |
| idea status or reply | `idea.contact_id` |
| test round opened | `contact_interest` matching the innovation's area, optionally filtered by `contact.location` |
| signup accepted or rejected | `test_signup.contact_id` |

Delivery: a background task after commit sends through the email notifier, which already exists in the architecture.
- **Semantics:** at-most-once (a failed send is logged, not retried) for the MVP. The source of truth stays the status on the item, visible through the profile link or the fallback link.
- **Upgrade path:** if we need retries, write an `outbox` row in the same transaction and add a sender loop (deferred §8).

## API
**Public:**
- Action endpoints accept an optional `{email, consent}`:
  - `POST /problem-reports`
  - `POST /problem-reports/{id}/support`
  - `POST /ideas`
  - `POST /test-rounds/{id}/signups`
- `GET /profile/{token}`: what I follow, my items and their status, interests
- `PATCH /profile/{token}`: location, interests
- `DELETE /profile/{token}`: deletes the contact and nulls `contact_id` on items, so counts stay
- `GET /ideas/status/{token}` and `GET /test-signups/status/{token}`: fallback links for users without email

**Admin:** none new. The reply and status endpoints trigger notifications.

**Demo:** Mailpit in compose (SMTP catcher with a web UI) to show emails arriving. Use synthetic addresses only.

## Failure modes
| Failure | Effect | Mitigation |
|---|---|---|
| SMTP down / not configured | no emails | notifier is a no-op; status still visible via links |
| Someone enters another person's email | unwanted emails | unsubscribe/delete link in each email; double opt-in after the demo |
| User gives no email and loses the fallback link | can't see status | the reply to a problem report is public on its page anyway; ideas and signups are lost, which is accepted |
| Profile link forwarded | another person sees the follow list | same risk as any emailed link; "usuń moje dane" and token rotation on request |
| Same person clicks "mnie też" from several browsers | inflated count | accepted; criticality also requires several distinct gminy |

## Rollout
1. Remove IP logic from admin auth (small, code exists now).
2. `contact` + `contact_interest`, the optional email field on the action schemas, the profile endpoints.
3. Wire notifications into the admin reply and status endpoints.
4. Update `architecture.md` §4/§6 and `innovation-testing.md` (contact_id instead of contact_email, status link only as fallback).
