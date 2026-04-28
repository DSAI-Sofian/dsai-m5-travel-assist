import re
from datetime import date, timedelta

from app.common.destination_normalizer import normalize_destinations


KNOWN_DESTINATIONS = {
    "malaysia": {
        "country": ["malaysia"],
        "regions": [
            "east malaysia",
            "west malaysia",
            "peninsular malaysia",
            "sabah",
            "sarawak",
            "penang",
            "langkawi",
            "genting",
            "genting highlands",
            "cameron highlands",
            "perhentian islands",
            "redang",
            "tioman",
        ],
        "cities": [
            "kuala lumpur",
            "kl",
            "george town",
            "kota kinabalu",
            "kk",
            "kuching",
            "melaka",
            "malacca",
            "johor bahru",
            "jb",
            "ipoh",
            "sandakan",
            "tawau",
            "miri",
            "kuantan",
            "kuala terengganu",
            "alor setar",
        ],
    },
    "singapore": {
        "country": ["singapore", "sg"],
        "regions": [
            "sentosa",
            "marina bay",
            "orchard",
            "chinatown",
            "little india",
        ],
        "cities": [
            "singapore",
        ],
    },
    "thailand": {
        "country": ["thailand"],
        "regions": [
            "phuket",
            "krabi",
            "koh samui",
            "phi phi",
            "koh phi phi",
            "koh tao",
            "koh phangan",
        ],
        "cities": [
            "bangkok",
            "chiang mai",
            "chiang rai",
            "pattaya",
            "hua hin",
            "ayutthaya",
        ],
    },
    "indonesia": {
        "country": ["indonesia"],
        "regions": [
            "bali",
            "lombok",
            "komodo",
            "java",
            "sumatra",
            "raja ampat",
            "gili islands",
        ],
        "cities": [
            "jakarta",
            "bandung",
            "yogyakarta",
            "jogja",
            "surabaya",
            "denpasar",
            "ubud",
            "medan",
            "makassar",
        ],
    },
    "vietnam": {
        "country": ["vietnam"],
        "regions": [
            "halong bay",
            "ha long bay",
            "sapa",
            "mekong delta",
            "phu quoc",
        ],
        "cities": [
            "hanoi",
            "ho chi minh",
            "ho chi minh city",
            "hcm",
            "saigon",
            "da nang",
            "hoi an",
            "hue",
            "nha trang",
            "da lat",
        ],
    },
    "philippines": {
        "country": ["philippines"],
        "regions": [
            "palawan",
            "boracay",
            "cebu",
            "bohol",
            "siargao",
            "coron",
            "el nido",
        ],
        "cities": [
            "manila",
            "cebu city",
            "davao",
            "iloilo",
        ],
    },
    "cambodia": {
        "country": ["cambodia"],
        "regions": [
            "angkor",
            "angkor wat",
        ],
        "cities": [
            "phnom penh",
            "siem reap",
            "sihanoukville",
            "kampot",
        ],
    },
    "laos": {
        "country": ["laos"],
        "regions": [],
        "cities": [
            "vientiane",
            "luang prabang",
            "vang vieng",
            "pakse",
        ],
    },
    "myanmar": {
        "country": ["myanmar", "burma"],
        "regions": [
            "bagan",
            "inle lake",
        ],
        "cities": [
            "yangon",
            "mandalay",
            "naypyidaw",
        ],
    },
    "brunei": {
        "country": ["brunei"],
        "regions": [],
        "cities": [
            "bandar seri begawan",
        ],
    },
}


def _build_all_destinations() -> list[str]:
    destinations = []

    for country_data in KNOWN_DESTINATIONS.values():
        destinations.extend(country_data.get("country", []))
        destinations.extend(country_data.get("regions", []))
        destinations.extend(country_data.get("cities", []))

    # Remove duplicates while preserving order.
    deduped = list(dict.fromkeys(destinations))

    # Match longer names first so "ho chi minh city" is detected before "ho chi minh".
    return sorted(deduped, key=len, reverse=True)


ALL_DESTINATIONS = _build_all_destinations()


PREFERENCE_NOISE_TOKENS = {
    "budget",
    "sgd",
    "s",
    "destination",
    "style",
    "same",
    "previous",
    "before",
    "feedback",
    "cheaper",
    "option",
    "please",
    "more",
    "want",
    "i",
    "than",
    "under",
    "below",
    "trip",
    "travel",
    "days",
    "day",
}


def _infer_dates(duration_days: int) -> tuple[str, str]:
    today = date.today()
    start = today + timedelta(days=14)
    end = start + timedelta(days=max(duration_days, 1))
    return start.isoformat(), end.isoformat()


def _remove_feedback_segment(text: str) -> str:
    return re.split(r"\bfeedback\s*:", text, maxsplit=1)[0].strip()


def _clean_preference_text(text: str) -> str:
    cleaned = text.lower()

    cleaned = _remove_feedback_segment(cleaned)

    # Remove duration expressions
    cleaned = re.sub(r"\b\d+\s*d\s*\d+\s*n\b", " ", cleaned)
    cleaned = re.sub(
        r"\b\d+\s*(day|days)\s*\d+\s*(night|nights)\b",
        " ",
        cleaned,
    )
    cleaned = re.sub(r"\b\d+\s*(day|days|d)\b", " ", cleaned)

    # Remove budget expressions
    cleaned = re.sub(r"\bbudget\s*(s\$|sgd|\$)?\s*\d+\b", " ", cleaned)
    cleaned = re.sub(r"\bunder\s*(s\$|sgd|\$)?\s*\d+\b", " ", cleaned)
    cleaned = re.sub(r"\bbelow\s*(s\$|sgd|\$)?\s*\d+\b", " ", cleaned)
    cleaned = re.sub(r"\bsgd\s*\d+\b", " ", cleaned)
    cleaned = re.sub(r"\bs\$\s*\d+\b", " ", cleaned)
    cleaned = re.sub(r"\$\s*\d+\b", " ", cleaned)

    for dest in ALL_DESTINATIONS:
        cleaned = re.sub(rf"\b{re.escape(dest)}\b", " ", cleaned)

    cleaned = re.sub(r"\b(in|to|for|from|with|and|at|near)\b", " ", cleaned)
    cleaned = re.sub(r"[^a-z0-9\s,]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    tokens = [
        token
        for token in cleaned.split()
        if token not in PREFERENCE_NOISE_TOKENS and not token.isdigit()
    ]

    return " ".join(tokens).strip()


def _extract_destinations(text: str) -> list[str]:
    found_destinations = []

    for dest in ALL_DESTINATIONS:
        if re.search(rf"\b{re.escape(dest)}\b", text):
            found_destinations.append(dest)

    if not found_destinations:
        return []

    return normalize_destinations(found_destinations)


def parse_trip_request(text: str) -> dict:
    raw = (text or "").strip()
    lowered = raw.lower()

    parse_scope = _remove_feedback_segment(lowered)

    duration_days = 5
    budget = None

    duration_patterns = [
        # Examples: 6D5N, 6D 5N, 6 d 5 n
        r"\b(\d+)\s*d\s*(\d+)\s*n\b",

        # Examples: 6 days 5 nights, 6 day 5 night
        r"\b(\d+)\s*(?:day|days)\s*(\d+)\s*(?:night|nights)\b",

        # Examples: 6 days, 6 day, 6d
        r"\b(\d+)\s*(?:day|days|d)\b",
    ]

    for pattern in duration_patterns:
        duration_match = re.search(pattern, parse_scope, flags=re.IGNORECASE)
        if duration_match:
            try:
                duration_days = int(duration_match.group(1))
                break
            except Exception:
                duration_days = 5

    budget_patterns = [
        r"\bbudget\s*(?:s\$|sgd|\$)?\s*(\d+)\b",
        r"\bunder\s*(?:s\$|sgd|\$)?\s*(\d+)\b",
        r"\bbelow\s*(?:s\$|sgd|\$)?\s*(\d+)\b",
        r"\bsgd\s*(\d+)\b",
        r"\bs\$\s*(\d+)\b",
        r"\$\s*(\d+)\b",
    ]

    for pattern in budget_patterns:
        match = re.search(pattern, lowered)
        if match:
            try:
                budget = int(match.group(1))
                break
            except Exception:
                pass

    # Final fallback: detect standalone 3-6 digit amount after removing duration expressions.
    # Example: "4d3n penang 1000 food"
    if budget is None:
        amount_scope = parse_scope

        amount_scope = re.sub(r"\b\d+\s*d\s*\d+\s*n\b", " ", amount_scope)
        amount_scope = re.sub(
            r"\b\d+\s*(day|days)\s*\d+\s*(night|nights)\b",
            " ",
            amount_scope,
        )
        amount_scope = re.sub(r"\b\d+\s*(day|days|d)\b", " ", amount_scope)

        bare_amount_match = re.search(r"\b(\d{3,6})\b", amount_scope)
        if bare_amount_match:
            try:
                budget = int(bare_amount_match.group(1))
            except Exception:
                budget = None

    destinations = _extract_destinations(lowered)

    cleaned_preferences = _clean_preference_text(lowered)

    preferences = []
    if cleaned_preferences:
        parts = re.split(r",|\band\b", cleaned_preferences)
        preferences = [p.strip() for p in parts if p.strip()]

    start_date, end_date = _infer_dates(duration_days)

    return {
        "origin": "Singapore",
        "destinations": destinations,
        "budget": budget,
        "duration_days": duration_days,
        "travelers": 1,
        "preferences": preferences,
        "start_date": start_date,
        "end_date": end_date,
    }


def parse_request(raw_request: str) -> dict:
    return parse_trip_request(raw_request)