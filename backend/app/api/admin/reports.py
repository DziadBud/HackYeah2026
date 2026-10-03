from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.schemas.admin.common import ReportFormat
from app.schemas.admin.reports import LocationRow, CriticalRow, GapRow, TrendRow
from app.services.admin.csv_export import rows_to_csv
from app.services.admin.deps import get_report_service
from app.services.admin.interfaces import ReportAdminService

router = APIRouter(prefix="/reports", tags=["admin:reports"])


def _csv(name: str, rows: list[BaseModel], model: type[BaseModel]) -> StreamingResponse:
    return StreamingResponse(
        rows_to_csv(rows, list(model.model_fields)),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{name}.csv"'},
    )


@router.get("/trends", response_model=list[TrendRow])
def trends(
    format: ReportFormat = ReportFormat.JSON,
    svc: ReportAdminService = Depends(get_report_service),
) -> list[TrendRow] | StreamingResponse:
    rows = svc.trends()
    return rows if format == ReportFormat.JSON else _csv("trends", rows, TrendRow)


@router.get("/critical", response_model=list[CriticalRow])
def critical(
    format: ReportFormat = ReportFormat.JSON,
    svc: ReportAdminService = Depends(get_report_service),
) -> list[CriticalRow] | StreamingResponse:
    rows = svc.critical()
    return rows if format == ReportFormat.JSON else _csv("critical", rows, CriticalRow)


@router.get("/locations", response_model=list[LocationRow])
def locations(
    format: ReportFormat = ReportFormat.JSON,
    svc: ReportAdminService = Depends(get_report_service),
) -> list[LocationRow] | StreamingResponse:
    rows = svc.locations()
    return rows if format == ReportFormat.JSON else _csv("locations", rows, LocationRow)


@router.get("/gaps", response_model=list[GapRow])
def gaps(
    format: ReportFormat = ReportFormat.JSON,
    svc: ReportAdminService = Depends(get_report_service),
) -> list[GapRow] | StreamingResponse:
    rows = svc.gaps()
    return rows if format == ReportFormat.JSON else _csv("gaps", rows, GapRow)
