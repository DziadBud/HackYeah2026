from collections.abc import Mapping, Sequence

from app.services.ollama import OllamaClient


class AnswerService:
    def __init__(self, client: OllamaClient | None = None) -> None:
        self.client = client or OllamaClient()

    def generate(
        self, query: str, matches: Sequence[Mapping[str, object]]
    ) -> str:
        result = self.client.generate(
            "Napisz po polsku jedno krótkie zdanie wyjaśniające, czego ogólnie "
            "dotyczy zapytanie użytkownika. Nie podsumowuj wyników wyszukiwania, "
            "nie wymieniaj identyfikatorów innowacji, nie dodawaj faktów spoza "
            "zapytania i nie używaj markdown.\n\n"
            f"Zapytanie użytkownika: {query}"
        )
        if isinstance(result, dict):
            result = (
                result.get("answer")
                or result.get("summary")
                or result.get("podsumowanie")
            )
        if isinstance(result, list):
            result = " ".join(str(item) for item in result)
        if not isinstance(result, str) or not result.strip():
            raise RuntimeError("LLM returned an invalid answer")
        return result.strip()