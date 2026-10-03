import re
import unicodedata
import uuid
from datetime import UTC, datetime

from app.schemas.admin.common import ChallengeArea, Page
from app.schemas.admin.grant_calls import GrantCall
from app.schemas.admin.ideas import Idea, IdeaStatus, SocialCanvas
from app.schemas.admin.innovations import Innovation, PublicationStatus
from app.schemas.admin.problem_reports import ProblemReport
from app.schemas.public.documents import DocumentKind, GeneratedDocument, MiddlemanRequest
from app.schemas.public.ideas import GrantApplicationRequest, IdeaCreate, IdeaCreated
from app.schemas.public.innovations import FeedbackCreate, FeedbackCreated, LibraryInnovation
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
from app.services.admin.errors import InvalidRequestError, NotFoundError
from app.services.admin.mock import (
    MockGrantCallAdminService,
    MockIdeaAdminService,
    MockInnovationAdminService,
    MockProblemReportAdminService,
)

# public mocks read and write the admin mocks, so a public action shows up in the admin panel.
# stand-ins until the db layer and the rag client land; word overlap replaces rag retrieval

MAX_MATCHES = 3


def _now() -> datetime:
    return datetime.now(UTC)


def _new_id() -> str:
    return str(uuid.uuid4())


def _words(text: str) -> set[str]:
    # crude polish stemming: diacritics folded, first 5 letters of every word longer than 3
    folded = unicodedata.normalize("NFKD", text.lower().replace("ł", "l")).encode("ascii", "ignore").decode()
    return {w[:5] for w in re.findall(r"\w+", folded) if len(w) > 3}


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

        query = _words(data.text)
        published = self._innovations.list(PublicationStatus.PUBLISHED, None, 1000, 0).items
        scored = sorted(
            ((len(query & _words(f"{i.title} {i.summary} {i.problem}")), i) for i in published),
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
            innovations=[
                MatchedInnovation(
                    id=i.id,
                    title=i.title,
                    summary=i.summary,
                    why=f"Pasuje, bo dotyczy: {', '.join(a.value for a in i.challenge_areas) or i.title}.",
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
        scored = [(len(query & _words(r.text)), r.location.lower() == city.lower(), r) for r in reports]
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

    def grant_application(self, idea_id: str, data: GrantApplicationRequest) -> GeneratedDocument:
        idea = self._ideas.get(idea_id)
        if idea.status == IdeaStatus.REJECTED:
            raise InvalidRequestError("this idea was rejected")
        call = next((c for c in self._grant_calls.list() if c.id == data.grant_call_id), None)
        if call is None:
            raise NotFoundError(data.grant_call_id)
        if not call.open:
            raise InvalidRequestError("this grant call is closed")
        # stand-in for the llm: one section per form section, filled from the idea card
        sections = [
            f"## {s.title}\n{idea.summary if i == 0 else '[uzupełnij]'}"
            for i, s in enumerate(call.sections)
        ]
        return self._documents.add(
            GeneratedDocument(
                id=_new_id(),
                kind=DocumentKind.GRANT_APPLICATION,
                idea_id=idea.id,
                grant_call_id=call.id,
                output="\n\n".join(sections) or idea.summary,
                created_at=_now(),
            )
        )


class MockLibraryService:
    def __init__(self, innovations: MockInnovationAdminService) -> None:
        self._innovations = innovations
        self._feedback: dict[str, list[FeedbackCreate]] = {}

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

    def _card(self, innovation: Innovation) -> LibraryInnovation:
        stars = [f.stars for f in self._feedback.get(innovation.id, [])]
        return LibraryInnovation(
            **innovation.model_dump(),
            rating_avg=sum(stars) / len(stars) if stars else None,
            rating_count=len(stars),
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
        # stand-in for the llm service card
        output = (
            f"Usługa: {innovation.title} dla instytucji typu {data.institution_type.value}\n"
            f"Potrzeba: {data.needs}\n"
            f"Na czym polega: {innovation.summary}\n"
            f"Koszt: do oszacowania (poziom {innovation.cost_level.value})"
        )
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
