from typing import Protocol

from google import genai
from google.genai import types

from app.config import settings
from app.services.llm.errors import LlmError


class LlmClient(Protocol):
    def generate(self, prompt: str, *, system: str | None = None) -> str: ...


class GeminiClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.gemini_api_key
        self._model = model if model is not None else settings.gemini_model
        self._client: genai.Client | None = None

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        if not self._api_key:
            raise LlmError("GEMINI_API_KEY is not set")

        try:
            response = self._get_client().models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=system)
                if system
                else None,
            )
        except LlmError:
            raise
        except Exception as exc:
            raise LlmError(f"gemini request failed: {exc}") from exc

        text = (response.text or "").strip()
        if not text:
            raise LlmError("gemini returned an empty response")
        return text

    def _get_client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(api_key=self._api_key)
        return self._client


def get_llm_client() -> GeminiClient:
    return GeminiClient()
