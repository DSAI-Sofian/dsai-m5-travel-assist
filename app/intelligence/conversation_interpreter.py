from __future__ import annotations

import re
from typing import Any


def interpret_conversation_followup(text: str | None) -> dict[str, Any]:
    """
    Lightweight deterministic interpreter for conversational follow-up requests.

    This detects whether the user is asking to modify an existing/generated plan
    rather than starting a fully new request.
    """

    raw = (text or "").strip()
    normalized = raw.lower()

    result: dict[str, Any] = {
        "has_followup": False,
        "followup_text": raw,
        "continuity_mode": None,
        "requested_adjustments": [],
        "new_budget": None,
        "confidence": 0.0,
        "reason": None,
    }

    if not normalized:
        return result

    adjustments: list[str] = []

    food_terms = [
        "more food",
        "food places",
        "restaurants",
        "local food",
        "cafes",
        "hawker",
        "seafood",
        "where to eat",
    ]

    nature_terms = [
        "nature",
        "parks",
        "hiking",
        "mountain",
        "waterfall",
        "beach",
        "island",
        "wildlife",
    ]

    slower_terms = [
        "less rushed",
        "less packed",
        "slower",
        "relaxed",
        "more relaxed",
        "more free time",
        "less tiring",
    ]

    activity_terms = [
        "more activities",
        "more attractions",
        "more things to do",
        "more sightseeing",
        "add activities",
    ]

    comfort_terms = [
        "more comfort",
        "better hotel",
        "nicer hotel",
        "upgrade",
        "comfortable",
    ]

    budget_terms = [
        "increase budget",
        "change budget",
        "budget to",
        "new budget",
        "raise budget",
        "lower budget",
    ]

    if any(term in normalized for term in food_terms):
        adjustments.append("add_food_places")

    if any(term in normalized for term in nature_terms):
        adjustments.append("add_nature_activities")

    if any(term in normalized for term in slower_terms):
        adjustments.append("relax_pace")

    if any(term in normalized for term in activity_terms):
        adjustments.append("add_more_activities")

    if any(term in normalized for term in comfort_terms):
        adjustments.append("increase_comfort")

    if any(term in normalized for term in budget_terms):
        adjustments.append("change_budget")

    budget_match = re.search(r"(?:sgd|s\$|\$)?\s*(\d{3,6})", normalized)
    if budget_match and any(term in normalized for term in budget_terms):
        result["new_budget"] = float(budget_match.group(1))

    if adjustments:
        result.update(
            {
                "has_followup": True,
                "continuity_mode": "modify_existing_plan",
                "requested_adjustments": adjustments,
                "confidence": 0.9,
                "reason": "User requested a follow-up modification to the current plan.",
            }
        )

    return result