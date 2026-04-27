from typing import Dict, Any, List


def _clean_text(text: str) -> str:
    if not text:
        return ""

    cleaned = str(text).strip()

    replacements = {
        "visitinging": "visiting",
        "Start the day by visitinging": "Start the day by visiting",
        "Start the day by enjoying pho breakfast": "Start the day with pho breakfast",

        "End by enjoying Hoi An cooking class": "End with an evening Hoi An cooking experience",

        "Pause for lunch with pho breakfast": "Pause for lunch with bun cha lunch",
        "Pause for lunch with pho dinner": "Pause for lunch with banh mi tasting",
        "Pause for lunch with seafood dinner": "Pause for lunch with mi quang lunch",
        "Pause for lunch with coffee stop": "Pause for lunch with a local food stop",

        "After settling in, have pho dinner": "After settling in, have banh mi tasting",
        "After arrival, have seafood dinner": "After arrival, have mi quang lunch",
        "After arrival, have egg coffee stop": "After arrival, have bun cha lunch",
        "After arrival, have cao lau lunch": "After arrival, have cao lau lunch",

        "Keep lunch simple with pho breakfast": "Keep lunch simple with bun cha lunch",
        "Keep lunch simple with seafood dinner": "Keep lunch simple with mi quang lunch",

        "Continue with a light visit to bun cha lunch": "Continue with a light local food stop for bun cha",
        "Keep lunch simple with explore beachside café stop": "Keep lunch simple with a beachside café stop",

        "old merchant house visit": "old merchant house",
    }

    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    cleaned = cleaned.replace("visitinging", "visiting")

    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")

    if cleaned and not cleaned.endswith("."):
        cleaned += "."

    return cleaned


def _extract_activity_signal(text: str) -> str:
    value = str(text or "").lower()

    stopwords = [
        "start the day by",
        "start the day with",
        "continue by",
        "continue with a light visit to",
        "continue with a light local food stop for",
        "end by",
        "end with",
        "pause for lunch with",
        "after settling in, have",
        "after arrival, have",
        "keep lunch simple with",
        "enjoying",
        "enjoy",
        "visiting",
        "visit",
        "trying",
        "try",
        "exploring",
        "explore",
        "optional add-on: include",
        "optional add-on: keep",
        "only if arrival timing allows",
        "if energy and timing allow",
        "as a flexible nearby stop",
        ".",
    ]

    for word in stopwords:
        value = value.replace(word, "")

    return value.strip()


def _detect_repetition(day_item: Dict[str, Any]) -> List[str]:
    warnings = []

    slots = [
        day_item.get("morning", ""),
        day_item.get("lunch", ""),
        day_item.get("afternoon", ""),
        day_item.get("evening", ""),
        day_item.get("optional_add_on", ""),
    ]

    signals = [
        _extract_activity_signal(slot)
        for slot in slots
        if _extract_activity_signal(slot)
    ]

    seen = set()

    for signal in signals:
        if signal in seen:
            warnings.append(f"Repeated activity detected: {signal}")
        seen.add(signal)

    return warnings


def _detect_timing_issues(day_item: Dict[str, Any]) -> List[str]:
    warnings = []

    lunch = str(day_item.get("lunch", "")).lower()
    evening = str(day_item.get("evening", "")).lower()

    bad_lunch_terms = [
        "breakfast",
        "dinner",
    ]

    bad_evening_terms = [
        "breakfast",
        " lunch",
        "museum",
        "mausoleum",
    ]

    for term in bad_lunch_terms:
        if term in lunch:
            warnings.append(f"Possible timing issue in lunch slot: {term.strip()}")

    for term in bad_evening_terms:
        if term in evening:
            warnings.append(f"Possible timing issue in evening slot: {term.strip()}")

    return warnings


def _detect_density_issues(day_item: Dict[str, Any]) -> List[str]:
    warnings = []

    filled_slots = 0

    for key in ["morning", "lunch", "afternoon", "evening", "optional_add_on"]:
        if day_item.get(key):
            filled_slots += 1

    if filled_slots < 4:
        warnings.append("Light schedule detected")

    return warnings


def validate_itinerary_item(day_item: Dict[str, Any]) -> Dict[str, Any]:
    warnings = []
    warnings.extend(_detect_repetition(day_item))
    warnings.extend(_detect_timing_issues(day_item))
    warnings.extend(_detect_density_issues(day_item))

    return {
        "day": day_item.get("day"),
        "city": day_item.get("city"),
        "warnings": warnings,
        "status": "needs_review" if warnings else "ok",
    }


def repair_itinerary_item(day_item: Dict[str, Any]) -> Dict[str, Any]:
    repaired = dict(day_item)

    for key in ["morning", "lunch", "afternoon", "evening", "optional_add_on", "travel_note"]:
        repaired[key] = _clean_text(repaired.get(key, ""))

    validation = validate_itinerary_item(repaired)

    repaired["validation"] = validation

    return repaired


def repair_and_validate_itinerary(itinerary: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(itinerary, list):
        return {
            "itinerary": [],
            "validation_summary": {
                "status": "invalid",
                "warnings": ["Itinerary was not a list"],
                "warning_count": 1,
            },
        }

    repaired_items = []
    all_warnings = []

    for item in itinerary:
        if not isinstance(item, dict):
            continue

        repaired = repair_itinerary_item(item)
        repaired_items.append(repaired)

        validation = repaired.get("validation", {})
        for warning in validation.get("warnings", []):
            all_warnings.append(
                {
                    "day": repaired.get("day"),
                    "city": repaired.get("city"),
                    "warning": warning,
                }
            )

    return {
        "itinerary": repaired_items,
        "validation_summary": {
            "status": "needs_review" if all_warnings else "ok",
            "warnings": all_warnings,
            "warning_count": len(all_warnings),
        },
    }