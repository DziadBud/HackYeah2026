// demo content until match-api serves innovations (GET /innovations/{id}) and
// /match. the first two entries come from the Stitch mockup, the rest from
// documentation/sample-data/sample-social-innovations.json. all people and
// comments are synthetic.

import type { Innovation } from "@/lib/api";

export interface ThreadReply {
  author: string;
  role: string;
  kind: "expert" | "mentor" | "practitioner";
  when: string;
  body: string;
}

export interface Thread {
  id: string;
  author: string;
  initials: string;
  meta: string;
  title: string;
  body: string;
  helpful: number;
  replies: ThreadReply[];
}

export interface DemoInnovation {
  id: string;
  title: string;
  // longer heading for the detail page
  fullTitle: string;
  summary: string;
  tags: string[];
  deployedIn?: string;
  author: string;
  partner?: string;
  recommended: boolean;
  problem: string;
  solution: string;
  results?: string;
  likes: number;
  keywords: string[];
  photoCaption?: string;
  threads: Thread[];
}

export const CARETAKER = {
  name: "Magdalena Szybist",
  role: "Koordynator Inkubatora Innowacji ROPS",
  phone: "+48 12 422 06 36 wew. 42",
  phoneHref: "tel:+48124220636",
  email: "innowacje@rops.krakow.pl",
  hours: "Środy: 09:00 – 14:00",
  place: "Kraków, ul. Piastowska 32 (pok. 114)",
};

export const INNOVATIONS: DemoInnovation[] = [
  {
    id: "sasiedzki-klub-aktywnego-seniora",
    title: "Sąsiedzki Klub Aktywnego Seniora",
    fullTitle:
      "Sąsiedzki Klub Aktywnego Seniora – Międzypokoleniowa animacja w świetlicach wiejskich",
    summary:
      "Międzypokoleniowy model animacji w świetlicach wiejskich oparty o tandem: senior-mentor i młody koordynator cyfrowy. Zawiera gotowe scenariusze 24 spotkań tematycznych.",
    tags: ["Seniorzy i Młodzież", "Aktywizacja lokalna"],
    deployedIn: "Powiat Tarnowski, Miechowski",
    author: "Fundacja Rozwoju Społecznego „Dolina Dunajca”",
    partner: "Regionalnym Ośrodkiem Polityki Społecznej w Krakowie",
    recommended: true,
    problem:
      "Izolacja osób starszych na terenach wiejskich, ograniczona siatka komunikacji zbiorowej oraz brak systemowych działań aktywizujących poza domem.",
    solution:
      "Reanimacja świetlic wiejskich w oparciu o wolontariat międzypokoleniowy. Młodzież uczy obsługi smartfonów, a seniorzy prowadzą warsztaty ginących zawodów.",
    results:
      "Wzrost samodzielności cyfrowej o 68% u uczestników, odnowienie więzi sąsiedzkich oraz uruchomienie lokalnych samopomocowych sieci dowozu leków.",
    likes: 142,
    keywords: ["senior", "seniorzy", "świetlica", "wieś", "wiejsk", "międzypokolen", "samotn", "izolacj", "aktywizacj", "integracj"],
    photoCaption:
      "Warsztaty cyfrowe w świetlicy wiejskiej w powiecie tarnowskim – testy praktyczne innowacji, edycja 2023/2024.",
    threads: [
      {
        id: "thread-1",
        author: "Anna K. (Koordynator GOPS Iwanowice)",
        initials: "AK",
        meta: "Zadano 2 dni temu • Kategoria: Logistyka i transport",
        title: "Jak poradzić sobie z transportem seniorów z odległych przysiółków?",
        body: "Chcemy uruchomić klub w remizie OSP, jednak część samotnych seniorów mieszka ponad 3 km od centrum wsi bez chodnika. Czy w ramach testowania innowacji można zorganizować refundację paliwa dla młodych wolontariuszy dowożących sąsiadów?",
        helpful: 12,
        replies: [
          {
            author: "Tomasz Nowak",
            role: "Ekspert ds. Innowacji ROPS Kraków",
            kind: "expert",
            when: "Wczoraj, 10:14",
            body: "Pani Anno, jak najbardziej! W testach w powiecie tarnowskim sprawdził się model sąsiedzkiego carpoolingu z bonem mobilnościowym rozliczanym ryczałtowo. W naszym pakiecie wdrożeniowym (Rozdział 4, str. 38) znajduje się gotowy wzór umowy porozumienia wolontariackiego na zwrot kosztów przejazdów bez konieczności skomplikowanych faktur. Chętnie pomożemy przygotować to w Państwa gminie.",
          },
          {
            author: "Marek Z.",
            role: "Praktyk (UG Limanowa)",
            kind: "practitioner",
            when: "Wczoraj, 14:30",
            body: "Dodatkowo warto zgrać zajęcia z lokalnymi kursami busów gminnych, a w dni powrotów wieczornych współpracujemy ze strażakami z OSP, którzy użyczają 9-osobowego busa ratowniczego. Seniorzy są zachwyceni tą formą!",
          },
        ],
      },
      {
        id: "thread-2",
        author: "Zofia B. (Biblioteka Publiczna w Żabnie)",
        initials: "ZB",
        meta: "1 tydzień temu • Kategoria: Dostępność materiałów",
        title: "Czy scenariusze zajęć cyfrowych nadają się dla osób 80+ z poważniejszymi wadami wzroku?",
        body: "Chcemy włączyć do warsztatów pensjonariuszy z lokalnego domu pobytu dziennego. Zastanawiamy się, czy czcionki i plansze edukacyjne posiadają warianty o wysokim kontraście i powiększonej skali druku?",
        helpful: 8,
        replies: [
          {
            author: "Katarzyna Wojtasik",
            role: "Mentor innowacji (Fundacja Dolina Dunajca)",
            kind: "mentor",
            when: "6 dni temu",
            body: "Pani Zofio, tak! W pakiecie dołączono specjalną paczkę „Materiały Wielkodrukowe (High Contrast A3)” ze stopniem pisma min. 24 pkt oraz prekonfigurowanymi lupami ekranowymi dla tabletów z systemem Android i iOS. Wszystkie karty pracy mają czarne obramowania na żółtym tle zgodnie z WCAG.",
          },
        ],
      },
    ],
  },
  {
    id: "cyfrowy-przewodnik-pokolen",
    title: "Cyfrowy Przewodnik Pokoleń",
    fullTitle: "Cyfrowy Przewodnik Pokoleń – młodzież uczy seniorów bezpieczeństwa w sieci",
    summary:
      "Praktyczne warsztaty bezpieczeństwa w sieci i obsługi e-usług prowadzonych przez lokalną młodzież szkolną. Projekt eliminuje wykluczenie cyfrowe osób 60+.",
    tags: ["Edukacja cyfrowa"],
    deployedIn: "Powiat Gorlicki, Nowotarski",
    author: "Stowarzyszenie „Cyfrowa Małopolska”",
    recommended: true,
    problem:
      "Wykluczenie cyfrowe osób 60+: brak umiejętności korzystania z e-usług publicznych i podatność na oszustwa internetowe.",
    solution:
      "Cykl warsztatów prowadzonych przez przeszkoloną młodzież szkolną w bibliotekach i świetlicach, z materiałami w dużym druku.",
    results: "Uczestnicy samodzielnie zakładają Profil Zaufany i rozpoznają typowe próby oszustw.",
    likes: 87,
    keywords: ["senior", "seniorzy", "cyfrow", "internet", "e-usług", "wykluczen", "młodzież", "oszust", "bezpieczeństw"],
    threads: [],
  },
  ...[
    {
      id: "wibraap",
      title: "Wibraap",
      problem:
        "Osoby niesłyszące i niedosłyszące są wykluczone z wydarzeń i aktywności, w których dominującym medium jest dźwięk; brak możliwości poza słuchowej percepcji muzyki w domu i na koncertach.",
      solution:
        "Zestaw kamizelki wibracyjnej i aplikacji (komputerowej oraz mobilnej), który przetwarza dowolne dźwięki na wibracje odczuwalne przez ciało. Tryby: mikrofon, import próbek dźwiękowych, gra na elektronicznym instrumencie.",
      tags: ["Osoby niesłyszące", "Kultura"],
      keywords: ["słuch", "niesłysz", "głuch", "muzyka", "wibracje", "dostępność", "koncert"],
      author: "Piotr Peszat",
    },
    {
      id: "straznik",
      title: "Strażnik",
      problem:
        "Osoby z dysfunkcją słuchu nie odbierają dźwiękowych sygnałów alarmowych (pożar, czujnik CO), zwłaszcza w nocy bez aparatów słuchowych — ryzyko dla zdrowia i życia.",
      solution:
        "Aplikacja mobilna współpracująca z telefonem i opaską/smartwatchem. Wykrywa alarmy dźwiękowe i ostrzega przez wibracje, latarkę, połączenie alarmowe do wskazanego numeru oraz wibracje w opasce inteligentnej.",
      tags: ["Osoby niesłyszące", "Bezpieczeństwo"],
      keywords: ["bezpieczeństw", "alarm", "pożar", "słuch", "niesłysz", "opaska", "ewakuacj"],
      author: "Marcin Kotliński",
    },
    {
      id: "hop-hop",
      title: "Hop Hop – mobilny plac zabaw",
      problem:
        "Dzieci w wieku przedszkolnym z zaburzeniami integracji sensorycznej i niepełnosprawnościami ruchowymi mają ograniczony dostęp do domowej rehabilitacji i atrakcyjnych narzędzi do ćwiczeń.",
      solution:
        "Meblo-zabawka wspierająca rehabilitację w domu: scenariusze zabaw i ćwiczeń dla opiekunów oraz zestaw meblozabawek do aktywności ruchowych. Adaptowalna do indywidualnych deficytów dziecka.",
      tags: ["Dzieci", "Rehabilitacja"],
      keywords: ["rehabilitacj", "dzieci", "dziecko", "sensory", "zabaw", "ruch", "przedszkol", "terapi"],
      author: "Aleksandra Satława",
    },
    {
      id: "himalaje-autyzmu",
      title: "Himalaje Autyzmu",
      problem:
        "Osoby neuroatypowe z trudnymi zachowaniami (agresja, autoagresja) mają utrudniony dostęp do diagnostyki i leczenia medycznego; personel i rodzice często nie radzą sobie z procedurami.",
      solution:
        "Model pracy ze scenariuszami przygotowującymi osoby neuroatypowe do wizyt w przychodniach, poradniach, punktach pobrań i szpitalach. Ścieżka postępowania, wsparcie komunikacji z personelem, wskazówki dla asystentów i opiekunów.",
      tags: ["Autyzm", "Zdrowie"],
      keywords: ["autyzm", "zdrowie", "lekarz", "neuroatyp", "opiek", "szpital", "przychodni"],
      author: "Chrześcijańskie Stowarzyszenie Osób Niepełnosprawnych, Ich Rodzin i Przyjaciół „Ognisko”",
    },
    {
      id: "gra-o-zdrowie",
      title: "Gra o zdrowie",
      problem:
        "Osoby z doświadczeniem kryzysu zdrowia psychicznego mają trudności z aktywizacją zawodową i oswojeniem tematu rynku pracy.",
      solution:
        "Terapeutyczna gra planszowa, w której gracze wcielają się w role z rynku pracy (pracownik, pracodawca, kandydat). Pomaga odkryć potencjał i przygotować się do realnych wyzwań przed podjęciem pracy.",
      tags: ["Zdrowie psychiczne", "Praca"],
      keywords: ["psychiczn", "praca", "pracy", "aktywizacj", "zawodow", "gra", "terapi", "bezrobo"],
      author: "Paulina Dąbrowska",
    },
    {
      id: "wozek-zakupowy",
      title: "Zakupy na jednym wózku z dzieckiem z niepełnosprawnością ruchową",
      problem:
        "Rodziny z dzieckiem z niepełnosprawnością ruchową (np. mózgowe porażenie dziecięce) nie mogą wygodnie robić zakupów w supermarketach — brak stabilnego siedziska w wózku zakupowym.",
      solution:
        "Wózek zakupowy z wyprofilowanym siedziskiem, stabilizatorami (zagłówek, odcinek lędźwiowy), pasami bezpieczeństwa. Dziecko uczestniczy w zakupach, współdecyduje i rozwija kompetencje społeczne.",
      tags: ["Niepełnosprawność ruchowa", "Rodzina"],
      keywords: ["zakup", "wózek", "dziecko", "dzieci", "niepełnospraw", "sklep", "supermarket", "rodzic"],
      author: "Jolanta Fień, Fundacja „APROBATA”",
    },
    {
      id: "maty-naprowadzajace",
      title: "Wsparcie imprez masowych dla osób z niepełnosprawnością wzroku",
      problem:
        "Osoby niewidome i niedowidzące mają utrudniony, niebezpieczny dostęp do koncertów i festiwali — trudność samodzielnego poruszania się w hałasie i tłoku.",
      solution:
        "Modułowe maty naprowadzające tworzące bezpieczne drogi na wydarzeniach masowych, w budynkach i na schodach. Uzupełnione podręcznikiem dla organizatorów imprez o organizacji dostępnego wydarzenia.",
      tags: ["Osoby niewidome", "Kultura"],
      keywords: ["wzrok", "niewidom", "niedowidz", "koncert", "festiwal", "imprez", "kultur", "bezpieczeństw"],
      author: "Tomasz Koźmiński",
    },
    {
      id: "paszport-choroby-rzadkiej",
      title: "Paszport pacjenta z chorobą rzadką",
      problem:
        "W nagłych sytuacjach medycznych lekarze nie mają szybkiego dostępu do kluczowych informacji o chorobie rzadkiej pacjenta, lekach i standardach postępowania.",
      solution:
        "System: aplikacja webowa (karty pacjentów, standardy postępowania), elektroniczny nośnik NFC z danymi pacjenta oraz programator chipów. Pacjent ma zawsze przy sobie najważniejsze informacje medyczne.",
      tags: ["Zdrowie", "Choroby rzadkie"],
      keywords: ["chorob", "rzadk", "zdrowie", "lekarz", "pacjent", "nagł", "medyczn"],
      author: "Jacek Sztajnke, Katarzyna Witkowska",
    },
  ].map(
    (s): DemoInnovation => ({
      ...s,
      fullTitle: s.title,
      summary: s.solution,
      recommended: false,
      likes: 0,
      threads: [],
    }),
  ),
];

export function findInnovation(id: string): DemoInnovation | undefined {
  return INNOVATIONS.find((i) => i.id === id);
}

export function toInnovation(d: DemoInnovation): Innovation {
  return { id: d.id, title: d.title, summary: d.summary, tags: d.tags, location: d.deployedIn };
}

// naive keyword overlap; stands in for the backend's hybrid search when the
// api is unreachable so the demo still answers.
export function demoMatch(text: string, limit = 3): Innovation[] {
  const q = text.toLowerCase();
  return INNOVATIONS.map((d) => ({
    d,
    score: d.keywords.reduce((n, k) => n + (q.includes(k.toLowerCase()) ? 1 : 0), 0),
  }))
    .filter((x) => x.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map((x) => toInnovation(x.d));
}
