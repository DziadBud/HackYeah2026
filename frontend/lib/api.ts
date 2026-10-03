// typed client for match-api. the only module that knows the api shape;
// types mirror the backend pydantic schemas (backend/app/schemas/{public,admin}).

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

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    // admin routes authenticate with an HttpOnly session cookie
    credentials: "include",
    // no content-type on bodiless calls, so plain GETs skip the cors preflight
    headers: init?.body ? { "Content-Type": "application/json", ...init.headers } : init?.headers,
  });
  if (!res.ok) {
    throw new ApiError(res.status, `${init?.method ?? "GET"} ${path} -> ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

const post = <T>(path: string, body?: unknown) =>
  request<T>(path, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) });

const enc = encodeURIComponent;

// ---- shared enums and pages (backend/app/schemas/admin/common.py) ----

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

// no accounts: an optional email stored on the item; the backend wants consent=true with it
interface OptionalContact {
  email?: string;
  consent?: boolean;
}

// ---- public, mirrors backend/app/schemas/public ----

// POST /match?test_signup=true needs an email (422 otherwise)
export interface MatchRequest extends OptionalContact {
  text: string;
  city?: string;
}

export interface MatchedInnovation {
  id: string;
  title: string;
  summary: string;
  // explanation of the fit; null when the llm is down
  why: string | null;
  // raw tags, e.g. "area:Seniorzy"
  tags: string[];
  city: string;
}

export interface SimilarProblemReport {
  id: string;
  text: string;
  city: string;
  support_count: number;
  admin_reply?: string | null;
}

export interface MatchResponse {
  problem_report_id: string;
  innovations: MatchedInnovation[];
  similar_reports: SimilarProblemReport[];
  // one per matched innovation when test_signup=true
  test_signup_ids: string[];
}

export interface SupportResponse {
  support_count: number;
}

// GET /innovations and /innovations/{id} serve published innovations only
export interface LibraryInnovation extends AdminInnovation {
  rating_avg: number | null;
  rating_count: number;
}

export type ModerationStatus = "pending" | "published" | "hidden";
export type ReplyKind = "practitioner" | "expert" | "mentor" | "admin";

export interface ThreadReply {
  id: string;
  body: string;
  author_label: string;
  kind: ReplyKind;
  created_at: string;
}

export interface Thread {
  id: string;
  innovation_id: string;
  title: string;
  body: string;
  author_label: string;
  created_at: string;
  // published replies only
  replies: ThreadReply[];
}

export interface ThreadCreate extends OptionalContact {
  title: string;
  body: string;
  author_label: string;
}

// public replies are always kind=practitioner
export interface ReplyCreate extends OptionalContact {
  body: string;
  author_label: string;
}

// new threads and replies wait for moderation (202)
export interface Submitted {
  id: string;
  status: ModerationStatus;
}

export interface IdeaCreate extends OptionalContact {
  summary: string;
  essence: string;
  target_group: string;
  stage: IdeaStage;
}

export interface IdeaCreated {
  id: string;
  status: IdeaStatus;
}

export const api = {
  match: (body: MatchRequest, testSignup = false) =>
    post<MatchResponse>(`/match${testSignup ? "?test_signup=true" : ""}`, body),
  supportProblemReport: (id: string) => post<SupportResponse>(`/problem-reports/${enc(id)}/support`),
  innovations: (limit: number, offset: number) =>
    request<Page<LibraryInnovation>>(`/innovations?limit=${limit}&offset=${offset}`),
  innovation: (id: string) => request<LibraryInnovation>(`/innovations/${enc(id)}`),
  threads: (innovationId: string) => request<Thread[]>(`/innovations/${enc(innovationId)}/threads`),
  createThread: (innovationId: string, body: ThreadCreate) =>
    post<Submitted>(`/innovations/${enc(innovationId)}/threads`, body),
  replyToThread: (threadId: string, body: ReplyCreate) => post<Submitted>(`/threads/${enc(threadId)}/replies`, body),
  createIdea: (body: IdeaCreate) => post<IdeaCreated>("/ideas", body),
};

// ---- admin (/admin/*), mirrors backend/app/schemas/admin ----

export interface LoginRequest {
  username: string;
  password: string;
}

export interface AdminMe {
  id: string;
  username: string;
}

export type PublicationStatus = "draft" | "published";
export type Readiness = "concept" | "prototype" | "pilot" | "running";
export type CostLevel = "low" | "medium" | "high";

export interface AdminInnovation {
  id: string;
  title: string;
  summary: string;
  problem: string;
  innovator: string;
  challenge_areas: ChallengeArea[];
  target_group: string[];
  // null for rows created before these columns existed
  readiness: Readiness | null;
  cost_level: CostLevel | null;
  city: string;
  video_url?: string | null;
  status: PublicationStatus;
}

export interface FeedbackComment {
  comment: string;
  rating: number;
  created_at: string;
}

// one row of GET /admin/reports/innovations (also streams as csv)
export interface InnovationStatsRow {
  innovation_id: string;
  title: string;
  status: PublicationStatus;
  // problem reports whose top 3 contained this innovation
  matches_total: number;
  matches_7d: number;
  matches_prev_7d: number;
  // matched problem reports plus their "mnie też" presses
  people_reached: number;
  distinct_locations: number;
  test_signups_applied: number;
  test_signups_accepted: number;
  test_signups_rejected: number;
  rating_avg: number | null;
  rating_count: number;
  last_matched_at: string | null;
}

export interface InnovationStats {
  innovation_id: string;
  matches_total: number;
  matches_7d: number;
  matches_prev_7d: number;
  people_reached: number;
  distinct_locations: number;
  last_matched_at: string | null;
  // last 6 weeks, oldest first
  matches_by_week: { week_start: string; matches: number }[];
  matches_by_area: { challenge_area: ChallengeArea; matches: number }[];
  // matches is null when the location has fewer than 5 problem reports
  matches_by_location: { location: string; matches: number | null; note?: string | null }[];
  test_signups: { applied: number; accepted: number; rejected: number };
  rating_avg: number | null;
  rating_count: number;
  // index 0 = 1 star ... index 4 = 5 stars
  rating_distribution: number[];
  recent_comments: FeedbackComment[];
  recent_problem_reports: {
    id: string;
    text: string;
    challenge_area: ChallengeArea;
    location: string;
    support_count: number;
    created_at: string;
  }[];
}

export type IdeaStatus = "new" | "in_review" | "accepted" | "rejected";
export type IdeaStage = "concept" | "prototype" | "pilot" | "running";

export interface Idea {
  id: string;
  summary: string;
  essence: string;
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
  // null when the llm classification failed
  challenge_area: ChallengeArea | null;
  // the problem report's city (the admin api still calls it location)
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

export type ReportName = "trends" | "critical" | "locations" | "gaps" | "innovations";

export const adminApi = {
  login: (body: LoginRequest) => post<void>("/admin/auth/login", body),
  logout: () => post<void>("/admin/auth/logout"),
  me: () => request<AdminMe>("/admin/auth/me"),
  inbox: () => request<Inbox>("/admin/inbox"),
  problemReports: () => request<ProblemReport[]>("/admin/problem-reports"),
  replyToProblemReport: (id: string, message: string) =>
    post<ProblemReport>(`/admin/problem-reports/${enc(id)}/reply`, { message }),
  ideas: () => request<Idea[]>("/admin/ideas"),
  replyToIdea: (id: string, message: string) => post<Idea>(`/admin/ideas/${enc(id)}/reply`, { message }),
  setIdeaStatus: (id: string, status: IdeaStatus) => post<Idea>(`/admin/ideas/${enc(id)}/status`, { status }),
  innovations: () => request<Page<AdminInnovation>>("/admin/innovations?limit=100"),
  innovation: (id: string) => request<AdminInnovation>(`/admin/innovations/${enc(id)}`),
  setInnovationPublished: (id: string, published: boolean) =>
    post<AdminInnovation>(`/admin/innovations/${enc(id)}/${published ? "publish" : "unpublish"}`),
  innovationStats: (id: string) => request<InnovationStats>(`/admin/innovations/${enc(id)}/stats`),
  innovationStatsReport: () => request<InnovationStatsRow[]>("/admin/reports/innovations"),
  trends: () => request<TrendRow[]>("/admin/reports/trends"),
  critical: () => request<CriticalRow[]>("/admin/reports/critical"),
  gaps: () => request<GapRow[]>("/admin/reports/gaps"),
  grantCalls: () => request<GrantCall[]>("/admin/grant-calls"),
  setGrantCallOpen: (id: string, open: boolean) =>
    request<GrantCall>(`/admin/grant-calls/${enc(id)}`, { method: "PATCH", body: JSON.stringify({ open }) }),
  reportCsvUrl: (name: ReportName) => `${API_URL}/admin/reports/${name}?format=csv`,
};
