// offline copy of the backend admin mocks (backend/app/services/admin/mock.py),
// used when match-api is unreachable so the panel can still be demoed.

import type {
  AdminInnovation,
  AdminThread,
  ChallengeArea,
  CriticalRow,
  GapRow,
  GrantApplication,
  GrantCall,
  Idea,
  InnovationStats,
  InnovationStatsRow,
  ProblemReport,
  TestSignup,
  TrendRow,
} from "@/lib/api";

export interface AdminData {
  problemReports: ProblemReport[];
  ideas: Idea[];
  innovations: AdminInnovation[];
  trends: TrendRow[];
  critical: CriticalRow[];
  gaps: GapRow[];
  grantCalls: GrantCall[];
  grantApplications: GrantApplication[];
  threads: AdminThread[];
  testSignups: TestSignup[];
}

const NOW = Date.parse("2026-10-03T09:00:00Z");
const ago = (hours: number) => new Date(NOW - hours * 3_600_000).toISOString();

export const ADMIN_MOCK: AdminData = {
  threads: [
    {
      id: "thread-pending-1",
      innovation_id: "gra-o-zdrowie",
      title: "Skąd wziąć salę na warsztaty w małej gminie?",
      body: "Chcemy uruchomić grę w remizie, ale nie mamy budżetu na wynajem. Macie doświadczenia z użyczeniem sali od OSP?",
      author_label: "Anna K. (OPS Myślenice)",
      email: "anna@example.pl",
      status: "pending",
      created_at: ago(2),
      replies: [
        {
          id: "reply-pending-1",
          body: "U nas wójt podpisał porozumienie z OSP — sala gratis w zamian za promocję.",
          author_label: "Piotr W. (GOPS Skawina)",
          email: null,
          kind: "practitioner",
          status: "pending",
          created_at: ago(1),
        },
      ],
    },
    {
      id: "thread-published-1",
      innovation_id: "sasiedzki-klub-aktywnego-seniora",
      title: "Jak rekrutować wolontariuszy do dowozu seniorów?",
      body: "Szukamy sprawdzonych kanałów — szkoły, parafie, Facebook lokalny?",
      author_label: "Marta L. (GOPS Wieliczka)",
      email: null,
      status: "published",
      created_at: ago(40),
      replies: [],
    },
  ],
  problemReports: [
    {
      id: "problem-report-1",
      text: "W naszej gminie nie ma żadnego wsparcia dla rodzin zastępczych po 18. roku życia dziecka.",
      challenge_area: "Rodzina i piecza zastepcza",
      location: "Wieliczka",
      support_count: 14,
      is_critical: true,
      criticality_score: 3.4,
      created_at: ago(144),
    },
    {
      id: "problem-report-2",
      text: "Brak psychologa dziecięcego, kolejka ponad pół roku.",
      challenge_area: "Zdrowie psychiczne",
      location: "Kraków",
      support_count: 7,
      is_critical: true,
      criticality_score: 2.1,
      admin_reply: "Zgłoszenie przekazane do ROPS.",
      created_at: ago(48),
    },
    {
      id: "problem-report-3",
      text: "Autobus do ośrodka zdrowia kursuje tylko dwa razy dziennie.",
      challenge_area: "Seniorzy",
      location: "Skawina",
      support_count: 2,
      is_critical: false,
      criticality_score: 0.4,
      created_at: ago(3),
    },
  ],
  ideas: [
    {
      id: "idea-1",
      summary: "Mobilny punkt porad dla seniorów na wsiach",
      essence: "Bus z doradcami raz w tygodniu odwiedza sołectwa bez punktu porad.",
      target_group: "seniorzy",
      stage: "concept",
      social_canvas: {
        problem: "Brak dostępu do porad prawnych i zdrowotnych poza miastem",
        solution: "Bus z doradcami odwiedzający sołectwa raz w tygodniu",
        beneficiaries: "seniorzy z małych miejscowości",
      },
      status: "new",
      created_at: ago(5),
    },
    {
      id: "idea-2",
      summary: "Mieszkania treningowe dla osób wychodzących z bezdomności",
      essence: "Roczny pobyt w mieszkaniu z asystentem przed samodzielnym najmem.",
      target_group: "osoby w kryzysie bezdomności",
      stage: "prototype",
      social_canvas: {
        problem: "Powroty na ulicę po opuszczeniu schroniska",
        solution: "Roczny program mieszkań z asystentem",
        beneficiaries: "osoby bezdomne",
        resources: "2 mieszkania, asystent",
      },
      status: "in_review",
      admin_reply: "Dziękujemy, analizujemy zgłoszenie.",
      created_at: ago(96),
    },
  ],
  innovations: [
    {
      id: "wibraap",
      title: "Wibraap",
      summary: "Kamizelka wibracyjna i aplikacja zamieniająca dźwięk na wibracje.",
      problem: "Osoby niesłyszące są wykluczone z wydarzeń, w których dominuje dźwięk.",
      innovator: "Piotr Peszat",
      city: "Kraków",
      challenge_areas: ["Niepelnosprawnosc"],
      target_group: ["osoby niesłyszące", "osoby niedosłyszące"],
      readiness: "prototype",
      cost_level: "medium",
      video_url: "https://example.com/wibraap.mp4",
      status: "published",
    },
    {
      id: "straznik",
      title: "Strażnik",
      summary: "Aplikacja wykrywająca alarmy dźwiękowe i ostrzegająca wibracjami.",
      problem: "Osoby z dysfunkcją słuchu nie słyszą alarmów, zwłaszcza w nocy.",
      innovator: "Marcin Kotliński",
      city: "Tarnów",
      challenge_areas: ["Niepelnosprawnosc", "Seniorzy"],
      target_group: ["osoby niesłyszące", "seniorzy"],
      readiness: "pilot",
      cost_level: "low",
      status: "published",
    },
    {
      id: "paszport-choroby-rzadkiej",
      title: "Paszport pacjenta z chorobą rzadką",
      summary: "System IT z danymi pacjenta dostępnymi dla personelu medycznego.",
      problem: "Lekarze w nagłych sytuacjach nie znają choroby rzadkiej pacjenta.",
      innovator: "Jacek Sztajnke, Katarzyna Witkowska",
      city: "",
      challenge_areas: ["Zdrowie"],
      target_group: ["pacjenci z chorobami rzadkimi"],
      readiness: "concept",
      cost_level: "high",
      status: "draft",
    },
  ],
  trends: [
    { week_start: "2026-09-14", challenge_area: "Rodzina i piecza zastepcza", location: "Wieliczka", problem_reports: 3, support_count: 9 },
    { week_start: "2026-09-21", challenge_area: "Rodzina i piecza zastepcza", location: "Wieliczka", problem_reports: 5, support_count: 21 },
    { week_start: "2026-09-21", challenge_area: "Zdrowie psychiczne", location: "Kraków", problem_reports: 8, support_count: 17 },
  ],
  critical: [
    {
      problem_report_id: "problem-report-1",
      text: "Brak wsparcia dla rodzin zastępczych po 18. roku życia dziecka.",
      challenge_area: "Rodzina i piecza zastepcza",
      distinct_locations: 4,
      growth_ratio_7d: 2.3,
      score: 36.8,
    },
  ],
  gaps: [
    {
      problem_report_id: "problem-report-2",
      text: "Brak psychologa dziecięcego, kolejka ponad pół roku.",
      challenge_area: "Zdrowie psychiczne",
      best_match_similarity: 0.31,
    },
  ],
  grantCalls: [
    {
      id: "call-1",
      name: "Nabór ROPS 2026: innowacje społeczne",
      deadline: "2026-12-15",
      open: true,
      sections: [
        { title: "Opis problemu", required: true },
        { title: "Plan wdrożenia", required: true },
        { title: "Budżet", required: false },
      ],
    },
  ],
  grantApplications: [
    {
      id: "app-1",
      idea_id: null,
      grant_call_id: "call-1",
      status: "submitted",
      title: "Sąsiedzka sieć wsparcia seniorów",
      applicant_type: "person",
      applicant: {
        first_name: "Anna",
        last_name: "Kowalska",
        address: "ul. Krakowska 5",
        postal_code: "33-100",
        city: "Tarnów",
        phone: "600 100 200",
        email: "anna@example.com",
      },
      description: "Wolontariusze z osiedla pomagają seniorom w zakupach i wizytach u lekarza.",
      innovativeness: "Łączy lokalne kluby seniora z prostą aplikacją do umawiania pomocy.",
      problem_diagnosis: "Seniorzy w małych miastach są samotni i nie mają wsparcia na co dzień.",
      beneficiaries: "Osoby 65+ mieszkające samotnie.",
      expected_change: "Mniej samotności, łatwiejszy dostęp do usług.",
      future_vision: "Sieć działa w 5 gminach Małopolski.",
      action_plan: {
        preparation_summary: "Rekrutacja wolontariuszy i spotkania w klubach seniora.",
        preparation: [{ action: "Spotkania informacyjne", timeline: "11.2026", cost_pln: 2000, note: null }],
        testing_summary: "Test w dwóch osiedlach Tarnowa.",
        testing_phase_1: [{ action: "Pilotaż na osiedlu Mościce", timeline: "01–03.2027", cost_pln: 18000, note: null }],
        testing_phase_2: [{ action: "Rozszerzenie na Jasną", timeline: "04–06.2027", cost_pln: 25000, note: null }],
      },
      grant_amount_pln: "45000",
      team: "Anna Kowalska — koordynatorka, 10 lat w organizacjach pozarządowych.",
      declarations: { resides_in_poland: true, full_legal_capacity: true, data_truthful: true },
      email: "anna@example.com",
      generated_by: "gemini",
      created_at: ago(48),
      updated_at: ago(24),
    },
    {
      id: "app-2",
      idea_id: null,
      grant_call_id: "call-1",
      status: "draft",
      title: "Warsztaty cyfrowe w bibliotece",
      applicant_type: "organization",
      applicant: { name: "Stowarzyszenie Razem", city: "Nowy Sącz" },
      description: "Cotygodniowe warsztaty obsługi smartfona dla seniorów.",
      innovativeness: "",
      problem_diagnosis: "",
      beneficiaries: "",
      expected_change: "",
      future_vision: "",
      action_plan: { preparation_summary: "", preparation: [], testing_summary: "", testing_phase_1: [], testing_phase_2: [] },
      grant_amount_pln: null,
      team: "",
      declarations: {},
      email: null,
      generated_by: null,
      created_at: ago(5),
      updated_at: ago(2),
    },
  ],
  testSignups: [
    {
      id: "signup-3",
      innovation_id: "straznik",
      innovation_title: "Strażnik",
      problem_report_id: null,
      email: "ops.wieliczka@example.com",
      status: "applied",
      created_at: ago(5),
    },
    {
      id: "signup-1",
      innovation_id: "wibraap",
      innovation_title: "Wibraap",
      problem_report_id: "problem-report-1",
      email: "tester@example.com",
      status: "applied",
      created_at: ago(30),
    },
    {
      id: "signup-2",
      innovation_id: "wibraap",
      innovation_title: "Wibraap",
      problem_report_id: "problem-report-2",
      email: "tester2@example.com",
      status: "accepted",
      created_at: ago(48),
    },
    {
      id: "signup-4",
      innovation_id: "wibraap",
      innovation_title: "Wibraap",
      problem_report_id: null,
      email: "dps@example.com",
      status: "rated",
      created_at: ago(240),
    },
  ],
};

const WEEKS = ["2026-08-24", "2026-08-31", "2026-09-07", "2026-09-14", "2026-09-21", "2026-09-28"];

function stats(
  id: string,
  a: {
    weekly: number[];
    locations: [string, number][];
    areas: [ChallengeArea, number][];
    people: number;
    signups: [number, number, number];
    ratings: number[];
    comments: [string, number, number][];
    reports: [string, ChallengeArea, string, number, number][];
  },
): InnovationStats {
  const count = a.ratings.reduce((x, y) => x + y, 0);
  const reports = a.reports.map(([text, challenge_area, location, support_count, days], n) => ({
    id: `problem-report-${id}-${n + 1}`,
    text,
    challenge_area,
    location,
    support_count,
    created_at: ago(days * 24),
  }));
  return {
    innovation_id: id,
    matches_total: a.weekly.reduce((x, y) => x + y, 0),
    matches_7d: a.weekly[a.weekly.length - 1],
    matches_prev_7d: a.weekly[a.weekly.length - 2],
    people_reached: a.people,
    distinct_locations: a.locations.length,
    last_matched_at: reports.length ? reports.map((r) => r.created_at).sort().at(-1)! : null,
    matches_by_week: a.weekly.map((matches, n) => ({ week_start: WEEKS[n], matches })),
    matches_by_area: a.areas.map(([challenge_area, matches]) => ({ challenge_area, matches })),
    // same privacy rule as the backend: fewer than 5 problem reports is not shown
    matches_by_location: a.locations.map(([location, n]) =>
      n >= 5 ? { location, matches: n } : { location, matches: null, note: "too few problem reports to display" },
    ),
    test_signups: { applied: a.signups[0], accepted: a.signups[1], rejected: a.signups[2] },
    rating_avg: count ? Math.round((a.ratings.reduce((s, n, i) => s + (i + 1) * n, 0) / count) * 100) / 100 : null,
    rating_count: count,
    rating_distribution: a.ratings,
    recent_comments: a.comments.map(([comment, rating, days]) => ({ comment, rating, created_at: ago(days * 24) })),
    recent_problem_reports: reports,
  };
}

const EMPTY = { weekly: [0, 0, 0, 0, 0, 0], locations: [], areas: [], people: 0, signups: [0, 0, 0] as [number, number, number], ratings: [0, 0, 0, 0, 0], comments: [], reports: [] };

// offline copy of the backend stats fixture (MockInnovationAdminService._ACTIVITY)
export const INNOVATION_STATS_MOCK: Record<string, InnovationStats> = {
  wibraap: stats("wibraap", {
    weekly: [2, 3, 5, 4, 6, 9],
    locations: [["Kraków", 15], ["Tarnów", 8], ["Nowy Sącz", 4], ["Wieliczka", 2]],
    areas: [["Niepelnosprawnosc", 26], ["Seniorzy", 3]],
    people: 61,
    signups: [5, 2, 1],
    ratings: [1, 0, 2, 4, 5],
    comments: [
      ["Dzieci w naszym ośrodku po raz pierwszy poczuły koncert. Prosimy o wersję dziecięcą kamizelki.", 5, 1],
      ["Aplikacja na telefon czasem gubi połączenie z kamizelką.", 3, 4],
    ],
    reports: [
      ["Głusi uczniowie nie mogą uczestniczyć w szkolnych koncertach i apelach.", "Niepelnosprawnosc", "Tarnów", 6, 2],
      ["Brak oferty kulturalnej dla osób niedosłyszących w domu kultury.", "Niepelnosprawnosc", "Kraków", 3, 5],
    ],
  }),
  straznik: stats("straznik", {
    weekly: [1, 2, 2, 4, 5, 7],
    locations: [["Kraków", 9], ["Skawina", 6], ["Myślenice", 4], ["Bochnia", 2]],
    areas: [["Niepelnosprawnosc", 13], ["Seniorzy", 8]],
    people: 38,
    signups: [4, 3, 1],
    ratings: [0, 1, 2, 8, 13],
    comments: [
      ["Świetny pomysł, chcemy przetestować w naszym DPS.", 5, 1],
      ["Potrzeba tańszej wersji dla gmin.", 4, 3],
      ["Opaska powinna działać też bez smartfona.", 4, 6],
    ],
    reports: [
      ["Mama jest niedosłysząca i nie słyszy czujnika dymu w nocy.", "Seniorzy", "Skawina", 9, 1],
      ["Mieszkańcy DPS z aparatami słuchowymi nie reagują na alarm pożarowy.", "Niepelnosprawnosc", "Kraków", 4, 3],
    ],
  }),
};

export function mockInnovationStats(id: string): InnovationStats {
  return INNOVATION_STATS_MOCK[id] ?? stats(id, EMPTY);
}

// the shape of GET /admin/reports/innovations, built from the detail stats
export function mockInnovationStatsReport(innovations: AdminInnovation[]): InnovationStatsRow[] {
  return innovations
    .map((i) => {
      const s = mockInnovationStats(i.id);
      return {
        innovation_id: i.id,
        title: i.title,
        status: i.status,
        matches_total: s.matches_total,
        matches_7d: s.matches_7d,
        matches_prev_7d: s.matches_prev_7d,
        people_reached: s.people_reached,
        distinct_locations: s.distinct_locations,
        test_signups_applied: s.test_signups.applied,
        test_signups_accepted: s.test_signups.accepted,
        test_signups_rejected: s.test_signups.rejected,
        rating_avg: s.rating_avg,
        rating_count: s.rating_count,
        last_matched_at: s.last_matched_at,
      };
    })
    .sort((a, b) => b.matches_total - a.matches_total);
}
