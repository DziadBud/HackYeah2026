// typed client for match-api. the only module that knows the api shape;
// types mirror the backend pydantic schemas (documentation/backend/architecture.md).

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export interface Innovation {
  id: string;
  title: string;
  summary: string;
  // llm explanation of the fit; absent when the llm is down
  why?: string | null;
  tags?: string[];
  city?: string | null;
}

export interface SimilarProblemReport {
  id: string;
  text: string;
  city?: string | null;
  support_count: number;
}

export interface MatchRequest {
  text: string;
  city?: string;
}

export interface MatchResponse {
  innovations: Innovation[];
  similar_reports?: SimilarProblemReport[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    // admin routes authenticate with an HttpOnly session cookie
    credentials: "include",
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    throw new ApiError(res.status, `${init?.method ?? "GET"} ${path} -> ${res.status}`);
  }
  return (await res.json()) as T;
}

export const api = {
  match: (text: string, city?: string) =>
    request<MatchResponse>("/match", {
      method: "POST",
      body: JSON.stringify({ text, city } satisfies MatchRequest),
    }),
};

// ---- admin (/admin/*), mirrors backend/app/schemas/admin ----

export type ChallengeArea =
  | "Rodzina i piecza zastepcza"
  | "Bezdomnosc"
  | "Niepelnosprawnosc"
  | "Ubostwo"
  | "Integracja cudzoziemcow"
  | "Zdrowie"
  | "Zdrowie psychiczne"
  | "Seniorzy";

export interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export type PublicationStatus = "draft" | "published";

export interface AdminInnovation {
  id: string;
  title: string;
  summary: string;
  challenge_areas: ChallengeArea[];
  target_group: string[];
  readiness: string;
  cost_level: string;
  video_url?: string | null;
  status: PublicationStatus;
}

export type IdeaStatus = "new" | "in_review" | "accepted" | "rejected";
export type IdeaStage = "concept" | "prototype" | "pilot" | "running";

export interface Idea {
  id: string;
  summary: string;
  target_group: string;
  stage: IdeaStage;
  social_canvas: { problem: string; solution: string; beneficiaries: string; resources?: string | null };
  status: IdeaStatus;
  admin_reply?: string | null;
  created_at: string;
}

export interface ProblemReport {
  id: string;
  text: string;
  challenge_area: ChallengeArea;
  location: string;
  support_count: number;
  is_critical: boolean;
  criticality_score: number;
  admin_reply?: string | null;
  created_at: string;
}

export interface Inbox {
  new_ideas: Idea[];
  new_problem_reports: ProblemReport[];
  critical_problem_reports: ProblemReport[];
}

export interface TrendRow {
  week_start: string;
  challenge_area: ChallengeArea;
  location: string;
  problem_reports: number;
  support_count: number;
}

export interface CriticalRow {
  problem_report_id: string;
  text: string;
  challenge_area: ChallengeArea;
  distinct_locations: number;
  growth_ratio_7d: number;
  score: number;
}

export interface GapRow {
  problem_report_id: string;
  text: string;
  challenge_area: ChallengeArea;
  best_match_similarity: number;
}

export interface GrantCall {
  id: string;
  name: string;
  deadline: string;
  open: boolean;
  sections: { title: string; description?: string | null; required: boolean }[];
}

export type ReportName = "trends" | "critical" | "locations" | "gaps";

const post = <T>(path: string, body?: unknown) =>
  request<T>(path, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) });

export const adminApi = {
  inbox: () => request<Inbox>("/admin/inbox"),
  problemReports: () => request<ProblemReport[]>("/admin/problem-reports"),
  replyToProblemReport: (id: string, message: string) =>
    post<ProblemReport>(`/admin/problem-reports/${encodeURIComponent(id)}/reply`, { message }),
  ideas: () => request<Idea[]>("/admin/ideas"),
  replyToIdea: (id: string, message: string) =>
    post<Idea>(`/admin/ideas/${encodeURIComponent(id)}/reply`, { message }),
  setIdeaStatus: (id: string, status: IdeaStatus) =>
    post<Idea>(`/admin/ideas/${encodeURIComponent(id)}/status`, { status }),
  innovations: () => request<Page<AdminInnovation>>("/admin/innovations?limit=100"),
  setInnovationPublished: (id: string, published: boolean) =>
    post<AdminInnovation>(`/admin/innovations/${encodeURIComponent(id)}/${published ? "publish" : "unpublish"}`),
  trends: () => request<TrendRow[]>("/admin/reports/trends"),
  critical: () => request<CriticalRow[]>("/admin/reports/critical"),
  gaps: () => request<GapRow[]>("/admin/reports/gaps"),
  grantCalls: () => request<GrantCall[]>("/admin/grant-calls"),
  setGrantCallOpen: (id: string, open: boolean) =>
    request<GrantCall>(`/admin/grant-calls/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify({ open }),
    }),
  reportCsvUrl: (name: ReportName) => `${API_URL}/admin/reports/${name}?format=csv`,
};
