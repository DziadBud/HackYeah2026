# postponed annotations: the services define list(), which shadows the builtin in later hints
from __future__ import annotations

import uuid

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.clients.gemini import GeminiClient
from app.db.models import Feedback, GeneratedDocument as DocumentRow, GrantCall as GrantCallRow
from app.db.models import GrantApplication as GrantApplicationRow
from app.db.models import Idea as IdeaRow, Innovation as InnovationRow, InnovationLike, InnovationProfile
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
from app.schemas.public.ratings import RatingState, RatingTarget
from app.schemas.admin.test_signups import TestSignupStatus
from app.schemas.public.threads import (
    ModerationStatus,
    Reply,
    ReplyCreate,
    ReplyKind,
    Submitted,
    Thread,
    ThreadCreate,
)
from app.services.admin.db import (
    grant_application_to_schema,
    grant_call_to_schema,
    innovation_to_schema,
    parse_uuid,
)
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
            llm=self._llm if data.use_ai else None,
        )
        applicant_type = data.applicant_type
        row = GrantApplicationRow(
            idea_id=idea.id,
            grant_call_id=call_row.id,
            status=GrantApplicationStatus.DRAFT.value,
            title=fields["title"],
            applicant_type=applicant_type.value,
            applicant=empty_applicant(applicant_type),
            description=fields["description"],
            innovativeness=fields["innovativeness"],
            problem_diagnosis=fields["problem_diagnosis"],
            beneficiaries=fields["beneficiaries"],
            expected_change=fields["expected_change"],
            future_vision=fields["future_vision"],
            action_plan=ActionPlan.model_validate(fields["action_plan"]).model_dump(),
            grant_amount_pln=None,
            team="",
            declarations=empty_declarations(applicant_type),
            email=data.email,
            generated_by=fields.get("generated_by"),
        )
        self._db.add(row)
        self._db.commit()
        return grant_application_to_schema(row)

    def get_grant_application(self, application_id: str) -> GrantApplication:
        row = self._db.get(GrantApplicationRow, parse_uuid(application_id))
        if row is None:
            raise NotFoundError(application_id)
        return grant_application_to_schema(row)

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
            new_type = ApplicantType(patch["applicant_type"])
            patch["applicant_type"] = new_type.value
            # switching type resets applicant/declarations unless provided in same request
            if "applicant" not in patch:
                patch["applicant"] = empty_applicant(new_type)
            if "declarations" not in patch:
                patch["declarations"] = empty_declarations(new_type)
        if "applicant" in patch and patch["applicant"] is not None:
            at = ApplicantType(patch.get("applicant_type", row.applicant_type))
            patch["applicant"] = normalize_applicant(at, patch["applicant"])
        if "declarations" in patch and patch["declarations"] is not None:
            at = ApplicantType(patch.get("applicant_type", row.applicant_type))
            patch["declarations"] = normalize_declarations(at, patch["declarations"])
        if "status" in patch and patch["status"] is not None:
            patch["status"] = GrantApplicationStatus(patch["status"]).value
        for key, value in patch.items():
            setattr(row, key, value)
        self._db.commit()
        return grant_application_to_schema(row)


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
        ids = [r.id for r in rows]
        ratings, profiles = self._ratings(ids), self._profiles(ids)
        return Page(
            items=[self._card(innovation_to_schema(r), ratings, profiles) for r in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

    def get(self, innovation_id: str) -> LibraryInnovation:
        row = _published(self._db, innovation_id)
        return self._card(innovation_to_schema(row), self._ratings([row.id]), self._profiles([row.id]))

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

    def sign_up_for_test(self, innovation_id: str, data: TestSignupCreate) -> TestSignupCreated:
        _published(self._db, innovation_id)
        row = TestSignup(innovation_id=innovation_id, email=data.email)
        self._db.add(row)
        self._db.commit()
        return TestSignupCreated(id=str(row.id), status=TestSignupStatus(row.status))


    def likes(self, innovation_id: str, client_id: str | None) -> LikeState:
        _published(self._db, innovation_id)
        return self._like_state(innovation_id, client_id)

    def set_like(self, innovation_id: str, client_id: str, liked: bool) -> LikeState:
        _published(self._db, innovation_id)
        client = uuid.UUID(client_id)
        if liked:
            # double clicks and two tabs hit the primary key; keep the one row
            self._db.execute(
                insert(InnovationLike)
                .values(innovation_id=innovation_id, client_id=client)
                .on_conflict_do_nothing()
            )
        else:
            self._db.execute(
                delete(InnovationLike).where(
                    InnovationLike.innovation_id == innovation_id,
                    InnovationLike.client_id == client,
                )
            )
        self._db.commit()
        return self._like_state(innovation_id, client_id)

    def _like_state(self, innovation_id: str, client_id: str | None) -> LikeState:
        count = self._db.scalar(
            select(func.count()).where(InnovationLike.innovation_id == innovation_id)
        ) or 0
        liked = client_id is not None and (
            self._db.get(InnovationLike, (innovation_id, uuid.UUID(client_id))) is not None
        )
        return LikeState(like_count=count, liked=liked)

    def _ratings(self, innovation_ids: list[str]) -> dict[str, tuple[float, int]]:
        if not innovation_ids:
            return {}
        rows = self._db.execute(
            select(Feedback.innovation_id, func.avg(Feedback.stars), func.count(Feedback.id))
            .where(Feedback.innovation_id.in_(innovation_ids))
            .group_by(Feedback.innovation_id)
        ).all()
        return {innovation_id: (float(avg), n) for innovation_id, avg, n in rows}

    def _profiles(self, innovation_ids: list[str]) -> dict[str, InnovationProfile]:
        if not innovation_ids:
            return {}
        rows = self._db.scalars(select(InnovationProfile).where(InnovationProfile.innovation_id.in_(innovation_ids)))
        return {r.innovation_id: r for r in rows}

    @staticmethod
    def _card(
        innovation: Innovation,
        ratings: dict[str, tuple[float, int]],
        profiles: dict[str, InnovationProfile],
    ) -> LibraryInnovation:
        avg, count = ratings.get(innovation.id, (None, 0))
        p = profiles.get(innovation.id)
        extra = (
            {
                "tagline": p.tagline,
                "program": p.program,
                "problem": p.problem,
                "target_group": p.target_group,
                "who_can_use": p.who_can_use,
                "effectiveness": p.effectiveness,
                "authors": list(p.authors or []),
                "photos": list(p.photos or []),
                "license_name": p.license_name,
                "license_url": p.license_url,
                "source_url": p.source_url,
            }
            if p
            else {}
        )
        return LibraryInnovation(**innovation.model_dump(), rating_avg=avg, rating_count=count, **extra)


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


RATEABLE = {TestSignupStatus.ACCEPTED.value, TestSignupStatus.COMPLETED.value}


class DbRatingService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _signup(self, signup_id: str, lock: bool = False) -> TestSignup | None:
        try:
            key = parse_uuid(signup_id)
        except NotFoundError:
            return None
        query = select(TestSignup).where(TestSignup.id == key)
        # two quick submits must not store two ratings
        return self._db.scalars(query.with_for_update() if lock else query).first()

    def _target(self, signup: TestSignup | None) -> RatingTarget:
        if signup is None:
            return RatingTarget(state=RatingState.UNAVAILABLE)
        if signup.status == TestSignupStatus.RATED.value:
            state = RatingState.RATED
        elif signup.status in RATEABLE:
            state = RatingState.OPEN
        else:
            state = RatingState.UNAVAILABLE
        return RatingTarget(
            state=state, innovation_id=signup.innovation_id, innovation_title=signup.innovation.title
        )

    def target(self, signup_id: str) -> RatingTarget:
        return self._target(self._signup(signup_id))

    def rate(self, signup_id: str, stars: int, comment: str) -> RatingTarget:
        signup = self._signup(signup_id, lock=True)
        target = self._target(signup)
        if target.state != RatingState.OPEN:
            self._db.rollback()
            return target
        assert signup is not None
        self._db.add(
            Feedback(
                innovation_id=signup.innovation_id,
                kind="test_signup",
                stars=stars,
                comment=comment.strip() or None,
            )
        )
        signup.status = TestSignupStatus.RATED.value
        self._db.commit()
        return target.model_copy(update={"state": RatingState.RATED})
