from typing import Dict, Any


DESTINATION_REGISTRY: Dict[str, Dict[str, Any]] = {
    "vietnam": {
        "display_name": "Vietnam",
        "route": ["Ho Chi Minh City", "Da Nang", "Hoi An", "Hanoi"],
        "arrival_city": "Ho Chi Minh City",
        "departure_city": "Hanoi",
        "pace_notes": "Best planned as a multi-city trip for journeys longer than 7 days.",
        "cities": {
            "Ho Chi Minh City": {
                "culture": [
                    "War Remnants Museum",
                    "Reunification Palace",
                    "Saigon Notre-Dame Cathedral area",
                ],
                "food": [
                    "banh mi tasting",
                    "pho dinner",
                    "Vietnamese coffee stop",
                    "Ben Thanh Market food stalls",
                ],
                "sightseeing": [
                    "Ben Thanh Market",
                    "Nguyen Hue Walking Street",
                    "Saigon Central Post Office",
                ],
                "nature": [
                    "Mekong Delta day trip",
                    "Saigon River evening walk",
                ],
            },
            "Da Nang": {
                "culture": [
                    "Cham Museum",
                    "Linh Ung Pagoda",
                ],
                "food": [
                    "mi quang lunch",
                    "seafood dinner",
                    "Vietnamese coffee stop",
                ],
                "sightseeing": [
                    "Dragon Bridge",
                    "Han River waterfront",
                    "Son Tra Peninsula viewpoint",
                ],
                "nature": [
                    "Marble Mountains",
                    "My Khe Beach",
                    "Ba Na Hills",
                ],
            },
            "Hoi An": {
                "culture": [
                    "Hoi An Ancient Town",
                    "Japanese Covered Bridge",
                    "old merchant house visit",
                ],
                "food": [
                    "cao lau lunch",
                    "white rose dumplings",
                    "Hoi An cooking class",
                ],
                "sightseeing": [
                    "lantern street walk",
                    "Thu Bon River boat ride",
                    "local tailor street",
                ],
                "nature": [
                    "An Bang Beach",
                    "Tra Que Vegetable Village",
                ],
            },
            "Hanoi": {
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
                    "Dong Xuan Market",
                    "Train Street area",
                ],
                "nature": [
                    "West Lake walk",
                    "Ninh Binh day trip",
                    "Ba Vi optional day trip",
                ],
            },
        },
    },

    "indonesia": {
        "display_name": "Indonesia",
        "route": ["Jakarta", "Yogyakarta", "Bali"],
        "arrival_city": "Jakarta",
        "departure_city": "Bali",
        "pace_notes": "Best planned with domestic transfers for trips longer than 8 days.",
        "cities": {
            "Jakarta": {
                "culture": [
                    "Jakarta History Museum",
                    "Istiqlal Mosque area",
                    "National Monument area",
                ],
                "food": [
                    "Jakarta street food stop",
                    "nasi goreng dinner",
                    "local warung lunch",
                ],
                "sightseeing": [
                    "Kota Tua old town",
                    "Grand Indonesia area",
                    "Sunda Kelapa Harbour",
                ],
                "nature": [
                    "Ancol waterfront",
                    "city park walk",
                ],
            },
            "Yogyakarta": {
                "culture": [
                    "Borobudur Temple",
                    "Prambanan Temple",
                    "Yogyakarta palace district",
                ],
                "food": [
                    "gudeg lunch",
                    "Malioboro street snacks",
                    "local warung dinner",
                ],
                "sightseeing": [
                    "Malioboro Street",
                    "Taman Sari Water Castle",
                    "local craft village",
                ],
                "nature": [
                    "Mount Merapi viewpoint",
                    "rice field cycling route",
                ],
            },
            "Bali": {
                "culture": [
                    "Balinese temple visit",
                    "Ubud art market",
                    "traditional craft village",
                ],
                "food": [
                    "Balinese cooking class",
                    "local warung lunch",
                    "satay dinner",
                ],
                "sightseeing": [
                    "Ubud rice terraces",
                    "Uluwatu sunset",
                    "Seminyak beach walk",
                ],
                "nature": [
                    "Bali beach day",
                    "waterfall visit",
                    "rice terrace walk",
                ],
            },
        },
    },

    "hanoi": {
        "display_name": "Hanoi",
        "route": ["Hanoi"],
        "arrival_city": "Hanoi",
        "departure_city": "Hanoi",
        "pace_notes": "Works well as a compact 3–5 day city itinerary.",
        "cities": {
            "Hanoi": {
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
                    "Dong Xuan Market",
                ],
                "nature": [
                    "West Lake walk",
                    "Ba Vi day trip",
                    "Ninh Binh optional day trip",
                ],
            },
        },
    },

    "penang": {
        "display_name": "Penang",
        "route": ["George Town", "Penang Hill", "Batu Ferringhi"],
        "arrival_city": "George Town",
        "departure_city": "George Town",
        "pace_notes": "Best for food, heritage, and compact sightseeing over 3–5 days.",
        "cities": {
            "George Town": {
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
                    "kopitiam breakfast",
                    "hawker centre dinner",
                ],
                "sightseeing": [
                    "Clan Jetties",
                    "Armenian Street",
                    "Cheong Fatt Tze Mansion",
                ],
                "nature": [
                    "Esplanade waterfront walk",
                    "Botanic Gardens",
                ],
            },
            "Penang Hill": {
                "culture": [
                    "Kek Lok Si Temple",
                    "hill heritage viewpoint",
                ],
                "food": [
                    "kopitiam breakfast",
                    "local snack stop",
                    "casual café break",
                ],
                "sightseeing": [
                    "Penang Hill viewpoint",
                    "funicular railway ride",
                    "Ayer Itam local area",
                ],
                "nature": [
                    "Penang Hill nature walk",
                    "The Habitat trail",
                    "Botanic Gardens",
                ],
            },
            "Batu Ferringhi": {
                "culture": [
                    "local craft market",
                    "nearby village walk",
                ],
                "food": [
                    "seafood dinner",
                    "beachside café stop",
                    "hawker-style dinner",
                ],
                "sightseeing": [
                    "Batu Ferringhi beach walk",
                    "night market stroll",
                    "coastal road viewpoint",
                ],
                "nature": [
                    "Batu Ferringhi beach",
                    "Tropical Spice Garden",
                    "coastal sunset walk",
                ],
            },
        },
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
            "pace_notes": "Generic destination profile used.",
            "cities": {
                destination or "Main area": {
                    "culture": ["local heritage site", "museum visit"],
                    "food": ["local food market", "recommended restaurant"],
                    "sightseeing": ["main landmark", "city walk"],
                    "nature": ["park or scenic area"],
                }
            },
        },
    )


def get_city_theme_items(profile: Dict[str, Any], city: str, theme: str) -> list[str]:
    cities = profile.get("cities", {})

    city_profile = cities.get(city)

    if not city_profile:
        return []

    return city_profile.get(theme, [])