import json
from app.common.openai_client import get_openai_client, MODEL


def review_options(req: dict, planner: dict, executor: dict):
    client = get_openai_client()

    messages = [
        {
            "role": "system",
            "content": "You are a travel reviewer. Return ONLY valid JSON.",
        },
        {
            "role": "user",
            "content": f"""
User request:
{req}

Planner output:
{planner}

Executor output:
{executor}

Return JSON with:
within_budget
estimated_total
accuracy_check
top_3_options
user_message
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

    return {"agent": "reviewer", **data}