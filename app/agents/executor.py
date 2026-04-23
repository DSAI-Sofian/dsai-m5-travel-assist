import json
import re
from urllib.parse import quote_plus
from app.common.openai_client import get_openai_client, MODEL
from app.pricing.engine import estimate_trip_costs


def _to_number(value, default=0.0):
    if isinstance(value, (int, float)):
        return float(value)

    if value is None:
        return float(default)

    text = str(value).strip()

    sgd_match = re.search(r"SGD\s*([0-9]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
    if sgd_match:
        try:
            return float(sgd_match.group(1))
        except Exception:
            pass

    num_match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text.replace(",", ""))
    if num_match:
        try:
            return float(num_match.group(1))
        except Exception:
            pass

    return float(default)


def _format_sgd(value):
    amount = float(value)
    if amount.is_integer():
        return f"SGD {int(amount)}"
    return f"SGD {amount:.2f}"


def _google_search_link(query: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(query)}"


def _google_flights_link(origin: str, destination: str, start_date: str, end_date: str) -> str:
    query = f"{origin} to {destination} flights {start_date} to {end_date}"
    return f"https://www.google.com/travel/flights?q={quote_plus(query)}"


def _booking_search_link(destination: str, start_date: str, end_date: str) -> str:
    return (
        "https://www.booking.com/searchresults.html?"
        f"ss={quote_plus(destination)}&checkin={start_date}&checkout={end_date}"
    )


def build_itinerary(req: dict, plan: dict):
    client = get_openai_client()

    destinations = req.get("destinations", [])
    origin = req.get("origin", "Singapore")
    destination_text = ", ".join(destinations) if destinations else "requested destination"
    start_date = req.get("start_date", "")
    end_date = req.get("end_date", "")

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
      "title": "Arrival and local exploration",
      "details": "Short description of the day's plan"
    }}
  ],
  "travel_details": {{
    "flight": {{
      "suggestion": "Airline + route",
      "estimated_price": 350
    }},
    "hotel": {{
      "name": "Hotel name",
      "estimated_price": 420,
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
      "distance_note": "Approximate time from hotel"
    }}
  ],
  "restaurants": [
    {{
      "name": "Restaurant name",
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
- Keep the trip scope tightly aligned to: {destination_text}
- Do NOT introduce extra cities, regions, or countries unless explicitly requested
- If the request names one destination, keep the trip focused on that destination only
- Use realistic travel suggestions and realistic price estimates
- nearby_attractions must contain 2 to 3 useful attractions close to the suggested hotel
- restaurants must contain 2 to 3 useful food places close to the suggested hotel
- Each nearby attraction and restaurant must include:
  name, distance_note
- distance_note must describe approximate travel time from the suggested hotel
- cost_breakdown must include:
  flight, hotel, activities, local_transport, food
- Do NOT calculate or return total
- daily_itinerary must be a list
- nearby_attractions must be a list
- restaurants must be a list
- best_fit_days must be a number

User request:
{req}

Planner output (JSON):
{json.dumps(plan)}
""",
        },
    ]

    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0,
    )

    content = resp.choices[0].message.content

    print("[executor] raw LLM output:", content[:500])

    try:
        data = json.loads(content)
    except Exception:
        data = {
            "daily_itinerary": [],
            "travel_details": {
                "flight": {
                    "suggestion": "No flight suggestion returned",
                    "estimated_price": 0,
                },
                "hotel": {
                    "name": "No hotel suggestion returned",
                    "estimated_price": 0,
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

    primary_destination = destinations[0] if destinations else "destination"

    data["travel_details"] = {
        "flight": {
            "suggestion": str(flight.get("suggestion", "No flight suggestion returned")),
            "estimated_price": _format_sgd(flight_price_num),
            "search_link": _google_flights_link(
                origin=origin,
                destination=primary_destination,
                start_date=start_date,
                end_date=end_date,
            ),
        },
        "hotel": {
            "name": str(hotel.get("name", "No hotel suggestion returned")),
            "estimated_price": _format_sgd(hotel_price_num),
            "booking_link": _booking_search_link(
                destination=primary_destination,
                start_date=start_date,
                end_date=end_date,
            ),
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
            name = str(item.get("name", "Unnamed attraction"))
            cleaned_attractions.append(
                {
                    "name": name,
                    "search_link": _google_search_link(f"{name} {primary_destination}"),
                    "distance_note": str(item.get("distance_note", "Distance not provided")),
                }
            )
        else:
            name = str(item)
            cleaned_attractions.append(
                {
                    "name": name,
                    "search_link": _google_search_link(f"{name} {primary_destination}"),
                    "distance_note": "Distance not provided",
                }
            )
    data["nearby_attractions"] = cleaned_attractions

    cleaned_restaurants = []
    for item in data["restaurants"][:3]:
        if isinstance(item, dict):
            name = str(item.get("name", "Unnamed restaurant"))
            cleaned_restaurants.append(
                {
                    "name": name,
                    "search_link": _google_search_link(f"{name} {primary_destination}"),
                    "distance_note": str(item.get("distance_note", "Distance not provided")),
                }
            )
        else:
            name = str(item)
            cleaned_restaurants.append(
                {
                    "name": name,
                    "search_link": _google_search_link(f"{name} {primary_destination}"),
                    "distance_note": "Distance not provided",
                }
            )
    data["restaurants"] = cleaned_restaurants

    raw_costs = data["cost_breakdown"]
    required_cost_keys = {"flight", "hotel", "activities", "local_transport", "food"}
    has_missing_cost_fields = not required_cost_keys.issubset(set(raw_costs.keys()))

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

    if has_missing_cost_fields or total_cost <= 0:
        estimated = estimate_trip_costs(
            destination=primary_destination,
            duration_days=req.get("duration_days", 1),
            travel_style=req.get("travel_style"),
        )
        flight_cost = _to_number(estimated.get("flight", 0))
        hotel_cost = _to_number(estimated.get("hotel", 0))
        activities_cost = _to_number(estimated.get("activities", 0))
        local_transport_cost = _to_number(estimated.get("local_transport", 0))
        food_cost = _to_number(estimated.get("food", 0))
        total_cost = _to_number(estimated.get("total", 0))
    
    # Sync travel_details with pricing engine if fallback used
    if has_missing_cost_fields or total_cost <= 0:
        data["travel_details"]["flight"]["estimated_price"] = _format_sgd(flight_cost)
        data["travel_details"]["hotel"]["estimated_price"] = _format_sgd(hotel_cost)
        data["travel_details"]["transport"]["estimated_cost"] = _format_sgd(local_transport_cost)
        
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
