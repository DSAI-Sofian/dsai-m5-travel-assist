from __future__ import annotations

from typing import Any, Dict


def interpret_user_feedback(text: str | None) -> Dict[str, Any]:
    """
    Lightweight deterministic feedback interpreter.

    Converts user follow-up messages into routing/selection hints.
    This avoids LLM dependency and keeps behavior predictable.
    """

    raw = (text or "").strip()
    normalized = raw.lower()

    result: Dict[str, Any] = {
        "has_feedback": False,
        "feedback_text": raw,
        "preferred_variant": None,
        "adjustment": None,
        "confidence": 0.0,
        "reason": None,
    }

    if not normalized:
        return result

    cheaper_terms = [
        "cheaper",
        "cheap",
        "lower cost",
        "less expensive",
        "budget",
        "save money",
        "too expensive",
        "cost less",
    ]

    comfort_terms = [
        "comfort",
        "comfortable",
        "upgrade",
        "better hotel",
        "nicer hotel",
        "less tiring",
        "premium",
    ]

    balanced_terms = [
        "balanced",
        "middle",
        "reasonable",
        "best fit",
        "normal option",
    ]

    activity_terms = [
        "more activities",
        "more things to do",
        "more attractions",
        "packed itinerary",
        "more sightseeing",
        "more places",
    ]

    slower_terms = [
        "less packed",
        "slower",
        "more relaxed",
        "relaxing",
        "less tiring",
        "not too rushed",
        "more free time",
    ]

    if any(term in normalized for term in cheaper_terms):
        result.update(
            {
                "has_feedback": True,
                "preferred_variant": "Budget Saver",
                "adjustment": "lower_cost",
                "confidence": 0.95,
                "reason": "User requested a cheaper or more budget-friendly option.",
            }
        )
        return result

    if any(term in normalized for term in comfort_terms):
        result.update(
            {
                "has_feedback": True,
                "preferred_variant": "Comfort Upgrade",
                "adjustment": "more_comfort",
                "confidence": 0.95,
                "reason": "User requested more comfort or an upgraded experience.",
            }
        )
        return result

    if any(term in normalized for term in balanced_terms):
        result.update(
            {
                "has_feedback": True,
                "preferred_variant": "Balanced Pick",
                "adjustment": "balanced",
                "confidence": 0.9,
                "reason": "User requested a balanced option.",
            }
        )
        return result

    if any(term in normalized for term in activity_terms):
        result.update(
            {
                "has_feedback": True,
                "preferred_variant": None,
                "adjustment": "more_activities",
                "confidence": 0.85,
                "reason": "User requested more activities or a fuller itinerary.",
            }
        )
        return result

    if any(term in normalized for term in slower_terms):
        result.update(
            {
                "has_feedback": True,
                "preferred_variant": None,
                "adjustment": "slower_pace",
                "confidence": 0.85,
                "reason": "User requested a slower or more relaxed itinerary.",
            }
        )
        return result

    return result