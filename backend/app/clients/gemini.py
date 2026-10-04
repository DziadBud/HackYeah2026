import json
from typing import Any

from google import genai
from google.genai import types

from app.config import settings
from app.services.admin.errors import UpstreamUnavailableError


class GeminiClient:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self._api_key = api_key
        self._model = model

    def generate_json(self, prompt: str) -> dict[str, Any]:
        api_key = self._api_key if self._api_key is not None else settings.gemini_api_key
        model = self._model if self._model is not None else settings.gemini_model
        if not api_key:
            raise UpstreamUnavailableError("GEMINI_API_KEY is not set")
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            text = (response.text or "").strip()
            if not text:
                raise UpstreamUnavailableError("gemini returned an empty response")
            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                raise ValueError("gemini json root must be an object")
            return parsed
        except UpstreamUnavailableError:
            raise
        except Exception as exc:
            raise UpstreamUnavailableError(f"gemini request failed: {exc}") from exc
