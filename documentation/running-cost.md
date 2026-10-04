# Koszt utrzymania i potrzebne zasoby

Szacunek dla wdrożenia na całe województwo w pierwszym roku. Ceny orientacyjne (netto, październik 2026); przed wdrożeniem trzeba je potwierdzić u wybranego dostawcy.

## Założenia

- do kilkudziesięciu tysięcy wizyt miesięcznie, kilkaset dopasowań dziennie
- dopasowanie nie woła płatnego modelu: embeddingi (`paraphrase-multilingual-MiniLM-L12-v2`) i wyszukiwanie (pgvector) działają na własnym serwerze, więc koszt nie rośnie z liczbą zapytań
- płatne AI (Gemini Flash) tylko przy szkicu wniosku grantowego, z limitem zapytań na IP; bez klucza wniosek wypełnia się z szablonu
- cały system to jeden `docker compose`: Postgres z pgvector, match-api, rag, embeddings, Ollama, frontend

## Infrastruktura (miesięcznie)

| Pozycja | Wariant | Koszt |
|---|---|---|
| Serwer aplikacji | 1 VM, 4 vCPU / 8 GB RAM (embeddingi i mały model Ollamy na CPU) | ok. 100–250 zł |
| Baza danych | Postgres z pgvector na tym samym serwerze (start) albo zarządzany Postgres | 0 zł / ok. 100–300 zł |
| Kopie zapasowe | codzienny dump bazy i plików PDF do object storage | ok. 10–30 zł |
| Wysyłka maili | przekaźnik SMTP w darmowym progu (kilka tysięcy maili miesięcznie) | 0–50 zł |
| AI do wniosków | Gemini Flash, kilka tysięcy tokenów na szkic; przy setkach szkiców miesięcznie | poniżej 50 zł |
| Domena i certyfikat | domena + Let's Encrypt | ok. 5 zł (ok. 60 zł rocznie) |
| **Razem** | | **ok. 120–700 zł miesięcznie** |

Infrastrukturę może też dać istniejąca serwerownia urzędu marszałkowskiego. Wtedy zostaje tylko koszt AI i maili.

## Zasoby ludzkie

| Rola | Wymiar | Zadania |
|---|---|---|
| Redaktor treści (ROPS) | ok. 0,25 etatu | dodawanie innowacji z PDF, moderacja wątków, odpowiedzi w skrzynce, otwieranie naborów |
| Opiekun techniczny | kilka godzin miesięcznie (umowa serwisowa) | aktualizacje obrazów, kopie zapasowe, monitoring |
| Audyt dostępności | jednorazowo przed startem | audyt WCAG 2.1 AA z testem czytnikiem ekranu |

## Skalowanie

- więcej ruchu: druga replika match-api i frontendu za load balancerem (najpierw przenieść sesje admina z pamięci do Postgresa), większy VM pod embeddingi
- więcej danych: indeks HNSW w pgvector obsługuje dziesiątki tysięcy innowacji i fragmentów na tym samym serwerze
- integracje (baza grantów, powiadomienia o naborach): przez API match-api; RabbitMQ jest już w compose na potrzeby przyszłej kolejki, dziś nieużywany

Szczegóły techniczne: [backend/architecture.md](backend/architecture.md) (§7 tryby awarii, §8 odłożone).
