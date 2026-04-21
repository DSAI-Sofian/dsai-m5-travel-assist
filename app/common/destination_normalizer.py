def normalize_destination_name(name: str) -> str:
    """
    Normalize user-entered destination text into a canonical destination name.
    """
    if not name:
        return ""

    value = name.strip().lower()

    aliases = {
        "kl": "Kuala Lumpur",
        "kuala lumpur": "Kuala Lumpur",
        "bandung": "Bandung",
        "bdg": "Bandung",
        "jakarta": "Jakarta",
        "jkt": "Jakarta",
        "bali": "Bali",
        "denpasar": "Bali",
        "penang": "Penang",
        "pg": "Penang",
        "malacca": "Melaka",
        "melaka": "Melaka",
        "singapore": "Singapore",
        "sg": "Singapore",
        "johor bahru": "Johor Bahru",
        "jb": "Johor Bahru",
        "yogyakarta": "Yogyakarta",
        "jogja": "Yogyakarta",
        "surabaya": "Surabaya",
        "bangkok": "Bangkok",
        "phuket": "Phuket",
        "chiang mai": "Chiang Mai",
        "ho chi minh": "Ho Chi Minh City",
        "hcm": "Ho Chi Minh City",
        "saigon": "Ho Chi Minh City",
        "hanoi": "Hanoi",
    }

    return aliases.get(value, name.strip())


def normalize_destinations(destinations: list[str]) -> list[str]:
    """
    Normalize a list of destinations and remove duplicates while preserving order.
    """
    seen = set()
    normalized = []

    for item in destinations or []:
        clean = normalize_destination_name(item)
        key = clean.lower()
        if key and key not in seen:
            seen.add(key)
            normalized.append(clean)

    return normalized