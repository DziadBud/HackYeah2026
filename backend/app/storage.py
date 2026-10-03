from pathlib import Path


class LocalFileStorage:
    def __init__(self, root: Path) -> None:
        self._root = root

    def save(self, name: str, content: bytes) -> Path:
        self._root.mkdir(parents=True, exist_ok=True)
        path = self._root / name
        path.write_bytes(content)
        return path

    def delete(self, path: Path) -> None:
        path.unlink(missing_ok=True)
