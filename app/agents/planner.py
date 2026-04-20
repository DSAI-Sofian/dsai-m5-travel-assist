from pydantic import BaseModel
from app.common.openai_client import client, MODEL

class PlannerOutput(BaseModel):
    summary: str
    travel_modes: list[str]
    route_assumptions: list[str]
    budget_notes: list[str]


def plan_trip(req: dict):
    prompt = f"""
You are the Planner for a SEA travel app.
Input: {req}
Return JSON with summary, travel_modes, route_assumptions, budget_notes.
Choose flight/land/sea modes appropriate to Singapore, Malaysia, Indonesia.
"""
    resp = client.responses.parse(
        model=MODEL,
        input=[{"role": "system", "content": prompt}],
        text_format=PlannerOutput,
    )
    out = resp.output_parsed
    return {"agent": "planner", **out.model_dump()}
