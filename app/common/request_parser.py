import re
from datetime import date, timedelta
from app.common.destination_normalizer import normalize_destinations


KNOWN_DESTINATIONS = [
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


def _infer_dates(duration_days: int) -> tuple[str, str]:
    """
    Infer simple travel dates based on today's date.
    Start = 14 days from today
    End = start + duration_days
    """
    today = date.today()
    start = today + timedelta(days=14)
    end = start + timedelta(days=max(duration_days, 1))
    return start.isoformat(), end.isoformat()


def parse_trip_request(text: str) -> dict:
    """
    Parse simple free-text travel requests into structured fields.
    Budget is optional; if not provided, it will be None.

    Examples:
    - '4 days Sabah budget 1500'
    - '3 days KL budget 600 shopping'
    - '5 days Penang under 1200 food and culture'
    - '2 days KL'
    """
    raw = (text or "").strip()
    lowered = raw.lower()

    duration_days = 5
    budget = None
    destinations = []
    preferences = []

    # ---- Duration ----
    duration_match = re.search(r"(\d+)\s*(day|days|d)\b", lowered)
    if duration_match:
        try:
            duration_days = int(duration_match.group(1))
        except Exception:
            duration_days = 5

    # ---- Budget ----
    budget_patterns = [
        r"budget\s*(\d+)",
        r"under\s*(\d+)",
        r"below\s*(\d+)",
        r"sgd\s*(\d+)",
        r"\$(\d+)",
    ]

    for pattern in budget_patterns:
        match = re.search(pattern, lowered)
        if match:
            try:
                budget = int(match.group(1))
                break
            except Exception:
                pass

    # ---- Destination detection ----
    found_destinations = []
    for dest in KNOWN_DESTINATIONS:
        if re.search(rf"\b{re.escape(dest)}\b", lowered):
            found_destinations.append(dest)

    if found_destinations:
        destinations = normalize_destinations(found_destinations)

    # ---- Preferences extraction ----
    cleaned = lowered

    cleaned = re.sub(r"\b\d+\s*(day|days|d)\b", " ", cleaned)
    cleaned = re.sub(r"\bbudget\s*\d+\b", " ", cleaned)
    cleaned = re.sub(r"\bunder\s*\d+\b", " ", cleaned)
    cleaned = re.sub(r"\bbelow\s*\d+\b", " ", cleaned)
    cleaned = re.sub(r"\bsgd\s*\d+\b", " ", cleaned)
    cleaned = re.sub(r"\$\d+\b", " ", cleaned)

    for dest in KNOWN_DESTINATIONS:
        cleaned = re.sub(rf"\b{re.escape(dest)}\b", " ", cleaned)

    cleaned = re.sub(r"\bin\b", " ", cleaned)
    cleaned = re.sub(r"\bto\b", " ", cleaned)
    cleaned = re.sub(r"\bfor\b", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if cleaned:
        parts = re.split(r",| and ", cleaned)
        preferences = [p.strip() for p in parts if p.strip()]

    # Safer fallback: if nothing detected, keep user's raw text as preference
    # but do NOT force Kuala Lumpur
    if not destinations:
        destinations = []

    start_date, end_date = _infer_dates(duration_days)

    return {
        "origin": "Singapore",
        "destinations": destinations,
        "budget": budget,
        "duration_days": duration_days,
        "travelers": 1,
        "preferences": preferences if preferences else [raw],
        "start_date": start_date,
        "end_date": end_date,
    }