from typing import Dict, Any, List


MEAL_METADATA = {
    "pho breakfast": {
        "type": "food",
        "meal_type": "breakfast",
        "best_slots": ["morning"],
        "display": "pho breakfast",
    },
    "pho dinner": {
        "type": "food",
        "meal_type": "dinner",
        "best_slots": ["evening"],
        "display": "pho dinner",
    },
    "bun cha lunch": {
        "type": "food",
        "meal_type": "lunch",
        "best_slots": ["lunch", "afternoon"],
        "display": "bun cha lunch",
    },
    "mi quang lunch": {
        "type": "food",
        "meal_type": "lunch",
        "best_slots": ["lunch", "afternoon"],
        "display": "mi quang lunch",
    },
    "cao lau lunch": {
        "type": "food",
        "meal_type": "lunch",
        "best_slots": ["lunch", "afternoon"],
        "display": "cao lau lunch",
    },
    "seafood dinner": {
        "type": "food",
        "meal_type": "dinner",
        "best_slots": ["evening"],
        "display": "seafood dinner",
    },
    "kopitiam breakfast": {
        "type": "food",
        "meal_type": "breakfast",
        "best_slots": ["morning"],
        "display": "kopitiam breakfast",
    },
    "hawker centre dinner": {
        "type": "food",
        "meal_type": "dinner",
        "best_slots": ["evening"],
        "display": "hawker centre dinner",
    },
    "hawker-style dinner": {
        "type": "food",
        "meal_type": "dinner",
        "best_slots": ["evening"],
        "display": "hawker-style dinner",
    },
    "beachside café stop": {
        "type": "food",
        "meal_type": "snack",
        "best_slots": ["afternoon"],
        "display": "beachside café stop",
    },
    "casual café break": {
        "type": "food",
        "meal_type": "snack",
        "best_slots": ["morning", "afternoon"],
        "display": "casual café break",
    },
    "local snack stop": {
        "type": "food",
        "meal_type": "snack",
        "best_slots": ["afternoon"],
        "display": "local snack stop",
    },
    "egg coffee stop": {
        "type": "food",
        "meal_type": "snack",
        "best_slots": ["morning", "afternoon"],
        "display": "egg coffee stop",
    },
    "vietnamese coffee stop": {
        "type": "food",
        "meal_type": "snack",
        "best_slots": ["morning", "afternoon"],
        "display": "Vietnamese coffee stop",
    },
    "banh mi tasting": {
        "type": "food",
        "meal_type": "snack",
        "best_slots": ["lunch", "afternoon"],
        "display": "banh mi tasting",
    },
    "white rose dumplings": {
        "type": "food",
        "meal_type": "lunch",
        "best_slots": ["lunch", "afternoon", "evening"],
        "display": "white rose dumplings",
    },
    "hoi an cooking class": {
        "type": "food",
        "meal_type": "experience",
        "best_slots": ["afternoon", "evening"],
        "display": "Hoi An cooking class",
    },
    "char kway teow": {
        "type": "food",
        "meal_type": "lunch",
        "best_slots": ["lunch", "afternoon", "evening"],
        "display": "char kway teow",
    },
    "asam laksa": {
        "type": "food",
        "meal_type": "lunch",
        "best_slots": ["lunch", "afternoon"],
        "display": "asam laksa",
    },
    "nasi kandar": {
        "type": "food",
        "meal_type": "lunch",
        "best_slots": ["lunch", "afternoon", "evening"],
        "display": "nasi kandar",
    },
}


FOOD_KEYWORDS = [
    "pho",
    "banh",
    "coffee",
    "café",
    "cafe",
    "food",
    "market food",
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
    "dumplings",
    "cao lau",
    "mi quang",
    "bun cha",
    "snack",
    "cooking class",
]

CULTURE_KEYWORDS = [
    "museum",
    "temple",
    "palace",
    "mansion",
    "mausoleum",
    "pagoda",
    "heritage",
    "monument",
    "mosque",
    "cathedral",
    "bridge",
    "old town",
    "ancient",
    "kongsi",
]

NATURE_KEYWORDS = [
    "beach",
    "hill",
    "garden",
    "lake",
    "river",
    "sunset",
    "trail",
    "waterfall",
    "coastal",
    "waterfront",
    "mountain",
    "fields",
    "terrace",
]


def _normalize(activity: str) -> str:
    return str(activity or "").strip().lower()


def get_activity_metadata(activity: str) -> Dict[str, Any]:
    key = _normalize(activity)

    if key in MEAL_METADATA:
        return {
            "name": activity,
            **MEAL_METADATA[key],
        }

    activity_type = classify_activity(activity)

    if activity_type == "food":
        return {
            "name": activity,
            "type": "food",
            "meal_type": "general",
            "best_slots": ["lunch", "afternoon", "evening"],
            "display": activity,
        }

    if activity_type == "culture":
        return {
            "name": activity,
            "type": "culture",
            "meal_type": None,
            "best_slots": ["morning", "afternoon"],
            "display": activity,
        }

    if activity_type == "nature":
        return {
            "name": activity,
            "type": "nature",
            "meal_type": None,
            "best_slots": ["morning", "afternoon", "evening"],
            "display": activity,
        }

    return {
        "name": activity,
        "type": "sightseeing",
        "meal_type": None,
        "best_slots": ["morning", "afternoon"],
        "display": activity,
    }


def classify_activity(activity: str) -> str:
    text = _normalize(activity)

    if any(keyword in text for keyword in FOOD_KEYWORDS):
        return "food"

    if any(keyword in text for keyword in CULTURE_KEYWORDS):
        return "culture"

    if any(keyword in text for keyword in NATURE_KEYWORDS):
        return "nature"

    return "sightseeing"


def infer_best_times(activity: str) -> List[str]:
    return get_activity_metadata(activity)["best_slots"]


def build_activity_metadata(activity: str) -> Dict[str, Any]:
    return get_activity_metadata(activity)


def is_activity_suitable_for_slot(activity: str, slot: str) -> bool:
    metadata = get_activity_metadata(activity)
    return slot in metadata["best_slots"]


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


def choose_meal_activity(
    activities: List[str],
    meal_slot: str,
    fallback_day: int = 1,
) -> str:
    """
    meal_slot should be:
    - breakfast
    - lunch
    - dinner
    - snack
    """

    if not activities:
        return "local food stop"

    slot_map = {
        "breakfast": "morning",
        "lunch": "lunch",
        "dinner": "evening",
        "snack": "afternoon",
    }

    preferred_slot = slot_map.get(meal_slot, "lunch")

    suitable = [
        activity
        for activity in activities
        if preferred_slot in get_activity_metadata(activity)["best_slots"]
    ]

    pool = suitable if suitable else activities
    index = (fallback_day - 1) % len(pool)

    return pool[index]