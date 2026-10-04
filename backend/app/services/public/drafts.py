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
    canvas = social_canvas or {}
    title = summary.strip()[:80] or ""
    description = essence.strip() or summary.strip() or ""
    if canvas.get("solution"):
        description = f"{description} Rozwiązanie: {canvas['solution']}".strip()
    return {
        "title": title,
        "description": description,
        "innovativeness": "",
        "problem_diagnosis": (canvas.get("problem") or "").strip(),
        "beneficiaries": (canvas.get("beneficiaries") or target_group).strip() or target_group,
        "expected_change": "",
        "future_vision": "",
        "action_plan": _empty_plan(),
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
    card = {
        "summary": summary,
        "essence": essence,
        "target_group": target_group,
        "stage": stage,
        "problem": canvas.get("problem", ""),
        "solution": canvas.get("solution", ""),
        "beneficiaries": canvas.get("beneficiaries", target_group),
        "resources": canvas.get("resources", ""),
        "notes": notes or "",
    }
    prompt = f"""Wypełnij szkic wniosku grantowego ROPS na podstawie karty pomysłu.

KARTA POMYSŁU:
{json.dumps(card, ensure_ascii=False)}

Zasady:
- pisz po polsku, 2-4 zdania na każde pole tekstowe
- używaj TYLKO faktów z karty (nie zmyślaj statystyk ani kwot)
- cost_pln ustaw na null, note na "do oszacowania"
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
