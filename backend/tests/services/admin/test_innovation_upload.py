from pathlib import Path

import pytest

from app.schemas.admin.common import ChallengeArea
from app.schemas.admin.innovations import CostLevel, Readiness
from app.services.admin.errors import InvalidUploadError, UploadTooLargeError
from app.services.admin.innovation_upload import InnovationUploadService, NewInnovation

PDF = b"%PDF-1.7 fake body"
DATA = NewInnovation(
    title="Wibraap: opaska dla seniorów",
    summary="Opis",
    problem="Seniorzy nie slysza alarmow",
    innovator="Fundacja Testowa",
    challenge_areas=[ChallengeArea.SENIORS, ChallengeArea.MENTAL_HEALTH],
    readiness=Readiness.PILOT,
    cost_level=CostLevel.LOW,
    tags=["opaska"],
)


class FakeStore:
    def __init__(self, fail: bool = False) -> None:
        self.rows: dict[str, list[str]] = {}
        self.published: list[str] = []
        self.fail = fail

    def insert_draft(self, innovation_id: str, data: NewInnovation, tags: list[str]) -> None:
        if self.fail:
            raise RuntimeError("db down")
        self.rows[innovation_id] = tags

    def publish(self, innovation_id: str) -> None:
        self.published.append(innovation_id)


class FakeFiles:
    def __init__(self, root: Path) -> None:
        self.root = root

    def save(self, name: str, content: bytes) -> Path:
        path = self.root / name
        path.write_bytes(content)
        return path

    def delete(self, path: Path) -> None:
        path.unlink(missing_ok=True)


class FakeRag:
    def __init__(self, fail: bool = False) -> None:
        self.embedded: list[tuple[str, str, bytes]] = []
        self.fail = fail

    def embed_pdf(self, innovation_id: str, filename: str, pdf: bytes) -> None:
        if self.fail:
            raise ConnectionError("rag down")
        self.embedded.append((innovation_id, filename, pdf))


def make(tmp_path: Path, store=None, rag=None, max_bytes: int = 1024):
    store = store or FakeStore()
    rag = rag or FakeRag()
    svc = InnovationUploadService(store, FakeFiles(tmp_path), rag, max_bytes)
    return svc, store, rag


@pytest.mark.parametrize(
    "content, err",
    [
        pytest.param(PDF, None, id="#1 - OK"),
        pytest.param(b"hello", InvalidUploadError, id="#2 - FAIL - not a pdf"),
        pytest.param(PDF + b"x" * 2000, UploadTooLargeError, id="#3 - FAIL - too large"),
    ],
)
def test_create(tmp_path, content, err) -> None:
    svc, store, rag = make(tmp_path)

    if err:
        with pytest.raises(err):
            svc.create(DATA, content)
        assert store.rows == {} and list(tmp_path.iterdir()) == []
        return

    created = svc.create(DATA, content)

    assert created.status == "draft"
    assert created.id.startswith("wibraap-opaska-dla-seniorow-")
    assert store.rows[created.id] == ["opaska", "type:innovation", "area:seniorzy", "area:zdrowie-psychiczne"]
    assert Path(created.file_path).read_bytes() == PDF
    # embedding is a separate background step
    assert rag.embedded == [] and store.published == []


@pytest.mark.parametrize(
    "rag_fails, want_published",
    [
        pytest.param(False, True, id="#1 - OK - embedded and published"),
        pytest.param(True, False, id="#2 - FAIL - rag down, stays draft"),
    ],
)
def test_embed(tmp_path, rag_fails, want_published) -> None:
    svc, store, rag = make(tmp_path, rag=FakeRag(fail=rag_fails))
    created = svc.create(DATA, PDF)

    svc.embed(created.id, created.file_path)

    assert (store.published == [created.id]) is want_published
    if not rag_fails:
        assert rag.embedded == [(created.id, f"{created.id}.pdf", PDF)]


def test_create_insert_fails_removes_file(tmp_path) -> None:
    svc, _, _ = make(tmp_path, store=FakeStore(fail=True))

    with pytest.raises(RuntimeError):
        svc.create(DATA, PDF)

    assert list(tmp_path.iterdir()) == []
