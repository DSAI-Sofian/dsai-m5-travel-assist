import json
from app.common.openai_client import get_openai_client, MODEL


def build_itinerary(req: dict, plan: dict):
    client = get_openai_client()

    messages = [
        {
            "role": "system",
            "content": (
                "You are a travel executor for a Southeast Asia travel planner app. "
                "Return ONLY valid JSON. "
                "Do not include markdown, explanation outside JSON, or code fences."
            ),
        },
        {
            "role": "user",
            "content": f"""
Execute the travel plan and return STRICT JSON in exactly this structure:

{{
  "daily_itinerary": [
    {{
      "day": 1,
      "title": "Arrival and shopping",
      "details": "Short description of the day's plan"
    }}
  ],
  "travel_details": {{
    "flight": {{
      "suggestion": "Airline + route",
      "estimated_price": "SGD value",
      "search_link": "Google Flights search URL"
    }},
    "hotel": {{
      "name": "Hotel name",
      "estimated_price": "SGD value per night",
      "booking_link": "Booking.com search URL",
      "location_note": "Approximate distance or travel time to main area"
    }},
    "transport": {{
      "mode": "Grab / taxi / train / bus",
      "estimated_cost": "SGD value",
      "notes": "Typical travel time or guidance"
    }}
  }},
  "nearby_attractions": [
    {{
      "name": "Attraction name",
      "google_maps_link": "Google Maps search URL",
      "distance_note": "Approximate time from hotel"
    }}
  ],
  "restaurants": [
    {{
      "name": "Restaurant name",
      "google_maps_link": "Google Maps search URL",
      "distance_note": "Approximate time from hotel"
    }}
  ],
  "cost_breakdown": {{
    "flight": "SGD 350",
    "hotel": "SGD 420",
    "activities": "SGD 180",
    "local_transport": "SGD 90",
    "food": "SGD 120",
    "total": "SGD 1160"
  }},
  "best_fit_days": 5
}}

Rules:
- Return ONLY JSON
- Always include currency for all costs
- Prefer SGD where possible
- If using another currency, clearly label it and include approximate SGD conversion if helpful
- Use realistic travel suggestions and realistic price estimates
- Flight links must be Google Flights search URLs
- Hotel links must be Booking.com search URLs
- nearby_attractions must contain 2 to 3 useful attractions close to the suggested hotel
- restaurants must contain 2 to 3 useful food places close to the suggested hotel
- Each nearby attraction and restaurant must include:
  name, google_maps_link, distance_note
- distance_note must describe approximate travel time from the suggested hotel
  for example: "8 min drive from hotel" or "12 min walk from hotel"
- cost_breakdown must always include:
  flight, hotel, activities, local_transport, food, total
- daily_itinerary must be a list
- nearby_attractions must be a list
- restaurants must be a list
- best_fit_days must be a number

User request:
{req}

Planner output:
{plan}
""",
        },
    ]

    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0,
    )

    content = resp.choices[0].message.content

    try:
        data = json.loads(content)
    except Exception:
        data = {
            "daily_itinerary": [],
            "travel_details": {
                "flight": {
                    "suggestion": "No flight suggestion returned",
                    "estimated_price": "SGD 0",
                    "search_link": "",
                },
                "hotel": {
                    "name": "No hotel suggestion returned",
                    "estimated_price": "SGD 0",
                    "booking_link": "",
                    "location_note": "No location note returned",
                },
                "transport": {
                    "mode": "No transport suggestion returned",
                    "estimated_cost": "SGD 0",
                    "notes": "No transport notes returned",
                },
            },
            "nearby_attractions": [],
            "restaurants": [],
            "cost_breakdown": {
                "flight": "SGD 0",
                "hotel": "SGD 0",
                "activities": "SGD 0",
                "local_transport": "SGD 0",
                "food": "SGD 0",
                "total": "SGD 0",
            },
            "best_fit_days": req.get("duration_days", 0),
            "raw_output": content,
        }

    if not isinstance(data.get("daily_itinerary"), list):
        data["daily_itinerary"] = []

    if not isinstance(data.get("travel_details"), dict):
        data["travel_details"] = {}

    if not isinstance(data.get("nearby_attractions"), list):
        data["nearby_attractions"] = []

    if not isinstance(data.get("restaurants"), list):
        data["restaurants"] = []

    if not isinstance(data.get("cost_breakdown"), dict):
        data["cost_breakdown"] = {}

    travel_details = data["travel_details"]

    flight = travel_details.get("flight", {})
    if not isinstance(flight, dict):
        flight = {}

    hotel = travel_details.get("hotel", {})
    if not isinstance(hotel, dict):
        hotel = {}

    transport = travel_details.get("transport", {})
    if not isinstance(transport, dict):
        transport = {}

    data["travel_details"] = {
        "flight": {
            "suggestion": str(flight.get("suggestion", "No flight suggestion returned")),
            "estimated_price": str(flight.get("estimated_price", "SGD 0")),
            "search_link": str(flight.get("search_link", "")),
        },
        "hotel": {
            "name": str(hotel.get("name", "No hotel suggestion returned")),
            "estimated_price": str(hotel.get("estimated_price", "SGD 0")),
            "booking_link": str(hotel.get("booking_link", "")),
            "location_note": str(hotel.get("location_note", "No location note returned")),
        },
        "transport": {
            "mode": str(transport.get("mode", "No transport suggestion returned")),
            "estimated_cost": str(transport.get("estimated_cost", "SGD 0")),
            "notes": str(transport.get("notes", "No transport notes returned")),
        },
    }

    cleaned_attractions = []
    for item in data["nearby_attractions"][:3]:
        if isinstance(item, dict):
            cleaned_attractions.append(
                {
                    "name": str(item.get("name", "Unnamed attraction")),
                    "google_maps_link": str(item.get("google_maps_link", "")),
                    "distance_note": str(item.get("distance_note", "Distance not provided")),
                }
            )
        else:
            cleaned_attractions.append(
                {
                    "name": str(item),
                    "google_maps_link": "",
                    "distance_note": "Distance not provided",
                }
            )
    data["nearby_attractions"] = cleaned_attractions

    cleaned_restaurants = []
    for item in data["restaurants"][:3]:
        if isinstance(item, dict):
            cleaned_restaurants.append(
                {
                    "name": str(item.get("name", "Unnamed restaurant")),
                    "google_maps_link": str(item.get("google_maps_link", "")),
                    "distance_note": str(item.get("distance_note", "Distance not provided")),
                }
            )
        else:
            cleaned_restaurants.append(
                {
                    "name": str(item),
                    "google_maps_link": "",
                    "distance_note": "Distance not provided",
                }
            )
    data["restaurants"] = cleaned_restaurants

    cost_breakdown = data["cost_breakdown"]
    data["cost_breakdown"] = {
        "flight": str(cost_breakdown.get("flight", "SGD 0")),
        "hotel": str(cost_breakdown.get("hotel", "SGD 0")),
        "activities": str(cost_breakdown.get("activities", "SGD 0")),
        "local_transport": str(cost_breakdown.get("local_transport", "SGD 0")),
        "food": str(cost_breakdown.get("food", "SGD 0")),
        "total": str(cost_breakdown.get("total", "SGD 0")),
    }

    try:
        data["best_fit_days"] = int(
            data.get("best_fit_days", req.get("duration_days", 0))
        )
    except Exception:
        data["best_fit_days"] = req.get("duration_days", 0)

    return {"agent": "executor", **data}