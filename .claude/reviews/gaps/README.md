# Gaps — 2026-10-04

Source review: [../staff-gap-review.md](../staff-gap-review.md). One file per gap; order = points per hour.

| # | Gap | Criterion | PR |
|---|---|---|---|
| [BE-01](be-01-notifier.md) | notifier + Mailpit, inbox fields | R10, R12 | `feat/notifier-rate-limit` |
| [BE-02](be-02-rate-limit.md) | per-IP rate limit | R11 | `feat/notifier-rate-limit` |
| [BE-07](be-07-hardening.md) | CSV, lockout, uploads, RabbitMQ, NUL | R11, R15 | `feat/notifier-rate-limit` |
| [BE-03](be-03-llm-drafts.md) | LLM grant + Middleman | R3, R7 | `feat/llm-drafts` |
| [BE-04](be-04-tester-admin.md) | tester admin + direct signup | R4 | `feat/tester-admin` |
| [BE-05](be-05-gaps-report.md) | gaps report empty | R2, R14 | `feat/tester-admin` |
| [BE-06](be-06-report-moderation.md) | public report moderation | R11 | `feat/tester-admin` |
| [BE-08](be-08-tests-regression.md) | Db tests + match hit@3 | R1, R13 | separate |
| [FE-01](fe-01-admin-moderation.md) | admin moderation + signups | R4, R5 | `feat/frontend-modules` |
| [FE-02](fe-02-rating-form.md) | rating form | R4 | `feat/frontend-modules` |
| [FE-03](fe-03-test-signup.md) | real test signup | R4 | `feat/frontend-modules` |
| [FE-04](fe-04-middleman.md) | Middleman flow | R7 | `feat/frontend-modules` |
| [FE-05](fe-05-grant-generator.md) | grant generator | R3 | `feat/frontend-modules` |
| [FE-06](fe-06-problem-report-page.md) | problem-report page | R5, R12 | `feat/frontend-modules` |
| [FE-07](fe-07-a11y-quality.md) | a11y, routes, fallbacks | R8, R14 | `chore/a11y-pass` |

Docs/code mismatch: traceability claims rate limit (R1, R9, R11) and email notifier (R10, R12) — neither exists. Fix in BE-01/BE-02 PR.
