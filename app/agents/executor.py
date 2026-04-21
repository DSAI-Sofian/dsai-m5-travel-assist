import json
from app.common.openai_client import get_openai_client, MODEL


def build_itinerary(req: dict, plan: dict):
    client = get_openai_client()

    messages = [
        {
            "role": "system",
            "content": (
                "You are a travel executor for a Southeast Asia travel planner app. "
                "Return ONLY valid JSON. Do not include markdown, explanation outside JSON, or code fences."
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
      "title": "Arrival and city walk",
      "details": "Short description of the day's plan"
    }}
  ],
  "nearby_attractions": [
    "Attraction 1",
    "Attraction 2"
  ],
  "restaurants": [
    "Restaurant 1",
    "Restaurant 2"
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
- If using another currency, clearly label it (USD, MYR, IDR, etc.)
- You may include approximate SGD conversion if helpful
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

    if not isinstance(data.get("nearby_attractions"), list):
        data["nearby_attractions"] = []

    if not isinstance(data.get("restaurants"), list):
        data["restaurants"] = []

    if not isinstance(data.get("cost_breakdown"), dict):
        data["cost_breakdown"] = {}

    cost_breakdown = data["cost_breakdown"]
    normalized_costs = {
        "flight": str(cost_breakdown.get("flight", "SGD 0")),
        "hotel": str(cost_breakdown.get("hotel", "SGD 0")),
        "activities": str(cost_breakdown.get("activities", "SGD 0")),
        "local_transport": str(cost_breakdown.get("local_transport", "SGD 0")),
        "food": str(cost_breakdown.get("food", "SGD 0")),
        "total": str(cost_breakdown.get("total", "SGD 0")),
    }
    data["cost_breakdown"] = normalized_costs

    try:
        data["best_fit_days"] = int(data.get("best_fit_days", req.get("duration_days", 0)))
    except Exception:
        data["best_fit_days"] = req.get("duration_days", 0)

    return {"agent": "executor", **data}