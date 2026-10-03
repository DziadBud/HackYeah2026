from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

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
