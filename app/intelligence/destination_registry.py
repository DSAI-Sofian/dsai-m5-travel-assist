from typing import Dict, Any


DESTINATION_REGISTRY: Dict[str, Dict[str, Any]] = {
    "vietnam": {
        "display_name": "Vietnam",
        "route": ["Ho Chi Minh City", "Da Nang", "Hoi An", "Hanoi"],
        "arrival_city": "Ho Chi Minh City",
        "departure_city": "Hanoi",
        "themes": {
            "culture": [
                "War Remnants Museum",
                "Reunification Palace",
                "Temple of Literature",
                "Old Quarter heritage walk",
                "Hoi An Ancient Town",
            ],
            "food": [
                "pho breakfast",
                "banh mi tasting",
                "Vietnamese coffee stop",
                "street food night market",
                "local cooking class",
            ],
            "sightseeing": [
                "Saigon Notre-Dame Cathedral",
                "Ben Thanh Market",
                "Dragon Bridge",
                "Hoan Kiem Lake",
                "Mekong Delta day trip",
            ],
            "nature": [
                "Mekong Delta canals",
                "Ba Na Hills",
                "Marble Mountains",
                "West Lake walk",
                "coastal Da Nang break",
            ],
        },
        "pace_notes": "Best planned as a multi-city trip for journeys longer than 7 days.",
    },
    "indonesia": {
        "display_name": "Indonesia",
        "route": ["Jakarta", "Yogyakarta", "Bali"],
        "arrival_city": "Jakarta",
        "departure_city": "Bali",
        "themes": {
            "culture": [
                "Borobudur Temple",
                "Prambanan Temple",
                "Yogyakarta palace district",
                "Balinese temple visit",
                "traditional craft village",
            ],
            "food": [
                "nasi goreng breakfast",
                "satay dinner",
                "local warung lunch",
                "Balinese cooking class",
                "Jakarta street food stop",
            ],
            "sightseeing": [
                "Jakarta old town",
                "Malioboro Street",
                "Ubud rice terraces",
                "Uluwatu sunset",
                "Seminyak beach walk",
            ],
            "nature": [
                "Mount Merapi viewpoint",
                "Ubud rice fields",
                "Bali beach day",
                "waterfall visit",
                "coastal sunset stop",
            ],
        },
        "pace_notes": "Best planned with domestic transfers for trips longer than 8 days.",
    },
    "hanoi": {
        "display_name": "Hanoi",
        "route": ["Hanoi"],
        "arrival_city": "Hanoi",
        "departure_city": "Hanoi",
        "themes": {
            "culture": [
                "Temple of Literature",
                "Ho Chi Minh Mausoleum area",
                "Vietnam Museum of Ethnology",
                "Old Quarter heritage walk",
            ],
            "food": [
                "pho breakfast",
                "egg coffee stop",
                "bun cha lunch",
                "Old Quarter street food walk",
            ],
            "sightseeing": [
                "Hoan Kiem Lake",
                "Train Street area",
                "West Lake",
                "Dong Xuan Market",
            ],
            "nature": [
                "West Lake walk",
                "Ba Vi day trip",
                "Ninh Binh optional day trip",
            ],
        },
        "pace_notes": "Works well as a compact 3–5 day city itinerary.",
    },
    "penang": {
        "display_name": "Penang",
        "route": ["George Town", "Penang Hill", "Batu Ferringhi"],
        "arrival_city": "George Town",
        "departure_city": "George Town",
        "themes": {
            "culture": [
                "George Town heritage walk",
                "Khoo Kongsi",
                "Pinang Peranakan Mansion",
                "street art trail",
            ],
            "food": [
                "char kway teow",
                "asam laksa",
                "nasi kandar",
                "hawker centre dinner",
                "kopitiam breakfast",
            ],
            "sightseeing": [
                "Penang Hill",
                "Kek Lok Si Temple",
                "Clan Jetties",
                "Armenian Street",
            ],
            "nature": [
                "Penang Hill nature walk",
                "Botanic Gardens",
                "Batu Ferringhi beach",
            ],
        },
        "pace_notes": "Best for food, heritage, and compact sightseeing over 3–5 days.",
    },
}


def normalize_destination_name(destination: str) -> str:
    if not destination:
        return "default"

    value = destination.strip().lower()

    if "vietnam" in value:
        return "vietnam"
    if "indonesia" in value:
        return "indonesia"
    if "hanoi" in value:
        return "hanoi"
    if "penang" in value:
        return "penang"

    return value


def get_destination_profile(destination: str) -> Dict[str, Any]:
    key = normalize_destination_name(destination)

    return DESTINATION_REGISTRY.get(
        key,
        {
            "display_name": destination or "Requested destination",
            "route": [destination or "Main area"],
            "arrival_city": destination or "Main area",
            "departure_city": destination or "Main area",
            "themes": {
                "culture": ["local heritage site", "museum visit"],
                "food": ["local food market", "recommended restaurant"],
                "sightseeing": ["main landmark", "city walk"],
                "nature": ["park or scenic area"],
            },
            "pace_notes": "Generic destination profile used.",
        },
    )