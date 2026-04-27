import json
import re
from urllib.parse import quote_plus
from app.common.openai_client import get_openai_client, MODEL
from app.pricing.engine import estimate_trip_costs
from app.intelligence.realism import assess_trip_realism
from app.intelligence.budget_engine import calculate_budget, generate_budget_variants
from app.intelligence.itinerary_chunker import generate_structured_itinerary, itinerary_to_markdown
from app.intelligence.narrative_enricher import enrich_itinerary
from app.intelligence.itinerary_validator import repair_and_validate_itinerary
from app.intelligence.personalization import (
    build_personalization_profile,
    default_personalization_profile,
)


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

    existing_profile = req.get("personalization")

    if isinstance(existing_profile, dict) and existing_profile:
        profile = existing_profile
    elif req.get("preferences"):
        profile = build_personalization_profile(
            preferences=req.get("preferences"),
            source="executor_generated",
        )
    else:
        profile = default_personalization_profile(
            reason="executor_no_preferences"
        )
    
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

    primary_destination = destinations[0] if destinations else "requested destination"

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

    # -------------------------------------------------------------------
    # Sprint 6.1 Budget Scaling Engine
    # -------------------------------------------------------------------

    duration_days = req.get("duration_days", 1)
    travelers = req.get("travelers", 1)

    budget_variants = generate_budget_variants(
        destination=primary_destination,
        duration_days=duration_days,
        travelers=travelers,
    )

    comfort_budget = budget_variants["comfort"]

    data["cost_breakdown"] = {
        "flight": _format_sgd(
            comfort_budget["breakdown"]["flights"]
        ),
        "hotel": _format_sgd(
            comfort_budget["breakdown"]["accommodation"]
        ),
        "activities": _format_sgd(
            comfort_budget["breakdown"]["activities"]
        ),
        "local_transport": _format_sgd(
            comfort_budget["breakdown"]["local_transport"]
        ),
        "food": _format_sgd(
            comfort_budget["breakdown"]["food"]
        ),
        "buffer": _format_sgd(
            comfort_budget["breakdown"]["buffer"]
        ),
        "total": _format_sgd(
            comfort_budget["estimated_total"]
        ),
    }

    # Sync travel_details with structured budget engine
    data["travel_details"]["flight"]["estimated_price"] = _format_sgd(
        comfort_budget["breakdown"]["flights"]
    )

    data["travel_details"]["hotel"]["estimated_price"] = _format_sgd(
        comfort_budget["breakdown"]["accommodation"]
    )

    data["travel_details"]["transport"]["estimated_cost"] = _format_sgd(
        comfort_budget["breakdown"]["local_transport"]
    )

    # Add variant budgets to output
    data["budget_variants"] = budget_variants

    # -------------------------------------------------------------------
    # Sprint 6.1 Long-Itinerary Chunking Engine
    # -------------------------------------------------------------------

    structured_itinerary = generate_structured_itinerary(
    destination=primary_destination,
    duration_days=duration_days,
    preferences=req.get("preferences", []),
    )

    enriched_itinerary = enrich_itinerary(structured_itinerary)

    validated_result = repair_and_validate_itinerary(enriched_itinerary)
    final_itinerary = validated_result["itinerary"]

    data["daily_itinerary"] = final_itinerary
    data["itinerary_validation"] = validated_result["validation_summary"]

    data["daily_itinerary_markdown"] = itinerary_to_markdown(
        final_itinerary
    )

    realism = assess_trip_realism(
        destination=primary_destination,
        duration_days=req.get("duration_days", 1),
        daily_itinerary=data.get("daily_itinerary", []),
        travel_details=data.get("travel_details"),
    )

    data["realism"] = realism
    
    try:
        llm_days = int(data.get("best_fit_days", req.get("duration_days", 0)))
        
    except Exception:
        llm_days = req.get("duration_days", 0)

    # Override with realism recommendation
    data["best_fit_days"] = realism.get("recommended_best_fit_days", llm_days)
    data["personalization"] = profile
    
    return {"agent": "executor", **data}


async def run_executor(parsed_request: dict, planner_output: dict) -> dict:
    """
    Day 3 compatibility wrapper.
    """
    return build_itinerary(parsed_request, planner_output)