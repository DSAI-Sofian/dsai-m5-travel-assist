from pydantic import BaseModel
from app.common.openai_client import get_openai_client, MODEL


class ReviewerOutput(BaseModel):
    within_budget: bool
    estimated_total: float
    accuracy_check: str
    top_3_options: list[dict]
    user_message: str


def review_options(req: dict, planner: dict, executor: dict):
    client = get_openai_client()

    prompt = f"""
You are the Reviewer for a Southeast Asia travel planning app.

User request:
{req}

Planner output:
{planner}

Executor output:
{executor}

Check whether the trip is realistic and within budget.

Return valid JSON with:
- within_budget
- estimated_total
- accuracy_check
- top_3_options
- user_message
"""

    resp = client.responses.parse(
        model=MODEL,
        input=[{"role": "system", "content": prompt}],
        text_format=ReviewerOutput,
    )

    out = resp.output_parsed
    return {"agent": "reviewer", **out.model_dump()}