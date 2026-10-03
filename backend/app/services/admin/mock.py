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
    FeedbackComment,
    Innovation,
    InnovationCreate,
    InnovationFeedback,
    PublicationStatus,
    InnovationUpdate,
)
from app.schemas.admin.problem_reports import ProblemReport
from app.schemas.admin.reports import LocationRow, CriticalRow, GapRow, TrendRow
from app.services.admin.errors import NotFoundError

NOW = datetime(2026, 10, 3, 9, 0, tzinfo=timezone.utc)
MIN_LOCATION_PROBLEM_REPORTS = 5


class MockAuthAdminService:
    def login(self, username: str, password: str) -> str:
        return "mock-admin-token"


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
                    target_group=["osoby niesluchace", "osoby niedoslyszace"],
                    readiness="prototype",
                    cost_level="medium",
                    video_url="https://example.com/wibraap.mp4",
                    status=PublicationStatus.PUBLISHED,
                ),
                Innovation(
                    id="straznik",
                    title="Straznik",
                    summary="Aplikacja wykrywajaca alarmy dzwiekowe i ostrzegajaca wibracjami.",
                    challenge_areas=[ChallengeArea.DISABILITY, ChallengeArea.SENIORS],
                    target_group=["osoby niesluchace", "seniorzy"],
                    readiness="pilot",
                    cost_level="low",
                    status=PublicationStatus.PUBLISHED,
                ),
                Innovation(
                    id="paszport-choroby-rzadkiej",
                    title="Paszport pacjenta z choroba rzadka",
                    summary="System IT z danymi pacjenta dostepnymi dla personelu medycznego.",
                    challenge_areas=[ChallengeArea.HEALTH],
                    target_group=["pacjenci z chorobami rzadkimi"],
                    readiness="concept",
                    cost_level="high",
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

    def create(self, data: InnovationCreate) -> Innovation:
        item = Innovation(
            id=f"innovation-{len(self._items) + 1}",
            status=PublicationStatus.DRAFT,
            **data.model_dump(),
        )
        self._items[item.id] = item
        return item

    def get(self, innovation_id: str) -> Innovation:
        try:
            return self._items[innovation_id]
        except KeyError:
            raise NotFoundError(innovation_id) from None

    def update(self, innovation_id: str, data: InnovationUpdate) -> Innovation:
        item = self.get(innovation_id)
        updated = item.model_copy(update=data.model_dump(exclude_unset=True))
        self._items[innovation_id] = updated
        return updated

    def set_status(self, innovation_id: str, status: PublicationStatus) -> Innovation:
        item = self.get(innovation_id)
        updated = item.model_copy(update={"status": status})
        self._items[innovation_id] = updated
        return updated

    def feedback(self, innovation_id: str) -> InnovationFeedback:
        self.get(innovation_id)
        return InnovationFeedback(
            rating_avg=4.5,
            rating_count=12,
            test_signups=3,
            recent_comments=[
                FeedbackComment(
                    comment="Swietny pomysl, chcemy przetestowac w naszym DPS.",
                    rating=5,
                    created_at=NOW - timedelta(days=1),
                ),
                FeedbackComment(
                    comment="Potrzeba tanszej wersji dla gmin.",
                    rating=4,
                    created_at=NOW - timedelta(days=3),
                ),
            ],
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

    def reply(self, problem_report_id: str, message: str) -> ProblemReport:
        updated = self.get(problem_report_id).model_copy(update={"admin_reply": message})
        self._items[problem_report_id] = updated
        return updated


class MockInboxAdminService:
    def get(self, since: datetime | None) -> Inbox:
        def fresh(created_at: datetime) -> bool:
            return since is None or created_at > since

        return Inbox(
            new_ideas=[i for i in _IDEAS if fresh(i.created_at)],
            new_problem_reports=[i for i in _PROBLEM_REPORTS if fresh(i.created_at)],
            critical_problem_reports=[i for i in _PROBLEM_REPORTS if i.is_critical],
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
        updated = call.model_copy(update=data.model_dump(exclude_unset=True))
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
