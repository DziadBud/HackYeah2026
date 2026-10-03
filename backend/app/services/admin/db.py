import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, literal_column, or_, select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from app.db.models import Feedback, GrantCall as GrantCallRow, Idea as IdeaRow
from app.db.models import Innovation as InnovationRow, ProblemReport as ProblemReportRow
from app.db.models import TestSignup, Thread as ThreadRow, ThreadReply as ThreadReplyRow
from app.schemas.admin.common import ChallengeArea, Page
from app.schemas.admin.grant_calls import GrantCall, GrantCallCreate, GrantCallUpdate
from app.schemas.admin.ideas import Idea, IdeaStatus, SocialCanvas
from app.schemas.admin.inbox import Inbox
from app.schemas.admin.innovations import (
    AreaMatches,
    FeedbackComment,
    Innovation,
    InnovationFeedback,
    InnovationStats,
    InnovationStatsRow,
    InnovationUpdate,
    LocationMatches,
    MatchedProblemReport,
    PublicationStatus,
    SignupCounts,
    WeeklyMatches,
)
from app.schemas.admin.problem_reports import ProblemReport
from app.schemas.admin.reports import CriticalRow, GapRow, LocationRow, TrendRow
from app.schemas.admin.threads import AdminReply, AdminThread
from app.schemas.public.threads import ModerationStatus, ReplyKind
from app.services.admin.errors import NotFoundError
from app.services.admin.innovation_upload import NewInnovation, areas_from_tags, with_area_tags

MIN_LOCATION_PROBLEM_REPORTS = 5
# score = reports x distinct cities x 7d growth; over this a problem area is critical
CRITICAL_SCORE = 10.0
RECENT_COMMENTS = 5
RECENT_PROBLEM_REPORTS = 5
STATS_WEEKS = 6


def parse_uuid(value: str) -> uuid.UUID:
    # a malformed id is just an id that doesn't exist, not a server error
    try:
        return uuid.UUID(value)
    except ValueError:
        raise NotFoundError(value) from None


def _area(value: str | None) -> ChallengeArea | None:
    return ChallengeArea(value) if value in {a.value for a in ChallengeArea} else None


def innovation_to_schema(row: InnovationRow) -> Innovation:
    return Innovation(
        id=row.id,
        title=row.title,
        summary=row.summary,
        challenge_areas=areas_from_tags(row.tags),
        city=row.city or "",
        page_url=row.page_url,
        status=PublicationStatus(row.status),
    )


def idea_to_schema(row: IdeaRow) -> Idea:
    canvas = {"problem": "", "solution": "", "beneficiaries": ""} | (row.social_canvas or {})
    return Idea(
        id=str(row.id),
        summary=row.summary,
        essence=row.essence,
        target_group=row.target_group,
        stage=row.stage,
        social_canvas=SocialCanvas.model_validate(canvas),
        status=IdeaStatus(row.status),
        admin_reply=row.admin_reply,
        created_at=row.created_at,
    )


def grant_call_to_schema(row: GrantCallRow) -> GrantCall:
    return GrantCall(
        id=str(row.id), name=row.name, deadline=row.deadline, open=row.open, sections=row.sections
    )


def _get(db: Session, model: type, key: object, raw_id: str):
    row = db.get(model, key)
    if row is None:
        raise NotFoundError(raw_id)
    return row


class DbInnovationAdminService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(
        self, status: PublicationStatus | None, q: str | None, limit: int, offset: int
    ) -> Page[Innovation]:
        query = select(InnovationRow)
        if status is not None:
            query = query.where(InnovationRow.status == status.value)
        if q:
            pattern = f"%{q}%"
            query = query.where(
                or_(InnovationRow.title.ilike(pattern), InnovationRow.summary.ilike(pattern))
            )
        total = self._db.scalar(select(func.count()).select_from(query.subquery())) or 0
        rows = self._db.scalars(
            query.order_by(InnovationRow.created_at.desc()).limit(limit).offset(offset)
        ).all()
        return Page(
            items=[innovation_to_schema(r) for r in rows], total=total, limit=limit, offset=offset
        )

    def get(self, innovation_id: str) -> Innovation:
        return innovation_to_schema(_get(self._db, InnovationRow, innovation_id, innovation_id))

    def update(self, innovation_id: str, data: InnovationUpdate) -> Innovation:
        row = _get(self._db, InnovationRow, innovation_id, innovation_id)
        changes = data.model_dump(exclude_unset=True, mode="json")
        # areas live in rag's tags, not in a column
        if "challenge_areas" in changes:
            row.tags = with_area_tags(row.tags, data.challenge_areas or [])
            del changes["challenge_areas"]
        for field, value in changes.items():
            setattr(row, field, value)
        self._db.commit()
        return innovation_to_schema(row)

    def set_status(self, innovation_id: str, status: PublicationStatus) -> Innovation:
        row = _get(self._db, InnovationRow, innovation_id, innovation_id)
        row.status = status.value
        self._db.commit()
        return innovation_to_schema(row)

    def feedback(self, innovation_id: str) -> InnovationFeedback:
        _get(self._db, InnovationRow, innovation_id, innovation_id)
        avg, count = self._db.execute(
            select(func.avg(Feedback.stars), func.count(Feedback.id)).where(
                Feedback.innovation_id == innovation_id
            )
        ).one()
        signups = self._db.scalar(
            select(func.count(TestSignup.id)).where(TestSignup.innovation_id == innovation_id)
        )
        comments = self._db.scalars(
            select(Feedback)
            .where(Feedback.innovation_id == innovation_id, Feedback.comment.is_not(None))
            .order_by(Feedback.created_at.desc())
            .limit(RECENT_COMMENTS)
        ).all()
        return InnovationFeedback(
            rating_avg=float(avg) if avg is not None else None,
            rating_count=count,
            test_signups=signups or 0,
            recent_comments=[
                FeedbackComment(comment=c.comment, rating=c.stars, created_at=c.created_at)
                for c in comments
            ],
        )


    def stats(self, innovation_id: str) -> InnovationStats:
        _get(self._db, InnovationRow, innovation_id, innovation_id)
        now = datetime.now(UTC)
        matched = (
            ProblemReportRow.hidden.is_(False),
            ProblemReportRow.matched_innovation_ids.any(innovation_id),
        )
        created = ProblemReportRow.created_at
        total, last7, prev7, support, cities, last_at = self._db.execute(
            select(
                func.count(),
                func.count().filter(created >= now - timedelta(days=7)),
                func.count().filter(created >= now - timedelta(days=14), created < now - timedelta(days=7)),
                func.coalesce(func.sum(ProblemReportRow.support_count), 0),
                func.count(ProblemReportRow.city.distinct()),
                func.max(created),
            ).where(*matched)
        ).one()

        week = func.date_trunc(literal_column("'week'"), created)
        weekly = dict(
            (w.date(), n)
            for w, n in self._db.execute(
                select(week, func.count())
                .where(*matched, created >= now - timedelta(weeks=STATS_WEEKS))
                .group_by(week)
            ).all()
        )
        this_week = (now - timedelta(days=now.weekday())).date()
        weeks = [this_week - timedelta(weeks=i) for i in reversed(range(STATS_WEEKS))]

        areas = self._db.execute(
            select(ProblemReportRow.challenge_area, func.count())
            .where(*matched)
            .group_by(ProblemReportRow.challenge_area)
            .order_by(func.count().desc())
        ).all()
        locations = self._db.execute(
            select(ProblemReportRow.city, func.count())
            .where(*matched)
            .group_by(ProblemReportRow.city)
            .order_by(func.count().desc())
        ).all()
        signups = dict(
            self._db.execute(
                select(TestSignup.status, func.count())
                .where(TestSignup.innovation_id == innovation_id)
                .group_by(TestSignup.status)
            ).all()
        )
        stars = dict(
            self._db.execute(
                select(Feedback.stars, func.count())
                .where(Feedback.innovation_id == innovation_id)
                .group_by(Feedback.stars)
            ).all()
        )
        rating_count = sum(stars.values())
        reports = self._db.scalars(
            select(ProblemReportRow).where(*matched).order_by(created.desc()).limit(RECENT_PROBLEM_REPORTS)
        ).all()
        return InnovationStats(
            innovation_id=innovation_id,
            matches_total=total,
            matches_7d=last7,
            matches_prev_7d=prev7,
            people_reached=total + support,
            distinct_locations=cities,
            last_matched_at=last_at,
            matches_by_week=[WeeklyMatches(week_start=w, matches=weekly.get(w, 0)) for w in weeks],
            matches_by_area=[
                AreaMatches(challenge_area=ChallengeArea(a), matches=n) for a, n in areas if _area(a)
            ],
            matches_by_location=[
                LocationMatches(location=city, matches=n)
                if n >= MIN_LOCATION_PROBLEM_REPORTS
                else LocationMatches(location=city, matches=None, note="too few problem reports to display")
                for city, n in locations
            ],
            test_signups=SignupCounts(
                applied=signups.get("applied", 0),
                accepted=signups.get("accepted", 0),
                rejected=signups.get("rejected", 0),
            ),
            rating_avg=sum(k * v for k, v in stars.items()) / rating_count if rating_count else None,
            rating_count=rating_count,
            rating_distribution=[stars.get(k, 0) for k in range(1, 6)],
            recent_comments=self.feedback(innovation_id).recent_comments,
            recent_problem_reports=[
                MatchedProblemReport(
                    id=str(r.id),
                    text=r.text,
                    challenge_area=ChallengeArea(r.challenge_area),
                    location=r.city,
                    support_count=r.support_count,
                    created_at=r.created_at,
                )
                for r in reports
                if _area(r.challenge_area)
            ],
        )

    # quoted: list() above shadows the builtin
    def stats_report(self) -> "list[InnovationStatsRow]":
        now = datetime.now(UTC)
        # one row per (report, matched innovation), so every aggregate below is per innovation
        matches = (
            select(
                func.unnest(ProblemReportRow.matched_innovation_ids).label("innovation_id"),
                ProblemReportRow.created_at,
                ProblemReportRow.support_count,
                ProblemReportRow.city,
            )
            .where(ProblemReportRow.hidden.is_(False))
            .subquery()
        )
        match_stats = {
            row[0]: row[1:]
            for row in self._db.execute(
                select(
                    matches.c.innovation_id,
                    func.count(),
                    func.count().filter(matches.c.created_at >= now - timedelta(days=7)),
                    func.count().filter(
                        matches.c.created_at >= now - timedelta(days=14),
                        matches.c.created_at < now - timedelta(days=7),
                    ),
                    func.coalesce(func.sum(matches.c.support_count), 0),
                    func.count(matches.c.city.distinct()),
                    func.max(matches.c.created_at),
                ).group_by(matches.c.innovation_id)
            ).all()
        }
        signups: dict[str, dict[str, int]] = {}
        for innovation_id, status, n in self._db.execute(
            select(TestSignup.innovation_id, TestSignup.status, func.count()).group_by(
                TestSignup.innovation_id, TestSignup.status
            )
        ).all():
            signups.setdefault(innovation_id, {})[status] = n
        ratings = {
            innovation_id: (float(avg), n)
            for innovation_id, avg, n in self._db.execute(
                select(Feedback.innovation_id, func.avg(Feedback.stars), func.count()).group_by(
                    Feedback.innovation_id
                )
            ).all()
        }

        rows = []
        for innovation in self._db.scalars(select(InnovationRow)).all():
            total, last7, prev7, support, cities, last_at = match_stats.get(
                innovation.id, (0, 0, 0, 0, 0, None)
            )
            counts = signups.get(innovation.id, {})
            avg, rating_count = ratings.get(innovation.id, (None, 0))
            rows.append(
                InnovationStatsRow(
                    innovation_id=innovation.id,
                    title=innovation.title,
                    status=PublicationStatus(innovation.status),
                    matches_total=total,
                    matches_7d=last7,
                    matches_prev_7d=prev7,
                    people_reached=total + support,
                    distinct_locations=cities,
                    test_signups_applied=counts.get("applied", 0),
                    test_signups_accepted=counts.get("accepted", 0),
                    test_signups_rejected=counts.get("rejected", 0),
                    rating_avg=avg,
                    rating_count=rating_count,
                    last_matched_at=last_at,
                )
            )
        return sorted(rows, key=lambda r: r.matches_total, reverse=True)


# InnovationStore for uploads: its own short sessions, so the draft is committed before rag
# embeds it, and publish runs from the background task after the request session is gone
class DbInnovationStore:
    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self._sessions = sessions

    def insert_draft(self, innovation_id: str, data: NewInnovation, tags: list[str]) -> None:
        with self._sessions.begin() as db:
            db.add(
                InnovationRow(
                    id=innovation_id,
                    title=data.title,
                    summary=data.summary,
                    tags=tags,
                    # rag's /query returns city as str, a null breaks it
                    city=data.city or "",
                    page_url=data.page_url,
                    status=PublicationStatus.DRAFT.value,
                )
            )

    def publish(self, innovation_id: str) -> None:
        with self._sessions.begin() as db:
            row = db.get(InnovationRow, innovation_id)
            if row is not None:
                row.status = PublicationStatus.PUBLISHED.value


class DbIdeaAdminService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(self, status: IdeaStatus | None) -> list[Idea]:
        query = select(IdeaRow).order_by(IdeaRow.created_at.desc())
        if status is not None:
            query = query.where(IdeaRow.status == status.value)
        return [idea_to_schema(r) for r in self._db.scalars(query).all()]

    def get(self, idea_id: str) -> Idea:
        return idea_to_schema(_get(self._db, IdeaRow, parse_uuid(idea_id), idea_id))

    def reply(self, idea_id: str, message: str) -> Idea:
        row = _get(self._db, IdeaRow, parse_uuid(idea_id), idea_id)
        row.admin_reply = message
        self._db.commit()
        return idea_to_schema(row)

    def set_status(self, idea_id: str, status: IdeaStatus) -> Idea:
        row = _get(self._db, IdeaRow, parse_uuid(idea_id), idea_id)
        row.status = status.value
        self._db.commit()
        return idea_to_schema(row)


@dataclass(frozen=True)
class _AreaStats:
    reports: int
    cities: int
    growth: float

    @property
    def score(self) -> float:
        return self.reports * self.cities * self.growth


def _area_stats(db: Session) -> dict[str, _AreaStats]:
    now = datetime.now(UTC)
    week_ago, two_weeks_ago = now - timedelta(days=7), now - timedelta(days=14)
    created = ProblemReportRow.created_at
    rows = db.execute(
        select(
            ProblemReportRow.challenge_area,
            func.count(),
            func.count(ProblemReportRow.city.distinct()),
            func.count().filter(created >= week_ago),
            func.count().filter(created >= two_weeks_ago, created < week_ago),
        )
        .where(ProblemReportRow.hidden.is_(False), ProblemReportRow.challenge_area.is_not(None))
        .group_by(ProblemReportRow.challenge_area)
    ).all()
    # a brand-new area (nothing in the previous week) counts as growth = reports this week
    return {
        area: _AreaStats(reports=n, cities=cities, growth=last / max(prev, 1))
        for area, n, cities, last, prev in rows
    }


def _report_to_schema(row: ProblemReportRow, stats: dict[str, _AreaStats]) -> ProblemReport:
    area_stats = stats.get(row.challenge_area or "")
    score = round(area_stats.score, 2) if area_stats else 0.0
    # the admin frontend still reads `location`; renaming it to city is a separate pr
    return ProblemReport(
        id=str(row.id),
        text=row.text,
        challenge_area=_area(row.challenge_area),
        location=row.city,
        support_count=row.support_count,
        is_critical=score >= CRITICAL_SCORE,
        criticality_score=score,
        admin_reply=row.admin_reply,
        created_at=row.created_at,
    )


class DbProblemReportAdminService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(
        self,
        challenge_area: ChallengeArea | None,
        location: str | None,
        is_critical: bool | None,
    ) -> list[ProblemReport]:
        query = select(ProblemReportRow).order_by(ProblemReportRow.created_at.desc())
        if challenge_area is not None:
            query = query.where(ProblemReportRow.challenge_area == challenge_area.value)
        if location:
            query = query.where(func.lower(ProblemReportRow.city) == location.lower())
        stats = _area_stats(self._db)
        reports = [_report_to_schema(r, stats) for r in self._db.scalars(query).all()]
        return [r for r in reports if is_critical is None or r.is_critical == is_critical]

    def get(self, problem_report_id: str) -> ProblemReport:
        row = _get(self._db, ProblemReportRow, parse_uuid(problem_report_id), problem_report_id)
        return _report_to_schema(row, _area_stats(self._db))

    def reply(self, problem_report_id: str, message: str) -> ProblemReport:
        row = _get(self._db, ProblemReportRow, parse_uuid(problem_report_id), problem_report_id)
        row.admin_reply = message
        self._db.commit()
        return _report_to_schema(row, _area_stats(self._db))


class DbInboxAdminService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, since: datetime | None) -> Inbox:
        ideas = select(IdeaRow).where(IdeaRow.status == IdeaStatus.NEW.value)
        reports = select(ProblemReportRow).where(ProblemReportRow.hidden.is_(False))
        if since is not None:
            ideas = ideas.where(IdeaRow.created_at > since)
        stats = _area_stats(self._db)
        all_reports = [
            (row, _report_to_schema(row, stats))
            for row in self._db.scalars(reports.order_by(ProblemReportRow.created_at.desc())).all()
        ]
        return Inbox(
            new_ideas=[idea_to_schema(r) for r in self._db.scalars(ideas).all()],
            new_problem_reports=[
                schema
                for row, schema in all_reports
                if row.admin_reply is None and (since is None or row.created_at > since)
            ],
            critical_problem_reports=[schema for _, schema in all_reports if schema.is_critical],
        )


class DbGrantCallAdminService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(self) -> list[GrantCall]:
        rows = self._db.scalars(select(GrantCallRow).order_by(GrantCallRow.deadline)).all()
        return [grant_call_to_schema(r) for r in rows]

    def create(self, data: GrantCallCreate) -> GrantCall:
        row = GrantCallRow(**data.model_dump(mode="json") | {"deadline": data.deadline})
        self._db.add(row)
        self._db.commit()
        return grant_call_to_schema(row)

    def update(self, call_id: str, data: GrantCallUpdate) -> GrantCall:
        row = _get(self._db, GrantCallRow, parse_uuid(call_id), call_id)
        changes = data.model_dump(exclude_unset=True, mode="json")
        if "deadline" in changes:
            changes["deadline"] = data.deadline
        for field, value in changes.items():
            setattr(row, field, value)
        self._db.commit()
        return grant_call_to_schema(row)


class DbReportAdminService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _visible(self):
        return (
            ProblemReportRow.hidden.is_(False),
            ProblemReportRow.challenge_area.is_not(None),
        )

    def trends(self) -> list[TrendRow]:
        week = func.date_trunc(literal_column("'week'"), ProblemReportRow.created_at)
        rows = self._db.execute(
            select(
                week,
                ProblemReportRow.challenge_area,
                ProblemReportRow.city,
                func.count(),
                func.coalesce(func.sum(ProblemReportRow.support_count), 0),
            )
            .where(*self._visible())
            .group_by(week, ProblemReportRow.challenge_area, ProblemReportRow.city)
            .order_by(week)
        ).all()
        return [
            TrendRow(
                week_start=week_start.date(),
                challenge_area=ChallengeArea(area),
                location=city,
                problem_reports=n,
                support_count=support,
            )
            for week_start, area, city, n, support in rows
            if _area(area)
        ]

    def critical(self) -> list[CriticalRow]:
        stats = _area_stats(self._db)
        result = []
        for area, s in stats.items():
            if s.score < CRITICAL_SCORE or not _area(area):
                continue
            # the most supported report stands for its area
            top = self._db.scalars(
                select(ProblemReportRow)
                .where(ProblemReportRow.challenge_area == area, ProblemReportRow.hidden.is_(False))
                .order_by(ProblemReportRow.support_count.desc(), ProblemReportRow.created_at.desc())
                .limit(1)
            ).first()
            if top is None:
                continue
            result.append(
                CriticalRow(
                    problem_report_id=str(top.id),
                    text=top.text,
                    challenge_area=ChallengeArea(area),
                    distinct_locations=s.cities,
                    growth_ratio_7d=round(s.growth, 2),
                    score=round(s.score, 2),
                )
            )
        return sorted(result, key=lambda r: r.score, reverse=True)

    def locations(self) -> list[LocationRow]:
        rows = self._db.execute(
            select(ProblemReportRow.city, ProblemReportRow.challenge_area, func.count())
            .where(*self._visible())
            .group_by(ProblemReportRow.city, ProblemReportRow.challenge_area)
            .order_by(func.count().desc())
        ).all()
        return [
            LocationRow(location=city, challenge_area=ChallengeArea(area), problem_reports=n)
            if n >= MIN_LOCATION_PROBLEM_REPORTS
            else LocationRow(
                location=city,
                challenge_area=ChallengeArea(area),
                problem_reports=None,
                note="too few problem reports to display",
            )
            for city, area, n in rows
            if _area(area)
        ]

    def gaps(self) -> list[GapRow]:
        # no similarity is stored; a report /match found nothing for is a gap
        rows = self._db.scalars(
            select(ProblemReportRow)
            .where(*self._visible(), func.cardinality(ProblemReportRow.matched_innovation_ids) == 0)
            .order_by(ProblemReportRow.created_at.desc())
        ).all()
        return [
            GapRow(
                problem_report_id=str(r.id),
                text=r.text,
                challenge_area=ChallengeArea(r.challenge_area),
                best_match_similarity=0.0,
            )
            for r in rows
            if _area(r.challenge_area)
        ]


def _reply(row: ThreadReplyRow) -> AdminReply:
    return AdminReply(
        id=str(row.id),
        body=row.body,
        author_label=row.author_label,
        email=row.email,
        kind=ReplyKind(row.kind),
        status=ModerationStatus(row.status),
        created_at=row.created_at,
    )


def _thread(row: ThreadRow) -> AdminThread:
    return AdminThread(
        id=str(row.id),
        innovation_id=row.innovation_id,
        title=row.title,
        body=row.body,
        author_label=row.author_label,
        email=row.email,
        status=ModerationStatus(row.status),
        created_at=row.created_at,
        replies=[_reply(r) for r in sorted(row.replies, key=lambda r: r.created_at)],
    )


class DbThreadAdminService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(self, status: ModerationStatus | None, innovation_id: str | None) -> list[AdminThread]:
        query = select(ThreadRow).options(selectinload(ThreadRow.replies))
        if status is not None:
            query = query.where(
                or_(
                    ThreadRow.status == status.value,
                    ThreadRow.replies.any(ThreadReplyRow.status == status.value),
                )
            )
        if innovation_id is not None:
            query = query.where(ThreadRow.innovation_id == innovation_id)
        rows = self._db.scalars(query.order_by(ThreadRow.created_at.desc())).all()
        return [_thread(r) for r in rows]

    def set_status(self, thread_id: str, status: ModerationStatus) -> AdminThread:
        row = _get(self._db, ThreadRow, parse_uuid(thread_id), thread_id)
        row.status = status.value
        self._db.commit()
        return _thread(row)

    def set_reply_status(self, reply_id: str, status: ModerationStatus) -> AdminReply:
        row = _get(self._db, ThreadReplyRow, parse_uuid(reply_id), reply_id)
        row.status = status.value
        self._db.commit()
        return _reply(row)
