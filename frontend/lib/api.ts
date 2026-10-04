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
    // no content-type on bodiless calls, so plain GETs skip the cors preflight;
    // FormData gets its multipart boundary from the browser
    headers: init?.body && !(init.body instanceof FormData)
      ? { "Content-Type": "application/json", ...init.headers }
      : init?.headers,
  });
  if (!res.ok) {
    throw new ApiError(
      res.status,
      `${init?.method ?? "GET"} ${path} -> ${res.status}`,
    );
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

const post = <T>(path: string, body?: unknown) =>
  request<T>(path, {
    method: "POST",
    body: body === undefined ? undefined : JSON.stringify(body),
  });

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
  // rag's llm summary of the problem, one for the whole result; empty when the llm is down
  answer: string;
  innovations: MatchedInnovation[];
  similar_reports: SimilarProblemReport[];
  // one per matched innovation when test_signup=true
  test_signup_ids: string[];
}

export interface SupportResponse {
  support_count: number;
}

// anonymous likes: client_id is a random uuid the browser keeps, one like per browser
export interface LikeState {
  like_count: number;
  liked: boolean;
}

// GET /innovations and /innovations/{id} serve published innovations only
// the mock-only problem / target_group of AdminInnovation are replaced by the profile texts
export interface LibraryInnovation extends Omit<AdminInnovation, "problem" | "target_group"> {
  rating_avg: number | null;
  rating_count: number;
  // only the detail endpoint fills it; true when innovationPdfUrl serves the source pdf
  has_pdf?: boolean;
  // description sections (innovation_profiles); empty for innovations without one
  tagline: string | null;
  program: string | null;
  problem: string | null;
  target_group: string | null;
  who_can_use: string | null;
  effectiveness: string | null;
  authors: string[];
  // file names for innovationPhotoUrl, the first one is the cover
  photos: string[];
  license_name: string | null;
  license_url: string | null;
  // the innovation's page in the ROPS library
  source_url: string | null;
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

// GET /admin/threads — every reply, whatever its status
export interface AdminReply {
  id: string;
  body: string;
  author_label: string;
  email: string | null;
  kind: ReplyKind;
  status: ModerationStatus;
  created_at: string;
}

export interface AdminThread {
  id: string;
  innovation_id: string;
  title: string;
  body: string;
  author_label: string;
  email: string | null;
  status: ModerationStatus;
  created_at: string;
  replies: AdminReply[];
}

export type ModerationDecision = ModerationStatus;

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

// POST /innovations/{id}/test-signups: one signup for that innovation, email + consent required
export interface TestSignupCreate {
  email: string;
  consent: true;
}

export interface TestSignupCreated {
  id: string;
  status: TestSignupStatus;
}

// ROPS Zał. 3 — public grant application (AI draft + user edit)
export type GrantApplicationStatus = "draft" | "submitted";
export type ApplicantType = "person" | "organization" | "informal_group";

export interface PlanStep {
  action: string;
  timeline: string;
  cost_pln: number | null;
  note: string | null;
}

export interface ActionPlan {
  preparation_summary: string;
  preparation: PlanStep[];
  testing_summary: string;
  testing_phase_1: PlanStep[];
  testing_phase_2: PlanStep[];
}

export interface GrantApplication {
  id: string;
  idea_id: string | null;
  grant_call_id: string | null;
  status: GrantApplicationStatus;
  title: string;
  applicant_type: ApplicantType;
  applicant: Record<string, unknown>;
  description: string;
  innovativeness: string;
  problem_diagnosis: string;
  beneficiaries: string;
  expected_change: string;
  future_vision: string;
  action_plan: ActionPlan;
  grant_amount_pln: string | null;
  team: string;
  declarations: Record<string, boolean>;
  email: string | null;
  generated_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface GrantApplicationCreate extends OptionalContact {
  grant_call_id: string;
  applicant_type?: ApplicantType;
  notes?: string;
  /** false = skip Gemini, empty/template draft only */
  use_ai?: boolean;
}

export type GrantApplicationUpdate = Partial<
  Pick<
    GrantApplication,
    | "status"
    | "title"
    | "applicant_type"
    | "applicant"
    | "description"
    | "innovativeness"
    | "problem_diagnosis"
    | "beneficiaries"
    | "expected_change"
    | "future_vision"
    | "action_plan"
    | "grant_amount_pln"
    | "team"
    | "declarations"
    | "email"
  >
>;

export interface PublicGrantCall {
  id: string;
  name: string;
  deadline: string;
  open: boolean;
  sections: { title: string; description?: string | null; required: boolean }[];
}

const patch = <T>(path: string, body: unknown) =>
  request<T>(path, { method: "PATCH", body: JSON.stringify(body) });

export const api = {
  match: (body: MatchRequest, testSignup = false) =>
    post<MatchResponse>(`/match${testSignup ? "?test_signup=true" : ""}`, body),
  supportProblemReport: (id: string) =>
    post<SupportResponse>(`/problem-reports/${enc(id)}/support`),
  innovations: (limit: number, offset: number) =>
    request<Page<LibraryInnovation>>(
      `/innovations?limit=${limit}&offset=${offset}`,
    ),
  innovation: (id: string) =>
    request<LibraryInnovation>(`/innovations/${enc(id)}`),
  // a download (content-disposition: attachment), not a viewer page
  innovationPdfUrl: (id: string) => `${API_URL}/innovations/${enc(id)}/pdf`,
  innovationPhotoUrl: (id: string, name: string) => `${API_URL}/innovations/${enc(id)}/photos/${enc(name)}`,
  likes: (innovationId: string, clientId: string) =>
    request<LikeState>(`/innovations/${enc(innovationId)}/likes?client_id=${enc(clientId)}`),
  setLike: (innovationId: string, clientId: string, liked: boolean) =>
    request<LikeState>(`/innovations/${enc(innovationId)}/likes/${enc(clientId)}`, {
      method: liked ? "PUT" : "DELETE",
    }),
  threads: (innovationId: string) =>
    request<Thread[]>(`/innovations/${enc(innovationId)}/threads`),
  createThread: (innovationId: string, body: ThreadCreate) =>
    post<Submitted>(`/innovations/${enc(innovationId)}/threads`, body),
  replyToThread: (threadId: string, body: ReplyCreate) =>
    post<Submitted>(`/threads/${enc(threadId)}/replies`, body),
  createIdea: (body: IdeaCreate) => post<IdeaCreated>("/ideas", body),
  signUpForTest: (innovationId: string, body: TestSignupCreate) =>
    post<TestSignupCreated>(`/innovations/${enc(innovationId)}/test-signups`, body),
  openGrantCalls: () => request<PublicGrantCall[]>("/grant-calls"),
  createGrantApplication: (ideaId: string, body: GrantApplicationCreate) =>
    post<GrantApplication>(`/ideas/${enc(ideaId)}/grant-application`, body),
  getGrantApplication: (id: string) =>
    request<GrantApplication>(`/grant-applications/${enc(id)}`),
  updateGrantApplication: (id: string, body: GrantApplicationUpdate) =>
    patch<GrantApplication>(`/grant-applications/${enc(id)}`, body),
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
  challenge_areas: ChallengeArea[];
  // not in the backend Innovation schema (only the offline mocks fill them), so always guard
  problem?: string;
  innovator?: string;
  target_group?: string[];
  readiness?: Readiness | null;
  cost_level?: CostLevel | null;
  city: string;
  page_url?: string | null;
  video_url?: string | null;
  status: PublicationStatus;
}

// POST /admin/innovations sends these as multipart form fields next to the pdf
export interface NewInnovationInput {
  title: string;
  summary: string;
  challenge_areas: ChallengeArea[];
  tags: string[];
  city: string;
  page_url: string | null;
}

// 202: the row is a draft until rag has embedded the pdf, then it publishes itself
export interface InnovationUploaded {
  id: string;
  title: string;
  status: PublicationStatus;
}

// PATCH /admin/innovations/{id}: omitted fields stay as they are, page_url: null clears it.
// the pdf and tags are not editable; summary edits do not re-index the pdf
export interface InnovationUpdate {
  title?: string;
  summary?: string;
  challenge_areas?: ChallengeArea[];
  city?: string;
  page_url?: string | null;
}

// mirrors backend settings.max_upload_bytes
export const MAX_PDF_BYTES = 10 * 1024 * 1024;

// every rating of one innovation, newest first (GET /admin/innovations/{id}/ratings)
export interface InnovationRating {
  rating: number;
  comment: string | null;
  // test_signup: rated by an accepted tester from the mail
  kind: "rating" | "test_signup";
  created_at: string;
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
  matches_by_location: {
    location: string;
    matches: number | null;
    note?: string | null;
  }[];
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
  social_canvas: {
    problem: string;
    solution: string;
    beneficiaries: string;
    resources?: string | null;
  };
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

// rated is set by the tester's rating from the mail, not by the admin
export type TestSignupStatus = "applied" | "accepted" | "rejected" | "completed" | "rated";
export type TestSignupDecision = Exclude<TestSignupStatus, "applied" | "rated">;

export interface TestSignup {
  id: string;
  innovation_id: string;
  innovation_title: string;
  // null for direct signups from an innovation page
  problem_report_id: string | null;
  email: string;
  status: TestSignupStatus;
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

export type ReportName =
  | "trends"
  | "critical"
  | "locations"
  | "gaps"
  | "innovations";

export const adminApi = {
  login: (body: LoginRequest) => post<void>("/admin/auth/login", body),
  logout: () => post<void>("/admin/auth/logout"),
  me: () => request<AdminMe>("/admin/auth/me"),
  inbox: () => request<Inbox>("/admin/inbox"),
  problemReports: () => request<ProblemReport[]>("/admin/problem-reports"),
  replyToProblemReport: (id: string, message: string) =>
    post<ProblemReport>(`/admin/problem-reports/${enc(id)}/reply`, { message }),
  ideas: () => request<Idea[]>("/admin/ideas"),
  replyToIdea: (id: string, message: string) =>
    post<Idea>(`/admin/ideas/${enc(id)}/reply`, { message }),
  setIdeaStatus: (id: string, status: IdeaStatus) =>
    post<Idea>(`/admin/ideas/${enc(id)}/status`, { status }),
  innovations: () =>
    request<Page<AdminInnovation>>("/admin/innovations?limit=100"),
  innovation: (id: string) =>
    request<AdminInnovation>(`/admin/innovations/${enc(id)}`),
  createInnovation: (input: NewInnovationInput, pdf: File) => {
    const body = new FormData();
    body.append("file", pdf);
    body.append("title", input.title);
    body.append("summary", input.summary);
    input.challenge_areas.forEach((a) => body.append("challenge_areas", a));
    input.tags.forEach((t) => body.append("tags", t));
    body.append("city", input.city);
    if (input.page_url) body.append("page_url", input.page_url);
    return request<InnovationUploaded>("/admin/innovations", { method: "POST", body });
  },
  updateInnovation: (id: string, body: InnovationUpdate) =>
    request<AdminInnovation>(`/admin/innovations/${enc(id)}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  replaceInnovationPdf: (id: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<InnovationUploaded>(`/admin/innovations/${enc(id)}/pdf`, { method: "POST", body: form });
  },
  setInnovationPublished: (id: string, published: boolean) =>
    post<AdminInnovation>(
      `/admin/innovations/${enc(id)}/${published ? "publish" : "unpublish"}`,
    ),
  innovationStats: (id: string) =>
    request<InnovationStats>(`/admin/innovations/${enc(id)}/stats`),
  innovationRatings: (id: string) =>
    request<InnovationRating[]>(`/admin/innovations/${enc(id)}/ratings`),
  innovationStatsReport: () =>
    request<InnovationStatsRow[]>("/admin/reports/innovations"),
  trends: () => request<TrendRow[]>("/admin/reports/trends"),
  critical: () => request<CriticalRow[]>("/admin/reports/critical"),
  gaps: () => request<GapRow[]>("/admin/reports/gaps"),
  testSignups: (innovationId?: string) =>
    request<TestSignup[]>(`/admin/test-signups${innovationId ? `?innovation_id=${enc(innovationId)}` : ""}`),
  setTestSignupStatus: (id: string, status: TestSignupDecision) =>
    post<TestSignup>(`/admin/test-signups/${enc(id)}/status`, { status }),
  grantCalls: () => request<GrantCall[]>("/admin/grant-calls"),
  setGrantCallOpen: (id: string, open: boolean) =>
    request<GrantCall>(`/admin/grant-calls/${enc(id)}`, {
      method: "PATCH",
      body: JSON.stringify({ open }),
    }),
  grantApplications: (status?: GrantApplicationStatus, grantCallId?: string) => {
    const q = new URLSearchParams();
    if (status) q.set("status", status);
    if (grantCallId) q.set("grant_call_id", grantCallId);
    const qs = q.toString();
    return request<GrantApplication[]>(`/admin/grant-applications${qs ? `?${qs}` : ""}`);
  },
  grantApplication: (id: string) =>
    request<GrantApplication>(`/admin/grant-applications/${enc(id)}`),
  threads: (status?: ModerationStatus, innovationId?: string) => {
    const q = new URLSearchParams();
    if (status) q.set("status", status);
    if (innovationId) q.set("innovation_id", innovationId);
    const qs = q.toString();
    return request<AdminThread[]>(`/admin/threads${qs ? `?${qs}` : ""}`);
  },
  setThreadStatus: (id: string, status: ModerationDecision) =>
    post<AdminThread>(`/admin/threads/${enc(id)}/status`, { status }),
  setReplyStatus: (id: string, status: ModerationDecision) =>
    post<AdminReply>(`/admin/threads/replies/${enc(id)}/status`, { status }),
  reportCsvUrl: (name: ReportName) =>
    `${API_URL}/admin/reports/${name}?format=csv`,
};
