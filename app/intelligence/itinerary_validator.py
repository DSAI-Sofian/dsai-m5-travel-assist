from typing import Dict, Any, List


def _clean_text(text: str) -> str:
    if not text:
        return ""

    cleaned = str(text).strip()

    replacements = {
        "visiting casual café break": "enjoying a casual café break",
        "visiting casual cafe break": "enjoying a casual cafe break",
        "visit casual café break": "enjoy a casual café break",
        "visit casual cafe break": "enjoy a casual cafe break",
        "visiting local snack stop": "enjoying a local snack stop",
        "visit local snack stop": "enjoy a local snack stop",
        "visiting a local snack stop": "enjoying a local snack stop",

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
        "Start the day by visit": "Start the day by visiting",
        "Continue with a light visit to": "Continue with a light visit to",
        "old merchant house visit": "old merchant house",
    }

    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

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
        "end by",
        "end with",
        "pause for lunch and",
        "take a lunch stop for",
        "after arrival,",
        "have lunch with",
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

    evening = str(day_item.get("evening", "")).lower()

    bad_evening_terms = [
        "breakfast",
        " lunch",
        "museum",
        "mausoleum",
    ]

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