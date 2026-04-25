from __future__ import annotations

from typing import Any


def select_variant_from_feedback(
    variants: list[dict[str, Any]],
    feedback: dict[str, Any],
    current_selected: dict[str, Any] | None = None,
) -> dict[str, Any]:

    if not variants:
        return current_selected or {}

    preferred_variant = feedback.get("preferred_variant")
    adjustment = feedback.get("adjustment")

    # Explicit variant selection
    if preferred_variant:
        for variant in variants:

            variant_label = (
                variant.get("variant_label")
                or variant.get("variant_name")
                or ""
            )

            if variant_label.lower() == preferred_variant.lower():
                return variant

    # Heuristic fallback logic
    if adjustment == "lower_cost":

        cheapest = min(
            variants,
            key=lambda v: (
                v.get("ranking", {}).get("estimated_total", 999999)
            ),
        )

        return cheapest

    if adjustment == "more_comfort":

        for variant in variants:
            if variant.get("variant_key") == "comfort":
                return variant

    if adjustment == "balanced":

        for variant in variants:
            if variant.get("variant_key") == "balanced":
                return variant

    return current_selected or variants[0]