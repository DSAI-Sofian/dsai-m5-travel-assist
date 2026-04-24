"""Deterministic personalization profile builder for travel preferences."""

from __future__ import annotations

from typing import Any

STYLE_PRIORITY = ("luxury", "budget", "food", "adventure", "general")

STYLE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "food": ("food", "foodie", "restaurant"),
    "luxury": ("luxury", "premium"),
    "budget": ("budget", "cheap"),
    "adventure": ("adventure", "hiking", "outdoors"),
}

TAG_KEYWORDS: dict[str, tuple[str, ...]] = {
    "food": ("food", "foodie", "restaurant"),
    "shopping": ("shopping", "mall", "market"),
    "adventure": ("adventure", "hiking", "outdoors"),
    "culture": ("culture", "museum", "heritage", "temple"),
    "relax": ("relax", "relaxing", "beach"),
    "luxury": ("luxury", "premium"),
    "budget": ("budget", "cheap"),
}

ACTIVITY_BIAS_MAP: dict[str, list[str]] = {
    "food": ["restaurants", "local_food", "markets"],
    "shopping": ["malls", "markets", "shopping_streets"],
    "culture": ["museums", "heritage_sites", "temples"],
    "adventure": ["hiking", "viewpoints", "outdoor_spots"],
    "relax": ["cafes", "parks", "beaches"],
}


def _normalize_preferences(preferences: list[str] | None) -> str:
    """Flatten and normalize preference text for deterministic keyword matching."""
    if not preferences:
        return ""
    cleaned_parts = [str(item).strip().lower() for item in preferences if str(item).strip()]
    return " ".join(cleaned_parts)


def _detect_interest_tags(text: str) -> list[str]:
    """Detect all supported preference tags from normalized text."""
    tags: list[str] = []
    for tag, keywords in TAG_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            tags.append(tag)
    return tags


def _choose_travel_style(text: str) -> str:
    """Choose travel style using fixed priority rules."""
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
    """Map travel style to hotel tier using deterministic rules."""
    if travel_style == "luxury":
        return "premium"
    if travel_style == "budget":
        return "budget"
    return "mid"


def _build_activity_bias(interest_tags: list[str]) -> list[str]:
    """Build ordered, de-duplicated activity bias list from interest tags."""
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
) -> dict[str, Any]:
    """
    Build a deterministic personalization profile from user preferences.

    Returns:
    {
      "travel_style": str,
      "interest_tags": list[str],
      "hotel_tier": str,
      "activity_bias": list[str],
    }
    """
    text = _normalize_preferences(preferences)
    interest_tags = _detect_interest_tags(text)
    travel_style = _choose_travel_style(text)
    hotel_tier = _hotel_tier_for_style(travel_style)
    activity_bias = _build_activity_bias(interest_tags)
    
    # ✅ Add fallback here
    if not activity_bias:
        activity_bias = ["general_sightseeing"]

    return {
        "travel_style": travel_style,
        "interest_tags": interest_tags,
        "hotel_tier": hotel_tier,
        "activity_bias": activity_bias,
    }


def personalize_request(parsed_request: dict) -> dict:
    """
    Day 3 compatibility wrapper.
    """
    return build_personalization_profile(
        preferences=parsed_request.get("preferences", [])
    )