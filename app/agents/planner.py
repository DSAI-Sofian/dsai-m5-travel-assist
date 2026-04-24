import json
from typing import Any

from app.agents.core.constraint_agent import (
    build_planner_constraints,
    format_constraints_for_prompt,
)
from app.agents.core.intent_agent import interpret_trip_intent
from app.common.openai_client import get_openai_client, MODEL


def plan_trip(req: dict[str, Any]) -> dict[str, Any]:
    constraints = build_planner_constraints()
    constraints_block = format_constraints_for_prompt(constraints)
    # FIX: preserve original behavior
    user_request = req

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
{constraints_block}

User request:
{user_request}
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


async def run_planner(parsed_request):
    """
    Day 3 compatibility wrapper.

    Existing planner function is plan_trip().
    This wrapper preserves the new workflow.py contract.
    """
    return plan_trip(parsed_request)