from fastapi import APIRouter, Depends

from app.schemas.admin.test_signups import AdminTestSignup, SignupDecision, SignupStatus
from app.services.admin.deps import get_test_signup_service
from app.services.admin.interfaces import TestSignupAdminService

router = APIRouter(prefix="/test-signups", tags=["admin:test-signups"])


@router.get("", response_model=list[AdminTestSignup])
def list_test_signups(
    innovation_id: str | None = None,
    status: SignupStatus | None = None,
    svc: TestSignupAdminService = Depends(get_test_signup_service),
) -> list[AdminTestSignup]:
    return svc.list(innovation_id, status)


# the volunteer is emailed on every change; accepted carries the feedback form link
@router.post("/{signup_id}/status", response_model=AdminTestSignup)
def set_test_signup_status(
    signup_id: str,
    body: SignupDecision,
    svc: TestSignupAdminService = Depends(get_test_signup_service),
) -> AdminTestSignup:
    return svc.set_status(signup_id, body.status)
