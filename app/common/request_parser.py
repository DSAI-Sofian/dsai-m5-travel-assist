import re
from app.common.destination_normalizer import normalize_destinations


KNOWN_DESTINATIONS = [
    "kuala lumpur",
    "kl",
    "bandung",
    "jakarta",
    "bali",
    "penang",
    "malacca",
    "melaka",
    "singapore",
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
]


def parse_trip_request(text: str) -> dict:
    """
    Parse simple free-text travel requests into structured fields.

    Examples:
    - '4 days Bandung budget 1800'
    - '3 days KL budget 600 shopping'
    - '5 days Penang under 1200 food and culture'
    """
    raw = (text or "").strip()
    lowered = raw.lower()

    duration_days = 5
    budget = 1200
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
    # Remove detected structured pieces, keep meaningful remainder
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
        # Split by commas or "and"
        parts = re.split(r",| and ", cleaned)
        preferences = [p.strip() for p in parts if p.strip()]

    # Fallback if no destination found
    if not destinations:
        destinations = ["Kuala Lumpur"]

    return {
        "origin": "Singapore",
        "destinations": destinations,
        "budget": budget,
        "duration_days": duration_days,
        "travelers": 1,
        "preferences": preferences if preferences else [raw],
    }