from typing import Protocol

from app.clients.rag import RagAnswer

from app.schemas.admin.common import ChallengeArea, Page
from app.schemas.admin.grant_calls import GrantCall
from app.schemas.public.documents import GeneratedDocument, MiddlemanRequest
from app.schemas.public.grant_applications import (
    GrantApplication,
    GrantApplicationCreate,
    GrantApplicationUpdate,
)
from app.schemas.public.ideas import IdeaCreate, IdeaCreated
from app.schemas.public.innovations import FeedbackCreate, FeedbackCreated, LibraryInnovation
from app.schemas.public.match import MatchRequest, MatchResponse
from app.schemas.public.problem_reports import PublicProblemReport, SupportResponse
from app.schemas.public.ratings import RatingTarget
from app.schemas.public.threads import (
    ReplyCreate,
    Submitted,
    Thread,
    ThreadCreate,
)


class Retriever(Protocol):
    def query(self, text: str, top_k: int) -> RagAnswer: ...


# R1: rag retrieval + llm answer; stores a problem report, optional test signups
class MatchService(Protocol):
    def match(self, data: MatchRequest, test_signup: bool) -> MatchResponse: ...


class ProblemReportService(Protocol):
    # the db implementation must treat hidden reports as not found
    def get(self, problem_report_id: str) -> PublicProblemReport: ...
    def support(self, problem_report_id: str) -> SupportResponse: ...


# R3: idea card + grant application (full ROPS form) while a call is open
class IdeaService(Protocol):
    def create(self, data: IdeaCreate) -> IdeaCreated: ...
    def grant_application(self, idea_id: str, data: GrantApplicationCreate) -> GrantApplication: ...
    def get_grant_application(self, application_id: str) -> GrantApplication: ...
    def update_grant_application(
        self, application_id: str, data: GrantApplicationUpdate
    ) -> GrantApplication: ...


# R2 + R4: published innovations only, feedback from anyone
class LibraryService(Protocol):
    def list(
        self, challenge_area: ChallengeArea | None, q: str | None, limit: int, offset: int
    ) -> Page[LibraryInnovation]: ...
    def get(self, innovation_id: str) -> LibraryInnovation: ...
    def add_feedback(self, innovation_id: str, data: FeedbackCreate) -> FeedbackCreated: ...


# R5: community threads, published only; new posts wait for moderation
class ThreadService(Protocol):
    def list(self, innovation_id: str) -> list[Thread]: ...
    def create(self, innovation_id: str, data: ThreadCreate) -> Submitted: ...
    def reply(self, thread_id: str, data: ReplyCreate) -> Submitted: ...


# R7: llm drafts stored as generated_documents
class DocumentService(Protocol):
    def middleman(self, data: MiddlemanRequest) -> GeneratedDocument: ...


class KnowledgeService(Protocol):
    def open_grant_calls(self) -> list[GrantCall]: ...


# R4: a tester rates from the mail; the signup id in the link is the token.
# one rating per signup: rate() moves the signup to rated
class RatingService(Protocol):
    def target(self, signup_id: str) -> RatingTarget: ...
    def rate(self, signup_id: str, stars: int, comment: str) -> RatingTarget: ...
