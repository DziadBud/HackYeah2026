from enum import StrEnum

from pydantic import BaseModel


class RatingState(StrEnum):
    OPEN = "open"
    RATED = "rated"
    # unknown link, or the signup was never accepted
    UNAVAILABLE = "unavailable"


class RatingTarget(BaseModel):
    state: RatingState
    innovation_id: str = ""
    innovation_title: str = ""
