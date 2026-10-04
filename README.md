# Małopolski Hub Innowacji Społecznych

Rozwiązanie wyzwania ROPS Kraków na HackYeah 2026. Mieszkaniec, organizacja albo gmina opisuje problem swoimi słowami, a platforma podpowiada sprawdzone innowacje społeczne z Małopolski, pokazuje podobne zgłoszenia i od razu prowadzi do kolejnego kroku: testowania rozwiązania, rozmowy z ROPS albo wniosku o grant. ROPS widzi w panelu, czego ludzie szukają i gdzie brakuje rozwiązań.

## Materiały zgłoszeniowe

| Materiał | Link |
|---|---|
| Działające demo | `TODO: link do demo` |
| Prezentacja (PDF, max 10 slajdów) / wideo (max 3 min) | `TODO: link do prezentacji lub wideo` |
| Makiety UX/UI | `TODO: link do makiet` (podgląd: [documentation/frontend/stitch/](documentation/frontend/stitch/)) |
| Koszt utrzymania i potrzebne zasoby | [documentation/running-cost.md](documentation/running-cost.md) |

## Moduły

| Moduł wyzwania | Co działa |
|---|---|
| Matchmaking społeczny | czat na stronie głównej: opis problemu → top 3 innowacje z bazy ROPS (wyszukiwanie semantyczne, model wielojęzyczny) + podobne zgłoszenia z „Mnie też” |
| Zasobnik wiedzy | biblioteka innowacji ze zdjęciami, filmami i kartami PDF; admin dodaje innowację z PDF-a i jest ona od razu indeksowana |
| Kreator pomysłów | fiszka pomysłu; generator wniosku (Zał. 3) ze szkicem AI, dostępny tylko przy otwartym naborze (demo ma jeden fikcyjny nabór) |
| Tester innowacji | zgłoszenie do testów z karty innowacji, decyzja ROPS mailem, ocena z linku w mailu |
| Platforma komunikacji | wątki przy każdej innowacji moderowane przez ROPS, odpowiedzi admina na pomysły i zgłoszenia, powiadomienia mailowe |
| Panel administratora | `/admin`: statystyki innowacji, skrzynka zgłoszeń, moderacja, testerzy, wnioski, raporty z CSV |
| Middleman innowacji | tylko API (`POST /middleman`, karta usługi z szablonu), bez ekranu |

Ścieżka „admin dowiaduje się o nowym zgłoszeniu → odpowiada → autor dostaje odpowiedź”: nowe pomysły, zgłoszenia, wątki i testerzy trafiają do skrzynki w `/admin/zgloszenia`; odpowiedź admina idzie mailem do autora, jeśli zostawił adres.

Dostępność (WCAG 2.1 AA): pasek dostępności na każdej stronie (powiększenie tekstu, wysoki kontrast, czytanie na głos), dyktowanie w czacie, pełna obsługa klawiaturą, axe-core bez naruszeń. Szczegóły: [documentation/frontend/architecture.md](documentation/frontend/architecture.md#6-accessibility-wcag-21-aa-20-of-the-score).

Dane demo są fikcyjne albo pochodzą z publicznej Biblioteki Innowacji ROPS; nie zawierają danych osobowych.

## Struktura

```
backend/        FastAPI (match-api: publiczne API + /admin) — patrz backend/CLAUDE.md
rag/            FastAPI (serwis RAG: indeksowanie PDF, wyszukiwanie, POST /query)
embeddings/     obraz serwisu embeddingów (TEI, multilingual MiniLM)
frontend/       Next.js (UI publiczne + panel admina) — patrz frontend/CLAUDE.md
media/          skrypty i dane z Biblioteki Innowacji ROPS (seed)
documentation/  architektura, kryteria wyzwania, dane przykładowe, OpenAPI
```

Architektura: [backend](documentation/backend/architecture.md), [frontend](documentation/frontend/architecture.md), [mapa wymagań](documentation/backend/requirements-traceability.md).

## Uruchamianie

### 1. Cały stack w Dockerze (najprościej)

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

Pierwsze uruchomienie pobiera model embeddingów i Ollamy, więc trwa kilka minut. Schemat bazy i innowacje demo zakładają się same (`migrate`, `seed-embed`).

| Usługa | Adres |
|---|---|
| Frontend | http://localhost:3000 |
| Panel admina | http://localhost:3000/admin (w compose bez logowania) |
| API + dokumentacja | http://localhost:8000, http://localhost:8000/docs |
| Serwis RAG | http://localhost:8001 |
| Postgres | localhost:5432 |

Powiadomienia mailowe wychodzą dopiero z ustawionym `MAIL_FROM` (adres nadawcy). Ustaw go w `.env` w katalogu głównym repo albo w powłoce, nie w `backend/.env`, bo sekcja `environment` w compose nadpisuje `env_file`. Bez `MAIL_FROM` powiadomienia są wyłączone, reszta działa.

Zatrzymanie: `docker compose down` (dane w wolumenach zostają; `-v` je usuwa).

### 2. Dev lokalnie (hot reload)

Każdy serwis w osobnym terminalu.

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

Baza, RAG i embeddingi z Dockera:
```bash
docker compose up db migrate rag seed-embed
```

### 2b. Frontend w Dockerze z hot reload

Backend zostaje na obrazie z `docker-compose.yml`; tylko `web` leci na `next dev` z montowanym kodem:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Na Windows włączony jest polling (`WATCHPACK_POLLING`). Zmiana `package.json` wymaga przebudowy / świeżego `npm ci` w volume.

## Konfiguracja

Zmienne trzymamy w `.env` (nigdy nie commitujemy — wzorce w `backend/.env.example` i `frontend/.env.example`).

| Zmienna | Gdzie | Domyślnie | Opis |
|---|---|---|---|
| `API_PORT`, `WEB_PORT`, `RAG_PORT` | compose | `8000`, `3000`, `8001` | porty hosta |
| `POSTGRES_*` | compose / backend | `hackyeah` | dane dostępowe do bazy |
| `ADMIN_USERNAME`, `ADMIN_PASSWORD` | backend | `admin` / `1234` | jedno wspólne konto admina; zmień poza demo |
| `ADMIN_AUTH_DISABLED` | compose / backend | `true` w compose, `false` w kodzie | demo: panel admina bez logowania; działa tylko z `DEBUG=true` |
| `GEMINI_API_KEY`, `GEMINI_MODEL` | backend | puste, `gemini-3.5-flash` | szkic wniosku AI; bez klucza wniosek wypełnia się z szablonu |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `MAIL_FROM` | compose / backend | puste | powiadomienia mailowe; pusty `SMTP_HOST` lub `MAIL_FROM` = wyłączone |
| `MAIL_REDIRECT_TO` | backend | puste | testy: wszystkie maile idą na ten adres |
| `WEB_URL`, `API_URL` | backend | `http://localhost:3000`, `http://localhost:8000` | adresy w linkach w mailach |
| `EMBEDDING_MODEL` | compose | `paraphrase-multilingual-MiniLM-L12-v2` | model embeddingów |
| `OLLAMA_MODEL`, `MATCH_MIN_SCORE` | compose (rag) | `qwen2.5:1.5b`, `0.15` | lokalny LLM do tagowania; próg trafności dopasowania |
| `NEXT_PUBLIC_API_URL` | frontend (build arg) | `http://localhost:8000` | adres API widziany przez przeglądarkę; wkompilowany na etapie build |

> `NEXT_PUBLIC_*` jest wstrzykiwany przy budowaniu obrazu, nie w runtime — zmiana wymaga przebudowania `web`.
