from pathlib import Path

import pytest

from app.schemas.admin.common import ChallengeArea
from app.schemas.admin.innovations import CostLevel, Readiness
from app.services.admin.errors import (
    EmbedPublishError,
    InvalidUploadError,
    UploadTooLargeError,
)
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
        self.fail = fail

    def insert_draft(self, innovation_id: str, data: NewInnovation, tags: list[str]) -> None:
        if self.fail:
            raise RuntimeError("db down")
        self.rows[innovation_id] = tags

    def delete(self, innovation_id: str) -> None:
        self.rows.pop(innovation_id, None)


class FakeFiles:
    def __init__(self, root: Path) -> None:
        self.root = root

    def save(self, name: str, content: bytes) -> Path:
        path = self.root / name
        path.write_bytes(content)
        return path

    def delete(self, path: Path) -> None:
        path.unlink(missing_ok=True)


class FakePublisher:
    def __init__(self, fail: bool = False) -> None:
        self.sent: list[tuple[str, str]] = []
        self.fail = fail

    def publish_embed_requested(self, innovation_id: str, file_path: str) -> None:
        if self.fail:
            raise ConnectionError("broker down")
        self.sent.append((innovation_id, file_path))


def make(tmp_path: Path, store=None, publisher=None, max_bytes: int = 1024):
    store = store or FakeStore()
    publisher = publisher or FakePublisher()
    svc = InnovationUploadService(store, FakeFiles(tmp_path), publisher, max_bytes)
    return svc, store, publisher


@pytest.mark.parametrize(
    "content, err",
    [
        pytest.param(PDF, None, id="#1 - OK"),
        pytest.param(b"hello", InvalidUploadError, id="#2 - FAIL - not a pdf"),
        pytest.param(PDF + b"x" * 2000, UploadTooLargeError, id="#3 - FAIL - too large"),
    ],
)
def test_create(tmp_path, content, err) -> None:
    svc, store, publisher = make(tmp_path)

    if err:
        with pytest.raises(err):
            svc.create(DATA, content)
        assert store.rows == {} and publisher.sent == []
        return

    created = svc.create(DATA, content)

    assert created.status == "draft"
    assert created.id.startswith("wibraap-opaska-dla-seniorow-")
    assert store.rows[created.id] == ["opaska", "type:innovation", "area:seniorzy", "area:zdrowie-psychiczne"]
    assert publisher.sent == [(created.id, created.file_path)]
    assert Path(created.file_path).read_bytes() == PDF


def test_create_publish_fails_rolls_back(tmp_path) -> None:
    svc, store, _ = make(tmp_path, publisher=FakePublisher(fail=True))

    with pytest.raises(EmbedPublishError):
        svc.create(DATA, PDF)

    assert store.rows == {}
    assert list(tmp_path.iterdir()) == []


def test_create_insert_fails_removes_file(tmp_path) -> None:
    svc, _, publisher = make(tmp_path, store=FakeStore(fail=True))

    with pytest.raises(RuntimeError):
        svc.create(DATA, PDF)

    assert publisher.sent == []
    assert list(tmp_path.iterdir()) == []
