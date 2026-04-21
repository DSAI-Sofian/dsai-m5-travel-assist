import json
import re
from app.common.openai_client import get_openai_client, MODEL


def _to_number(value, default=0.0):
    """
    Convert a value like:
    - 120
    - 120.5
    - "120"
    - "SGD 120"
    - "USD 90 (~SGD 120)"
    into a float.
    Preference:
    - If SGD appears in the string, extract the SGD amount
    - Otherwise extract the first numeric value
    """
    if isinstance(value, (int, float)):
        return float(value)

    if value is None:
        return float(default)

    text = str(value).strip()

    # Prefer SGD amount if present
    sgd_match = re.search(r"SGD\s*([0-9]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
    if sgd_match:
        try:
            return float(sgd_match.group(1))
        except Exception:
            pass

    # Otherwise take first numeric value
    num_match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text.replace(",", ""))
    if num_match:
        try:
            return float(num_match.group(1))
        except Exception:
            pass

    return float(default)


def _format_sgd(value):
    """
    Format numeric value into a clean SGD string.
    """
    amount = float(value)
    if amount.is_integer():
        return f"SGD {int(amount)}"
    return f"SGD {amount:.2f}"


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
      "estimated_price": 350,
      "search_link": "Google Flights search URL"
    }},
    "hotel": {{
      "name": "Hotel name",
      "estimated_price": 420,
      "booking_link": "Booking.com search URL",
      "location_note": "Approximate distance or travel time to main area"
    }},
    "transport": {{
      "mode": "Grab / taxi / train / bus",
      "estimated_cost": 90,
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
    "flight": 350,
    "hotel": 420,
    "activities": 180,
    "local_transport": 90,
    "food": 120
  }},
  "best_fit_days": 5
}}

Rules:
- Return ONLY JSON
- All cost values must be numeric and in SGD
- Do NOT include currency symbols inside numeric fields
- Use realistic travel suggestions and realistic price estimates
- Flight links must be Google Flights search URLs
- Hotel links must be Booking.com search URLs
- nearby_attractions must contain 2 to 3 useful attractions close to the suggested hotel
- restaurants must contain 2 to 3 useful food places close to the suggested hotel
- Each nearby attraction and restaurant must include:
  name, google_maps_link, distance_note
- distance_note must describe approximate travel time from the suggested hotel
- cost_breakdown must include:
  flight, hotel, activities, local_transport, food
- Do NOT calculate or return total
- daily_itinerary must be a list
- nearby_attractions must be a list
- restaurants must be a list
- best_fit_days must be a number
- Keep scope tightly aligned to the user's requested destination(s)
- Do not introduce additional countries or cities unless the user explicitly asks for them

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
                    "estimated_price": 0,
                    "search_link": "",
                },
                "hotel": {
                    "name": "No hotel suggestion returned",
                    "estimated_price": 0,
                    "booking_link": "",
                    "location_note": "No location note returned",
                },
                "transport": {
                    "mode": "No transport suggestion returned",
                    "estimated_cost": 0,
                    "notes": "No transport notes returned",
                },
            },
            "nearby_attractions": [],
            "restaurants": [],
            "cost_breakdown": {
                "flight": 0,
                "hotel": 0,
                "activities": 0,
                "local_transport": 0,
                "food": 0,
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

    flight_price_num = _to_number(flight.get("estimated_price", 0))
    hotel_price_num = _to_number(hotel.get("estimated_price", 0))
    transport_price_num = _to_number(transport.get("estimated_cost", 0))

    data["travel_details"] = {
        "flight": {
            "suggestion": str(flight.get("suggestion", "No flight suggestion returned")),
            "estimated_price": _format_sgd(flight_price_num),
            "search_link": str(flight.get("search_link", "")),
        },
        "hotel": {
            "name": str(hotel.get("name", "No hotel suggestion returned")),
            "estimated_price": _format_sgd(hotel_price_num),
            "booking_link": str(hotel.get("booking_link", "")),
            "location_note": str(hotel.get("location_note", "No location note returned")),
        },
        "transport": {
            "mode": str(transport.get("mode", "No transport suggestion returned")),
            "estimated_cost": _format_sgd(transport_price_num),
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

    raw_costs = data["cost_breakdown"]

    flight_cost = _to_number(raw_costs.get("flight", 0))
    hotel_cost = _to_number(raw_costs.get("hotel", 0))
    activities_cost = _to_number(raw_costs.get("activities", 0))
    local_transport_cost = _to_number(raw_costs.get("local_transport", 0))
    food_cost = _to_number(raw_costs.get("food", 0))

    total_cost = (
        flight_cost
        + hotel_cost
        + activities_cost
        + local_transport_cost
        + food_cost
    )

    data["cost_breakdown"] = {
        "flight": _format_sgd(flight_cost),
        "hotel": _format_sgd(hotel_cost),
        "activities": _format_sgd(activities_cost),
        "local_transport": _format_sgd(local_transport_cost),
        "food": _format_sgd(food_cost),
        "total": _format_sgd(total_cost),
    }

    try:
        data["best_fit_days"] = int(
            data.get("best_fit_days", req.get("duration_days", 0))
        )
    except Exception:
        data["best_fit_days"] = req.get("duration_days", 0)

    return {"agent": "executor", **data}