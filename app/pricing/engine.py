"""Deterministic pricing engine for trip cost estimation."""

from __future__ import annotations


CITY_COST_INDEX: dict[str, float] = {
    "kuala lumpur": 0.85,
    "kota kinabalu": 0.95,
    "bangkok": 0.80,
    "singapore": 1.40,
    "denpasar": 0.90,
    "phuket": 0.95,
    "jakarta": 0.75,
}

HOTEL_TIER_MULTIPLIER: dict[str, float] = {
    "budget": 0.85,
    "mid": 1.00,
    "premium": 1.35,
}

TRAVEL_STYLE_TO_HOTEL_TIER: dict[str, str] = {
    "budget": "budget",
    "food": "mid",
    "adventure": "mid",
    "luxury": "premium",
}

DEFAULT_CITY_MULTIPLIER = 1.0

BASE_FLIGHT = 280.0
BASE_HOTEL_PER_NIGHT = 120.0
BASE_FOOD_PER_DAY = 40.0
BASE_TRANSPORT_PER_DAY = 18.0
BASE_ACTIVITIES_PER_DAY = 55.0


def _normalize_text(value: str | None) -> str:
    """Return normalized lowercase text for deterministic dictionary lookup."""
    return (value or "").strip().lower()


def _resolve_city_multiplier(destination: str) -> float:
    """Return cost multiplier for destination; fallback to default for unknowns."""
    key = _normalize_text(destination)
    return CITY_COST_INDEX.get(key, DEFAULT_CITY_MULTIPLIER)


def _resolve_hotel_tier(travel_style: str | None) -> str:
    """Map travel style to hotel tier, defaulting to mid tier."""
    style = _normalize_text(travel_style)
    return TRAVEL_STYLE_TO_HOTEL_TIER.get(style, "mid")


def _resolve_hotel_tier_multiplier(travel_style: str | None) -> float:
    """Return hotel tier multiplier from travel style."""
    tier = _resolve_hotel_tier(travel_style)
    return HOTEL_TIER_MULTIPLIER.get(tier, HOTEL_TIER_MULTIPLIER["mid"])


def _safe_duration_days(duration_days: int) -> int:
    """Clamp duration to a deterministic minimum of 1 day."""
    try:
        days = int(duration_days)
    except Exception:
        return 1
    return max(days, 1)


def _round_money(value: float) -> float:
    """Round monetary output to 2 decimal places."""
    return round(float(value), 2)


def estimate_trip_costs(
    destination: str,
    duration_days: int,
    traveler_type: str | None = None,
    travel_style: str | None = None,
) -> dict[str, float]:
    """
    Estimate deterministic trip costs by destination and duration.

    Pricing model:
    - destination controls city cost index
    - hotel uses per-night baseline * duration * hotel tier multiplier
    - food, transport, and activities scale by duration
    - flight is a one-time single-trip estimate
    - outputs are rounded to 2 decimals
    """
    _ = traveler_type  # Reserved for future deterministic extensions.

    days = _safe_duration_days(duration_days)
    city_multiplier = _resolve_city_multiplier(destination)
    hotel_multiplier = _resolve_hotel_tier_multiplier(travel_style)

    flight = max(200.0, BASE_FLIGHT * city_multiplier)
    hotel = BASE_HOTEL_PER_NIGHT * days * city_multiplier * hotel_multiplier
    activities = BASE_ACTIVITIES_PER_DAY * days * city_multiplier
    local_transport = BASE_TRANSPORT_PER_DAY * days * city_multiplier
    food = BASE_FOOD_PER_DAY * days * city_multiplier
    total = flight + hotel + activities + local_transport + food

    return {
        "flight": _round_money(flight),
        "hotel": _round_money(hotel),
        "activities": _round_money(activities),
        "local_transport": _round_money(local_transport),
        "food": _round_money(food),
        "total": _round_money(total),
    }
