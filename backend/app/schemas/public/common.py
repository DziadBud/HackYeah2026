from typing import Self

from pydantic import BaseModel, Field, model_validator

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class OptionalContact(BaseModel):
    # no accounts: an optional email stored on the item, only with consent
    email: str | None = Field(default=None, max_length=254, pattern=EMAIL_PATTERN)
    consent: bool = False

    @model_validator(mode="after")
    def _consent_with_email(self) -> Self:
        if self.email and not self.consent:
            raise ValueError("consent is required when an email is given")
        return self
