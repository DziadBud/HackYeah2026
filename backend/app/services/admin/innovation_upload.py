import re
import unicodedata
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from app.services.admin.errors import (
    EmbedPublishError,
    InvalidUploadError,
    UploadTooLargeError,
)

PDF_MAGIC = b"%PDF-"


@dataclass(frozen=True)
class NewInnovation:
    title: str
    summary: str
    author: str
    tags: list[str] = field(default_factory=list)
    city: str = ""
    page_url: str | None = None
    image_url: str | None = None


@dataclass(frozen=True)
class CreatedInnovation:
    id: str
    title: str
    status: str
    file_path: str


class InnovationStore(Protocol):
    def insert_draft(self, innovation_id: str, data: NewInnovation, tags: list[str]) -> None: ...
    def delete(self, innovation_id: str) -> None: ...


class FileStorage(Protocol):
    def save(self, name: str, content: bytes) -> Path: ...
    def delete(self, path: Path) -> None: ...


class EmbedPublisher(Protocol):
    def publish_embed_requested(self, innovation_id: str, file_path: str) -> None: ...


class InnovationUploadService:
    def __init__(
        self,
        store: InnovationStore,
        files: FileStorage,
        publisher: EmbedPublisher,
        max_bytes: int,
    ) -> None:
        self._store = store
        self._files = files
        self._publisher = publisher
        self._max_bytes = max_bytes

    def create(self, data: NewInnovation, pdf: bytes) -> CreatedInnovation:
        if len(pdf) > self._max_bytes:
            raise UploadTooLargeError(f"pdf larger than {self._max_bytes} bytes")
        if not pdf.startswith(PDF_MAGIC):
            raise InvalidUploadError("file is not a pdf")

        innovation_id = _new_id(data.title)
        path = self._files.save(f"{innovation_id}.pdf", pdf)
        try:
            # committed before publishing: rag looks the row up as soon as it gets the message
            self._store.insert_draft(innovation_id, data, _tags(data))
        except Exception:
            self._files.delete(path)
            raise

        try:
            self._publisher.publish_embed_requested(innovation_id, str(path))
        except Exception as exc:
            # no outbox: undo instead, so there is never a draft that nobody will embed
            self._store.delete(innovation_id)
            self._files.delete(path)
            raise EmbedPublishError("could not queue the embedding, try again") from exc

        return CreatedInnovation(
            id=innovation_id, title=data.title, status="draft", file_path=str(path)
        )


def _tags(data: NewInnovation) -> list[str]:
    # rag's innovations table has no author column; tags are the only free-form field
    extra = ["type:innovation", f"author:{data.author}"]
    return list(dict.fromkeys([*data.tags, *extra]))


def _new_id(title: str) -> str:
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")[:40] or "innovation"
    return f"{slug}-{uuid.uuid4().hex[:6]}"
