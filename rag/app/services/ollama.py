import json
import os
from typing import Any

import httpx


class OllamaClient:
    def __init__(self) -> None:
        self.service_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

    def generate(self, prompt: str) -> Any:
        try:
            response = httpx.post(
                f"{self.service_url.rstrip('/')}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
                timeout=120.0,
            )
            response.raise_for_status()
            payload = response.json()
            return json.loads(payload["response"])
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
            raise RuntimeError("Ollama request failed") from error