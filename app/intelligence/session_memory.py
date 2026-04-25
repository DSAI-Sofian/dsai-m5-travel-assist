from __future__ import annotations

from typing import Any


def build_session_memory_snapshot(state: dict[str, Any]) -> dict[str, Any]:
    """
    Builds lightweight memory from the completed workflow state.

    This is not database persistence yet.
    It is request-level memory output that can later be stored by API/session layer.
    """

    parsed = state.get("parsed_request", {}) or {}
    selected_variant = state.get("selected_variant", {}) or {}
    executor_output = state.get("executor_output", {}) or {}
    ranking_output = state.get("ranking_output", {}) or {}
    personalization = state.get("personalization", {}) or {}

    return {
        "last_origin": parsed.get("origin"),
        "last_destinations": state.get("display_destinations")
        or parsed.get("display_destinations")
        or parsed.get("destinations", []),
        "last_budget": parsed.get("budget"),
        "last_duration_days": parsed.get("duration_days"),
        "last_travelers": parsed.get("travelers"),
        "last_preferences": parsed.get("preferences", []),
        "last_travel_style": personalization.get("travel_style"),
        "last_hotel_tier": personalization.get("hotel_tier"),
        "last_selected_variant": selected_variant.get("variant_label")
        or executor_output.get("variant_label"),
        "last_selected_variant_key": selected_variant.get("variant_key")
        or executor_output.get("variant_key"),
        "last_estimated_total": ranking_output.get("estimated_total"),
        "last_score_pct": ranking_output.get("score_pct"),
        "last_itinerary_days": len(executor_output.get("daily_itinerary", [])),
    }


def apply_memory_to_raw_request(
    raw_request: str,
    memory: dict[str, Any] | None,
) -> str:
    """
    Applies lightweight memory hints to a new raw request.

    This supports phrases like:
    - same style as previous trip
    - same destination
    - same budget
    - cheaper than before
    """

    if not memory:
        return raw_request

    normalized = raw_request.lower()
    additions: list[str] = []

    if "same destination" in normalized:
        destinations = memory.get("last_destinations") or []
        if destinations:
            additions.append("destination " + ", ".join(destinations))

    if "same budget" in normalized:
        budget = memory.get("last_budget")
        if budget:
            additions.append(f"budget S${budget}")

    if "same style" in normalized or "previous style" in normalized:
        travel_style = memory.get("last_travel_style")
        if travel_style:
            additions.append(f"{travel_style} style")

    if "same hotel" in normalized or "same comfort" in normalized:
        hotel_tier = memory.get("last_hotel_tier")
        if hotel_tier:
            additions.append(f"{hotel_tier} hotel")

    if "cheaper than before" in normalized:
        last_budget = memory.get("last_budget")
        if last_budget:
            cheaper_budget = int(float(last_budget) * 0.85)
            additions.append(f"budget S${cheaper_budget}")

    if not additions:
        return raw_request

    return raw_request + " " + " ".join(additions)