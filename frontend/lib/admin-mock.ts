// offline copy of the backend admin mocks (backend/app/services/admin/mock.py),
// used when match-api is unreachable so the panel can still be demoed.

import type { AdminInnovation, ChallengeArea, CriticalRow, GapRow, GrantCall, Idea, ProblemReport, TrendRow } from "@/lib/api";

export const AREA_LABEL: Record<ChallengeArea, string> = {
  "Rodzina i piecza zastepcza": "Rodzina i piecza zastępcza",
  Bezdomnosc: "Bezdomność",
  Niepelnosprawnosc: "Niepełnosprawność",
  Ubostwo: "Ubóstwo",
  "Integracja cudzoziemcow": "Integracja cudzoziemców",
  Zdrowie: "Zdrowie",
  "Zdrowie psychiczne": "Zdrowie psychiczne",
  Seniorzy: "Seniorzy",
};

export interface AdminData {
  problemReports: ProblemReport[];
  ideas: Idea[];
  innovations: AdminInnovation[];
  trends: TrendRow[];
  critical: CriticalRow[];
  gaps: GapRow[];
  grantCalls: GrantCall[];
}

const NOW = Date.parse("2026-10-03T09:00:00Z");
const ago = (hours: number) => new Date(NOW - hours * 3_600_000).toISOString();

export const ADMIN_MOCK: AdminData = {
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
      challenge_areas: ["Niepelnosprawnosc"],
      target_group: ["osoby niesłyszące", "osoby niedosłyszące"],
      readiness: "prototype",
      cost_level: "medium",
      status: "published",
    },
    {
      id: "straznik",
      title: "Strażnik",
      summary: "Aplikacja wykrywająca alarmy dźwiękowe i ostrzegająca wibracjami.",
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
};
