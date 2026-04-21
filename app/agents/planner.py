import json
from app.common.openai_client import get_openai_client, MODEL


def plan_trip(req: dict):
    client = get_openai_client()

    messages = [
        {
            "role": "system",
            "content": (
                "You are a travel planner for a Southeast Asia travel planner app. "
                "Return ONLY valid JSON. "
                "Do not include markdown, explanation outside JSON, or code fences."
            ),
        },
        {
            "role": "user",
            "content": f"""
Plan the trip and return STRICT JSON in exactly this structure:

{{
  "summary": "Short summary of the trip approach",
  "travel_modes": ["flight", "grab"],
  "route_assumptions": [
    "Assumption 1",
    "Assumption 2"
  ],
  "budget_notes": [
    "Budget note 1",
    "Budget note 2"
  ]
}}

Rules:
- Return ONLY JSON
- Keep the trip scope tightly aligned to the user's requested destination(s)
- Do NOT introduce extra cities, regions, or countries unless the user explicitly asks for them
- If the user mentions only one destination, keep the trip focused on that destination only
- If the user mentions multiple destinations, you may plan across those destinations only
- Do NOT assume cross-border travel unless clearly requested
- Travel modes should be realistic for the requested destination(s)
- Budget notes should reflect the user's stated budget

User request:
{req}
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
            "summary": "Trip planning summary unavailable.",
            "travel_modes": [],
            "route_assumptions": [],
            "budget_notes": [],
            "raw_output": content,
        }

    if not isinstance(data.get("travel_modes"), list):
        data["travel_modes"] = []

    if not isinstance(data.get("route_assumptions"), list):
        data["route_assumptions"] = []

    if not isinstance(data.get("budget_notes"), list):
        data["budget_notes"] = []

    data["summary"] = str(data.get("summary", "Trip planning summary unavailable."))

    return {"agent": "planner", **data}