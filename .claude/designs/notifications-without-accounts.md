# Notifications without accounts

**Status:** accepted · **Date:** 2026-10-03 · public accounts rejected (users must not need to register)

## Goal
Tell people when something changes, with no accounts, no passwords and no extra tables:
- the admin replies to a problem report or an idea
- an idea changes status
- a test signup is accepted or rejected

Non-goals:
- login for residents
- profile pages, in-app inboxes, threads
- history across devices

## Approach: an optional email on the item
- **Problem reports and ideas:** the form has one optional field, "Podaj e-mail, jeśli chcesz dostać odpowiedź", plus a consent checkbox. The email is stored on the item (`problem_reports.email`, `ideas.email`).
- **Test signups** require an email (`test_signups.email`).
- No email means the action still works and nobody is notified.

The admin reply is an `admin_reply` column on the problem report or idea. A problem report reply is also shown on its public page, so one reply reaches everyone who pressed "mnie też", with or without an email.

Trade-off: emails are unverified, so someone can type another person's address. That is acceptable for the demo: the worst case is one unwanted email. Double opt-in comes after the demo.

## Who gets informed
| Event | Recipient |
|---|---|
| new idea, new problem report | admin (`ADMIN_NOTIFY_EMAIL`) |
| `admin_reply` set | the item's `email` |
| idea status changed | `ideas.email` |
| test signup accepted / rejected | `test_signups.email` |

## Delivery
- SMTP from env; a no-op if unset; Mailpit in compose for the demo (synthetic addresses only).
- It runs as a FastAPI background task after commit, at-most-once: a failed send is logged, not retried.
- The source of truth stays the item: the admin inbox, and the public problem report page.

## Failure modes
| Failure | Effect | Mitigation |
|---|---|---|
| SMTP down | no email | logged; reply still visible on the public problem report page and in the admin panel |
| no email given | author not notified about an idea | accepted; problem report replies are public |
| someone enters another person's email | one unwanted email | double opt-in after the demo |

## Deferred
A contacts table, per-contact links, message threads and an outbox. Add them when one reply column or at-most-once delivery is not enough (architecture §8).
