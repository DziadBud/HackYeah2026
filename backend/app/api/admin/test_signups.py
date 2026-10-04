from fastapi import APIRouter, Depends

from app.schemas.admin.test_signups import TestSignup, TestSignupStatus, TestSignupStatusRequest
from app.services.admin.deps import get_test_signup_service
from app.services.admin.interfaces import TestSignupAdminService

router = APIRouter(prefix="/test-signups", tags=["admin:test-signups"])


@router.get("", response_model=list[TestSignup])
def list_test_signups(
    innovation_id: str | None = None,
    status: TestSignupStatus | None = None,
    svc: TestSignupAdminService = Depends(get_test_signup_service),
) -> list[TestSignup]:
    return svc.list(innovation_id, status)


@router.post("/{signup_id}/status", response_model=TestSignup)
def set_test_signup_status(
    signup_id: str,
    body: TestSignupStatusRequest,
    svc: TestSignupAdminService = Depends(get_test_signup_service),
) -> TestSignup:
    return svc.set_status(signup_id, body.status)
