from typing import List, Dict, Any
from app.intelligence.destination_registry import (
    get_destination_profile,
    get_city_theme_items,
)


FOOD_KEYWORDS = [
    "pho",
    "banh",
    "coffee",
    "food",
    "market",
    "class",
    "laksa",
    "char",
    "nasi",
    "hawker",
    "kopitiam",
    "warung",
    "satay",
    "breakfast",
    "lunch",
    "dinner",
    "seafood",
    "café",
    "cafe",
    "dumplings",
]

CULTURE_KEYWORDS = [
    "museum",
    "temple",
    "palace",
    "mansion",
    "heritage",
    "mausoleum",
    "kongsi",
    "ancient",
    "pagoda",
    "cathedral",
    "monument",
    "mosque",
    "bridge",
]

NATURE_KEYWORDS = [
    "hill",
    "lake",
    "beach",
    "garden",
    "canal",
    "mountain",
    "waterfall",
    "fields",
    "coastal",
    "river",
    "terrace",
    "trail",
    "waterfront",
]


def chunk_days(duration_days: int, chunk_size: int = 3) -> List[range]:
    duration_days = max(int(duration_days or 1), 1)
    chunk_size = max(int(chunk_size or 3), 1)

    chunks = []
    start = 1

    while start <= duration_days:
        end = min(start + chunk_size - 1, duration_days)
        chunks.append(range(start, end + 1))
        start = end + 1

    return chunks


def _clean_preferences(preferences: List[str] | None) -> List[str]:
    if not preferences:
        return ["sightseeing"]

    cleaned = []

    for pref in preferences:
        for part in str(pref).replace(",", " ").split():
            value = part.strip().lower()
            if value:
                cleaned.append(value)

    return cleaned or ["sightseeing"]


def _classify_activity(activity: str) -> str:
    text = activity.lower()

    if any(keyword in text for keyword in FOOD_KEYWORDS):
        return "food"

    if any(keyword in text for keyword in CULTURE_KEYWORDS):
        return "culture"

    if any(keyword in text for keyword in NATURE_KEYWORDS):
        return "nature"

    return "sightseeing"


def _activity_phrase(activity: str, slot: str) -> str:
    activity_type = _classify_activity(activity)

    if activity_type == "food":
        if slot == "morning":
            return f"enjoy {activity}"
        if slot == "afternoon":
            return f"try {activity} as part of the local food trail"
        return f"enjoy {activity} or a nearby local dinner"

    if activity_type == "culture":
        if slot == "evening":
            return f"take a light walk around the {activity} area"
        return f"visit {activity}"

    if activity_type == "nature":
        return f"explore {activity}"

    return f"visit {activity}"


def _pick_item(items: List[str], day: int) -> str:
    if not items:
        return "local activity"

    return items[(day - 1) % len(items)]


def _pick_city(route: List[str], day: int, duration_days: int) -> str:
    if not route:
        return "Main area"

    if len(route) == 1:
        return route[0]

    segment_size = max(duration_days // len(route), 1)
    index = min((day - 1) // segment_size, len(route) - 1)

    return route[index]


def _available_themes_for_city(profile: Dict[str, Any], city: str) -> List[str]:
    cities = profile.get("cities", {})
    city_profile = cities.get(city, {})

    return [
        theme
        for theme, items in city_profile.items()
        if isinstance(items, list) and len(items) > 0
    ]


def _build_theme_plan(
    day: int,
    preferences: List[str],
    available_themes: List[str],
) -> Dict[str, str]:
    fallback_cycle = ["culture", "food", "sightseeing", "nature"]
    available = [theme for theme in fallback_cycle if theme in available_themes]

    if not available:
        available = available_themes or ["sightseeing"]

    preferred = [p for p in preferences if p in available]

    anchor_theme = preferred[0] if preferred else available[(day - 1) % len(available)]

    support_candidates = [
        theme for theme in available
        if theme != anchor_theme
    ]

    support_theme = (
        support_candidates[(day - 1) % len(support_candidates)]
        if support_candidates
        else anchor_theme
    )

    evening_theme = "food" if "food" in available else support_theme

    return {
        "anchor": anchor_theme,
        "support": support_theme,
        "evening": evening_theme,
    }


def _choose_activity(
    profile: Dict[str, Any],
    city: str,
    theme: str,
    day: int,
) -> str:
    city_items = get_city_theme_items(profile, city, theme)

    if city_items:
        return _pick_item(city_items, day)

    return "local activity"


def generate_structured_itinerary(
    destination: str,
    duration_days: int,
    preferences: List[str] | None = None,
) -> List[Dict[str, Any]]:
    duration_days = max(int(duration_days or 1), 1)
    profile = get_destination_profile(destination)

    route = profile.get("route", [destination])
    cleaned_preferences = _clean_preferences(preferences)

    itinerary = []

    for day_range in chunk_days(duration_days, chunk_size=3):
        for day in day_range:
            city = _pick_city(route, day, duration_days)
            available_themes = _available_themes_for_city(profile, city)

            theme_plan = _build_theme_plan(
                day=day,
                preferences=cleaned_preferences,
                available_themes=available_themes,
            )

            anchor_theme = theme_plan["anchor"]
            support_theme = theme_plan["support"]
            evening_theme = theme_plan["evening"]

            anchor_activity = _choose_activity(profile, city, anchor_theme, day)
            support_activity = _choose_activity(profile, city, support_theme, day + 1)
            evening_activity = _choose_activity(profile, city, evening_theme, day + 2)

            if day == 1:
                title = f"Arrival and orientation in {city}"
                morning = f"Arrive in {city}, check in, and settle near the main travel area."
                afternoon = (
                    f"Take a light orientation walk and "
                    f"{_activity_phrase(anchor_activity, 'afternoon')}."
                )
                evening = f"Ease into the trip and {_activity_phrase(evening_activity, 'evening')}."

            elif day == duration_days:
                title = f"Final day in {city}"
                morning = f"Enjoy a relaxed final breakfast and short walk around {city}."
                afternoon = (
                    f"Use the afternoon to {_activity_phrase(anchor_activity, 'afternoon')} "
                    f"or complete last-minute shopping."
                )
                evening = "Transfer to the airport or prepare for departure."

            else:
                title = f"{anchor_theme.title()} and {support_theme.title()} day in {city}"
                morning = f"Start the day with {_activity_phrase(anchor_activity, 'morning')}."
                afternoon = f"Continue with {_activity_phrase(support_activity, 'afternoon')}."
                evening = f"End with {_activity_phrase(evening_activity, 'evening')}."

            itinerary.append(
                {
                    "day": day,
                    "city": city,
                    "theme": anchor_theme,
                    "support_theme": support_theme,
                    "title": title,
                    "morning": morning,
                    "afternoon": afternoon,
                    "evening": evening,
                    "pace": "moderate",
                    "notes": profile.get("pace_notes", ""),
                }
            )

    return itinerary


def itinerary_to_markdown(itinerary: List[Dict[str, Any]]) -> str:
    lines = []

    for item in itinerary:
        lines.append(f"### Day {item['day']}: {item['title']}")
        lines.append(f"- City/Area: {item.get('city', 'Main area')}")
        lines.append(f"- Main Theme: {item.get('theme', 'sightseeing')}")
        lines.append(f"- Support Theme: {item.get('support_theme', 'balanced')}")
        lines.append(f"- Morning: {item['morning']}")
        lines.append(f"- Afternoon: {item['afternoon']}")
        lines.append(f"- Evening: {item['evening']}")
        lines.append(f"- Pace: {item['pace']}")
        lines.append(f"- Notes: {item['notes']}")
        lines.append("")

    return "\n".join(lines).strip()