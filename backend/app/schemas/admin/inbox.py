from pydantic import BaseModel

from app.schemas.admin.ideas import Idea
from app.schemas.admin.problem_reports import ProblemReport
from app.schemas.admin.test_signups import TestSignup
from app.schemas.admin.threads import AdminThread


class Inbox(BaseModel):
    new_ideas: list[Idea]
    new_problem_reports: list[ProblemReport]
    critical_problem_reports: list[ProblemReport]
    # threads with the thread itself or a reply awaiting moderation
    pending_threads: list[AdminThread]
    new_test_signups: list[TestSignup]
