from pydantic import BaseModel, Field

from app.schemas.admin.innovations import Innovation
from app.schemas.admin.test_signups import TestSignupStatus
from app.schemas.public.common import EMAIL_PATTERN, OptionalContact


class LibraryInnovation(Innovation):
    rating_avg: float | None = None
    rating_count: int = 0
    # set on the detail endpoint: GET /innovations/{id}/pdf serves the source pdf
    has_pdf: bool = False


class FeedbackCreate(BaseModel):
    stars: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=2000)
    # set when a tester from /match?test_signup=true rates
    test_signup_id: str | None = None


class FeedbackCreated(BaseModel):
    id: str


class TestSignupCreate(OptionalContact):
    # tester mails need an address, so it is required here
    email: str = Field(max_length=254, pattern=EMAIL_PATTERN)


class TestSignupCreated(BaseModel):
    id: str
    status: TestSignupStatus
