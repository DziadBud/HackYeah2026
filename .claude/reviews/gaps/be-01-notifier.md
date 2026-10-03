# BE-01 Notifier + Mailpit

**Criterion:** R10, R12 (jury: "how is the admin notified, how does the reply reach the author"). Hard req: automated notifications.
**PR:** `feat/notifier-rate-limit`

## Problem
No SMTP / notifier code. `config.py` has no mail settings. Inbox lacks pending threads and test signups. Reply path ends at `admin_reply` in the DB. `requirements-traceability.md` R10/R12 claim it exists.

## Fix
- `Notifier` protocol + `SmtpNotifier` on stdlib `smtplib`; no-op when `SMTP_HOST` empty.
- Settings: `SMTP_HOST`, `SMTP_PORT`, `MAIL_FROM`, `ADMIN_NOTIFY_EMAIL`, `WEB_URL`.
- Mailpit service in `docker-compose.yml` (web UI for the demo).
- Send from FastAPI `BackgroundTasks` after commit.
- **Delivery: at-most-once.** Failure logged, not retried; inbox is the source of truth. Outbox + worker (at-least-once) deferred.

| event | to |
|---|---|
| new idea, problem report, pending thread/reply, test signup | `ADMIN_NOTIFY_EMAIL` |
| idea reply / status, problem report reply | author email |
| thread/reply published | author email |
| test signup status change | signup email |
| grant call opened | idea authors with email + consent |

- `GET /admin/inbox`: add `pending_threads`, `new_test_signups`.

## Done when
Submit idea → mail in Mailpit to admin → admin replies → mail in Mailpit to author. Tests with a fake notifier assert each trigger.

## Docs
`architecture.md` §4 + Changes, traceability R10/R12.
