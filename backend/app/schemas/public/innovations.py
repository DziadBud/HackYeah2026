from pydantic import BaseModel, Field

from app.schemas.admin.innovations import Innovation
from app.schemas.admin.test_signups import TestSignupStatus
from app.schemas.public.common import EMAIL_PATTERN, OptionalContact


class LibraryInnovation(Innovation):
    rating_avg: float | None = None
    rating_count: int = 0
    # set on the detail endpoint: GET /innovations/{id}/pdf serves the source pdf
    has_pdf: bool = False
    # description sections from innovation_profiles; empty for innovations without one
    tagline: str | None = None
    program: str | None = None
    problem: str | None = None
    target_group: str | None = None
    who_can_use: str | None = None
    effectiveness: str | None = None
    authors: list[str] = []
    # file names for GET /innovations/{id}/photos/{name}, first one is the cover
    photos: list[str] = []
    license_name: str | None = None
    license_url: str | None = None
    # the innovation's page in the ROPS library
    source_url: str | None = None


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


class LikeState(BaseModel):
    like_count: int
    # whether the asking browser (client_id) has liked it
    liked: bool
