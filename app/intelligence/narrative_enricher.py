from typing import Dict, Any, List


def _clean_sentence(text: str) -> str:
    if not text:
        return ""

    cleaned = str(text).strip()

    replacements = {
        "Start the day by enjoy ": "Start the day by enjoying ",
        "Start the day by visit ": "Start the day by visiting ",
        "Start the day by explore ": "Start the day by exploring ",
        "Start the day by try ": "Start the day by trying ",

        "Continue by enjoy ": "Continue by enjoying ",
        "Continue by visit ": "Continue by visiting ",
        "Continue by explore ": "Continue by exploring ",
        "Continue by try ": "Continue by trying ",

        "End by enjoy ": "End by enjoying ",
        "End by visit ": "End by visiting ",
        "End by explore ": "End by exploring ",
        "End by try ": "End by trying ",

        "Start the day by enjoying pho breakfast": "Start the day with pho breakfast",
        "End by enjoying pho breakfast": "End with a light local dinner",
        "End by enjoying kopitiam breakfast": "End with a casual local dinner",
        "End by enjoying mi quang lunch": "End with a casual local dinner",
        "End by enjoying bun cha lunch": "End with a casual local dinner",
        "End by enjoying cao lau lunch": "End with a casual local dinner",

        "End by enjoying Hoi An cooking class": "End with an evening Hoi An cooking experience",
        "Pause for lunch and take a lunch stop for": "Pause for lunch at",
        "Keep lunch simple with take a lunch stop for": "Keep lunch simple with",
        "After arrival, take a lunch stop for": "After arrival, have lunch with",

        "old merchant house visit": "old merchant house",
        "local snack stop": "a local snack stop",
        "or a nearby hawker-style dinner": "or a nearby local dinner",
    }

    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")

    cleaned = cleaned.replace("..", ".")
    cleaned = cleaned.replace(" ,", ",")

    if cleaned and not cleaned.endswith("."):
        cleaned += "."

    return cleaned


def _enrich_title(title: str) -> str:
    if not title:
        return "Daily travel plan"

    title = str(title).strip()

    replacements = {
        "Food and Sightseeing day": "Food and sightseeing day",
        "Culture and Sightseeing day": "Culture and sightseeing day",
        "Culture and Nature day": "Culture and nature day",
        "Culture and Food day": "Culture and food day",
        "Food and Nature day": "Food and nature day",
        "Food and Culture day": "Food and culture day",
    }

    for old, new in replacements.items():
        title = title.replace(old, new)

    return title


def enrich_itinerary_item(item: Dict[str, Any]) -> Dict[str, Any]:
    enriched = dict(item)

    enriched["title"] = _enrich_title(enriched.get("title", "Daily travel plan"))
    enriched["morning"] = _clean_sentence(enriched.get("morning", ""))
    enriched["lunch"] = _clean_sentence(enriched.get("lunch", ""))
    enriched["afternoon"] = _clean_sentence(enriched.get("afternoon", ""))
    enriched["evening"] = _clean_sentence(enriched.get("evening", ""))
    enriched["optional_add_on"] = _clean_sentence(enriched.get("optional_add_on", ""))
    enriched["travel_note"] = _clean_sentence(enriched.get("travel_note", ""))

    return enriched


def enrich_itinerary(itinerary: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not isinstance(itinerary, list):
        return []

    return [
        enrich_itinerary_item(item)
        for item in itinerary
        if isinstance(item, dict)
    ]