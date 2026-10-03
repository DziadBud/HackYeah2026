from pydantic import BaseModel

from app.schemas.admin.ideas import Idea
from app.schemas.admin.problem_reports import ProblemReport


class Inbox(BaseModel):
    new_ideas: list[Idea]
    new_problem_reports: list[ProblemReport]
    critical_problem_reports: list[ProblemReport]
