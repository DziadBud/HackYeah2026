import re
import unicodedata

from app.schemas.admin.grant_calls import GrantCall
from app.schemas.admin.innovations import Innovation
from app.schemas.public.documents import MiddlemanRequest

# stand-ins for rag retrieval and the llm, shared by the mock and db services until the
# rag client and llm prompts land


def words(text: str) -> set[str]:
    # crude polish stemming: diacritics folded, first 5 letters of every word longer than 3
    folded = unicodedata.normalize("NFKD", text.lower().replace("ł", "l")).encode("ascii", "ignore").decode()
    return {w[:5] for w in re.findall(r"\w+", folded) if len(w) > 3}


def overlap(query: set[str], innovation: Innovation) -> int:
    return len(query & words(f"{innovation.title} {innovation.summary}"))


def explain_fit(innovation: Innovation) -> str:
    areas = ", ".join(a.value for a in innovation.challenge_areas)
    return f"Pasuje, bo dotyczy: {areas or innovation.title}."


def middleman_card(innovation: Innovation, data: MiddlemanRequest) -> str:
    return (
        f"Usługa: {innovation.title} dla instytucji typu {data.institution_type.value}\n"
        f"Potrzeba: {data.needs}\n"
        f"Na czym polega: {innovation.summary}\n"
        "Koszt: do oszacowania"
    )


def grant_draft(idea_summary: str, call: GrantCall) -> str:
    # one section per form section, filled from the idea card
    sections = [
        f"## {s.title}\n{idea_summary if i == 0 else '[uzupełnij]'}"
        for i, s in enumerate(call.sections)
    ]
    return "\n\n".join(sections) or idea_summary
