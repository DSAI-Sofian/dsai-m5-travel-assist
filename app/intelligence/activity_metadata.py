from typing import Dict, Any, List


FOOD_TIME_RULES = {
    "breakfast": ["morning"],
    "kopitiam": ["morning"],
    "coffee": ["morning", "afternoon"],
    "lunch": ["afternoon"],
    "snack": ["afternoon"],
    "dinner": ["evening"],
    "hawker": ["evening"],
    "night": ["evening"],
    "street food": ["evening"],
    "seafood": ["evening"],
    "market": ["afternoon", "evening"],
    "cooking class": ["afternoon", "evening"],
}


CULTURE_TIME_RULES = {
    "museum": ["morning", "afternoon"],
    "temple": ["morning", "afternoon"],
    "palace": ["morning", "afternoon"],
    "mansion": ["morning", "afternoon"],
    "mausoleum": ["morning", "afternoon"],
    "pagoda": ["morning", "afternoon"],
    "heritage": ["morning", "afternoon"],
}


NATURE_TIME_RULES = {
    "beach": ["afternoon", "evening"],
    "hill": ["morning", "afternoon"],
    "garden": ["morning", "afternoon"],
    "lake": ["morning", "afternoon", "evening"],
    "river": ["afternoon", "evening"],
    "sunset": ["evening"],
    "trail": ["morning", "afternoon"],
    "waterfall": ["morning", "afternoon"],
}


def classify_activity(activity: str) -> str:
    text = str(activity or "").lower()

    food_keywords = list(FOOD_TIME_RULES.keys()) + [
        "pho",
        "banh",
        "laksa",
        "char",
        "nasi",
        "warung",
        "satay",
        "dumplings",
        "cao lau",
        "mi quang",
        "bun cha",
    ]

    culture_keywords = list(CULTURE_TIME_RULES.keys()) + [
        "monument",
        "mosque",
        "cathedral",
        "bridge",
        "old town",
        "ancient",
        "kongsi",
    ]

    nature_keywords = list(NATURE_TIME_RULES.keys()) + [
        "coastal",
        "waterfront",
        "mountain",
        "fields",
        "terrace",
    ]

    if any(keyword in text for keyword in food_keywords):
        return "food"

    if any(keyword in text for keyword in culture_keywords):
        return "culture"

    if any(keyword in text for keyword in nature_keywords):
        return "nature"

    return "sightseeing"


def infer_best_times(activity: str) -> List[str]:
    text = str(activity or "").lower()

    for keyword, times in FOOD_TIME_RULES.items():
        if keyword in text:
            return times

    for keyword, times in CULTURE_TIME_RULES.items():
        if keyword in text:
            return times

    for keyword, times in NATURE_TIME_RULES.items():
        if keyword in text:
            return times

    activity_type = classify_activity(activity)

    if activity_type == "food":
        return ["afternoon", "evening"]

    if activity_type == "culture":
        return ["morning", "afternoon"]

    if activity_type == "nature":
        return ["morning", "afternoon", "evening"]

    return ["morning", "afternoon"]


def build_activity_metadata(activity: str) -> Dict[str, Any]:
    return {
        "name": activity,
        "type": classify_activity(activity),
        "best_times": infer_best_times(activity),
    }


def is_activity_suitable_for_slot(activity: str, slot: str) -> bool:
    metadata = build_activity_metadata(activity)
    return slot in metadata["best_times"]


def choose_slot_suitable_activity(
    activities: List[str],
    preferred_slot: str,
    fallback_day: int = 1,
) -> str:
    if not activities:
        return "local activity"

    suitable = [
        activity
        for activity in activities
        if is_activity_suitable_for_slot(activity, preferred_slot)
    ]

    pool = suitable if suitable else activities
    index = (fallback_day - 1) % len(pool)

    return pool[index]