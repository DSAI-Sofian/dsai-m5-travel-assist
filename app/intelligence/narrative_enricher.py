from typing import Dict, Any, List


def _clean_sentence(text: str) -> str:
    if not text:
        return ""

    cleaned = str(text).strip()

    replacements = {
        "Continue with visit ": "Continue by visiting ",
        "Continue with explore ": "Continue by exploring ",
        "Continue with try ": "Continue by trying ",
        "Continue with enjoy ": "Continue by enjoying ",
        "Continue with take ": "Continue by taking ",
        "End with end with ": "End with ",
        "End with enjoy ": "End by enjoying ",
        "End with take ": "End by taking ",
        "Start the day with enjoy ": "Start the day by enjoying ",
        "Start the day with visit ": "Start the day by visiting ",
        "Start the day with explore ": "Start the day by exploring ",
        "Start the day with try ": "Start the day by trying ",
        "Start the day and start with ": "Start the day with ",
        "Start the day and visit ": "Start the day by visiting ",
        "Start the day and explore ": "Start the day by exploring ",
        "Start the day and try ": "Start the day by trying ",
        "Use the afternoon to try ": "Use the afternoon to enjoy ",
        "Use the afternoon to visit ": "Use the afternoon to visit ",
        "Use the afternoon to enjoy enjoy ": "Use the afternoon to enjoy ",
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
    enriched["afternoon"] = _clean_sentence(enriched.get("afternoon", ""))
    enriched["evening"] = _clean_sentence(enriched.get("evening", ""))

    return enriched


def enrich_itinerary(itinerary: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not isinstance(itinerary, list):
        return []

    return [
        enrich_itinerary_item(item)
        for item in itinerary
        if isinstance(item, dict)
    ]