import httpx


class RagClient:
    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    def embed_pdf(self, innovation_id: str, filename: str, pdf: bytes) -> None:
        # rag replaces all chunks of the innovation, so a retry is harmless
        res = httpx.post(
            f"{self._base_url}/embed/pdf",
            data={"innovation_id": innovation_id, "source": filename},
            files={"file": (filename, pdf, "application/pdf")},
            timeout=self._timeout,
        )
        res.raise_for_status()
