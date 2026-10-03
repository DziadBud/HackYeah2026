# Admin authentication

**Status:** accepted, MVP implemented (in-memory store) · **Date:** 2026-10-03

**Changed:** IP logic removed; no IP stored on sessions, login limit keyed by email only (see [notifications-without-accounts.md](notifications-without-accounts.md)).

## Goal
Only named ROPS staff can use `/admin/*` (match-api) and `/ingest/*` (ingest-service). Reports, problem reports and replies must never leak to the public (brief requirement, R6, R11). Every admin action is tied to a specific person.

Non-goals: public user accounts, self-service sign-up, SSO with the voivodeship IdP (production path, see Rollout).

## Requirements & assumptions
- Functional: login, logout, "who am I", per-person accounts, disable an admin immediately, record who replied, published or changed what.
- Non-functional: admin traffic under 1 rps; one Postgres query per request is acceptable (about 1 ms on an indexed PK).
- Security: passwords never stored in plain text, a stolen browser token is useless after logout or expiry, no token readable by JS (XSS), brute-force protection, no default credentials in the repo.
- Assumptions (flagged):
  - 2-10 admins.
  - Admin UI and API are served same-site behind one proxy (`/api`, `/ingest`), so cookies work.
  - HTTPS in any non-local deployment.

## Options
### A. Shared env credentials + JWT bearer (current plan)
One username/password in `.env`, login returns an HS256 JWT, and the UI sends it as `Authorization: Bearer`.
- \+ Stateless and quick to build.
- \- One shared account: no audit, no offboarding without rotating the password for everyone.
- \- No revocation before expiry.
- \- The token lives in JS storage, so XSS can steal it.

### B. Per-admin accounts + server-side sessions in an HttpOnly cookie
An `admin_user` table with argon2id hashes. Login creates an opaque random session token, stores only its hash in `admin_session` and sets it as an `HttpOnly; Secure; SameSite=Strict` cookie. Each request looks the session up.
- \+ Instant revocation (logout, disable an admin, kill all sessions).
- \+ The token is invisible to JS.
- \+ Audit per person.
- \+ ingest-service shares the DB, so the same dependency works there.
- \- One DB lookup per request.
- \- Needs same-site hosting and CSRF care for cookies.

### C. External identity provider (OIDC: Keycloak or the office's Entra ID)
- \+ MFA, offboarding and password policy handled by the IdP.
- \+ Best fit for production in a public institution.
- \- An extra service or tenant to run.
- \- Too heavy for the hackathon.

## Recommendation
**B.** Two things decide it. Revocation and audit matter for a public institution, and at under 1 rps the "stateful lookup" cost of sessions is irrelevant.

Trade-off: we give up stateless JWT verification, which only pays off with many services or high request rates, for revocability and no token in JS. C is the production target, and B's `require_admin` interface stays the same when it is swapped in.

## Design

```
browser ──POST /admin/auth/login──▶ match-api ── verify argon2id ──▶ admin_user
        ◀── Set-Cookie: admin_session=<random 256 bit> (HttpOnly, Secure, SameSite=Strict)
browser ──GET /admin/... (cookie)──▶ require_admin ── sha256(token) ──▶ admin_session (+ admin_user.is_active)
                                     └─▶ AdminPrincipal(id, email) passed to the route
```

### Data model
```sql
admin_user(
  id uuid pk, email citext unique, password_hash text, is_active bool default true,
  created_at timestamptz, last_login_at timestamptz
)
admin_session(
  token_hash bytea pk,            -- sha256 of the cookie value, the raw token is never stored
  admin_id uuid fk -> admin_user, created_at, last_seen_at, expires_at
)                                  -- index on admin_id (kill all sessions for one admin)
admin_login_attempt(
  email citext, attempted_at timestamptz, ok bool
)                                  -- index (email, attempted_at)
admin_audit(
  id uuid pk, admin_id fk, action text, target_type text, target_id text, at timestamptz
)
```
Replies get a `replied_by` (admin id) and `replied_at` next to `admin_reply`.

### API
| Endpoint | Behaviour |
|---|---|
| `POST /admin/auth/login {email, password}` | 204 + Set-Cookie; 401 generic "invalid credentials"; 429 when rate limited |
| `POST /admin/auth/logout` | deletes the session row, clears the cookie, 204 |
| `GET /admin/auth/me` | `{id, email}`; used by the UI to check whether it is logged in |

`TokenResponse` is removed. `require_admin` reads the cookie and returns `AdminPrincipal`, and routes that mutate state write `admin_audit`.

### Rules
- **Password hashing:** argon2id (`argon2-cffi`, new dependency). When the email is unknown, verify against a dummy hash so the response time does not reveal which emails exist.
- **Session lifetime:** 8 h absolute, 30 min idle. `last_seen_at` is updated at most once a minute, to avoid a write on every request.
- **Cookie flags:** `Secure` is off only when `DEBUG=true` (local http).
- **CSRF:** `SameSite=Strict`, plus unsafe methods (POST, PATCH, DELETE) must carry an `Origin` header that is in `CORS_ORIGINS`. CORS uses `allow_credentials=True` with explicit origins, never `*`.
- **Brute force:** 5 failed logins per email in 15 min gives 429. Stored in Postgres, so the limit holds across instances.
- **Bootstrap:** `make create-admin`, a CLI that prompts for the password. No seeded or default admin. `SESSION_PEPPER` is not needed because tokens are random 256-bit values.
- **Hardening:** disable `/docs` and `/openapi.json` when `DEBUG=false`, because they list every admin route.
- **ingest-service:** imports the same dependency from `common/auth.py`.

## Failure modes
| Failure | Effect | Mitigation |
|---|---|---|
| XSS in the admin UI | attacker acts while the tab is open | HttpOnly cookie: the token can't be exfiltrated; CSP on the UI |
| CSRF from another site | forged admin action | SameSite=Strict + Origin check |
| Password guessing | account takeover | argon2id, rate limit, generic errors |
| Stolen laptop / admin leaves | lingering access | `is_active=false` + delete sessions: takes effect on the next request |
| DB leak | hashes exposed | argon2id passwords; session hashes are useless without the raw cookie |
| Postgres down | admin can't log in | same as the rest of the app, accepted for MVP |
| Clock skew | n/a | expiry is checked against DB time (`now()`), not the app clock |

## Scaling & limits
The first bottleneck is the session lookup per request, which matters only at hundreds of rps of admin traffic, far beyond our numbers. The next step would be caching sessions in Redis with a short TTL, accepting a few seconds of delay on revocation.

## Rollout
1. Migration: the four tables above plus `replied_by` and `replied_at`.
2. `common/auth.py`: `require_admin` → `AdminPrincipal`. The login service gets a real implementation, and the mock login is kept only for tests through `dependency_overrides`.
3. Tests:
   - The parametrised check that every protected route returns 401 without a cookie.
   - Expired session → 401; inactive admin → 401.
   - Logout invalidates the session.
   - The 6th failed login → 429.
   - POST with a foreign `Origin` → 403.
4. Docs: update §4 of `architecture.md` (JWT → session cookie) and R11.
5. Production path: replace password login with OIDC (option C) and add MFA there. Sessions and `require_admin` stay.

## Open questions
1. **MFA (TOTP) now?** About two hours of extra work. I suggest skipping it for the demo and mentioning it on the slides as part of the OIDC path.
2. **Admin UI hosting:** will it be served from the same domain as the API? Cookies assume same-site. If not, we fall back to a short-lived bearer token held in memory plus a refresh cookie, which is more complex.
3. **Who are the admins in the demo?** We need 1-2 demo accounts created by the CLI. The password goes in the team chat, not the repo.
