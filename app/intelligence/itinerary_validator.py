from typing import Dict, Any, List


GENERIC_REPAIR_OPTIONS = {
    "food": [
        "a nearby local food stop",
        "a casual café break",
        "a light local snack",
        "a recommended neighbourhood eatery",
    ],
    "culture": [
        "a nearby heritage walk",
        "a local cultural stop",
        "a short neighbourhood museum visit",
    ],
    "sightseeing": [
        "a nearby viewpoint",
        "a short local walk",
        "a flexible neighbourhood stop",
    ],
    "nature": [
        "a nearby scenic walk",
        "a relaxed park or waterfront stop",
        "a light outdoor break",
    ],
}


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
        "use the afternoon to",
        "or complete last-minute shopping",
        "take a light orientation walk and",
        "ease into the trip and",
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


def _infer_slot_category(slot_name: str, text: str) -> str:
    value = str(text or "").lower()

    if slot_name in ["lunch", "evening"]:
        return "food"

    if any(word in value for word in ["museum", "temple", "palace", "mansion", "heritage", "mausoleum", "pagoda", "cathedral"]):
        return "culture"

    if any(word in value for word in ["beach", "hill", "garden", "lake", "river", "waterfront", "trail", "viewpoint"]):
        return "nature"

    if any(word in value for word in ["food", "lunch", "dinner", "coffee", "café", "cafe", "snack", "laksa", "nasi", "banh", "pho", "dumplings"]):
        return "food"

    return "sightseeing"


def _repair_repeated_slots(day_item: Dict[str, Any]) -> Dict[str, Any]:
    repaired = dict(day_item)

    slot_order = [
        "morning",
        "lunch",
        "afternoon",
        "evening",
        "optional_add_on",
    ]

    seen = {}

    for slot in slot_order:
        text = repaired.get(slot, "")
        signal = _extract_activity_signal(text)

        if not signal:
            continue

        if signal in seen:
            category = _infer_slot_category(slot, text)
            replacement_pool = GENERIC_REPAIR_OPTIONS.get(
                category,
                GENERIC_REPAIR_OPTIONS["sightseeing"],
            )

            replacement = replacement_pool[
                (int(repaired.get("day", 1)) + len(seen)) % len(replacement_pool)
            ]

            if slot == "lunch":
                repaired[slot] = f"Pause for lunch with {replacement}."
            elif slot == "afternoon":
                repaired[slot] = f"Continue with {replacement}."
            elif slot == "evening":
                repaired[slot] = f"End with {replacement}."
            elif slot == "optional_add_on":
                repaired[slot] = f"Optional add-on: include {replacement} if energy and timing allow."
            else:
                repaired[slot] = f"Start the day with {replacement}."

            signal = _extract_activity_signal(repaired[slot])

        seen[signal] = slot

    return repaired


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

    first_validation = validate_itinerary_item(repaired)

    if first_validation.get("warnings"):
        repaired = _repair_repeated_slots(repaired)

        for key in ["morning", "lunch", "afternoon", "evening", "optional_add_on", "travel_note"]:
            repaired[key] = _clean_text(repaired.get(key, ""))

    final_validation = validate_itinerary_item(repaired)

    repaired["validation"] = final_validation

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