from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.public.common import OptionalContact


class InstitutionType(StrEnum):
    GMINA = "gmina"
    CUS = "cus"
    NGO = "ngo"
    OTHER = "other"


class DocumentKind(StrEnum):
    MIDDLEMAN = "middleman"
    GRANT_APPLICATION = "grant_application"


class MiddlemanRequest(OptionalContact):
    innovation_id: str
    institution_type: InstitutionType
    needs: str = Field(min_length=3, max_length=3000)


class GeneratedDocument(BaseModel):
    id: str
    kind: DocumentKind
    innovation_id: str | None = None
    idea_id: str | None = None
    grant_call_id: str | None = None
    output: str
    created_at: datetime
