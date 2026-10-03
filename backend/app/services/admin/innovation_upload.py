import logging
import re
import unicodedata
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from app.schemas.admin.common import ChallengeArea
from app.services.admin.errors import InvalidUploadError, UploadTooLargeError

logger = logging.getLogger(__name__)

PDF_MAGIC = b"%PDF-"


@dataclass(frozen=True)
class NewInnovation:
    title: str
    summary: str
    challenge_areas: list[ChallengeArea]
    tags: list[str] = field(default_factory=list)
    city: str = ""
    page_url: str | None = None


@dataclass(frozen=True)
class CreatedInnovation:
    id: str
    title: str
    status: str
    file_path: str


class InnovationStore(Protocol):
    def insert_draft(self, innovation_id: str, data: NewInnovation, tags: list[str]) -> None: ...
    def publish(self, innovation_id: str) -> None: ...


class FileStorage(Protocol):
    def save(self, name: str, content: bytes) -> Path: ...
    def delete(self, path: Path) -> None: ...


class EmbeddingClient(Protocol):
    def embed_pdf(self, innovation_id: str, filename: str, pdf: bytes) -> None: ...


class InnovationUploadService:
    def __init__(
        self,
        store: InnovationStore,
        files: FileStorage,
        rag: EmbeddingClient,
        max_bytes: int,
    ) -> None:
        self._store = store
        self._files = files
        self._rag = rag
        self._max_bytes = max_bytes

    def create(self, data: NewInnovation, pdf: bytes) -> CreatedInnovation:
        if len(pdf) > self._max_bytes:
            raise UploadTooLargeError(f"pdf larger than {self._max_bytes} bytes")
        if not pdf.startswith(PDF_MAGIC):
            raise InvalidUploadError("file is not a pdf")

        innovation_id = _new_id(data.title)
        path = self._files.save(f"{innovation_id}.pdf", pdf)
        try:
            # committed before embedding: rag looks the row up and replaces its chunks
            self._store.insert_draft(innovation_id, data, _tags(data))
        except Exception:
            self._files.delete(path)
            raise

        return CreatedInnovation(
            id=innovation_id, title=data.title, status="draft", file_path=str(path)
        )

    def embed(self, innovation_id: str, file_path: str) -> None:
        # runs as a background task after the 202; a failure leaves the draft unpublished
        path = Path(file_path)
        try:
            self._rag.embed_pdf(innovation_id, path.name, path.read_bytes())
            self._store.publish(innovation_id)
        except Exception:
            logger.exception("embedding failed, innovation %s stays draft", innovation_id)


def _tags(data: NewInnovation) -> list[str]:
    return with_area_tags([*data.tags, "type:innovation"], data.challenge_areas)


def with_area_tags(tags: list[str], areas: list[ChallengeArea]) -> list[str]:
    # rag only filters on tags, so the challenge areas are mirrored there as area:<slug>
    kept = [t for t in tags if not t.startswith("area:")]
    return list(dict.fromkeys([*kept, *(f"area:{_slug(a.value)}" for a in areas)]))


def area_tag(area: ChallengeArea) -> str:
    return f"area:{_slug(area.value)}"


def areas_from_tags(tags: list[str] | None) -> list[ChallengeArea]:
    by_tag = {area_tag(a): a for a in ChallengeArea}
    return [by_tag[t] for t in tags or [] if t in by_tag]


def _new_id(title: str) -> str:
    return f"{_slug(title)[:40].strip('-') or 'innovation'}-{uuid.uuid4().hex[:6]}"


def _slug(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
