# Innovation testing (Tester innowacji, R4)

**Status:** accepted · **Date:** 2026-10-03

## Goal
People can volunteer to test an innovation, the admin picks testers, and ratings and improvement ideas reach the admin. The brief asks for: sign up for tests, rate existing solutions, give feedback, propose improvements (CRITERIA module IV, +5%). Hackathon scope: as few tables and flows as possible.

Non-goals:
- test rounds, slots, deadlines, scheduling
- verified tester reports, accounts, tester profiles

## Design

### Flow
```
public: POST /match?test_signup=true {text, city, email, consent}
          -> normal match response + one test_signups row per matched innovation (status applied)
admin:  inbox shows new signups
        GET /admin/test-signups?innovation_id=&status=
        POST /admin/test-signups/{id}/status {accepted|rejected|completed} -> email to the signup's email (background task)
anyone: POST /innovations/{id}/feedback {stars, comment, test_signup_id?}  (per-IP rate limit)
admin:  GET /admin/innovations/{id}/feedback -> rating avg/count, signups, recent comments
```

There is no separate signup endpoint: volunteering is an option on the match request, so the people who have the problem test the solutions proposed for it. `email` is required when `test_signup=true` (422 otherwise). Testing itself is arranged by ROPS outside the platform; the acceptance email says who will get in touch. Improvement proposals are feedback comments.

### Data model
```sql
test_signups(id uuid pk, innovation_id text fk innovations,
             problem_report_id uuid fk problem_reports,  -- the match it came from
             email text,
             status text,  -- applied | accepted | rejected | completed
             created_at, updated_at)
feedback(id uuid pk, innovation_id text fk innovations,  -- rag's table (rag/sql/006)
         kind text,  -- rating | test_signup; test_signup when a valid test_signup_id is sent
         rating int,  -- api field stars
         comment text, created_at)
```

## Failure modes
| Failure | Mitigation |
|---|---|
| spam signups or ratings | per-IP rate limit, length caps |
| email send fails | logged, not retried; the admin still sees the status |
| anyone can rate without having tested | accepted for the MVP; optional `test_signup_id` is validated and stored as `kind='test_signup'` (which signup is not kept); shown as an average with a count |

## Rollout
1. `test_signups` + admin status change + email.
2. `feedback` + admin feedback view (already mocked in `GET /admin/innovations/{id}/feedback`).

Demo script: someone describes a problem with "chcę testować" ticked, the admin accepts, the email lands in Mailpit, then a rating with an improvement comment shows up in the admin feedback view.

## Deferred
Test rounds and verified tester reports through one-time links: add these when ROPS runs real testing rounds (architecture §8).
