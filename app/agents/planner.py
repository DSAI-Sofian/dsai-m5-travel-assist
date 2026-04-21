import json
from app.common.openai_client import get_openai_client, MODEL


def plan_trip(req: dict):
    client = get_openai_client()

    messages = [
        {
            "role": "system",
            "content": "You are a travel planner. Return ONLY valid JSON.",
        },
        {
            "role": "user",
            "content": f"""
User request:
{req}

Return JSON with:
summary
travel_modes
route_assumptions
budget_notes
""",
        },
    ]

    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0
    )

    content = resp.choices[0].message.content

    try:
        data = json.loads(content)
    except Exception:
        data = {"summary": content}

    return {"agent": "planner", **data}