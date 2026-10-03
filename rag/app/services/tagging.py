from app.services.ollama import OllamaClient


class TaggingService:
    def __init__(self, client: OllamaClient | None = None) -> None:
        self.client = client or OllamaClient()

    def generate(self, text: str) -> list[str]:
        result = self.client.generate(
            "Wygeneruj od 3 do 10 krótkich tagów opisujących tę innowację. "
            "Zwróć wyłącznie poprawny JSON jako tablicę stringów, bez markdown.\n\n"
            f"Tekst innowacji:\n{text}"
        )
        if isinstance(result, dict):
            result = result.get("tags")
        if not isinstance(result, list) or not all(
            isinstance(tag, str) for tag in result
        ):
            raise RuntimeError("LLM returned invalid innovation tags")
        return result[:10]