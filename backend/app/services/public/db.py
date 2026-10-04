# postponed annotations: the services define list(), which shadows the builtin in later hints
from __future__ import annotations

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.clients.gemini import GeminiClient
from app.db.models import Feedback, GeneratedDocument as DocumentRow, GrantCall as GrantCallRow
from app.db.models import GrantApplication as GrantApplicationRow
from app.db.models import Idea as IdeaRow, Innovation as InnovationRow
from app.db.models import ProblemReport as ProblemReportRow, TestSignup, Thread as ThreadRow
from app.db.models import ThreadReply
from app.schemas.admin.common import ChallengeArea, Page
from app.schemas.admin.grant_calls import GrantCall
from app.schemas.admin.ideas import IdeaStatus
from app.schemas.admin.innovations import Innovation, PublicationStatus
from app.schemas.public.documents import DocumentKind, GeneratedDocument, MiddlemanRequest
from app.schemas.public.grant_applications import (
    ActionPlan,
    ApplicantType,
    GrantApplication,
    GrantApplicationCreate,
    GrantApplicationStatus,
    GrantApplicationUpdate,
)
from app.schemas.public.ideas import IdeaCreate, IdeaCreated
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
from app.services.admin.db import grant_call_to_schema, innovation_to_schema, parse_uuid
from app.services.admin.innovation_upload import area_tag
from app.services.admin.errors import InvalidRequestError, NotFoundError
from app.services.public.drafts import grant_draft_fields, middleman_card
from app.services.public.interfaces import Retriever

MAX_MATCHES = 3
SIMILAR_REPORTS = 3
# pg_trgm similarity below this is noise for one-sentence problem descriptions
MIN_SIMILARITY = 0.1


def _published(db: Session, innovation_id: str) -> InnovationRow:
    row = db.get(InnovationRow, innovation_id)
    if row is None or row.status != PublicationStatus.PUBLISHED.value:
        raise NotFoundError(innovation_id)
    return row


def _document(row: DocumentRow) -> GeneratedDocument:
    return GeneratedDocument(
        id=str(row.id),
        kind=DocumentKind(row.kind),
        innovation_id=row.innovation_id,
        idea_id=str(row.idea_id) if row.idea_id else None,
        grant_call_id=str(row.grant_call_id) if row.grant_call_id else None,
        output=row.output,
        created_at=row.created_at,
    )


def _grant_application(row: GrantApplicationRow) -> GrantApplication:
    return GrantApplication(
        id=str(row.id),
        idea_id=str(row.idea_id) if row.idea_id else None,
        grant_call_id=str(row.grant_call_id) if row.grant_call_id else None,
        status=GrantApplicationStatus(row.status),
        title=row.title,
        applicant_type=ApplicantType(row.applicant_type),
        applicant=row.applicant or {},
        description=row.description,
        innovativeness=row.innovativeness,
        problem_diagnosis=row.problem_diagnosis,
        beneficiaries=row.beneficiaries,
        expected_change=row.expected_change,
        future_vision=row.future_vision,
        action_plan=ActionPlan.model_validate(row.action_plan or {}),
        grant_amount_pln=row.grant_amount_pln,
        team=row.team,
        declarations=row.declarations or {},
        email=row.email,
        generated_by=row.generated_by,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class DbMatchService:
    def __init__(self, db: Session, rag: Retriever) -> None:
        self._db = db
        self._rag = rag

    def match(self, data: MatchRequest, test_signup: bool) -> MatchResponse:
        if test_signup and not data.email:
            raise InvalidRequestError("email is required to sign up for testing")

        # before any write: when rag is down nothing is stored and the user can retry
        result = self._rag.query(data.text, MAX_MATCHES)
        rows = {
            r.id: r
            for r in self._db.scalars(
                select(InnovationRow).where(
                    InnovationRow.id.in_(result.innovation_ids),
                    InnovationRow.status == PublicationStatus.PUBLISHED.value,
                )
            ).all()
        }
        # keep rag's ranking
        matches = [innovation_to_schema(rows[i]) for i in result.innovation_ids if i in rows]

        # before the insert, so the new report doesn't come back as similar to itself
        similar = self._similar_reports(data.text, data.city)
        report = ProblemReportRow(
            text=data.text,
            challenge_area=matches[0].challenge_areas[0].value
            if matches and matches[0].challenge_areas
            else None,
            city=data.city,
            matched_innovation_ids=[i.id for i in matches],
            email=data.email,
        )
        self._db.add(report)
        self._db.flush()

        signups = []
        if test_signup:
            signups = [
                TestSignup(innovation_id=i.id, problem_report_id=report.id, email=data.email)
                for i in matches
            ]
            self._db.add_all(signups)
        self._db.commit()

        return MatchResponse(
            problem_report_id=str(report.id),
            answer=result.answer,
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
            test_signup_ids=[str(s.id) for s in signups],
        )

    def _similar_reports(self, text: str, city: str) -> list[SimilarProblemReport]:
        similarity = func.similarity(ProblemReportRow.text, text)
        rows = self._db.scalars(
            select(ProblemReportRow)
            .where(ProblemReportRow.hidden.is_(False), similarity > MIN_SIMILARITY)
            # same city first, then the closest text
            .order_by((func.lower(ProblemReportRow.city) == city.lower()).desc(), similarity.desc())
            .limit(SIMILAR_REPORTS)
        ).all()
        return [
            SimilarProblemReport(
                id=str(r.id),
                text=r.text,
                city=r.city,
                support_count=r.support_count,
                admin_reply=r.admin_reply,
            )
            for r in rows
        ]


class DbProblemReportService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, problem_report_id: str) -> PublicProblemReport:
        row = self._db.get(ProblemReportRow, parse_uuid(problem_report_id))
        if row is None or row.hidden:
            raise NotFoundError(problem_report_id)
        return PublicProblemReport(
            id=str(row.id),
            text=row.text,
            challenge_area=row.challenge_area
            if row.challenge_area in {a.value for a in ChallengeArea}
            else None,
            city=row.city,
            support_count=row.support_count,
            admin_reply=row.admin_reply,
            created_at=row.created_at,
        )

    def support(self, problem_report_id: str) -> SupportResponse:
        # one atomic update, so concurrent "mnie też" clicks don't lose increments
        count = self._db.scalar(
            update(ProblemReportRow)
            .where(
                ProblemReportRow.id == parse_uuid(problem_report_id),
                ProblemReportRow.hidden.is_(False),
            )
            .values(support_count=ProblemReportRow.support_count + 1)
            .returning(ProblemReportRow.support_count)
        )
        if count is None:
            raise NotFoundError(problem_report_id)
        self._db.commit()
        return SupportResponse(support_count=count)


class DbIdeaService:
    def __init__(self, db: Session, llm: GeminiClient | None = None) -> None:
        self._db = db
        self._llm = llm

    def create(self, data: IdeaCreate) -> IdeaCreated:
        row = IdeaRow(
            summary=data.summary,
            essence=data.essence,
            target_group=data.target_group,
            stage=data.stage.value,
            social_canvas=data.social_canvas.model_dump() if data.social_canvas else {},
            status=IdeaStatus.NEW.value,
            email=data.email,
        )
        self._db.add(row)
        self._db.commit()
        return IdeaCreated(id=str(row.id), status=IdeaStatus.NEW)

    def grant_application(self, idea_id: str, data: GrantApplicationCreate) -> GrantApplication:
        idea = self._db.get(IdeaRow, parse_uuid(idea_id))
        if idea is None:
            raise NotFoundError(idea_id)
        if idea.status == IdeaStatus.REJECTED.value:
            raise InvalidRequestError("this idea was rejected")
        call_row = self._db.get(GrantCallRow, parse_uuid(data.grant_call_id))
        if call_row is None:
            raise NotFoundError(data.grant_call_id)
        if not call_row.open:
            raise InvalidRequestError("this grant call is closed")
        fields = grant_draft_fields(
            summary=idea.summary,
            essence=idea.essence,
            target_group=idea.target_group,
            stage=idea.stage,
            social_canvas=idea.social_canvas,
            notes=data.notes,
            llm=self._llm,
        )
        row = GrantApplicationRow(
            idea_id=idea.id,
            grant_call_id=call_row.id,
            status=GrantApplicationStatus.DRAFT.value,
            title=fields["title"],
            applicant_type=ApplicantType.PERSON.value,
            applicant={},
            description=fields["description"],
            innovativeness=fields["innovativeness"],
            problem_diagnosis=fields["problem_diagnosis"],
            beneficiaries=fields["beneficiaries"],
            expected_change=fields["expected_change"],
            future_vision=fields["future_vision"],
            action_plan=fields["action_plan"],
            grant_amount_pln=None,
            team="",
            declarations={},
            email=data.email,
            generated_by=fields.get("generated_by"),
        )
        self._db.add(row)
        self._db.commit()
        return _grant_application(row)

    def get_grant_application(self, application_id: str) -> GrantApplication:
        row = self._db.get(GrantApplicationRow, parse_uuid(application_id))
        if row is None:
            raise NotFoundError(application_id)
        return _grant_application(row)

    def update_grant_application(
        self, application_id: str, data: GrantApplicationUpdate
    ) -> GrantApplication:
        row = self._db.get(GrantApplicationRow, parse_uuid(application_id))
        if row is None:
            raise NotFoundError(application_id)
        if row.status == GrantApplicationStatus.SUBMITTED.value:
            raise InvalidRequestError("this application was already submitted")
        patch = data.model_dump(exclude_unset=True)
        if "action_plan" in patch and patch["action_plan"] is not None:
            patch["action_plan"] = ActionPlan.model_validate(patch["action_plan"]).model_dump()
        if "applicant_type" in patch and patch["applicant_type"] is not None:
            patch["applicant_type"] = ApplicantType(patch["applicant_type"]).value
        if "status" in patch and patch["status"] is not None:
            patch["status"] = GrantApplicationStatus(patch["status"]).value
        for key, value in patch.items():
            setattr(row, key, value)
        self._db.commit()
        return _grant_application(row)


class DbLibraryService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(
        self, challenge_area: ChallengeArea | None, q: str | None, limit: int, offset: int
    ) -> Page[LibraryInnovation]:
        query = select(InnovationRow).where(InnovationRow.status == PublicationStatus.PUBLISHED.value)
        if challenge_area is not None:
            query = query.where(InnovationRow.tags.any(area_tag(challenge_area)))
        if q:
            query = query.where(InnovationRow.title.ilike(f"%{q}%") | InnovationRow.summary.ilike(f"%{q}%"))
        total = self._db.scalar(select(func.count()).select_from(query.subquery())) or 0
        rows = self._db.scalars(query.order_by(InnovationRow.title).limit(limit).offset(offset)).all()
        ratings = self._ratings([r.id for r in rows])
        return Page(
            items=[self._card(innovation_to_schema(r), ratings) for r in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

    def get(self, innovation_id: str) -> LibraryInnovation:
        row = _published(self._db, innovation_id)
        return self._card(innovation_to_schema(row), self._ratings([row.id]))

    def add_feedback(self, innovation_id: str, data: FeedbackCreate) -> FeedbackCreated:
        _published(self._db, innovation_id)
        kind = "rating"
        if data.test_signup_id:
            signup = self._db.get(TestSignup, parse_uuid(data.test_signup_id))
            if signup is None or signup.innovation_id != innovation_id:
                raise InvalidRequestError("this test signup is not for this innovation")
            # rag's feedback has no signup fk; the id is only validated
            kind = "test_signup"
        row = Feedback(
            innovation_id=innovation_id,
            kind=kind,
            stars=data.stars,
            comment=data.comment or None,
        )
        self._db.add(row)
        self._db.commit()
        return FeedbackCreated(id=str(row.id))

    def _ratings(self, innovation_ids: list[str]) -> dict[str, tuple[float, int]]:
        if not innovation_ids:
            return {}
        rows = self._db.execute(
            select(Feedback.innovation_id, func.avg(Feedback.stars), func.count(Feedback.id))
            .where(Feedback.innovation_id.in_(innovation_ids))
            .group_by(Feedback.innovation_id)
        ).all()
        return {innovation_id: (float(avg), n) for innovation_id, avg, n in rows}

    @staticmethod
    def _card(innovation: Innovation, ratings: dict[str, tuple[float, int]]) -> LibraryInnovation:
        avg, count = ratings.get(innovation.id, (None, 0))
        return LibraryInnovation(**innovation.model_dump(), rating_avg=avg, rating_count=count)


class DbThreadService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(self, innovation_id: str) -> list[Thread]:
        _published(self._db, innovation_id)
        published = ModerationStatus.PUBLISHED.value
        threads = self._db.scalars(
            select(ThreadRow)
            .where(ThreadRow.innovation_id == innovation_id, ThreadRow.status == published)
            .order_by(ThreadRow.created_at.desc())
        ).all()
        return [
            Thread(
                id=str(t.id),
                innovation_id=t.innovation_id,
                title=t.title,
                body=t.body,
                author_label=t.author_label,
                created_at=t.created_at,
                replies=[
                    Reply(
                        id=str(r.id),
                        body=r.body,
                        author_label=r.author_label,
                        kind=ReplyKind(r.kind),
                        created_at=r.created_at,
                    )
                    for r in sorted(t.replies, key=lambda r: r.created_at)
                    if r.status == published
                ],
            )
            for t in threads
        ]

    def create(self, innovation_id: str, data: ThreadCreate) -> Submitted:
        _published(self._db, innovation_id)
        row = ThreadRow(
            innovation_id=innovation_id,
            title=data.title,
            body=data.body,
            author_label=data.author_label,
            email=data.email,
            status=ModerationStatus.PENDING.value,
        )
        self._db.add(row)
        self._db.commit()
        return Submitted(id=str(row.id), status=ModerationStatus.PENDING)

    def reply(self, thread_id: str, data: ReplyCreate) -> Submitted:
        thread = self._db.get(ThreadRow, parse_uuid(thread_id))
        if thread is None or thread.status != ModerationStatus.PUBLISHED.value:
            raise NotFoundError(thread_id)
        row = ThreadReply(
            thread_id=thread.id,
            body=data.body,
            author_label=data.author_label,
            email=data.email,
            kind=ReplyKind.PRACTITIONER.value,
            status=ModerationStatus.PENDING.value,
        )
        self._db.add(row)
        self._db.commit()
        return Submitted(id=str(row.id), status=ModerationStatus.PENDING)


class DbDocumentService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def middleman(self, data: MiddlemanRequest) -> GeneratedDocument:
        innovation = innovation_to_schema(_published(self._db, data.innovation_id))
        row = DocumentRow(
            kind=DocumentKind.MIDDLEMAN.value,
            innovation_id=innovation.id,
            input=data.model_dump(mode="json", exclude={"email", "consent"}),
            output=middleman_card(innovation, data),
            email=data.email,
        )
        self._db.add(row)
        self._db.commit()
        return _document(row)


class DbKnowledgeService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def open_grant_calls(self) -> list[GrantCall]:
        rows = self._db.scalars(
            select(GrantCallRow).where(GrantCallRow.open.is_(True)).order_by(GrantCallRow.deadline)
        ).all()
        return [grant_call_to_schema(r) for r in rows]
