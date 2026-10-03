import re


class MockTaggingService:
    """Deterministic stand-in for the future LLM tagger."""

    def generate(self, text: str) -> list[str]:
        words = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", text.lower())
        tags: list[str] = []
        for word in words:
            if len(word) < 4 or word in tags:
                continue
            tags.append(word)
            if len(tags) == 10:
                break
        return tags