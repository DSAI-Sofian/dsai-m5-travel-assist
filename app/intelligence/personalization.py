"""Deterministic personalization profile builder for travel preferences."""

from __future__ import annotations

from typing import Any


STYLE_PRIORITY = ("luxury", "budget", "food", "adventure", "general")

STYLE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "food": ("food", "foodie", "restaurant", "restaurants", "local food", "seafood"),
    "luxury": ("luxury", "premium", "comfort", "comfortable", "upgrade"),
    "budget": ("budget", "cheap", "cheaper", "save", "saver"),
    "adventure": ("adventure", "hiking", "outdoors", "diving", "snorkeling", "nature"),
}

TAG_KEYWORDS: dict[str, tuple[str, ...]] = {
    "food": ("food", "foodie", "restaurant", "restaurants", "local food", "seafood"),
    "shopping": ("shopping", "mall", "market", "markets"),
    "adventure": ("adventure", "hiking", "outdoors", "diving", "snorkeling"),
    "culture": ("culture", "museum", "heritage", "temple", "cultural"),
    "relax": ("relax", "relaxing", "beach", "slow", "relaxed"),
    "luxury": ("luxury", "premium", "comfort", "comfortable", "upgrade"),
    "budget": ("budget", "cheap", "cheaper", "save", "saver"),
    "nature": ("nature", "park", "parks", "wildlife", "waterfall", "mountain"),
}

ACTIVITY_BIAS_MAP: dict[str, list[str]] = {
    "food": ["restaurants", "local_food", "markets"],
    "shopping": ["malls", "markets", "shopping_streets"],
    "culture": ["museums", "heritage_sites", "temples"],
    "adventure": ["diving", "snorkeling", "hiking", "viewpoints", "outdoor_spots"],
    "relax": ["cafes", "parks", "beaches"],
    "nature": ["parks", "viewpoints", "wildlife", "waterfalls"],
}


def _normalize_preferences(preferences: list[str] | None) -> str:
    if not preferences:
        return ""

    cleaned_parts = [
        str(item).strip().lower()
        for item in preferences
        if str(item).strip()
    ]

    return " ".join(cleaned_parts)


def _detect_interest_tags(text: str) -> list[str]:
    tags: list[str] = []

    for tag, keywords in TAG_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            tags.append(tag)

    return tags


def _choose_travel_style(text: str) -> str:
    matched_styles: set[str] = set()

    for style, keywords in STYLE_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            matched_styles.add(style)

    if not matched_styles:
        return "general"

    for style in STYLE_PRIORITY:
        if style in matched_styles:
            return style

    return "general"


def _hotel_tier_for_style(travel_style: str) -> str:
    if travel_style == "luxury":
        return "premium"

    if travel_style == "budget":
        return "budget"

    return "mid"


def _build_activity_bias(interest_tags: list[str]) -> list[str]:
    bias: list[str] = []
    seen: set[str] = set()

    for tag in interest_tags:
        for activity in ACTIVITY_BIAS_MAP.get(tag, []):
            if activity not in seen:
                seen.add(activity)
                bias.append(activity)

    return bias


def build_personalization_profile(
    preferences: list[str] | None = None,
    source: str = "generated",
) -> dict[str, Any]:
    text = _normalize_preferences(preferences)

    interest_tags = _detect_interest_tags(text)
    travel_style = _choose_travel_style(text)
    hotel_tier = _hotel_tier_for_style(travel_style)
    activity_bias = _build_activity_bias(interest_tags)

    if not activity_bias:
        activity_bias = ["general_sightseeing"]

    return {
        "travel_style": travel_style,
        "interest_tags": interest_tags,
        "hotel_tier": hotel_tier,
        "activity_bias": activity_bias,
        "source": source,
    }


def default_personalization_profile(reason: str = "personalization_skipped") -> dict[str, Any]:
    return {
        "travel_style": "general",
        "interest_tags": [],
        "hotel_tier": "mid",
        "activity_bias": ["general_sightseeing"],
        "source": "defaulted",
        "reason": reason,
    }


def personalize_request(parsed_request: dict) -> dict:
    preferences = parsed_request.get("preferences", [])

    if not preferences:
        return default_personalization_profile(
            reason="no_clean_preferences_detected"
        )

    return build_personalization_profile(
        preferences=preferences,
        source="generated",
    )