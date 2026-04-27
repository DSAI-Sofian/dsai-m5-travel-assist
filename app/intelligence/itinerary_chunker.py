from typing import List, Dict, Any


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


def generate_structured_itinerary(
    destination: str,
    duration_days: int,
    preferences: List[str] | None = None,
) -> List[Dict[str, Any]]:
    preferences = preferences or []
    pref_text = ", ".join(preferences) if preferences else "balanced sightseeing"

    itinerary = []

    for day_range in chunk_days(duration_days, chunk_size=3):
        for day in day_range:
            itinerary.append(
                {
                    "day": day,
                    "title": f"Day {day} in {destination}",
                    "morning": f"Start with a practical {pref_text} activity near your accommodation.",
                    "afternoon": f"Visit a key {destination} attraction with time for meals and transfers.",
                    "evening": f"End with a relaxed local dinner or light walk suitable for Day {day}.",
                    "pace": "moderate",
                    "notes": "Generated through chunk-safe itinerary logic to support long trips.",
                }
            )

    return itinerary


def itinerary_to_markdown(itinerary: List[Dict[str, Any]]) -> str:
    lines = []

    for item in itinerary:
        lines.append(f"### Day {item['day']}: {item['title']}")
        lines.append(f"- Morning: {item['morning']}")
        lines.append(f"- Afternoon: {item['afternoon']}")
        lines.append(f"- Evening: {item['evening']}")
        lines.append(f"- Pace: {item['pace']}")
        lines.append(f"- Notes: {item['notes']}")
        lines.append("")

    return "\n".join(lines).strip()