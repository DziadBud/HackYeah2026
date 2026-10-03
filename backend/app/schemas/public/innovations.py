from pydantic import BaseModel, Field

from app.schemas.admin.innovations import Innovation


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
