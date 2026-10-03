from collections.abc import Sequence
from datetime import date, datetime, timedelta, timezone

from app.schemas.admin.common import ChallengeArea, Page
from app.schemas.admin.grant_calls import (
    GrantCall,
    GrantCallCreate,
    GrantCallUpdate,
    GrantSection,
)
from app.schemas.admin.ideas import Idea, IdeaStage, IdeaStatus, SocialCanvas
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
from app.schemas.admin.reports import LocationRow, CriticalRow, GapRow, TrendRow
from app.services.admin.errors import NotFoundError
from app.services.admin.innovation_upload import NewInnovation
from app.services.admin.interfaces import IdeaAdminService, ProblemReportAdminService

NOW = datetime(2026, 10, 3, 9, 0, tzinfo=timezone.utc)
MIN_LOCATION_PROBLEM_REPORTS = 5


class MockInnovationAdminService:
    def __init__(self) -> None:
        self._items: dict[str, Innovation] = {
            i.id: i
            for i in [
                Innovation(
                    id="wibraap",
                    title="Wibraap",
                    summary="Kamizelka wibracyjna i aplikacja zamieniajaca dzwiek na wibracje.",
                    challenge_areas=[ChallengeArea.DISABILITY],
                    status=PublicationStatus.PUBLISHED,
                ),
                Innovation(
                    id="straznik",
                    title="Straznik",
                    summary="Aplikacja wykrywajaca alarmy dzwiekowe i ostrzegajaca wibracjami.",
                    challenge_areas=[ChallengeArea.DISABILITY, ChallengeArea.SENIORS],
                    status=PublicationStatus.PUBLISHED,
                ),
                Innovation(
                    id="paszport-choroby-rzadkiej",
                    title="Paszport pacjenta z choroba rzadka",
                    summary="System IT z danymi pacjenta dostepnymi dla personelu medycznego.",
                    challenge_areas=[ChallengeArea.HEALTH],
                    status=PublicationStatus.DRAFT,
                ),
            ]
        }

    def list(
        self, status: PublicationStatus | None, q: str | None, limit: int, offset: int
    ) -> Page[Innovation]:
        items = [
            i
            for i in self._items.values()
            if (status is None or i.status == status)
            and (q is None or q.lower() in f"{i.title} {i.summary}".lower())
        ]
        return Page(
            items=items[offset : offset + limit],
            total=len(items),
            limit=limit,
            offset=offset,
        )

    # InnovationStore for uploads; the real table lands once the data model is settled
    # Sequence, not list: the class's own list() method shadows the builtin here
    def insert_draft(self, innovation_id: str, data: NewInnovation, tags: Sequence[str]) -> None:
        self._items[innovation_id] = Innovation(
            id=innovation_id,
            title=data.title,
            summary=data.summary,
            challenge_areas=data.challenge_areas,
            city=data.city,
            page_url=data.page_url,
            status=PublicationStatus.DRAFT,
        )

    def publish(self, innovation_id: str) -> None:
        self.set_status(innovation_id, PublicationStatus.PUBLISHED)

    def get(self, innovation_id: str) -> Innovation:
        try:
            return self._items[innovation_id]
        except KeyError:
            raise NotFoundError(innovation_id) from None

    def update(self, innovation_id: str, data: InnovationUpdate) -> Innovation:
        item = self.get(innovation_id)
        # model_validate, not model_copy: copy skips validation and nested defaults
        updated = Innovation.model_validate(
            item.model_dump() | data.model_dump(exclude_unset=True)
        )
        self._items[innovation_id] = updated
        return updated

    def set_status(self, innovation_id: str, status: PublicationStatus) -> Innovation:
        item = self.get(innovation_id)
        updated = item.model_copy(update={"status": status})
        self._items[innovation_id] = updated
        return updated

    def feedback(self, innovation_id: str) -> InnovationFeedback:
        stats = self.stats(innovation_id)
        signups = stats.test_signups
        return InnovationFeedback(
            rating_avg=stats.rating_avg,
            rating_count=stats.rating_count,
            test_signups=signups.applied + signups.accepted + signups.rejected,
            recent_comments=stats.recent_comments,
        )

    def stats(self, innovation_id: str) -> InnovationStats:
        self.get(innovation_id)
        return _stats(innovation_id)

    # quoted: list() above shadows the builtin
    def stats_report(self) -> "list[InnovationStatsRow]":
        rows = []
        for item in self._items.values():
            s = _stats(item.id)
            rows.append(
                InnovationStatsRow(
                    innovation_id=item.id,
                    title=item.title,
                    status=item.status,
                    matches_total=s.matches_total,
                    matches_7d=s.matches_7d,
                    matches_prev_7d=s.matches_prev_7d,
                    people_reached=s.people_reached,
                    distinct_locations=s.distinct_locations,
                    test_signups_applied=s.test_signups.applied,
                    test_signups_accepted=s.test_signups.accepted,
                    test_signups_rejected=s.test_signups.rejected,
                    rating_avg=s.rating_avg,
                    rating_count=s.rating_count,
                    last_matched_at=s.last_matched_at,
                )
            )
        return sorted(rows, key=lambda r: r.matches_total, reverse=True)


# per-innovation activity behind the stats; weekly, location and area counts add up to the same total.
# real impl: aggregates over problem_reports.matched_innovation_ids, test_signups and feedback
_ACTIVITY: dict[str, dict] = {
    "wibraap": {
        "weekly": [2, 3, 5, 4, 6, 9],
        "locations": {"Krakow": 15, "Tarnow": 8, "Nowy Sacz": 4, "Wieliczka": 2},
        "areas": {ChallengeArea.DISABILITY: 26, ChallengeArea.SENIORS: 3},
        "people_reached": 61,
        "signups": (5, 2, 1),
        "ratings": [1, 0, 2, 4, 5],
        "comments": [
            ("Dzieci w naszym osrodku po raz pierwszy poczuly koncert. Prosimy o wersje dziecieca kamizelki.", 5, 1),
            ("Aplikacja na telefon czasem gubi polaczenie z kamizelka.", 3, 4),
        ],
        "reports": [
            ("Glusi uczniowie nie moga uczestniczyc w szkolnych koncertach i apelach.", ChallengeArea.DISABILITY, "Tarnow", 6, 2),
            ("Brak oferty kulturalnej dla osob niedoslyszacych w domu kultury.", ChallengeArea.DISABILITY, "Krakow", 3, 5),
        ],
    },
    "straznik": {
        "weekly": [1, 2, 2, 4, 5, 7],
        "locations": {"Krakow": 9, "Skawina": 6, "Myslenice": 4, "Bochnia": 2},
        "areas": {ChallengeArea.DISABILITY: 13, ChallengeArea.SENIORS: 8},
        "people_reached": 38,
        "signups": (4, 3, 1),
        "ratings": [0, 1, 2, 8, 13],
        "comments": [
            ("Swietny pomysl, chcemy przetestowac w naszym DPS.", 5, 1),
            ("Potrzeba tanszej wersji dla gmin.", 4, 3),
            ("Opaska powinna dzialac tez bez smartfona.", 4, 6),
        ],
        "reports": [
            ("Mama jest niedoslyszaca i nie slyszy czujnika dymu w nocy.", ChallengeArea.SENIORS, "Skawina", 9, 1),
            ("Mieszkancy DPS z aparatami sluchowymi nie reaguja na alarm pozarowy.", ChallengeArea.DISABILITY, "Krakow", 4, 3),
        ],
    },
}


def _week_start(days_ago: int) -> date:
    day = (NOW - timedelta(days=days_ago)).date()
    return day - timedelta(days=day.weekday())


def _stats(innovation_id: str) -> InnovationStats:
    a = _ACTIVITY.get(innovation_id)
    if a is None:
        # new or never matched (drafts are never returned by /match)
        a = {"weekly": [0] * 6, "locations": {}, "areas": {}, "people_reached": 0,
             "signups": (0, 0, 0), "ratings": [0] * 5, "comments": [], "reports": []}
    weekly: list[int] = a["weekly"]
    ratings: list[int] = a["ratings"]
    rating_count = sum(ratings)
    reports = [
        MatchedProblemReport(
            id=f"problem-report-{innovation_id}-{n}",
            text=text,
            challenge_area=area,
            location=location,
            support_count=support,
            created_at=NOW - timedelta(days=days),
        )
        for n, (text, area, location, support, days) in enumerate(a["reports"], 1)
    ]
    return InnovationStats(
        innovation_id=innovation_id,
        matches_total=sum(weekly),
        matches_7d=weekly[-1],
        matches_prev_7d=weekly[-2],
        people_reached=a["people_reached"],
        distinct_locations=len(a["locations"]),
        last_matched_at=max((r.created_at for r in reports), default=None),
        matches_by_week=[
            WeeklyMatches(week_start=_week_start(7 * (len(weekly) - 1 - n)), matches=m)
            for n, m in enumerate(weekly)
        ],
        matches_by_area=[AreaMatches(challenge_area=k, matches=v) for k, v in a["areas"].items()],
        matches_by_location=[
            LocationMatches(location=loc, matches=n)
            if n >= MIN_LOCATION_PROBLEM_REPORTS
            else LocationMatches(location=loc, matches=None, note="too few problem reports to display")
            for loc, n in a["locations"].items()
        ],
        test_signups=SignupCounts(
            applied=a["signups"][0], accepted=a["signups"][1], rejected=a["signups"][2]
        ),
        rating_avg=(
            round(sum((i + 1) * n for i, n in enumerate(ratings)) / rating_count, 2)
            if rating_count
            else None
        ),
        rating_count=rating_count,
        rating_distribution=ratings,
        recent_comments=[
            FeedbackComment(comment=c, rating=r, created_at=NOW - timedelta(days=d))
            for c, r, d in a["comments"]
        ],
        recent_problem_reports=reports,
    )


_IDEAS = [
    Idea(
        id="idea-1",
        summary="Mobilny punkt porad dla seniorow na wsiach",
        target_group="seniorzy",
        stage=IdeaStage.CONCEPT,
        social_canvas=SocialCanvas(
            problem="Brak dostepu do porad prawnych i zdrowotnych poza miastem",
            solution="Bus z doradcami odwiedzajacy solectwa raz w tygodniu",
            beneficiaries="seniorzy z malych miejscowosci",
        ),
        status=IdeaStatus.NEW,
        created_at=NOW - timedelta(hours=5),
    ),
    Idea(
        id="idea-2",
        summary="Mieszkania treningowe dla osob wychodzacych z bezdomnosci",
        target_group="osoby w kryzysie bezdomnosci",
        stage=IdeaStage.PROTOTYPE,
        social_canvas=SocialCanvas(
            problem="Powroty na ulice po opuszczeniu schroniska",
            solution="Roczny program mieszkan z asystentem",
            beneficiaries="osoby bezdomne",
            resources="2 mieszkania, asystent",
        ),
        status=IdeaStatus.IN_REVIEW,
        admin_reply="Dziekujemy, analizujemy zgloszenie.",
        created_at=NOW - timedelta(days=4),
    ),
]

_PROBLEM_REPORTS = [
    ProblemReport(
        id="problem-report-1",
        text="W naszej gminie nie ma zadnego wsparcia dla rodzin zastepczych po 18. roku zycia dziecka.",
        challenge_area=ChallengeArea.FOSTER_CARE,
        location="Wieliczka",
        support_count=14,
        is_critical=True,
        criticality_score=3.4,
        created_at=NOW - timedelta(days=6),
    ),
    ProblemReport(
        id="problem-report-2",
        text="Brak psychologa dzieciecego, kolejka ponad pol roku.",
        challenge_area=ChallengeArea.MENTAL_HEALTH,
        location="Krakow",
        support_count=7,
        is_critical=True,
        criticality_score=2.1,
        admin_reply="Zgloszenie przekazane do ROPS.",
        created_at=NOW - timedelta(days=2),
    ),
    ProblemReport(
        id="problem-report-3",
        text="Autobus do osrodka zdrowia kursuje tylko dwa razy dziennie.",
        challenge_area=ChallengeArea.SENIORS,
        location="Skawina",
        support_count=2,
        is_critical=False,
        criticality_score=0.4,
        created_at=NOW - timedelta(hours=3),
    ),
]


class MockIdeaAdminService:
    def __init__(self) -> None:
        self._items = {i.id: i for i in _IDEAS}

    def list(self, status: IdeaStatus | None) -> list[Idea]:
        return [i for i in self._items.values() if status is None or i.status == status]

    def get(self, idea_id: str) -> Idea:
        try:
            return self._items[idea_id]
        except KeyError:
            raise NotFoundError(idea_id) from None

    # public writes land here so they show up in the admin inbox
    def add(self, idea: Idea) -> None:
        self._items[idea.id] = idea

    def reply(self, idea_id: str, message: str) -> Idea:
        updated = self.get(idea_id).model_copy(update={"admin_reply": message})
        self._items[idea_id] = updated
        return updated

    def set_status(self, idea_id: str, status: IdeaStatus) -> Idea:
        updated = self.get(idea_id).model_copy(update={"status": status})
        self._items[idea_id] = updated
        return updated


class MockProblemReportAdminService:
    def __init__(self) -> None:
        self._items = {i.id: i for i in _PROBLEM_REPORTS}

    def list(
        self,
        challenge_area: ChallengeArea | None,
        location: str | None,
        is_critical: bool | None,
    ) -> list[ProblemReport]:
        return [
            i
            for i in self._items.values()
            if (challenge_area is None or i.challenge_area == challenge_area)
            and (location is None or i.location.lower() == location.lower())
            and (is_critical is None or i.is_critical == is_critical)
        ]

    def get(self, problem_report_id: str) -> ProblemReport:
        try:
            return self._items[problem_report_id]
        except KeyError:
            raise NotFoundError(problem_report_id) from None

    def add(self, report: ProblemReport) -> None:
        self._items[report.id] = report

    def support(self, problem_report_id: str) -> ProblemReport:
        report = self.get(problem_report_id)
        updated = report.model_copy(update={"support_count": report.support_count + 1})
        self._items[problem_report_id] = updated
        return updated

    def reply(self, problem_report_id: str, message: str) -> ProblemReport:
        updated = self.get(problem_report_id).model_copy(update={"admin_reply": message})
        self._items[problem_report_id] = updated
        return updated


class MockInboxAdminService:
    # reads through the other services so status changes and replies show up here
    def __init__(
        self, ideas: IdeaAdminService, problem_reports: ProblemReportAdminService
    ) -> None:
        self._ideas = ideas
        self._problem_reports = problem_reports

    def get(self, since: datetime | None) -> Inbox:
        def fresh(created_at: datetime) -> bool:
            return since is None or created_at > since

        reports = self._problem_reports.list(None, None, None)
        return Inbox(
            new_ideas=[i for i in self._ideas.list(IdeaStatus.NEW) if fresh(i.created_at)],
            new_problem_reports=[
                r for r in reports if r.admin_reply is None and fresh(r.created_at)
            ],
            critical_problem_reports=[r for r in reports if r.is_critical],
        )


class MockGrantCallAdminService:
    def __init__(self) -> None:
        self._items: dict[str, GrantCall] = {
            "call-1": GrantCall(
                id="call-1",
                name="Nabor ROPS 2026: innowacje spoleczne",
                deadline=date(2026, 12, 15),
                open=True,
                sections=[
                    GrantSection(title="Opis problemu"),
                    GrantSection(title="Plan wdrozenia"),
                    GrantSection(title="Budzet", required=False),
                ],
            )
        }

    def list(self) -> list[GrantCall]:
        return list(self._items.values())

    def create(self, data: GrantCallCreate) -> GrantCall:
        call = GrantCall(id=f"call-{len(self._items) + 1}", **data.model_dump())
        self._items[call.id] = call
        return call

    def update(self, call_id: str, data: GrantCallUpdate) -> GrantCall:
        try:
            call = self._items[call_id]
        except KeyError:
            raise NotFoundError(call_id) from None
        updated = GrantCall.model_validate(
            call.model_dump() | data.model_dump(exclude_unset=True)
        )
        self._items[call_id] = updated
        return updated


class MockReportAdminService:
    def trends(self) -> list[TrendRow]:
        return [
            TrendRow(week_start=date(2026, 9, 14), challenge_area=ChallengeArea.FOSTER_CARE, location="Wieliczka", problem_reports=3, support_count=9),
            TrendRow(week_start=date(2026, 9, 21), challenge_area=ChallengeArea.FOSTER_CARE, location="Wieliczka", problem_reports=5, support_count=21),
            TrendRow(week_start=date(2026, 9, 21), challenge_area=ChallengeArea.MENTAL_HEALTH, location="Krakow", problem_reports=8, support_count=17),
        ]

    def critical(self) -> list[CriticalRow]:
        return [
            CriticalRow(
                problem_report_id="problem-report-1",
                text="Brak wsparcia dla rodzin zastepczych po 18. roku zycia dziecka.",
                challenge_area=ChallengeArea.FOSTER_CARE,
                distinct_locations=4,
                growth_ratio_7d=2.3,
                score=36.8,
            )
        ]

    def locations(self) -> list[LocationRow]:
        counts = [
            ("Krakow", ChallengeArea.MENTAL_HEALTH, 12),
            ("Wieliczka", ChallengeArea.FOSTER_CARE, 8),
            ("Skawina", ChallengeArea.SENIORS, 2),
        ]
        return [
            LocationRow(location=c, challenge_area=a, problem_reports=n)
            if n >= MIN_LOCATION_PROBLEM_REPORTS
            else LocationRow(
                location=c, challenge_area=a, problem_reports=None, note="too few problem reports to display"
            )
            for c, a, n in counts
        ]

    def gaps(self) -> list[GapRow]:
        return [
            GapRow(
                problem_report_id="problem-report-2",
                text="Brak psychologa dzieciecego, kolejka ponad pol roku.",
                challenge_area=ChallengeArea.MENTAL_HEALTH,
                best_match_similarity=0.31,
            )
        ]
