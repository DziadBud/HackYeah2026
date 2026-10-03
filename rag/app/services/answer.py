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
        answer = self._extract_text(result)
        return answer or f"Zapytanie dotyczy: {query}."

    @staticmethod
    def _extract_text(value: object) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, list):
            return " ".join(
                text for item in value if (text := AnswerService._extract_text(item))
            ).strip()
        if isinstance(value, dict):
            preferred_keys = (
                "answer",
                "summary",
                "podsumowanie",
                "odpowiedz",
                "response",
                "text",
                "description",
                "opis",
            )
            for key in preferred_keys:
                if key in value:
                    text = AnswerService._extract_text(value[key])
                    if text:
                        return text
            for item in value.values():
                text = AnswerService._extract_text(item)
                if text:
                    return text
        return ""