def normalize_destination_name(name: str) -> str:
    """
    Normalize user-entered destination text into a canonical destination name.

    This keeps user input flexible while helping downstream agents receive
    consistent destination names.
    """
    if not name:
        return ""

    value = name.strip().lower()

    aliases = {
        # Malaysia
        "malaysia": "Malaysia",
        "east malaysia": "East Malaysia",
        "west malaysia": "West Malaysia",
        "peninsular malaysia": "Peninsular Malaysia",
        "kl": "Kuala Lumpur",
        "kuala lumpur": "Kuala Lumpur",
        "sabah": "Sabah",
        "kota kinabalu": "Kota Kinabalu",
        "kk": "Kota Kinabalu",
        "sandakan": "Sandakan",
        "tawau": "Tawau",
        "sarawak": "Sarawak",
        "kuching": "Kuching",
        "miri": "Miri",
        "penang": "Penang",
        "pg": "Penang",
        "george town": "George Town",
        "langkawi": "Langkawi",
        "genting": "Genting Highlands",
        "genting highlands": "Genting Highlands",
        "cameron highlands": "Cameron Highlands",
        "malacca": "Melaka",
        "melaka": "Melaka",
        "johor bahru": "Johor Bahru",
        "jb": "Johor Bahru",
        "ipoh": "Ipoh",
        "kuantan": "Kuantan",
        "kuala terengganu": "Kuala Terengganu",
        "alor setar": "Alor Setar",
        "perhentian islands": "Perhentian Islands",
        "redang": "Redang",
        "tioman": "Tioman",

        # Singapore
        "singapore": "Singapore",
        "sg": "Singapore",
        "sentosa": "Sentosa",
        "marina bay": "Marina Bay",
        "orchard": "Orchard",
        "chinatown": "Chinatown",
        "little india": "Little India",

        # Thailand
        "thailand": "Thailand",
        "bangkok": "Bangkok",
        "phuket": "Phuket",
        "krabi": "Krabi",
        "koh samui": "Koh Samui",
        "phi phi": "Phi Phi Islands",
        "koh phi phi": "Phi Phi Islands",
        "koh tao": "Koh Tao",
        "koh phangan": "Koh Phangan",
        "chiang mai": "Chiang Mai",
        "chiang rai": "Chiang Rai",
        "pattaya": "Pattaya",
        "hua hin": "Hua Hin",
        "ayutthaya": "Ayutthaya",

        # Indonesia
        "indonesia": "Indonesia",
        "bali": "Bali",
        "denpasar": "Bali",
        "ubud": "Ubud",
        "lombok": "Lombok",
        "komodo": "Komodo",
        "java": "Java",
        "sumatra": "Sumatra",
        "raja ampat": "Raja Ampat",
        "gili islands": "Gili Islands",
        "jakarta": "Jakarta",
        "jkt": "Jakarta",
        "bandung": "Bandung",
        "bdg": "Bandung",
        "yogyakarta": "Yogyakarta",
        "jogja": "Yogyakarta",
        "surabaya": "Surabaya",
        "medan": "Medan",
        "makassar": "Makassar",

        # Vietnam
        "vietnam": "Vietnam",
        "hanoi": "Hanoi",
        "ho chi minh": "Ho Chi Minh City",
        "ho chi minh city": "Ho Chi Minh City",
        "hcm": "Ho Chi Minh City",
        "saigon": "Ho Chi Minh City",
        "da nang": "Da Nang",
        "hoi an": "Hoi An",
        "hue": "Hue",
        "nha trang": "Nha Trang",
        "da lat": "Da Lat",
        "halong bay": "Ha Long Bay",
        "ha long bay": "Ha Long Bay",
        "sapa": "Sapa",
        "mekong delta": "Mekong Delta",
        "phu quoc": "Phu Quoc",

        # Philippines
        "philippines": "Philippines",
        "manila": "Manila",
        "cebu": "Cebu",
        "cebu city": "Cebu City",
        "palawan": "Palawan",
        "boracay": "Boracay",
        "bohol": "Bohol",
        "siargao": "Siargao",
        "coron": "Coron",
        "el nido": "El Nido",
        "davao": "Davao",
        "iloilo": "Iloilo",

        # Cambodia
        "cambodia": "Cambodia",
        "phnom penh": "Phnom Penh",
        "siem reap": "Siem Reap",
        "angkor": "Angkor",
        "angkor wat": "Angkor Wat",
        "sihanoukville": "Sihanoukville",
        "kampot": "Kampot",

        # Laos
        "laos": "Laos",
        "vientiane": "Vientiane",
        "luang prabang": "Luang Prabang",
        "vang vieng": "Vang Vieng",
        "pakse": "Pakse",

        # Myanmar
        "myanmar": "Myanmar",
        "burma": "Myanmar",
        "yangon": "Yangon",
        "mandalay": "Mandalay",
        "naypyidaw": "Naypyidaw",
        "bagan": "Bagan",
        "inle lake": "Inle Lake",

        # Brunei
        "brunei": "Brunei",
        "bandar seri begawan": "Bandar Seri Begawan",
    }

    return aliases.get(value, name.strip().title())


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