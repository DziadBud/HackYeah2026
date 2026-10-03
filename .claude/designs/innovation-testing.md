# Innovation testing (Tester innowacji, R4)

**Status:** draft · **Date:** 2026-10-03

## Goal
ROPS can recruit testers for chosen innovations, testers can apply and learn the outcome, and their ratings and improvement ideas reach the admin. The brief asks for: sign up for tests, rate existing solutions, give feedback, propose improvements (CRITERIA module IV, +5%).

Non-goals:
- public accounts or tester profiles
- scheduling and calendars

## Requirements & assumptions
- **Functional:**
  - The admin opens a **test round** for an innovation and closes it.
  - The public sees the open rounds and applies.
  - The admin accepts or rejects applicants with a message, and the applicant sees the outcome.
  - An accepted tester leaves a structured report.
  - Anyone can rate an innovation.
- **Constraints:**
  - No accounts.
  - Minimal personal data: zero personal data in the demo, synthetic only.
  - WCAG: no time limits, plain language.
  - Same patterns as ideas (optional email contact, fallback access token) so we build them once.
- **Numbers (assumed):** about 200 innovations, a handful of open rounds, tens of applications per round. All of this is trivial for Postgres.
- **Assumption:** testers are often institutions (gmina, CUS, NGO), not only residents. The `applicant_type` field covers both.

## How applicants learn the outcome
Follows [notifications-without-accounts.md](notifications-without-accounts.md); not duplicated here.
- The signup form has the shared optional `{email, consent}` field. With an email, the signup gets `contact_id`; status changes are emailed and visible on `/profile/{token}`.
- Without an email, the signup gets a fallback `access_token` link (shown once on screen) to `GET /test-signups/status/{token}`.
- Every signup also gets a short reference code (e.g. `TST-4F7K`), so a senior can phone ROPS and staff look the status up. Admin lookup key only.

What we give up: users who skip the email must revisit the link or call.

## Design

### Flow
```
admin: POST /admin/test-rounds {innovation_id, brief, who, slots, apply_until} -> open
        └─ innovation card + /match results show "szuka testerów" badge
public: GET /test-rounds  ("Chcę testować" intent)
        POST /test-rounds/{id}/signups [optional email + consent]
          -> reference_code, plus access_token link only when no email
admin:  inbox shows new signups -> POST /admin/test-signups/{id}/status {accepted|rejected, message}
        └─ email to test_signup.contact_id if set (background task)
public: /profile/{token} or GET /test-signups/status/{token} -> status, admin message, next steps
        report (only when accepted) -> rating, what worked, improvements
anyone: POST /innovations/{id}/ratings {stars, comment}  (per-IP rate limit, nothing stored)
```

### How we inform users
| Moment | Channel |
|---|---|
| A round opens | "szuka testerów" badge on the innovation card and in `/match` results. A gmina that just found a matching innovation is invited to test it, which links matchmaking to testing. Also listed under the "Chcę testować" intent. Email to contacts whose `contact_interest` matches the innovation's challenge area, optionally filtered by `contact.location` |
| After applying | Reference code on screen; fallback status link too when no email, with a prompt to save, print or copy it |
| Status change | Email to `test_signup.contact_id` if set; status visible on the profile page or fallback link |
| Round closes | Status shows "zakończone" |

### Data model
```sql
test_round(
  id uuid pk, innovation_id fk, title text, brief text,  -- what testing involves
  who_can_apply text[],                                  -- resident | institution | ngo
  slots int null, apply_until date null,
  status text,                                           -- open | closed
  created_at
)
test_signup(
  id uuid pk, test_round_id fk,
  applicant_type text,           -- resident | institution | ngo
  location text,                 -- gmina from the fixed list
  motivation text,               -- capped length
  contact_id uuid null fk -> contact,  -- see notifications-without-accounts.md
  status text,                   -- applied | accepted | rejected | withdrawn | completed
  admin_message text null, status_changed_at,
  access_token_hash bytea null unique,  -- fallback only, when no email
  reference_code text unique,           -- admin lookup key (phone support)
  created_at
)  -- partial unique (test_round_id, contact_id) where contact_id is not null
test_report(
  id uuid pk, test_signup_id fk unique, rating int 1..5,
  what_worked text, problems text, improvements text, created_at
)
innovation_rating(
  id uuid pk, innovation_id fk, stars int 1..5, comment text null, created_at
)  -- no dedupe column; per-IP rate limit only
```
These replace the generic `feedback(kind = rating | test_signup)` table in the architecture. Verified tester reports and anonymous ratings are kept apart, so admin reports can weight them differently.

### API
**Public:**
- `GET /test-rounds`
- `GET /test-rounds/{id}`
- `POST /test-rounds/{id}/signups`
- `GET /test-signups/status/{token}`: fallback status link (no email)
- `POST /test-signups/status/{token}/report`, or from the profile `POST /profile/{token}/test-signups/{id}/report`
- `DELETE /test-signups/status/{token}`, or `DELETE /profile/{token}/test-signups/{id}`: withdraw
- `POST /innovations/{id}/ratings`
- email data is managed on `/profile/{token}` (shared, not per round)

**Admin:**
- `GET/POST /admin/test-rounds`
- `PATCH /admin/test-rounds/{id}`: open/close; opening notifies matching `contact_interest`
- `GET /admin/test-rounds/{id}/signups`
- `POST /admin/test-signups/{id}/status`: notifies `test_signup.contact_id`
- admin search by `reference_code`
- `GET /admin/innovations/{id}/feedback`: extended with rating stats, signup counts by status, and the latest test reports including improvements
- Inbox gains `new_test_signups`

## Failure modes
| Failure | Effect | Mitigation |
|---|---|---|
| Applicant without email loses the link | can't see status | reference code: ROPS staff can look up the status and read it out on the phone (admin search by code) |
| Spam signups | noisy queue | per-IP rate limit (nothing stored), partial unique (round, contact_id), length caps |
| Spam ratings | skewed averages | per-IP rate limit; ratings shown apart from verified tester reports |
| Email send fails | no push | at-most-once, failure logged; status on the profile page / fallback link is still correct |
| Reference code guessed | sees someone's status | the code is a lookup key for admins only; public access needs the 256-bit token |
| Round closes with pending applications | applicants left hanging | closing sets remaining `applied` signups to `rejected` with a default message |

## Scaling & limits
Nothing here is hot. The first limit is human: how many applications an admin can triage. If a round gets hundreds of signups, add bulk accept/reject.

## Rollout (hackathon cut)
1. **Must (for the +5%):**
   - `test_round` and `test_signup` with reference code and fallback token link
   - the admin status change
   - `test_report`
   - ratings
   - badge on the card
   - extending admin feedback
2. **Should:** `contact_id` on signups with the shared contact/profile flow, round-opened emails via `contact_interest` ("powiadom mnie o testach z obszaru X / w mojej gminie"), and the badge in `/match` results.
3. **Later:** bulk triage.

Demo script: the admin opens a round, a gmina applies from a match result with a synthetic email, the admin accepts with a message, the email lands in Mailpit and the profile page shows it, then the tester submits a report and the admin sees the improvement ideas.

## Open questions
1. **Applicants:** can residents test, or only institutions? This drives the form, so I suggest allowing both, with `applicant_type`.
2. **Ownership:** who owns this module? It touches public routes nobody has started yet.
