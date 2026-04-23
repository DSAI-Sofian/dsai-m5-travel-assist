"""Deterministic realism checks for generated trip itineraries."""

from __future__ import annotations

from typing import Any

KEYWORDS = (
    "arrival",
    "flight",
    "check-in",
    "depart",
    "departure",
    "checkout",
    "transfer",
)


def _safe_days(duration_days: int) -> int:
    """Normalize duration to a deterministic minimum of 1 day."""
    try:
        days = int(duration_days)
    except Exception:
        return 1
    return max(days, 1)


def _to_text(value: Any) -> str:
    """Convert value to lowercase text for keyword checks."""
    return str(value or "").strip().lower()


def _contains_ops_keywords(text: str) -> bool:
    """Check whether text contains arrival/departure/transfer keywords."""
    return any(k in text for k in KEYWORDS)


def _is_overloaded_day(entry: dict[str, Any]) -> bool:
    """
    Heuristic for overloaded day:
    keyword day text + rich detail text likely indicating many activities.
    """
    title = _to_text(entry.get("title", ""))
    details = _to_text(entry.get("details", ""))
    day_text = f"{title} {details}".strip()
    if not _contains_ops_keywords(day_text):
        return False

    # Simple deterministic proxies for "many activities"
    separators = details.count(",") + details.count(";")
    mention_count = sum(details.count(word) for word in ("then", "after", "and"))
    detail_len = len(details.split())
    return separators >= 2 or mention_count >= 4 or detail_len >= 24


def assess_trip_realism(
    destination: str,
    duration_days: int,
    daily_itinerary: list[dict],
    travel_details: dict | None = None,
) -> dict[str, Any]:
    """
    Assess itinerary realism using deterministic, rule-based checks.

    Returns:
    {
      "feasible": bool,
      "pace": "light" | "balanced" | "packed",
      "flags": list[str],
      "notes": list[str],
      "recommended_best_fit_days": int,
    }
    """
    _ = destination
    _ = travel_details

    days = _safe_days(duration_days)
    itinerary = daily_itinerary if isinstance(daily_itinerary, list) else []
    items_total = len(itinerary)
    avg_items_per_day = items_total / days if days else float(items_total)

    flags: list[str] = []
    notes: list[str] = []
    pace = "balanced"

    if (days <= 2 and items_total > 3) or avg_items_per_day >= 1.6:
        pace = "packed"
        flags.append("too_many_activities_for_duration")
        notes.append(
            "The itinerary appears dense for the trip duration and may feel rushed."
        )
    elif days >= 4 and items_total <= 2:
        pace = "light"
        flags.append("too_few_activities_for_duration")
        notes.append(
            "The itinerary appears light for the trip duration and may underuse travel time."
        )

    if itinerary:
        first = itinerary[0] if isinstance(itinerary[0], dict) else {}
        if _is_overloaded_day(first):
            flags.append("arrival_day_overloaded")
            notes.append(
                "Arrival/check-in day appears overloaded with activities; consider reducing first-day load."
            )

        last = itinerary[-1] if isinstance(itinerary[-1], dict) else {}
        if _is_overloaded_day(last):
            flags.append("departure_day_overloaded")
            notes.append(
                "Departure/checkout day appears overloaded with activities; consider simplifying the final day."
            )

    flags = list(dict.fromkeys(flags))
    notes = list(dict.fromkeys(notes))

    recommended_best_fit_days = days
    if pace == "packed":
        recommended_best_fit_days = days + 1
    elif pace == "light" and days > 2:
        recommended_best_fit_days = days - 1

    recommended_best_fit_days = max(recommended_best_fit_days, 1)
    feasible = pace != "packed"

    return {
        "feasible": feasible,
        "pace": pace,
        "flags": flags,
        "notes": notes,
        "recommended_best_fit_days": recommended_best_fit_days,
    }
