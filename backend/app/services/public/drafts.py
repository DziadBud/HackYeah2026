import json
import logging
import re
import unicodedata
from typing import Any

from app.clients.gemini import GeminiClient
from app.schemas.admin.innovations import Innovation
from app.schemas.public.documents import MiddlemanRequest
from app.services.admin.errors import UpstreamUnavailableError

logger = logging.getLogger(__name__)

_REQUIRED = (
    "title",
    "description",
    "innovativeness",
    "problem_diagnosis",
    "beneficiaries",
    "expected_change",
    "future_vision",
    "action_plan",
)

_OUTPUT_EXAMPLE = {
    "title": "...",
    "description": "...",
    "innovativeness": "...",
    "problem_diagnosis": "...",
    "beneficiaries": "...",
    "expected_change": "...",
    "future_vision": "...",
    "action_plan": {
        "preparation_summary": "...",
        "preparation": [
            {"action": "...", "timeline": "miesiąc 1-3", "cost_pln": None, "note": "do oszacowania"}
        ],
        "testing_summary": "...",
        "testing_phase_1": [
            {"action": "...", "timeline": "miesiąc 4-6", "cost_pln": None, "note": "do oszacowania"}
        ],
        "testing_phase_2": [
            {"action": "...", "timeline": "miesiąc 7-9", "cost_pln": None, "note": "do oszacowania"}
        ],
    },
}


def words(text: str) -> set[str]:
    folded = unicodedata.normalize("NFKD", text.lower().replace("ł", "l")).encode("ascii", "ignore").decode()
    return {w[:5] for w in re.findall(r"\w+", folded) if len(w) > 3}


def overlap(query: set[str], innovation: Innovation) -> int:
    return len(query & words(f"{innovation.title} {innovation.summary}"))


def middleman_card(innovation: Innovation, data: MiddlemanRequest) -> str:
    return (
        f"Usługa: {innovation.title} dla instytucji typu {data.institution_type.value}\n"
        f"Potrzeba: {data.needs}\n"
        f"Na czym polega: {innovation.summary}\n"
        "Koszt: do oszacowania"
    )


def grant_draft_fields(
    *,
    summary: str,
    essence: str,
    target_group: str,
    stage: str,
    social_canvas: dict[str, Any] | None = None,
    notes: str | None = None,
    llm: GeminiClient | None = None,
) -> dict[str, Any]:
    """AI/template fields for form sections 1+3–9. Returns a plain dict for DB columns."""
    if llm is not None:
        try:
            return _from_gemini(summary, essence, target_group, stage, social_canvas, notes, llm)
        except (UpstreamUnavailableError, ValueError, TypeError, KeyError) as exc:
            logger.warning("grant draft llm failed, using template: %s", exc)
    return _template(summary, essence, target_group, social_canvas)


def _empty_plan() -> dict[str, Any]:
    return {
        "preparation_summary": "",
        "preparation": [],
        "testing_summary": "",
        "testing_phase_1": [],
        "testing_phase_2": [],
    }


def _template(
    summary: str,
    essence: str,
    target_group: str,
    social_canvas: dict[str, Any] | None,
) -> dict[str, Any]:
    """Sensible starter text from the user's description (used when AI is off or fails)."""
    canvas = social_canvas or {}
    idea = (essence or summary or "").strip()
    title = (summary or idea)[:80].strip()
    audience = (canvas.get("beneficiaries") or target_group or "").strip()
    if audience.lower().startswith("do uzupełnienia"):
        audience = ""
    problem = (canvas.get("problem") or "").strip() or idea
    description = idea
    if canvas.get("solution"):
        description = f"{description} Rozwiązanie: {canvas['solution']}".strip()
    return {
        "title": title,
        "description": description
        or "Uzupełnij opis innowacji: charakter rozwiązania i związek z włączeniem społecznym.",
        "innovativeness": (
            f"Propozycja wyróżnia się podejściem opartym na: {idea[:200]}. "
            "Uzupełnij porównanie z istniejącymi rozwiązaniami w Polsce i na świecie."
            if idea
            else "Opisz, czym rozwiązanie wyróżnia się na tle istniejących praktyk."
        ),
        "problem_diagnosis": problem
        or "Opisz problem społeczny, skalę i źródła diagnozy (bez zmyślania statystyk).",
        "beneficiaries": audience
        or (
            f"Odbiorcy wynikający z opisu pomysłu: {idea[:180]}…"
            if idea
            else "Opisz grupę odbiorców, ich potrzeby i ryzyko wykluczenia."
        ),
        "expected_change": (
            f"Wdrożenie pomysłu („{title}”) ma poprawić sytuację odbiorców w zakresie opisanego problemu. "
            "Uzupełnij konkretne efekty dla włączenia społecznego."
            if title
            else "Opisz oczekiwaną zmianę w życiu odbiorców i wpływ na włączenie społeczne."
        ),
        "future_vision": (
            "Rozwiązanie ma potencjał do powielenia w innych gminach / kontekstach po pilotażu. "
            "Uzupełnij, co ułatwia skalowanie i wdrażanie."
        ),
        "action_plan": {
            "preparation_summary": "Okres przygotowawczy (do 3 miesięcy): doprecyzowanie prototypu, partnerów i narzędzi testu.",
            "preparation": [
                {
                    "action": "Doprecyzowanie koncepcji i planu testu na podstawie opisu pomysłu",
                    "timeline": "miesiąc 1",
                    "cost_pln": None,
                    "note": "do oszacowania",
                },
                {
                    "action": "Nawiązanie współpracy z partnerami / miejscem testu",
                    "timeline": "miesiąc 1-2",
                    "cost_pln": None,
                    "note": "do oszacowania",
                },
                {
                    "action": "Przygotowanie materiałów / prototypu do testowania",
                    "timeline": "miesiąc 2-3",
                    "cost_pln": None,
                    "note": "do oszacowania",
                },
            ],
            "testing_summary": "Okres testowania (do 9 miesięcy): Faza I — pierwsze próby z odbiorcami; Faza II — poprawki i model końcowy.",
            "testing_phase_1": [
                {
                    "action": "Przeprowadzenie pierwszych spotkań / sesji testujących z odbiorcami",
                    "timeline": "miesiąc 4-6",
                    "cost_pln": None,
                    "note": "do oszacowania",
                }
            ],
            "testing_phase_2": [
                {
                    "action": "Wprowadzenie poprawek i opracowanie modelu końcowego innowacji",
                    "timeline": "miesiąc 7-9",
                    "cost_pln": None,
                    "note": "do oszacowania",
                }
            ],
        },
        "generated_by": "template",
    }


def _from_gemini(
    summary: str,
    essence: str,
    target_group: str,
    stage: str,
    social_canvas: dict[str, Any] | None,
    notes: str | None,
    llm: GeminiClient,
) -> dict[str, Any]:
    canvas = social_canvas or {}
    idea_text = (essence or summary or "").strip()
    card = {
        "opis_pomyslu": idea_text,
        "summary": summary,
        "essence": essence,
        "target_group": target_group if not str(target_group).lower().startswith("do uzupełnienia") else "",
        "stage": stage,
        "problem": canvas.get("problem", ""),
        "solution": canvas.get("solution", ""),
        "beneficiaries": canvas.get("beneficiaries", ""),
        "resources": canvas.get("resources", ""),
        "notes": notes or "",
    }
    prompt = f"""Wypełnij szkic wniosku grantowego ROPS (Załącznik nr 3) na podstawie OPISU POMYSŁU użytkownika.

OPIS POMYSŁU / PROBLEM:
{json.dumps(card, ensure_ascii=False)}

Zasady:
- pisz po polsku, konkretnie, 2-5 zdań na każde pole tekstowe
- wywnioskuj z opisu: tytuł, odbiorców, diagnozę problemu, innowacyjność, oczekiwaną zmianę i wizję rozwoju
- NIE zmyślaj statystyk, dat ani kwot — jeśli brak danych, napisz to wprost i zaproponuj co użytkownik powinien uzupełnić
- cost_pln ustaw na null, note na "do oszacowania"
- action_plan: po 2-4 realnych krokach w preparation, testing_phase_1 i testing_phase_2
- nie dodawaj innych kluczy niż w przykładzie poniżej

Zwróć WYŁĄCZNIE jeden obiekt JSON dokładnie w tym kształcie:
{json.dumps(_OUTPUT_EXAMPLE, ensure_ascii=False, indent=2)}
"""
    raw = llm.generate_json(prompt)
    for key in _REQUIRED:
        if key not in raw or raw[key] in (None, ""):
            raise ValueError(f"missing or empty field: {key}")
    plan = raw.get("action_plan")
    if not isinstance(plan, dict):
        raise ValueError("action_plan must be an object")
    return {
        "title": str(raw["title"]),
        "description": str(raw["description"]),
        "innovativeness": str(raw["innovativeness"]),
        "problem_diagnosis": str(raw["problem_diagnosis"]),
        "beneficiaries": str(raw["beneficiaries"]),
        "expected_change": str(raw["expected_change"]),
        "future_vision": str(raw["future_vision"]),
        "action_plan": {
            "preparation_summary": str(plan.get("preparation_summary") or ""),
            "preparation": plan.get("preparation") or [],
            "testing_summary": str(plan.get("testing_summary") or ""),
            "testing_phase_1": plan.get("testing_phase_1") or [],
            "testing_phase_2": plan.get("testing_phase_2") or [],
        },
        "generated_by": "gemini",
    }
