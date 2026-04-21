import json
from app.common.openai_client import get_openai_client, MODEL


def review_options(req: dict, planner: dict, executor: dict):
    client = get_openai_client()

    messages = [
        {
            "role": "system",
            "content": (
                "You are a travel reviewer for a Southeast Asia travel planner app. "
                "Return ONLY valid JSON. "
                "Do not include markdown, explanation outside JSON, or code fences."
            ),
        },
        {
            "role": "user",
            "content": f"""
Review the proposed trip and return STRICT JSON in exactly this structure:

{{
  "within_budget": true,
  "estimated_total": 1200,
  "accuracy_check": "Short review of whether the plan is realistic and complete.",
  "top_3_options": [
    {{
      "name": "Option 1 name",
      "fit": "Why this option fits the request"
    }},
    {{
      "name": "Option 2 name",
      "fit": "Why this option fits the request"
    }},
    {{
      "name": "Option 3 name",
      "fit": "Why this option fits the request"
    }}
  ],
  "user_message": "A short friendly summary for the traveler"
}}

Rules:
- Return ONLY JSON
- top_3_options must always be a list of exactly 3 objects
- each object in top_3_options must contain both "name" and "fit"
- within_budget must be true or false
- estimated_total must be a number
- accuracy_check must be a string
- user_message must be a string

User request:
{req}

Planner output:
{planner}

Executor output:
{executor}
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
            "within_budget": False,
            "estimated_total": 0,
            "accuracy_check": "Reviewer returned non-JSON output.",
            "top_3_options": [
                {"name": "Option 1", "fit": "Unable to parse reviewer output."},
                {"name": "Option 2", "fit": "Unable to parse reviewer output."},
                {"name": "Option 3", "fit": "Unable to parse reviewer output."},
            ],
            "user_message": content or "No reviewer message returned.",
        }

    # Safety cleanup to guarantee expected structure
    if not isinstance(data.get("top_3_options"), list):
        data["top_3_options"] = []

    cleaned_options = []
    for i, item in enumerate(data["top_3_options"][:3], start=1):
        if isinstance(item, dict):
            cleaned_options.append(
                {
                    "name": str(item.get("name", f"Option {i}")),
                    "fit": str(item.get("fit", "No fit description provided.")),
                }
            )
        else:
            cleaned_options.append(
                {
                    "name": f"Option {i}",
                    "fit": str(item),
                }
            )

    while len(cleaned_options) < 3:
        idx = len(cleaned_options) + 1
        cleaned_options.append(
            {
                "name": f"Option {idx}",
                "fit": "No fit description provided.",
            }
        )

    data["top_3_options"] = cleaned_options

    if not isinstance(data.get("within_budget"), bool):
        data["within_budget"] = False

    try:
        data["estimated_total"] = float(data.get("estimated_total", 0))
    except Exception:
        data["estimated_total"] = 0.0

    data["accuracy_check"] = str(
        data.get("accuracy_check", "No accuracy check provided.")
    )
    data["user_message"] = str(
        data.get("user_message", "No user message provided.")
    )

    return {"agent": "reviewer", **data}