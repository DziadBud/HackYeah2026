from collections.abc import Mapping, Sequence

from app.services.ollama import OllamaClient


class AnswerService:
    def __init__(self, client: OllamaClient | None = None) -> None:
        self.client = client or OllamaClient()

    def generate(
        self, query: str, matches: Sequence[Mapping[str, object]]
    ) -> str:
        result = self.client.generate(
            "Odpowiedz po polsku w jednym lub dwóch zdaniach. "
            "Podsumuj wyłącznie to, co wynika z listy znalezionych identyfikatorów. "
            "Nie wymyślaj szczegółów i nie używaj markdown.\n\n"
            f"Zapytanie: {query}\n"
            f"Znalezione innowacje: {[match['innovation_id'] for match in matches[:3]]}"
        )
        if isinstance(result, dict):
            result = result.get("answer")
        if not isinstance(result, str) or not result.strip():
            raise RuntimeError("LLM returned an invalid answer")
        return result.strip()