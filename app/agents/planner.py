from pydantic import BaseModel
from app.common.openai_client import get_openai_client, MODEL


class PlannerOutput(BaseModel):
    summary: str
    travel_modes: list[str]
    route_assumptions: list[str]
    budget_notes: list[str]


def plan_trip(req: dict):
    client = get_openai_client()

    prompt = f"""
You are the Planner for a Southeast Asia travel planning app.

User request:
{req}

Return valid JSON with:
- summary
- travel_modes
- route_assumptions
- budget_notes

Keep the answer practical and budget-aware.
"""

    resp = client.responses.parse(
        model=MODEL,
        input=[{"role": "system", "content": prompt}],
        text_format=PlannerOutput,
    )

    out = resp.output_parsed
    return {"agent": "planner", **out.model_dump()}