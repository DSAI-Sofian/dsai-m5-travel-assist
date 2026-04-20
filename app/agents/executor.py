from pydantic import BaseModel
from app.common.openai_client import get_openai_client, MODEL


class ExecutorOutput(BaseModel):
    daily_itinerary: list[dict]
    nearby_attractions: list[dict]
    restaurants: list[dict]
    cost_estimate: dict
    best_fit_days: int


def build_itinerary(req: dict, plan: dict):
    client = get_openai_client()

    prompt = f"""
You are the Executor for a Southeast Asia travel planning app.

User request:
{req}

Planner output:
{plan}

Return valid JSON with:
- daily_itinerary
- nearby_attractions
- restaurants
- cost_estimate
- best_fit_days

Make the trip realistic and simple.
"""

    resp = client.responses.parse(
        model=MODEL,
        input=[{"role": "system", "content": prompt}],
        text_format=ExecutorOutput,
    )

    out = resp.output_parsed
    return {"agent": "executor", **out.model_dump()}