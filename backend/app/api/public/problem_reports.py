from fastapi import APIRouter, Depends

from app.schemas.public.problem_reports import PublicProblemReport, SupportResponse
from app.services.public.deps import get_problem_report_service
from app.services.public.interfaces import ProblemReportService

router = APIRouter(prefix="/problem-reports", tags=["problem-reports"])


@router.get("/{problem_report_id}", response_model=PublicProblemReport)
def get_problem_report(
    problem_report_id: str, svc: ProblemReportService = Depends(get_problem_report_service)
) -> PublicProblemReport:
    return svc.get(problem_report_id)


@router.post("/{problem_report_id}/support", response_model=SupportResponse)
def support_problem_report(
    problem_report_id: str, svc: ProblemReportService = Depends(get_problem_report_service)
) -> SupportResponse:
    return svc.support(problem_report_id)
