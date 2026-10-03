# HackYeah 2026 — Innowacje społeczne (ROPS)

Matchmaking problemów społecznych z innowacjami z bazy ROPS.

## Struktura

```
backend/        FastAPI (match-api: publiczne API + /admin) — patrz backend/CLAUDE.md
rag/            FastAPI (serwis RAG: indeksowanie + wyszukiwanie, POST /query)
frontend/       Next.js (public UI + admin UI) — patrz frontend/CLAUDE.md
docker/         inicjalizacja Postgresa (pgvector)
documentation/  architektura, kryteria, dane przykładowe
docker-compose.yml   db + api + web
```

Architektura: [documentation/backend/architecture.md](documentation/backend/architecture.md),
[documentation/frontend/architecture.md](documentation/frontend/architecture.md).

## Uruchamianie środowisk

### 1. Cały stack w Dockerze (najprościej)

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- API:      http://localhost:8000  (dokumentacja: http://localhost:8000/docs)
- Postgres: localhost:5432

Zatrzymanie: `docker compose down` (dane w wolumenie zostają; `-v` je usuwa).

### 2. Dev lokalnie (hot reload)

Każdy serwis w osobnym terminalu, do codziennej pracy.

Backend:
```bash
cd backend
cp .env.example .env
make venv      # tworzy .venv i instaluje zależności
make run       # uvicorn na :8000 z reloadem
```

Frontend:
```bash
cd frontend
cp .env.example .env.local
make install   # npm install
make dev       # next dev na :3000 z reloadem
```

Baza do dev lokalnego — podnieś samego Postgresa z Dockera:
```bash
docker compose up db
```

### 3. Tylko wybrany serwis w Dockerze

```bash
docker compose up --build web    # frontend (wymaga dostępnego api)
docker compose up --build api    # backend + db
```

## Konfiguracja

Zmienne środowiskowe trzymamy w `.env` (nigdy nie commitujemy — wzorce w `.env.example`).

| Zmienna | Gdzie | Domyślnie | Opis |
|---|---|---|---|
| `API_PORT` | compose | `8000` | port hosta dla API |
| `WEB_PORT` | compose | `3000` | port hosta dla frontendu |
| `POSTGRES_*` | compose / backend | `hackyeah` | dane dostępowe do bazy |
| `ADMIN_AUTH_DISABLED` | compose / backend | `true` w compose, `false` w kodzie | demo: panel admina bez logowania; działa tylko z `DEBUG=true` |
| `NEXT_PUBLIC_API_URL` | frontend (build arg) | `http://localhost:8000` | adres API widziany przez przeglądarkę; wkompilowany na etapie build |

> `NEXT_PUBLIC_*` jest wstrzykiwany przy budowaniu obrazu, nie w runtime — zmiana wymaga przebudowania `web`.
