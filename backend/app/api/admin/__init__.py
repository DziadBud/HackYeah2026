from fastapi import APIRouter, Depends

from app.api.admin import (
    auth,
    grant_calls,
    ideas,
    inbox,
    innovations,
    problem_reports,
    reports,
)
from app.api.admin.errors import map_domain_errors
from app.auth import require_admin, require_same_origin

# login must stay public, so it sits outside the protected sub-router
protected = APIRouter(dependencies=[Depends(require_admin), Depends(map_domain_errors)])
for feature in (innovations, inbox, ideas, problem_reports, grant_calls, reports):
    protected.include_router(feature.router)

router = APIRouter(prefix="/admin", dependencies=[Depends(require_same_origin)])
router.include_router(auth.router)
router.include_router(protected)
