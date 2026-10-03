from collections.abc import Mapping, Sequence


class MockAnswerService:
    """Deterministic stand-in for an LLM grounded in retrieved matches."""

    def generate(
        self, query: str, matches: Sequence[Mapping[str, object]]
    ) -> str:
        if not matches:
            return f"Nie znaleziono dopasowanych innowacji dla: {query}."

        innovation_ids = [str(match["innovation_id"]) for match in matches[:3]]
        if len(innovation_ids) == 1:
            return f"Znaleziono innowację o identyfikatorze: {innovation_ids[0]}."
        if len(innovation_ids) == 2:
            return (
                "Znaleziono innowacje o identyfikatorach: "
                f"{innovation_ids[0]} oraz {innovation_ids[1]}."
            )
        return (
            "Znaleziono innowacje o identyfikatorach: "
            f"{innovation_ids[0]}, {innovation_ids[1]} oraz {innovation_ids[2]}."
        )