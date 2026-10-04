-- one open ROPS call so the public grant generator has something to fill
INSERT INTO grant_calls (id, name, deadline, open, sections)
VALUES (
    'a0000000-0000-4000-8000-000000000001',
    'Inkubator Włączenia Społecznego 2.0 — nabór ROPS',
    '2026-12-15',
    true,
    '[
      {"title": "Tytuł innowacji", "description": "Krótki tytuł kojarzący się z przedmiotem innowacji", "required": true},
      {"title": "Opis innowacji", "description": "Na czym polega innowacja? Charakter (produkt, aplikacja, model pracy…); włączenie społeczne / deinstytucjonalizacja", "required": true},
      {"title": "Innowacyjność rozwiązania", "description": "Wyjątkowość względem rozwiązań w PL/świecie; nowa wartość", "required": true},
      {"title": "Diagnoza problemu", "description": "Problem, skala (dane jeśli znane), Mapa Wyzwań Społecznych — bez zmyślania liczb", "required": true},
      {"title": "Opis odbiorców innowacji", "description": "Grupa docelowa, potrzeby, ryzyko wykluczenia", "required": true},
      {"title": "Zmiana jaką wprowadza innowacja", "description": "Wpływ na problem i włączenie społeczne odbiorców", "required": true},
      {"title": "Wizja przyszłości innowacji", "description": "Skalowalność, inne konteksty, wdrażalność", "required": true},
      {"title": "Plan działania i koszty", "description": "Okres przygotowawczy (≤3 mies.) oraz testowanie Faza I/II (≤9 mies.): działanie, termin, koszt", "required": true}
    ]'::jsonb
)
ON CONFLICT (id) DO NOTHING;
