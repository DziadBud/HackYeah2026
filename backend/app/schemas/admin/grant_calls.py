from datetime import date

from pydantic import BaseModel, Field


class GrantSection(BaseModel):
    title: str
    description: str | None = None
    required: bool = True


class GrantCallCreate(BaseModel):
    name: str = Field(min_length=1)
    deadline: date
    open: bool = False
    sections: list[GrantSection] = []


class GrantCallUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    deadline: date | None = None
    open: bool | None = None
    sections: list[GrantSection] | None = None


class GrantCall(GrantCallCreate):
    id: str
