from typing import List, Dict, Any, Set
from app.intelligence.destination_registry import (
    get_destination_profile,
    get_city_theme_items,
)
from app.intelligence.activity_metadata import (
    classify_activity,
    choose_slot_suitable_activity,
    choose_meal_activity,
)


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


def _activity_phrase(activity: str, slot: str) -> str:
    activity_type = classify_activity(activity)

    if activity_type == "food":
        if slot == "morning":
            return f"enjoy {activity}"
        if slot == "lunch":
            return f"have {activity}"
        if slot == "afternoon":
            return f"try {activity}"
        return f"enjoy {activity}"

    if activity_type == "culture":
        if slot == "evening":
            return f"walk around the {activity} area"
        return f"visit {activity}"

    if activity_type == "nature":
        return f"explore {activity}"

    return f"visit {activity}"


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

    return {
        "anchor": anchor_theme,
        "support": support_theme,
    }


def _mark_used(activity: str, used_recent: Set[str], used_global: Set[str]) -> None:
    used_recent.add(activity.lower())
    used_global.add(activity.lower())

    if len(used_recent) > 8:
        used_recent.pop()


def _choose_diverse_activity(
    profile: Dict[str, Any],
    city: str,
    theme: str,
    slot: str,
    day: int,
    used_recent: Set[str],
    used_global: Set[str],
) -> str:
    city_items = get_city_theme_items(profile, city, theme)

    if not city_items:
        return "local activity"

    candidates = [
        item for item in city_items
        if item.lower() not in used_recent
        and item.lower() not in used_global
    ]

    if not candidates:
        candidates = [
            item for item in city_items
            if item.lower() not in used_recent
        ]

    pool = candidates if candidates else city_items

    chosen = choose_slot_suitable_activity(
        activities=pool,
        preferred_slot=slot,
        fallback_day=day,
    )

    _mark_used(chosen, used_recent, used_global)
    return chosen


def _choose_food_activity(
    profile: Dict[str, Any],
    city: str,
    meal_slot: str,
    day: int,
    used_recent: Set[str],
    used_global: Set[str],
) -> str:
    food_items = get_city_theme_items(profile, city, "food")

    if not food_items:
        return "local food stop"

    candidates = [
        item for item in food_items
        if item.lower() not in used_recent
        and item.lower() not in used_global
    ]

    if not candidates:
        candidates = [
            item for item in food_items
            if item.lower() not in used_recent
        ]

    pool = candidates if candidates else food_items

    chosen = choose_meal_activity(
        activities=pool,
        meal_slot=meal_slot,
        fallback_day=day,
    )

    _mark_used(chosen, used_recent, used_global)
    return chosen


def _build_travel_note(
    day: int,
    city: str,
    previous_city: str | None,
) -> str:
    if previous_city and previous_city != city:
        return f"Travel transition: move from {previous_city} to {city}; keep this day slightly flexible."

    if day == 1:
        return "Travel note: keep the first day light for arrival, check-in, and orientation."

    return "Travel note: group nearby stops together to reduce transfer time."


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
    used_global: Set[str] = set()
    used_recent: Set[str] = set()
    previous_city = None

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

            morning_activity = _choose_diverse_activity(
                profile=profile,
                city=city,
                theme=anchor_theme,
                slot="morning",
                day=day,
                used_recent=used_recent,
                used_global=used_global,
            )

            lunch_activity = _choose_food_activity(
                profile=profile,
                city=city,
                meal_slot="lunch",
                day=day + 1,
                used_recent=used_recent,
                used_global=used_global,
            )

            afternoon_activity = _choose_diverse_activity(
                profile=profile,
                city=city,
                theme=support_theme,
                slot="afternoon",
                day=day + 2,
                used_recent=used_recent,
                used_global=used_global,
            )

            evening_activity = _choose_food_activity(
                profile=profile,
                city=city,
                meal_slot="dinner",
                day=day + 3,
                used_recent=used_recent,
                used_global=used_global,
            )

            optional_activity = _choose_diverse_activity(
                profile=profile,
                city=city,
                theme="sightseeing" if "sightseeing" in available_themes else support_theme,
                slot="afternoon",
                day=day + 4,
                used_recent=used_recent,
                used_global=used_global,
            )

            travel_note = _build_travel_note(
                day=day,
                city=city,
                previous_city=previous_city,
            )

            is_transition_day = previous_city and previous_city != city

            if day == 1:
                title = f"Arrival and orientation in {city}"
                morning = f"Arrive in {city}, check in, and settle near the main travel area."
                lunch = f"After settling in, have {lunch_activity}."
                afternoon = (
                    f"Take a light orientation walk and "
                    f"{_activity_phrase(afternoon_activity, 'afternoon')}."
                )
                evening = f"Ease into the trip and {_activity_phrase(evening_activity, 'evening')}."
                optional = f"Optional add-on: keep {optional_activity} as a flexible nearby stop."

            elif day == duration_days:
                title = f"Final day in {city}"
                morning = f"Enjoy a relaxed final breakfast and short walk around {city}."
                lunch = f"Keep lunch simple with {lunch_activity}."
                afternoon = (
                    f"Use the afternoon to {_activity_phrase(afternoon_activity, 'afternoon')} "
                    f"or complete last-minute shopping."
                )
                evening = "Transfer to the airport or prepare for departure."
                optional = "Optional add-on: keep the schedule light to avoid departure-day stress."

            elif is_transition_day:
                title = f"Travel transition and light exploration in {city}"
                morning = f"Transfer from {previous_city} to {city} and check in."
                lunch = f"After arrival, have {lunch_activity}."
                afternoon = f"Continue with a light visit to {afternoon_activity}."
                evening = f"End by {_activity_phrase(evening_activity, 'evening')}."
                optional = f"Optional add-on: include {optional_activity} only if arrival timing allows."

            else:
                title = f"{anchor_theme.title()} and {support_theme.title()} day in {city}"
                morning = f"Start the day by {_activity_phrase(morning_activity, 'morning')}."
                lunch = f"Pause for lunch with {lunch_activity}."
                afternoon = f"Continue by {_activity_phrase(afternoon_activity, 'afternoon')}."
                evening = f"End by {_activity_phrase(evening_activity, 'evening')}."
                optional = f"Optional add-on: include {optional_activity} if energy and timing allow."

            itinerary.append(
                {
                    "day": day,
                    "city": city,
                    "theme": anchor_theme,
                    "support_theme": support_theme,
                    "title": title,
                    "morning": morning,
                    "lunch": lunch,
                    "afternoon": afternoon,
                    "evening": evening,
                    "optional_add_on": optional,
                    "travel_note": travel_note,
                    "pace": "moderate",
                    "notes": profile.get("pace_notes", ""),
                }
            )

            previous_city = city

    return itinerary


def itinerary_to_markdown(itinerary: List[Dict[str, Any]]) -> str:
    lines = []

    for item in itinerary:
        lines.append(f"### Day {item['day']}: {item['title']}")
        lines.append(f"- City/Area: {item.get('city', 'Main area')}")
        lines.append(f"- Main Theme: {item.get('theme', 'sightseeing')}")
        lines.append(f"- Support Theme: {item.get('support_theme', 'balanced')}")
        lines.append(f"- Morning: {item['morning']}")
        lines.append(f"- Lunch: {item.get('lunch', 'Flexible lunch stop')}")
        lines.append(f"- Afternoon: {item['afternoon']}")
        lines.append(f"- Evening: {item['evening']}")
        lines.append(f"- Optional: {item.get('optional_add_on', 'None')}")
        lines.append(f"- Travel Note: {item.get('travel_note', 'Group nearby stops together.')}")
        lines.append(f"- Pace: {item['pace']}")
        lines.append(f"- Notes: {item['notes']}")
        lines.append("")

    return "\n".join(lines).strip()