from fastapi import APIRouter, Depends

from app.api.admin.errors import map_domain_errors
from app.api.public import (
    documents,
    ideas,
    innovations,
    knowledge,
    match,
    problem_reports,
    ratings,
    threads,
)

# no auth: public writes get the per-ip rate limit once it lands
router = APIRouter(dependencies=[Depends(map_domain_errors)])
for feature in (match, problem_reports, ideas, innovations, threads, documents, knowledge, ratings):
    router.include_router(feature.router)
