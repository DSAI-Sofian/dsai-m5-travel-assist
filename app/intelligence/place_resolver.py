"""Deterministic place resolver for broad, regional, and remote travel inputs."""

from __future__ import annotations

from typing import Any


COUNTRY_DEFAULTS: dict[str, dict[str, Any]] = {
    "malaysia": {
        "resolved_destination": "Kuala Lumpur",
        "display_destination": "Malaysia",
        "gateway_city": "Kuala Lumpur",
        "airport": "KUL",
        "resolution_type": "country_default",
        "confidence": "medium",
    },
    "indonesia": {
        "resolved_destination": "Jakarta",
        "display_destination": "Indonesia",
        "gateway_city": "Jakarta",
        "airport": "CGK",
        "resolution_type": "country_default",
        "confidence": "medium",
    },
    "thailand": {
        "resolved_destination": "Bangkok",
        "display_destination": "Thailand",
        "gateway_city": "Bangkok",
        "airport": "BKK",
        "resolution_type": "country_default",
        "confidence": "medium",
    },
    "vietnam": {
        "resolved_destination": "Ho Chi Minh City",
        "display_destination": "Vietnam",
        "gateway_city": "Ho Chi Minh City",
        "airport": "SGN",
        "resolution_type": "country_default",
        "confidence": "medium",
    },
}

REGION_DEFAULTS: dict[str, dict[str, Any]] = {
    "sabah": {
        "resolved_destination": "Kota Kinabalu",
        "display_destination": "Sabah",
        "gateway_city": "Kota Kinabalu",
        "airport": "BKI",
        "resolution_type": "region_gateway",
        "confidence": "high",
    },
    "east malaysia": {
        "resolved_destination": "Kota Kinabalu",
        "display_destination": "East Malaysia",
        "gateway_city": "Kota Kinabalu",
        "airport": "BKI",
        "resolution_type": "region_gateway",
        "confidence": "medium",
    },
    "west malaysia": {
        "resolved_destination": "Kuala Lumpur",
        "display_destination": "West Malaysia",
        "gateway_city": "Kuala Lumpur",
        "airport": "KUL",
        "resolution_type": "region_gateway",
        "confidence": "medium",
    },
    "peninsular malaysia": {
        "resolved_destination": "Kuala Lumpur",
        "display_destination": "Peninsular Malaysia",
        "gateway_city": "Kuala Lumpur",
        "airport": "KUL",
        "resolution_type": "region_gateway",
        "confidence": "medium",
    },
    "bali": {
        "resolved_destination": "Denpasar",
        "display_destination": "Bali",
        "gateway_city": "Denpasar",
        "airport": "DPS",
        "resolution_type": "region_gateway",
        "confidence": "high",
    },
    "phuket": {
        "resolved_destination": "Phuket",
        "display_destination": "Phuket",
        "gateway_city": "Phuket",
        "airport": "HKT",
        "resolution_type": "region_gateway",
        "confidence": "high",
    },
}

REMOTE_PLACE_GATEWAYS: dict[str, dict[str, Any]] = {
    "mabul island": {
        "resolved_destination": "Semporna",
        "display_destination": "Mabul Island",
        "gateway_city": "Tawau",
        "airport": "TWU",
        "resolution_type": "remote_place_gateway",
        "confidence": "medium",
    },
    "sipadan": {
        "resolved_destination": "Semporna",
        "display_destination": "Sipadan",
        "gateway_city": "Tawau",
        "airport": "TWU",
        "resolution_type": "remote_place_gateway",
        "confidence": "medium",
    },
    "perhentian islands": {
        "resolved_destination": "Kuala Besut",
        "display_destination": "Perhentian Islands",
        "gateway_city": "Kota Bharu",
        "airport": "KBR",
        "resolution_type": "remote_place_gateway",
        "confidence": "medium",
    },
    "tioman": {
        "resolved_destination": "Mersing",
        "display_destination": "Tioman Island",
        "gateway_city": "Johor Bahru",
        "airport": "JHB",
        "resolution_type": "remote_place_gateway",
        "confidence": "medium",
    },
}

CITY_AIRPORTS: dict[str, str] = {
    "kuala lumpur": "KUL",
    "kota kinabalu": "BKI",
    "bangkok": "BKK",
    "denpasar": "DPS",
    "jakarta": "CGK",
    "phuket": "HKT",
    "singapore": "SIN",
    "ho chi minh city": "SGN",
    "hanoi": "HAN",
    "penang": "PEN",
    "bandung": "BDO",
}


def _normalize_place(value: str) -> str:
    return str(value or "").strip().lower()


def _title_place(value: str) -> str:
    return " ".join(word.capitalize() for word in str(value or "").split())


def resolve_place(place: str) -> dict[str, Any]:
    """
    Resolve a user-supplied place into a planning destination.

    The resolver is deterministic and API-free. It supports:
    - country defaults
    - regional gateways
    - remote-place gateways
    - known cities
    - unknown pass-through
    """
    key = _normalize_place(place)

    if not key:
        return {
            "input": place,
            "resolved_destination": "",
            "display_destination": "",
            "gateway_city": "",
            "airport": None,
            "resolution_type": "empty",
            "confidence": "low",
        }

    if key in REMOTE_PLACE_GATEWAYS:
        return {"input": place, **REMOTE_PLACE_GATEWAYS[key]}

    if key in REGION_DEFAULTS:
        return {"input": place, **REGION_DEFAULTS[key]}

    if key in COUNTRY_DEFAULTS:
        return {"input": place, **COUNTRY_DEFAULTS[key]}

    if key in CITY_AIRPORTS:
        city = _title_place(key)
        return {
            "input": place,
            "resolved_destination": city,
            "display_destination": city,
            "gateway_city": city,
            "airport": CITY_AIRPORTS[key],
            "resolution_type": "city",
            "confidence": "high",
        }

    display = _title_place(place)
    return {
        "input": place,
        "resolved_destination": display,
        "display_destination": display,
        "gateway_city": display,
        "airport": None,
        "resolution_type": "unknown_passthrough",
        "confidence": "low",
    }


def resolve_places(places: list[str]) -> dict[str, Any]:
    """
    Resolve multiple destination strings.

    Returns:
    {
      "resolved_destinations": [...],
      "display_destinations": [...],
      "metadata": [...]
    }
    """
    metadata = [resolve_place(place) for place in places if str(place).strip()]

    return {
        "resolved_destinations": [
            item["resolved_destination"] for item in metadata if item["resolved_destination"]
        ],
        "display_destinations": [
            item["display_destination"] for item in metadata if item["display_destination"]
        ],
        "metadata": metadata,
    }