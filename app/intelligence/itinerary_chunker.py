from typing import List, Dict, Any
from app.intelligence.destination_registry import get_destination_profile


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


def _pick_theme(day: int, preferences: List[str], available_themes: Dict[str, List[str]]) -> str:
    preferred = [p for p in preferences if p in available_themes]

    if preferred:
        return preferred[(day - 1) % len(preferred)]

    fallback = list(available_themes.keys())

    return fallback[(day - 1) % len(fallback)] if fallback else "sightseeing"


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


def generate_structured_itinerary(
    destination: str,
    duration_days: int,
    preferences: List[str] | None = None,
) -> List[Dict[str, Any]]:
    duration_days = max(int(duration_days or 1), 1)
    profile = get_destination_profile(destination)

    route = profile.get("route", [destination])
    themes = profile.get("themes", {})
    cleaned_preferences = _clean_preferences(preferences)

    itinerary = []

    for day_range in chunk_days(duration_days, chunk_size=3):
        for day in day_range:
            city = _pick_city(route, day, duration_days)
            theme = _pick_theme(day, cleaned_preferences, themes)
            theme_items = themes.get(theme, [])
            main_activity = _pick_item(theme_items, day)

            secondary_theme = "food" if theme != "food" else "culture"
            secondary_items = themes.get(secondary_theme, theme_items)
            secondary_activity = _pick_item(secondary_items, day + 1)

            if day == 1:
                title = f"Arrival and orientation in {city}"
                morning = f"Arrive in {city}, check in, and settle near the main travel area."
                afternoon = f"Take a light orientation walk and visit {main_activity}."
                evening = f"Try {secondary_activity} for an easy first-night experience."
            elif day == duration_days:
                title = f"Final day in {city}"
                morning = f"Enjoy a relaxed final breakfast and short walk around {city}."
                afternoon = f"Use the afternoon for {main_activity} or last-minute shopping."
                evening = "Transfer to the airport or prepare for departure."
            else:
                title = f"{theme.title()} focused day in {city}"
                morning = f"Start with {main_activity}."
                afternoon = f"Continue with a nearby {theme} experience and allow time for transfers."
                evening = f"End the day with {secondary_activity}."

            itinerary.append(
                {
                    "day": day,
                    "city": city,
                    "theme": theme,
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
        lines.append(f"- Theme: {item.get('theme', 'sightseeing')}")
        lines.append(f"- Morning: {item['morning']}")
        lines.append(f"- Afternoon: {item['afternoon']}")
        lines.append(f"- Evening: {item['evening']}")
        lines.append(f"- Pace: {item['pace']}")
        lines.append(f"- Notes: {item['notes']}")
        lines.append("")

    return "\n".join(lines).strip()