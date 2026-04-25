import re
from datetime import date, timedelta

from app.common.destination_normalizer import normalize_destinations


KNOWN_DESTINATIONS = [
    "east malaysia",
    "west malaysia",
    "peninsular malaysia",
    "malaysia",
    "indonesia",
    "thailand",
    "vietnam",
    "kuala lumpur",
    "kl",
    "bandung",
    "jakarta",
    "bali",
    "denpasar",
    "penang",
    "pg",
    "malacca",
    "melaka",
    "singapore",
    "sg",
    "johor bahru",
    "jb",
    "yogyakarta",
    "jogja",
    "surabaya",
    "bangkok",
    "phuket",
    "chiang mai",
    "ho chi minh",
    "hcm",
    "saigon",
    "hanoi",
    "sabah",
    "kota kinabalu",
    "kk",
    "sandakan",
    "tawau",
]


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

    cleaned = re.sub(r"\b\d+\s*(day|days|d)\b", " ", cleaned)
    cleaned = re.sub(r"\bbudget\s*(s\$|sgd|\$)?\s*\d+\b", " ", cleaned)
    cleaned = re.sub(r"\bunder\s*(s\$|sgd|\$)?\s*\d+\b", " ", cleaned)
    cleaned = re.sub(r"\bbelow\s*(s\$|sgd|\$)?\s*\d+\b", " ", cleaned)
    cleaned = re.sub(r"\bsgd\s*\d+\b", " ", cleaned)
    cleaned = re.sub(r"\bs\$\s*\d+\b", " ", cleaned)
    cleaned = re.sub(r"\$\s*\d+\b", " ", cleaned)

    for dest in KNOWN_DESTINATIONS:
        cleaned = re.sub(rf"\b{re.escape(dest)}\b", " ", cleaned)

    cleaned = re.sub(r"\b(in|to|for|from|with|and)\b", " ", cleaned)
    cleaned = re.sub(r"[^a-z0-9\s,]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    tokens = [
        token
        for token in cleaned.split()
        if token not in PREFERENCE_NOISE_TOKENS and not token.isdigit()
    ]

    return " ".join(tokens).strip()


def parse_trip_request(text: str) -> dict:
    raw = (text or "").strip()
    lowered = raw.lower()

    parse_scope = _remove_feedback_segment(lowered)

    duration_days = 5
    budget = None
    destinations = []

    duration_match = re.search(r"(\d+)\s*(day|days|d)\b", parse_scope)
    if duration_match:
        try:
            duration_days = int(duration_match.group(1))
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

    found_destinations = []

    for dest in KNOWN_DESTINATIONS:
        if re.search(rf"\b{re.escape(dest)}\b", lowered):
            found_destinations.append(dest)

    if found_destinations:
        destinations = normalize_destinations(found_destinations)

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