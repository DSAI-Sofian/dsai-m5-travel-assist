from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class BudgetProfile:
    tier: str
    hotel_per_night: float
    food_per_day: float
    activities_per_day: float
    local_transport_per_day: float
    intercity_transport_total: float
    flight_estimate: float
    buffer_rate: float


DESTINATION_COST_BASELINES = {
    "vietnam": {
        "hotel": 55,
        "food": 28,
        "activities": 25,
        "local_transport": 12,
        "intercity": 180,
        "flight": 350,
    },
    "indonesia": {
        "hotel": 65,
        "food": 32,
        "activities": 35,
        "local_transport": 18,
        "intercity": 250,
        "flight": 330,
    },
    "hanoi": {
        "hotel": 50,
        "food": 25,
        "activities": 22,
        "local_transport": 10,
        "intercity": 40,
        "flight": 320,
    },
    "penang": {
        "hotel": 60,
        "food": 30,
        "activities": 18,
        "local_transport": 12,
        "intercity": 30,
        "flight": 180,
    },
    "default": {
        "hotel": 70,
        "food": 35,
        "activities": 30,
        "local_transport": 18,
        "intercity": 150,
        "flight": 350,
    },
}


TIER_MULTIPLIERS = {
    "budget": {
        "hotel": 0.75,
        "food": 0.80,
        "activities": 0.80,
        "local_transport": 0.85,
        "buffer": 0.10,
    },
    "comfort": {
        "hotel": 1.20,
        "food": 1.15,
        "activities": 1.20,
        "local_transport": 1.15,
        "buffer": 0.15,
    },
    "premium": {
        "hotel": 1.80,
        "food": 1.60,
        "activities": 1.70,
        "local_transport": 1.50,
        "buffer": 0.20,
    },
}


def normalize_destination_key(destination: str) -> str:
    if not destination:
        return "default"

    value = destination.strip().lower()

    if "vietnam" in value:
        return "vietnam"
    if "indonesia" in value:
        return "indonesia"
    if "hanoi" in value:
        return "hanoi"
    if "penang" in value:
        return "penang"

    return value if value in DESTINATION_COST_BASELINES else "default"


def calculate_budget(
    destination: str,
    duration_days: int,
    travelers: int = 1,
    tier: str = "comfort",
) -> Dict[str, Any]:
    duration_days = max(int(duration_days or 1), 1)
    travelers = max(int(travelers or 1), 1)

    destination_key = normalize_destination_key(destination)
    baseline = DESTINATION_COST_BASELINES.get(destination_key, DESTINATION_COST_BASELINES["default"])
    multiplier = TIER_MULTIPLIERS.get(tier, TIER_MULTIPLIERS["comfort"])

    hotel_total = baseline["hotel"] * multiplier["hotel"] * max(duration_days - 1, 1)
    food_total = baseline["food"] * multiplier["food"] * duration_days
    activities_total = baseline["activities"] * multiplier["activities"] * duration_days
    local_transport_total = baseline["local_transport"] * multiplier["local_transport"] * duration_days

    intercity_total = baseline["intercity"]
    flight_total = baseline["flight"] * travelers

    subtotal = (
        hotel_total
        + food_total
        + activities_total
        + local_transport_total
        + intercity_total
        + flight_total
    )

    buffer_total = subtotal * multiplier["buffer"]
    grand_total = subtotal + buffer_total

    return {
        "destination": destination,
        "duration_days": duration_days,
        "travelers": travelers,
        "tier": tier,
        "currency": "SGD",
        "breakdown": {
            "flights": round(flight_total, 2),
            "accommodation": round(hotel_total, 2),
            "food": round(food_total, 2),
            "activities": round(activities_total, 2),
            "local_transport": round(local_transport_total, 2),
            "intercity_transport": round(intercity_total, 2),
            "buffer": round(buffer_total, 2),
        },
        "estimated_total": round(grand_total, 2),
        "estimated_daily_average": round(grand_total / duration_days, 2),
    }


def generate_budget_variants(
    destination: str,
    duration_days: int,
    travelers: int = 1,
) -> Dict[str, Any]:
    return {
        "budget": calculate_budget(destination, duration_days, travelers, "budget"),
        "comfort": calculate_budget(destination, duration_days, travelers, "comfort"),
        "premium": calculate_budget(destination, duration_days, travelers, "premium"),
    }