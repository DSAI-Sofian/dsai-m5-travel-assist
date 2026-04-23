"""Deterministic destination resolution utilities for Travel Assist."""

from __future__ import annotations

from typing import Any

REGION_TO_CITY: dict[str, dict[str, str]] = {
    "sabah": {"city": "Kota Kinabalu", "airport": "BKI"},
    "bali": {"city": "Denpasar", "airport": "DPS"},
    "phuket": {"city": "Phuket", "airport": "HKT"},
}

# Known city aliases that should be treated as direct city inputs.
KNOWN_CITY_ALIASES: dict[str, tuple[str, str | None]] = {
    "kota kinabalu": ("Kota Kinabalu", "BKI"),
    "denpasar": ("Denpasar", "DPS"),
    "phuket": ("Phuket", "HKT"),
}


def _normalize_text(value: str) -> str:
    """Normalize destination text for deterministic matching."""
    return value.strip().lower()


def resolve_destinations(destinations: list[str]) -> dict[str, Any]:
    """
    Resolve user destinations into canonical city-level destinations.

    Rules:
    - Lowercase + strip whitespace before matching.
    - Known regions map to a canonical city.
    - Known cities pass through unchanged (canonicalized by casing).
    - Unknown values pass through unchanged with type='unknown'.

    Returns:
        {
            "resolved_destinations": [str, ...],
            "metadata": [
                {
                    "original": str,
                    "resolved": str,
                    "type": "region" | "city" | "unknown",
                    "airport": str | None,
                },
                ...
            ],
        }
    """
    resolved_destinations: list[str] = []
    metadata: list[dict[str, Any]] = []
    seen: set[str] = set()

    for raw in destinations or []:
        original = "" if raw is None else str(raw)
        cleaned = _normalize_text(original)

        if not cleaned:
            continue

        item_type = "unknown"
        airport: str | None = None
        resolved = original.strip()

        if cleaned in REGION_TO_CITY:
            mapped = REGION_TO_CITY[cleaned]
            resolved = mapped["city"]
            airport = mapped.get("airport")
            item_type = "region"
        elif cleaned in KNOWN_CITY_ALIASES:
            resolved, airport = KNOWN_CITY_ALIASES[cleaned]
            item_type = "city"

        dedupe_key = _normalize_text(resolved)
        if dedupe_key not in seen:
            seen.add(dedupe_key)
            resolved_destinations.append(resolved)

        metadata.append(
            {
                "original": original,
                "resolved": resolved,
                "type": item_type,
                "airport": airport,
            }
        )

    return {
        "resolved_destinations": resolved_destinations,
        "metadata": metadata,
    }
