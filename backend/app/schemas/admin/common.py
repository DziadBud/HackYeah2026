from enum import StrEnum
from typing import ClassVar, Generic, Self, TypeVar

from pydantic import BaseModel, Field, model_validator

T = TypeVar("T")


class ChallengeArea(StrEnum):
    FOSTER_CARE = "Rodzina i piecza zastepcza"
    HOMELESSNESS = "Bezdomnosc"
    DISABILITY = "Niepelnosprawnosc"
    POVERTY = "Ubostwo"
    FOREIGNERS = "Integracja cudzoziemcow"
    HEALTH = "Zdrowie"
    MENTAL_HEALTH = "Zdrowie psychiczne"
    SENIORS = "Seniorzy"


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int


class ReplyRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)


class ReportFormat(StrEnum):
    JSON = "json"
    CSV = "csv"


class PatchModel(BaseModel):
    # omitted fields stay unset; explicit null only allowed for fields listed here
    nullable_fields: ClassVar[frozenset[str]] = frozenset()

    @model_validator(mode="after")
    def _reject_nulls(self) -> Self:
        bad = sorted(
            f for f in self.model_fields_set
            if getattr(self, f) is None and f not in self.nullable_fields
        )
        if bad:
            raise ValueError(f"fields cannot be null: {', '.join(bad)}")
        return self
