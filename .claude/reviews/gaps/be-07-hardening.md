# BE-07 Small hardening

**Criterion:** R11, R15 (maintenance, cost).
**PR:** `feat/notifier-rate-limit`

- **CSV formula injection** — `services/admin/csv_export.py:15`: prefix `'` to cells starting with `= + - @ \t \r`.
- **Admin lockout DoS** — `services/admin/auth.py:56-58` keys failures on username only; key on username+IP, reset on success, prune old attempts.
- **Uploads lost on recreate** — `uploads` volume declared (`docker-compose.yml:176`) but not mounted on `api` at `/data/uploads`.
- **Open admin by default** — compose defaults `ADMIN_AUTH_DISABLED=true`, password `1234`. Keep for laptop; hosted demo `.env` must turn auth on.
- **Unused RabbitMQ** — nothing imports it; drop from compose (RAM + cost sheet).
- **NUL bytes** → Postgres `DataError` → 500; strip/reject in a shared validator.
