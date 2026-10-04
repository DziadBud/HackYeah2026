import uuid
from datetime import UTC, datetime

from app.schemas.admin.common import ChallengeArea, Page
from app.schemas.admin.grant_calls import GrantCall
from app.schemas.admin.ideas import Idea, IdeaStatus, SocialCanvas
from app.schemas.admin.innovations import Innovation, PublicationStatus
from app.schemas.admin.problem_reports import ProblemReport
from app.schemas.public.documents import DocumentKind, GeneratedDocument, MiddlemanRequest
from app.schemas.public.grant_applications import (
    ActionPlan,
    ApplicantType,
    GrantApplication,
    GrantApplicationCreate,
    GrantApplicationStatus,
    GrantApplicationUpdate,
    empty_applicant,
    empty_declarations,
    normalize_applicant,
    normalize_declarations,
)
from app.schemas.public.ideas import IdeaCreate, IdeaCreated
from app.schemas.public.innovations import (
    FeedbackCreate,
    FeedbackCreated,
    LibraryInnovation,
    TestSignupCreate,
    TestSignupCreated,
    LikeState,
)
from app.schemas.public.match import (
    MatchedInnovation,
    MatchRequest,
    MatchResponse,
    SimilarProblemReport,
)
from app.schemas.public.problem_reports import PublicProblemReport, SupportResponse
from app.schemas.public.threads import (
    ModerationStatus,
    Reply,
    ReplyCreate,
    ReplyKind,
    Submitted,
    Thread,
    ThreadCreate,
)
from app.schemas.public.ratings import RatingState, RatingTarget
from app.services.admin.errors import InvalidRequestError, NotFoundError
from app.services.public.drafts import grant_draft_fields, middleman_card, overlap, words
from app.services.admin.mock import (
    MockGrantCallAdminService,
    MockIdeaAdminService,
    MockInnovationAdminService,
    MockProblemReportAdminService,
    MockTestSignupAdminService,
)

# public mocks read and write the admin mocks, so a public action shows up in the admin panel.
# stand-ins until the db layer and the rag client land; word overlap replaces rag retrieval

MAX_MATCHES = 3


def _now() -> datetime:
    return datetime.now(UTC)


def _new_id() -> str:
    return str(uuid.uuid4())


def _published(innovations: MockInnovationAdminService, innovation_id: str) -> Innovation:
    innovation = innovations.get(innovation_id)
    if innovation.status != PublicationStatus.PUBLISHED:
        raise NotFoundError(innovation_id)
    return innovation


class MockMatchService:
    def __init__(
        self,
        innovations: MockInnovationAdminService,
        problem_reports: MockProblemReportAdminService,
    ) -> None:
        self._innovations = innovations
        self._problem_reports = problem_reports
        self.test_signups: dict[str, dict[str, str]] = {}

    def match(self, data: MatchRequest, test_signup: bool) -> MatchResponse:
        if test_signup and not data.email:
            raise InvalidRequestError("email is required to sign up for testing")

        query = words(data.text)
        published = self._innovations.list(PublicationStatus.PUBLISHED, None, 1000, 0).items
        scored = sorted(
            ((overlap(query, i), i) for i in published),
            key=lambda pair: pair[0],
            reverse=True,
        )
        matches = [i for score, i in scored[:MAX_MATCHES] if score > 0]

        similar = self._similar_reports(query, data.city)
        report = ProblemReport(
            id=_new_id(),
            text=data.text,
            challenge_area=matches[0].challenge_areas[0] if matches and matches[0].challenge_areas else None,
            location=data.city,
            support_count=0,
            is_critical=False,
            criticality_score=0.0,
            created_at=_now(),
        )
        self._problem_reports.add(report)

        signup_ids = []
        if test_signup:
            for innovation in matches:
                signup_id = _new_id()
                self.test_signups[signup_id] = {
                    "innovation_id": innovation.id,
                    "problem_report_id": report.id,
                    "email": data.email or "",
                    "status": "applied",
                }
                signup_ids.append(signup_id)

        return MatchResponse(
            problem_report_id=report.id,
            answer="Zgłoszenie dotyczy problemu opisanego przez mieszkańca.",
            innovations=[
                MatchedInnovation(
                    id=i.id,
                    title=i.title,
                    summary=i.summary,
                    tags=[f"area:{a.value}" for a in i.challenge_areas],
                    city=i.city,
                )
                for i in matches
            ],
            similar_reports=similar,
            test_signup_ids=signup_ids,
        )

    def _similar_reports(self, query: set[str], city: str) -> list[SimilarProblemReport]:
        reports = self._problem_reports.list(None, None, None)
        scored = [(len(query & words(r.text)), r.location.lower() == city.lower(), r) for r in reports]
        best = sorted((s for s in scored if s[0] > 0), key=lambda s: (s[1], s[0]), reverse=True)
        return [
            SimilarProblemReport(
                id=r.id,
                text=r.text,
                city=r.location,
                support_count=r.support_count,
                admin_reply=r.admin_reply,
            )
            for _, _, r in best[:3]
        ]


class MockProblemReportService:
    def __init__(self, problem_reports: MockProblemReportAdminService) -> None:
        self._problem_reports = problem_reports

    def get(self, problem_report_id: str) -> PublicProblemReport:
        r = self._problem_reports.get(problem_report_id)
        return PublicProblemReport(
            id=r.id,
            text=r.text,
            challenge_area=r.challenge_area,
            city=r.location,
            support_count=r.support_count,
            admin_reply=r.admin_reply,
            created_at=r.created_at,
        )

    def support(self, problem_report_id: str) -> SupportResponse:
        return SupportResponse(support_count=self._problem_reports.support(problem_report_id).support_count)


class MockDocumentStore:
    def __init__(self) -> None:
        self.items: dict[str, GeneratedDocument] = {}

    def add(self, doc: GeneratedDocument) -> GeneratedDocument:
        self.items[doc.id] = doc
        return doc


class MockIdeaService:
    def __init__(
        self,
        ideas: MockIdeaAdminService,
        grant_calls: MockGrantCallAdminService,
        documents: MockDocumentStore,
    ) -> None:
        self._ideas = ideas
        self._grant_calls = grant_calls
        self._documents = documents
        self._applications: dict[str, GrantApplication] = {}

    def create(self, data: IdeaCreate) -> IdeaCreated:
        idea = Idea(
            id=_new_id(),
            summary=data.summary,
            essence=data.essence,
            target_group=data.target_group,
            stage=data.stage,
            social_canvas=data.social_canvas
            or SocialCanvas(problem="", solution="", beneficiaries=data.target_group),
            status=IdeaStatus.NEW,
            created_at=_now(),
        )
        self._ideas.add(idea)
        return IdeaCreated(id=idea.id, status=idea.status)

    def grant_application(self, idea_id: str, data: GrantApplicationCreate) -> GrantApplication:
        idea = self._ideas.get(idea_id)
        if idea.status == IdeaStatus.REJECTED:
            raise InvalidRequestError("this idea was rejected")
        call = next((c for c in self._grant_calls.list() if c.id == data.grant_call_id), None)
        if call is None:
            raise NotFoundError(data.grant_call_id)
        if not call.open:
            raise InvalidRequestError("this grant call is closed")
        fields = grant_draft_fields(
            summary=idea.summary,
            essence=idea.essence,
            target_group=idea.target_group,
            stage=idea.stage.value,
            social_canvas=idea.social_canvas.model_dump(),
            notes=data.notes,
        )
        now = _now()
        app = GrantApplication(
            id=_new_id(),
            idea_id=idea.id,
            grant_call_id=call.id,
            status=GrantApplicationStatus.DRAFT,
            title=fields["title"],
            applicant_type=data.applicant_type,
            applicant=empty_applicant(data.applicant_type),
            description=fields["description"],
            innovativeness=fields["innovativeness"],
            problem_diagnosis=fields["problem_diagnosis"],
            beneficiaries=fields["beneficiaries"],
            expected_change=fields["expected_change"],
            future_vision=fields["future_vision"],
            action_plan=ActionPlan.model_validate(fields["action_plan"]),
            grant_amount_pln=None,
            team="",
            declarations=empty_declarations(data.applicant_type),
            email=data.email,
            generated_by=fields.get("generated_by"),
            created_at=now,
            updated_at=now,
        )
        self._applications[app.id] = app
        return app

    def get_grant_application(self, application_id: str) -> GrantApplication:
        try:
            return self._applications[application_id]
        except KeyError:
            raise NotFoundError(application_id) from None

    def update_grant_application(
        self, application_id: str, data: GrantApplicationUpdate
    ) -> GrantApplication:
        current = self.get_grant_application(application_id)
        if current.status == GrantApplicationStatus.SUBMITTED:
            raise InvalidRequestError("this application was already submitted")
        patch = data.model_dump(exclude_unset=True)
        if "action_plan" in patch and patch["action_plan"] is not None:
            patch["action_plan"] = ActionPlan.model_validate(patch["action_plan"])
        if "applicant_type" in patch and patch["applicant_type"] is not None:
            new_type = ApplicantType(patch["applicant_type"])
            if "applicant" not in patch:
                patch["applicant"] = empty_applicant(new_type)
            if "declarations" not in patch:
                patch["declarations"] = empty_declarations(new_type)
        at = ApplicantType(patch.get("applicant_type", current.applicant_type))
        if "applicant" in patch and patch["applicant"] is not None:
            patch["applicant"] = normalize_applicant(at, patch["applicant"])
        if "declarations" in patch and patch["declarations"] is not None:
            patch["declarations"] = normalize_declarations(at, patch["declarations"])
        updated = GrantApplication.model_validate(
            current.model_copy(update=patch | {"updated_at": _now()}).model_dump()
        )
        self._applications[application_id] = updated
        return updated


class MockLibraryService:
    def __init__(
        self,
        innovations: MockInnovationAdminService,
        test_signups: MockTestSignupAdminService | None = None,
    ) -> None:
        self._innovations = innovations
        self._test_signups = test_signups or MockTestSignupAdminService()
        self._feedback: dict[str, list[FeedbackCreate]] = {}
        self._likes: dict[str, set[str]] = {}
        # innovation_profiles rows; tests add their own
        self.profiles: dict[str, dict] = {}

    def list(
        self, challenge_area: ChallengeArea | None, q: str | None, limit: int, offset: int
    ) -> Page[LibraryInnovation]:
        items = [
            self._card(i)
            for i in self._innovations.list(PublicationStatus.PUBLISHED, q, 1000, 0).items
            if challenge_area is None or challenge_area in i.challenge_areas
        ]
        return Page(items=items[offset : offset + limit], total=len(items), limit=limit, offset=offset)

    def get(self, innovation_id: str) -> LibraryInnovation:
        return self._card(_published(self._innovations, innovation_id))

    def add_feedback(self, innovation_id: str, data: FeedbackCreate) -> FeedbackCreated:
        _published(self._innovations, innovation_id)
        self._feedback.setdefault(innovation_id, []).append(data)
        return FeedbackCreated(id=_new_id())

    def sign_up_for_test(self, innovation_id: str, data: TestSignupCreate) -> TestSignupCreated:
        signup = self._test_signups.add(_published(self._innovations, innovation_id), data.email)
        return TestSignupCreated(id=signup.id, status=signup.status)


    def likes(self, innovation_id: str, client_id: str | None) -> LikeState:
        _published(self._innovations, innovation_id)
        clients = self._likes.get(innovation_id, set())
        return LikeState(like_count=len(clients), liked=client_id in clients)

    def set_like(self, innovation_id: str, client_id: str, liked: bool) -> LikeState:
        _published(self._innovations, innovation_id)
        clients = self._likes.setdefault(innovation_id, set())
        if liked:
            clients.add(client_id)
        else:
            clients.discard(client_id)
        return self.likes(innovation_id, client_id)

    def _card(self, innovation: Innovation) -> LibraryInnovation:
        stars = [f.stars for f in self._feedback.get(innovation.id, [])]
        return LibraryInnovation(
            **innovation.model_dump(),
            rating_avg=sum(stars) / len(stars) if stars else None,
            rating_count=len(stars),
            **self.profiles.get(innovation.id, {}),
        )


class MockThreadService:
    def __init__(self, innovations: MockInnovationAdminService) -> None:
        self._innovations = innovations
        self._threads: dict[str, dict] = {}
        self._seed()

    def list(self, innovation_id: str) -> list[Thread]:
        _published(self._innovations, innovation_id)
        return [
            Thread(
                **{k: v for k, v in t.items() if k not in ("status", "replies", "helpful_count")},
                replies=[r["reply"] for r in t["replies"] if r["status"] == ModerationStatus.PUBLISHED],
            )
            for t in self._threads.values()
            if t["innovation_id"] == innovation_id and t["status"] == ModerationStatus.PUBLISHED
        ]

    def create(self, innovation_id: str, data: ThreadCreate) -> Submitted:
        _published(self._innovations, innovation_id)
        thread_id = _new_id()
        self._threads[thread_id] = self._thread(
            thread_id, innovation_id, data.title, data.body, data.author_label, ModerationStatus.PENDING
        )
        return Submitted(id=thread_id, status=ModerationStatus.PENDING)

    def reply(self, thread_id: str, data: ReplyCreate) -> Submitted:
        thread = self._published_thread(thread_id)
        reply = Reply(
            id=_new_id(),
            body=data.body,
            author_label=data.author_label,
            kind=ReplyKind.PRACTITIONER,
            created_at=_now(),
        )
        thread["replies"].append({"reply": reply, "status": ModerationStatus.PENDING})
        return Submitted(id=reply.id, status=ModerationStatus.PENDING)


    def _published_thread(self, thread_id: str) -> dict:
        thread = self._threads.get(thread_id)
        if thread is None or thread["status"] != ModerationStatus.PUBLISHED:
            raise NotFoundError(thread_id)
        return thread

    @staticmethod
    def _thread(thread_id, innovation_id, title, body, author_label, status) -> dict:
        return {
            "id": thread_id,
            "innovation_id": innovation_id,
            "title": title,
            "body": body,
            "author_label": author_label,
            "helpful_count": 0,
            "created_at": _now(),
            "status": status,
            "replies": [],
        }

    def _seed(self) -> None:
        thread = self._thread(
            "thread-wibraap-1",
            "wibraap",
            "Czy kamizelka działa w szkole?",
            "Chcemy przetestować Wibraap w klasie integracyjnej. Ktoś już próbował?",
            "Nauczycielka, Tarnów",
            ModerationStatus.PUBLISHED,
        )
        thread["replies"].append(
            {
                "reply": Reply(
                    id="reply-wibraap-1",
                    body="Tak, w naszej szkole sprawdza się na lekcjach muzyki.",
                    author_label="Dyrektor szkoły, Nowy Sącz",
                    kind=ReplyKind.PRACTITIONER,
                    created_at=_now(),
                ),
                "status": ModerationStatus.PUBLISHED,
            }
        )
        self._threads[thread["id"]] = thread


class MockDocumentService:
    def __init__(self, innovations: MockInnovationAdminService, documents: MockDocumentStore) -> None:
        self._innovations = innovations
        self._documents = documents

    def middleman(self, data: MiddlemanRequest) -> GeneratedDocument:
        innovation = _published(self._innovations, data.innovation_id)
        output = middleman_card(innovation, data)
        return self._documents.add(
            GeneratedDocument(
                id=_new_id(),
                kind=DocumentKind.MIDDLEMAN,
                innovation_id=innovation.id,
                output=output,
                created_at=_now(),
            )
        )


class MockKnowledgeService:
    def __init__(self, innovations: MockInnovationAdminService, grant_calls: MockGrantCallAdminService) -> None:
        self._innovations = innovations
        self._grant_calls = grant_calls

    def open_grant_calls(self) -> list[GrantCall]:
        return [c for c in self._grant_calls.list() if c.open]


class MockRatingService:
    def __init__(self) -> None:
        self.feedback: list[tuple[str, int, str]] = []
        self._signups: dict[str, tuple[str, str, str]] = {
            # id: (status, innovation_id, title)
            "signup-accepted": ("accepted", "wibraap", "Wibraap"),
            "signup-applied": ("applied", "wibraap", "Wibraap"),
        }

    def target(self, signup_id: str) -> RatingTarget:
        if signup_id not in self._signups:
            return RatingTarget(state=RatingState.UNAVAILABLE)
        status, innovation_id, title = self._signups[signup_id]
        state = {"accepted": RatingState.OPEN, "completed": RatingState.OPEN, "rated": RatingState.RATED}.get(
            status, RatingState.UNAVAILABLE
        )
        return RatingTarget(state=state, innovation_id=innovation_id, innovation_title=title)

    def rate(self, signup_id: str, stars: int, comment: str) -> RatingTarget:
        target = self.target(signup_id)
        if target.state != RatingState.OPEN:
            return target
        self.feedback.append((signup_id, stars, comment))
        _, innovation_id, title = self._signups[signup_id]
        self._signups[signup_id] = ("rated", innovation_id, title)
        return target.model_copy(update={"state": RatingState.RATED})
