-- demo innovations from documentation/sample-data/sample-social-innovations.json.
-- chunks need embeddings, so compose `seed-embed` calls rag POST /embed for every
-- published innovation without chunks. ON CONFLICT keeps admin edits on re-runs.
INSERT INTO innovations (id, title, content, summary, tags, city, status)
VALUES
    (
        'wibraap',
        'Wibraap',
        'Problem: Osoby niesłyszące i niedosłyszące są wykluczone z wydarzeń i aktywności, w których dominującym medium jest dźwięk; brak możliwości poza słuchowej percepcji muzyki w domu i na koncertach.

Rozwiązanie: Zestaw kamizelki wibracyjnej i aplikacji (komputerowej oraz mobilnej), który przetwarza dowolne dźwięki na wibracje odczuwalne przez ciało. Tryby: mikrofon, import próbek dźwiękowych, gra na elektronicznym instrumencie.

Dla kogo: osoby niesłyszące, osoby niedosłyszące, osoby g/Głuche.

Rodzaj: product + app.

Innowator: Piotr Peszat.

Źródło: Inkubator Dostępności – Innowacje społeczne dla dostępności (ROPS Kraków / FIRR, 2022).',
        'Zestaw kamizelki wibracyjnej i aplikacji (komputerowej oraz mobilnej), który przetwarza dowolne dźwięki na wibracje odczuwalne przez ciało. Tryby: mikrofon, import próbek dźwiękowych, gra na elektronicznym instrumencie.',
        ARRAY['słuch', 'muzyka', 'wibracje', 'dostępność', 'kamizelka', 'aplikacja', 'koncert', 'type:innovation', 'area:niepelnosprawnosc'],
        '',
        'published'
    ),
    (
        'straznik',
        'Strażnik',
        'Problem: Osoby z dysfunkcją słuchu nie odbierają dźwiękowych sygnałów alarmowych (pożar, czujnik CO), zwłaszcza w nocy bez aparatów słuchowych — ryzyko dla zdrowia i życia.

Rozwiązanie: Aplikacja mobilna współpracująca z telefonem i opaską/smartwatchem. Wykrywa alarmy dźwiękowe i ostrzega przez wibracje, latarkę, połączenie alarmowe do wskazanego numeru oraz wibracje w opasce inteligentnej.

Dla kogo: osoby niesłyszące, osoby niedosłyszące, osoby głuchoniewidome.

Rodzaj: app.

Innowator: Marcin Kotliński.

Źródło: Inkubator Dostępności – Innowacje społeczne dla dostępności (ROPS Kraków / FIRR, 2022).',
        'Aplikacja mobilna współpracująca z telefonem i opaską/smartwatchem. Wykrywa alarmy dźwiękowe i ostrzega przez wibracje, latarkę, połączenie alarmowe do wskazanego numeru oraz wibracje w opasce inteligentnej.',
        ARRAY['bezpieczeństwo', 'alarm', 'pożar', 'słuch', 'opaska', 'aplikacja', 'ewakuacja', 'type:innovation', 'area:niepelnosprawnosc'],
        '',
        'published'
    ),
    (
        'hop-hop',
        'Hop Hop – mobilny plac zabaw',
        'Problem: Dzieci w wieku przedszkolnym z zaburzeniami integracji sensorycznej i niepełnosprawnościami ruchowymi mają ograniczony dostęp do domowej rehabilitacji i atrakcyjnych narzędzi do ćwiczeń.

Rozwiązanie: Meblo-zabawka wspierająca rehabilitację w domu: scenariusze zabaw i ćwiczeń dla opiekunów oraz zestaw meblozabawek do aktywności ruchowych. Adaptowalna do indywidualnych deficytów dziecka.

Dla kogo: dzieci przedszkolne, zaburzenia integracji sensorycznej, niepełnosprawność ruchowa, przedszkola, fizjoterapeuci.

Rodzaj: product.

Innowator: Aleksandra Satława.

Źródło: Inkubator Dostępności – Innowacje społeczne dla dostępności (ROPS Kraków / FIRR, 2022).',
        'Meblo-zabawka wspierająca rehabilitację w domu: scenariusze zabaw i ćwiczeń dla opiekunów oraz zestaw meblozabawek do aktywności ruchowych. Adaptowalna do indywidualnych deficytów dziecka.',
        ARRAY['rehabilitacja', 'dzieci', 'sensoryka', 'zabawa', 'ruch', 'dom', 'terapia', 'type:innovation', 'area:niepelnosprawnosc'],
        '',
        'published'
    ),
    (
        'himalaje-autyzmu',
        'Himalaje Autyzmu',
        'Problem: Osoby neuroatypowe z trudnymi zachowaniami (agresja, autoagresja) mają utrudniony dostęp do diagnostyki i leczenia medycznego; personel i rodzice często nie radzą sobie z procedurami.

Rozwiązanie: Model pracy ze scenariuszami przygotowującymi osoby neuroatypowe do wizyt w przychodniach, poradniach, punktach pobrań i szpitalach. Ścieżka postępowania, wsparcie komunikacji z personelem, wskazówki dla asystentów i opiekunów.

Dla kogo: osoby w spektrum autyzmu, osoby neuroatypowe, rodzice i opiekunowie, personel medyczny.

Rodzaj: service / work model.

Innowator: Chrześcijańskie Stowarzyszenie Osób Niepełnosprawnych, Ich Rodzin i Przyjaciół „Ognisko”.

Źródło: Inkubator Dostępności – Innowacje społeczne dla dostępności (ROPS Kraków / FIRR, 2022).',
        'Model pracy ze scenariuszami przygotowującymi osoby neuroatypowe do wizyt w przychodniach, poradniach, punktach pobrań i szpitalach. Ścieżka postępowania, wsparcie komunikacji z personelem, wskazówki dla asystentów i opiekunów.',
        ARRAY['autyzm', 'zdrowie', 'wizyta lekarska', 'neuroatypowość', 'opieka', 'procedury medyczne', 'type:innovation', 'area:niepelnosprawnosc', 'area:zdrowie'],
        '',
        'published'
    ),
    (
        'gra-o-zdrowie',
        'Gra o zdrowie',
        'Problem: Osoby z doświadczeniem kryzysu zdrowia psychicznego mają trudności z aktywizacją zawodową i oswojeniem tematu rynku pracy.

Rozwiązanie: Terapeutyczna gra planszowa, w której gracze wcielają się w role z rynku pracy (pracownik, pracodawca, kandydat). Pomaga odkryć potencjał i przygotować się do realnych wyzwań przed podjęciem pracy. Przydatna także na dziennych oddziałach psychiatrycznych i w WTZ.

Dla kogo: osoby z zaburzeniami psychicznymi, dzienne oddziały psychiatryczne, Warsztaty Terapii Zajęciowej.

Rodzaj: educational product.

Innowator: Paulina Dąbrowska.

Źródło: Inkubator Dostępności – Innowacje społeczne dla dostępności (ROPS Kraków / FIRR, 2022).',
        'Terapeutyczna gra planszowa, w której gracze wcielają się w role z rynku pracy (pracownik, pracodawca, kandydat). Pomaga odkryć potencjał i przygotować się do realnych wyzwań przed podjęciem pracy. Przydatna także na dziennych oddziałach psychiatrycznych i w WTZ.',
        ARRAY['zdrowie psychiczne', 'praca', 'aktywizacja zawodowa', 'gra', 'terapia', 'rynek pracy', 'type:innovation', 'area:zdrowie-psychiczne'],
        '',
        'published'
    ),
    (
        'wozek-zakupowy',
        'Zakupy na jednym wózku z dzieckiem z niepełnosprawnością ruchową',
        'Problem: Rodziny z dzieckiem z niepełnosprawnością ruchową (np. mózgowe porażenie dziecięce) nie mogą wygodnie robić zakupów w supermarketach — brak stabilnego siedziska w wózku zakupowym.

Rozwiązanie: Wózek zakupowy z wyprofilowanym siedziskiem, stabilizatorami (zagłówek, odcinek lędźwiowy), pasami bezpieczeństwa. Dziecko uczestniczy w zakupach, współdecyduje i rozwija kompetencje społeczne.

Dla kogo: dzieci z niepełnosprawnością ruchową, rodzice, opiekunowie, supermarkety.

Rodzaj: product.

Innowator: Jolanta Fień, Fundacja „APROBATA”.

Źródło: Inkubator Dostępności – Innowacje społeczne dla dostępności (ROPS Kraków / FIRR, 2022).',
        'Wózek zakupowy z wyprofilowanym siedziskiem, stabilizatorami (zagłówek, odcinek lędźwiowy), pasami bezpieczeństwa. Dziecko uczestniczy w zakupach, współdecyduje i rozwija kompetencje społeczne.',
        ARRAY['zakupy', 'wózek', 'dziecko', 'niepełnosprawność ruchowa', 'supermarket', 'dostępność', 'type:innovation', 'area:niepelnosprawnosc'],
        '',
        'published'
    ),
    (
        'maty-naprowadzajace',
        'Wsparcie imprez masowych dla osób z niepełnosprawnością wzroku',
        'Problem: Osoby niewidome i niedowidzące mają utrudniony, niebezpieczny dostęp do koncertów i festiwali — trudność samodzielnego poruszania się w hałasie i tłoku.

Rozwiązanie: Modułowe maty naprowadzające tworzące bezpieczne drogi na wydarzeniach masowych, w budynkach i na schodach. Uzupełnione podręcznikiem dla organizatorów imprez o organizacji dostępnego wydarzenia.

Dla kogo: osoby niewidome, osoby niedowidzące, organizatorzy imprez masowych.

Rodzaj: product + guide.

Innowator: Tomasz Koźmiński.

Źródło: Inkubator Dostępności – Innowacje społeczne dla dostępności (ROPS Kraków / FIRR, 2022).',
        'Modułowe maty naprowadzające tworzące bezpieczne drogi na wydarzeniach masowych, w budynkach i na schodach. Uzupełnione podręcznikiem dla organizatorów imprez o organizacji dostępnego wydarzenia.',
        ARRAY['wzrok', 'koncert', 'festiwal', 'maty', 'nawigacja', 'kultura', 'bezpieczeństwo', 'type:innovation', 'area:niepelnosprawnosc'],
        '',
        'published'
    ),
    (
        'paszport-choroby-rzadkiej',
        'Paszport pacjenta z chorobą rzadką',
        'Problem: W nagłych sytuacjach medycznych lekarze nie mają szybkiego dostępu do kluczowych informacji o chorobie rzadkiej pacjenta, lekach i standardach postępowania.

Rozwiązanie: System: aplikacja webowa (karty pacjentów, standardy postępowania), elektroniczny nośnik NFC z danymi pacjenta oraz programator chipów. Pacjent ma zawsze przy sobie najważniejsze informacje medyczne.

Dla kogo: pacjenci z chorobami rzadkimi, personel medyczny, POZ.

Rodzaj: IT system.

Innowator: Jacek Sztajnke, Katarzyna Witkowska.

Źródło: Inkubator Dostępności – Innowacje społeczne dla dostępności (ROPS Kraków / FIRR, 2022).',
        'System: aplikacja webowa (karty pacjentów, standardy postępowania), elektroniczny nośnik NFC z danymi pacjenta oraz programator chipów. Pacjent ma zawsze przy sobie najważniejsze informacje medyczne.',
        ARRAY['choroby rzadkie', 'zdrowie', 'paszport', 'NFC', 'nagły wypadek', 'lekarz', 'dane medyczne', 'type:innovation', 'area:zdrowie'],
        '',
        'published'
    )
ON CONFLICT (id) DO NOTHING;
