# Backend

FastAPI service, worked on by 3 backend devs in parallel. Deps via `venv` + `pip` (no uv), pinned in `requirements*.txt`. Runs in Docker via `../docker-compose.yml`.

## Commands

- `make venv`: create `.venv`, install dev deps
- `make run`: uvicorn with reload on :8000
- `make test`: pytest
- `make up` / `make down`: docker compose
- `make openapi`: regenerate `openapi.json`, the API contract the frontend builds against

## Layout

- `app/main.py`: app wiring only, no business logic
- `app/config.py`: settings from env (`pydantic-settings`)
- `app/api/<feature>.py`: one router per feature, included in `main.py`
- `app/schemas/`, `app/services/`: add per feature when needed
- `tests/`: pytest, mirrors `app/`

New features go in new modules so devs rarely edit the same file.

## Collaboration

- Never push to `main`. Branch per task: `feat/<area>-<what>`, `fix/<area>-<what>`; PR reviewed by a teammate.
- Small PRs, merge often, rebase on `main` first.
- Agree on API contracts before implementing; the Pydantic schema is the contract.
- Shared files (`main.py`, `config.py`, `requirements.txt`, `docker-compose.yml`): small, additive edits only; announce in team chat.
- Commits start with a verb, scope in parens: `feat(booking): add create endpoint`. No bare "fix"/"update".
- Never commit `.env`, secrets, `.venv`. New env vars go in `.env.example`.
- New dependency: pin in `requirements.txt`, separate commit, mention in PR.

## Code rules

- Type hints everywhere; request/response bodies are Pydantic models, not dicts.
- Routes stay thin; logic lives in services, testable without HTTP.
- Use `HTTPException` (or domain errors mapped to it) with correct status codes.
- No hardcoded secrets or URLs; read from `Settings`.
- Comments only for non-obvious why; lowercase, short.
- Every new endpoint gets a pytest test: happy path plus one failure.
- Before a PR: `make test` passes and the app starts; if the API changed, run `make openapi` and commit `openapi.json`.
- No premature abstractions; mock blocking external services behind a small interface.
