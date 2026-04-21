import json
from app.common.openai_client import get_openai_client, MODEL


def build_itinerary(req: dict, plan: dict):
    client = get_openai_client()

    messages = [
        {
            "role": "system",
            "content": "You are a travel executor. Return ONLY valid JSON.",
        },
        {
            "role": "user",
            "content": f"""
User request:
{req}

Planner output:
{plan}

Return JSON with:
daily_itinerary
nearby_attractions
restaurants
cost_estimate
best_fit_days
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
        data = {"raw_output": content}

    return {"agent": "executor", **data}