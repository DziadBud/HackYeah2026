from fastapi import APIRouter, Depends

from app.schemas.admin.common import ChallengeArea, ReplyRequest
from app.schemas.admin.problem_reports import ProblemReport
from app.services.admin.deps import get_problem_report_service
from app.services.admin.interfaces import ProblemReportAdminService

router = APIRouter(prefix="/problem-reports", tags=["admin:problem-reports"])


@router.get("", response_model=list[ProblemReport])
def list_problem_reports(
    challenge_area: ChallengeArea | None = None,
    location: str | None = None,
    is_critical: bool | None = None,
    svc: ProblemReportAdminService = Depends(get_problem_report_service),
) -> list[ProblemReport]:
    return svc.list(challenge_area, location, is_critical)


@router.get("/{problem_report_id}", response_model=ProblemReport)
def get_problem_report(
    problem_report_id: str, svc: ProblemReportAdminService = Depends(get_problem_report_service)
) -> ProblemReport:
    return svc.get(problem_report_id)


@router.post("/{problem_report_id}/reply", response_model=ProblemReport)
def reply_to_problem_report(
    problem_report_id: str,
    body: ReplyRequest,
    svc: ProblemReportAdminService = Depends(get_problem_report_service),
) -> ProblemReport:
    return svc.reply(problem_report_id, body.message)
