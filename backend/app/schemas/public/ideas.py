from pydantic import BaseModel, Field

from app.schemas.admin.ideas import IdeaStage, IdeaStatus, SocialCanvas
from app.schemas.public.common import OptionalContact


class IdeaCreate(OptionalContact):
    summary: str = Field(min_length=1, max_length=2000)
    essence: str = Field(min_length=1, max_length=2000)
    target_group: str = Field(min_length=1, max_length=500)
    stage: IdeaStage
    social_canvas: SocialCanvas | None = None


class IdeaCreated(BaseModel):
    id: str
    status: IdeaStatus


class GrantApplicationRequest(OptionalContact):
    grant_call_id: str
